from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import json
import base64

AES_LENGTH = 16


class AESCipher:
    def __init__(self, key):
        # 确保密钥长度是16字节
        key = key.encode('utf-8')
        if len(key) > AES_LENGTH:
            key = key[:AES_LENGTH]
        else:
            key = key.ljust(AES_LENGTH, b'\0')
        self.cipher = AES.new(key, AES.MODE_ECB)

    def encrypt(self, plain_value):
        plain_text = json.dumps(plain_value).encode('utf-8')
        padded = pad(plain_text, AES_LENGTH)
        encrypted = self.cipher.encrypt(padded)
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt_base64(self, cipher_text):
        if not cipher_text:
            return cipher_text

        cipher_bytes = base64.b64decode(cipher_text)

        # 检查长度
        if len(cipher_bytes) % AES_LENGTH != 0:
            raise ValueError(f"Invalid cipher length: {len(cipher_bytes)}, must be multiple of {AES_LENGTH}")

        decrypted_padded = self.cipher.decrypt(cipher_bytes)
        plain_text = unpad(decrypted_padded, AES_LENGTH).decode('utf-8')
        return json.loads(plain_text)
