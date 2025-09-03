
import django_filters
from .models import User, Role


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='username', lookup_expr='icontains')
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    role = django_filters.NumberFilter(field_name='roles')

    class Meta:
        model = User
        fields = ['username', 'email', 'is_active', 'role']


class RoleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Role
        fields = ['name']
