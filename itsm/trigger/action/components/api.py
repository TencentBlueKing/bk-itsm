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

from itsm.component.esb.backend_component import bk
from itsm.postman.models import RemoteApi
from itsm.trigger.action.core.component import BaseComponent
from itsm.trigger.action.core import ApiSourceField, ApiInfoField, BaseForm, JSONField

__register_ignore__ = False


class ApiForms(BaseForm):
    """
    发送通知的输入数据格式
    api_info: 为API的参数配置信息，根据API字段进行刷新
    """

    api_source = ApiSourceField(name=_("API接口ID"))
    req_params = ApiInfoField(name=_("API请求参数配置"))
    response = JSONField(
        name=_("API系统返回参数"), display=False, default={"ref_type": "reference", "value": "api_response_message"}
    )


class APIComponent(BaseComponent):
    name = _("API执行")
    code = "api"
    is_async = False
    form_class = ApiForms

    def get_api_source_config(self):
        remote_api = RemoteApi._objects.get(id=self.data.get_one_of_inputs("api_source"))
        api_config = remote_api.get_api_config(self.data.get_one_of_inputs("req_params"))
        # 默认API处理人的请求用户为触发事件的操作人
        api_config['query_params']['__remote_user__'] = self.context.get("operator", 'admin')
        return api_config

    def _execute(self):
        """
        API执行的业务逻辑，参考API节点
        """
        api_config = self.get_api_source_config()
        rsp = bk.http(config=api_config)
        self.data.set_outputs("api_response_message", rsp.get('message'))
        self.data.set_outputs("api_response", rsp.get('message'))
        if rsp['result']:
            return True
        self.data.set_outputs("message", rsp['message'])
        return False
