
import django_filters
from django_filters import rest_framework as filters
from .models import Role, CustomPermission, User


class UserFilter(django_filters.FilterSet):
    # 精确匹配
    department = django_filters.CharFilter(field_name='department', lookup_expr='exact')
    position = django_filters.CharFilter(field_name='position', lookup_expr='exact')
    status = django_filters.BooleanFilter(field_name='status')

    # 数字范围
    importance = django_filters.NumberFilter(field_name='importance')
    importance__gte = django_filters.NumberFilter(field_name='importance', lookup_expr='gte')
    importance__lte = django_filters.NumberFilter(field_name='importance', lookup_expr='lte')

    # 角色筛选（多对多）
    roles = django_filters.ModelMultipleChoiceFilter(
        field_name='roles',
        queryset=Role.objects.all(),
        conjoined=False  # False = OR（任一角色匹配），True = AND（必须包含所有角色）
    )

    # 手机号模糊搜索（可选）
    username = django_filters.CharFilter(field_name='username', lookup_expr='icontains')
    phone = django_filters.CharFilter(field_name='phone', lookup_expr='icontains')

    # 创建时间范围
    created_at__gte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = User
        fields = [
            'department',
            'position',
            'status',
            'importance',
            'roles',
            'phone',
        ]


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