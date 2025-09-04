# models.py
from django.db import models


class SystemConfig(models.Model):
    """
    系统参数配置表
    """
    CONFIG_TYPE_CHOICES = [
        ('text', '文本'),
        ('number', '数字'),
        ('boolean', '布尔值'),
        ('textarea', '多行文本'),
        ('image', '图片'),
    ]

    key = models.CharField(max_length=100, unique=True, verbose_name="配置键")
    value = models.TextField(verbose_name="配置值")
    label = models.CharField(max_length=100, verbose_name="显示名称")
    type = models.CharField(max_length=20, choices=CONFIG_TYPE_CHOICES, default='text', verbose_name="类型")
    group = models.CharField(max_length=50, default="basic", verbose_name="分组")  # 如：basic, seo, mail, auth
    remark = models.CharField(max_length=200, blank=True, null=True, verbose_name="备注")

    class Meta:
        db_table = 'system_config'
        verbose_name = "系统参数配置"
        verbose_name_plural = "系统参数配置"

    def __str__(self):
        return f"{self.label} ({self.key})"


class Menu(models.Model):
    """
    后台菜单（树形结构）
    """
    title = models.CharField(max_length=50, verbose_name="菜单名称")
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name="图标")
    path = models.CharField(max_length=200, blank=True, null=True, verbose_name="路由路径")
    component = models.CharField(max_length=200, blank=True, null=True, verbose_name="组件路径")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name="父菜单")
    order = models.PositiveIntegerField(default=0, verbose_name="排序")
    visible = models.BooleanField(default=True, verbose_name="是否可见")
    permission = models.CharField(max_length=100, blank=True, null=True, verbose_name="权限标识")

    class Meta:
        db_table = 'system_menu'
        verbose_name = "菜单管理"
        verbose_name_plural = "菜单管理"
        ordering = ['order']

    def __str__(self):
        return self.title


class StorageConfig(models.Model):
    """
    文件存储配置
    """
    TYPE_CHOICES = [
        ('local', '本地存储'),
        ('minio', 'MinIO'),
        ('aliyun', '阿里云OSS'),
        ('qcloud', '腾讯云COS'),
    ]


    name = models.CharField(max_length=50, unique=True, verbose_name="配置名称")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="存储类型")
    is_default = models.BooleanField(default=False, verbose_name="是否默认")
    config = models.JSONField(verbose_name="配置详情")  # 如：endpoint, bucket, access_key 等
    base_url = models.URLField(verbose_name="访问域名")

    class Meta:
        db_table = 'system_storage'
        verbose_name = "文件存储配置"
        verbose_name_plural = "文件存储配置"

    def __str__(self):
        return f"{self.name} ({self.type})"
