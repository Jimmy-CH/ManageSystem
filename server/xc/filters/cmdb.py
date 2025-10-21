from django_filters import FilterSet, filters
from xc.models import Product, Application

__all__ = ['ProductFilter', 'ApplicationFilter']


class ProductFilter(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    level = filters.CharFilter(field_name='level', lookup_expr='exact')

    class Meta:
        model = Product
        fields = []


class ApplicationFilter(FilterSet):
    id = filters.CharFilter(field_name='id', lookup_expr='exact')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    cname = filters.CharFilter(field_name='cname', lookup_expr='icontains')
    system = filters.CharFilter(field_name='product_id', lookup_expr='exact')  # 根据系统过滤
    owner_id = filters.CharFilter(field_name='owner_id', lookup_expr='exact')

    class Meta:
        model = Application
        fields = []
