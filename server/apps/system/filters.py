
import django_filters
from .models import SystemConfig, Menu, StorageConfig


class SystemConfigFilter(django_filters.FilterSet):
    key = django_filters.CharFilter(lookup_expr='icontains')
    group = django_filters.CharFilter(lookup_expr='exact')

    class Meta:
        model = SystemConfig
        fields = ['key', 'group']


class MenuFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    parent = django_filters.NumberFilter(field_name='parent_id')

    class Meta:
        model = Menu
        fields = ['title', 'parent', 'visible']


class StorageConfigFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    type = django_filters.ChoiceFilter(choices=StorageConfig.TYPE_CHOICES)

    class Meta:
        model = StorageConfig
        fields = ['name', 'type', 'is_default']
