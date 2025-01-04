from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden


class ConnectSocialAccountAdapter(DefaultSocialAccountAdapter):
    def on_authentication_error(self, request, provider, error=None,
                                exception=None, extra_context=None):
        print(provider)
        print(error)
        print(exception)
        print(extra_context)

    def pre_social_login(self, request, sociallogin):
        print(request.user)
        print(user_email(sociallogin.user))
        email = user_email(sociallogin.user)
        if email:
            try:
                user = User.objects.get(email=email)
                sociallogin.connect(request, user)
            except User.DoesNotExist:
                return HttpResponseForbidden("Please contact your organization administrator for access.")


class ConnectAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False
