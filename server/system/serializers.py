
from rest_framework import serializers
from .models import SystemConfig, Menu, StorageConfig


class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = '__all__'


class MenuSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = '__all__'

    def get_children(self, obj):
        if obj.children.exists():
            return MenuSerializer(obj.children.all(), many=True).data
        return []


class StorageConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageConfig
        fields = '__all__'
