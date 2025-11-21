"""
ASGI config for server project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
# 显式导入各 app 的路由
from apps.system.routing import websocket_urlpatterns as system_patterns
from apps.cmdb.webssh.routing import websocket_urlpatterns as webssh_patterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
# 合并路由列表
websocket_urlpatterns = system_patterns + webssh_patterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
