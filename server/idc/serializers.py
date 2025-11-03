
from rest_framework import serializers
from .models import DataCenter, Rack, Device, IPAddress, WorkOrder


class DataCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataCenter
        fields = '__all__'


class RackSerializer(serializers.ModelSerializer):
    data_center_name = serializers.CharField(source='data_center.name', read_only=True)

    class Meta:
        model = Rack
        fields = '__all__'


class DeviceSerializer(serializers.ModelSerializer):
    rack_name = serializers.CharField(source='rack.name', read_only=True)

    class Meta:
        model = Device
        fields = '__all__'


class IPAddressSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)

    class Meta:
        model = IPAddress
        fields = '__all__'


class WorkOrderSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    requester_name = serializers.CharField(source='requester.username', read_only=True)
    assignee_name = serializers.CharField(source='assignee.username', read_only=True)

    class Meta:
        model = WorkOrder
        fields = '__all__'
