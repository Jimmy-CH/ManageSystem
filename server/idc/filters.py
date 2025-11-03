
import django_filters
from django.db.models import Q

from .models import DataCenter, Device, WorkOrder


class DataCenterFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')  # 模糊搜索
    level = django_filters.ChoiceFilter(choices=DataCenter.LEVEL_CHOICES)
    is_active = django_filters.BooleanFilter()
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = DataCenter
        fields = ['name', 'level', 'is_active', 'created_after', 'created_before']


class DeviceFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=Device.STATUS_CHOICES)
    data_center = django_filters.NumberFilter(field_name='rack__data_center_id')  # 通过机柜关联机房
    rack = django_filters.NumberFilter()
    ip_address = django_filters.CharFilter(field_name='ip_addresses__ip', lookup_expr='icontains')  # 关联 IP

    class Meta:
        model = Device
        fields = ['name', 'status', 'rack', 'data_center', 'ip_address']


class WorkOrderFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=WorkOrder.STATUS_CHOICES)
    device = django_filters.NumberFilter()
    requester = django_filters.NumberFilter()
    assignee = django_filters.NumberFilter()
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    keyword = django_filters.CharFilter(method='filter_keyword')  # 自定义搜索

    class Meta:
        model = WorkOrder
        fields = ['status', 'device', 'requester', 'assignee', 'created_after', 'created_before']

    def filter_keyword(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(device__name__icontains=value)
        )

