import io
import terno.models as models
from django.contrib.auth.models import Group, Permission
from sqlshield.shield import Session
from sqlshield.models import MDatabase
import sqlalchemy
from terno.llm.base import LLMFactory
import math
from django.template import Template, Context, Engine
import logging
from terno.pipeline.pipeline import Pipeline
from terno.pipeline.step import Step
from terno.prompt import query_generation
import csv
from django.http import HttpResponse
from django.utils import timezone
from django.core.cache import cache
from terno.llm.base import NoSufficientCreditsException, NoDefaultLLMException
from subscription.models import LLMCredit
from subscription.utils import deduct_llm_credits
from django.conf import settings
import terno.llm as llms
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Boolean


logger = logging.getLogger(__name__)


def create_db_engine(db_type, connection_string, **kwargs):
    if db_type == 'bigquery':
        credentials_info = kwargs.get('credentials_info')
        if not credentials_info:
            raise ValueError("BigQuery requires credentials_info")
        engine = sqlalchemy.create_engine(connection_string, credentials_info=credentials_info)
    else:
        engine = sqlalchemy.create_engine(connection_string)

    return engine


def prepare_mdb(datasource, roles):
    role_ids = sorted(roles.values_list('id', flat=True))
    cache_key = f"datasource_{datasource.id}_roles_{'_'.join(map(str, role_ids))}"
    cached_mdb = cache.get(cache_key)

    if cached_mdb is not None:
        return cached_mdb

    allowed_tables, allowed_columns = get_admin_config_object(datasource, roles)

    mDb = generate_mdb(datasource)
    mDb.keep_only_tables(allowed_tables.values_list('name', flat=True))
    keep_only_columns(mDb, allowed_tables, allowed_columns)

    tables = mDb.get_table_dict()
    update_table_descriptions(tables)
    update_filters(tables, datasource, roles)

    cache.set(cache_key, mDb, timeout=3600)

    return mDb


def keep_only_columns(mDb, tables, columns):
    '''
    As there is no keep_only_columns method on mDb
    we use the drop columns method on table
    '''
    for _, table in mDb.tables.items():
        table_obj = tables.filter(name=table.name)
        if table_obj:
            table.pub_name = table_obj.first().public_name
            keep_columns = columns.filter(table__name=table.name).values_list('name', flat=True)
            table_columns = models.TableColumn.objects.filter(
                table__in=table_obj).values_list('name', flat=True)
            drop_columns = set(table_columns).difference(keep_columns)
            table.drop_columns(drop_columns)
            for _, col in table.columns.items():
                allowed_column = columns.filter(table=table_obj.first(), name=col.name)
                if allowed_column:
                    col.pub_name = allowed_column.first().public_name


def update_table_descriptions(tables):
    for tbl_name, tbl_object in tables.items():
        table_description = models.Table.objects.filter(
            name=tbl_name).first().description
        tbl_object.desc = table_description


def _get_base_filters(datasource):
    tbl_base_filters = {}
    for trf in models.TableRowFilter.objects.filter(data_source=datasource):
        filter_str = trf.filter_str.strip()
        if len(filter_str) > 0:
            tbl_base_filters[trf.table.name] = ["(" + filter_str + ")"]
    return tbl_base_filters


def _get_grp_filters(datasource, roles):
    tbls_grp_filter = {}  # key: table_name, value = [filter1, filter2]
    for gtrf in models.GroupTableRowFilter.objects.filter(data_source=datasource, group__in=roles):
        filter_str = gtrf.filter_str.strip()
        if len(filter_str) > 0:
            tbl_name = gtrf.table.name
            lst = []
            if tbl_name not in tbls_grp_filter:
                tbls_grp_filter[tbl_name] = lst
            else:
                lst = tbls_grp_filter[tbl_name]
            lst.append("(" + filter_str + ")")
    return tbls_grp_filter


def _merge_grp_filters(tbl_base_filters, tbls_grp_filter):
    '''
    Updates the row filter for each table in tables based on TableRowFIlter or GroupTableFilter.
    argument `tables' should be a dictionary of name and Mtable.

    '''
    for tbl, grp_filters in tbls_grp_filter.items():
        role_filter_str = " ( " + ' OR '.join(grp_filters) + " ) "
        all_filters = []
        if tbl in tbl_base_filters:
            all_filters = tbl_base_filters[tbl]
        else:
            tbl_base_filters[tbl] = all_filters
        all_filters.append(role_filter_str)


def update_filters(tables, datasource, roles):
    tbl_base_filters = _get_base_filters(datasource) # table_name -> ["(a=2)", "(x = 1) or (y = 2)"]
    tbls_grp_filter = _get_grp_filters(datasource, roles)
    _merge_grp_filters(tbl_base_filters, tbls_grp_filter)
    for tbl, filters_list in tbl_base_filters.items():
        if len(filters_list) > 0:
            tables[tbl].filters = 'WHERE ' + ' AND '.join(filters_list)


