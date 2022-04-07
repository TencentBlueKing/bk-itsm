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

from settings import BK_IAM_SYSTEM_ID

BK_IAM_SYSTEM_ID = BK_IAM_SYSTEM_ID
ACTIONS = [
    {
        "id": "project_create",
        "name": "创建项目",
        "relate_resources": [],
        "relate_actions": [],
        "resource_topo": ["project"],
    },
    {
        "id": "project_view",
        "name": "项目查看",
        "relate_resources": ["project"],
        "relate_actions": [],
        "resource_topo": ["project"],
    },
    {
        "id": "project_edit",
        "name": "项目编辑",
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project"],
    },
    {
        "id": "workflow_create",
        "name": "流程创建",
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "workflow"],
    },
    {
        "id": "workflow_manage",
        "name": "流程管理",
        "relate_resources": ["workflow"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "workflow"],
    },
    {
        "id": "workflow_deploy",
        "name": "流程部署",
        "relate_resources": ["workflow"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "workflow"],
    },
    {
        "id": "service_create",
        "name": "服务创建",
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "service"],
    },
    {
        "id": "service_view",
        "name": "服务查看",
        "relate_resources": ["service"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "service"],
    },
    {
        "id": "service_manage",
        "name": "服务管理",
        "relate_resources": ["service"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "service"],
    },
    {
        "id": "flow_version_restore",
        "name": "流程版本还原",
        "relate_resources": ["flow_version"],
        "relate_actions": ["project_view", "workflow_create"],
        "resource_topo": ["project", "flow_version"],
    },
    {
        "id": "flow_version_manage",
        "name": "流程版本管理",
        "relate_resources": ["flow_version"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "flow_version"],
    },
    {
        "id": "role_create",
        "name": "角色创建",
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "role"],
    },
    {
        "id": "role_manage",
        "name": "角色管理",
        "relate_resources": ["role"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "role"],
    },
    {
        "id": "sla_manage",
        "name": "服务协议管理",
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "sla"],
    },
    {
        "id": "flow_element_manage",
        "name": "流程元素管理",
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "flow_element"],
    },
    {
        "id": "system_settings_manage",
        "name": "系统配置管理",
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "system_settings"],
    },
    {
        "id": "ticket_view",
        "name": "工单查看",
        "relate_resources": ["service"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "service"],
    },
    {
        "id": "ticket_management",
        "name": "工单管理",
        "relate_resources": ["service"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "service"],
    },
    {
        "id": "operational_data_view",
        "name": "运营数据查看",
        "relate_resources": [],
        "relate_actions": [],
        "resource_topo": [],
    },
    {
        "id": "field_create",
        "name": "字段新建",
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "field"],
    },
    {
        "id": "field_view",
        "name": "字段查看",
        "relate_resources": ["field"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "field"],
    },
    {
        "id": "field_edit",
        "name": "字段编辑",
        "relate_resources": ["field"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "field"],
    },
    {
        "id": "field_delete",
        "name": "字段删除",
        "relate_resources": ["field"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "field"],
    },
    {
        "id": "triggers_create",
        "name": "触发器新建",
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "trigger"],
    },
    {
        "id": "triggers_view",
        "name": "触发器查看",
        "relate_resources": ["trigger"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "trigger"],
    },
    {
        "id": "triggers_edit",
        "name": "触发器编辑",
        "relate_resources": ["trigger"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "trigger"],
    },
    {
        "id": "triggers_manage",
        "name": "触发器管理",
        "relate_resources": ["trigger"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "trigger"],
    },
    {
        "id": "settings_view",
        "name": "设置查看",
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project"],
    },
    {
        "id": "settings_manage",
        "name": "设置管理",
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project"],
    },
    {
        "id": "catalog_create",
        "name": "目录新建",
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project"],
    },
    {
        "id": "catalog_edit",
        "name": "目录编辑",
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project"],
    },
    {
        "id": "catalog_delete",
        "name": "目录删除",
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project"],
    },
    {
        "id": "user_group_create",
        "name": "用户组新建",
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "user_group"],
    },
    {
        "id": "user_group_create",
        "name": "用户组新建",
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "user_group"],
    },
    {
        "id": "user_group_view",
        "name": "用户组查看",
        "relate_resources": ["user_group"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "user_group"],
    },
    {
        "id": "user_group_edit",
        "name": "用户组编辑",
        "relate_resources": ["user_group"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "user_group"],
    },
    {
        "id": "user_group_delete",
        "name": "用户组删除",
        "relate_resources": ["user_group"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "user_group"],
    },
    {
        "id": "sla_calendar_view",
        "name": "SLA 服务模式查看",
        "relate_resources": ["sla_calendar"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "sla_calendar"],
    },
    {
        "id": "sla_calendar_edit",
        "name": "SLA 服务模式编辑",
        "relate_resources": ["sla_calendar"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "sla_calendar"],
    },
    {
        "id": "sla_calendar_delete",
        "name": "SLA 服务模式删除",
        "relate_resources": ["sla_calendar"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "sla_calendar"],
    },
    {
        "id": "sla_calendar_create",
        "name": "SLA 服务模式新建",
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "sla_calendar"],
    },
    {
        "id": "sla_agreement_view",
        "name": "SLA 服务协议查看",
        "relate_resources": ["sla_agreement"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "sla_agreement"],
    },
    {
        "id": "sla_agreement_create",
        "name": "SLA 服务协议创建",
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "sla_agreement"],
    },
    {
        "id": "sla_agreement_edit",
        "name": "SLA 服务协议编辑",
        "relate_resources": ["sla_agreement"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "sla_agreement"],
    },
    {
        "id": "sla_agreement_delete",
        "name": "SLA 服务协议删除",
        "relate_resources": ["sla_agreement"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "sla_agreement"],
    },
    {
        "id": "sla_priority_view",
        "name": "SLA 优先级查看",
        "relate_resources": [],
        "relate_actions": [],
        "resource_topo": [],
    },
    {
        "id": "sla_priority_manage",
        "name": "SLA 优先级管理",
        "relate_resources": [],
        "relate_actions": [],
        "resource_topo": [],
    },
    {
        "id": "public_field_create",
        "name": "公共字段新建",
        "relate_resources": [],
        "relate_actions": [],
        "resource_topo": ["public_field"],
    },
    {
        "id": "public_field_edit",
        "name": "公共字段编辑",
        "relate_resources": ["public_field"],
        "relate_actions": ["public_field_view"],
        "resource_topo": ["public_field"],
    },
    {
        "id": "public_field_delete",
        "name": "公共字段删除",
        "relate_resources": ["public_field"],
        "relate_actions": ["public_field_view"],
        "resource_topo": ["public_field"],
    },
    {
        "id": "public_field_view",
        "name": "公共字段查看",
        "relate_resources": ["public_field"],
        "relate_actions": [],
        "resource_topo": ["public_field"],
    },
    {
        "id": "public_api_create",
        "name": "公共API新建",
        "relate_resources": [],
        "relate_actions": [],
        "resource_topo": ["public_api"],
    },
    {
        "id": "public_api_view",
        "name": "公共API查看",
        "relate_resources": ["public_api"],
        "relate_actions": [],
        "resource_topo": ["public_api"],
    },
    {
        "id": "public_api_manage",
        "name": "公共API管理",
        "relate_resources": ["public_api"],
        "relate_actions": ["public_api_view"],
        "resource_topo": ["public_api"],
    },
    {
        "id": "task_template_view",
        "name": "任务模版查看",
        "relate_resources": ["task_template"],
        "relate_actions": [],
        "resource_topo": ["task_template"],
    },
    {
        "id": "task_template_create",
        "name": "任务模版创建",
        "relate_resources": [],
        "relate_actions": [],
        "resource_topo": [],
    },
    {
        "id": "task_template_manage",
        "name": "任务模版管理",
        "relate_resources": ["task_template"],
        "relate_actions": ["task_template_view"],
        "resource_topo": ["task_template"],
    },
    {
        "id": "notification_view",
        "name": "通知配置查看",
        "relate_resources": [],
        "relate_actions": [],
        "resource_topo": [],
    },
    {
        "id": "notification_manage",
        "name": "通知配置管理",
        "relate_resources": [],
        "relate_actions": [],
        "resource_topo": [],
    },
    {
        "id": "global_settings_view",
        "name": "全局设置查看",
        "relate_resources": [],
        "relate_actions": [],
        "resource_topo": [],
    },
    {
        "id": "global_settings_manage",
        "name": "全局设置管理",
        "relate_resources": [],
        "relate_actions": [],
        "resource_topo": [],
    },
    {
        "id": "ticket_state_view",
        "name": "单据状态查看",
        "relate_resources": [],
        "relate_actions": [],
        "resource_topo": [],
    },
    {
        "id": "ticket_state_manage",
        "name": "单据状态管理",
        "relate_resources": [],
        "relate_actions": [],
        "resource_topo": [],
    },
    {
        "id": "platform_manage_access",
        "name": "平台管理访问",
        "relate_resources": [],
        "relate_actions": [],
        "resource_topo": [],
    },
]

