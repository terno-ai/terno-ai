from django.http import HttpResponseForbidden
from terno.models import Organisation, OrganisationUser


class SubdomainOrganisationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        org_id_cookie = request.COOKIES.get('org_id')
        bypass_paths = ['/api', '/sso-login', '/admin']

        if any(path in request.path for path in bypass_paths) or not request.user.is_authenticated:
            if org_id_cookie:
                request.org_id = org_id_cookie
            return self.get_response(request)

        path_parts = request.path.strip('/').split('/')
        if not path_parts:
            if org_id_cookie:
                request.org_id = org_id_cookie
            return self.get_response(request)

        slug = path_parts[0]
        try:
            organisation = Organisation.objects.get(subdomain=slug)
            if not OrganisationUser.objects.filter(
                    user=request.user, organisation=organisation).exists():
                return HttpResponseForbidden("You are not allowed to access this Organisation.")
            request.org_id = organisation.id
            response = self.get_response(request)
            response.set_cookie('org_id', organisation.id)
            return response
        except Organisation.DoesNotExist:
            return HttpResponseForbidden("Organisation doesn't exist")
