
import django_filters
from django_filters import rest_framework as filters
from .models import Role, CustomPermission, User


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='username', lookup_expr='icontains')
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    role = django_filters.NumberFilter(field_name='roles')

    class Meta:
        model = User
        fields = ['username', 'email', 'is_active', 'role']


class RoleFilter(filters.FilterSet):
    # 1. 精确匹配字段
    status = filters.BooleanFilter(field_name='status', label='状态')
    importance = filters.NumberFilter(field_name='importance', label='重要程度')

    # 2. 模糊搜索（名称、描述）
    name = filters.CharFilter(field_name='name', lookup_expr='icontains', label='角色名称')
    description = filters.CharFilter(field_name='description', lookup_expr='icontains', label='描述')

    # 3. 权限过滤（多对多）→ 按权限ID过滤
    permission_id = filters.ModelMultipleChoiceFilter(
        field_name='permissions',
        queryset=CustomPermission.objects.all(),
        label='权限ID',
        conjoined=False  # False = OR（满足任一权限即可），True = AND（必须包含所有权限）
    )

    # 4. 权限名称过滤（可选）
    permission_name = filters.CharFilter(
        field_name='permissions__name',
        lookup_expr='icontains',
        label='权限名称'
    )

    class Meta:
        model = Role
        fields = [
            'name',
            'description',
            'status',
            'importance',
            'permission_id',
            'permission_name',
        ]