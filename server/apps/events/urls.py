
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'sla-standards', views.SLAStandardViewSet)
router.register(r'incidents', views.IncidentViewSet)
router.register(r'faults', views.FaultViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
