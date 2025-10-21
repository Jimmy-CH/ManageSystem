from django_filters import FilterSet, CharFilter, NumberFilter
from basic.models import OperateLog

__all__ = ['OperateLogFilter']


class OperateLogFilter(FilterSet):
    # 模糊匹配模型名（如 "user", "order"）
    instance = CharFilter(lookup_expr='icontains')

    # 精确匹配 ID（假设为数字）
    instance_id = NumberFilter()

    class Meta:
        model = OperateLog
        fields = []
