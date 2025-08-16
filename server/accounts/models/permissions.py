
from django.contrib.auth.models import User
from django.db import models


class CustomPermission(models.Model):
    """
    自定义权限，不绑定特定的Django模型。
    适用于 'view_dashboard', 'export_reports', 'manage_users' 等抽象权限。
    """
    codename = models.CharField(
        max_length=100,
        unique=True,
        help_text="权限唯一标识符，如 'view_dashboard', 'export_data'"
    )
    name = models.CharField(
        max_length=255,
        help_text="权限名称，如 '查看仪表盘', '导出数据'"
    )
    description = models.TextField(blank=True, help_text="权限描述")
    app_label = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="所属应用或模块，如 'reports', 'admin'"
    )
    # 可以添加其他字段，如是否激活、创建时间等
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '自定义权限'
        verbose_name_plural = '自定义权限'
        # 确保活跃权限的唯一性
        constraints = [
            models.UniqueConstraint(
                fields=['codename'],
                condition=models.Q(is_active=True),
                name='unique_active_codename'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.codename})"


class Role(models.Model):
    """
    角色，包含一组自定义权限。
    用户通过被分配角色来获得权限。
    """
    name = models.CharField(max_length=100, unique=True, help_text="角色名称，如 '管理员', '分析师'")
    description = models.TextField(blank=True, help_text="角色描述")
    permissions = models.ManyToManyField(
        CustomPermission,
        blank=True,
        related_name='roles',
        help_text="该角色拥有的权限"
    )
    is_system = models.BooleanField(
        default=False,
        help_text="系统内置角色，通常不可删除或修改"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色'

    def __str__(self):
        return self.name


class UserRole(models.Model):
    """
    用户-角色关联表。
    一个用户可以有多个角色，一个角色可以分配给多个用户。
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="角色有效期，为空表示永久有效"
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_user_roles',
        help_text="分配此角色的用户"
    )
    notes = models.TextField(blank=True, help_text="备注")

    class Meta:
        verbose_name = '用户角色'
        verbose_name_plural = '用户角色'
        # 确保同一用户在同一时间内不会重复拥有同一角色
        # (需要应用层逻辑配合，确保 expires_at 的处理)
        unique_together = ('user', 'role')

    def __str__(self):
        return f"{self.user.username} -> {self.role.name}"

