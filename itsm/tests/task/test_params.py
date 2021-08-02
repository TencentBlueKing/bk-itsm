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

sops_create_res = {
    'message': '',
    'code': 0,
    'data': {
        'pipeline_tree': {
            'activities': {
                'n144ad529f86379f92aadc76a5b003c9': {
                    'outgoing': 'l4e520dfadd8393bbb5787705f460454',
                    'incoming': ['l2f19fbf12603e00984cb52e4b66d5c4'],
                    'name': '定时',
                    'error_ignorable': False,
                    'labels': [],
                    'component': {
                        'code': 'sleep_timer',
                        'data': {
                            'force_check': {'hook': False, 'value': True},
                            'bk_timing': {'hook': True, 'value': '${bk_timing}'},
                        },
                        'version': 'legacy',
                    },
                    'stage_name': '步骤1',
                    'skippable': True,
                    'type': 'ServiceActivity',
                    'retryable': True,
                    'optional': False,
                    'id': 'n144ad529f86379f92aadc76a5b003c9',
                    'loop': None,
                },
                'na5d869e262d3d25ae3a35d463f529ce': {
                    'outgoing': 'l2cc2762848939b7b022909a14f12d9c',
                    'incoming': ['l4e520dfadd8393bbb5787705f460454'],
                    'name': '定时',
                    'error_ignorable': False,
                    'labels': [],
                    'component': {
                        'code': 'sleep_timer',
                        'data': {
                            'force_check': {'hook': False, 'value': True},
                            'bk_timing': {'hook': True, 'value': '${bk_timing}'},
                        },
                        'version': 'legacy',
                    },
                    'stage_name': '步骤1',
                    'skippable': True,
                    'type': 'ServiceActivity',
                    'retryable': True,
                    'optional': False,
                    'id': 'na5d869e262d3d25ae3a35d463f529ce',
                    'loop': None,
                },
            },
            'end_event': {
                'outgoing': '',
                'incoming': ['l2cc2762848939b7b022909a14f12d9c'],
                'name': '',
                'labels': [],
                'type': 'EmptyEndEvent',
                'id': 'nf6557d90c5734b6b5582cc3c62c08af',
            },
            'outputs': [],
            'flows': {
                'l2f19fbf12603e00984cb52e4b66d5c4': {
                    'is_default': False,
                    'source': 'nfa14f726c403a47ba866602a1bad2e2',
                    'id': 'l2f19fbf12603e00984cb52e4b66d5c4',
                    'target': 'n144ad529f86379f92aadc76a5b003c9',
                },
                'l2cc2762848939b7b022909a14f12d9c': {
                    'is_default': False,
                    'source': 'na5d869e262d3d25ae3a35d463f529ce',
                    'id': 'l2cc2762848939b7b022909a14f12d9c',
                    'target': 'nf6557d90c5734b6b5582cc3c62c08af',
                },
                'l4e520dfadd8393bbb5787705f460454': {
                    'is_default': False,
                    'source': 'n144ad529f86379f92aadc76a5b003c9',
                    'id': 'l4e520dfadd8393bbb5787705f460454',
                    'target': 'na5d869e262d3d25ae3a35d463f529ce',
                },
            },
            'id': 'n5ebed4d8fc93af5a7211da2998afa78',
            'gateways': {},
            'line': [
                {
                    'source': {'id': 'nfa14f726c403a47ba866602a1bad2e2', 'arrow': 'Right'},
                    'id': 'l2f19fbf12603e00984cb52e4b66d5c4',
                    'target': {'id': 'n144ad529f86379f92aadc76a5b003c9', 'arrow': 'Left'},
                },
                {
                    'source': {'id': 'n144ad529f86379f92aadc76a5b003c9', 'arrow': 'Right'},
                    'target': {'id': 'na5d869e262d3d25ae3a35d463f529ce', 'arrow': 'Left'},
                    'id': 'l4e520dfadd8393bbb5787705f460454',
                },
                {
                    'source': {'id': 'na5d869e262d3d25ae3a35d463f529ce', 'arrow': 'Right'},
                    'target': {'id': 'nf6557d90c5734b6b5582cc3c62c08af', 'arrow': 'Left'},
                    'id': 'l2cc2762848939b7b022909a14f12d9c',
                },
            ],
            'start_event': {
                'outgoing': 'l2f19fbf12603e00984cb52e4b66d5c4',
                'incoming': '',
                'name': '',
                'labels': [],
                'type': 'EmptyStartEvent',
                'id': 'nfa14f726c403a47ba866602a1bad2e2',
            },
            'constants': {
                '_result': {
                    'source_tag': '',
                    'source_info': {'na5d869e262d3d25ae3a35d463f529ce': ['_result']},
                    'name': '执行结果123',
                    'custom_type': '',
                    'index': 1,
                    'value': '',
                    'show_type': 'hide',
                    'source_type': 'component_outputs',
                    'version': 'legacy',
                    'key': '_result',
                    'validation': '',
                    'desc': '',
                },
                '_loop': {
                    'source_tag': '',
                    'source_info': {'na5d869e262d3d25ae3a35d463f529ce': ['_loop']},
                    'name': '循环次数213',
                    'custom_type': '',
                    'index': 2,
                    'value': '',
                    'show_type': 'hide',
                    'source_type': 'component_outputs',
                    'version': 'legacy',
                    'key': '_loop',
                    'validation': '',
                    'desc': '',
                },
                '${bk_timing}': {
                    'source_tag': 'sleep_timer.bk_timing',
                    'source_info': {
                        'n144ad529f86379f92aadc76a5b003c9': ['bk_timing'],
                        'na5d869e262d3d25ae3a35d463f529ce': ['bk_timing'],
                    },
                    'name': '定时时间',
                    'custom_type': '',
                    'index': 0,
                    'value': '3',
                    'show_type': 'show',
                    'source_type': 'component_inputs',
                    'formSchema': {
                        'type': 'input',
                        'attrs': {
                            'hookable': True,
                            'validation': [{'type': 'required'}, {'type': 'custom'}],
                            'placeholder': '秒(s) 或 时间(%Y-%m-%d %H:%M:%S)',
                            'name': '定时时间',
                        },
                    },
                    'version': 'legacy',
                    'key': '${bk_timing}',
                    'validation': '',
                    'desc': '',
                },
                '${_loop_4413}': {
                    'source_tag': '',
                    'source_info': {'n144ad529f86379f92aadc76a5b003c9': ['_loop']},
                    'name': '循环次数',
                    'custom_type': '',
                    'index': 6,
                    'value': '',
                    'show_type': 'hide',
                    'source_type': 'component_outputs',
                    'version': 'legacy',
                    'key': '${_loop_4413}',
                    'validation': '',
                    'desc': '',
                },
                '_loop_test': {
                    'source_tag': '',
                    'source_info': {'na5d869e262d3d25ae3a35d463f529ce': ['_loop_test']},
                    'name': '循环次数',
                    'custom_type': '',
                    'index': 7,
                    'value': '',
                    'show_type': 'hide',
                    'source_type': 'component_outputs',
                    'version': 'legacy',
                    'key': '_loop_test',
                    'validation': '',
                    'desc': '',
                },
                '_loop111': {
                    'source_tag': '',
                    'source_info': {'na5d869e262d3d25ae3a35d463f529ce': ['_loop111']},
                    'name': '循环次数',
                    'custom_type': '',
                    'index': 4,
                    'value': '',
                    'show_type': 'hide',
                    'source_type': 'component_outputs',
                    'version': 'legacy',
                    'key': '_loop111',
                    'validation': '',
                    'desc': '',
                },
                '${_result_dd0f}': {
                    'source_tag': '',
                    'source_info': {'n144ad529f86379f92aadc76a5b003c9': ['_result']},
                    'name': '执行结果',
                    'custom_type': '',
                    'index': 5,
                    'value': '',
                    'show_type': 'hide',
                    'source_type': 'component_outputs',
                    'version': 'legacy',
                    'key': '${_result_dd0f}',
                    'validation': '',
                    'desc': '',
                },
                '${_loopaaaa}': {
                    'source_tag': '',
                    'source_info': {'na5d869e262d3d25ae3a35d463f529ce': ['_loop']},
                    'name': '循环次数213',
                    'custom_type': '',
                    'index': 9,
                    'value': '',
                    'show_type': 'hide',
                    'source_type': 'component_outputs',
                    'version': 'legacy',
                    'key': '${_loopaaaa}',
                    'validation': '',
                    'desc': '',
                },
                '_loop000': {
                    'source_tag': '',
                    'source_info': {'na5d869e262d3d25ae3a35d463f529ce': ['_loop000']},
                    'name': '循环次数',
                    'custom_type': '',
                    'index': 3,
                    'value': '',
                    'show_type': 'hide',
                    'source_type': 'component_outputs',
                    'version': 'legacy',
                    'key': '_loop000',
                    'validation': '',
                    'desc': '',
                },
                '_loopcccc': {
                    'source_tag': '',
                    'source_info': {'na5d869e262d3d25ae3a35d463f529ce': ['_loop']},
                    'name': '循环次数',
                    'custom_type': '',
                    'index': 8,
                    'value': '',
                    'show_type': 'hide',
                    'source_type': 'component_outputs',
                    'version': 'legacy',
                    'key': '_loopcccc',
                    'validation': '',
                    'desc': '',
                },
            },
            'location': [
                {'y': 150, 'x': 20, 'type': 'startpoint', 'id': 'nfa14f726c403a47ba866602a1bad2e2'},
                {
                    'stage_name': '步骤1',
                    'group': '蓝鲸服务(BK)',
                    'name': '定时',
                    'y': 145,
                    'x': 240,
                    'type': 'tasknode',
                    'id': 'n144ad529f86379f92aadc76a5b003c9',
                    'icon': '',
                },
                {'y': 175, 'x': 800, 'type': 'endpoint', 'id': 'nf6557d90c5734b6b5582cc3c62c08af'},
                {
                    'stage_name': '步骤1',
                    'group': '蓝鲸服务(BK)',
                    'name': '定时',
                    'y': 155,
                    'x': 555,
                    'type': 'tasknode',
                    'id': 'na5d869e262d3d25ae3a35d463f529ce',
                    'icon': '',
                },
            ],
        },
        'task_url': 'https://xxx.com:443/o/bk_sops/taskflow/execute/1/?instance_id=28238',
        'task_id': 28238,
    },
    'result': True,
    'request_id': 'a7af1a60b16a44ca97e09ab208687c80',
}

