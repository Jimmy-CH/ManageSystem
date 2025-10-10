import base64
import hashlib
from django.db import models
from django.conf import settings
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet


# 生成密钥示例：Fernet.generate_key()
# 请在 settings.py 中设置：ENCRYPTION_KEY = 'your-32-url-safe-base64-encoded-key'

#
# class EncryptedCharField(models.CharField):
#     def __init__(self, *args, **kwargs):
#         self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
#         super().__init__(*args, **kwargs)
#
#     def from_db_value(self, value, expression, connection):
#         if value is None:
#             return value
#         try:
#             decrypted = self.cipher.decrypt(value.encode()).decode()
#             return decrypted
#         except Exception:
#             return value  # 解密失败时原样返回（兼容旧数据或错误数据）
#
#     def to_python(self, value):
#         if isinstance(value, str) or value is None:
#             return value
#         return str(value)
#
#     def get_prep_value(self, value):
#         if value is None:
#             return value
#         if isinstance(value, str):
#             encrypted = self.cipher.encrypt(value.encode()).decode()
#             return encrypted
#         return str(value)


class EncryptedCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 从 ENCRYPTION_KEY 生成 32 字节密钥
        key_source = settings.ENCRYPTION_KEY
        self.key = hashlib.sha256(key_source.encode()).digest()[:32]

    def _encrypt(self, plaintext):
        if plaintext is None:
            return None
        # 使用明文的哈希作为 nonce（确保确定性）
        nonce = hashlib.sha256(plaintext.encode()).digest()[:12]  # GCM 要求 12 字节
        cipher = Cipher(algorithms.AES(self.key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
        # GCM 会生成 16 字节的 tag
        tag = encryptor.tag
        # 存储结构: nonce (12) + tag (16) + ciphertext
        encrypted_data = nonce + tag + ciphertext
        return base64.urlsafe_b64encode(encrypted_data).decode()

    def _decrypt(self, ciphertext_b64):
        if ciphertext_b64 is None:
            return None
        data = base64.urlsafe_b64decode(ciphertext_b64.encode())
        nonce = data[:12]
        tag = data[12:28]          # 12 + 16 = 28
        ciphertext = data[28:]
        cipher = Cipher(algorithms.AES(self.key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext.decode()

    def from_db_value(self, value, expression, connection):
        return self._decrypt(value)

    def get_prep_value(self, value):
        return self._encrypt(value)

    @classmethod
    def encrypt_value(cls, plain_text):
        if plain_text is None:
            return None
        key = hashlib.sha256(settings.ENCRYPTION_KEY.encode()).digest()[:32]
        nonce = hashlib.sha256(plain_text.encode()).digest()[:12]
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plain_text.encode()) + encryptor.finalize()
        tag = encryptor.tag
        encrypted_data = nonce + tag + ciphertext
        return base64.urlsafe_b64encode(encrypted_data).decode()

