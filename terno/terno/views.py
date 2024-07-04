from django.shortcuts import render
from django.http import JsonResponse
import terno.models as models
import terno.utils as utils
import json


def index(request):
    return render(request, 'frontend/index.html')


def settings(request):
    return render(request, 'frontend/index.html')


def get_datasource(request):
    datasources = models.DataSource.objects.all()
    data = [{'name': d.display_name, 'id': d.id} for d in datasources]
    return JsonResponse({
        'datasources': data
    })


def get_sql(request):
    data = json.loads(request.body)
    question = data.get('prompt')
    print('ques', question)
    datasource = models.DataSource.objects.first()
    role = request.user.groups.all()
    allowed_tables, allowed_columns = utils.get_admin_config_object(datasource, role)

    mDb = utils.generate_mdb(datasource)
    mDb.keep_only_tables(allowed_tables.values_list('name', flat=True))
    tables = mDb.get_table_dict()
    print(tables)

    schema_generated = mDb.generate_schema()
    generated_sql = utils.llm_response(question, schema_generated)

    return JsonResponse({
        'generated_sql': generated_sql,
    })


def execute_sql(request):
    data = json.loads(request.body)
    aSQL = data.get('sql')
    status = 'failed'
    datasource = models.DataSource.objects.first()
    mDb = utils.generate_mdb(datasource)
    status, response = utils.generate_native_sql(mDb, aSQL)
    if status == 'failed':
        return JsonResponse({
            'status': status,
            'error': response
        })
    status, data = utils.execute_native_sql(datasource, response)
    if status == 'failed':
        return JsonResponse({
            'status': status,
            'error': response
        })
    else:
        return JsonResponse({
            'status': status,
            'table_data': data
        })


def get_tables(request, datasource_id):
    if datasource_id:
        print('here is dsid{datasource_id}', datasource_id)
        datasource = models.DataSource.objects.get(id=datasource_id)
    else:
        datasource = models.DataSource.objects.first()
    role = request.user.groups.all()
    allowed_tables, allowed_columns = utils.get_admin_config_object(datasource, role)
    return JsonResponse({
        'allowed_tables': list(allowed_tables.values_list('name', flat=True)),
        # 'allowed_columns': allowed_columns
    })
