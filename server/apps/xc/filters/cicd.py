from django_filters import FilterSet, filters
from apps.xc.models import Project, Version

__all__ = ['ProjectFilter', 'VersionFilter']


class ProjectFilter(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Project
        fields = []


class VersionFilter(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    project = filters.CharFilter(field_name='project_id', lookup_expr='exact')

    class Meta:
        model = Version
        fields = []
