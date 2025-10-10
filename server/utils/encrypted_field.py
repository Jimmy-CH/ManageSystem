from cryptography.fernet import Fernet
from django.db import models
from django.conf import settings

# 生成密钥示例：Fernet.generate_key()
# 请在 settings.py 中设置：ENCRYPTION_KEY = 'your-32-url-safe-base64-encoded-key'


class EncryptedCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            decrypted = self.cipher.decrypt(value.encode()).decode()
            return decrypted
        except Exception:
            return value  # 解密失败时原样返回（兼容旧数据或错误数据）

    def to_python(self, value):
        if isinstance(value, str) or value is None:
            return value
        return str(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        if isinstance(value, str):
            encrypted = self.cipher.encrypt(value.encode()).decode()
            return encrypted
        return str(value)
