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


class CollectionsGSE(object):
    """Collections of GSE APIS"""

    def __init__(self, client):
        self.client = client

        self.get_agent_info = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/gse/get_agent_info/',
            description=u'Agent心跳信息查询'
        )
        self.get_agent_status = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/gse/get_agent_status/',
            description=u'Agent在线状态查询'
        )
        self.proc_create_session = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/gse/proc_create_session/',
            description=u'进程管理：新建 session'
        )
        self.proc_get_task_result_by_id = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/gse/proc_get_task_result_by_id/',
            description=u'进程管理：获取任务结果'
        )
        self.proc_run_command = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/gse/proc_run_command/',
            description=u'进程管理：执行命令'
        )
