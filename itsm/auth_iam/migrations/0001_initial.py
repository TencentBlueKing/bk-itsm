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


from django.db import migrations


def migrate_history_permission_data(apps, schema_editor):
    """
    迁移2.4版本的数据历史权限数据
    """

    from itsm.workflow.models import Workflow, WorkflowVersion
    from itsm.service.models import Service
    from itsm.role.models import UserRole
    from itsm.iadmin.models import ReleaseVersionLog

    from itsm.auth_iam.utils import grant_instance_creator_related_actions, grant_resource_creator_related_actions

    project_view_users = []
    try:
        latest_version = ReleaseVersionLog.objects.get(is_latest=True, lang="zh-cn")
    except ReleaseVersionLog.DoesNotExist:
        print("no release log")
        return

    if latest_version.version >= "2.5.4":
        print("the latest version %s is greater than 2.5.4" % latest_version.version)
        return

    for flow in Workflow.objects.all():
        try:
            grant_instance_creator_related_actions(flow, include_owners=True, delete_instance=False)
            project_view_users.append(flow.creator)
            project_view_users.extend(flow.owners.split(","))
        except BaseException as error:
            print("init workflow %s's project permission error: %s" % (flow.name, str(error)))
            continue

    for flow_version in WorkflowVersion.objects.all():
        try:
            grant_instance_creator_related_actions(flow_version, include_owners=True, delete_instance=False)
            project_view_users.append(flow_version.creator)
            project_view_users.extend(flow_version.owners.split(","))
        except BaseException as error:
            print("init version %s's  permission error: %s" % (flow_version.name, str(error)))
            continue

    for service_instance in Service.objects.all():
        try:
            grant_instance_creator_related_actions(service_instance, include_owners=True, delete_instance=False)
            project_view_users.append(service_instance.creator)
            project_view_users.extend(service_instance.owners.split(","))
        except BaseException as error:
            print("init service  %s's  permission error: %s" % (service_instance.name, str(error)))
            continue

    for role_instance in UserRole.objects.filter(role_type="GENERAL"):
        try:
            grant_instance_creator_related_actions(role_instance, include_owners=True, delete_instance=False)
            project_view_users.append(role_instance.creator)
            project_view_users.extend(role_instance.owners.split(","))
        except BaseException as error:
            print("init role %s's  permission error: %s" % (role_instance.name, str(error)))
            continue

    for username in set(project_view_users):
        if not username:
            continue

        try:
            grant_resource_creator_related_actions(
                resource_type='project', resource_id=0, resource_name='默认项目', creator=username
            )
        except BaseException as error:
            print("init %s's project permission error: %s" % (username, str(error)))


class Migration(migrations.Migration):
    dependencies = [
        ('iam_migration', '0003_update'),
        ('iadmin', '0011_auto_20200510_1038'),
        ('workflow', '0033_auto_20200714_1037'),
        ('service', '0018_auto_20200502_1535'),
        ('role', '0010_auto_20200502_1535'),
    ]

    operations = [migrations.RunPython(migrate_history_permission_data)]
