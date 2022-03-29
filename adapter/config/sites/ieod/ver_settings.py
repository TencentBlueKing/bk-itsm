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

# 内部版配置
# init APIGW public_key
import os

# show.py 敏感信息处理, 内部白皮书地址，内部登陆地址
BK_IEOD_DOC_URL = os.environ.get("BK_IEOD_DOC_URL", "")
BK_IEOD_LOGIN_URL = os.environ.get("BK_IEOD_LOGIN_URL", "")

# itsm-tapd 网关API地址
ITSM_TAPD_APIGW = os.environ.get("ITSM_TAPD_APIGW", "")
# tapd 项目授权链接
TAPD_OAUTH_URL = os.environ.get("TAPD_OAUTH_URL", "")

# blueapps 相关的配置覆盖
BLUEAPPS_ACCOUNT_LOGIN_URL = os.environ.get("BK_IEOD_LOGIN_URL", "")
BLUEAPPS_ACCOUNT_LOGIN_PLAIN_URL = os.environ.get("BK_LOGIN_PLAIN_URL", "")
BLUEAPPS_SPECIFIC_REDIRECT_KEY = os.environ.get(
    "BLUEAPPS_SPECIFIC_REDIRECT_KEY",
)

# bkchat快速审批
USE_BKCHAT = True if os.getenv("USE_BKCHAT", "true").lower() == "true" else False
if USE_BKCHAT:
    BKCHAT_URL = os.environ.get("BKCHAT_URL", "")
    BKCHAT_APPID = os.environ.get("BKCHAT_APPID", "")
    BKCHAT_APPKEY = os.environ.get("BKCHAT_APPKEY", "")
