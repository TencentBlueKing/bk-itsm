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
from typing import Pattern, List
from urllib.parse import urlparse

from django.conf import settings

from common.log import logger
from common.pxfilter import XssHtml


# 开发框架公用方法
# 1. 页面输入内容转义（防止xss攻击）
# from common.utils import html_escape, url_escape, texteditor_escape
# 2. 转义html内容
# html_content = html_escape(input_content)
# 3. 转义url内容
# url_content = url_escape(input_content)
# 4. 转义富文本内容
# texteditor_content = texteditor_escape(input_content)


def html_escape(html, is_json=False):
    """
    Replace special characters "&", "<" and ">" to HTML-safe sequences.
    If the optional flag quote is true, the quotation mark character (")
    is also translated.
    rewrite the cgi method
    @param html: html代码
    @param is_json: 是否为json串（True/False） ，默认为False
    """
    # &转换
    if not is_json:
        html = html.replace("&", "&amp;")  # Must be done first!
    # <>转换
    html = html.replace("<", "&lt;")
    html = html.replace(">", "&gt;")
    # 单双引号转换
    if not is_json:
        html = html.replace(" ", "&nbsp;")
        html = html.replace('"', "&quot;")
        html = html.replace("'", "&#39;")
    return html


def url_escape(url):
    url = url.replace("<", "")
    url = url.replace(">", "")
    url = url.replace(" ", "")
    url = url.replace('"', "")
    url = url.replace("'", "")
    return url


def texteditor_escape(str_escape, unsupported_tags=None):
    """
    富文本处理
    @param str_escape: 要检测的字符串
    @param unsupported_tags: 不支持的标签集合
    """
    try:
        if unsupported_tags is None:
            allow_tags = []
        else:
            allow_tags = [
                tag for tag in XssHtml.allow_tags if tag not in unsupported_tags
            ]

        parser = XssHtml(allows=allow_tags)
        parser.feed(str_escape)
        parser.close()
        return parser.get_html()
    except Exception as e:
        logger.error("js脚本注入检测发生异常，错误信息：%s" % e)
        return str_escape


def cmp(a, b):
    """适配py2的cmp方法"""
    return (a > b) - (a < b)


def is_safe_url(url, allow_pattern: Pattern = None):
    try:
        parsed = urlparse(url)

        # 限定协议
        if parsed.scheme not in ["http", "https"]:
            return False

        # 限定域名
        hostname = parsed.hostname
        if allow_pattern and not allow_pattern.findall(hostname):
            return False

        return True
    except Exception:
        return False


def sanitize_user_content(content):
    if isinstance(content, dict):
        return {key: sanitize_user_content(value) for key, value in content.items()}
    elif isinstance(content, list):
        return [sanitize_user_content(element) for element in content]
    elif isinstance(content, str):
        return content.replace("\r\n", "").replace("\n", "")
    else:
        return content


def filter_user_sensitive_info(users: List):
    """
    过滤用户敏感信息
    """
    fields = settings.BK_USER_WHITE_FIELDS
    results = []
    for user_info in users:
        user = {}
        for field in fields:
            if field in user_info:
                user[field] = user_info[field]
        if user:
            results.append(user)
    return results
