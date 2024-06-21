from django.urls import path
from . import views
from . import receivers

app_name = 'terno'

urlpatterns = [
    path('', views.index, name='index'),
    path('settings', views.settings, name='settings'),
    path('get_sql_for_english_query', views.get_sql_for_english_query, name='get_sql_for_english_query'),
]
