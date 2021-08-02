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


class CollectionsITSM(object):
    """Collections of ITSM APIS"""

    def __init__(self, client):
        self.client = client

        self.create_ticket = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/itsm/create_ticket/',
            description=u'创建单据'
        )
        self.get_service_catalogs = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/itsm/get_service_catalogs/',
            description=u'服务目录查询'
        )
        self.get_service_detail = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/itsm/get_service_detail/',
            description=u'服务详情查询'
        )
        self.get_services = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/itsm/get_services/',
            description=u'服务列表查询'
        )
        self.get_ticket_info = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/itsm/get_ticket_info/',
            description=u'单据详情查询'
        )
        self.get_ticket_logs = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/itsm/get_ticket_logs/',
            description=u'单据日志查询'
        )
        self.get_ticket_status = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/itsm/get_ticket_status/',
            description=u'单据状态查询'
        )
        self.get_tickets = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/itsm/get_tickets/',
            description=u'获取单据列表'
        )
        self.operate_node = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/itsm/operate_node/',
            description=u'处理单据节点'
        )
        self.operate_ticket = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/itsm/operate_ticket/',
            description=u'处理单据'
        )
