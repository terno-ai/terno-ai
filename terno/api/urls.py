from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('organisation', views.get_org_details, name='get_org_details'),
    path('user', views.create_user, name='create_user'),
    path('check-user', views.check_user, name='check_user'),
    path('add-datasource', views.add_datasource, name='add_datasource'),
    path('logout', views.logout_user, name='logout_user'),
    path('get-llm-credits', views.get_llm_credits, name='get_llm_credits'),
    path('file-upload', views.file_upload, name='file_upload'),
]
