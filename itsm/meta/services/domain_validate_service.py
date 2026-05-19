# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C)2025 Tencent.  All rights reserved.

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
import logging
import re
from urllib.parse import urlparse

from itsm.meta.services.context import ContextService


class DomainValidateService:
    def __init__(self, key: str = "domain_regex_pattern"):
        self.allow_patterns = self.compile_domain_patterns(key)

    def is_safe_url(self, url):
        try:
            parsed = urlparse(url)

            # 限定协议
            if parsed.scheme not in ["http", "https"]:
                return False

            # 限定域名
            hostname = parsed.hostname
            if not hostname:
                return False

            # 如果没有配置允许的域名正则表达式列表，则默认允许
            if not self.allow_patterns:
                return True

            # 匹配域名是否符合允许的正则表达式列表
            for pattern in self.allow_patterns:
                if pattern.match(hostname):
                    return True

            return False
        except Exception as e:  # 如果可能，特定捕获异常类型，比如 ValueError
            logging.error(f"error parsing URL: {e}")
            return False

    @staticmethod
    def compile_domain_patterns(key):
        """编译并返回域名正则表达式"""
        patterns = ContextService.get_context_value(key)
        if not patterns:
            return []
        return [re.compile(i.strip()) for i in patterns.split(";") if i.strip()]
