from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'event-categories', views.EventCategoryViewSet)
router.register(r'event-components', views.EventComponentInfoViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'time-effective', views.EventTimeEffectiveViewSet)
router.register(r'time-specials', views.EventTimeSpecialViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