RESOURCES = [
    # 当前默认一个项目，所有的操作都在默认项目下操作
    {"id": "project", "name": "项目", "parent_id": None},
    # 服务，对应服务管理
    {"id": "service", "name": "服务", "parent_id": "project"},
    # 对应流程设计
    {"id": "workflow", "name": "流程", "parent_id": "project"},
    # 对应部署的流程版本的预览和还原
    {"id": "flow_version", "name": "流程版本", "parent_id": None},
    # 对应API配置，公共字段，基础模型，触发器，任务组，单据状态管理
    {"id": "flow_element", "name": "流程元素", "parent_id": None},
    # 对应角色管理
    {"id": "role", "name": "通用角色", "parent_id": None},
    # 对应工单管理
    {"id": "ticket", "name": "工单", "parent_id": "project"},
    # 对应服务模式，服务协议管理，优先级管理
    {"id": "sla", "name": "服务协议", "parent_id": None},
    # 对应服务目录， 基础配置，角色表管理
    {"id": "system_settings", "name": "系统配置", "parent_id": None},
    # 对应服务目录， 基础配置，角色表管理
    {"id": "operational_data", "name": "运营数据", "parent_id": None},
    # 对应服务目录管理
    {"id": "catalog", "name": "服务目录", "parent_id": "project"},
    # 对应项目下的用户组管理
    {"id": "user_group", "name": "用户组", "parent_id": "project"},
    # 对应项目下的字段管理
    {"id": "field", "name": "字段", "parent_id": "project"},
    # 对应项目下的触发器管理
    {"id": "trigger", "name": "触发器", "parent_id": "project"},
    # 对应项目下的服务协议管理
    {"id": "sla_agreement", "name": "SLA 服务协议", "parent_id": "project"},
    # 对应项目下的服务模式管理
    {"id": "sla_calendar", "name": "SLA 服务模式", "parent_id": "project"},
    # 对应公共字段
    {"id": "public_field", "name": "公共字段", "parent_id": None},
    # 对应公共API
    {"id": "public_api", "name": "公共API", "parent_id": None},
    # 对应服务类型
    {"id": "service_type", "name": "服务类型", "parent_id": None},
    # 对应服务类型
    {"id": "task_template", "name": "任务模版", "parent_id": None},
]

BK_IAM_SYSTEM_NAME = "流程服务"

HTTP_499_IAM_FORBIDDEN = 499

# 当前的项目，默认只有一个
PROJECT_INFO = {
    "resource_id": "0",
    "resource_name": "默认项目",
    "resource_type": "project",
    "resource_type_name": "项目",
}

PLATFORM_PERMISSION = [
    "project_create",
    "notification_view",
    "notification_manage",
    "global_settings_view",
    "global_settings_manage",
    "knowledge_manage",
    "operational_data_view",
    "settings_view",
    "settings_manage",
    "task_template_create",
    "public_api_create",
    "public_field_create",
    "sla_priority_view",
    "sla_priority_manage",
    "ticket_state_view",
    "ticket_state_manage",
    "platform_manage_access",
]

IAM_SEARCH_INSTANCE_CACHE_TIME = 10 * 60  # 缓存5分钟
