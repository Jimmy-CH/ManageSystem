"""
以下表数据均同步
"""

from django.db import models

from basic.models import BaseModel, Org, Employee

__all__ = ['Project', 'Version', 'Demand', 'Regression', 'RegressionConnApplication', 'PublishTask']


class DemandRiskLevel(models.IntegerChoices):
    R0 = 1, 'R0（低风险）'
    R1 = 2, 'R1（中风险）'
    R0_1 = 3, 'R0-1（混合）'
    R2 = 4, 'R2（高风险）'


class Project(models.Model):
    """
    项目表
    """
    id = models.CharField(
        max_length=32,
        primary_key=True,
        verbose_name='项目编号（对标 CICD project_num，对应 Jira 项目 Key）'
    )
    name = models.CharField(max_length=128, blank=True, verbose_name='项目名称')
    org = models.ForeignKey(
        to=Org,
        to_field='org_code',
        null=True,
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name='关联部门'
    )
    created_at = models.DateTimeField(null=True, verbose_name='创建时间')

    def __str__(self):
        return f"{self.name or 'Unnamed'} ({self.id})"

    class Meta:
        db_table = 'xc_cicd_project'


class Version(BaseModel):
    """
    版本表
    """
    id = models.CharField(
        max_length=32,
        primary_key=True,
        verbose_name='版本ID（对应 CICD version_id）'
    )
    name = models.CharField(max_length=128, blank=True, verbose_name='版本名称')
    project = models.ForeignKey(
        to='Project',
        null=True,
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name='关联项目'
    )
    start_time = models.DateTimeField(null=True, verbose_name='创建时间')

    def __str__(self):
        return f"{self.name or 'Unnamed Version'} ({self.id})"

    class Meta:
        db_table = 'xc_cicd_version'


class Demand(models.Model):
    """
    需求表
    """
    id = models.IntegerField(primary_key=True, verbose_name='需求ID（对应 CICD ID）')
    demand_num = models.CharField(max_length=256, blank=True, verbose_name='需求编号（CICD demand_num）')
    demand_type = models.IntegerField(null=True, verbose_name='需求类型')
    name = models.CharField(max_length=256, blank=True, verbose_name='名称')
    risk_level = models.IntegerField(
        null=True,
        choices=DemandRiskLevel.choices,
        verbose_name='风险等级'
    )
    version = models.ForeignKey(
        to='Version',
        null=True,
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='demands',
        verbose_name='关联版本'
    )
    description = models.TextField(blank=True, verbose_name='描述')
    is_mobile_demand = models.BooleanField(default=False, verbose_name="是否为移动端需求")

    @property
    def risk_level_info(self):
        if self.risk_level is None:
            return {}
        return {
            'label': self.get_risk_level_display(),
            'value': self.risk_level
        }

    def __str__(self):
        return f"{self.name or 'Unnamed Demand'} [{self.demand_num}]"

    class Meta:
        db_table = 'xc_cicd_demand'


class Regression(models.Model):
    """
    回归单
    """
    id = models.BigAutoField(primary_key=True)
    version = models.ForeignKey(
        to='Version',
        null=True,
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='regression_tasks',
        verbose_name='关联版本'
    )
    application = models.ManyToManyField(
        to='Application',
        through='RegressionConnApplication',
        through_fields=('regression', 'application'),
        related_name='regression_tasks',
        verbose_name='关联应用'
    )
    created_by = models.ForeignKey(
        to=Employee,
        to_field='psncode',
        db_constraint=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='created_regression_tasks',
        verbose_name='创建用户'
    )
    test_addr = models.TextField(blank=True, verbose_name='测试地址')
    test_owner = models.ForeignKey(
        to=Employee,
        to_field='psncode',
        db_constraint=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='owned_regression_tasks',
        verbose_name='测试负责人'
    )
    created_time = models.DateTimeField(null=True, verbose_name='创建时间')

    @property
    def test_owner_info(self):
        if not self.test_owner:
            return {}
        return {
            'psncode': self.test_owner.psncode,
            'psnname': self.test_owner.psnname,
            'org_name': getattr(self.test_owner, 'org_name', ''),
        }

    def __str__(self):
        return f"Regression #{self.id}"

    class Meta:
        db_table = 'xc_cicd_regression'


