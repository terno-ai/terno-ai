import terno.utils as terno_utils
import terno.models as terno_models
from suggestions import prompt as prompt_template
from sqlalchemy import MetaData, Table, select, func, text, inspect, case
from sqlalchemy.sql.sqltypes import (
    Integer, Float, Numeric, BigInteger, SmallInteger, DECIMAL,
    String, Text, Enum, DateTime, Date, TIMESTAMP
)
from sqlalchemy.sql import column
from terno.llm.base import LLMFactory
import logging
from terno.llm.base import NoSufficientCreditsException, NoDefaultLLMException
from subscription.utils import deduct_llm_credits
import json
from django.utils.timezone import now
import time
import math
from decimal import Decimal

logger = logging.getLogger(__name__)


def safe_float(val):
    if isinstance(val, Decimal):
        return float(val)
    return val


def generate_tribal_knowledge(datasource, external_knowledge=''):
    pass


def get_column_stats(conn, table_inspector, Mtable_name, column_name, cardinality_limit=20):
    """
    Compute column statistics in a dialect-independent manner for:
      - SQLite, PostgreSQL, MySQL, Oracle, BigQuery.
      
    Uses widely supported SQL aggregates and arithmetic.
    Each stat block is wrapped in try/except so that a failure in one does not stop the rest.
    """
    logger.info(f"Analyzing column: {Mtable_name}.{column_name}")
    stats = {}

    # Validate column existence
    if column_name not in table_inspector.columns:
        logger.error(f"Column '{column_name}' not found in table '{Mtable_name}'")
        raise ValueError(f"Column '{column_name}' not found in table '{Mtable_name}'")
    
    col = table_inspector.c[column_name]
    dialect_name = conn.dialect.name.lower()

    # Basic row count, null count, and cardinality
    try:
        basic_query = select(
            func.count().label("row_count"),
            func.sum(case((col.is_(None), 1), else_=0)).label("null_count"),
            func.count(func.distinct(col)).label("cardinality")
        ).select_from(table_inspector)
        row_count, null_count, cardinality = conn.execute(basic_query).fetchone()
        stats.update({
            "row_count": row_count,
            "null_count": null_count,
            "cardinality": cardinality,
            "null_percentage": round((null_count / row_count) * 100, 2) if row_count else 0
        })
    except Exception as e:
        logger.warning(f"Basic stats failed for {Mtable_name}.{column_name}: {e}")

    # Check if column is indexed
    try:
        inspector = inspect(conn)
        indexed_columns = {c for idx in inspector.get_indexes(Mtable_name) for c in idx["column_names"]}
        stats["is_indexed"] = column_name in indexed_columns
    except Exception as e:
        logger.warning(f"Index check failed for {Mtable_name}: {e}")
        stats["is_indexed"] = False

    # Numeric column stats
    if isinstance(col.type, (Integer, Float, Numeric, BigInteger, SmallInteger, DECIMAL)):
        try:
            # Compute average, min, max, and variance (avg(x*x) - avg(x)^2)
            numeric_query = select(
                func.avg(col).label("mean"),
                func.min(col).label("min"),
                func.max(col).label("max"),
                (func.avg(col * col) - func.avg(col) * func.avg(col)).label("variance")
            ).where(col.isnot(None)).select_from(table_inspector)
            result = conn.execute(numeric_query).fetchone()
            mean, min_val, max_val, variance = result

            # Convert to float using safe_float
            mean = safe_float(mean)
            min_val = safe_float(min_val)
            max_val = safe_float(max_val)
            variance = safe_float(variance)

            std_dev = math.sqrt(variance) if (variance is not None and variance >= 0) else None
            stats.update({
                "mean": mean,
                "min": min_val,
                "max": max_val,
                "std_dev": std_dev,
                "range": (max_val - min_val) if (min_val is not None and max_val is not None) else None
            })
        except Exception as e:
            logger.warning(f"Numeric stats failed for {Mtable_name}.{column_name}: {e}")
            stats["mean"] = stats["min"] = stats["max"] = stats["std_dev"] = stats["range"] = None

        # Median Calculation
        try:
            median_query = None

            if dialect_name in {"postgresql", "oracle"}:
                # PostgreSQL and Oracle support percentile_cont with within_group
                median_query = select(func.percentile_cont(0.5).within_group(col)).select_from(table_inspector)
            elif dialect_name == "bigquery":
                # BigQuery: Use APPROX_QUANTILES to get median
                median_query = text(f"""
                    SELECT quantiles[OFFSET(1)] as median
                    FROM (
                        SELECT APPROX_QUANTILES({column_name}, 2) as quantiles
                        FROM {Mtable_name}
                        WHERE {column_name} IS NOT NULL
                    )
                """)
            elif dialect_name == "mysql":
                # For MySQL: fetch total count first, then use limit/offset
                total_count = conn.execute(
                    text(f"SELECT COUNT(*) FROM {Mtable_name} WHERE {column_name} IS NOT NULL")
                ).scalar()
                if total_count == 0:
                    stats["median"] = None
                else:
                    offset = (total_count - 1) // 2
                    limit = 2 if total_count % 2 == 0 else 1
                    median_query = text(f"""
                        SELECT AVG({column_name}) as median FROM (
                            SELECT {column_name}
                            FROM {Mtable_name}
                            WHERE {column_name} IS NOT NULL
                            ORDER BY {column_name}
                            LIMIT {limit} OFFSET {offset}
                        ) as sub
                    """)
            elif dialect_name == "sqlite":
                # SQLite: simple median query using OFFSET subquery
                median_query = text(f"""
                    SELECT {column_name} as median FROM {Mtable_name}
                    WHERE {column_name} IS NOT NULL
                    ORDER BY {column_name}
                    LIMIT 1 OFFSET (
                        SELECT COUNT(*)/2 FROM {Mtable_name} WHERE {column_name} IS NOT NULL
                    )
                """)
            if median_query is not None:
                result = conn.execute(median_query).scalar()
                stats["median"] = safe_float(result) if result is not None else None
        except Exception as e:
            logger.warning(f"Median computation failed for {Mtable_name}.{column_name}: {e}")
            stats["median"] = None

    # String/Text column stats
    elif isinstance(col.type, (String, Text, Enum)):
        try:
            if stats.get("cardinality", 0) <= cardinality_limit:
                unique_query = select(col, func.count().label("cnt")).group_by(col).order_by(func.count().desc()).limit(cardinality_limit)
                rows = conn.execute(unique_query).fetchall()
                stats["unique_values"] = [{"value": row[0], "count": row[1]} for row in rows]
            else:
                top_query = select(col, func.count().label("cnt")).group_by(col).order_by(func.count().desc()).limit(5)
                rows = conn.execute(top_query).fetchall()
                stats["top_values"] = [{"value": row[0], "count": row[1]} for row in rows]
        except Exception as e:
            logger.warning(f"String frequency analysis failed for {Mtable_name}.{column_name}: {e}")

        try:
            # Oracle uses LENGTH; other dialects generally support func.length.
            length_func = func.length
            length_query = select(
                func.min(length_func(col)).label("min_length"),
                func.max(length_func(col)).label("max_length")
            ).select_from(table_inspector)
            min_length, max_length = conn.execute(length_query).fetchone()
            stats["min_length"] = min_length
            stats["max_length"] = max_length
        except Exception as e:
            logger.warning(f"String length stats failed for {Mtable_name}.{column_name}: {e}")
            stats["min_length"] = stats["max_length"] = None

    # Date/Time column stats
    elif isinstance(col.type, (DateTime, Date, TIMESTAMP)):
        try:
            dt_query = select(
                func.min(col).label("min_date"),
                func.max(col).label("max_date")
            ).where(col.isnot(None)).select_from(table_inspector)
            min_date, max_date = conn.execute(dt_query).fetchone()
            stats["min_date"] = min_date
            stats["max_date"] = max_date
            stats["date_range"] = (max_date - min_date).days if (min_date and max_date) else None
        except Exception as e:
            logger.warning(f"Date range stats failed for {Mtable_name}.{column_name}: {e}")
            stats["min_date"] = stats["max_date"] = stats["date_range"] = None

        try:
            freq_query = select(col, func.count().label("cnt")).group_by(col).order_by(func.count().desc()).limit(1)
            freq_date = conn.execute(freq_query).fetchone()
            stats["most_frequent_date"] = freq_date[0] if freq_date else None
        except Exception as e:
            logger.warning(f"Most frequent date query failed for {Mtable_name}.{column_name}: {e}")
            stats["most_frequent_date"] = None

    logger.info(f"Stats: {stats}")
    return stats


