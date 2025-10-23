from django.shortcuts import get_object_or_404
from django.db.models import Q, F
from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied

# 假设你的 models 和 serializers 在 basic 应用中
from basic.models import (
    Role, RoleConnEmployee, RoleConnOrg, Menu, RoleConnMenu,
    Permission, RoleConnPermission, MenuConnPermission
)
from basic.serializers import (
    RoleSerializer, RoleConnEmployeeSerializer, RoleConnOrgSerializer,
    MenuSerializer, RoleConnMenuSerializer, PermissionSerializer,
    RoleConnPermissionSerializer, MenuConnPermissionSerializer
)
from basic.filters import RoleFilter, MenuFilter, PermissionFilter
from basic.utils import fetch_menu_tree, fetch_menu_permission_tree


__all__ = [
    'RoleViewSet', 'RoleConnEmployeeViewSet', 'RoleConnOrgViewSet',
    'MenuViewSet', 'RoleConnMenuViewSet', 'PermissionViewSet',
    'RoleConnPermissionViewSet', 'MenuConnPermissionViewSet'
]


# ======================
# 通用批量关联基类（仅使用 DRF 原生）
# ======================
class BulkRelationViewSet(viewsets.GenericViewSet):
    foreign_key_field = None  # e.g., 'employee'
    reverse_field = None      # e.g., 'role'

    def _get_common_data(self, request):
        return {
            'created_by': getattr(request.user, 'psncode', 'system'),
            self.reverse_field: request.data.get(self.reverse_field),
            f"{self.foreign_key_field}s": request.data.get(f"{self.foreign_key_field}s")
        }

    @action(methods=['post'], detail=False)
    def add(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=self._get_common_data(request),
            context={'preset_fields': f'add_{self.foreign_key_field}_fields'}
        )
        serializer.is_valid(raise_exception=True)
        getattr(serializer, f'add_{self.foreign_key_field}s')()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=False)
    def adjust(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=self._get_common_data(request),
            context={'preset_fields': f'adjust_{self.foreign_key_field}_fields'}
        )
        serializer.is_valid(raise_exception=True)
        getattr(serializer, f'adjust_{self.foreign_key_field}s')()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ======================
