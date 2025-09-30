# views.py
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import SystemConfig, Menu, StorageConfig
from .serializers import SystemConfigSerializer, MenuSerializer, StorageConfigSerializer
from .filters import SystemConfigFilter, MenuFilter, StorageConfigFilter


class SystemConfigViewSet(viewsets.ModelViewSet):
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SystemConfigFilter
    search_fields = ['key', 'label']
    ordering_fields = ['id']


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MenuFilter
    search_fields = ['title']
    ordering_fields = ['order']

    # 可选：在 list 时只返回根节点（前端自己递归展开）
    def get_queryset(self):
        if self.action == 'list':
            return Menu.objects.filter(parent__isnull=True)
        return Menu.objects.all()  # retrieve/update/destroy 需要完整 queryset


class StorageConfigViewSet(viewsets.ModelViewSet):
    queryset = StorageConfig.objects.all()
    serializer_class = StorageConfigSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StorageConfigFilter
    search_fields = ['name']
    ordering_fields = ['id']