def get_sample_rows(conn, table_inspector, n=10):
    # Finding primary key to order table in descending manner so we can extract latest records
    latest_column = None
    for col in table_inspector.columns:
        if col.primary_key:
            latest_column = col
            break
        if isinstance(col.type, (DateTime, Date, TIMESTAMP)):
            latest_column = col

    if latest_column is not None:
        query = select(table_inspector).order_by(latest_column.desc()).limit(n)
    else:
        query = select(table_inspector).limit(n)

    result = conn.execute(query).fetchall()
    return result


def generate_table_detailed_schema(conn, metadata, Mtable_name, Mtable_obj):
    table_inspector = Table(Mtable_name, metadata, autoload_with=conn.engine)

    sample_rows = get_sample_rows(conn, table_inspector, 20)

    columns = Mtable_obj.columns

    return_dict = {'sample_rows': None, 'unique_values': {}, 'prompt': '', 'column_list': list(columns.keys())}

    prompt = f"Table Name: {Mtable_name}\n\n"
    prompt += "\nThis table consists of the following columns:\n"

    for col, col_obj in columns.items():
        stats = get_column_stats(conn, table_inspector, Mtable_name, col)

        prompt += f"\nColumn Name: {col}\n"
        prompt += f"Data Type: {col_obj.type}\n"
        prompt += f"Column Constraints: "
        if col_obj.primary_key:
            prompt += "Primary Key\n"

        prompt += f"Total Rows in Column: {stats['row_count']}\n"
        prompt += f"Number of Null Values: {stats['null_count']}, which is {stats['null_percentage']}% of total rows\n"
        prompt += f"Number of Unique Values: {stats['cardinality']}\n"

        if stats.get("approx_distinct") is not None:
            prompt += f"Approximate Unique Values based on information schema: {stats['approx_distinct']}\n"

        if stats.get("is_indexed"):
            prompt += "This column is indexed, which may improve query performance.\n"

        if "mean" in stats:
            prompt += "Statistical Summary:\n"
            prompt += f"Mean Value: {stats['mean']}\n"
            prompt += f"Standard Deviation: {stats['std_dev']}\n"
            prompt += f"Minimum Value: {stats['min']}\n"
            prompt += f"Maximum Value: {stats['max']}\n"
            prompt += f"Range: {stats['range']}\n"
            prompt += f"Median Value: {stats['median']}\n"

        if "unique_values" in stats:
            prompt += "All unique Values in Column:\n"
            return_dict['unique_values'][col] = {}
            return_dict['unique_values'][col]['unique_value_type'] = 'unique'
            for item in stats["unique_values"]:
                prompt += f"Value: {item['value']}, Occurrences: {item['count']}\n"
                return_dict['unique_values'][col][item['value']] = item['count']
        elif "top_values" in stats:
            prompt += "Most Frequent Values:\n"
            return_dict['unique_values'][col] = {}
            return_dict['unique_values'][col]['unique_value_type'] = 'top'
            for item in stats["top_values"]:
                prompt += f"Value: {item['value']}, Occurrences: {item['count']}\n"
                return_dict['unique_values'][col][item['value']] = item['count']

        if "min_date" in stats:
            prompt += f"Date Range in Column: From {stats['min_date']} to {stats['max_date']} spanning {stats['date_range']} days\n"
            if stats.get("most_frequent_date"):
                prompt += f"Most Common Date: {stats['most_frequent_date']}\n"

    # Convert sample rows into structured text
    if sample_rows:
        return_dict['sample_rows'] = {"column_order": list(columns.keys()),
                                    "sample_rows": []}
        prompt += "\nBelow are some sample rows from the table:\n"
        prompt += "=" * 80 + "\n"  # Header Separator

        column_names = list(columns.keys())
        prompt += " | ".join(column_names) + "\n"
        prompt += "-" * 80 + "\n"  # Column Separator

        for i, row in enumerate(sample_rows, start=1):
            formatted_row = [f'"{value}"' if "\n" in str(value) else str(value) for value in row]
            return_dict['sample_rows']['sample_rows'].append(formatted_row)
            prompt += f"Row {i}: " + " | ".join(formatted_row) + "\n"
            prompt += "-" * 80 + "\n"  # Row Separator

    return_dict['prompt'] = prompt

    return return_dict


