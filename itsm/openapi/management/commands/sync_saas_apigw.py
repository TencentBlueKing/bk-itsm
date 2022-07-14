# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import traceback

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if not settings.IS_PAAS_V3:
            print("[bk-itsm]current version is not open v3,skip sync_saas_apigw")
            return

        print("[bk-itsm]call fetch_apigw_public_key")
        try:
            call_command("fetch_apigw_public_key")
        except Exception:
            print(
                "[bk-itsm]this env has not bk-itsm esb api,skip fetch_apigw_public_key "
            )
            traceback.print_exc()

        print("[bk-itsm]call fetch_esb_public_key")
        try:
            call_command("fetch_esb_public_key")
        except Exception:
            print(
                "[bk-itsm]this env has not bk-itsm esb api,skip fetch_esb_public_key "
            )
            traceback.print_exc()
