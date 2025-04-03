from django.urls import path
from . import views

app_name = 'suggestions'

urlpatterns = [
   path('get_table_and_column_description/', views.get_table_and_column_description, name='generate_table_description'),
   path('task-status/<str:task_id>/', views.get_task_status, name='task_status'),
]