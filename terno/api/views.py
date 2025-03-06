import os
from terno.models import Organisation, OrganisationUser, DataSource, OrganisationDataSource
from api.utils import get_user_name
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from allauth.account.models import EmailAddress
from allauth.account.utils import complete_signup
from django.conf import settings
from subscription.models import LLMCredit
from django.contrib.auth import logout
import subscription.models as subs_models
import terno.utils as utils
import terno.models as models


@csrf_exempt
def get_org_details(request):
    if request.method == "GET":
        user_email = request.GET.get('user')
        user = User.objects.filter(email=user_email).first()
        if user:
            user_organisations = OrganisationUser.objects.filter(
                user=user)
            main_domain = settings.MAIN_DOMAIN

            organisation_details = []
            for orgs in user_organisations:
                org = orgs.organisation
                subdomain = org.subdomain
                url = f"https://{subdomain}.{main_domain}"
                admin_url = f"https://{subdomain}.{main_domain}/admin"

                organisation_details.append({
                    'id': org.id,
                    'name': org.name,
                    'subdomain': org.subdomain,
                    'url': url,
                    'admin_url': admin_url,
                    'owner': '',
                    'logo': org.logo,
                    'is_active': org.is_active,
                })
            return JsonResponse(
                {"status": "success", "organisations": organisation_details}, status=200)
        else:
            return JsonResponse(
                {"status": "error", "data": None}, status=200)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        user_email = data.get('user')
        org_name = data.get('name')
        subdomain = data.get('subdomain')
        try:
            user = User.objects.filter(email=user_email).first()
            llm_credit, created = LLMCredit.objects.get_or_create(owner=user)
            if created:
                llm_credit.credit = settings.FREE_LLM_CREDITS
                llm_credit.save()
            organisation = Organisation.objects.create(
                name=org_name, subdomain=subdomain, owner=user,
                llm_credit=llm_credit, is_active=True)
            org_id = organisation.id
            return JsonResponse(
                {"status": "success",
                    "message": "Organisation Created Successfully!",
                    "org_id": org_id}, status=200
            )
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": str(e)}, status=200
            )


@csrf_exempt
def create_user(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    user_email = data.get('email')
    user_password = data.get('password')
    user = User.objects.filter(email=user_email)
    if not user:
        new_user = User.objects.create_user(
            username=get_user_name(user_email),
            email=user_email,
            password=user_password,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'))
        complete_signup(request, new_user, "none", '')

        email_address = EmailAddress(user=new_user, email=new_user.email)
        email_address.primary = 1
        email_address.verified = 1
        email_address.save()

        user_details = {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email,
            'first_name': new_user.first_name,
            'last_name': new_user.last_name,
            'full_name': new_user.get_full_name(),
        }

        return JsonResponse({
            'status': 'success',
            'user': user_details}, status=200)
    else:
        return JsonResponse({
            'status': 'success',
            'user': user}, status=200)


@csrf_exempt
def check_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            if User.objects.filter(email=email).exists():
                return JsonResponse({'status': 'success', 'password_set': True})
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'error': 'Invalid JSON data'
            })
    return JsonResponse({'status': 'error', 'error': 'User not found'})


@csrf_exempt
def add_datasource(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    org_id = data.get('org_id')
    user_email = data.get('user')
    user = User.objects.filter(email=user_email).first()
    type = data.get('type')
    connection_str = data.get('connection_str')
    organisation = Organisation.objects.get(id=org_id)
    if not OrganisationUser.objects.filter(
            user=user,
            organisation=organisation).exists():
        return JsonResponse({
            'message': 'You do not belong to this organisation.'}, status=200)
    total_existing_ds = OrganisationDataSource.objects.filter(organisation=organisation).count()
    display_name = organisation.name + "_ds_" + str(total_existing_ds+1)
    datasource = DataSource.objects.create(
        type=type, connection_str=connection_str, display_name=display_name
    )
    OrganisationDataSource.objects.create(
        organisation=organisation,
        datasource=datasource
    )
    main_domain = settings.MAIN_DOMAIN
    redirect_url = f"https://{organisation.subdomain}.{main_domain}"
    return JsonResponse({
        'status': 'success',
        'message': 'Added the DataSource successfully',
        'redirect_url': redirect_url}, status=200)


@csrf_exempt
def logout_user(request):
    if request.method == 'DELETE':
        logout(request)
        return JsonResponse({'status': 'success', 'error': 'User logout'})


@csrf_exempt
def get_llm_credits(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_email = data.get('user_email')
            user = User.objects.filter(email=user_email)
            if user:
                llm_credits = subs_models.LLMCredit.objects.filter(owner=user.first())
                return JsonResponse({
                    'llm_credits': round(llm_credits.first().credit, 2) if llm_credits else 0,
                    'is_active': llm_credits.first().is_active if llm_credits else False
                })
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'error': 'Invalid JSON data'
            })
    return JsonResponse({'status': 'error', 'error': 'User not found'})


@csrf_exempt
def file_upload(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        org_id = request.POST.get('org_id')
        organisation = models.Organisation.objects.get(id=org_id)

        if not models.OrganisationUser.objects.filter(
            user=request.user,
            organisation=organisation).exists():
            return HttpResponseForbidden("You do not belong to this organisation.")

        try:
            total_existing_ds = models.OrganisationDataSource.objects.filter(organisation=organisation).count()
            display_name = f"{organisation.name}_ds_{total_existing_ds + 1}"
            datasource = models.DataSource.objects.create(
                type='sqlite',
                display_name=display_name,
                enabled=True
            )

            models.OrganisationDataSource.objects.create(
                organisation=organisation,
                datasource=datasource
            )
            for file in files:
                file_metadata = utils.parsing_csv_file(request.user, file, organisation)
                table, sqlite_url = utils.write_sqlite_from_json(file_metadata, datasource)
                utils.add_data_sqlite(sqlite_url, file_metadata, table, file)
                datasource.connection_str = sqlite_url
                datasource.save()
            return JsonResponse({'status': 'success', 'message': 'Files uploaded successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': e}, status=200)
    return JsonResponse({'status': 'error', 'error': 'Invalid request'}, status=400)