def get_all_group_tables(datasource, roles):
    # Get all tables from datasource
    global_tables = models.Table.objects.filter(
        data_source=datasource)
    # Get private tables in datasource
    private_table_object = models.PrivateTableSelector.objects.filter(
        data_source=datasource).first()
    if private_table_object:
        private_tables_ids = private_table_object.tables.all().values_list('id', flat=True)
        # Get tables excluding private tables
        global_tables = global_tables.exclude(id__in=private_tables_ids)

    # Add tables accessible by the user's groups
    group_tables_object = models.GroupTableSelector.objects.filter(
        group__in=roles,
        tables__data_source=datasource).first()
    if group_tables_object:
        group_tables = group_tables_object.tables.all()
        all_group_tables = global_tables.union(group_tables)
        # Using subquery to allow filtering after union
        all_group_tables = models.Table.objects.filter(
            id__in=all_group_tables.values('id'))
    else:
        all_group_tables = global_tables
    return all_group_tables


def get_all_group_columns(datasource, tables, roles):
    tables_ids = list(tables.values_list('id', flat=True))
    # Get all columns for the tables
    table_columns = models.TableColumn.objects.filter(table_id__in=tables_ids)
    # Get private columns for tables
    private_columns_object = models.PrivateColumnSelector.objects.filter(
        data_source=datasource).first()
    if private_columns_object:
        private_columns_ids = private_columns_object.columns.all().values_list('id', flat=True)
        table_columns = table_columns.exclude(id__in=private_columns_ids)

    # Add columns accessible by the user's groups
    group_columns_object = models.GroupColumnSelector.objects.filter(
        group__in=roles,
        columns__table__in=tables).first()
    if group_columns_object:
        group_columns = group_columns_object.columns.all()
        all_table_columns = table_columns.union(group_columns)
        # Using subquery to allow filtering after union
        all_table_columns = models.TableColumn.objects.filter(
            id__in=all_table_columns.values('id'))
    else:
        all_table_columns = table_columns
    return all_table_columns


# @cache_page(24*3600)
def get_admin_config_object(datasource, roles):
    """
    Return Tables and columns accessible for user
    """
    all_group_tables = get_all_group_tables(datasource, roles)
    group_columns = get_all_group_columns(datasource, all_group_tables, roles)
    return all_group_tables, group_columns


def console_llm_response(user, human_prompt):
    try:
        organisation = models.OrganisationUser.objects.get(user=user).organisation
        llm, is_default_llm = LLMFactory.create_llm(organisation)
        message = llm.create_message_for_llm(system_prompt="You are a helpful assistant skilled in data analysis and schema inference.", ai_prompt="", human_prompt=human_prompt)
        response = llm.get_response(message)
        response_sql = response
    except NoSufficientCreditsException as e:
        logger.exception(e)
        return {'status': 'error', 'error': str(e)}
    except NoDefaultLLMException as e:
        logger.exception(e)
        return {'status': 'error', 'error': str(e)}
    except Exception as e:
        logger.exception(e)
        return {'status': 'error', 'error': str(e)}

    if is_default_llm:
        organisation = models.OrganisationUser(user=user)
        try:
            deduct_llm_credits(organisation.llm_credit, response)
        except Exception as e:
            logger.exception(e)
            disable_default_llm()
    response_sql['status'] = 'success'
    return response_sql


def llm_response(user, user_query, db_schema, organisation, datasource):
    try:
        llm, is_default_llm = LLMFactory.create_llm(organisation)
        pipeline = create_pipeline(llm, 'one_step_pipeline', user, db_schema, datasource, user_query)
        response = get_response_from_pipeline(pipeline)
        response_sql = response[0][0]
    except NoSufficientCreditsException as e:
        logger.exception(e)
        return {'status': 'error', 'error': str(e)}
    except NoDefaultLLMException as e:
        logger.exception(e)
        return {'status': 'error', 'error': str(e)}
    except Exception as e:
        logger.exception(e)
        return {'status': 'error', 'error': str(e)}

    if is_default_llm:
        try:
            if organisation.name == 'demo':
                llm_credit, created = LLMCredit.objects.get_or_create(owner=user)
                if created:
                    llm_credit.credit = settings.FREE_LLM_CREDITS
                    llm_credit.save()
                deduct_llm_credits(llm_credit, response)
            else:
                deduct_llm_credits(organisation.llm_credit, response)
        except Exception as e:
            logger.exception(e)
            disable_default_llm()

    response_sql['status'] = 'success'
    return response_sql


