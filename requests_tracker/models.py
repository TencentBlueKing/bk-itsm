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


# """
# requests_tracker.models
# =======================
# """

import json

from django.db import models, transaction
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from requests_tracker.constants import *  # noqa


class Record(models.Model):
    # tracking record info
    uid = models.UUIDField(unique=True)
    api_uid = models.CharField(max_length=64, blank=True, default='')

    ticket_id = models.IntegerField(_('单据ID'), default=0)
    state_id = models.IntegerField(_('节点ID'), default=0)
    api_instance_id = models.IntegerField(_('api实例主键'), default=0)

    remark = models.CharField(max_length=255, blank=True, default='')
    # request info
    method = models.CharField(max_length=8, choices=list(zip(ALL_METHODS, ALL_METHODS)), default=GET)
    url = models.URLField(max_length=255)
    request_message = models.TextField(blank=True)
    operator = models.CharField(max_length=255)
    request_host = models.CharField(max_length=128)

    # response info
    status_code = models.PositiveSmallIntegerField(default=0)
    response_message = models.TextField(blank=True)

    # important datetimes
    date_created = models.DateTimeField(default=now)
    duration = models.DurationField(blank=True, null=True)

    def __unicode__(self):
        return str("[#%s] %s %s" % (self.pk, self.method, self.url))

    @transaction.atomic
    def update(self, **kwargs):
        Record.objects.filter(pk=self.pk).update(**kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def get_last_response(cls, ticket_id, state_id, api_instance_id):
        """获取API节点的接口调用记录（最后一次）"""

        record = cls.objects.filter(ticket_id=ticket_id, state_id=state_id, api_instance_id=api_instance_id).last()

        if record:
            try:
                return json.loads(record.response_message)
            except BaseException:
                return record.response_message

        return {}

    class Meta:
        db_table = "Records"
        ordering = ("-date_created", "-method")
