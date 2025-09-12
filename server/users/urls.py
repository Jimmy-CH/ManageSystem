from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RoleViewSet, CustomPermissionViewSet, RegisterView, LoginView, LogoutView, MeView, \
    CustomPermissionCreateView

router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', CustomPermissionViewSet, basename='permissions')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('info/', MeView.as_view(), name='info'),
    path('permission/', CustomPermissionCreateView.as_view(), name='permission'),
    path('', include(router.urls)),
]
