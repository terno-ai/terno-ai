from django.shortcuts import render
from django.http import JsonResponse
import terno.models as models
import terno.utils as utils
import sqlalchemy
import sqlshield.models as shield_models


def index(request):
    return render(request, 'frontend/index.html')


def settings(request):
    return render(request, 'frontend/index.html')


def get_sql(request):
    # question = request.POST.get('prompt')
    datasource = models.DataSource.objects.first()
    role = request.user.groups.all()
    allowed_tables, allowed_columns = utils.get_admin_config_object(datasource, role)

    mDb = utils.generate_mdb(datasource)
    mDb.keep_only_tables(allowed_tables.values_list('name', flat=True))
    tables = mDb.get_table_dict()
    print(tables)

    schema_generated = mDb.generate_schema()
    question = "Get all artists"
    aSQL = utils.llm_response(question, schema_generated)

    return JsonResponse({
        'response': 'This is LLM response',
        'tables': list(tables.keys()),
        'llm_response': aSQL,
    })


def execute_sql(request):
    datasource = models.DataSource.objects.first()
    mDb = utils.generate_mdb(datasource)
    # aSQL = request.POST.get('sql')
    aSQL = 'SELECT * FROM Artist;'
    gSQL = utils.generate_native_sql(mDb, aSQL)
    data = utils.execute_native_sql(datasource, gSQL)
    return JsonResponse({
        'data': data
    })