# Role 视图集
# ======================
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.prefetch_related('employees', 'orgs', 'menus')
    serializer_class = RoleSerializer
    filterset_class = RoleFilter
    filter_backends = [filters.DjangoFilterBackend]

    PROTECTED_ALIASES = {'admin', 'system-admin', 'default-users'}

    def _is_protected(self, obj):
        return obj.alias in self.PROTECTED_ALIASES

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if self._is_protected(instance):
            return Response(
                {'detail': '该角色不支持修改角色名'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if self._is_protected(instance):
            return Response(
                {'detail': '预设角色不可删除'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    @action(methods=['get'], detail=True)
    def menus_permissions(self, request, pk=None):
        menu_ids = RoleConnMenu.objects.filter(role_id=pk).values_list('menu_id', flat=True)
        permission_ids = RoleConnPermission.objects.filter(role_id=pk).values_list('permission_id', flat=True)
        return Response({
            'menus': list(menu_ids),
            'permissions': list(permission_ids)
        })

    @action(methods=['post'], detail=True)
    def adjust_menus_permissions(self, request, pk=None):
        serializer = self.get_serializer(
            data={
                'created_by': getattr(request.user, 'psncode', 'system'),
                'role': pk,
                'menus': request.data.get('menus'),
                'permissions': request.data.get('permissions'),
            },
            context={'preset_fields': 'adjust_menus_permissions_fields'}
        )
        serializer.is_valid(raise_exception=True)
        serializer.adjust_menus_permissions()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ======================
# 角色-员工关联
# ======================
class RoleConnEmployeeViewSet(BulkRelationViewSet):
    queryset = RoleConnEmployee.objects.select_related('role', 'employee')
    serializer_class = RoleConnEmployeeSerializer
    foreign_key_field = 'employee'
    reverse_field = 'role'

    @action(methods=['get'], detail=True)
    def employees(self, request, pk=None):
        queryset = RoleConnEmployee.objects.filter(role_id=pk)
        serializer = self.get_serializer(queryset, many=True, context={'preset_fields': 'employee_fields'})
        return Response(serializer.data)

    @action(methods=['get'], detail=True, url_path='roles')
    def roles(self, request, pk=None):
        queryset = self.get_queryset().filter(employee_id=pk).prefetch_related('role')
        serializer = self.get_serializer(queryset, many=True, context={'preset_fields': 'role_fields'})
        return Response(serializer.data)


# ======================
# 角色-组织关联
# ======================
class RoleConnOrgViewSet(BulkRelationViewSet):
    queryset = RoleConnOrg.objects.select_related('role', 'org')
    serializer_class = RoleConnOrgSerializer
    foreign_key_field = 'org'
    reverse_field = 'role'

    @action(methods=['get'], detail=True)
    def orgs(self, request, pk=None):
        queryset = self.get_queryset().filter(role_id=pk)
        serializer = self.get_serializer(queryset, many=True, context={'preset_fields': 'org_fields'})
        return Response(serializer.data)


# ======================
# 菜单视图集
# ======================
class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    filterset_class = MenuFilter
    filter_backends = [filters.DjangoFilterBackend]

    @action(methods=['get'], detail=False)
    def tree(self, request):
        return Response(fetch_menu_tree())

    @action(methods=['get'], detail=False, url_path='menu-permission-tree')
    def menu_permission_tree(self, request):
        return Response(fetch_menu_permission_tree())

    @action(methods=['get'], detail=False, url_path='level-menus')
    def level_menus(self, request):
        level = request.query_params.get('level', 1)
        exclude = request.query_params.get('self') or 0
        try:
            exclude = int(exclude)
        except ValueError:
            exclude = 0
        queryset = self.get_queryset().filter(~Q(id=exclude), level=level).order_by('order')
        serializer = self.get_serializer(queryset, many=True, context={'preset_fields': 'menus_fields'})
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def permissions(self, request, pk=None):
        perms = MenuConnPermission.objects.filter(menu_id=pk).annotate(
            permission_name=F('permission__name'),
            permission_alias=F('permission__alias')
        ).values('permission_id', 'permission_name', 'permission_alias')
        return Response(list(perms))

    @action(methods=['get'], detail=True, url_path='user-permissions')
    def user_permissions(self, request, pk=None):
        user = request.user
        role_aliases = set(user.roles.values_list('alias', flat=True))
        role_aliases.add('default-users')

        menu_perm_ids = MenuConnPermission.objects.filter(menu_id=pk).values_list('permission_id', flat=True)

        if 'admin' in role_aliases:
            permissions = Permission.objects.filter(id__in=menu_perm_ids)
        else:
            user_perm_ids = RoleConnPermission.objects.filter(
                role__alias__in=role_aliases,
                permission_id__in=menu_perm_ids
            ).values_list('permission_id', flat=True).distinct()
            permissions = Permission.objects.filter(id__in=user_perm_ids)

        serializer = PermissionSerializer(permissions, many=True, context={'preset_fields': 'simple_list_fields'})
        return Response(serializer.data)


# ======================
# 权限视图集
# ======================
class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    filterset_class = PermissionFilter
    filter_backends = [filters.DjangoFilterBackend]

    @action(methods=['get'], detail=False)
    def select(self, request):
        bound_ids = MenuConnPermission.objects.values_list('permission_id', flat=True)
        qs = Permission.objects.exclude(id__in=bound_ids)
        filtered_qs = self.filter_queryset(qs)
        page = self.paginate_queryset(filtered_qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'preset_fields': 'simple_list_fields'})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(filtered_qs, many=True, context={'preset_fields': 'simple_list_fields'})
        return Response(serializer.data)


# ======================
# 角色-权限关联
# ======================
class RoleConnPermissionViewSet(BulkRelationViewSet):
    queryset = RoleConnPermission.objects.select_related('role', 'permission')
    serializer_class = RoleConnPermissionSerializer
    foreign_key_field = 'permission'
    reverse_field = 'role'


# ======================
# 菜单-权限关联
# ======================
class MenuConnPermissionViewSet(viewsets.GenericViewSet):
    queryset = MenuConnPermission.objects.select_related('menu', 'permission')
    serializer_class = MenuConnPermissionSerializer

    @action(methods=['post'], detail=False, url_path='add-permission')
    def add_permission(self, request):
        serializer = self.get_serializer(
            data={
                'created_by': getattr(request.user, 'psncode', 'system'),
                'menu': request.data.get('menu'),
                'permission': request.data.get('permission')  # 应为 permission ID
            },
            context={'preset_fields': 'add_permission_fields'}
        )
        serializer.is_valid(raise_exception=True)
        serializer.add_permissions()
        return Response({'detail': '新增权限成功'}, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False, url_path='delete-permission')
    def delete_permission(self, request):
        serializer = self.get_serializer(
            data={
                'created_by': getattr(request.user, 'psncode', 'system'),
                'menu': request.data.get('menu'),
                'permission': request.data.get('permission')
            },
            context={'preset_fields': 'delete_permission_fields'}
        )
        serializer.is_valid(raise_exception=True)
        serializer.delete_permission()
        return Response({'detail': '删除权限成功'}, status=status.HTTP_204_NO_CONTENT)


# ======================
# 角色-菜单关联（保留兼容）
# ======================
class RoleConnMenuViewSet(viewsets.GenericViewSet):
    queryset = RoleConnMenu.objects.select_related('role', 'menu')
    serializer_class = RoleConnMenuSerializer

    @action(methods=['get'], detail=True, url_path='menus-permissions')
    def menus_permissions(self, request, pk=None):
        role = get_object_or_404(Role, id=pk)
        if role.alias == 'admin':
            menu_ids = Menu.objects.values_list('id', flat=True)
            permission_ids = Permission.objects.values_list('id', flat=True)
        else:
            menu_ids = RoleConnMenu.objects.filter(role_id=pk).values_list('menu_id', flat=True)
            permission_ids = RoleConnPermission.objects.filter(role_id=pk).values_list('permission_id', flat=True)
        return Response({
            'menus': list(menu_ids),
            'permissions': list(permission_ids)
        })

    @action(methods=['post'], detail=False)
    def adjust(self, request):
        serializer = self.get_serializer(
            data=request.data,
            context={'preset_fields': 'adjust_fields'}
        )
        serializer.is_valid(raise_exception=True)
        serializer.adjust()
        return Response(status=status.HTTP_204_NO_CONTENT)

