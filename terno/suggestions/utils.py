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
from pymilvus import MilvusClient, DataType
import json
from django.utils.timezone import now
import time
import os
import math
from decimal import Decimal
from django.conf import settings

logger = logging.getLogger(__name__)


def safe_float(val):
    if isinstance(val, Decimal):
        return float(val)
    return val


def generate_tribal_knowledge(datasource, external_knowledge=''):
    pass


def get_column_stats(conn, table_inspector, Mtable_name, column_name, cardinality_limit=20):
    """
    Compute column statistics in a dialect-independent manner.
    Includes protection against errors in any specific stat block and wraps the whole thing
    in a rollback-protected try/except to avoid partial failures from crashing the process.
    """
    logger.debug(f"Analyzing column: {Mtable_name}.{column_name}")
    stats = {}

    try:
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
                numeric_query = select(
                    func.avg(col).label("mean"),
                    func.min(col).label("min"),
                    func.max(col).label("max"),
                    (func.avg(col * col) - func.avg(col) * func.avg(col)).label("variance")
                ).where(col.isnot(None)).select_from(table_inspector)
                result = conn.execute(numeric_query).fetchone()
                mean, min_val, max_val, variance = result

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

            # Median
            try:
                median_query = None
                if dialect_name in {"postgresql", "oracle"}:
                    median_query = select(func.percentile_cont(0.5).within_group(col)).select_from(table_inspector)
                elif dialect_name == "bigquery":
                    median_query = text(f"""
                        SELECT quantiles[OFFSET(1)] as median
                        FROM (
                            SELECT APPROX_QUANTILES({column_name}, 2) as quantiles
                            FROM {Mtable_name}
                            WHERE {column_name} IS NOT NULL
                        )
                    """)
                elif dialect_name == "mysql":
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

    except Exception as top_level_err:
        logger.error(f"Top-level failure while processing {Mtable_name}.{column_name}: {top_level_err}")
        try:
            conn.rollback()
        except Exception as rollback_err:
            logger.warning(f"Rollback failed while handling error in {Mtable_name}.{column_name}: {rollback_err}")
        return {}

    logger.debug(f"Stats: {stats}")
    return stats


def get_sample_rows(conn, table_inspector, n=20):
    try:
        # Finding primary key or timestamp column to sort by latest
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

    except Exception as e:
        logger.error(f"Error fetching sample rows for table {table_inspector.name}: {e}")
        try:
            conn.rollback()
        except Exception as rollback_err:
            logger.warning(f"Rollback failed for sample row fetch on {table_inspector.name}: {rollback_err}")
        return []


