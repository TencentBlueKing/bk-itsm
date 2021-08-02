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

#     serializers相关模块代码
#     https://www.django-rest-framework.org/api-guide/serializers/#dynamically-modifying-fields
#     >>> class UserSerializer(DynamicFieldsModelSerializer):
#     >>>     class Meta:
#     >>>         model = User
#     >>>         fields = ['id', 'username', 'email']
#     >>>
#     >>> print(UserSerializer(user))
#     {'id': 2, 'username': 'jonwatts', 'email': 'jon@example.com'}
#     >>>
#     >>> print(UserSerializer(user, fields=('id', 'email')))
#     {'id': 2, 'email': 'jon@example.com'}

from django.db.models import Model
from rest_framework import serializers
from rest_framework.fields import empty

from common.log import logger
from itsm.auth_iam.utils import IamRequest
from itsm.component.constants import DEFAULT_PROJECT_PROJECT_KEY


class AuthModelSerializer(serializers.ModelSerializer):
    """
    权限中心接入每个资源权限内容序列化
    """

    def __init__(self, instance=None, data=empty, **kwargs):
        super(AuthModelSerializer, self).__init__(instance, data, **kwargs)

        self.resource_permissions = {}
        if self.instance and self.context.get("request"):
            self.resource_permissions = self.get_resource_permission()

    def get_resource_permission(self):
        """
        获取资源的权限
        :return: 
        """
        instance_list = (
            [self.instance]
            if isinstance(self.instance, self.Meta.model) or isinstance(self.instance, dict)
            else self.instance
        )
        resource_type = self.Meta.model.auth_resource.get('resource_type', None)
        if resource_type is None:
            return []

        instance = instance_list[0]
        project_key = DEFAULT_PROJECT_PROJECT_KEY
        if hasattr(instance, "project_key"):
            project_key = getattr(instance, "project_key")

        resources = [
            {"resource_id": str(item.id), "resource_type": resource_type,
             "creator": getattr(item, "creator", "")}
            if isinstance(item, self.Meta.model)
            else {"resource_id": str(item['id']), "resource_type": resource_type,
                  "creator": item.get("creator")}
            for item in instance_list
        ]
        iam_client = IamRequest(self.context.get('request'))
        try:
            return iam_client.batch_resource_multi_actions_allowed(
                self.Meta.model.resource_operations, resources, project_key=project_key)
        except BaseException:
            logger.exception("get auth permission error, resource is %s" % resource_type)
            return []

    def to_representation(self, instance):
        data = super(AuthModelSerializer, self).to_representation(instance)
        return self.update_auth_actions(instance, data)

    def update_auth_actions(self, instance, data):
        """
        更新权限信息
        """
        if instance is not None:
            resource_id = str(instance.id if isinstance(instance, Model) else instance['id'])
            instance_permissions = self.resource_permissions.get(resource_id, {})
            data.update(
                auth_actions=[action for action, result in instance_permissions.items() if result])
        return data


class DynamicFieldsModelSerializer(AuthModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        # clean fields
        if isinstance(fields, (list, tuple)):
            valid_fields = set(self.fields.keys())
            fields = list(field for field in fields if field in valid_fields)

        if fields is not None and fields:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
