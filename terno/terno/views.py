from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.urls import reverse
import terno.models as models
import terno.utils as utils
import json
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.exceptions import ObjectDoesNotExist
import logging
from django.conf import settings
import jwt
from django.contrib.auth.models import User
from urllib.parse import unquote
from allauth.account.utils import perform_login


logger = logging.getLogger(__name__)


@login_required
@ensure_csrf_cookie
def index(request):
    return render(request, 'frontend/index.html')


@ensure_csrf_cookie
def login_page(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('terno:index'))
    return render(request, 'frontend/index.html')


@ensure_csrf_cookie
def reset_password(request, key):
    return render(request, 'frontend/index.html')


@staff_member_required
def console(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        datasource_id = data.get('datasourceId')
        system_prompt = data.get('systemPrompt')
        assistant_message = data.get('assistantMessage')
        user_prompt = data.get('userPrompt')
        org_id = request.org_id

        organisation = models.Organisation.objects.get(id=org_id)

        try:
            if not models.OrganisationUser.objects.filter(
                user=request.user,
                organisation=organisation).exists():
                return HttpResponseForbidden("You do not belong to this organisation.")

            datasource = models.DataSource.objects.get(
                    id=datasource_id,
                    enabled=True,
                    organisationdatasource__organisation=organisation
                )
        except ObjectDoesNotExist:
            return JsonResponse({
                'status': 'error',
                'error': 'No Datasource found.'
            })
        roles = request.user.groups.all()

        models.QueryHistory.objects.create(
            user=request.user, data_source=datasource,
            data_type='user_prompt', data=user_prompt)

        mDB = utils.prepare_mdb(datasource, roles)
        schema_generated = mDB.generate_schema()

        context_dict = {
            'db_schema': schema_generated,
            'dialect_name': datasource.dialect_name,
            'dialect_version': datasource.dialect_version,
        }
        system_prompt = utils.substitute_variables(template_str=system_prompt,
                                                   context_dict=context_dict)
        assistant_message = utils.substitute_variables(template_str=assistant_message,
                                                       context_dict=context_dict)
        user_prompt = utils.substitute_variables(template_str=user_prompt,
                                                 context_dict=context_dict)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": assistant_message},
            {"role": "user", "content": user_prompt},
        ]

        models.QueryHistory.objects.create(
            user=request.user, data_source=datasource,
            data_type='user_prompt', data=user_prompt)

        llm_response = utils.llm_response(
            request.user, messages, organisation)

        if llm_response['status'] == 'error':
            return JsonResponse({
                'status': llm_response['status'],
                'error': llm_response['error'],
            })

        models.QueryHistory.objects.create(
            user=request.user, data_source=datasource,
            data_type='generated_sql', data=llm_response['generated_sql'])

        return JsonResponse({
            'status': llm_response['status'],
            'generated_prompt': str(messages),
            'generated_sql': llm_response['generated_sql'],
        })
    return render(request, 'frontend/index.html')


def usersettings(request):
    return render(request, 'frontend/index.html')


@login_required
def get_datasources(request):
    org_id = request.org_id
    organisation = models.Organisation.objects.get(id=org_id)

    if not models.OrganisationUser.objects.filter(
        user=request.user,
        organisation=organisation).exists():
        return HttpResponseForbidden("You do not belong to this organisation.")

    datasources = models.DataSource.objects.filter(
            enabled=True,
            organisationdatasource__organisation=organisation
        )
    data = [{'name': d.display_name, 'id': d.id} for d in datasources]
    return JsonResponse({
        'datasources': data
    })


@login_required
def get_sql(request):
    data = json.loads(request.body)
    datasource_id = data.get('datasourceId')
    question = data.get('prompt')
    org_id = request.org_id

    organisation = models.Organisation.objects.get(id=org_id)

    if not models.OrganisationUser.objects.filter(
        user=request.user,
        organisation=organisation).exists():
        return HttpResponseForbidden("You do not belong to this organisation.")

    try:
        datasource = models.DataSource.objects.get(
            id=datasource_id,
            enabled=True,
            organisationdatasource__organisation=organisation)
    except ObjectDoesNotExist:
        return JsonResponse({
            'status': 'error',
            'error': 'No Datasource found.'
        })
    roles = request.user.groups.all()

    models.QueryHistory.objects.create(
        user=request.user, data_source=datasource,
        data_type='user_prompt', data=question)

    mDB = utils.prepare_mdb(datasource, roles)
    schema_generated = mDB.generate_schema()
    llm_response = utils.llm_response(
        request.user, question, schema_generated, organisation, datasource)

    if llm_response['status'] == 'error':
        return JsonResponse({
            'status': llm_response['status'],
            'error': llm_response['error'],
        })

    models.QueryHistory.objects.create(
        user=request.user, data_source=datasource,
        data_type='generated_sql', data=llm_response['generated_sql'])

    return JsonResponse({
        'status': llm_response['status'],
        'generated_sql': llm_response['generated_sql'],
    })


