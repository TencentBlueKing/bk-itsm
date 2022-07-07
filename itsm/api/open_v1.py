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

from itertools import chain

from itsm.openapi.service.urls import urlpatterns as service_urlpatterns
from itsm.openapi.ticket.urls import urlpatterns as ticket_urlpatterns
from itsm.openapi.workflow.urls import urlpatterns as workflow_urlpatterns
from itsm.openapi.devops_plugin.urls import urlpatterns as devops_plugin_urlpatterns
from itsm.openapi.service_catalog.urls import urlpatterns as service_catalog_urlpatterns

# 公共URL配置
urlpatterns = list(
    chain(
        service_urlpatterns,
        ticket_urlpatterns,
        workflow_urlpatterns,
        devops_plugin_urlpatterns,
        service_catalog_urlpatterns,
    )
)
