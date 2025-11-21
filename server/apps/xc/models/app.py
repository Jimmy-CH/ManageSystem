from django.db import models
from apps.basic.models import BaseModel

__all__ = ['App']


class App(BaseModel):
    """
    应用模型（含 CMDB 应用 + 外部第三方应用）
    注意：此模型独立于 cmdb.Application，用于维护第三方集成数据。
    用户信息以文本形式存储（非外键），便于对接外部系统。
    """
    CATEGORY_CHOICES = [
        (1, '总部'),
        (2, '第三方'),
    ]

    # ⚠️ 谨慎：若 id 来自外部系统且不可变，可保留；否则建议用默认自增主键
    id = models.IntegerField(primary_key=True, verbose_name='外部系统应用ID')

    name = models.CharField(max_length=128, verbose_name='应用名称（对应 CMDB 的 cname）')
    system_name = models.CharField(max_length=128, blank=True, verbose_name='系统名称')

    category = models.IntegerField(
        choices=CATEGORY_CHOICES,
        default=1,
        verbose_name='应用类别'
    )

    # 使用 blank=True 即可，避免 NULL（Django 最佳实践）
    owner = models.CharField(max_length=255, blank=True, verbose_name='应用负责人（中文名，多个用逗号分隔）')
    depart_owner = models.CharField(max_length=255, blank=True, verbose_name='部门负责人（中文名，多个用逗号分隔）')
    leader = models.CharField(max_length=255, blank=True, verbose_name='总监（中文名，多个用逗号分隔）')

    @property
    def category_info(self):
        return {
            'label': self.get_category_display(),
            'value': self.category
        }

    def __str__(self):
        return f"{self.name} ({'总部' if self.category == 1 else '第三方'})"

    class Meta:
        db_table = 'xd_application'
        verbose_name = '应用'
        verbose_name_plural = '应用'
