"""
操作日志视图集
"""
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from apps.basic.models import OperateLog
from apps.basic.serializers import OperateLogSerializer
from apps.basic.filters import OperateLogFilter

__all__ = ['OperateLogViewSet']


class OperateLogViewSet(ModelViewSet):
    """
    操作日志管理接口
    - 默认按操作时间倒序排列
    - 支持通过 OperateLogFilter 进行字段过滤（如操作人、模块、时间范围等）
    """
    queryset = OperateLog.objects.select_related().order_by('-operate_time')
    serializer_class = OperateLogSerializer
    filterset_class = OperateLogFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['operate_time', 'id']  # 允许前端指定排序字段（可选）
    ordering = ['-operate_time']              # 默认排序（与 queryset 一致，可省略）


