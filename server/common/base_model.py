
from django.db import models


class BaseModel(models.Model):
    """
    抽象基类模型，为所有继承它的模型自动添加创建时间和更新时间。
    """
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    create_user_name = models.CharField(max_length=10, blank=True, null=True, verbose_name="创建人姓名", default="admin")
    change_user_name = models.CharField(max_length=64, blank=True, null=True, verbose_name="修改人姓名", default="admin")

    class Meta:
        # 设置 abstract = True 表示这是一个抽象类，不会生成数据库表
        abstract = True

        # 可选：按创建时间倒序排列（最新在前）
        ordering = ['-create_time']

