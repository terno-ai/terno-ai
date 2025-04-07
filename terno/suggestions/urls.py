from django.urls import path
from . import views

app_name = 'suggestions'

urlpatterns = [
   path('get_table_and_column_description/', views.get_table_and_column_description, name='generate_table_description'),
]