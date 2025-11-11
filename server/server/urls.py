"""
URL configuration for server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static

api_patterns = [
    path('users/', include('users.urls')),
    path('events/', include('events.urls')),
    path('system/', include('system.urls')),
    path('record/', include('record.urls')),
    path('basic/', include('basic.urls')),
    path('xc/', include('xc.urls')),
    path('idc/', include('idc.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/dev/', include(api_patterns)),
    # path('api/prod/', include(api_patterns)),
    # API 文档路由
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),  # OpenAPI schema
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('silk/', include('silk.urls', namespace='silk')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
