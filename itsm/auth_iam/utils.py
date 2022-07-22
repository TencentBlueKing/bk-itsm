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
from iam.api.client import Client
from iam import IAM, Subject, Action, Resource
from iam.apply.models import (
    ActionWithoutResources,
    ActionWithResources,
    Application,
    RelatedResourceType,
)
from iam.apply.models import ResourceInstance, ResourceNode
from iam.auth.models import MultiActionRequest, Request
from blueapps.utils import get_request

from common.log import logger
from itsm.component.constants import (
    DEFAULT_PROJECT_PROJECT_KEY,
    PUBLIC_PROJECT_PROJECT_KEY,
)
from itsm.component.exceptions import IamGrantCreatorActionError
from itsm.project.models import Project
from itsm.workflow.models import TemplateField


class IamRequest(object):
    def __init__(self, request=None, username=None):
        self._iam = IAM(
            settings.APP_CODE,
            settings.SECRET_KEY,
            settings.BK_IAM_INNER_HOST,
            settings.BK_IAM_ESB_PAAS_HOST,
        )
        self.request = request
        self.username = username

    def make_application(self, apply_info):
        # 1. make application
        # 这里支持带层级的资源, 例如 biz: 1/set: 2/host: 3
        # 如果不带层级, list中只有对应资源实例

        actions = []

        for apply_action in apply_info.get("actions"):
            # 每次请求可能跨系统
            related_resource_types = []
            for related_resource_type in apply_action["related_resource_types"]:

                instances = [
                    ResourceInstance(
                        [
                            ResourceNode(
                                resource_instance["type"],
                                resource_instance["id"],
                                resource_instance["name"],
                            )
                        ]
                    )
                    for resource_instances in related_resource_type["instances"]
                    for resource_instance in resource_instances
                ]
                if instances:
                    # 同一个资源类型可以包含多个资源
                    related_resource_types.append(
                        RelatedResourceType(
                            related_resource_type["system_id"],
                            related_resource_type["type"],
                            instances,
                        )
                    )

            if related_resource_types:
                actions.append(
                    ActionWithResources(apply_action["id"], related_resource_types)
                )
            else:
                actions.append(ActionWithoutResources(apply_action["id"]))

        return Application(settings.BK_IAM_SYSTEM_ID, actions)

    def generate_apply_url(self, apply_info):
        """
        处理无权限 - 跳转申请列表
        """
        bk_token = None
        if self.request:
            bk_token = self.request.COOKIES.get("bk_token", "")
            self.username = self.request.user.username

        ok, message, url = self._iam._client.get_apply_url(
            bk_token, self.username, apply_info
        )
        if not ok:
            logger.error("iam generate apply url fail: %s", message)
            return "%s/apply-custom-perm" % settings.BK_IAM_SAAS_HOST
        return url

    def batch_resource_multi_actions_allowed(
        self, actions, resources, project_key=DEFAULT_PROJECT_PROJECT_KEY
    ):
        """
        获取批量资源的权限
        :return:
        """
        if settings.ENVIRONMENT == "dev":
            # dev 环境不走权限中心
            actions_result = {action: True for action in actions}
            return {
                str(resource["resource_id"]): actions_result for resource in resources
            }

        if len(resources) == 0:
            return {}

        subject = Subject(
            "user", self.request.user.username if self.request else self.username
        )
        actions = [Action(action) for action in actions]
        bk_iam_path = "/project,{}/".format(project_key)
        resources = [
            [
                Resource(
                    settings.BK_IAM_SYSTEM_ID,
                    resource["resource_type"],
                    str(resource["resource_id"]),
                    {
                        "iam_resource_owner": resource.get("creator", ""),
                        "_bk_iam_path_": "/project,{}/".format(
                            resource.get("project_key")
                        )
                        if resource.get("project_key") is not None
                        else bk_iam_path,
                        "name": resource.get("resource_name", ""),
                    },
                )
            ]
            for resource in resources
        ]

        request = MultiActionRequest(
            settings.BK_IAM_SYSTEM_ID, subject, actions, [], None
        )
        try:
            auth_actions = self._iam.batch_resource_multi_actions_allowed(
                request, resources
            )
        except BaseException as error:
            logger.exception(error)
            auth_actions = {}

        return auth_actions

    def resource_multi_actions_allowed(
        self, actions, resources, project_key=DEFAULT_PROJECT_PROJECT_KEY
    ):
        """
        当个资源批量申请的权限
        """

        subject = Subject(
            "user", self.request.user.username if self.request else self.username
        )
        actions = [Action(action) for action in actions]

        bk_iam_path = "/project,{}/".format(project_key)

        resources = [
            Resource(
                settings.BK_IAM_SYSTEM_ID,
                resource["resource_type"],
                str(resource["resource_id"]),
                {
                    "iam_resource_owner": resource.get("creator", ""),
                    "_bk_iam_path_": bk_iam_path
                    if resource["resource_type"] != "project"
                    else "",
                    "name": resource.get("resource_name", ""),
                },
            )
            for resource in resources
        ]

        request = MultiActionRequest(
            settings.BK_IAM_SYSTEM_ID, subject, actions, resources, None
        )
        try:
            auth_actions = self._iam.resource_multi_actions_allowed(request)
        except BaseException as error:
            logger.exception(error)
            auth_actions = {}
        return auth_actions

    def query_by_action(self, action):
        subject = Subject(
            "user", self.request.user.username if self.request else self.username
        )
        request = Request(
            settings.BK_IAM_SYSTEM_ID,
            subject,
            Action(action),
            None,
            None,
        )
        try:
            polices = self._iam._do_policy_query(request)
        except BaseException as error:
            logger.exception(error)
            polices = {}
        return polices


