from django.http import HttpResponseForbidden
from terno.models import Organisation


class DefaultOrganisationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        organisation = Organisation.objects.first()
        if organisation:
            request.org_id = organisation.id
        else:
            return HttpResponseForbidden("Default organisation not found.")

        response = self.get_response(request)
        return response
