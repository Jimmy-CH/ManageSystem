# system/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/config/$', consumers.ConfigConsumer.as_asgi()),
    re_path(r'ws/menu/$', consumers.MenuUpdateConsumer.as_asgi()),
]
