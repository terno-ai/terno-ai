from django.http import HttpResponseForbidden
from terno.models import Organisation
import os


class SubdomainOrganisationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not os.getenv('ENABLE_SUBDOMAIN'):
            return self.get_response(request)

        if '/api' in request.path or '/sso-login' in request.path:
            return self.get_response(request)

        host = request.get_host().split(':')[0]
        subdomain = host.split('.')[0]
        try:
            organisation = Organisation.objects.get(subdomain=subdomain)
            request.org_id = organisation.id
        except Organisation.DoesNotExist:
            return HttpResponseForbidden("Organisation doesn't exist")

        response = self.get_response(request)
        return response
