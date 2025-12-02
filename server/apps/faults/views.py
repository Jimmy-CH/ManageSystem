from rest_framework import viewsets
from .models import (
    EventCategory, EventComponentInfo, Event,
    EventDeviceInfo, EventHandleProcess,
    EventTimeEffective, EventTimeSpecial
)
from .serializers import (
    EventCategorySerializer, EventComponentInfoSerializer,
    EventSerializer, EventTimeEffectiveSerializer,
    EventTimeSpecialSerializer
)
from .filters import (
    EventFilter, EventCategoryFilter, EventComponentInfoFilter,
    EventTimeEffectiveFilter, EventTimeSpecialFilter
)


class EventCategoryViewSet(viewsets.ModelViewSet):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer
    filterset_class = EventCategoryFilter
    search_fields = ['name']
    ordering_fields = ['update_time', 'depth']


class EventComponentInfoViewSet(viewsets.ModelViewSet):
    queryset = EventComponentInfo.objects.select_related('event_sub')
    serializer_class = EventComponentInfoSerializer
    filterset_class = EventComponentInfoFilter
    search_fields = ['component_name', 'component_brand', 'component_model']


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.prefetch_related(
        'device_info', 'event_handle_process'
    ).select_related().order_by('-update_time')
    serializer_class = EventSerializer
    filterset_class = EventFilter
    search_fields = ['mal_id', 'registrant', 'handler', 'description']
    ordering_fields = ['start_time', 'duration', 'update_time']


class EventTimeEffectiveViewSet(viewsets.ModelViewSet):
    queryset = EventTimeEffective.objects.all()
    serializer_class = EventTimeEffectiveSerializer
    filterset_class = EventTimeEffectiveFilter
    ordering_fields = ['update_time']


class EventTimeSpecialViewSet(viewsets.ModelViewSet):
    queryset = EventTimeSpecial.objects.all()
    serializer_class = EventTimeSpecialSerializer
    filterset_class = EventTimeSpecialFilter
    ordering_fields = ['update_time']

