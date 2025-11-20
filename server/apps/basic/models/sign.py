from django.db import models
from django.core.exceptions import ValidationError
from apps.basic.models import Employee
from apps.xc.models import Application

__all__ = ['Sign', 'SignAPIs']


class Sign(models.Model):
    """
    Token 签发表
    每个 (申请人, 应用) 组合最多一个有效签发记录（通过 unique_together 保证）
    """
    security_key = models.CharField(max_length=1024, verbose_name='签发认证信息加密串')
    sign_time = models.DateTimeField(verbose_name='签发时间')
    is_active = models.BooleanField(default=True, verbose_name='启用状态')
    apply_user = models.ForeignKey(
        to=Employee,
        to_field='psncode',
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='sign_keys',  # 改为复数更合理
        verbose_name='申请人',
    )
    application = models.ForeignKey(
        to=Application,
        null=True,
        blank=True,  # 允许表单为空（虽不影响 DB）
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='sign_keys',
        verbose_name='关联应用',
    )
    comment = models.CharField(max_length=64, verbose_name='用途备注')

    @property
    def apply_user_info(self):
        if not self.apply_user:
            return {}
        return {
            'id': self.apply_user.id,
            'psncode': self.apply_user.psncode,
            'psnname': self.apply_user.psnname,
        }

    @property
    def application_info(self):
        if not self.application:
            return {}
        return {
            'id': self.application.id,
            'name': self.application.name,
            'cname': self.application.cname or "",
        }

    def __str__(self):
        app_name = self.application.name if self.application else "N/A"
        return f"Sign for {self.apply_user.psncode} - {app_name}"

    class Meta:
        db_table = 'basic_sign'
        # 注意：当 application 为 NULL 时，unique_together 仍会生效（Django 中 NULL != NULL）
        # 如果业务允许同一个用户对“无应用”签发多次，需移除此约束或使用 partial index
        unique_together = ('apply_user', 'application')
        verbose_name = 'Token 签发'
        verbose_name_plural = 'Token 签发'


def validate_http_methods(value):
    """校验 methods 字段是否为合法的 HTTP 方法列表"""
    valid_methods = {'GET', 'POST', 'PUT', 'PATCH', 'DELETE'}
    if not isinstance(value, list):
        raise ValidationError('Methods 必须是列表')
    invalid = set(value) - valid_methods
    if invalid:
        raise ValidationError(f'包含非法方法: {invalid}')


class SignAPIs(models.Model):
    """
    认证接口列表
    每个签发记录可绑定多个 API 路径和允许的方法
    """
    url = models.CharField(max_length=512, verbose_name='请求地址')
    methods = models.JSONField(
        default=list,
        validators=[validate_http_methods],
        verbose_name='请求方法（如 ["GET", "POST"]）'
    )
    sign = models.ForeignKey(
        to='Sign',
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='apis',
        verbose_name='签发的认证',
    )

    def clean(self):
        super().clean()
        validate_http_methods(self.methods)

    def __str__(self):
        methods_str = ', '.join(self.methods) if isinstance(self.methods, list) else 'N/A'
        return f"{self.url} [{methods_str}]"

    class Meta:
        db_table = 'basic_sign_apis'
        verbose_name = '认证接口'
        verbose_name_plural = '认证接口'
