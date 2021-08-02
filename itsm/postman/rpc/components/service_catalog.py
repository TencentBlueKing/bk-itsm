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

from django.utils.translation import ugettext as _

from itsm.component.dlls.component import BaseComponentForm
from itsm.component.exceptions import RpcAPIError
from itsm.postman.rpc.core.component import BaseComponent
from itsm.service.models import ServiceCatalog


class GetServiceCatalog(BaseComponent):
    name = _("服务目录")
    code = "service_catalog"

    class Form(BaseComponentForm):
        def clean(self):
            """数据清理"""
            cleaned_data = super().clean()
            return cleaned_data

    def handle(self):

        self.response.payload = ServiceCatalog.tree_data(request=self.request)

    def validate_payload(self):
        if not isinstance(self.response.payload, list):
            raise RpcAPIError("Result must be List Type")

        for item in self.response.payload:
            if isinstance(item, dict) and not all(k in item for k in ["key", "name"]):
                raise RpcAPIError("Each item must both contain key and name")