def generate_table_detailed_schema(conn, metadata, Mtable_name, Mtable_obj):
    try:
        table_inspector = Table(Mtable_name, metadata, autoload_with=conn.engine)
        sample_rows = get_sample_rows(conn, table_inspector, 20)
        columns = Mtable_obj.columns

        return_dict = {
            'sample_rows': None,
            'unique_values': {},
            'prompt': '',
            'column_list': list(columns.keys())
        }

        prompt = f"Table Name: {Mtable_name}\n\n"
        prompt += "This table consists of the following columns:\n"

        for col, col_obj in columns.items():
            try:
                stats = get_column_stats(conn, table_inspector, Mtable_name, col)
            except Exception as e:
                logger.warning(f"[{Mtable_name}.{col}] Failed to get column stats: {e}")
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.warning(f"[{Mtable_name}.{col}] Rollback failed: {rollback_err}")
                stats = {}

            prompt += f"\nColumn Name: {col}\n"
            prompt += f"Data Type: {col_obj.type}\n"

            prompt += "Column Constraints: "
            constraints = []
            if col_obj.primary_key:
                constraints.append("Primary Key")
            if not col_obj.nullable:
                constraints.append("Not Null")
            if getattr(col_obj, "unique", False):
                constraints.append("Unique")
            prompt += ", ".join(constraints) + "\n" if constraints else "None\n"

            prompt += f"Total Rows in Column: {stats.get('row_count', 'N/A')}\n"
            prompt += f"Number of Null Values: {stats.get('null_count', 'N/A')} ({stats.get('null_percentage', 'N/A')}%)\n"
            prompt += f"Number of Unique Values: {stats.get('cardinality', 'N/A')}\n"

            if stats.get("approx_distinct") is not None:
                prompt += f"Approximate Unique Values: {stats['approx_distinct']}\n"

            if stats.get("is_indexed"):
                prompt += "This column is indexed.\n"

            if all(k in stats for k in ["mean", "std_dev", "min", "max", "range", "median"]):
                prompt += "Statistical Summary:\n"
                prompt += f"- Mean: {stats['mean']}\n"
                prompt += f"- Std Dev: {stats['std_dev']}\n"
                prompt += f"- Min: {stats['min']}\n"
                prompt += f"- Max: {stats['max']}\n"
                prompt += f"- Range: {stats['range']}\n"
                prompt += f"- Median: {stats['median']}\n"

            if "unique_values" in stats:
                prompt += "All Unique Values:\n"
                return_dict['unique_values'][col] = {'unique_value_type': 'unique'}
                for item in stats["unique_values"]:
                    prompt += f"  - {item['value']}: {item['count']} occurrences\n"
                    return_dict['unique_values'][col][item['value']] = item['count']
            elif "top_values" in stats:
                prompt += "Most Frequent Values:\n"
                return_dict['unique_values'][col] = {'unique_value_type': 'top'}
                for item in stats["top_values"]:
                    prompt += f"  - {item['value']}: {item['count']} occurrences\n"
                    return_dict['unique_values'][col][item['value']] = item['count']

            if "min_date" in stats:
                prompt += f"Date Range: {stats['min_date']} to {stats['max_date']} ({stats['date_range']} days)\n"
                if stats.get("most_frequent_date"):
                    prompt += f"Most Common Date: {stats['most_frequent_date']}\n"

        if sample_rows:
            return_dict['sample_rows'] = {
                "column_order": list(columns.keys()),
                "sample_rows": []
            }
            prompt += "\nBelow are some sample rows from the table:\n"
            prompt += "=" * 80 + "\n"
            prompt += " | ".join(columns.keys()) + "\n"
            prompt += "-" * 80 + "\n"

            for i, row in enumerate(sample_rows, start=1):
                formatted_row = [f'"{value}"' if "\n" in str(value) else str(value) for value in row]
                return_dict['sample_rows']['sample_rows'].append(formatted_row)
                prompt += f"Row {i}: " + " | ".join(formatted_row) + "\n"
                prompt += "-" * 80 + "\n"

        return_dict['prompt'] = prompt
        return return_dict

    except Exception as e:
        logger.error(f"Error generating detailed schema for table {Mtable_name}: {e}")
        try:
            conn.rollback()
        except Exception as rollback_err:
            logger.warning(f"Rollback failed during schema generation for {Mtable_name}: {rollback_err}")
        return None


