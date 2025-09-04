
import django_filters
from events.models import Category
from events.models.constants import LEVEL_CHOICES


class CategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    level = django_filters.ChoiceFilter(choices=LEVEL_CHOICES)  # 如果你把 choices 提取为常量更好
    is_active = django_filters.BooleanFilter()
    parent = django_filters.NumberFilter(field_name='parent_id')  # 按父分类 ID 过滤
    parent__isnull = django_filters.BooleanFilter(field_name='parent', lookup_expr='isnull')

    class Meta:
        model = Category
        fields = ['name', 'level', 'is_active', 'parent', 'parent__isnull']
