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

# 工作流测试数据

PIPELINE_DATA = {
    'activities': {
        '66e5fc0ada053fd8a9951fb8baec68c1': {
            'component': {'code': 'pipe_example_component', 'inputs': {}},
            'error_ignorable': False,
            'id': '66e5fc0ada053fd8a9951fb8baec68c1',
            'incoming': ['50798ac5a9163d80a26df622a3a2c206'],
            'name': 'shenpi',
            'optional': False,
            'outgoing': '107c380cbcfe3fa9abea3ae993a584d2',
            'type': 'ServiceActivity',
        },
        '6e1b3c8bdfdf33a891a80ea847693784': {
            'component': {'code': 'pipe_example_component', 'inputs': {}},
            'error_ignorable': False,
            'id': '6e1b3c8bdfdf33a891a80ea847693784',
            'incoming': ['701040fef2953c1793c65d9d32c3a730'],
            'name': 'xiaojia',
            'optional': False,
            'outgoing': 'c1d896443ddb3ec9bcd8105aa21e86eb',
            'type': 'ServiceActivity',
        },
        '997a6b68bfe933ab9a46890b6ee56e53': {
            'component': {'code': 'pipe_example_component', 'inputs': {}},
            'error_ignorable': False,
            'id': '997a6b68bfe933ab9a46890b6ee56e53',
            'incoming': ['de49748f24c731efb06bae78565ca945'],
            'name': 'tidan',
            'optional': False,
            'outgoing': '50798ac5a9163d80a26df622a3a2c206',
            'type': 'ServiceActivity',
        },
    },
    'data': {
        'inputs': {
            '${act_1_output}': {
                'source_act': '66e5fc0ada053fd8a9951fb8baec68c1',
                'source_key': 'input_a',
                'type': 'splice',
                'value': None,
            },
            '${input_a}': {'type': 'plain', 'value': 0},
        },
        'outputs': [],
    },
    'end_event': {
        'id': 'ab8bc5c813263b73a8777ace488e18b4',
        'incoming': ['2b9cb8cab4473f679b1e99c61f878c7a', 'c1d896443ddb3ec9bcd8105aa21e86eb'],
        'name': None,
        'outgoing': '',
        'type': 'EmptyEndEvent',
    },
    'flows': {
        '107c380cbcfe3fa9abea3ae993a584d2': {
            'id': '107c380cbcfe3fa9abea3ae993a584d2',
            'is_default': False,
            'source': '66e5fc0ada053fd8a9951fb8baec68c1',
            'target': 'c06ddd4beca03bd18cb9f17960eede68',
        },
        '2b9cb8cab4473f679b1e99c61f878c7a': {
            'id': '2b9cb8cab4473f679b1e99c61f878c7a',
            'is_default': False,
            'source': 'c06ddd4beca03bd18cb9f17960eede68',
            'target': 'ab8bc5c813263b73a8777ace488e18b4',
        },
        '50798ac5a9163d80a26df622a3a2c206': {
            'id': '50798ac5a9163d80a26df622a3a2c206',
            'is_default': False,
            'source': '997a6b68bfe933ab9a46890b6ee56e53',
            'target': '66e5fc0ada053fd8a9951fb8baec68c1',
        },
        '701040fef2953c1793c65d9d32c3a730': {
            'id': '701040fef2953c1793c65d9d32c3a730',
            'is_default': False,
            'source': 'c06ddd4beca03bd18cb9f17960eede68',
            'target': '6e1b3c8bdfdf33a891a80ea847693784',
        },
        'c1d896443ddb3ec9bcd8105aa21e86eb': {
            'id': 'c1d896443ddb3ec9bcd8105aa21e86eb',
            'is_default': False,
            'source': '6e1b3c8bdfdf33a891a80ea847693784',
            'target': 'ab8bc5c813263b73a8777ace488e18b4',
        },
        'de49748f24c731efb06bae78565ca945': {
            'id': 'de49748f24c731efb06bae78565ca945',
            'is_default': False,
            'source': '3284bc0698633e30a25b167ed8c8d87b',
            'target': '997a6b68bfe933ab9a46890b6ee56e53',
        },
    },
    'gateways': {
        'c06ddd4beca03bd18cb9f17960eede68': {
            'conditions': {
                '2b9cb8cab4473f679b1e99c61f878c7a': {'evaluate': '${act_1_output} >= 0'},
                '701040fef2953c1793c65d9d32c3a730': {'evaluate': '${act_1_output} < 0'},
            },
            'id': 'c06ddd4beca03bd18cb9f17960eede68',
            'incoming': ['107c380cbcfe3fa9abea3ae993a584d2'],
            'name': 'xiaojia?',
            'outgoing': ['701040fef2953c1793c65d9d32c3a730', '2b9cb8cab4473f679b1e99c61f878c7a'],
            'type': 'ExclusiveGateway',
        }
    },
    'id': '9f684273608532d88b3a6c232fbabf57',
    'start_event': {
        'id': '3284bc0698633e30a25b167ed8c8d87b',
        'incoming': '',
        'name': None,
        'outgoing': 'de49748f24c731efb06bae78565ca945',
        'type': 'EmptyStartEvent',
    },
}
