"""
用户表和组织架构表的字段映射均采用数据分发平台的字段名。
数据由数据分发平台主动推送至星盾数据库。
"""

from django.db import models

__all__ = ['AnonymousUser', 'Employee', 'Org', 'BaseModel']


class AnonymousUser:
    """ 匿名用户（非模型，仅用于权限兜底） """
    id = '0'
    name = '匿名用户'
    username = 'basic_anonymous_user'


class Org(models.Model):
    """
    组织架构表（部门/机构）
    字段命名与数据分发平台保持一致
    """
    id = models.CharField(primary_key=True, max_length=64, verbose_name='分发系统主键')
    org_code = models.CharField(max_length=64, unique=True, verbose_name='机构编码')
    org_name = models.CharField(max_length=128, null=True, verbose_name='机构名称')
    unit_name = models.CharField(max_length=128, null=True, verbose_name='公司名称')
    unit_code = models.CharField(max_length=64, null=True, verbose_name='公司编码')
    pk_org_id = models.CharField(max_length=255, unique=True, null=True, verbose_name='机构主键（全系统唯一）')

    # 父级关系：优先使用 org_code 作为外键（更稳定）
    parent = models.ForeignKey(
        to='self',
        to_field='org_code',
        db_column='parent_code',
        db_constraint=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='children',
        verbose_name='父级机构（通过 org_code 关联）'
    )

    # 部门负责人（工号关联）
    principal = models.ForeignKey(
        to='Employee',
        to_field='psncode',
        db_column='principal_code',
        db_constraint=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='managed_orgs',
        verbose_name='部门负责人（工号）'
    )

    org_full_code = models.CharField(max_length=1024, null=True, verbose_name='机构全路径编码（如：A|B|C）')
    org_full_name = models.CharField(max_length=1024, null=True, verbose_name='机构全路径名称（如：集团|总部|IT部）')
    seal_status = models.CharField(max_length=16, null=True, verbose_name='是否封存（Y/N）')
    create_time = models.DateTimeField(null=True, verbose_name='创建时间')
    update_time = models.DateTimeField(null=True, verbose_name='更新时间')

    class Meta:
        db_table = 'basic_org'
        verbose_name = '组织架构'
        verbose_name_plural = '组织架构'

    def __str__(self):
        return f"{self.org_name} ({self.org_code})"

    @property
    def parent_info(self):
        if not self.parent:
            return {}
        return {
            'id': self.parent.id,
            'org_code': self.parent.org_code,
            'org_name': self.parent.org_name,
        }

    @property
    def principal_info(self):
        if not self.principal:
            return {}
        return {
            'id': self.principal.id,
            'psncode': self.principal.psncode,
            'psnname': self.principal.psnname,
            'deptname': self.principal.deptname or self.principal.org_name,
        }

    @property
    def full_name_path(self):
        """ 返回格式化后的全路径名称，如 '集团/总部/IT部' """
        if self.org_full_name:
            return self.org_full_name.strip('|').replace('|', '/')
        return self.org_name or ''


class Employee(models.Model):
    """
    员工表（用户）
    主键为数据分发系统的员工主键（字符串）
    """
    id = models.CharField(primary_key=True, max_length=64, verbose_name='分发系统主键')
    psncode = models.CharField(max_length=128, unique=True, verbose_name='员工编码（工号）')
    psnname = models.CharField(db_index=True, max_length=128, verbose_name='员工姓名')
    email = models.EmailField(max_length=254, null=True, verbose_name='邮箱')  # 使用 EmailField 更规范
    mobile = models.CharField(max_length=32, null=True, verbose_name='手机号码')  # 通常不超过32位

    # 【关键优化】只保留一个部门关联字段：推荐使用 dept（通过 org_code 关联）
    dept = models.ForeignKey(
        to=Org,
        to_field='org_code',
        db_column='deptcode',
        db_constraint=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='employees',
        verbose_name='所属部门（org_code）'
    )

    # 【可选】保留 deptname 用于展示加速（避免每次 join），但需确保数据同步一致性
    deptname = models.CharField(max_length=128, null=True, verbose_name='部门名称（冗余字段）')

    outdutydate = models.CharField(max_length=32, null=True, verbose_name='离职日期（YYYY-MM-DD）')
    psnclscope = models.IntegerField(default=0, verbose_name='人员状态：0-在职，2-离职')
    login_time = models.DateTimeField(null=True, verbose_name='最后登录时间')
    unitname = models.CharField(max_length=128, null=True, verbose_name='公司名称')
    jobname = models.CharField(max_length=128, null=True, verbose_name='岗位名称')

    class Meta:
        db_table = 'basic_employee'
        verbose_name = '员工'
        verbose_name_plural = '员工'

    def __str__(self):
        return f"{self.psnname} ({self.psncode})"

    @property
    def code(self):
        return self.psncode

    @property
    def name(self):
        return self.psnname

    @property
    def org_name(self):
        """ 优先使用冗余字段 deptname，其次 fallback 到关联部门 """
        return self.deptname or (self.dept.org_name if self.dept else "")

    @property
    def org_full_name(self):
        if self.dept:
            return self.dept.full_name_path
        return ""

    # ========================
    # 角色相关（假设你有 Role 模型）
    # ========================
    # 注意：以下代码假设存在 `roles` 多对多关系，若无请删除或调整

    # 示例（如存在）：
    # roles = models.ManyToManyField('Role', related_name='users')

    @property
    def org_role_list(self):
        """ 获取部门角色（假设 Org 有 roles 字段） """
        if not self.dept:
            return []
        try:
            return [
                {'id': role.id, 'alias': role.alias, 'name': role.name}
                for role in self.dept.roles.all()
            ]
        except AttributeError:
            # 如果 Org 没有 roles 字段，返回空
            return []

    @property
    def role_list(self):
        """ 合并个人角色 + 部门角色（去重） """
        personal_roles = []
        role_ids = set()

        # 假设存在 self.roles.all()
        try:
            for role in self.roles.all():
                role_dict = {'id': role.id, 'alias': role.alias, 'name': role.name}
                personal_roles.append(role_dict)
                role_ids.add(role.id)
        except AttributeError:
            pass  # 无个人角色

        org_roles = []
        for role in self.org_role_list:
            if role['id'] not in role_ids:
                org_roles.append(role)

        return personal_roles + org_roles


class BaseTimeModel(models.Model):
    """提供创建时间和更新时间的抽象基类"""
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True


class BaseUserModel(models.Model):
    """提供创建人和更新人的抽象基类，关联 Employee 表（通过工号 psncode）"""
    created_by = models.ForeignKey(
        to=Employee,
        to_field='psncode',
        db_column='created_by',
        db_constraint=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',  # 禁用反向关系
        verbose_name='创建人（工号）'
    )
    updated_by = models.ForeignKey(
        to=Employee,
        to_field='psncode',
        db_column='updated_by',
        db_constraint=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='更新人（工号）'
    )

    class Meta:
        abstract = True

    def _get_user_info(self, user: Employee):
        """安全获取员工信息，避免 None 或异常"""
        if not user:
            return {}
        return {
            'id': user.id,
            'psncode': user.psncode,
            'psnname': user.psnname,
            'org_name': user.org_name,  # 注意：org_name 是 property，已处理异常
        }

    @property
    def created_by_info(self):
        return self._get_user_info(self.created_by)

    @property
    def updated_by_info(self):
        return self._get_user_info(self.updated_by)


class BaseModel(BaseTimeModel, BaseUserModel):
    """组合时间与用户信息的通用抽象基类"""
    class Meta:
        abstract = True

