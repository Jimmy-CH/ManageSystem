
from rest_framework import permissions
from django.contrib.auth.models import User
from .models import Role, UserRole
from accounts.utils import has_permission


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    允许超级用户进行所有操作，其他用户只能读取。
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser


class CanManageRoles(permissions.BasePermission):
    """
    检查用户是否拥有管理角色的权限。
    """
    def has_permission(self, request, view):
        # 安全方法（GET, HEAD, OPTIONS）可能需要单独的权限，这里简化处理
        if request.method in permissions.SAFE_METHODS:
            # 例如，需要 'view_roles' 权限才能查看
            return has_permission(request.user, 'view_roles')
        else:
            # 非安全方法（POST, PUT, PATCH, DELETE）需要 'manage_roles' 权限
            return has_permission(request.user, 'manage_roles')

    def has_object_permission(self, request, view, obj):
        # 对于 PUT, PATCH, DELETE，检查对象级别
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            # 系统内置角色不可修改或删除
            if obj.is_system:
                return False
            # 可以添加更复杂的逻辑，比如只有创建者或特定管理员才能修改
        return True # has_permission 已在 has_permission 中检查


class CanManagePermissions(permissions.BasePermission):
    """
    检查用户是否拥有管理自定义权限的权限。
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return has_permission(request.user, 'view_permissions')
        else:
            return has_permission(request.user, 'manage_permissions')


class CanManageUserRoles(permissions.BasePermission):
    """
    检查用户是否拥有管理用户角色的权限。
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return has_permission(request.user, 'view_user_roles')
        else:
            return has_permission(request.user, 'manage_user_roles')
