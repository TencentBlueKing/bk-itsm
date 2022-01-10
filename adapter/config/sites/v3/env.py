# coding=utf-8
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

import os

from adapter.config.sites.v3.utils import get_bk_itsm_host

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")

os.environ["BKAPP_REDIS_HOST"] = REDIS_HOST
os.environ["BKAPP_REDIS_PORT"] = REDIS_PORT
os.environ["BKAPP_REDIS_PASSWORD"] = REDIS_PASSWORD

if "BKAPP_FRONTEND_URL" not in os.environ:
    os.environ["BKAPP_FRONTEND_URL"] = get_bk_itsm_host()
