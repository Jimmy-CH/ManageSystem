import openpyxl
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .constants import PRIORITY_CHOICES
from .models import Category, SLAStandard, Incident, Fault
from .serializers import (
    CategorySerializer, SLAStandardSerializer, IncidentListSerializer,
    IncidentDetailSerializer, IncidentCreateUpdateSerializer,
    FaultSerializer, CategoryTreeSerializer
)
from .filters import IncidentFilter, FaultFilter, CategoryFilter
from django.utils import timezone
from .permissions import IncidentPermission
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField, Q
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IncidentPermission]  # 添加权限控制
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = CategoryFilter
    ordering_fields = ['order', 'id', 'level']
    ordering = ['order', 'id']

    @action(detail=False, methods=['get'], url_path='tree')
    def tree_view(self, request):
        """返回树形结构数据（递归）"""
        roots = Category.objects.filter(parent__isnull=True).order_by('order', 'id')
        serializer = CategoryTreeSerializer(roots, many=True)
        return Response(serializer.data)


class SLAStandardViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IncidentPermission]  # 添加权限控制
    queryset = SLAStandard.objects.all()
    serializer_class = SLAStandardSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['priority']
    ordering_fields = ['priority']
    ordering = ['priority']


class IncidentViewSet(viewsets.ModelViewSet):
    permission_classes = [IncidentPermission]  # 添加权限控制
    queryset = Incident.objects.select_related(
        'category', 'reporter', 'assignee', 'sla'
    ).prefetch_related('faults')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = IncidentFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'occurred_at', 'priority', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return IncidentListSerializer
        elif self.action == 'retrieve':
            return IncidentDetailSerializer
        return IncidentCreateUpdateSerializer

    @action(detail=True, methods=['post'], url_path='respond')
    def mark_responded(self, request, pk=None):
        """快速标记为已响应"""
        incident = self.get_object()
        if not incident.responded_at:
            incident.responded_at = timezone.now()
            incident.save(update_fields=['responded_at'])
        serializer = self.get_serializer(incident)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='resolve')
    def mark_resolved(self, request, pk=None):
        """快速标记为已解决"""
        incident = self.get_object()
        if incident.status not in [2, 3]:
            incident.status = 2
            incident.resolved_at = timezone.now()
            incident.save(update_fields=['status', 'resolved_at'])
        serializer = self.get_serializer(incident)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='statistics/general')
    def general_statistics(self, request):
        """总体统计"""
        total = self.queryset.count()
        unresolved = self.queryset.filter(status__in=[0, 1]).count()
        overdue = self.queryset.filter(
            Q(responded_at__isnull=True, sla__response_time__isnull=False) |
            Q(resolved_at__isnull=True, sla__resolve_time__isnull=False, status__in=[0, 1])
        ).count()
        avg_resolve_time = self.queryset.filter(
            resolved_at__isnull=False
        ).aggregate(
            avg=Avg(ExpressionWrapper(F('resolved_at') - F('created_at'), output_field=DurationField()))
        )['avg']

        return Response({
            "total_incidents": total,
            "unresolved": unresolved,
            "overdue": overdue,
            "average_resolve_time_hours": avg_resolve_time.total_seconds() / 3600 if avg_resolve_time else 0,
        })

    @action(detail=False, methods=['get'], url_path='statistics/by-category')
    def stats_by_category(self, request):
        """按分类统计故障数"""
        data = self.queryset.values(
            'category__id', 'category__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        return Response(data)

    @action(detail=False, methods=['get'], url_path='statistics/by-priority')
    def stats_by_priority(self, request):
        """按优先级统计"""
        data = self.queryset.values('priority').annotate(
            count=Count('id')
        ).order_by('priority')
        for item in data:
            item['priority_display'] = dict(PRIORITY_CHOICES).get(item['priority'])
        return Response(data)

    @action(detail=False, methods=['get'], url_path='statistics/trend')
    def incident_trend(self, request):
        """近30天事件趋势（按天）"""
        from django.utils import timezone
        from datetime import timedelta

        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)

        data = self.queryset.filter(
            created_at__gte=start_date, created_at__lte=end_date
        ).annotate(
            date=TruncDay('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        # 补全缺失日期
        result = []
        current = start_date
        data_dict = {item['date'].date(): item['count'] for item in data}
        while current <= end_date:
            result.append({
                "date": current.date(),
                "count": data_dict.get(current.date(), 0)
            })
            current += timedelta(days=1)

        return Response(result)

    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        """导出事件列表为 Excel"""
        queryset = self.filter_queryset(self.get_queryset())[:1000]  # 防止过大

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "故障事件列表"

        headers = [
            "ID", "标题", "分类", "优先级", "状态", "来源",
            "上报人", "处理人", "发生时间", "响应时间", "解决时间",
            "是否响应超时", "是否解决超时", "SLA等级", "创建时间"
        ]
        ws.append(headers)

        for obj in queryset:
            ws.append([
                obj.id,
                obj.title,
                obj.category.name if obj.category else "",
                obj.get_priority_display(),
                obj.get_status_display(),
                obj.get_source_display(),
                obj.reporter.username if obj.reporter else "",
                obj.assignee.username if obj.assignee else "",
                obj.occurred_at.strftime("%Y-%m-%d %H:%M") if obj.occurred_at else "",
                obj.responded_at.strftime("%Y-%m-%d %H:%M") if obj.responded_at else "",
                obj.resolved_at.strftime("%Y-%m-%d %H:%M") if obj.resolved_at else "",
                "是" if obj.is_overdue_response else "否",
                "是" if obj.is_overdue_resolve else "否",
                obj.sla.level_name if obj.sla else "",
                obj.created_at.strftime("%Y-%m-%d %H:%M")
            ])

        # 自动列宽
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col)].width = 15

        response = HttpResponse(content_type='application/vnd.openxmlformats-officed.com')
        response['Content-Disposition'] = 'attachment; filename=incidents.xlsx'
        wb.save(response)
        return response


class FaultViewSet(viewsets.ModelViewSet):
    permission_classes = [IncidentPermission]  # 添加权限控制
    queryset = Fault.objects.select_related('incident')
    serializer_class = FaultSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = FaultFilter
    ordering_fields = ['created_at', 'downtime_minutes']
    ordering = ['-created_at']