def create_pipeline(llm, name, user, db_schema, datasource, user_query):
    steps = []
    if name == 'one_step_pipeline':
        pipeline = Pipeline()
        system_message = query_generation.query_generation_system_prompt\
            .format(dialect_name=datasource.dialect_name,
                    dialect_version=datasource.dialect_version)
        ai_message = query_generation.query_generation_ai_prompt\
            .format(database_schema=db_schema)
        human_message = query_generation.query_generation_human_prompt\
            .format(question=user_query, dialect_name=datasource.dialect_name)
        messages = llm.create_message_for_llm(system_message, ai_message,
                                              human_message)
        step1 = Step(llm, messages)
        steps.append(step1)
    else:
        raise Exception("Invalid Pipeline Name")

    for step in steps:
        pipeline.add_step(step)
        models.PromptLog.objects.create(user=user, llm_prompt=step.messages)
    return pipeline


def get_response_from_pipeline(pipeline):
    return pipeline.run()


# @cache_page(24*3600)
def generate_mdb(datasource):
    tables = {}
    dbtables = models.Table.objects.filter(data_source=datasource)
    columns = {}
    for dbt in dbtables:
        tables[dbt.name] = {
            'name': dbt.name,
            'public_name': dbt.public_name,
            'description': dbt.description
        }
        dbcolumns = models.TableColumn.objects.filter(table=dbt)
        column_data = []
        for dbc in dbcolumns:
            column_data.append({
                'name': dbc.name,
                'pub_name': dbc.public_name,
                'type': dbc.data_type,
                'primary_key': '',
                'nullable': '',
                'desc': ''
            })
        columns[dbt.name] = column_data

    foreign_keys = {}
    for dbt in dbtables:
        dbfks = models.ForeignKey.objects.filter(constrained_table=dbt)
        fk_data = []
        for dbfk in dbfks:
            fk_data.append({
                'constrained_columns': [dbfk.constrained_columns.name],
                'referred_table': dbfk.referred_table.name,
                'referred_columns': [dbfk.referred_columns.name],
                'referred_schema': '',
            })
        foreign_keys[dbt.name] = fk_data

    mdb = MDatabase.from_data(tables, columns, foreign_keys)
    return mdb


