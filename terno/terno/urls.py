from django.urls import path
from . import views
from . import receivers

app_name = 'terno'

urlpatterns = [
    path('', views.index, name='index'),
    path('console/', views.console, name='console'),
    path('settings', views.usersettings, name='usersettings'),
    path('get-datasources', views.get_datasources, name='get_datasources'),
    path('get-sql/', views.get_sql, name='get_sql'),
    path('execute-sql', views.execute_sql, name='execute_sql'),
    path('export-sql-result', views.export_sql_result, name='export_sql_result'),
    path('get-tables/<int:datasource_id>', views.get_tables, name='get_tables'),
    path('get-user-details/', views.get_user_details, name='get_user_details'),
    path('sso-login', views.sso_login, name='sso_login'),
    path('check-user', views.check_user_exists, name='check_user_exists'),
    path('accounts/login/', views.login_page, name='login_page'),
    path('accounts/provider/callback/', views.login_page, name='provider_callback'),
    path('accounts/password/reset/', views.login_page, name='request_password_reset'),
    path('accounts/password/reset/key/<str:key>', views.reset_password, name='reset_password'),
]
