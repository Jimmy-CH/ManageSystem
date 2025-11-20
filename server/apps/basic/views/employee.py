# views.py
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
import django.db.models as models
# 模型与工具
from apps.basic.models import Employee, Org, Task
from apps.basic.serializers import EmployeeSerializer, OrgSerializer
from apps.basic.filters import EmployeeFilter, OrgFilter
from apps.basic.utils import fetch_department_tree, fetch_department_user_tree

# 第三方任务工具（建议移入项目内部，如 utils/yt_task.py）
# 假设你已将 yt_task_base 移到 utils.yt_task
# from utils.yt_task import yt_task_base


# ========== 自定义 PrefixSearchFilter（替代 libs.dj.PrefixSearchFilter）==========
from rest_framework.filters import BaseFilterBackend

__all__ = ['EmployeeViewSet', 'OrgViewSet']


class PrefixSearchFilter(BaseFilterBackend):
    """
    支持对 search_fields 进行前缀匹配（如 psncode=123 匹配 123, 1234, 123abc）
    """
    def filter_queryset(self, request, queryset, view):
        search_term = request.query_params.get('search')
        if not search_term or not getattr(view, 'search_fields', None):
            return queryset

        q = None
        for field in view.search_fields:
            # 使用 field__startswith 实现前缀搜索
            lookup = f"{field}__istartswith"  # 不区分大小写前缀
            if q is None:
                q = models.Q(**{lookup: search_term})
            else:
                q |= models.Q(**{lookup: search_term})
        return queryset.filter(q) if q else queryset


# ========== 视图集 ==========

class EmployeeViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    queryset = Employee.objects.filter(psnclscope=0)
    serializer_class = EmployeeSerializer
    filterset_class = EmployeeFilter
    filter_backends = [PrefixSearchFilter, DjangoFilterBackend]
    search_fields = ['psncode', 'psnname']

    @action(methods=['get'], detail=False, url_path='info')
    def info(self, request, *args, **kwargs):
        # 通过 context 传递字段控制（原 preset_fields='info_fields'）
        serializer = self.get_serializer(
            request.user,
            context={'preset': 'info_fields'}
        )
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path='so')
    def so(self, request):
        """获取同一部门下的用户列表"""
        try:
            deptcode = getattr(request.user, 'deptcode', None)
            if not deptcode:
                return Response({"error": "User has no deptcode"}, status=status.HTTP_400_BAD_REQUEST)

            queryset = Employee.objects.filter(psnclscope=0, deptcode=deptcode)
            queryset = self.filter_queryset(queryset)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(
                    page,
                    many=True,
                    context={'preset': 'rename_list_fields', 'request': request}
                )
                return self.get_paginated_response(serializer.data)
            else:
                serializer = self.get_serializer(
                    queryset,
                    many=True,
                    context={'preset': 'rename_list_fields', 'request': request}
                )
                return Response(serializer.data)
        except Exception as e:
            # 生产环境建议记录日志，此处简化
            return Response({})

    @action(methods=['get'], detail=False, url_path='tree')
    def tree(self, request):
        """获取部门+用户的树状结构"""
        return Response(fetch_department_user_tree())

    @action(methods=['post'], detail=False, url_path='task/update')
    def update_dingding_task(self, request, *args, **kwargs):
        """待办任务回调接口（临时）"""
        data = request.data
        task_id = data.get('id')
        if not task_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        task_qs = Task.objects.filter(id=task_id)
        if not task_qs.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)

        # task_obj = task_qs.first()
        # try:
        #     ret = yt_task_base.get_task_detail(
        #         task_id=task_id,
        #         user_code=task_obj.appoint_user_id,
        #         user_name=task_obj.appoint_user.psnname
        #     )
        #     res = ret.get('data', {})
        #     if task_obj.kind == 1:  # 漏洞任务
        #         vuln_obj = task_obj.relate_vuln.first()
        #         if vuln_obj and res.get('state') == 8:  # 已完成
        #             vuln_obj.status = 3  # 待复核
        #             vuln_obj.repair_time = dt_now()
        #             vuln_obj.save()
        # except Exception:
        #     # 临时接口，静默失败
        #     pass
        return Response()


class OrgViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    queryset = Org.objects.filter(seal_status='N')
    serializer_class = OrgSerializer
    filterset_class = OrgFilter
    filter_backends = [SearchFilter, DjangoFilterBackend]  # Org 用标准搜索即可
    search_fields = ['org_name']

    @action(methods=['get'], detail=False, url_path='select')
    def select(self, request):
        """获取部门 id、code、名称、用户数"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
                context={'preset': 'select_fields'}
            )
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(
                queryset,
                many=True,
                context={'preset': 'select_fields'}
            )
            return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path='tree')
    def tree(self, request, *args, **kwargs):
        """组织架构树"""
        return Response(fetch_department_tree())
