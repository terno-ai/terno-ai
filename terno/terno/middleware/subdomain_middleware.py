from django.http import HttpResponseForbidden
from terno.models import Organisation, OrganisationUser


class SubdomainOrganisationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if '/api' in request.path or '/sso-login' in request.path or not request.user.is_authenticated:
            return self.get_response(request)

        path_parts = request.path.strip('/').split('/')
        if not path_parts:
            return self.get_response(request)

        slug = path_parts[0]
        try:
            organisation = Organisation.objects.get(subdomain=slug)
            if not OrganisationUser.objects.filter(
                    user=request.user, organisation=organisation).exists():
                return HttpResponseForbidden("You are not allowed to access this Organisation.")
            request.org_id = organisation.id
        except Organisation.DoesNotExist:
            return HttpResponseForbidden("Organisation doesn't exist")

        response = self.get_response(request)
        return response