def generate_table_and_column_description(datasource_id, input_table_names=None, update_model=True, overwrite=False):
    logger.info(f"Starting generate_table_and_column_description for datasource_id: {datasource_id}")
    table_descriptions = {}

    try:
        # 1. Fetch datasource and organisation info
        datasource = terno_models.DataSource.objects.get(id=datasource_id, enabled=True)
        organisation = terno_models.OrganisationDataSource.objects.get(datasource=datasource).organisation

        # 2. Generate metadata bridge (mDB)
        logger.debug("Generating mDB metadata bridge")
        mDB = terno_utils.generate_mdb(datasource)
        schema_generated = mDB.generate_schema()
        Mtables = mDB.get_table_dict()

        # 3. Create engine and connect safely using context manager
        engine = terno_utils.create_db_engine(
            datasource.type,
            datasource.connection_str,
            credentials_info=datasource.connection_json
        )

        with engine.connect() as conn:
            # 4. Reflect SQLAlchemy metadata inside the connection
            metadata = MetaData()
            if input_table_names:
                logger.debug(f"Reflecting only selected tables: {input_table_names}")
                metadata.reflect(bind=conn, only=input_table_names)
            else:
                logger.debug("Reflecting full metadata")
                metadata.reflect(bind=conn)

            # 5. Process each table one by one
            for Mtable_name, Mtable_obj in Mtables.items():
                if input_table_names and Mtable_name not in input_table_names:
                    continue

                terno_table = terno_models.Table.objects.get(name=Mtable_name)

                if not overwrite and terno_table.description is not None:
                    logger.info(f"Skipping {Mtable_name} — already has a description.")
                    continue

                logger.info(f"Started generating table description for {Mtable_name}")

                # Generate table structure prompts
                table_schema_sql = Mtable_obj.generate_schema()
                table_schema_stats_dict = generate_table_detailed_schema(conn, metadata, Mtable_name, Mtable_obj)
                table_schema_stats = table_schema_stats_dict['prompt']

                # Prompt preparation
                system_prompt = prompt_template.table_description_system_prompt.format(
                    dialect_name=datasource.dialect_name,
                    dialect_version=datasource.dialect_version)

                ai_prompt = prompt_template.table_description_ai_prompt.format(
                    database_schema=schema_generated,
                    table_schema_json=table_schema_stats,
                    table_schema_sql=table_schema_sql,
                    column_list=table_schema_stats_dict['column_list']
                )

                # 6. Call LLM
                try:
                    logger.debug(f"Calling LLM to describe table: {Mtable_name}")
                    llm, is_default_llm = LLMFactory.create_llm(organisation)
                    messages = [
                        llm.get_role_specific_message(system_prompt, 'system'),
                        llm.get_role_specific_message(ai_prompt, 'assistant')
                    ]
                    response = llm.get_response(messages)
                except (NoSufficientCreditsException, NoDefaultLLMException) as e:
                    logger.exception(e)
                    return {'status': 'error', 'error': str(e)}
                except Exception as e:
                    logger.exception(f"Error during LLM response for {Mtable_name}: {e}")
                    continue

                # 7. Process response
                try:
                    res = json.loads(response['generated_sql'])
                    logger.debug(f"Raw LLM response parsed successfully for {Mtable_name}")

                    if isinstance(res, dict) and len(res) == 1:
                        res = list(res.values())[0]

                    if update_model:
                        terno_table.public_name = res.get("table_name")
                        terno_table.description = res.get("table_description")
                        terno_table.sample_rows = table_schema_stats_dict['sample_rows']
                        terno_table.description_updated_at = now()

                        terno_table_columns = {
                            col.name: col for col in terno_models.TableColumn.objects.filter(table=terno_table)
                        }

                        for col in res["columns"]:
                            terno_table_col = terno_table_columns.get(col["column_name"])
                            if terno_table_col:
                                terno_table_col.public_name = col["column_public_name"]
                                terno_table_col.description = col["column_description"]
                                if col["column_name"] in table_schema_stats_dict['unique_values']:
                                    terno_table_col.unique_categories = table_schema_stats_dict['unique_values'][col["column_name"]]
                                terno_table_col.save()

                        terno_table.save()

                    logger.debug(f"Updated description for table {Mtable_name} and its columns")
                    table_descriptions[Mtable_name] = res

                except Exception as e:
                    logger.exception(f"Error processing LLM response for {Mtable_name}: {e}. Response: {response}")
                    continue

        return {'status': 'success', 'descriptions': table_descriptions}

    except Exception as e:
        logger.exception(f"Unhandled error in table description task {e}")
        return {'status': 'error', 'error': str(e)}
