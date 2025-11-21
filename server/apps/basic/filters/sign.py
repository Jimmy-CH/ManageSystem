from django_filters import FilterSet, CharFilter
from apps.basic.models import Sign

__all__ = ['SignFilter']


class SignFilter(FilterSet):
    comment = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Sign
        fields = ['is_active', 'apply_user_id', 'application_id']
