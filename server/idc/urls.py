# idc/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'datacenters', views.DataCenterViewSet)
router.register(r'racks', views.RackViewSet)
router.register(r'devices', views.DeviceViewSet)
router.register(r'ipaddresses', views.IPAddressViewSet)
router.register(r'workorders', views.WorkOrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
