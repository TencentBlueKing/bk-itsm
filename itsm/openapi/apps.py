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
from blueapps.utils import get_client_by_user
from django.apps import AppConfig
from django.conf import settings

from common.log import logger


class OpenapiConfig(AppConfig):
    name = "itsm.openapi"

    def get_esb_public_key(self):
        client = get_client_by_user(settings.SYSTEM_USE_API_ACCOUNT)
        esb_result = client.esb.get_api_public_key()
        return esb_result

    def ready(self):
        print("init api public key")
        if not settings.IS_PAAS_V3:
            esb_result = self.get_esb_public_key()
            if esb_result["result"]:
                esb_public_key = esb_result["data"]["public_key"]
                try:
                    from apigw_manager.apigw.helper import PublicKeyManager

                    PublicKeyManager().set("bk-esb", esb_public_key)
                    PublicKeyManager().set("apigw", esb_public_key)
                except Exception:
                    logger.exception(
                        "[API] apigw_manager_context table is not migrated"
                    )
            else:
                logger.warning(
                    "[API] get esb public key error: %s" % esb_result["message"]
                )
        if settings.IS_PAAS_V3 and settings.RUN_VER == "ieod":
            esb_result = self.get_esb_public_key()
            if esb_result["result"]:
                esb_public_key = esb_result["data"]["public_key"]
                try:
                    from apigw_manager.apigw.helper import PublicKeyManager

                    PublicKeyManager().set("esb-ieod-clouds", esb_public_key)
                except Exception:
                    logger.exception(
                        "[API] apigw_manager_context table is not migrated"
                    )
            else:
                logger.warning(
                    "[API] get esb public key error: %s" % esb_result["message"]
                )

        print("init api public success")
