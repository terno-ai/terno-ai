from terno.models import OrganisationUser
import django.contrib.auth.models as authmodels
from django.http import JsonResponse


# Create your views here.
def get_org_details(request):
    if request.method == "GET":
        user_email = request.GET.get('user')
        user = authmodels.User.objects.get(email=user_email)
        if user:
            user_organisations = OrganisationUser.objects.filter(
                user=user).values_list('organisation', flat=True)

            organisation_details = []
            for orgs in user_organisations:
                org = orgs.organisation
                organisation_details.append({
                    'organisation_id': org.id,
                    'organisaiton_name': org.name,
                    'organisation_subdomain': org.subdomain,
                    'organisation_owner': org.owner,
                    'organisation_logo': org.logo,
                    'organisation_is_active': org.is_active,
                })
            return JsonResponse(
                {"status": "success", "organisations": organisation_details}, status=200)
        else:
            return JsonResponse(
                {"status": "error", "organisations": None}, status=200)

    if request.method == "POST":
        return JsonResponse(
            {"status": "success", "message": "Organisation Created Successfully!"}, status=200)


def get_user_details(request):
    user_email = request.GET.get('user')
    user = authmodels.User.objects.get(email=user_email)
    user_details = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }

    return JsonResponse({
        'status': 'success',
        'user': user_details}, status=200)
