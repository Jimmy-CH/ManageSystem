from django.db import models
from utils.encrypted_field import EncryptedCharField


class Asset(models.Model):
    name = models.CharField("资产名称", max_length=100)
    ip = models.GenericIPAddressField("IP 地址")
    port = models.IntegerField("SSH 端口", default=22)
    username = models.CharField("用户名", max_length=50)
    password = EncryptedCharField("密码", max_length=255)  # 建议加密
    os_type = models.CharField("操作系统", max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.ip})"

