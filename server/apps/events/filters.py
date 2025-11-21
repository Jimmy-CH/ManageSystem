
import django_filters
from django.db.models import Q, F

from .constants import FAULT_STATUS_CHOICES, PRIORITY_CHOICES, SOURCE_CHOICES
from .models import Incident, Fault, Category, SLAStandard
from django.utils import timezone


class IncidentFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    category = django_filters.NumberFilter(field_name='category')
    category_name = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    priority = django_filters.ChoiceFilter(choices=PRIORITY_CHOICES)
    status = django_filters.ChoiceFilter(choices=FAULT_STATUS_CHOICES)
    source = django_filters.ChoiceFilter(choices=SOURCE_CHOICES)
    reporter = django_filters.NumberFilter(field_name='reporter')
    assignee = django_filters.NumberFilter(field_name='assignee')
    sla = django_filters.NumberFilter(field_name='sla')
    is_overdue = django_filters.BooleanFilter(method='filter_overdue')
    date_range = django_filters.DateFromToRangeFilter(field_name='occurred_at')

    class Meta:
        model = Incident
        fields = [
            'title', 'category', 'category_name', 'priority', 'status',
            'source', 'reporter', 'assignee', 'sla', 'is_overdue', 'date_range'
        ]

    def filter_overdue(self, queryset, name, value):
        if value:
            now = timezone.now()
            return queryset.filter(
                Q(responded_at__isnull=True) & Q(sla__response_time__isnull=False) &
                Q(create_time__lt=now - timezone.timedelta(hours=F('sla__response_time')))
            ) | Q(
                Q(status__in=[0, 1]) & Q(sla__resolve_time__isnull=False) &
                Q(create_time__lt=now - timezone.timedelta(hours=F('sla__resolve_time')))
            )
        return queryset


class FaultFilter(django_filters.FilterSet):
    incident = django_filters.NumberFilter(field_name='incident')
    status = django_filters.ChoiceFilter(choices=FAULT_STATUS_CHOICES)
    impact_scope = django_filters.CharFilter(field_name='impact_scope', lookup_expr='icontains')

    class Meta:
        model = Fault
        fields = ['incident', 'status', 'impact_scope']


class CategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    level = django_filters.NumberFilter()
    is_active = django_filters.BooleanFilter()
    parent = django_filters.NumberFilter()

    class Meta:
        model = Category
        fields = ['name', 'level', 'is_active', 'parent']
