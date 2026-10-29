# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2025 Tencent.  All rights reserved.

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

import base64
import hashlib
import hmac
import json
import time

from django.conf import settings


CALLBACK_TOKEN_VERSION = "v2"
# 默认 7 天，可用 settings.CALLBACK_TOKEN_TTL 覆盖
CALLBACK_TOKEN_TTL = 7 * 24 * 3600


def _get_callback_sign_key():
    """优先取独立配置的 CALLBACK_SIGN_KEY，未配置则基于 SECRET_KEY 域分隔派生。"""
    key = getattr(settings, "CALLBACK_SIGN_KEY", "")
    if key:
        return key.encode("utf-8")
    return hashlib.sha256(
        ("itsm_callback_sign_v2|{}".format(settings.SECRET_KEY)).encode("utf-8")
    ).digest()


class CallbackToken(object):
    """单向 HMAC-SHA256 签名，绑定单据与状态并带时效，令牌中不含任何可还原的密钥。"""

    @staticmethod
    def ttl():
        return int(getattr(settings, "CALLBACK_TOKEN_TTL", CALLBACK_TOKEN_TTL))

    @classmethod
    def generate(cls, sn, current_status=""):
        """生成回调令牌，返回 str。"""
        payload = {
            "v": 2,
            "sn": sn,
            "status": current_status,
            "ts": int(time.time()),
        }
        body = base64.urlsafe_b64encode(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).decode("utf-8")
        signature = hmac.new(
            _get_callback_sign_key(), body.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return "{}:{}.{}".format(CALLBACK_TOKEN_VERSION, body, signature)

    @classmethod
    def verify(cls, token):
        """校验回调令牌，返回 {"is_passed": bool, "sn": str, "reason": str}。"""
        result = {"is_passed": False, "sn": "", "reason": "invalid"}

        if not token or not isinstance(token, str) or ":" not in token:
            result["reason"] = "malformed"
            return result

        version, rest = token.split(":", 1)
        if version != CALLBACK_TOKEN_VERSION:
            result["reason"] = "unsupported_version"
            return result

        try:
            body, signature = rest.rsplit(".", 1)
            expected = hmac.new(
                _get_callback_sign_key(), body.encode("utf-8"), hashlib.sha256
            ).hexdigest()
        except Exception:
            result["reason"] = "malformed"
            return result

        # 常量时间比较，避免时序侧信道
        if not hmac.compare_digest(signature, expected):
            result["reason"] = "bad_signature"
            return result

        try:
            payload = json.loads(
                base64.urlsafe_b64decode(body.encode("utf-8")).decode("utf-8")
            )
        except Exception:
            result["reason"] = "bad_payload"
            return result

        result["sn"] = payload.get("sn", "")
        if abs(int(time.time()) - int(payload.get("ts", 0))) > cls.ttl():
            result["reason"] = "expired"
            return result

        result["is_passed"] = True
        result["reason"] = "ok"
        return result
