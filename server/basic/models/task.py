"""
任务管理平台 - 任务模型
"""
from django.db import models
from basic.models import Employee

__all__ = ['Task']


class TaskKind(models.IntegerChoices):
    """任务类型枚举"""
    VULNERABILITY = 1, '漏洞'
    CICD_TEST = 2, 'CICD测试任务'
    PERIODIC_TEST = 3, '周期测试任务'


class Task(models.Model):
    """
    记录外部系统（如钉钉/得物待办）下发的任务信息。

    保存 appoint_user 是因为调用第三方接口获取任务详情时，
    需要传入指派人的 user_code 和 user_name。
    """
    id = models.BigIntegerField(
        primary_key=True,
        verbose_name='待办任务ID',
        help_text='来自第三方任务系统的唯一ID'
    )
    kind = models.IntegerField(
        choices=TaskKind.choices,
        default=TaskKind.VULNERABILITY,
        verbose_name='任务类别',
        db_index=True  # 提升按类型查询性能
    )
    appoint_user = models.ForeignKey(
        Employee,
        to_field='psncode',  # 关联 Employee.psncode（必须唯一！）
        db_constraint=False,  # 允许数据库无外键约束（软关联）
        on_delete=models.SET_NULL,  # 员工离职时保留任务记录
        null=True,
        blank=True,  # 表单可为空（虽业务可能非空，但模型层更灵活）
        verbose_name='指派人',
        db_index=True  # 加速按指派人查询
    )

    class Meta:
        db_table = 'basic_task'
        verbose_name = '待办任务'
        verbose_name_plural = '待办任务'

    def __str__(self):
        return f"[{self.get_kind_display()}] 任务ID: {self.id} - 指派人: {self.appoint_user.psnname if self.appoint_user else 'N/A'}"
