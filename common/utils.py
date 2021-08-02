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


# 开发框架公用方法
# 1. 页面输入内容转义（防止xss攻击）
# from common.utils import html_escape, url_escape, texteditor_escape
# 2. 转义html内容
# html_content = html_escape(input_content)
# 3. 转义url内容
# url_content = url_escape(input_content)
# 4. 转义富文本内容
# texteditor_content = texteditor_escape(input_content)


from common.log import logger
from common.pxfilter import XssHtml


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
        html = html.replace(' ', "&nbsp;")
        html = html.replace('"', "&quot;")
        html = html.replace("'", "&#39;")
    return html


def url_escape(url):
    url = url.replace("<", "")
    url = url.replace(">", "")
    url = url.replace(' ', "")
    url = url.replace('"', "")
    url = url.replace("'", "")
    return url


def texteditor_escape(str_escape):
    """
    富文本处理
    @param str_escape: 要检测的字符串
    """
    try:
        parser = XssHtml()
        parser.feed(str_escape)
        parser.close()
        return parser.get_html()
    except Exception as e:
        logger.error("js脚本注入检测发生异常，错误信息：%s" % e)
        return str_escape


def cmp(a, b):
    """适配py2的cmp方法"""
    return (a > b) - (a < b)
