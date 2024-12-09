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
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from common.log import logger

CACHE_TIMEOUT = 30  # 缓存过期时间


class Context(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    key = models.CharField(max_length=255, unique=True)
    value = models.TextField(blank=True)

    def __str__(self):
        return self.key

    class Meta:
        db_table = "meta_context"


@receiver(post_save, sender=Context)
def update_cache(sender, instance, **kwargs):
    cache_key = f"meta_context_{instance.key}"
    cache.set(cache_key, instance.value, CACHE_TIMEOUT)


class ContextService:
    @staticmethod
    def get_context_value(key):
        """返回str类型的context_value"""
        cache_key = f"meta_context_{key}"
        context_value = cache.get(cache_key)
        if context_value is None:
            try:
                context_value = Context.objects.get(key=key).value
            except Context.DoesNotExist:
                logger.info(f"key为'{key}'的上下文配置不存在")
                context_value = ""
            cache.set(cache_key, context_value, CACHE_TIMEOUT)
        return context_value

    @staticmethod
    def get_context_value_list(key):
        """返回list类型的context_value"""
        context_value = ContextService.get_context_value(key)

        if context_value:
            # 分割字符串，去除空白字符，并去重
            unique_values = list(set(item.strip() for item in context_value.split(",")))
            return unique_values
        return []

    @staticmethod
    def notice_receiver_filter(receivers):
        """通知名单过滤"""
        if not receivers:
            return receivers

        if isinstance(receivers, str):
            receivers = receivers.strip().split(",")

        # 对黑名单的内容进行去重
        notice_blacklist = ContextService.get_context_value_list("notice_blacklist")
        filtered_receivers = [i for i in receivers if i not in notice_blacklist]
        return (
            filtered_receivers
            if isinstance(receivers, list)
            else ",".join(filtered_receivers)
        )


context_service = ContextService()
