from django.http import HttpResponseForbidden
from terno.models import Organisation, OrganisationUser


class SubdomainOrganisationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        bypass_paths = ['/api', '/sso-login']

        if any(path in request.path for path in bypass_paths) or not request.user.is_authenticated:
            return self.get_response(request)

        host = request.get_host()
        subdomain = host.split('.')[0]
        try:
            organisation = Organisation.objects.get(subdomain=subdomain)
            if not OrganisationUser.objects.filter(
                    user=request.user, organisation=organisation).exists():
                return HttpResponseForbidden("You are not allowed to access this Organisation.")
            request.org_id = organisation.id
            response = self.get_response(request)
            return response
        except Organisation.DoesNotExist:
            return HttpResponseForbidden("Organisation doesn't exist")
