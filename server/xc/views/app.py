from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from xc.models import App
from xc.serializers import AppSerializer
from xc.filters import AppFilter

__all__ = ['AppViewSet']


class AppViewSet(ModelViewSet):
    queryset = App.objects.order_by('-created_time')
    serializer_class = AppSerializer
    filterset_class = AppFilter
    search_fields = ['name']

    def create(self, request, *args, **kwargs):
        # 创建可变副本（request.data 是 ImmutableQueryDict）
        data = request.data.copy()

        # 仅当 category == 1 时自定义 ID
        if data.get('category') == 1:
            with transaction.atomic():
                # 锁定相关行，防止并发 ID 冲突
                last_obj = App.objects.filter(category=1).select_for_update().order_by('-id').first()
                if last_obj is None:
                    new_id = 90000
                else:
                    new_id = last_obj.id + 1
                data['id'] = new_id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.category != 1:
            return Response(
                {'code': -1, 'msg': '非外部第三方的应用无法删除'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
