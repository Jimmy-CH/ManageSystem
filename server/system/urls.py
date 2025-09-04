from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConfigViewSet, StorageConfigViewSet, MenuViewSet

router = DefaultRouter()
router.register(r'config', ConfigViewSet, basename='config')
router.register(r'storage', StorageConfigViewSet, basename='storage')
router.register(r'menu', MenuViewSet, basename='menu')


urlpatterns = [
    path('', include(router.urls)),
]