@login_required
def execute_sql(request):
    data = json.loads(request.body)
    user_sql = data.get('sql')
    datasource_id = data.get('datasourceId')
    page = data.get('page', 1)
    per_page = data.get('per_page', 25)
    org_id = request.org_id

    organisation = models.Organisation.objects.get(id=org_id)

    if not models.OrganisationUser.objects.filter(
        user=request.user,
        organisation=organisation).exists():
        return HttpResponseForbidden("You do not belong to this organisation.")

    try:
        datasource = models.DataSource.objects.get(
            id=datasource_id,
            enabled=True,
            organisationdatasource__organisation=organisation)
    except ObjectDoesNotExist:
        return JsonResponse({
            'status': 'error',
            'error': 'No Datasource found.'
        })
    roles = request.user.groups.all()

    models.QueryHistory.objects.create(
        user=request.user, data_source=datasource,
        data_type='user_executed_sql', data=user_sql)

    mDB = utils.prepare_mdb(datasource, roles)

    native_sql_response = utils.generate_native_sql(
        mDB, user_sql, datasource.dialect_name)

    if native_sql_response['status'] == 'error':
        return JsonResponse({
            'status': native_sql_response['status'],
            'error': native_sql_response['error'],
        })

    models.QueryHistory.objects.create(
        user=request.user,
        data_source=datasource,
        data_type='actual_executed_sql',
        data=native_sql_response['native_sql'])

    execute_sql_response = utils.execute_native_sql(
        datasource, native_sql_response['native_sql'],
        page=page, per_page=per_page)

    if execute_sql_response['status'] == 'error':
        return JsonResponse({
            'status': execute_sql_response['status'],
            'error': execute_sql_response['error'],
        })

    return JsonResponse({
        'status': execute_sql_response['status'],
        'table_data': execute_sql_response['table_data']
    })


@login_required
def export_sql_result(request):
    data = json.loads(request.body)
    user_sql = data.get('sql')
    datasource_id = data.get('datasourceId')
    org_id = request.org_id

    organisation = models.Organisation.objects.get(id=org_id)
    if not models.OrganisationUser.objects.filter(
        user=request.user,
        organisation=organisation).exists():
        return HttpResponseForbidden("You do not belong to this organisation.")

    try:
        datasource = models.DataSource.objects.get(
            id=datasource_id,
            enabled=True,
            organisationdatasource__organisation=organisation)
    except ObjectDoesNotExist:
        return JsonResponse({
            'status': 'error',
            'error': 'No Datasource found.'
        })
    roles = request.user.groups.all()

    models.QueryHistory.objects.create(
        user=request.user, data_source=datasource,
        data_type='user_executed_sql', data=user_sql)

    mDB = utils.prepare_mdb(datasource, roles)

    native_sql_response = utils.generate_native_sql(
        mDB, user_sql, datasource.dialect_name)

    if native_sql_response['status'] == 'error':
        return JsonResponse({
            'status': native_sql_response['status'],
            'error': native_sql_response['error'],
        })

    models.QueryHistory.objects.create(
        user=request.user,
        data_source=datasource,
        data_type='actual_executed_sql',
        data=native_sql_response['native_sql'])

    execute_sql_response = utils.export_native_sql_result(
        datasource, native_sql_response['native_sql'])

    return execute_sql_response


