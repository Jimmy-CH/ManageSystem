from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SystemConfigViewSet, MenuViewSet, StorageConfigViewSet

router = DefaultRouter()
router.register(r'system-config', SystemConfigViewSet)
router.register(r'menu', MenuViewSet)
router.register(r'storage-config', StorageConfigViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
