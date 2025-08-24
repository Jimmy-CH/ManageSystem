
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from accounts.models import CustomPermission, Role, UserRole
from accounts.serializers import CustomPermissionSerializer, RoleSerializer, UserRoleSerializer
from accounts.permissions import CanManagePermissions, CanManageRoles, CanManageUserRoles
from common import custom_response


# from .utils import has_permission # 可能需要


class CustomPermissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing custom permissions.
    """
    queryset = CustomPermission.objects.all().order_by('name')
    serializer_class = CustomPermissionSerializer
    permission_classes = [IsAuthenticated, CanManagePermissions]  # 应用权限类
    # 可以根据需要添加搜索、过滤
    # filter_backends = [filters.SearchFilter]
    # search_fields = ['name', 'codename', 'app_label']


class RoleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing roles.
    """
    queryset = Role.objects.all().prefetch_related('permissions').order_by('name')
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, CanManageRoles]

    # 可选：添加自定义动作
    @action(detail=True, methods=['get'], url_path='users')
    def list_users(self, request, pk=None):
        """列出拥有该角色的所有用户"""
        role = self.get_object()
        user_roles = UserRole.objects.filter(role=role).select_related('user')
        user_data = [
            {
                'id': ur.user.id,
                'username': ur.user.username,
                'email': ur.user.email,
                'assigned_at': ur.assigned_at,
                'expires_at': ur.expires_at
            }
            for ur in user_roles
        ]
        return custom_response(user_data)


class UserRoleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user-role assignments.
    """
    queryset = UserRole.objects.all().select_related('user', 'role', 'assigned_by')
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated, CanManageUserRoles]

    def get_queryset(self):
        # 可以根据当前用户过滤，例如只允许查看/管理自己分配的角色，或特定部门的用户
        # 这里返回所有，实际项目中需要根据业务逻辑调整
        return super().get_queryset()

    # 可选：添加动作来管理单个用户的所有角色
    @action(detail=False, methods=['get', 'post'], url_path='user/(?P<user_id>[^/.]+)')
    def manage_user_roles(self, request, user_id=None):
        """获取或设置指定用户的所有角色"""
        user = User.objects.get(id=user_id)
        if request.method == 'GET':
            user_roles = UserRole.objects.filter(user=user, expires_at__isnull=True)
            roles_data = RoleSerializer([ur.role for ur in user_roles], many=True).data
            return custom_response({'user_id': user.id, 'username': user.username, 'roles': roles_data})

        elif request.method == 'POST':
            role_ids = request.data.get('role_ids', [])
            # 清除用户当前所有有效角色
            UserRole.objects.filter(user=user, expires_at__isnull=True).delete()
            # 分配新角色
            new_user_roles = []
            for role_id in role_ids:
                role = Role.objects.get(id=role_id)
                new_user_roles.append(UserRole(user=user, role=role, assigned_by=request.user))
            UserRole.objects.bulk_create(new_user_roles)
            return custom_response(message=f'已更新用户 {user.username} 的角色', status=status.HTTP_200_OK)