@login_required
def get_tables(request, datasource_id):
    org_id = request.org_id
    organisation = models.Organisation.objects.get(id=org_id)

    if not models.OrganisationUser.objects.filter(
        user=request.user,
        organisation=organisation).exists():
        return HttpResponseForbidden("You do not belong to this organisation.")

    try:
        datasource = models.DataSource.objects.get(
            id=datasource_id,
            enabled=True,
            organisationdatasource__organisation=organisation)
    except ObjectDoesNotExist:
        return JsonResponse({
            'status': 'error',
            'error': 'No Datasource found.'
        })
    role = request.user.groups.all()
    allowed_tables, allowed_columns = utils.get_admin_config_object(
        datasource, role)
    table_data = []
    for table in allowed_tables:
        column = allowed_columns.filter(table_id=table)
        column_data = list(column.values('public_name', 'data_type'))
        result = {
            'table_name': table.public_name,
            'table_description': table.description,
            'column_data': column_data
        }
        table_data.append(result)
    return JsonResponse({
        'status': 'success',
        'table_data': table_data
    })


@login_required
def get_user_details(request):
    user = request.user
    org_id = request.org_id
    organisation = models.Organisation.objects.get(id=org_id)

    if not models.OrganisationUser.objects.filter(
            user=request.user,
            organisation=organisation).exists():
        return HttpResponseForbidden("You do not belong to this organisation.")

    return JsonResponse({
        'id': user.id,
        'username': user.username,
        'is_admin': organisation.owner == user
    })


def sso_login(request):
    token = request.GET.get('token')
    org_id = request.GET.get('org_id')
    redirect_to = request.GET.get('redirect_to')

    if not token:
        return HttpResponseForbidden("Missing token")

    try:
        payload = jwt.decode(token, settings.SSO_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return HttpResponseForbidden("Token expired")
    except jwt.InvalidTokenError:
        return HttpResponseForbidden("Invalid token")

    user = User.objects.get(email=payload["email"])

    perform_login(request, user, email_verification="none")

    redirect_url = unquote(redirect_to)
    org_user = models.OrganisationUser.objects.filter(user=user, organisation__id=org_id)
    if org_user:
        org_user = org_user.first()
        redirect_url = f"https://{org_user.organisation.subdomain}.{settings.MAIN_DOMAIN}"
        if redirect_to == 'admin':
            redirect_url += '/admin'
        elif redirect_to == 'add-ds':
            redirect_url += '/admin/terno/datasource'
        elif redirect_to == 'add-llm':
            redirect_url += '/admin/terno/llmconfiguration'
        return HttpResponseRedirect(redirect_url)
    return HttpResponseForbidden


def file_upload(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        org_id = request.org_id
        organisation = models.Organisation.objects.get(id=org_id)

        if not models.OrganisationUser.objects.filter(
            user=request.user,
            organisation=organisation).exists():
            return HttpResponseForbidden("You do not belong to this organisation.")

        try:
            total_existing_ds = models.OrganisationDataSource.objects.filter(organisation=organisation).count()
            display_name = f"{organisation.name}_ds_{total_existing_ds + 1}"
            for file in files:
                file_metadata_response = utils.parsing_csv_file(request.user, file, organisation)
                if file_metadata_response['status'] == 'error':
                    return JsonResponse({'status': 'error', 'error': file_metadata_response['error']})
                print("THIS is the llm response", file_metadata_response['response'])

                sqlite_write_response = utils.write_sqlite_from_json(file_metadata_response['response'], display_name)
                if sqlite_write_response['status'] == 'error':
                    return JsonResponse({'status': 'error', 'error': sqlite_write_response['error']})

                add_data_response = utils.add_data_sqlite(sqlite_write_response['sqlite_url'],
                                                          file_metadata_response['response'],
                                                          sqlite_write_response['table'], file)
                if add_data_response['status'] == 'error':
                    return JsonResponse({'status': 'error', 'error': add_data_response['error']})

                datasource = models.DataSource.objects.create(
                    type='Generic',
                    display_name=display_name,
                    connection_str=sqlite_write_response['sqlite_url'],
                    enabled=True
                )

                models.OrganisationDataSource.objects.create(
                    organisation=organisation,
                    datasource=datasource
                )

                datasource.connection_str = sqlite_write_response['sqlite_url']
                datasource.save()
                logger.info(f"File Uploaded Successfully: {file_metadata_response['response']}")
            return JsonResponse({'status': 'success', 'message': 'Files uploaded successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': e}, status=200)
    return JsonResponse({'status': 'error', 'error': 'Invalid request'}, status=400)
