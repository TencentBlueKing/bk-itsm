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

logger = logging.getLogger("root")

# 回调 URL 长度上限，超出视为异常输入
MAX_URL_LENGTH = 2048
# URL 中不允许出现的字符：控制字符与空白，防 CRLF 注入请求行/请求头
URL_FORBIDDEN_CHARS = frozenset(chr(i) for i in range(0x20)) | {"\x7f", " "}
# 域名白名单分隔符：英文逗号/分号/换行，三选一即可
PATTERN_SEPARATORS = frozenset({",", ";", "\n", "\r"})
# 正则内的括号结构，其中的分隔符不作为规则边界（如 {2,3}、[^,]）
PATTERN_BRACKETS = {"[": "]", "{": "}", "(": ")"}
# 通配符风格规则 `*.example.com`：整条仅由 `*.` 与域名字符构成时自动转正则
WILDCARD_PATTERN = re.compile(r"^\*\.[a-zA-Z0-9.-]+$")


class DomainValidateService:
    def __init__(self, key: str = "domain_regex_pattern"):
        self.key = key
        # 编译失败的原始规则，供调用方区分“配置异常”与“域名未放行”
        self.invalid_patterns = []
        self.allow_patterns = self.compile_domain_patterns(key)

    def is_safe_url(self, url, fail_open=True):
        """域名白名单校验

        fail_open=True：白名单未配置时放行（Postman 远程 API 等内网场景，保持存量行为）
        fail_open=False：白名单未配置时拒绝（工单回调等对外场景，默认拒绝）
        """
        try:
            parsed = urlparse(url)

            # 限定协议
            if parsed.scheme not in ["http", "https"]:
                return False

            # 限定域名
            hostname = parsed.hostname
            if not hostname:
                return False

            # 没有配置允许的域名正则表达式列表
            if not self.allow_patterns:
                logger.warning(
                    "[CALLBACK_URL] 域名白名单为空, key is %s, host is %s, result is %s",
                    self.key,
                    hostname,
                    "allowed" if fail_open else "rejected",
                )
                return fail_open

            # 匹配域名是否符合允许的正则表达式列表
            for pattern in self.allow_patterns:
                if pattern.match(hostname):
                    return True

            return False
        except Exception as e:  # 如果可能，特定捕获异常类型，比如 ValueError
            logging.error(f"error parsing URL: {e}")
            return False

    @staticmethod
    def is_wellformed_url(url):
        """URL 规范性校验：只管 URL 本身是否合法，不限制 host（内网 IP 同样放行）。

        与 is_safe_url 解耦——后者只做域名白名单匹配，两者可独立启用。
        覆盖：类型、长度、控制字符与空白（CRLF 注入）、协议、host 存在、URL 内携带凭据。
        """
        if not isinstance(url, str) or not url.strip():
            return False

        if len(url) > MAX_URL_LENGTH:
            logger.warning("[CALLBACK_URL] 拒绝超长 URL, length is %s", len(url))
            return False

        if any(char in URL_FORBIDDEN_CHARS for char in url):
            logger.warning("[CALLBACK_URL] 拒绝含控制字符或空白的 URL")
            return False

        try:
            parsed = urlparse(url)
        except Exception as error:  # noqa
            logger.warning("[CALLBACK_URL] URL 解析失败: %s", error)
            return False

        if parsed.scheme not in ["http", "https"]:
            logger.warning("[CALLBACK_URL] 拒绝非 http/https 协议: %s", parsed.scheme)
            return False

        if not parsed.hostname:
            logger.warning("[CALLBACK_URL] 拒绝缺少 host 的 URL")
            return False

        if parsed.username or parsed.password:
            logger.warning("[CALLBACK_URL] 拒绝携带凭据的 URL")
            return False

        return True

    @staticmethod
    def split_patterns(raw):
        """按逗号/分号/换行拆分多条域名正则。

        正则括号内（如 `a{2,3}`、`[^,]`）与转义字符（如 `\,`）中的分隔符不切分。
        """
        if not raw:
            return []

        parts, buffer, stack = [], [], []
        index, length = 0, len(raw)
        while index < length:
            char = raw[index]
            if char == "\\" and index + 1 < length:
                buffer.append(raw[index : index + 2])
                index += 2
                continue
            if char in PATTERN_BRACKETS:
                stack.append(PATTERN_BRACKETS[char])
            elif stack and char == stack[-1]:
                stack.pop()
            elif not stack and char in PATTERN_SEPARATORS:
                parts.append("".join(buffer))
                buffer = []
                index += 1
                continue
            buffer.append(char)
            index += 1

        parts.append("".join(buffer))
        return [part.strip() for part in parts if part.strip()]

    @staticmethod
    def normalize_pattern(pattern):
        """`*.example.com` 通配符写法转正则，其余按正则原样处理。"""
        if WILDCARD_PATTERN.match(pattern):
            return r"^([a-z0-9-]+\.)*" + re.escape(pattern[2:].lower()) + "$"
        return pattern

    def compile_domain_patterns(self, key):
        """编译并返回域名正则表达式。

        单条规则非法时仅记录并跳过，避免一条写错的配置导致全部提单请求 500；
        非法规则会保留在 invalid_patterns 中，由调用方决定如何提示。
        """
        patterns = ContextService.get_context_value(key)
        if not patterns:
            return []

        compiled = []
        for pattern in self.split_patterns(patterns):
            try:
                compiled.append(re.compile(self.normalize_pattern(pattern)))
            except re.error as error:
                self.invalid_patterns.append(pattern)
                logger.error(
                    "[CALLBACK_URL] 域名白名单正则非法, key is %s, pattern is %s, error is %s",
                    key,
                    pattern,
                    error,
                )
        return compiled