task_params = {
    'bk_biz_id': 2,
    'operator': 'admin',
    'username': 'admin',
    'template_id': 296,
    'name': 'test_task',
    'flow_type': 'common',
    'template_source': 'business',
    'constants': {'${bk_timing}': '3'},
    'exclude_task_nodes_id': [],
}


create_ticket_data = {
    "catalog_id": 3,
    "service_id": 1,
    "service_type": "request",
    "fields": [
        {"type": "STRING", "id": 1, "key": "title", "value": "test_ticket", "choice": []},
        {
            "type": "STRING",
            "id": 5,
            "key": "apply_content",
            "value": "测试内容",
        },
        {
            "type": "STRING",
            "key": "ZHIDINGSHENPIREN",
            "value": "test",
        },
        {
            "type": "STRING",
            "key": "apply_reason",
            "value": "test",
        },
    ],
    "creator": "admin",
    "attention": True,
}

create_sops_task_data = {
    "processors": "hoganren1",
    "processors_type": "PERSON",
    "fields": {
        "task_name": "test_task",
        "sops_templates": {
            "id": 296,
            "template_source": "business",
            "bk_biz_id": 2,
            "constants": [
                {
                    "source_tag": "sleep_timer.bk_timing",
                    "source_info": {
                        "nodec1990a959e07f24be496d68af3a4": ["bk_timing"],
                        "node2cb27e5bd218083ff741b90500cc": ["bk_timing"],
                    },
                    "name": "定时时间",
                    "custom_type": "",
                    "index": 0,
                    "schema": {
                        "enum": [],
                        "type": "string",
                        "description": "定时时间，格式为秒(s) 或 (%%Y-%%m-%%d %%H:%%M:%%S)",
                    },
                    "value": "3",
                    "show_type": "show",
                    "source_type": "component_inputs",
                    "formSchema": {
                        "type": "input",
                        "attrs": {
                            "hookable": True,
                            "validation": [{"type": "required"}, {"type": "custom"}],
                            "placeholder": "秒(s) 或 时间(%Y-%m-%d %H:%M:%S)",
                            "name": "定时时间",
                        },
                    },
                    "version": "legacy",
                    "key": "${bk_timing}",
                    "validation": "",
                    "desc": "",
                }
            ],
        },
    },
    "ticket_id": 1,
    "task_schema_id": 1,
    "need_start": True,
    "source": "template",
    "exclude_task_nodes_id": [],
}
