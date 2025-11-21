"""
数据同步 CMDB
1. 产品线数据：CMDB 将部门+开发组+产品+系统串联为一条源数据，此处拆分为四层树形结构
2. 应用数据
"""

from django.db import models
from apps.basic.models import Employee


__all__ = ['Product', 'Application', 'DutyScheduleData']


class Product(models.Model):
    """
    产品线信息（树形结构）
    - level=1: 部门
    - level=2: 开发组
    - level=3: 产品
    - level=4: 系统
    """
    parent = models.ForeignKey(
        to='self',
        related_name='children',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        db_constraint=False,
        verbose_name='上级产品线'
    )
    level = models.PositiveSmallIntegerField(verbose_name='层级（1~4）')
    name = models.CharField(max_length=256, verbose_name='名称')
    owner = models.ForeignKey(
        Employee,
        to_field='psncode',
        null=True,
        db_constraint=False,
        on_delete=models.SET_NULL,  # 更安全：避免 DO_NOTHING 导致 DB 约束问题
        verbose_name='负责人'
    )

    @property
    def owner_info(self):
        if not self.owner:
            return {}
        return {
            'psncode': self.owner.psncode,
            'psnname': self.owner.psnname,
        }

    def __str__(self):
        return f"{self.name} (L{self.level})"

    class Meta:
        db_table = 'xc_cmdb_product'
        unique_together = ('name', 'parent')
        verbose_name = '产品线'
        verbose_name_plural = '产品线'


class Application(models.Model):
    """
    应用信息
    """
    id = models.IntegerField(primary_key=True, verbose_name='应用ID')
    name = models.CharField(max_length=128, verbose_name='应用名')
    cname = models.CharField(max_length=512, blank=True, verbose_name='应用中文名')  # 移除 null=True
    product = models.ForeignKey(
        Product,
        null=True,
        db_constraint=False,
        on_delete=models.SET_NULL,
        verbose_name='所属产品线（系统层）'
    )
    owner = models.ForeignKey(
        Employee,
        related_name='owned_applications',
        to_field='psncode',
        null=True,
        db_constraint=False,
        on_delete=models.SET_NULL,
        verbose_name='应用负责人'
    )

    @property
    def owner_info(self):
        if not self.owner:
            return {}
        return {
            'psncode': self.owner.psncode,
            'psnname': self.owner.psnname,
        }

    @property
    def depart_owner_info(self):
        """
        应用所属部门负责人（通过 owner 所在部门的 principal_code 获取）
        假设 Employee 有 deptcode 字段，且 deptcode 有 principal_code 关联 Employee
        """
        try:
            if not self.owner or not hasattr(self.owner, 'deptcode'):
                return {}
            dept = self.owner.dept
            if not dept or not hasattr(dept, 'principal_code') or not dept.principal:
                return {}
            principal = dept.principal
            return {
                'psncode': principal.psncode,
                'psnname': principal.psnname,
            }
        except (AttributeError, TypeError):
            return {}

    @property
    def system_name(self):
        """系统名称 = 所属 product 的 name（通常为 level=4 的系统节点）"""
        return self.product.name if self.product else ""

    @property
    def basic_info(self):
        """供 RegressionConnApplication 等关联模型使用"""
        product_name = self.product.name if self.product else ""
        return {
            'id': self.id,
            'name': self.name,
            'cname': self.cname or "",
            'product_name': product_name,
            'system_name': product_name,  # 与 system_name property 一致
        }

    def __str__(self):
        return f"{self.name} ({self.cname or 'N/A'})"

    class Meta:
        db_table = 'xc_cmdb_application'
        verbose_name = '应用'
        verbose_name_plural = '应用'


class DutyScheduleData(models.Model):
    """
    值班表数据（按日期存储）
    duty_content 示例：
    {
        "morning": {"psncode": "U123", "psnname": "张三"},
        "night": {"psncode": "U456", "psnname": "李四"}
    }
    """
    duty_date = models.DateField(verbose_name="值班日期")
    duty_content = models.JSONField(blank=True, null=True, default=None)

    def __str__(self):
        return f"值班 {self.duty_date}"

    class Meta:
        db_table = 'cmdb_dutyscheduledata'
        app_label = 'xc'
        verbose_name = '值班表'
        verbose_name_plural = '值班表'
        unique_together = ('duty_date',)
