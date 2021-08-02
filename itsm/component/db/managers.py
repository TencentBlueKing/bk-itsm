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


import django
from django.db import models, transaction
from django.db.models.query import QuerySet

from mptt.managers import TreeManager


if django.VERSION >= (1, 6):
    # TreeManager bug:
    if "get_query_set" in TreeManager.__dict__:
        # TreeManager should not define this, it messes things up.
        del TreeManager.get_query_set

        # See also:
        # https://github.com/django-mptt/django-mptt/pull/388

        # Once this has been merged, a new release for django-mptt has been
        # made, and we can specify the new version in our requirements, this
        # hack can be removed.


class SoftDeleteQuerySet(QuerySet):
    def delete(self):
        with transaction.atomic():
            return super(SoftDeleteQuerySet, self).select_for_update().update(is_deleted=True)

    def hard_delete(self):
        return super(SoftDeleteQuerySet, self).delete()


class BaseTreeManager(TreeManager):
    """soft delete: objects.delete()"""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)
        # return SoftDeleteQuerySet(self.model).select_related("parent")


class Manager(models.Manager):
    """支持软删除"""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model).filter(is_deleted=False)