def generate_native_sql(mDb, user_sql):
    sess = Session(mDb, '')
    try:
        native_sql = sess.generateNativeSQL(user_sql)
        return {
            'status': 'success',
            'native_sql': native_sql
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


def execute_native_sql(datasource, native_sql, page, per_page):
    engine = create_db_engine(datasource.type, datasource.connection_str,
                              credentials_info=datasource.connection_json)
    with engine.connect() as con:
        try:
            execute_result = con.execute(sqlalchemy.text(native_sql))
            table_data = prepare_table_data_from_execute(execute_result, page, per_page)
            return {
                'status': 'success',
                'table_data': table_data
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }


def export_native_sql_result(datasource, native_sql):
    engine = sqlalchemy.create_engine(datasource.connection_str)
    utc_time = timezone.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_name = f'terno_{datasource.display_name}_{utc_time}.csv'
    with engine.connect() as con:
        execute_result = con.execute(sqlalchemy.text(native_sql))
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        writer = csv.writer(response)
        writer.writerow(execute_result.keys())  # Write the headers (column names)
        writer.writerows(execute_result)  # Write all rows of data
        return response


def prepare_table_data_from_execute(execute_result, page, per_page):
    table_data = {}
    table_data['columns'] = list(execute_result.keys())

    fetch_result = execute_result.fetchall()

    total_count = execute_result.rowcount
    if total_count <= 0:
        total_count = len(fetch_result)
    total_pages = math.ceil(total_count // per_page)
    table_data['total_pages'] = total_pages
    table_data['row_count'] = total_count
    table_data['page'] = page

    offset = (page - 1) * per_page
    paginated_results = fetch_result[offset:offset+per_page]
    table_data['data'] = []

    for row in paginated_results:
        data = {}
        for i, column in enumerate(table_data['columns']):
            data[column] = row[i]
        table_data['data'].append(data)
    return table_data


'''
def extract_limit_from_query(query):
    expression = sqlglot.parse_one(query)
    limit_expression = expression.args.get('limit')
    offset_expression = expression.args.get('offset')

    limit, offset = None, None
    if limit_expression:
        limit = int(limit_expression.expression.this)
    if offset_expression:
        offset = int(offset_expression.expression.this)

    return limit, offset


def add_limit_offset_to_query(query, set_limit, set_offset):
    expression = sqlglot.parse_one(query)
    query = expression.limit(set_limit).offset(set_offset).sql()
    return query
'''


def substitute_variables(template_str, context_dict):
    engine = Engine(
        debug=True,
        libraries={'terno_extras': 'terno.templatetags.terno_extras'}
    )
    template_str = "{% load terno_extras %}" + template_str
    template = Template(template_str, engine=engine)
    context = Context(context_dict)
    return template.render(context)


def create_org_owner_group():
    group = Group.objects.create(name="org_owner")
    permissions = Permission.objects.all()
    group.permissions.set(permissions)


def disable_default_llm():
    default_org = models.Organisation.objects.filter(subdomain='terno-root').first()
    if default_org:
        # Get the default LLM (subdomain 'terno-root') if available
        organisation_llms = models.OrganisationLLM.objects.filter(
            organisation=default_org,
            llm__enabled=True
        )

        for org_llm in organisation_llms:
            org_llm.llm.enabled = False
            org_llm.llm.save()


def count_non_null(row):
    return sum(1 for value in row if value.strip())


def sample_data_for_llm(file, no_of_rows):
    file.seek(0)
    reader = csv.reader(io.StringIO(file.read().decode('utf-8')))
    data = list(reader)

    columns = data[0]
    num_columns = len(columns)
    rows = data[0:]
    null_counts_column = {col: 0 for col in columns}
    for row in rows:
        for i, value in enumerate(row):
            if not value.strip():  
                null_counts_column[columns[i]] += 1

    rows_with_count = [(index, count_non_null(row), row) for index, row in enumerate(rows)]
    rows_sorted = sorted(rows_with_count, key=lambda x: (-x[1], x[0])) 
    top_five_rows = [row for _, _, row in rows_sorted[:no_of_rows]]

    return top_five_rows, num_columns, null_counts_column


def parsing_csv_file(user, file, organisation):
    sample_data, num_columns, null_values_count_in_columns = sample_data_for_llm(file,5)

    json_response_format = {
        "table_name": "table_name_here",
        "columns": [
            {
                "name": "column_name_1",
                "type": "data type here",
                "nullable": True,
                "description": "Short description here."
            },
            {
                "name": "column_name_2",
                "type": "data type here",
                "nullable": False,
                "description": "Short description here."
            }
        ],
        "header_row": "True or false"
    }

    prompt = f"""
    You are given a DataFrame sample in tabular form:

    {sample_data}

    Analyze the DataFrame and determine the most appropriate table name based on its structure and contents.
    - Examine the column names and data patterns in the provided sample.
    - Based on the observed data, infer a suitable name for the table that best represents its purpose.
    - Ensure the table name is meaningful, concise, and aligns with standard database naming conventions.
    - Table name should be in lowercase and snake_case format.

    Analyze each column based on this DataFrame sample. For each column, provide:
    - The count of columns in the DataFrame is {num_columns}. Make sure the order of columns is preserved.
    - Column names can be present in first row, if not Suggest human friendly column names for every column.
    - Column names should be in lowercase and snake_case format.
    - If column names are present set header_row to true otherwise false. 
    - Data type (choose from: INT, SMALLINT, BIGINT, DECIMAL, FLOAT, CHAR, VARCHAR, DATE, TIMESTAMP)
    - Nullable status : If null count for that column is greater than 0 then it is nullable otherwise not : The null counts for each column are as follows: {null_values_count_in_columns}.
    - A short and clear description (one sentence maximum) of the content in each column.

    Respond strictly in the JSON format shown below without any explanations or markdown formatting. JSON format:

    {json_response_format}
    """
    response = console_llm_response(user, prompt)
    return response


def write_sqlite_from_json(data, datasource):
    type_mapping = {
        'int': Integer,
        'str': String,
        'float': Float,
        'bool': Boolean
    }
    sqlite_url = 'sqlite:///' + datasource.display_name + '.db'
    engine = create_engine(sqlite_url, echo=True)
    metadata = MetaData()
    columns = []
    for col in data['columns']:
        col_name = col['name']
        col_type = type_mapping.get(col['type'], String)

        if col_name.lower() == 'id':
            column = Column(col_name, col_type, primary_key=True, nullable=col['nullable'],
                            comment=col.get('description', ''))
        else:
            column = Column(col_name, col_type, nullable=col['nullable'],
                            comment=col.get('description', ''))
        columns.append(column)

    table = Table(data['table_name'], metadata, *columns)
    metadata.create_all(engine)
    return table, sqlite_url


def add_data_sqlite(sqlite_url, data, table, file):
    engine = create_engine(sqlite_url, echo=True)
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            file.seek(0)
            reader = csv.reader(file.read().decode('utf-8').splitlines())

            if data.get('header_row', True):
                header = next(reader, None)

            for row in reader:
                ordered_row = {}
                for index, col in enumerate(data['columns']):
                    col_name = col['name']
                    value = row[index] if index < len(row) else None
                    if col['type'] == 'int':
                        ordered_row[col_name] = int(value) if value else None
                    elif col['type'] == 'float':
                        ordered_row[col_name] = float(value) if value else None
                    else:
                        ordered_row[col_name] = value
                connection.execute(table.insert().values(**ordered_row))
            trans.commit()
        except Exception as e:
            trans.rollback()
            print("Error inserting data:", e)
