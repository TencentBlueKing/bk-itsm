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

# 内部版配置

import os

from adapter.utils.storage import CephStorage
from . import api as ADAPTER_API  # noqa

ESB_SDK_NAME = 'blueking.component.ieod'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('GCS_MYSQL_NAME'),
        'USER': os.environ.get('GCS_MYSQL_USER'),
        'PASSWORD': os.environ.get('GCS_MYSQL_PASSWORD'),
        'HOST': os.environ.get('GCS_MYSQL_HOST'),
        'PORT': os.environ.get('GCS_MYSQL_PORT'),
    },
}

# RGW 相关配置，请修改为蓝鲸为你分配的相关信息
RGW_ACCESS_KEY_ID = os.environ.get('CEPH_AWS_ACCESS_KEY_ID', '')
RGW_SECRET_ACCESS_KEY = os.environ.get('CEPH_AWS_SECRET_ACCESS_KEY', '')
RGW_STORAGE_BUCKET_NAME = os.environ.get('CEPH_BUCKET', '')
RGW_ENDPOINT_URL = os.environ.get('CEPH_RGW_URL', '')

# TODO: 暂时开放文件读写控制，后期改为私有存储+临时访问链接的方式
RGW_OBJECT_PARAMETERS = {'ACL': 'public-read'}
DEFAULT_FILE_STORAGE = 'bkstorages.backends.rgw.RGWBoto3Storage'

# STATICFILES_STORAGE = 'bkstorages.backends.rgw.StaticRGWBoto3Storage'


STORE = CephStorage()

# 企业微信发送
QY_WEIXIN = 'rtx'
