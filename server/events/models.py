from django.db import models
from common import BaseModel
from events.constants import LEVEL_CHOICES, PRIORITY_CHOICES, SOURCE_CHOICES, FAULT_STATUS_CHOICES
from users.models import User
from django.utils import timezone


class Category(BaseModel):

    name = models.CharField("分类名称", max_length=100, db_index=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="父分类"
    )
    level = models.IntegerField("层级", choices=LEVEL_CHOICES, default=1)
    order = models.PositiveIntegerField("排序", default=0)
    is_active = models.BooleanField("是否启用", default=True)

    class Meta:
        verbose_name = "分类"
        verbose_name_plural = "分类管理"
        ordering = ['order', 'id']

    def __str__(self):
        return self.name

    def get_ancestors(self, include_self=False):
        """获取所有祖先节点（从根到父）"""
        ancestors = []
        parent = self.parent
        while parent:
            ancestors.append(parent)
            parent = parent.parent
        if include_self:
            ancestors.insert(0, self)
        return list(reversed(ancestors))

    def get_full_path_name(self):
        """返回完整路径名称，如：家电 > 电视 > 液晶电视 > 4K液晶电视"""
        ancestors = self.get_ancestors(include_self=True)
        return " > ".join([anc.name for anc in ancestors])


# SLA 响应/解决时效单位（小时）
class SLAStandard(BaseModel):
    level_name = models.CharField("SLA等级名称", max_length=50, unique=True)  # 如 P1-P4
    priority = models.IntegerField("对应优先级", choices=PRIORITY_CHOICES, unique=True)
    response_time = models.FloatField("响应时限（小时）", help_text="从创建到首次响应")
    resolve_time = models.FloatField("解决时限（小时）", help_text="从创建到关闭")
    description = models.TextField("说明", blank=True, null=True)

    class Meta:
        verbose_name = "SLA标准"
        verbose_name_plural = "SLA标准管理"
        ordering = ['priority']

    def __str__(self):
        return f"{self.level_name} (优先级: {self.get_priority_display()})"


class Incident(BaseModel):
    title = models.CharField("事件标题", max_length=200)
    description = models.TextField("事件描述")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="分类"
    )
    priority = models.IntegerField("优先级", choices=PRIORITY_CHOICES, default=2)
    source = models.IntegerField("来源", choices=SOURCE_CHOICES, default=1)
    reporter = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reported_incidents',
        verbose_name="上报人"
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_incidents',
        verbose_name="处理人"
    )
    status = models.IntegerField("状态", choices=FAULT_STATUS_CHOICES, default=0)
    occurred_at = models.DateTimeField("发生时间", default=timezone.now)
    responded_at = models.DateTimeField("首次响应时间", blank=True, null=True)
    resolved_at = models.DateTimeField("解决时间", blank=True, null=True)
    is_active = models.BooleanField("是否有效", default=True)

    # 关联 SLA
    sla = models.ForeignKey(
        SLAStandard,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="SLA标准"
    )

    class Meta:
        verbose_name = "事件"
        verbose_name_plural = "事件管理"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_overdue_response(self):
        """是否响应超时"""
        if not self.sla or not self.responded_at:
            return False
        expected = self.created_at + timezone.timedelta(hours=self.sla.response_time)
        return timezone.now() > expected and not self.responded_at

    @property
    def is_overdue_resolve(self):
        """是否解决超时"""
        if not self.sla or self.status in [2, 3]:
            return False
        expected = self.created_at + timezone.timedelta(hours=self.sla.resolve_time)
        return timezone.now() > expected

        # 👇 缓存旧值

    _original_responded_at = None
    _original_resolved_at = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始化时缓存当前值
        self._original_responded_at = self.responded_at
        self._original_resolved_at = self.resolved_at

    def save(self, *args, **kwargs):
        # 判断字段是否变更
        is_responded = (self.responded_at is not None) and (self._original_responded_at is None)
        is_resolved = (self.resolved_at is not None) and (self._original_resolved_at is None)

        super().save(*args, **kwargs)

        # 触发信号或直接调用推送（推荐用信号）
        from .signals import handle_incident_update
        handle_incident_update(self, is_responded, is_resolved)

        # 更新缓存
        self._original_responded_at = self.responded_at
        self._original_resolved_at = self.resolved_at


class Fault(BaseModel):
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='faults',
        verbose_name="所属事件"
    )
    detail = models.TextField("故障详情")
    root_cause = models.TextField("根本原因", blank=True, null=True)
    solution = models.TextField("解决方案", blank=True, null=True)
    downtime_minutes = models.PositiveIntegerField("停机时长（分钟）", default=0)
    impact_scope = models.CharField("影响范围", max_length=200, blank=True, null=True)
    status = models.IntegerField("状态", choices=FAULT_STATUS_CHOICES, default=0)

    class Meta:
        verbose_name = "故障"
        verbose_name_plural = "故障管理"
        ordering = ['-created_at']

    def __str__(self):
        return f"故障 #{self.id} - {self.incident.title}"

