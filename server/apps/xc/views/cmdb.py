from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.xc.models import Product, Application
from apps.xc.serializers import ProductSerializer, ApplicationSerializer
from apps.xc.filters import ProductFilter, ApplicationFilter
from apps.xc.utils import fetch_tree


class ProductViewSet(GenericViewSet, ListModelMixin):
    queryset = Product.objects.select_related('parent')
    serializer_class = ProductSerializer
    filterset_class = ProductFilter

    @action(methods=['get'], detail=False, url_path='tree')
    def tree(self, request, *args, **kwargs):
        # 获取原始数据（必须包含 id, name, parent）
        flat_data = Product.objects.values('id', 'name', 'parent')
        tree_data = fetch_tree(root_tag=None, queryset_values=flat_data, primary_key='id')
        return Response(tree_data)


class ApplicationViewSet(ModelViewSet):
    queryset = Application.objects.select_related('product', 'owner')
    serializer_class = ApplicationSerializer
    filterset_class = ApplicationFilter
    search_fields = ['name', 'cname']
