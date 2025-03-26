import terno.utils as terno_utils
import terno.models as terno_models
from sqlalchemy import MetaData, Table, select, func, text
from sqlalchemy.sql.sqltypes import DateTime, Date, TIMESTAMP
from sqlalchemy.sql import column
from sqlalchemy.types import Integer, Float, Numeric, BigInteger, SmallInteger, DECIMAL, String, Text, Enum, DateTime, Date, TIMESTAMP


def generate_tribal_knowledge(datasource, external_knowledge=''):
    pass


def get_column_stats(conn, table_name, column_name, cardinality_limit=20):
    """
    Computes key statistics for a given column in a database table using SQLAlchemy.
    Also leverages information_schema for metadata (if supported).
    """

    stats = {}
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=conn.engine)

    # Validate column existence
    if column_name not in table.columns:
        raise ValueError(f"Column '{column_name}' not found in table '{table_name}'")

    col = table.c[column_name]

    # Row count & Null count
    stats["row_count"] = conn.execute(select(func.count())).scalar()
    stats["null_count"] = conn.execute(select(func.count()).where(col.is_(None))).scalar()
    stats["null_percentage"] = round((stats["null_count"] / stats["row_count"]) * 100, 2)

    # Cardinality (Unique values count)
    stats["cardinality"] = conn.execute(select(func.count(func.distinct(col)))).scalar()

    # Detect database dialect for `information_schema` support
    dialect = conn.engine.dialect.name

    if dialect in ["postgresql", "mysql"]:
        # Approximate distinct count using `pg_stats` (PostgreSQL) or `information_schema` (MySQL)
        try:
            approx_distinct_query = text(f"""
                SELECT n_distinct FROM pg_stats
                WHERE tablename = '{table_name}' AND attname = '{column_name}'
            """) if dialect == "postgresql" else text(f"""
                SELECT cardinality FROM information_schema.columns
                WHERE table_schema = DATABASE() AND table_name = '{table_name}' AND column_name = '{column_name}'
            """)

            stats["approx_distinct"] = conn.execute(approx_distinct_query).scalar()
        except:
            stats["approx_distinct"] = None

        # Column indexed?
        index_check_query = text(f"""
            SELECT COUNT(*) FROM pg_indexes
            WHERE tablename = '{table_name}' AND indexdef LIKE '% {column_name} %'
        """) if dialect == "postgresql" else text(f"""
            SELECT COUNT(*) FROM information_schema.statistics
            WHERE table_schema = DATABASE() AND table_name = '{table_name}' AND column_name = '{column_name}'
        """)

        stats["is_indexed"] = conn.execute(index_check_query).scalar() > 0

    # Determine column type and compute relevant statistics
    if isinstance(col.type, (Integer, Float, Numeric, BigInteger, SmallInteger, DECIMAL)):
        # Numeric Stats
        stats["mean"] = conn.execute(select(func.avg(col))).scalar()
        stats["std_dev"] = conn.execute(select(func.stddev(col))).scalar()
        stats["min"] = conn.execute(select(func.min(col))).scalar()
        stats["max"] = conn.execute(select(func.max(col))).scalar()
        stats["range"] = stats["max"] - stats["min"] if stats["max"] and stats["min"] else None

        # Approximate Median (using PERCENTILE_CONT if available)
        median_query = text(f"SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY {column_name}) FROM {table_name}")
        stats["median"] = conn.execute(median_query).scalar()

    elif isinstance(col.type, (String, Text, Enum)):
        if stats["cardinality"] <= cardinality_limit:
            # If unique values ≤ limit, show all unique values
            unique_values_query = select(col).distinct()
            unique_values = [row[0] for row in conn.execute(unique_values_query).fetchall()]
            stats["unique_values"] = unique_values
        else:
            # Show only top 5 most frequent values
            top_values_query = select(col, func.count()).group_by(col).order_by(func.count().desc()).limit(5)
            top_values = conn.execute(top_values_query).fetchall()
            stats["top_values"] = [dict(value=row[0], count=row[1]) for row in top_values]

        # Min/Max length (if supported)
        if dialect in ["postgresql", "mysql"]:
            min_max_len_query = text(f"""
                SELECT MIN(CHAR_LENGTH({column_name})), MAX(CHAR_LENGTH({column_name}))
                FROM {table_name}
            """)
            min_len, max_len = conn.execute(min_max_len_query).fetchone()
            stats["min_length"] = min_len
            stats["max_length"] = max_len

    elif isinstance(col.type, (DateTime, Date, TIMESTAMP)):
        # Date/Time Stats
        stats["min_date"] = conn.execute(select(func.min(col))).scalar()
        stats["max_date"] = conn.execute(select(func.max(col))).scalar()
        stats["date_range"] = (stats["max_date"] - stats["min_date"]).days if stats["max_date"] and stats["min_date"] else None

        # Most Frequent Date
        freq_date_query = select(col, func.count()).group_by(col).order_by(func.count().desc()).limit(1)
        freq_date = conn.execute(freq_date_query).fetchone()
        stats["most_frequent_date"] = freq_date[0] if freq_date else None

    return stats


def get_sample_rows(conn, table, n=10):
    metadata = MetaData()
    table = Table(table, metadata, autoload_with=conn.engine)

    # Finding primary key to order table in descending manner so we can extract latest records
    latest_column = None
    for col in table.columns:
        if col.primary_key:
            latest_column = col
            break
        if isinstance(col.type, (DateTime, Date, TIMESTAMP)):
            latest_column = col

    if latest_column is not None:
        query = select(table).order_by(latest_column.desc()).limit(n)
    else:
        query = select(table).limit(n)

    result = conn.execute(query).fetchall()
    return result


def generate_table_schema(conn, table, table_obj):
    sample_rows = get_sample_rows(conn, table, 20)
    columns = table_obj.columns
    for col, col_obj in columns.items():
        stat = get_column_stats(conn, table, col)



def generate_table_description(datasource_id):
    datasource = terno_models.DataSource.objects.get(
            id=datasource_id,
            enabled=True)   # Make this function directly take datasource as input
    mDB = terno_utils.generate_mdb(datasource)
    schema_generated = mDB.generate_schema()
    tables = mDB.get_table_dict()
    engine = terno_utils.create_db_engine(datasource.type, datasource.connection_str,
                              credentials_info=datasource.connection_json)
    conn = engine.connect()
    try:
        for table, table_obj in tables.items():
            table_schema = generate_table_schema(conn, table, table_obj)
    finally:
        conn.close()


#Table description:-
#1. Can generate only for tribal knowledge, or specific table or for specific column.
#2. Provide option whether to overwrite the current schema or first get user's approval before overwriting
#3. 