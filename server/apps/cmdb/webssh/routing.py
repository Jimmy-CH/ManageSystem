
from django.urls import re_path
from .consumers import WebSSHConsumer

websocket_urlpatterns = [
    re_path(r'ws/ssh/(?P<asset_id>\d+)/$', WebSSHConsumer.as_asgi()),
]

