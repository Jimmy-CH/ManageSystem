
from rest_framework import viewsets
from .models import DataCenter, Rack, Device, IPAddress, WorkOrder
from .serializers import (
    DataCenterSerializer, RackSerializer, DeviceSerializer,
    IPAddressSerializer, WorkOrderSerializer
)
from .filters import DataCenterFilter, DeviceFilter, WorkOrderFilter


class DataCenterViewSet(viewsets.ModelViewSet):
    queryset = DataCenter.objects.all()
    serializer_class = DataCenterSerializer
    filterset_class = DataCenterFilter
    search_fields = ['name', 'address']  # 用于 SearchFilter（?search=xxx）
    ordering_fields = ['created_at', 'name']


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.select_related('rack__data_center', 'owner')
    serializer_class = DeviceSerializer
    filterset_class = DeviceFilter
    search_fields = ['name', 'sn', 'model']
    ordering_fields = ['created_at', 'name']


class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.select_related('device', 'requester', 'assignee')
    serializer_class = WorkOrderSerializer
    filterset_class = WorkOrderFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at']


class RackViewSet(viewsets.ModelViewSet):
    queryset = Rack.objects.select_related('data_center')
    serializer_class = RackSerializer


class IPAddressViewSet(viewsets.ModelViewSet):
    queryset = IPAddress.objects.select_related('device')
    serializer_class = IPAddressSerializer


