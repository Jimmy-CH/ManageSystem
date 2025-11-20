from django.db import models
from apps.basic.models import BaseModel

__all__ = [
    'Menu', 'Role', 'Permission',
    'RoleConnEmployee', 'RoleConnOrg', 'RoleConnMenu',
    'RoleConnPermission', 'MenuConnPermission'
]


# =============== 抽象中间表基类 ===============
class BaseConnModel(models.Model):
    """通用中间连接表基类，包含创建时间和创建人"""
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    created_by = models.ForeignKey(
        to='Employee',
        to_field='psncode',
        db_constraint=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='创建人'
    )

    class Meta:
        abstract = True

    def _get_employee_info(self, emp):
        if not emp:
            return {}
        return {
            'id': emp.id,
            'psncode': emp.psncode,
            'psnname': emp.psnname,
            'org_name': emp.org_name,
        }

    @property
    def created_by_info(self):
        return self._get_employee_info(self.created_by)


# =============== 菜单模型 ===============
class Menu(BaseModel):
    """
    菜单表
    """
    KindChoices = (
        (1, '目录'),
        (2, '菜单')
    )
    name = models.CharField(max_length=32, verbose_name='菜单名称')
    level = models.IntegerField(default=1, verbose_name='菜单级别')
    parent = models.ForeignKey(
        to='self',
        related_name='children',
        null=True,
        on_delete=models.CASCADE,
        db_constraint=False,
        verbose_name='父级菜单'
    )
    kind = models.IntegerField(choices=KindChoices, default=2, verbose_name='类型')
    path = models.CharField(max_length=1024, blank=True, verbose_name='全路径')
    component = models.CharField(max_length=256, blank=True, null=True, verbose_name='前端组件')
    icon = models.CharField(max_length=256, blank=True, null=True, verbose_name='图标')
    order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='启用状态')
    is_hidden = models.BooleanField(default=False, verbose_name='隐藏菜单')

    @property
    def kind_info(self):
        return {
            'label': self.get_kind_display(),
            'value': self.kind
        }

    def __str__(self):
        return f"{self.name} ({self.get_kind_display()})"

    class Meta:
        db_table = 'basic_menu'


# =============== 角色模型 ===============
class Role(BaseModel):
    """
    角色表
    """
    name = models.CharField(max_length=32, unique=True, verbose_name='角色名称')
    alias = models.CharField(unique=True, max_length=64, verbose_name='角色唯一标识')

    employees = models.ManyToManyField(
        to='Employee',
        through='RoleConnEmployee',
        through_fields=('role', 'employee'),  # ← 添加这一行
        related_name='roles',
        verbose_name='关联用户'
    )
    orgs = models.ManyToManyField(
        to='Org',
        through='RoleConnOrg',
        through_fields=('role', 'org'),       # ← 添加这一行
        related_name='roles',
        verbose_name='关联部门'
    )
    menus = models.ManyToManyField(
        to='Menu',
        through='RoleConnMenu',
        through_fields=('role', 'menu'),      # ← 添加这一行
        related_name='roles',
        verbose_name='关联菜单'
    )
    permissions = models.ManyToManyField(
        to='Permission',
        through='RoleConnPermission',
        through_fields=('role', 'permission'),  # ← 添加这一行
        related_name='roles',
        verbose_name='关联权限'
    )

    # 不在 property 中执行数据库查询，避免 N+1
    def get_employee_list(self, queryset=None):
        """需配合 prefetch_related('employees') 使用"""
        qs = queryset or self.employees.all()
        return [
            {
                'id': emp.id,
                'psncode': emp.psncode,
                'psnname': emp.psnname,
                'org_name': emp.org_name,
            }
            for emp in qs
        ]

    def get_org_list(self, queryset=None):
        """需配合 prefetch_related('orgs') 使用"""
        qs = queryset or self.orgs.all()
        return [
            {'org_code': org.org_code, 'org_name': org.org_name}
            for org in qs
        ]

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'basic_role'


# =============== 权限模型 ===============
class Permission(BaseModel):
    """
    权限表
    """
    name = models.CharField(max_length=100, verbose_name='操作权限名称')
    alias = models.CharField(max_length=64, unique=True, verbose_name='权限别名')
    description = models.CharField(max_length=256, null=True, blank=True, verbose_name='描述')

    def __str__(self):
        return f"{self.name} ({self.alias})"

    class Meta:
        db_table = 'basic_permission'


# =============== 中间连接表 ===============
class RoleConnEmployee(BaseConnModel):
    role = models.ForeignKey(
        to='Role',
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='role_employee_conns',
        verbose_name='关联角色'
    )
    employee = models.ForeignKey(
        to='Employee',
        to_field='psncode',
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='role_employee_conns',
        verbose_name='关联用户'
    )

    @property
    def role_name(self):
        return self.role.name if self.role_id else ""

    @property
    def employee_info(self):
        return self._get_employee_info(self.employee)

    def __str__(self):
        return f"{self.role.name} ↔ {self.employee.psncode}"

    class Meta:
        db_table = 'basic_role_conn_employee'
        unique_together = ('role', 'employee')


class RoleConnOrg(BaseConnModel):
    role = models.ForeignKey(
        to='Role',
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='role_org_conns',
        verbose_name='关联角色'
    )
    org = models.ForeignKey(
        to='Org',
        to_field='org_code',
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='role_org_conns',
        verbose_name='关联部门'
    )

    @property
    def org_name(self):
        return self.org.org_name if self.org_id else ""

    def __str__(self):
        return f"{self.role.name} ↔ {self.org.org_code}"

    class Meta:
        db_table = 'basic_role_conn_org'
        unique_together = ('role', 'org')


class RoleConnMenu(BaseConnModel):
    half_checked = models.BooleanField(default=False, verbose_name='菜单半选状态(有子菜单，且子菜单未全选)')
    role = models.ForeignKey(
        to='Role',
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='role_menu_conns',
        verbose_name='关联角色'
    )
    menu = models.ForeignKey(
        to='Menu',
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='role_menu_conns',
        verbose_name='关联菜单'
    )

    def __str__(self):
        return f"{self.role.name} ↔ {self.menu.name}"

    class Meta:
        db_table = 'basic_role_conn_menu'
        unique_together = ('role', 'menu')


class RoleConnPermission(BaseConnModel):
    role = models.ForeignKey(
        to='Role',
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='role_permission_conns',
        verbose_name='关联角色'
    )
    permission = models.ForeignKey(
        'Permission',
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='role_permission_conns',
        verbose_name='关联权限'
    )

    @property
    def permission_name(self):
        return self.permission.name if self.permission_id else ""

    def __str__(self):
        return f"{self.role.name} ↔ {self.permission.alias}"

    class Meta:
        db_table = 'basic_role_conn_permission'
        unique_together = ('role', 'permission')


class MenuConnPermission(BaseConnModel):
    """
    菜单关联权限（一对一：一个菜单绑定一个权限）
    ⚠️ 若需支持一个菜单绑定多个权限，请改用 ForeignKey + unique_together
    """
    menu = models.ForeignKey(
        to='Menu',
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='menu_permission_conns',
        verbose_name='关联菜单'
    )
    permission = models.OneToOneField(
        'Permission',
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='menu_permission_conns',
        verbose_name='关联权限'
    )

    @property
    def permission_name(self):
        return self.permission.name if self.permission_id else ""

    def __str__(self):
        return f"{self.menu.name} → {self.permission.alias}"

    class Meta:
        db_table = 'basic_menu_conn_permission'
        # OneToOneField 已隐含唯一约束，无需 unique_together
