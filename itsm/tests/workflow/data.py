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


import os

import django

from itsm.workflow.models import *  # noqa

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

category_parent = {
    "level": 1,
    "key": "zi_kai_fa_ye_wu_lei",
    "name": "自开发业务类",
    "desc": "描述1",
    "parent_key": "",
}

category_child = {
    "level": 2,
    "key": "ban_ben_bian_geng",
    "name": "版本变更",
    "desc": "描述2",
    "parent_key": "zi_kai_fa_ye_wu_lei",
}

change_type = {"key": "normal", "name": "常规", "desc": "常规变更"}

service_property = {
    "change": {"change_type": "test_plat_type"},
    "public": {"service_category": "yi_ji_mu_lu"},
}

workflow = {
    "name": "自研业务类变更流程{}",
    "desc": "自研业务类变更流程描述信息",
    "is_enabled": True,
    "is_draft": True,
    "service": "change",
    "service_property": service_property,
    "is_biz_needed": False,
    "creator": "admin",
}

states = {
    "a": {
        "name": "填写变更",
        "type": "NORMAL",
        "processors_type": "ROLE",
        "processors": "dev",
        "distribute_type": "WAIT",
        "fields": [],
    },
    "b": {
        "name": "开发leader审批",
        "type": "NORMAL",
        "processors_type": "ROLE",
        "processors": "dev_leader",
        "distribute_type": "WAIT",
        "fields": [],
    },
    "c": {
        "name": "测试leader审批",
        "type": "NORMAL",
        "processors_type": "ROLE",
        "processors": "test_leader",
        "distribute_type": "WAIT",
        "fields": [],
    },
    "d": {
        "name": "填写实施计划",
        "type": "NORMAL",
        "processors_type": "ROLE",
        "processors": "ops",
        "distribute_type": "WAIT",
        "fields": [],
    },
    "e": {
        "name": "运维leader审批",
        "type": "NORMAL",
        "processors_type": "ROLE",
        "processors": "ops_leader",
        "distribute_type": "WAIT",
        "fields": [],
    },
    "f": {
        "name": "实施变更",
        "type": "NORMAL",
        "processors_type": "ROLE",
        "processors": "ops",
        "distribute_type": "WAIT",
        "fields": [],
    },
    "g": {
        "name": "验收",
        "type": "NORMAL",
        "processors_type": "ROLE",
        "processors": "dev",
        "distribute_type": "WAIT",
        "fields": [],
    },
}

transitions = {
    "t-start-a": {"direction": "FORWARD", "name": "开始"},
    "t-a-b": {"direction": "FORWARD", "name": "填单确认"},
    "t-b-a": {"direction": "BACK", "name": "驳回"},
    "t-b-c": {"direction": "FORWARD", "name": "通过"},
    "t-c-a": {"direction": "BACK", "name": "驳回"},
    "t-c-d": {"direction": "FORWARD", "name": "通过"},
    "t-d-e": {"direction": "FORWARD", "name": "填单确认"},
    "t-e-d": {"direction": "BACK", "name": "驳回"},
    "t-e-f": {"direction": "FORWARD", "name": "实施确认"},
    "t-f-g": {"direction": "FORWARD", "name": "验收确认"},
    "t-g-end": {"direction": "FORWARD", "name": "验收确认"},
}

