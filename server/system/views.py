from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser

from system.models import SystemConfig, Menu, StorageConfig
from system.serializers import SystemConfigSerializer, MenuSerializer, StorageConfigSerializer
from rest_framework.response import Response


class ConfigViewSet(viewsets.ModelViewSet):
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'])
    def group(self, request):
        """按分组返回配置"""
        group = request.query_params.get('group', 'basic')
        configs = SystemConfig.objects.filter(group=group)
        return Response({item.key: item.value for item in configs})

    @action(detail=False, methods=['post'])
    def batch_save(self, request):
        """批量保存配置"""
        data = request.data
        for key, value in data.items():
            SystemConfig.objects.filter(key=key).update(value=value)
        return Response({"message": "保存成功"})


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.filter(parent__isnull=True).order_by('order')
    serializer_class = MenuSerializer
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        # 返回树形结构
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class StorageConfigViewSet(viewsets.ModelViewSet):
    queryset = StorageConfig.objects.all()
    serializer_class = StorageConfigSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        StorageConfig.objects.filter(is_default=True).update(is_default=False)
        storage = self.get_object()
        storage.is_default = True
        storage.save()
        return Response({"message": "默认存储设置成功"})
