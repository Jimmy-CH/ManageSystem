# encoding: utf-8
# @File  : urls.py
# @Author: Jimmy Chen
# @Desc : 
# @Date  :  2025/08/13

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import (UserRegistrationView, MyTokenObtainPairView, MyTokenRefreshView,
                            UserProfileView, RoleViewSet, UserRoleViewSet, CustomPermissionViewSet)

router = DefaultRouter()
router.register(r'permissions', CustomPermissionViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'user-roles', UserRoleViewSet)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
    path('user/', UserProfileView.as_view(), name='user_profile'),
    path('', include(router.urls)),
]
