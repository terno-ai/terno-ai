from django.urls import path
from . import views
from . import receivers

app_name = 'sqlshield'

urlpatterns = [
    path('', views.index, name='index'),
    path('chat', views.chat, name='chat'),
    path('settings', views.settings, name='settings')
]
