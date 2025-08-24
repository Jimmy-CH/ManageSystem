# encoding: utf-8
# @File  : urls.py
# @Author: Jimmy Chen
# @Desc : 
# @Date  :  2025/08/13

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import (UserRegistrationView, MyTokenObtainPairView, MyTokenRefreshView, UserViewSet,
                            UserProfileView, RoleViewSet, UserRoleViewSet, CustomPermissionViewSet, logout_view)

router = DefaultRouter()
router.register(r'permissions', CustomPermissionViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'user-roles', UserRoleViewSet)
router.register(r'user-profile', UserViewSet)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('login/', MyTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
    path('user/', UserProfileView.as_view(), name='user_profile'),
    path('logout/', logout_view, name='logout'),


    path('', include(router.urls)),
]
