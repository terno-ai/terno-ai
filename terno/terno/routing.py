from django.urls import path
from .consumers import TernoWebsockerConsumer

websocket_urlpatterns = [
    path("ws/agent/", TernoWebsockerConsumer.as_asgi()),
]