class RegressionConnApplication(models.Model):
    """
    回归单关联应用表
    """
    regression = models.ForeignKey(
        to='Regression',
        null=True,
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='application_connections',
        verbose_name='关联回归单'
    )
    application = models.ForeignKey(
        to='Application',
        null=True,
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='regression_connections',
        verbose_name='关联回归单'
    )
    package_path = models.CharField(max_length=256, blank=True, verbose_name='包地址信息')

    @property
    def product_name(self):
        return self.application.basic_info['product_name'] if self.application else ""

    @property
    def system_name(self):
        return self.application.basic_info['system_name'] if self.application else ""

    @property
    def application_name(self):
        return self.application.basic_info['name'] if self.application else ""

    @property
    def create_user_info(self):
        if not self.regression or not self.regression.created_by:
            return {}
        return {
            'psncode': self.regression.created_by.psncode,
            'psnname': self.regression.created_by.psnname,
            'org_name': getattr(self.regression.created_by, 'org_name', ''),
        }

    @property
    def created_time(self):
        return self.regression.created_time if self.regression else None

    @property
    def task_number(self):
        return self.regression.id if self.regression else None

    @property
    def is_pubnet_mapping(self):
        # TODO: 后续从工单获取
        return False

    def __str__(self):
        app_name = self.application_name or 'Unknown App'
        reg_id = self.regression.id if self.regression else 'Unknown'
        return f"Regression #{reg_id} - {app_name}"

    class Meta:
        db_table = 'xc_cicd_regression_conn_application'


class PublishTask(models.Model):
    """
    发布单
    """
    FLAG_CHOICES = [
        (0, '国内'),
        (1, '国外'),
    ]

    id = models.CharField(
        max_length=32,
        primary_key=True,
        verbose_name='发布单号（对应 CD 的 id）'
    )
    task_number = models.CharField(max_length=64, blank=True, verbose_name='发布单号（CD task_number）')
    version = models.ForeignKey(
        to='Version',
        null=True,
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='publish_tasks',
        verbose_name='关联版本'
    )
    application = models.ForeignKey(
        to='Application',
        null=True,
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='publish_tasks',
        verbose_name='关联应用'
    )
    package_path = models.CharField(max_length=256, blank=True, verbose_name='包地址信息')
    created_by = models.ForeignKey(
        to=Employee,
        to_field='psncode',
        db_constraint=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='created_publish_tasks',
        verbose_name='创建用户'
    )
    created_time = models.DateTimeField(null=True, verbose_name='创建时间')
    description = models.TextField(blank=True, verbose_name='描述')
    is_pub_mapping = models.BooleanField(default=False, verbose_name='是否公网映射')
    is_deleted = models.BooleanField(default=False, verbose_name='是否取消')

    @property
    def product_name(self):
        return self.application.basic_info['product_name'] if self.application else ""

    @property
    def system_name(self):
        return self.application.basic_info['system_name'] if self.application else ""

    @property
    def application_name(self):
        return self.application.basic_info['name'] if self.application else ""

    @property
    def application_cname(self):
        return self.application.basic_info['cname'] if self.application else ""

    @property
    def application_owner(self):
        return self.application.owner_info if self.application else {}

    @property
    def create_user_info(self):
        if not self.created_by:
            return {}
        return {
            'psncode': self.created_by.psncode,
            'psnname': self.created_by.psnname,
            'org_name': getattr(self.created_by, 'org_name', ''),
        }

    # 注意：不再需要 is_pubnet_mapping property，直接用 is_pub_mapping 字段

    def __str__(self):
        return f"PublishTask {self.id} - {self.application_name or 'Unknown App'}"

    class Meta:
        db_table = 'xc_cicd_publish'
