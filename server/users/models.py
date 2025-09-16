# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

from common import BaseModel


# 自定义权限表
class CustomPermission(BaseModel):
    """
    自定义权限，不依赖 Django 默认的 Permission 模型
    """
    codename = models.CharField("权限码", max_length=100, unique=True)
    name = models.CharField("权限名称", max_length=100)
    description = models.TextField("描述", blank=True, null=True)
    category = models.CharField("分类", max_length=50, help_text="用于前端分组展示，如 content, user, system")
    importance = models.PositiveIntegerField("重要程度", default=1)
    status = models.BooleanField("状态", default=True)

    class Meta:
        verbose_name = "自定义权限"
        verbose_name_plural = "自定义权限"

    def __str__(self):
        return f"{self.name} ({self.codename})"


class Role(BaseModel):
    name = models.CharField("角色名称", max_length=50, unique=True)
    description = models.CharField("描述", max_length=200, blank=True, null=True)
    permissions = models.ManyToManyField(CustomPermission, verbose_name="权限", blank=True)
    importance = models.PositiveIntegerField("重要程度", default=1)
    status = models.BooleanField("状态", default=True)

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = "角色管理"

    def __str__(self):
        return self.name


# 扩展 User 模型
class User(AbstractUser):
    phone = models.CharField("手机号", max_length=11, blank=True, null=True, unique=True)
    avatar = models.ImageField("头像", upload_to='avatars/', blank=True, null=True)
    department = models.CharField("部门", max_length=50, blank=True, null=True)
    position = models.CharField("职位", max_length=50, blank=True, null=True)
    status = models.BooleanField("是否启用", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    importance = models.PositiveIntegerField("重要程度", default=1)

    # 用户直接关联角色（一个用户可有多个角色）
    roles = models.ManyToManyField(Role, verbose_name="角色", blank=True)

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户管理"

    @property
    def all_permissions(self):
        """
        返回用户所有权限的 codename 列表
        """
        perms = set()
        for role in self.roles.all():
            perms.update(role.permissions.values_list('codename', flat=True))
        return perms

    def has_perm(self, perm):
        """
        检查用户是否有某权限
        :param perm: 权限码，如 'can_publish'
        :return: bool
        """
        return perm in self.all_permissions
