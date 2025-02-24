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

from .accounts import WeixinAccount
from .decorators import weixin_login_exempt
from common.log import logger

def print_request_info(request):
    """打印调试"""

    try:
        body = request.body
        body_str = body.decode("utf-8")
    except UnicodeDecodeError:
        body_str = "非文本数据"

    logger.info("debug，打印完整请求信息: \n %s", {
        "full_url": request.build_absolute_uri(),
        "scheme": request.scheme,
        "method": request.method,
        "path": request.path,
        "full_path": request.get_full_path(),
        "query_params": request.GET.dict(),
        "body": body_str,
        "headers": dict(request.headers),
    })


@weixin_login_exempt
def login(request):
    """微信登录"""
    print('weixin login')
    logger.info('enter weixin login')
    print_request_info(request)
    return WeixinAccount().login(request)