def grant_resource_creator_related_actions(
    resource_type, resource_id, resource_name, creator, bk_token=""
):
    """
    创建实例之后去权限中心授权关联操作
    :param resource_type: 资源类型
    :param resource_id: 资源ID
    :param resource_name: 资源名称
    :param creator: 创建人
    :param bk_token: 用户登录态
    :return:
    """
    iam_client = Client(
        settings.APP_CODE,
        settings.SECRET_KEY,
        settings.BK_IAM_INNER_HOST,
        settings.BK_IAM_ESB_PAAS_HOST,
    )
    if not bk_token:
        try:
            request = get_request()
            bk_token = request.COOKIES.get("bk_token")
        except BaseException:
            pass
    request_data = {
        "system": settings.BK_IAM_SYSTEM_ID,
        "type": resource_type,
        "id": resource_id,
        "name": resource_name,
        "creator": creator,
    }
    logger.info("正在向权限中心主动授权, request_data={}".format(request_data))
    result, message = iam_client.grant_resource_creator_actions(
        bk_token=bk_token, bk_username="admin", data=request_data
    )
    if not result:
        logger.info("权限中心主动授权发生异常, 权限中心报错: {}".format(message))
        logger.error(message)
        raise IamGrantCreatorActionError(message)


def grant_instance_creator_related_actions(
    instance, include_owners=False, delete_instance=True
):
    """
    创建人关联操作权限授权
    :param instance: 资源对象
    :param include_owners: 是否包含负责人
    :param delete_instance: 失败是否删除实例
    :return:
    """

    resource_type = instance.auth_resource["resource_type"]
    if isinstance(instance, TemplateField):
        if instance.project_key == PUBLIC_PROJECT_PROJECT_KEY:
            resource_type = "public_field"

    if instance.creator:
        try:

            if isinstance(instance, Project):
                resource_id = instance.key
            else:
                resource_id = instance.id

            grant_resource_creator_related_actions(
                resource_type=resource_type,
                resource_id=resource_id,
                resource_name=instance.name,
                creator=instance.creator,
            )

        except BaseException as error:
            if delete_instance:
                # 用户手动操作的时候，如果权限注册不成功，需要删除资源对象
                instance.delete()
            raise error

    owners = getattr(instance, "owners", None)
    if not (include_owners and owners):
        return

    for owner in owners.split(","):
        if not owner:
            continue
        try:
            grant_resource_creator_related_actions(
                resource_type=resource_type,
                resource_id=instance.id,
                resource_name=instance.name,
                creator=owner,
            )
        except BaseException as error:
            instance.delete()
            raise error
