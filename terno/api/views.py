from terno.models import Organisation, OrganisationUser
from api.utils import get_or_create_user
import django.contrib.auth.models as authmodels
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
@csrf_exempt
def get_org_details(request):
    if request.method == "GET":
        user_email = request.GET.get('user')
        user = get_or_create_user(user_email)
        if user:
            user_organisations = OrganisationUser.objects.filter(
                user=user)

            organisation_details = []
            for orgs in user_organisations:
                org = orgs.organisation
                organisation_details.append({
                    # 'organisation_id': org.id,
                    'organisation_name': org.name,
                    'organisation_subdomain': org.subdomain,
                    # 'organisation_owner': org.owner,
                    # 'organisation_logo': org.logo,
                    # 'organisation_is_active': org.is_active,
                })
            return JsonResponse(
                {"status": "success", "data": organisation_details}, status=200)
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
            user = get_or_create_user(user_email)
            Organisation.objects.create(
                name=org_name, subdomain=subdomain, owner=user, is_active=True)

            return JsonResponse(
                {"status": "success", "message": "Organisation Created Successfully!"}, status=200
            )
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": str(e)}, status=200
            )


def get_user_details(request):
    user_email = request.GET.get('user')
    user = authmodels.User.objects.get(email=user_email)
    user_details = {
        # 'id': user.id,
        # 'username': user.username,
        # 'email': user.email,
        # 'first_name': user.first_name,
        # 'last_name': user.last_name,
        'full_name': user.get_full_name(),
    }

    return JsonResponse({
        'status': 'success',
        'user': user_details}, status=200)
