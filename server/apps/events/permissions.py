
from rest_framework import permissions


class IncidentPermission(permissions.BasePermission):
    """
    自定义权限：基于 CustomPermission + Role
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # 超级管理员跳过权限检查
        if request.user.is_superuser:
            return True

        # 获取当前用户角色
        user_roles = getattr(request.user, 'roles', None)
        if not user_roles:
            return False

        # 获取当前视图所需权限
        required_perms = self.get_required_permissions(view)

        # 获取用户所有权限 code
        user_perm_codes = set()
        for role in user_roles.all():
            for perm in role.permissions.all():
                user_perm_codes.add(perm.codename)

        # 检查是否拥有任一所需权限
        return any(perm in user_perm_codes for perm in required_perms)

    def get_required_permissions(self, view):
        # 根据 action 映射所需权限 code
        mapping = {
            'list': ['view_incident'],
            'retrieve': ['view_incident'],
            'create': ['add_incident'],
            'update': ['change_incident'],
            'partial_update': ['change_incident'],
            'destroy': ['delete_incident'],
            'mark_responded': ['respond_incident'],
            'mark_resolved': ['resolve_incident'],
            'export': ['export_incident'],
            'statistics': ['view_statistics'],
        }
        return mapping.get(view.action, ['view_incident'])  # 默认需要查看权限
