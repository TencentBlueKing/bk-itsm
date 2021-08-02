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

from django.db import models
from django.utils.translation import ugettext as _

from itsm.component.constants import LEN_NORMAL
from itsm.component.utils.basic import get_random_key
from itsm.sla import managers


class Model(models.Model):
    """基础字段"""

    DISPLAY_FIELDS = (
        'creator',
        'create_at',
        'updated_by',
        'update_at',
    )

    creator = models.CharField(_("创建人"), max_length=LEN_NORMAL)
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    update_at = models.DateTimeField(_("更新时间"), auto_now=True)
    updated_by = models.CharField(_("修改人"), max_length=LEN_NORMAL)
    is_deleted = models.BooleanField(_("是否软删除"), default=False)

    class Meta:
        abstract = True

    objects = managers.Manager()
    _objects = models.Manager()

    auth_resource = {"resource_type": "sla", "resource_type_name": "服务协议管理"}
    resource_operations = ["sla_manage"]

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    def hard_delete(self, using=None):
        super(Model, self).delete()

    @classmethod
    def get_unique_key(cls, name):
        """生成唯一的key"""

        key = get_random_key(name)
        retry = 0

        while retry < 60:
            # 满足条件，退出循环，且retry<60
            if not cls.objects.filter(key=key).exists():
                break

            key = get_random_key(name)
            retry += 1
        else:
            # 尝试60次一直重复，则放弃生成key
            return '##Err##'

        return key
