from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('organisation', views.get_org_details, name='get_org_details'),
    path('user', views.create_user, name='create_user'),
    path('check-user', views.check_user, name='check_user'),
    path('logout', views.logout_user, name='logout_user'),
]
