from django.db import models
from basic.models import Employee

__all__ = ['OperateLog']


class OperateLog(models.Model):
    """
    统一操作审计日志

    - instance: 格式为 'app_label.ModelName'，例如 'xc.Application'
    - instance_id: 模型主键的字符串表示（支持非整型主键）
    - operate: 操作描述，如 '创建回归单'、'删除应用'
    """
    instance = models.CharField(max_length=64, verbose_name='模型标识（app_label.ModelName）')
    instance_id = models.CharField(max_length=256, verbose_name='实例主键（字符串）')
    operate = models.CharField(max_length=256, verbose_name='操作描述')
    operate_user = models.ForeignKey(
        to=Employee,
        to_field='psncode',
        db_constraint=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',  # 不创建反向关系，避免 Employee 模型膨胀
        verbose_name='操作用户'
    )
    operate_time = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')  # 移除 null=True

    @property
    def operate_user_info(self):
        user = self.operate_user
        if not user:
            return {}
        return {
            'psncode': user.psncode,
            'psnname': user.psnname,
            'org_name': getattr(user, 'org_name', ''),
        }

    def __str__(self):
        user = self.operate_user.psncode if self.operate_user else 'anonymous'
        return f"[{self.operate_time}] {user} {self.operate} on {self.instance}({self.instance_id})"

    class Meta:
        db_table = 'basic_operate_log'
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        indexes = [
            models.Index(fields=['operate_user', '-operate_time']),
            models.Index(fields=['instance', 'instance_id']),
        ]
