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


# 跳过一下接口的请求记录
EXCLUDED_URLS = [
    'login/accounts/is_login',
    'login/accounts/get_user',
    'login/accounts/get_user_profile',
    'v2/cc/search_business',
    'v2/bk_login/get_all_users',
    'v2/bk_login/get_user',
    'v2/esb/get_components',
    'v2/esb/get_systems',
    'v2/cmsi/send_msg',
    'v2/cmsi/send_mail',
    'v2/cmsi/send_sms',
    'v2/cmsi/send_weixin',
    'v2/usermanage/department_list',
    'v2/usermanage/list_users',
    'v2/usermanage/list_profile_departments',
    'v2/cc/search_object_attribute',
]


def rt_filter(prepared_request, **kwargs):
    """请求过滤器"""

    for url in EXCLUDED_URLS:
        if url in prepared_request.url:
            return False

    return True