fields = {
    "suo_shu_ye_wu": {
        "is_builtin": True,
        "type": "STRING",
        "key": "suo_shu_ye_wu",
        "name": "所属业务",
        "layout": "COL_6",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
    "bian_geng_lei_xing": {
        "is_builtin": True,
        "type": "CHECKBOX",
        "key": "bian_geng_lei_xing",
        "name": "变更类型",
        "layout": "COL_6",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
    "bian_geng_ye_wu_mo_kuai": {
        "is_builtin": False,
        "type": "STRING",
        "key": "bian_geng_ye_wu_mo_kuai",
        "name": "变更业务模块",
        "layout": "COL_6",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
    "biang_geng_mu_di": {
        "is_builtin": False,
        "type": "TEXT",
        "key": "biang_geng_mu_di",
        "name": "变更目的",
        "layout": "COL_6",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
    "biang_geng_cao_zuo_ren": {
        "is_builtin": False,
        "type": "MEMBERS",
        "key": "biang_geng_cao_zuo_ren",
        "name": "变更操作人",
        "layout": "COL_6",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
    "ji_hua_bian_geng_shi_jian": {
        "is_builtin": False,
        "type": "DATETIME",
        "key": "ji_hua_bian_geng_shi_jian",
        "name": "计划变更时间",
        "layout": "COL_6",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
    "bian_geng_nei_rong": {
        "is_builtin": False,
        "type": "TEXT",
        "key": "bian_geng_nei_rong",
        "name": "变更内容",
        "layout": "COL_6",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
    "shi_fou_zhi_chi_hui_du": {
        "is_builtin": False,
        "type": "RADIO",
        "key": "shi_fou_zhi_chi_hui_du",
        "name": "是否支持灰度",
        "layout": "COL_6",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "shi",
        "choice": {"shi": "是", "fou": "否"},
    },
    "bian_geng_fang_an": {
        "is_builtin": False,
        "type": "TEXT",
        "key": "bian_geng_fang_an",
        "name": "变更风险",
        "layout": "COL_6",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
    "yan_zheng_fang_an": {
        "is_builtin": False,
        "type": "TEXT",
        "key": "yan_zheng_fang_an",
        "name": "验证方案",
        "layout": "COL_6",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
    "guan_zhu_ren": {
        "is_builtin": False,
        "type": "MEMBERS",
        "key": "guan_zhu_ren",
        "name": "关注人",
        "layout": "COL_6",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
    "shi_fou_wan_cheng_review_jiao_yan": {
        "is_builtin": False,
        "type": "RADIO",
        "key": "shi_fou_wan_cheng_review_jiao_yan",
        "name": "是否完成review校验",
        "layout": "COL_6",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "shi",
        "choice": {"shi": "是", "fou": "否"},
    },
    "shen_pi_yi_jian": {
        "is_builtin": False,
        "type": "TEXT",
        "key": "shen_pi_yi_jian",
        "name": "审批意见",
        "layout": "COL_12",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
    "bei_zhu": {
        "is_builtin": False,
        "type": "TEXT",
        "key": "bei_zhu",
        "name": "备注",
        "layout": "COL_12",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
    "shen_pi_yi_jian_1": {
        "is_builtin": False,
        "type": "TEXT",
        "key": "shen_pi_yi_jian_1",
        "name": "审批意见",
        "layout": "COL_12",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
    "bei_zhu_2": {
        "is_builtin": False,
        "type": "TEXT",
        "key": "bei_zhu_2",
        "name": "备注",
        "layout": "COL_12",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
    "cao_zuo_bu_zhou": {
        "is_builtin": False,
        "type": "TEXT",
        "key": "cao_zuo_bu_zhou",
        "name": "操作步骤",
        "layout": "COL_12",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
    "hui_gun_fang_an": {
        "is_builtin": False,
        "type": "TEXT",
        "key": "hui_gun_fang_an",
        "name": "回滚方案",
        "layout": "COL_12",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
    "shen_pi_yi_jian_2": {
        "is_builtin": False,
        "type": "TEXT",
        "key": "shen_pi_yi_jian_2",
        "name": "审批意见",
        "layout": "COL_12",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
    "bei_zhu_3": {
        "is_builtin": False,
        "type": "TEXT",
        "key": "bei_zhu_3",
        "name": "备注",
        "layout": "COL_12",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
    "shi_shi_jie_guo": {
        "is_builtin": False,
        "type": "TEXT",
        "key": "shi_shi_jie_guo",
        "name": "实施结果",
        "layout": "COL_12",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
    "yan_shou_jie_guo": {
        "is_builtin": False,
        "type": "TEXT",
        "key": "yan_shou_jie_guo",
        "name": "验收结果",
        "layout": "COL_12",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
    "shi_fou_zhi_xing_hui_gun_fang_an": {
        "is_builtin": False,
        "type": "RADIO",
        "key": "shi_fou_zhi_xing_hui_gun_fang_an",
        "name": "是否执行回滚方案",
        "layout": "COL_6",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "fou",
        "choice": {"shi": "是", "fou": "否"},
    },
    "yi_chang_jie_guo_shuo_ming": {
        "is_builtin": False,
        "type": "TEXT",
        "key": "yi_chang_jie_guo_shuo_ming",
        "name": "异常结果说明",
        "layout": "COL_6",
        "desc": "",
        "validate_type": "OPTION",
        "regex": "",
        "default": "",
        "choice": {},
    },
}


def init_workflow_data():
    State._objects.all().delete()
    Transition._objects.all().delete()
    Workflow._objects.all().delete()
    Field._objects.all().delete()
    Notify.objects.all().delete()

    obj = Workflow.objects.create_workflow(workflow)
    obj_map = State.objects.create_states(obj.id, states)
    Transition.objects.create_transitions(obj.id, transitions, obj_map)
    Field.objects.create_fields(obj.id, fields)

    import random

    for id, state in obj_map.items():
        state_obj = State.objects.get(id=state)
        state_obj.fields = Field.objects.filter(
            id__lte=random.randint(1, 6)
        ).values_list("id", flat=True)
        state_obj.save()


if __name__ == "__main__":
    init_workflow_data()
