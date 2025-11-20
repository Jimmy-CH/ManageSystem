from django_filters import FilterSet, CharFilter
from apps.basic.models import Role, RoleConnEmployee, Menu, Permission
from django.db.models import Exists, OuterRef

__all__ = ['RoleFilter', 'MenuFilter', 'PermissionFilter']


class RoleFilter(FilterSet):
    name = CharFilter(lookup_expr='icontains')
    psncode = CharFilter(method='filter_by_psncode')
    psnname = CharFilter(method='filter_by_psnname')

    def filter_by_psncode(self, queryset, name, value):
        return queryset.filter(
            Exists(
                RoleConnEmployee.objects.filter(
                    role=OuterRef('pk'),
                    employee__psncode=value
                )
            )
        )

    def filter_by_psnname(self, queryset, name, value):
        return queryset.filter(
            Exists(
                RoleConnEmployee.objects.filter(
                    role=OuterRef('pk'),
                    employee__psnname=value
                )
            )
        )

    class Meta:
        model = Role
        fields = []


class MenuFilter(FilterSet):
    name = CharFilter(lookup_expr='icontains')
    kind = CharFilter()  # lookup_expr='exact' 是默认值，可省略

    class Meta:
        model = Menu
        fields = []


class PermissionFilter(FilterSet):
    name = CharFilter(lookup_expr='icontains')
    description = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Permission
        fields = []
