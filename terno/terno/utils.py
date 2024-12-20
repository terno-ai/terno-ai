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


def console_llm_response(user, messages):
    try:
        llm = LLMFactory.create_llm()
        response = llm.get_response(messages)
        generated_sql = response
    except Exception as e:
        logger.exception(e)
        return {'status': 'error', 'error': str(e)}

    return {'status': 'success', 'generated_sql': generated_sql}


def llm_response(user, user_query, db_schema, organisation, datasource):
    try:
        llm = LLMFactory.create_llm(organisation)
        pipeline = create_pipeline(llm, 'one_step_pipeline', user, db_schema, datasource, user_query)
        response = get_response_from_pipeline(pipeline)
        generated_sql = response[0][0]
    except Exception as e:
        logger.exception(e)
        return {'status': 'error', 'error': str(e)}

    return {'status': 'success', 'generated_sql': generated_sql}


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