def generate_table_and_column_description(datasource_id, org_id=None, input_table_names=None, update_model=True, overwrite=False):
    logger.info(f"Starting generate_table_and_column_description for datasource_id: {datasource_id}")
    table_descriptions = []
    result = {}

    try:
        # 1. Fetch datasource and organisation info
        datasource = terno_models.DataSource.objects.get(id=datasource_id, enabled=True)
        if org_id:
            organisation = terno_models.Organisation.objects.get(id=org_id)
        else:
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

                terno_table = terno_models.Table.objects.get(name=Mtable_name, data_source=datasource)

                if (not overwrite) and terno_table.complete_description:
                    logger.info(f"Skipping {Mtable_name} — already has a description.")
                    continue

                logger.info(f"Started generating table description for {Mtable_name}")

                # Generate table structure prompts
                table_schema_sql = Mtable_obj.generate_schema()

                try:
                    table_schema_stats_dict = generate_table_detailed_schema(conn, metadata, Mtable_name, Mtable_obj)
                    if not table_schema_stats_dict:
                        logger.warning(f"No detailed schema returned for {Mtable_name}, skipping...")
                        continue
                except Exception as e:
                    logger.exception(f"Error generating detailed schema for {Mtable_name}: {e}")
                    continue

                table_schema_stats = table_schema_stats_dict['prompt']

                if datasource.is_erp:
                    logger.info("Found ERP datasource and adjusting the prompt accordingly")
                    system_prompt = prompt_template.ERP_table_description_system_prompt.format(
                        dialect_name=datasource.dialect_name,
                        dialect_version=datasource.dialect_version)

                    ai_prompt = prompt_template.ERP_table_description_ai_prompt.format(
                        database_schema=schema_generated,
                        table_schema_json=table_schema_stats,
                        table_schema_sql=table_schema_sql,
                        column_list=table_schema_stats_dict['column_list']
                    )
                else:
                    logger.info("Found non-ERP datasource and adjusting the prompt accordingly")
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
                    llm, is_default_llm = LLMFactory.create_llm(organisation, model_name_override="o3-mini")
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

                    category = res.get("category", "")
                    table_description = res.get("table_description")
                    table_cat_desc = f"{category} | {table_description}" if category else table_description
                    table_description_vector = llm.generate_vector(table_cat_desc)

                    record = {
                        "table_name": Mtable_name,
                        "embedding": table_description_vector
                    }
                    table_descriptions.append(record)

                    if update_model:
                        terno_table.public_name = res.get("table_name").replace(' ', '_')
                        terno_table.category = category
                        terno_table.description = table_description
                        terno_table.sample_rows = table_schema_stats_dict['sample_rows']
                        terno_table.description_updated_at = now()
                        terno_table.save()
                        terno_table_columns = {
                            col.name: col for col in terno_models.TableColumn.objects.filter(table=terno_table)
                        }

                        for col in res["columns"]:
                            terno_table_col = terno_table_columns.get(col["column_name"])
                            if terno_table_col:
                                terno_table_col.public_name = col.get("column_public_name").replace(' ', '_')
                                terno_table_col.description = col.get("column_description")
                                if col["column_name"] in table_schema_stats_dict['unique_values']:
                                    terno_table_col.unique_categories = table_schema_stats_dict['unique_values'][col["column_name"]]
                                terno_table_col.save()

                        terno_table.complete_description = True
                        terno_table.save()

                    logger.debug(f"Updated description for table {Mtable_name} and its columns")
                    result[Mtable_name] = res

                except Exception as e:
                    logger.exception(f"Error processing LLM response for {Mtable_name}: {e}. Response: {response}")
                    continue

        create_store_vector_DB(datasource_id, table_descriptions)
        return {'status': 'success', 'descriptions': result}

    except Exception as e:
        logger.exception(f"Unhandled error in table description task {e}")
        return {'status': 'error', 'error': str(e)}



def is_ERP(datasource_id):
    """
    Uses LLM to determine whether a given datasource is an ERP system.
    Updates the `is_erp` flag in the DataSource model.
    """
    datasource = terno_models.DataSource.objects.get(id=datasource_id, enabled=True)
    organisation = terno_models.OrganisationDataSource.objects.get(datasource=datasource).organisation

    mDB = terno_utils.generate_mdb(datasource)
    full_schema_str = mDB.generate_schema()

    system_prompt = prompt_template.ERP_detection_system_prompt
    ai_prompt = prompt_template.ERP_detection_ai_prompt.format(
        full_schema_sql=full_schema_str
    )

    try:
        llm, is_default_llm = LLMFactory.create_llm(organisation)
        messages = [
            llm.get_role_specific_message(system_prompt, 'system'),
            llm.get_role_specific_message(ai_prompt, 'assistant')
        ]
        response = llm.get_response(messages)
    except NoSufficientCreditsException as e:
        logger.exception(e)
        return {'status': 'error', 'error': str(e)}
    except NoDefaultLLMException as e:
        logger.exception(e)
        return {'status': 'error', 'error': str(e)}
    except Exception as e:
        logger.exception(e)
        return {'status': 'error', 'error': str(e)}
    res = json.loads(response['generated_sql'])
    is_erp_flag = res.get("is_erp", 0) == 1
    terno_models.DataSource.objects.filter(id=datasource.id).update(is_erp=is_erp_flag)

    return {
        "datasource_id": datasource_id,
        "is_erp": is_erp_flag
    }


