import terno.utils as terno_utils
import terno.models as terno_models
from suggestions import prompt as prompt_template
from sqlalchemy import MetaData, Table, select, func, text, inspect
from sqlalchemy.sql.sqltypes import DateTime, Date, TIMESTAMP
from sqlalchemy.sql import column
from sqlalchemy.types import Integer, Float, Numeric, BigInteger, SmallInteger, DECIMAL, String, Text, Enum, DateTime, Date, TIMESTAMP
from terno.llm.base import LLMFactory
import logging
from terno.llm.base import NoSufficientCreditsException, NoDefaultLLMException
from subscription.utils import deduct_llm_credits
import json

logger = logging.getLogger(__name__)


def generate_tribal_knowledge(datasource, external_knowledge=''):
    pass


def get_column_stats(conn, table_inspector, Mtable_name, column_name, cardinality_limit=20):
    """
    Optimized function to compute key statistics for a given column in a database table using SQLAlchemy.
    """

    stats = {}

    # Validate column existence
    if column_name not in table_inspector.columns:
        raise ValueError(f"Column '{column_name}' not found in table '{Mtable_name}'")

    col = table_inspector.c[column_name]

    # **Batch Query Execution for row_count, null_count, and cardinality**
    row_null_card_query = select(
        func.count().label("row_count"),
        func.count().filter(col.is_(None)).label("null_count"),
        func.count(func.distinct(col)).label("cardinality")
    ).select_from(table_inspector)

    row_null_card_result = conn.execute(row_null_card_query).fetchone()
    stats["row_count"], stats["null_count"], stats["cardinality"] = row_null_card_result
    stats["null_percentage"] = round((stats["null_count"] / stats["row_count"]) * 100, 2) if stats["row_count"] else 0

    # **Check if column is indexed**
    inspector = inspect(conn)
    indexed_columns = {col for idx in inspector.get_indexes(Mtable_name) for col in idx["column_names"]}
    stats["is_indexed"] = column_name in indexed_columns

    # **Optimized Aggregates for Numeric Columns**
    if isinstance(col.type, (Integer, Float, Numeric, BigInteger, SmallInteger, DECIMAL)):
        numeric_query = select(
            func.avg(col).label("mean"),
            func.stddev(col).label("std_dev"),
            func.min(col).label("min"),
            func.max(col).label("max")
        )
        numeric_result = conn.execute(numeric_query).fetchone()
        stats.update({k: v for k, v in zip(["mean", "std_dev", "min", "max"], numeric_result)})
        stats["range"] = (stats["max"] - stats["min"]) if stats["max"] is not None and stats["min"] is not None else None

        # **Efficient Median Calculation**
        try:
            median_query = select(func.percentile_cont(0.5).within_group(col))
            stats["median"] = conn.execute(median_query).scalar()
        except:
            stats["median"] = None

    # **Optimized String Column Stats**
    elif isinstance(col.type, (String, Text, Enum)):
        if stats["cardinality"] <= cardinality_limit:
            unique_values_query = select(col).distinct().limit(cardinality_limit)
            stats["unique_values"] = [row[0] for row in conn.execute(unique_values_query).fetchall()]
        else:
            top_values_query = select(col, func.count()).group_by(col).order_by(func.count().desc()).limit(5)
            stats["top_values"] = [{"value": row[0], "count": row[1]} for row in conn.execute(top_values_query).fetchall()]

        # **Optimize Min/Max Length Queries**
        length_query = select(
            func.min(func.char_length(col)).label("min_length"),
            func.max(func.char_length(col)).label("max_length")
        )
        min_length, max_length = conn.execute(length_query).fetchone()
        stats["min_length"], stats["max_length"] = min_length, max_length

    # **Optimized Date/Time Column Stats**
    elif isinstance(col.type, (DateTime, Date, TIMESTAMP)):
        date_query = select(
            func.min(col).label("min_date"),
            func.max(col).label("max_date")
        )
        min_date, max_date = conn.execute(date_query).fetchone()
        stats.update({"min_date": min_date, "max_date": max_date})
        stats["date_range"] = (max_date - min_date).days if max_date and min_date else None

        # **Efficient Most Frequent Date Calculation**
        freq_date_query = select(col, func.count()).group_by(col).order_by(func.count().desc()).limit(1)
        freq_date = conn.execute(freq_date_query).fetchone()
        stats["most_frequent_date"] = freq_date[0] if freq_date else None

    return stats


