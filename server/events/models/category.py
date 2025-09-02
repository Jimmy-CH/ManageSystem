from django.db import models
from common import BaseModel
from events.models.constants import LEVEL_CHOICES


class Category(BaseModel):
    name = models.CharField("分类名称", max_length=100, db_index=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="父分类"
    )
    level = models.IntegerField("层级", choices=LEVEL_CHOICES, default=1)
    order = models.PositiveIntegerField("排序", default=0)
    is_active = models.BooleanField("是否启用", default=True)

    class Meta:
        verbose_name = "分类"
        verbose_name_plural = "分类管理"
        ordering = ['order', 'id']

    def __str__(self):
        return self.name

    def get_ancestors(self, include_self=False):
        """获取所有祖先节点（从根到父）"""
        ancestors = []
        parent = self.parent
        while parent:
            ancestors.append(parent)
            parent = parent.parent
        if include_self:
            ancestors.insert(0, self)
        return list(reversed(ancestors))

    def get_full_path_name(self):
        """返回完整路径名称，如：家电 > 电视 > 液晶电视 > 4K液晶电视"""
        ancestors = self.get_ancestors(include_self=True)
        return " > ".join([anc.name for anc in ancestors])
