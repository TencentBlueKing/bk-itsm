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

from itsm.component.constants import EMPTY_INT
from .models import Trigger, TriggerRule, ActionSchema


def import_trigger(src_trigger_ids, dst_source_type, dst_source_id, dst_sender=None, **kwargs):
    """
    批量引用触发器
    :param src_trigger_ids: 引用的触发器id
    :param dst_source_type: 引用至的模块类型
    :param dst_source_id: 引用至的模块id
    :param dst_sender: 信号发送者
    :param kwargs: 覆盖引用的触发器属性
    :return:
    """
    original_triggers = Trigger.objects.filter(id__in=src_trigger_ids)
    new_trigger_ids = []
    for trigger in original_triggers:
        old_trigger_id = trigger.id
        new_trigger_id = trigger.clone(dst_source_type, dst_source_id, dst_sender, **kwargs)
        original_rules = list(TriggerRule.objects.filter(trigger_id=old_trigger_id))
        for original_rule in original_rules:
            original_rule.id = None
            original_rule.trigger_id = new_trigger_id
            new_action_schema_ids = []
            for action_schema in original_rule.actions:
                new_action_schema_ids.append(action_schema.clone())
            original_rule.action_schemas = new_action_schema_ids
            original_rule.save()
        new_trigger_ids.append(new_trigger_id)
    return new_trigger_ids


def copy_triggers_by_source(src_source_type, src_source_id, dst_source_type, dst_source_id):
    """
    批量通过源进行触发器的更新
    :param src_source_type: 原类型
    :param src_source_id: 原id
    :param dst_source_type: 目标类型
    :param dst_source_id: 目标id
    :return: 新的触发器列表
    """
    src_trigger_ids = Trigger.objects.filter(source_type=src_source_type, source_id=src_source_id).values_list(
        "id", flat=True
    )
    return import_trigger(src_trigger_ids, dst_source_type, dst_source_id)


def restore_trigger_data(triggers, source_type, source_id, operator="", sender_map=None):
    """
    存储导入的数据
    """
    if sender_map is None:
        sender_map = {}
    new_rules = []
    for trigger in triggers:
        rules = trigger.pop("rules", [])
        trigger.update(
            id=None,
            creator=operator,
            updated_by=operator,
            source_id=source_id,
            source_type=source_type,
            source_table_id=EMPTY_INT,
        )
        new_trigger = Trigger.objects.create(**trigger)
        if new_trigger.signal_type in sender_map:
            # 需要对sender进行更新
            new_trigger.sender = sender_map[new_trigger.signal_type].get(new_trigger.sender, new_trigger.sender)
            new_trigger.save()

        for rule in rules:
            new_action_schema_ids = restore_action_schemas(rule.pop("action_schemas", []), operator)
            rule.update(trigger_id=new_trigger.id, action_schemas=new_action_schema_ids)
            new_rules.append(TriggerRule(**rule))
    # 触发规则可以批量保存
    TriggerRule.objects.bulk_create(new_rules)


def restore_action_schemas(action_schemas, operator=""):
    """
    保存导入的响应事件信息
    """
    new_action_schemas = []
    for action_schema in action_schemas:
        action_schema.update(id=None, creator=operator, updated_by=operator)
        new_action_schemas.append(ActionSchema.objects.create(**action_schema).id)
    return new_action_schemas
