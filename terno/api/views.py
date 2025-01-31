from terno.models import Organisation, OrganisationUser, DataSource, OrganisationDataSource
from api.utils import get_user_name
from django.contrib.auth.models import User
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from allauth.account.models import EmailAddress
from allauth.account.utils import complete_signup
from django.conf import settings


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
            organisation = Organisation.objects.create(
                name=org_name, subdomain=subdomain, owner=user, is_active=True)
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
