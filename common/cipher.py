# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.

License for BK-ITSM 蓝鲸流程服务:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import binascii
import base64
import hashlib
import math

from Crypto.Cipher import AES
from Crypto.Random import new

from django.conf import settings


class AESCipher(object):
    def __init__(self, key, iv=None):
        self.bs = 16
        self.iv = iv
        self.key = hashlib.sha256(key.encode('utf-8')).digest()

    def encrypt(self, raw):
        if isinstance(raw, str):
            raw = raw.encode("utf-8")
        raw = self._pad(raw)
        iv = new().read(AES.block_size) if not self.iv else self.iv
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        iv = iv if not self.iv else ""
        result = base64.b64encode(iv + cipher.encrypt(raw))
        return result

    def decrypt(self, enc):
        if isinstance(enc, str):
            enc = enc.encode("utf-8")
        enc = base64.b64decode(enc)
        iv = enc[: AES.block_size] if not self.iv else self.iv
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        if not self.iv:
            return self._unpad(cipher.decrypt(enc[AES.block_size :])).decode('utf-8')
        else:
            return self._unpad(cipher.decrypt(enc)).decode('utf-8')

    def _pad(self, s):
        return s + bytes((self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs), encoding='utf-8')

    @staticmethod
    def _unpad(s):
        return s[: -ord(s[len(s) - 1 :])]

    @staticmethod
    def predict_length(length):
        """
        计算加密后的长度
        :param length: int
        :return: int
        """
        return int(math.ceil(((length + 1) // 16 * 16 + 16) / 3.0)) * 4


class AESVerification(object):
    @classmethod
    def cipher(cls):
        # 需要判断是否有指定密钥，如有，优先级最高
        aes_key = getattr(settings, "CALLBACK_AES_KEY", "APPROVAL_RESULT")
        x_key = settings.APP_CODE + '_' + aes_key
        return AESCipher(x_key)

    @classmethod
    def gen_signature(cls, message):
        signature = cls.cipher().encrypt(message)
        return signature

    @classmethod
    def verify(cls, message, signature):
        try:
            return message == cls.cipher().decrypt(signature)
        except (binascii.Error, ValueError):
            return False
