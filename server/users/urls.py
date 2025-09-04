from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RoleViewSet, CustomPermissionViewSet, RegisterView, LoginView, LogoutView, MeView

router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', CustomPermissionViewSet, basename='permission')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
]
