from django_filters import FilterSet, CharFilter
from apps.xc.models import App

__all__ = ['AppFilter']


class AppFilter(FilterSet):
    name = CharFilter(lookup_expr='icontains')
    system_name = CharFilter(lookup_expr='icontains')
    category = CharFilter(lookup_expr='icontains')
    owner = CharFilter(lookup_expr='icontains')
    depart_owner = CharFilter(lookup_expr='icontains')
    leader = CharFilter(lookup_expr='icontains')

    class Meta:
        model = App
        fields = []  # 所有过滤字段已显式定义

