# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C)2024 THL A29 Limited, a Tencent company.  All rights reserved.

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

from django.core.cache import cache

from itsm.component.constants import CACHE_5MIN
from itsm.meta.models import Context
from common.log import logger


class ContextService:
    @staticmethod
    def get_context_value(key):
        """返回context_value，若不存在则返回None"""
        cache_key = f"meta_context_{key}"
        context_value = cache.get(cache_key)

        # 如果缓存中没有找到值
        if context_value is None:
            try:
                # 尝试从数据库中获取值
                context_value = Context.objects.get(key=key).value
            except Context.DoesNotExist:
                logger.info(f"数据库中key为'{key}'的上下文配置不存在")
                context_value = None
            except Exception as e:
                logger.error(f"获取key为'{key}'的上下文配置时发生错误: {str(e)}")
                context_value = None

            # 将获取到的值存入缓存
            cache.set(cache_key, context_value, CACHE_5MIN)

        return context_value

    @staticmethod
    def get_context_value_list(key):
        """返回list类型的context_value，若不存在则返回空列表"""
        context_value = ContextService.get_context_value(key)

        if context_value:
            # 分割字符串，去除空白字符，并去重
            unique_values = list(set(item.strip() for item in context_value.split(",")))
            return unique_values
        return []
