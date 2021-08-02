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

__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved."

from rest_framework.serializers import ModelSerializer as BaseModelSerializer


class ModelSerializer(BaseModelSerializer):
    def __init__(self, instance=None, *args, **kwargs):
        super(ModelSerializer, self).__init__(instance, *args, **kwargs)

    def update_one_field_relation(self, field_key, data, instance):
        """
        更新和一个字段关系
        """
        field = getattr(instance, field_key)
        old_items = field.all()
        if not self.partial:
            field.remove(*old_items)
        field_serializer = self.fields.fields[field_key].child
        for field_data in data:
            _id = field_data.get("id")
            if _id is None:
                _obj = field_serializer.create(field_data)
            else:
                _obj = field_serializer.update(field_serializer.Meta.model.objects.get(id=_id), field_data)
            if not self.partial or (self.partial and not old_items.filter(id=_id).exists()):
                field.add(_obj)
        return instance

    def update_many_to_many_relation(self, instance, fields):
        """
        更新多对多关系
        """
        for field_key, data in list(fields.items()):
            self.update_one_field_relation(field_key, data, instance)
        return instance
