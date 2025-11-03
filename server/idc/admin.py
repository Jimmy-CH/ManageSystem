
from django.contrib import admin
from .models import DataCenter, Rack, Device, IPAddress, WorkOrder


@admin.register(DataCenter)
class DataCenterAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'level', 'is_active']
    list_filter = ['level', 'is_active']


@admin.register(Rack)
class RackAdmin(admin.ModelAdmin):
    list_display = ['name', 'data_center', 'height', 'is_full']
    list_filter = ['data_center']


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['asset_tag', 'name', 'device_type', 'rack', 'ip_address', 'status']
    list_filter = ['device_type', 'status', 'rack__data_center']
    search_fields = ['name', 'asset_tag', 'serial_number']


@admin.register(IPAddress)
class IPAddressAdmin(admin.ModelAdmin):
    list_display = ['ip', 'is_used', 'device', 'description']
    list_filter = ['is_used']


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ['title', 'order_type', 'device', 'requester', 'status', 'created_at']
    list_filter = ['order_type', 'status', 'requester']
