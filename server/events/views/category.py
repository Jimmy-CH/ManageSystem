# views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from events.models import Category
from events.serializers import CategorySerializer
from events.filters import CategoryFilter


class CategoryViewSet(viewsets.ModelViewSet):
    """
    分类管理：支持树形结构展示、过滤、排序
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]  # 可根据需要调整
    filter_backends = [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter'
    ]
    filterset_class = CategoryFilter
    search_fields = ['name']
    ordering_fields = ['order', 'level', 'created_at']
    ordering = ['order', 'id']

    def get_queryset(self):
        """
        可选：默认只返回启用的分类
        """
        return Category.objects.filter(is_active=True).order_by('order', 'id')