def get_sample_rows(conn, table_inspector, n=10):
    print("Table created")
    # Finding primary key to order table in descending manner so we can extract latest records
    latest_column = None
    for col in table_inspector.columns:
        print("Analyzing column", col)
        if col.primary_key:
            latest_column = col
            break
        if isinstance(col.type, (DateTime, Date, TIMESTAMP)):
            latest_column = col
    print("Latest column", latest_column)
    if latest_column is not None:
        query = select(table_inspector).order_by(latest_column.desc()).limit(n)
    else:
        query = select(table_inspector).limit(n)

    result = conn.execute(query).fetchall()
    return result


def generate_table_detailed_schema(conn, Mtable_name, Mtable_obj):
    metadata = MetaData()
    metadata.reflect(bind=conn.engine)
    print("Metadata calculated")
    table_inspector = Table(Mtable_name, metadata, autoload_with=conn.engine)

    print("Getting sample rows")
    sample_rows = get_sample_rows(conn, table_inspector, 20)
    print("Got sample rows")
    columns = Mtable_obj.columns
    prompt = f"Table Name: {Mtable_name}\n\n"

    prompt += "\nThis table consists of the following columns:\n"

    for col, col_obj in columns.items():
        print("Column", col)
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
            prompt += ", ".join(map(str, stats["unique_values"])) + "\n"
        elif "top_values" in stats:
            prompt += "Most Frequent Values:\n"
            for item in stats["top_values"]:
                prompt += f"Value: {item['value']}, Occurrences: {item['count']}\n"
        if "min_date" in stats:
            prompt += f"Date Range in Column: From {stats['min_date']} to {stats['max_date']} spanning {stats['date_range']} days\n"
            if stats.get("most_frequent_date"):
                prompt += f"Most Common Date: {stats['most_frequent_date']}\n"

    # Convert sample rows into structured text
    if sample_rows:
        prompt += "\nBelow are some sample rows from the table:\n"
        prompt += "=" * 80 + "\n"  # Header Separator

        column_names = list(columns.keys())
        prompt += " | ".join(column_names) + "\n"
        prompt += "-" * 80 + "\n"  # Column Separator

        for i, row in enumerate(sample_rows, start=1):
            formatted_row = [f'"{value}"' if "\n" in str(value) else str(value) for value in row]
            prompt += f"Row {i}: " + " | ".join(formatted_row) + "\n"
            prompt += "-" * 80 + "\n"  # Row Separator

    else:
        prompt += "No sample data available.\n"

    return prompt


def generate_table_description(datasource_id, org_id, input_table_name='', update_model=False):
    print("Function called")

    datasource = terno_models.DataSource.objects.get(
            id=datasource_id,
            enabled=True)   # Make this function directly take datasource as input
    organisation = terno_models.Organisation.objects.get(org_id=org_id)
    mDB = terno_utils.generate_mdb(datasource)
    schema_generated = mDB.generate_schema()
    Mtables = mDB.get_table_dict()
    engine = terno_utils.create_db_engine(datasource.type, datasource.connection_str,
                              credentials_info=datasource.connection_json)
    conn = engine.connect()
    table_descriptions = {}
    try:
        for Mtable_name, Mtable_obj in Mtables.items():
            # if input_table_name != '' and Mtable_name != input_table_name:
            #     continue
            print("Table found")
            table_schema_sql = Mtable_obj.generate_schema()
            table_schema_stats = generate_table_detailed_schema(conn, Mtable_name, Mtable_obj)
            system_prompt = prompt_template.table_description_system_prompt.format(
                dialect_name=datasource.dialect_name,
                dialect_version=datasource.dialect_version)
            ai_prompt = prompt_template.table_description_ai_prompt.format(
                database_schema=schema_generated,
                table_schema_json=table_schema_stats,
                table_schema_sql=table_schema_sql
            )
            try:
                llm, is_default_llm = LLMFactory.create_llm(organisation)
                messages = [llm.get_role_specific_message(system_prompt, 'system'),
                            llm.get_role_specific_message(ai_prompt, 'assistant')]
                print("/n/nSystem")
                print(system_prompt)
                print("/n/nAssistant")
                print(ai_prompt)
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
            # if is_default_llm:
            #     try:
            #         deduct_llm_credits(organisation.llm_credit, response)
            #     except Exception as e:
            #         logger.exception(e)
            #         terno_utils.disable_default_llm()
            print("For table  {Mtable_name}")
            res = json.loads(response['generated_sql'])
            if update_model:
                pass
            else:
                table_descriptions[Mtable_name] = res
        return table_descriptions
    except Exception as e:
        print(e)
    finally:
        conn.close()


#Table description:-
#1. Generate tribal knowledge
#1. Can generate only for tribal knowledge, or specific table or for specific column.
#2. Provide option whether to overwrite the current schema or first get user's approval before overwriting
#3. Add functionality so if it breaks in between, it can resume from the table whose schema is not generated.
#4. If there's a comment, then pass it in the prompt.
#5. Try with low-cost LLMs.