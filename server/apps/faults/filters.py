import django_filters
from .models import (
    Event, EventCategory, EventComponentInfo,
    EventTimeEffective, EventTimeSpecial
)


class EventFilter(django_filters.FilterSet):
    start_time_min = django_filters.NumberFilter(field_name="start_time", lookup_expr='gte')
    start_time_max = django_filters.NumberFilter(field_name="start_time", lookup_expr='lte')
    level = django_filters.MultipleChoiceFilter(choices=Event.EVENT_LEVEL_CHOICE)
    category = django_filters.MultipleChoiceFilter(choices=Event.EVENT_CHOICE)
    mal_id = django_filters.CharFilter(lookup_expr='icontains')
    registrant = django_filters.CharFilter(lookup_expr='icontains')
    handler = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Event
        fields = [
            'category', 'level', 'mal_result', 'is_overtime',
            'maintenance_status', 'solution_type',
            'first_level', 'subdivision', 'third_level', 'fourth_level'
        ]


class EventCategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    active = django_filters.ChoiceFilter(choices=((1, "启用"), (2, "禁用")))

    class Meta:
        model = EventCategory
        fields = ['name', 'active', 'parent']


class EventComponentInfoFilter(django_filters.FilterSet):
    component_name = django_filters.CharFilter(lookup_expr='icontains')
    component_brand = django_filters.CharFilter(lookup_expr='icontains')
    event_sub = django_filters.NumberFilter()

    class Meta:
        model = EventComponentInfo
        fields = ['component_name', 'component_brand', 'event_sub']


class EventTimeEffectiveFilter(django_filters.FilterSet):
    first_level = django_filters.CharFilter(lookup_expr='icontains')
    second_level = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = EventTimeEffective
        fields = ['category', 'first_level', 'second_level', 'level']


class EventTimeSpecialFilter(django_filters.FilterSet):
    component_name = django_filters.CharFilter(lookup_expr='icontains')
    component_brand = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = EventTimeSpecial
        fields = ['component_name', 'component_brand']

