"""
ASGI config for server project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# 设置环境变量
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

# 第一步：先获取 ASGI application，这会触发 django.setup()
application = get_asgi_application()

# 第二步：只有在这之后，才能安全导入包含模型的 routing 模块！
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# 动态导入 routing（此时 Django 已 ready）
from apps.cmdb.webssh.routing import websocket_urlpatterns as webssh_patterns
from apps.system.routing import websocket_urlpatterns as system_patterns
websocket_urlpatterns = system_patterns + webssh_patterns

# 重新构建支持 WebSocket 的 application
application = ProtocolTypeRouter({
    "http": application,  # 复用已初始化的 http app
    "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
})

