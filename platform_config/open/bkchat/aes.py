# -*- coding: utf-8 -*-
"""
快速审批携带信息的加密&解密算法
使用AES算法，ECB模式
"""

import hashlib
import json
from base64 import urlsafe_b64decode, urlsafe_b64encode

from Crypto.Cipher import AES


def pad(text, blocksize=16):
    """
    PKCS#5 Padding
    """
    pad = blocksize - (len(text) % blocksize)
    return text + pad * chr(pad)


def unpad(text):
    """
    PKCS#5 Padding
    """
    pad = ord(text[-1])
    return text[:-pad]


class Aes(object):
    def __init__(self, app_id="default", app_key="kN8jP5fV4mZ6lN0u"):
        self.key = hashlib.md5(f"{app_id}{app_key}".encode("utf-8")).hexdigest()

    def decrypt_dict(self, ciphertext, base64=True):
        return json.loads(self.decrypt(ciphertext, base64))

    def encrypt_dict(self, value, base64=True):
        return self.encrypt(json.dumps(value), base64)

    def decrypt(self, ciphertext, base64=True):
        """
        AES Decrypt
        """
        if base64:
            ciphertext = urlsafe_b64decode(
                str(ciphertext + "=" * (4 - len(ciphertext) % 4))
            )

        data = ciphertext
        key = self.key.encode("utf-8")
        key = hashlib.md5(key).digest()
        cipher = AES.new(key, AES.MODE_ECB)
        return unpad(cipher.decrypt(data).decode())

    def encrypt(self, plaintext, base64=True):
        """
        AES Encrypt
        """
        key = self.key.encode("utf-8")
        key = hashlib.md5(key).digest()
        cipher = AES.new(key, AES.MODE_ECB)
        plaintext = pad(plaintext).encode("utf-8")
        ciphertext = cipher.encrypt(plaintext)

        # 将密文base64加密
        if base64:
            ciphertext = urlsafe_b64encode(ciphertext).decode().rstrip("=")

        return ciphertext
