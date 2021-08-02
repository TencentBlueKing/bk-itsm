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

from ..base import ComponentAPI


class CollectionsBkPaas(object):
    """Collections of BK_PAAS APIS"""

    def __init__(self, client):
        self.client = client

        self.get_app_info = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/bk_paas/get_app_info/',
            description='获取应用信息'
        )
        self.create_app = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/bk_paas/create_app/',
            description='创建一个轻应用'
        )
        self.edit_app = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/bk_paas/edit_app/',
            description='编辑一个轻应用'
        )
        self.del_app = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/bk_paas/del_app/',
            description='下架一个轻应用'
        )
        self.modify_app_logo = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/bk_paas/modify_app_logo/',
            description='修改轻应用的 logo'
        )
