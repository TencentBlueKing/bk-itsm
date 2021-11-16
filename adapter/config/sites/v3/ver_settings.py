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
from adapter.utils.storage import RepoStorage

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("MYSQL_NAME"),
        "USER": os.environ.get("MYSQL_USER"),
        "PASSWORD": os.environ.get("MYSQL_PASSWORD"),
        "HOST": os.environ.get("MYSQL_HOST"),
        "PORT": os.environ.get("MYSQL_PORT"),
    },
}

BKREPO_ENDPOINT_URL = os.environ.get("BKREPO_ENDPOINT_URL")
BKREPO_USERNAME = os.environ.get("BKREPO_USERNAME")
BKREPO_PASSWORD = os.environ.get("BKREPO_PASSWORD")
BKREPO_PROJECT = os.environ.get("BKREPO_PROJECT")
BKREPO_BUCKET = os.environ.get("BKREPO_BUCKET")

STORE = RepoStorage()

# 企业微信发送，默认weixin，可配置为企业微信rtx
QY_WEIXIN = os.environ.get("BKAPP_WEIXIN_TYPE", "weixin")

BK_IAM_RESOURCE_API_HOST = get_bk_itsm_host()
