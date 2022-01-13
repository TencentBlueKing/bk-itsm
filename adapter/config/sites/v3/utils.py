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

import base64
import json
import os
from collections import defaultdict
from typing import Dict, List, Optional, Any

from common.log import logger


def str2bool(string: Optional[str], strict: bool = True) -> bool:
    """
    字符串转布尔值
    对于bool(str) 仅在len(str) == 0 or str is None 的情况下为False，为了适配bool("False") 等环境变量取值情况，定义该函数
    参考：https://stackoverflow.com/questions/21732123/convert-true-false-value-read-from-file-to-boolean
    :param string:
    :param strict: 严格校验，非 False / True / false / true  时抛出异常，用于环境变量的转换
    :return:
    """
    if string in ["False", "false"]:
        return False
    if string in ["True", "true"]:
        return True

    if strict:
        raise ValueError(f"{string} can not convert to bool")
    return bool(string)


def get_type_env(
    key: str, default: Any = None, _type: type = str, exempt_empty_str: bool = False
) -> Any:
    """
    获取环境变量并转为目标类型
    :param key: 变量名
    :param default: 默认值，若获取不到环境变量会默认使用该值
    :param _type: 环境变量需要转换的类型，不会转 default
    :param exempt_empty_str: 是否豁免空串
    :return:
    """
    value = os.getenv(key) or default
    if value == default:
        return value

    # 豁免空串
    if isinstance(value, str) and not value and exempt_empty_str:
        return value

    if _type == bool:
        return str2bool(value)

    try:
        value = _type(value)
    except TypeError:
        raise TypeError(f"can not convert env value -> {value} to type -> {_type}")

    return value


DEFAULT_MODULE_NAME = "default"

APP_CODE = get_type_env(key="BKPAAS_APP_ID", default="", _type=str)

ENVIRONMENT = get_type_env(key="BKPAAS_ENVIRONMENT", default="dev", _type=str)

BKPAAS_SERVICE_ADDRESSES_BKSAAS = os.getenv("BKPAAS_SERVICE_ADDRESSES_BKSAAS")
BKPAAS_SERVICE_ADDRESSES_BKSAAS_LIST: List[Dict[str, Dict[str, str]]] = (
    json.loads(base64.b64decode(BKPAAS_SERVICE_ADDRESSES_BKSAAS).decode("utf-8"))
    if BKPAAS_SERVICE_ADDRESSES_BKSAAS
    else {}
)

APP_CODE__SAAS_MODULE_HOST_MAP: Dict[str, Dict[str, str]] = defaultdict(
    lambda: defaultdict(str)
)

for item in BKPAAS_SERVICE_ADDRESSES_BKSAAS_LIST:
    module_info = item["key"]
    bk_app_code = module_info.get("bk_app_code")
    module_name = module_info.get("module_name")

    if not bk_app_code:
        continue
    if not module_name or module_name == "None":
        module_name = DEFAULT_MODULE_NAME

    APP_CODE__SAAS_MODULE_HOST_MAP[bk_app_code][module_name] = item["value"].get(
        ENVIRONMENT
    )

BK_ITSM_HOST = APP_CODE__SAAS_MODULE_HOST_MAP[APP_CODE][DEFAULT_MODULE_NAME]


def get_bk_itsm_host():
    logger.info("BK_ITSM_HOST={}".format(BK_ITSM_HOST))
    return BK_ITSM_HOST