def create_store_vector_DB(datasource_id, table_descriptions=[]):
    """
    Creates database/collection/partition in Milvus and stores the given table_descriptions (with vectors).
    """
    datasource = terno_models.DataSource.objects.get(id=datasource_id, enabled=True)
    organisation = terno_models.OrganisationDataSource.objects.get(datasource=datasource).organisation
    org_name = organisation.name
    try:
        milvus_client = MilvusClient(uri=settings.MILVUS_URI)
        db_name = f"db_{org_name.replace(' ', '_')}"
        collection_name = f"coll_{org_name.replace(' ', '_')}"
        partition_name = f"ps_{datasource_id}"
        
        if settings.MILVUS_SERVER:
            if db_name not in milvus_client.list_databases():
                milvus_client.create_database(db_name)
            milvus_client.using_database(db_name)

        if collection_name not in milvus_client.list_collections():
            schema = milvus_client.create_schema(auto_id=True, enable_dynamic_field=True)
            schema.add_field("id", datatype=DataType.INT64, is_primary=True)
            schema.add_field("table_name", datatype=DataType.VARCHAR, max_length=100)
            schema.add_field("embedding", datatype=DataType.FLOAT_VECTOR, dim=1536)

            milvus_client.create_collection(collection_name=collection_name, schema=schema, dimension=1536)

            index_params = MilvusClient.prepare_index_params()
            index_params.add_index(
                field_name="embedding",
                metric_type="COSINE",
                index_type="IVF_FLAT",
                index_name="embedding_index",
                params={"nlist": 25}
            )

            milvus_client.create_index(
                collection_name=collection_name,
                index_params=index_params,
                sync=True
            )
        
        if partition_name in milvus_client.list_partitions(collection_name):
            milvus_client.insert(collection_name, table_descriptions, partition_name=partition_name)
        else:
            milvus_client.create_partition(collection_name, partition_name)
            milvus_client.insert(collection_name, table_descriptions, partition_name=partition_name)

        print(f"Stored {len(table_descriptions)} tables in Milvus DB: {db_name}, Collection: {collection_name}, Partition: {partition_name}")

    except Exception as e:
        logger.exception(e)
        return {"status": "error", "error": str(e)}


def get_category_for_user_question(question, organisation):
    """
    get_category_for_user_question takes users question and categorise it into predefined categories using llm.
    """

    system_prompt = prompt_template.categorise_user_question_system_prompt
    ai_prompt = prompt_template.categorise_user_question_ai_prompt.format(
        question = question
    )

    try:
        llm, is_default_llm = LLMFactory.create_llm(organisation)
        messages = [llm.get_role_specific_message(system_prompt, 'system'),
            llm.get_role_specific_message(ai_prompt, 'assistant')]
        response = llm.get_response(messages)
    except NoSufficientCreditsException as e:
        logger.exception(e)
        return {'status': 'error', 'error': str(e)}
    except NoDefaultLLMException as e:
        logger.exception(e)
        return {'status': 'error', 'error': str(e)}
    except Exception as e:
        logger.exception(e)
        return {'status': 'error', 'error': str(e)}
    print(f"For Question  {question}")
    res = json.loads(response['generated_sql'])
    text = f"{res['categories']} | {res['user_question']}"
    print(f"{text}")
    user_question_vector = llm.generate_vector(text)
    return user_question_vector


