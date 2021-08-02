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

from django.conf import settings
from common.log import logger

from iam import Subject, Action
from iam.auth.models import ApiAuthResourceWithPath, ApiAuthRequest
from itsm.auth_iam.utils import IamRequest
from itsm.component.constants import DEFAULT_PROJECT_PROJECT_KEY
from itsm.component.exceptions import AuthMigrateError
from itsm.project.models import Project


class MigrateIamRequest(IamRequest):
    
    def grant_or_revoke_instance_permission(self, actions, resources, operate,
                                            project_key=DEFAULT_PROJECT_PROJECT_KEY):

        subject = Subject("user", self.request.user.username if self.request else self.username)
        actions = [Action(action) for action in actions]

        project = self.get_project(project_key)

        resources = [
            ApiAuthResourceWithPath(
                settings.BK_IAM_SYSTEM_ID,
                resource['resource_type'],
                path=[
                    {
                        "type": "project",
                        "id": project_key,
                        "name": project.name
                    },
                    {
                        "type": resource['resource_type'],
                        "id": resource['resource_id'],
                        "name": resource['resource_name']
                    }
                ]
            )
            for resource in resources
        ]

        for action in actions:
            request = ApiAuthRequest(settings.BK_IAM_SYSTEM_ID, subject, action, resources, None,
                                     operate)
            try:
                self._iam.grant_or_revoke_path_permission(request,
                                                          bk_username=self.request.user.username)
            except BaseException as error:
                logger.error("实例权限迁移失败， error={}, actions={}, operate={}, project_key={}"
                             .format(error, actions, operate, project_key))
                raise AuthMigrateError("权限迁移失败，请检查您的配置 error={}, actions={}, operate={}, "
                                       "project_key={}"
                                       .format(error, actions, operate, project_key))

    def grant_or_revoke_permit_with_project(self, actions, operate,
                                            project_key=DEFAULT_PROJECT_PROJECT_KEY):

        subject = Subject("user", self.request.user.username if self.request else self.username)
        actions = [Action(action) for action in actions]

        project = self.get_project(project_key)

        resources = [
            ApiAuthResourceWithPath(
                settings.BK_IAM_SYSTEM_ID,
                "project",
                path=[
                    {
                        "type": "project",
                        "id": project_key,
                        "name": project.name
                    },
                ]
            )
        ]

        for action in actions:
            request = ApiAuthRequest(settings.BK_IAM_SYSTEM_ID, subject, action, resources, None,
                                     operate)
            try:
                self._iam.grant_or_revoke_path_permission(request,
                                                          bk_username=self.request.user.username)
            except BaseException as error:
                logger.error("项目权限迁移失败， error={}, actions={}, operate={}, project_key={}"
                             .format(error, actions, operate, project_key))
                raise AuthMigrateError("项目权限迁移失败，请检查您的配置 error={}, actions={}, operate={},"
                                       " project_key={}"
                                       .format(error, actions, operate, project_key))

    def get_project(self, project_key):
        return Project.objects.get(key=project_key)
