# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import logging
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command

from itsm.iadmin.contants import NOTICE_CENTER_SWITCH
from itsm.iadmin.models import SystemSettings

logger = logging.getLogger("root")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # 非PAAS v3 无法开启通知中心
        if not settings.IS_PAAS_V3:
            print(
                "[bk_itsm]current version is not open v3,skip register_bk_itsm_notice"
            )
            return
        try:
            call_command("register_application", raise_error=True)
            SystemSettings.objects.update_or_create(
                defaults={"value": "on"}, key=NOTICE_CENTER_SWITCH
            )
        except Exception as e:
            print("[register_bk_itsm_notice] err: {}".format(e))