def drop_vector_DB(datasource=None, datasource_id=""):
    # Load datasource if only ID is given
    if not datasource and datasource_id:
        try:
            datasource = terno_models.DataSource.objects.get(id=datasource_id, enabled=True)
        except terno_models.DataSource.DoesNotExist:
            print(f"[drop_vector_DB] DataSource with ID {datasource_id} not found or not enabled.")
            return

    if not datasource:
        print("[drop_vector_DB] No valid datasource provided.")
        return
    else:
        datasource_id = str(datasource.id)
    
    try:
        organisation = terno_models.OrganisationDataSource.objects.get(datasource=datasource).organisation
    except terno_models.OrganisationDataSource.DoesNotExist:
        logger.warning(f"[drop_vector_DB] Organisation not found for datasource: {datasource_id}")
        return

    org_name = organisation.name
    db_name = f"db_{org_name.replace(' ', '_')}"
    collection_name = f"coll_{org_name.replace(' ', '_')}"
    partition_name = f"ps_{datasource_id}"

    # db_name = "db_Default_Organisation"
    # collection_name = "coll_Default_Organisation"
    # partition_name = f"ps_{datasource_id}"

    try:
        milvus_client = MilvusClient(uri=settings.MILVUS_URI)
        milvus_client.using_database(db_name)
    except Exception as e:
        logger.error(f"Failed to switch to database: {e}")

    try:
        milvus_client.drop_partition(collection_name, partition_name)
        logger.info(f"Dropped partition: {partition_name}")
    except Exception as e:
        logger.error(f"Failed to drop partition: {e}")


def search_vector_DB(datasource_id, user_question='', allowed_tables=[], threshold=0.72, max_results=15):
    """
    search_vector_DB Searches for similar records in Milvus vector DB using cosine similarity.

    :param query_vector: The embedding vector to search for using cosine similarity
    :param allowed_tables: List of allowed table names to filter the results
    :return: List of relevant table names with similarity scores
    """
    print(f"\n[DEBUG] Starting vector search for datasource_id: {datasource_id}")
    print(f"[DEBUG] Threshold: {threshold}, Max Results: {max_results}")
    print(f"[DEBUG] User question: {user_question}")

    datasource = terno_models.DataSource.objects.get(id=datasource_id, enabled=True)
    organisation = terno_models.OrganisationDataSource.objects.get(datasource=datasource).organisation
    org_name = organisation.name

    if datasource.is_erp:
        print(f"\nERP datasource detected: {datasource_id}\n")
        user_question_vector = get_category_for_user_question(user_question, organisation)
    else:
        llm, is_default_llm = LLMFactory.create_llm(organisation)
        user_question_vector = llm.generate_vector(user_question)

    print(f"[DEBUG] Organisation: {org_name}")

    # Initialize MilvusClient
    milvus_client = MilvusClient(uri=settings.MILVUS_URI)

    db_name = f"db_{org_name.replace(' ', '_')}"
    collection_name = f"coll_{org_name.replace(' ', '_')}"
    partition_name = f"ps_{datasource_id}"

    print(f"[DEBUG] Milvus DB: {db_name}")
    print(f"[DEBUG] Collection: {collection_name}")
    print(f"[DEBUG] Partition: {partition_name}")

    milvus_client.using_database(db_name)

    if collection_name not in milvus_client.list_collections():
        raise Exception(f"Collection {collection_name} does not exist in Vector DB")

    milvus_client.load_collection(collection_name)

    try:
        print(f"[DEBUG] Running vector search in Milvus...")
        search_results = milvus_client.search(
            collection_name=collection_name,
            data=[user_question_vector],
            partition_names=[partition_name],
            output_fields=["table_name"],
            metric_type="COSINE",
            top_k=max_results,
        )

        matching_results = []
        print(f"[DEBUG] Raw search results count: {len(search_results[0])}")

        for result in search_results[0]:
            similarity = result.get("distance")
            table_name = result.get("entity", {}).get("table_name")

            if table_name is None:
                print(f"[DEBUG] Skipping result with no table name")
                continue

            print(f"[DEBUG] Result: table_name={table_name}, similarity={similarity}")

            if similarity is not None and similarity >= threshold:
                print(f"[DEBUG] --> Table '{table_name}' passed threshold ({threshold})")
                matching_results.append(table_name)
            else:
                print(f"[DEBUG] --> Table '{table_name}' did not meet threshold ({threshold})")

        if allowed_tables:
            print(f"[DEBUG] Filtering by allowed tables (count={len(allowed_tables)})...")
            relevant_tables = [table for table in matching_results if table in allowed_tables]
        else:
            relevant_tables = matching_results

        print(f"[DEBUG] Final relevant tables (after filtering): {relevant_tables}")

        return relevant_tables

    finally:
        print(f"[DEBUG] Releasing collection '{collection_name}'")
        milvus_client.release_collection(collection_name)