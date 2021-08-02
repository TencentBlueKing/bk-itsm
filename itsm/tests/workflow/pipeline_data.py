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
    "activities": {
        "d7ae65aadfb43512b63ce66c2aeb89cd": {
            "component": {"inputs": {}, "code": "pipe_example_component"},
            "outgoing": "8788a1c3f2003d0e826a59ac5ee4c565",
            "incoming": ["0125f774ee74306e8d59490858b7f6c7"],
            "name": "shenhe",
            "error_ignorable": False,
            "type": "ServiceActivity",
            "id": "d7ae65aadfb43512b63ce66c2aeb89cd",
            "optional": False,
        },
        "a64e46369aa834198b597a9cbe0ff93c": {
            "component": {"inputs": {}, "code": "pipe_example_component"},
            "outgoing": "c6e5c4bc547b3821a0e3dc0813da4fb5",
            "incoming": ["5d386a7107513e688d3be06a341f43e8"],
            "name": "test",
            "error_ignorable": False,
            "type": "ServiceActivity",
            "id": "a64e46369aa834198b597a9cbe0ff93c",
            "optional": False,
        },
        "cacfa5a3f0fd33cca34880760716dfb9": {
            "component": {"inputs": {}, "code": "pipe_example_component"},
            "outgoing": "0125f774ee74306e8d59490858b7f6c7",
            "incoming": ["aaf6795dd8413e5096ee139e7fb2a9dd"],
            "name": "tidan",
            "error_ignorable": False,
            "type": "ServiceActivity",
            "id": "cacfa5a3f0fd33cca34880760716dfb9",
            "optional": False,
        },
        "b3f41e16ecd63423971118cb0b03b5c9": {
            "component": {"inputs": {}, "code": "pipe_example_component"},
            "outgoing": "5d386a7107513e688d3be06a341f43e8",
            "incoming": ["d270d72afa01388aa908d346b360b04d", "aa4749b6d5b33f21a2dc0bfd53d32004"],
            "name": "product",
            "error_ignorable": False,
            "type": "ServiceActivity",
            "id": "b3f41e16ecd63423971118cb0b03b5c9",
            "optional": False,
        },
        "e2f9252439bc324fa6cc2769b3c88052": {
            "component": {"inputs": {}, "code": "pipe_example_component"},
            "outgoing": "6e4ce96335683087a4a7e1c9752cd317",
            "incoming": ["13c944b6ccca36b7a94afcf3e168d66e"],
            "name": "check_jiqi",
            "error_ignorable": False,
            "type": "ServiceActivity",
            "id": "e2f9252439bc324fa6cc2769b3c88052",
            "optional": False,
        },
        "cf1b209adff03f0daf5d8ebf77939a1d": {
            "component": {"inputs": {}, "code": "pipe_example_component"},
            "outgoing": "13c944b6ccca36b7a94afcf3e168d66e",
            "incoming": ["47c4644b26003afeb486786b76fc4ab0", "13a6bdcf5d243f4696fac1f0e12989e9"],
            "name": "prepare_jiqi",
            "error_ignorable": False,
            "type": "ServiceActivity",
            "id": "cf1b209adff03f0daf5d8ebf77939a1d",
            "optional": False,
        },
        "c8e000d6217b3994aec11b9835008e2f": {
            "component": {"inputs": {}, "code": "pipe_example_component"},
            "outgoing": "e3e9bded659a3625b50e455082fa8447",
            "incoming": ["265305952cc23f098ec0a2dc8cbd0974"],
            "name": "check_cailiao",
            "error_ignorable": False,
            "type": "ServiceActivity",
            "id": "c8e000d6217b3994aec11b9835008e2f",
            "optional": False,
        },
        "882e5572415a3b9a9b0429bdea6d10b2": {
            "component": {"inputs": {}, "code": "pipe_example_component"},
            "outgoing": "265305952cc23f098ec0a2dc8cbd0974",
            "incoming": ["6978366a50df35329890fc8e8d81d86f", "24a0fff27376374e901cc563d53c92f7"],
            "name": "prepare_cailiao",
            "error_ignorable": False,
            "type": "ServiceActivity",
            "id": "882e5572415a3b9a9b0429bdea6d10b2",
            "optional": False,
        },
    },
    "end_event": {
        "type": "EmptyEndEvent",
        "outgoing": "",
        "incoming": ["44821106fc873f16af6156a7ea80cf94", "9aa992dbe6793dce87f934fa3ae23e5e"],
        "id": "d29bfaca82943283837570d4576d6c57",
        "name": "end",
    },
    "flows": {
        "9aa992dbe6793dce87f934fa3ae23e5e": {
            "is_default": False,
            "source": "ae16a7d842a533f38aefd12c17605a43",
            "target": "d29bfaca82943283837570d4576d6c57",
            "id": "9aa992dbe6793dce87f934fa3ae23e5e",
        },
        "8788a1c3f2003d0e826a59ac5ee4c565": {
            "is_default": False,
            "source": "d7ae65aadfb43512b63ce66c2aeb89cd",
            "target": "5f17a27823c431e0805ca834e0bdf82c",
            "id": "8788a1c3f2003d0e826a59ac5ee4c565",
        },
        "c6e5c4bc547b3821a0e3dc0813da4fb5": {
            "is_default": False,
            "source": "a64e46369aa834198b597a9cbe0ff93c",
            "target": "ae16a7d842a533f38aefd12c17605a43",
            "id": "c6e5c4bc547b3821a0e3dc0813da4fb5",
        },
        "47c4644b26003afeb486786b76fc4ab0": {
            "is_default": False,
            "source": "24ffb6dd945831878fca3dfec9eb3140",
            "target": "cf1b209adff03f0daf5d8ebf77939a1d",
            "id": "47c4644b26003afeb486786b76fc4ab0",
        },
        "24a0fff27376374e901cc563d53c92f7": {
            "is_default": False,
            "source": "77048831d0703ac59e748f7e3f33069e",
            "target": "882e5572415a3b9a9b0429bdea6d10b2",
            "id": "24a0fff27376374e901cc563d53c92f7",
        },
        "aaf6795dd8413e5096ee139e7fb2a9dd": {
            "is_default": False,
            "source": "b5b4f395db00334e862bacb56e7828e2",
            "target": "cacfa5a3f0fd33cca34880760716dfb9",
            "id": "aaf6795dd8413e5096ee139e7fb2a9dd",
        },
        "265305952cc23f098ec0a2dc8cbd0974": {
            "is_default": False,
            "source": "882e5572415a3b9a9b0429bdea6d10b2",
            "target": "c8e000d6217b3994aec11b9835008e2f",
            "id": "265305952cc23f098ec0a2dc8cbd0974",
        },
        "d270d72afa01388aa908d346b360b04d": {
            "is_default": False,
            "source": "2b44fffa37b53736abf496acad963755",
            "target": "b3f41e16ecd63423971118cb0b03b5c9",
            "id": "d270d72afa01388aa908d346b360b04d",
        },
        "e23e182a1f6a37dbbb137ea5b5437361": {
            "is_default": False,
            "source": "77048831d0703ac59e748f7e3f33069e",
            "target": "2b44fffa37b53736abf496acad963755",
            "id": "e23e182a1f6a37dbbb137ea5b5437361",
        },
        "13a6bdcf5d243f4696fac1f0e12989e9": {
            "is_default": False,
            "source": "39d871a79f7637b2b2dda74b92f0a9fc",
            "target": "cf1b209adff03f0daf5d8ebf77939a1d",
            "id": "13a6bdcf5d243f4696fac1f0e12989e9",
        },
        "44821106fc873f16af6156a7ea80cf94": {
            "is_default": False,
            "source": "5f17a27823c431e0805ca834e0bdf82c",
            "target": "d29bfaca82943283837570d4576d6c57",
            "id": "44821106fc873f16af6156a7ea80cf94",
        },
        "aa4749b6d5b33f21a2dc0bfd53d32004": {
            "is_default": False,
            "source": "ae16a7d842a533f38aefd12c17605a43",
            "target": "b3f41e16ecd63423971118cb0b03b5c9",
            "id": "aa4749b6d5b33f21a2dc0bfd53d32004",
        },
        "e3e9bded659a3625b50e455082fa8447": {
            "is_default": False,
            "source": "c8e000d6217b3994aec11b9835008e2f",
            "target": "77048831d0703ac59e748f7e3f33069e",
            "id": "e3e9bded659a3625b50e455082fa8447",
        },
        "13c944b6ccca36b7a94afcf3e168d66e": {
            "is_default": False,
            "source": "cf1b209adff03f0daf5d8ebf77939a1d",
            "target": "e2f9252439bc324fa6cc2769b3c88052",
            "id": "13c944b6ccca36b7a94afcf3e168d66e",
        },
        "6e4ce96335683087a4a7e1c9752cd317": {
            "is_default": False,
            "source": "e2f9252439bc324fa6cc2769b3c88052",
            "target": "39d871a79f7637b2b2dda74b92f0a9fc",
            "id": "6e4ce96335683087a4a7e1c9752cd317",
        },
        "5d386a7107513e688d3be06a341f43e8": {
            "is_default": False,
            "source": "b3f41e16ecd63423971118cb0b03b5c9",
            "target": "a64e46369aa834198b597a9cbe0ff93c",
            "id": "5d386a7107513e688d3be06a341f43e8",
        },
        "da906b13e6d43aea8025e9cc272502a2": {
            "is_default": False,
            "source": "5f17a27823c431e0805ca834e0bdf82c",
            "target": "24ffb6dd945831878fca3dfec9eb3140",
            "id": "da906b13e6d43aea8025e9cc272502a2",
        },
        "0627917d731f381e8ada8ce92395f360": {
            "is_default": False,
            "source": "39d871a79f7637b2b2dda74b92f0a9fc",
            "target": "2b44fffa37b53736abf496acad963755",
            "id": "0627917d731f381e8ada8ce92395f360",
        },
        "0125f774ee74306e8d59490858b7f6c7": {
            "is_default": False,
            "source": "cacfa5a3f0fd33cca34880760716dfb9",
            "target": "d7ae65aadfb43512b63ce66c2aeb89cd",
            "id": "0125f774ee74306e8d59490858b7f6c7",
        },
        "6978366a50df35329890fc8e8d81d86f": {
            "is_default": False,
            "source": "24ffb6dd945831878fca3dfec9eb3140",
            "target": "882e5572415a3b9a9b0429bdea6d10b2",
            "id": "6978366a50df35329890fc8e8d81d86f",
        },
    },
    "gateways": {
        "5f17a27823c431e0805ca834e0bdf82c": {
            "outgoing": ["da906b13e6d43aea8025e9cc272502a2", "44821106fc873f16af6156a7ea80cf94"],
            "incoming": ["8788a1c3f2003d0e826a59ac5ee4c565"],
            "name": "shenhe_ok?",
            "conditions": {
                "44821106fc873f16af6156a7ea80cf94": {"evaluate": "1==0"},
                "da906b13e6d43aea8025e9cc272502a2": {"evaluate": "1==1"},
            },
            "type": "ExclusiveGateway",
            "id": "5f17a27823c431e0805ca834e0bdf82c",
        },
        "77048831d0703ac59e748f7e3f33069e": {
            "outgoing": ["24a0fff27376374e901cc563d53c92f7", "e23e182a1f6a37dbbb137ea5b5437361"],
            "incoming": ["e3e9bded659a3625b50e455082fa8447"],
            "name": "shenhe_cailiao?",
            "conditions": {
                "e23e182a1f6a37dbbb137ea5b5437361": {"evaluate": "1==0"},
                "24a0fff27376374e901cc563d53c92f7": {"evaluate": "1==1"},
            },
            "converge_gateway_id": "2b44fffa37b53736abf496acad963755",
            "type": "ExclusiveGateway",
            "id": "77048831d0703ac59e748f7e3f33069e",
        },
        "39d871a79f7637b2b2dda74b92f0a9fc": {
            "outgoing": ["13a6bdcf5d243f4696fac1f0e12989e9", "0627917d731f381e8ada8ce92395f360"],
            "incoming": ["6e4ce96335683087a4a7e1c9752cd317"],
            "name": "shenhe_jiqi?",
            "conditions": {
                "13a6bdcf5d243f4696fac1f0e12989e9": {"evaluate": "1==1"},
                "0627917d731f381e8ada8ce92395f360": {"evaluate": "1==0"},
            },
            "converge_gateway_id": "2b44fffa37b53736abf496acad963755",
            "type": "ExclusiveGateway",
            "id": "39d871a79f7637b2b2dda74b92f0a9fc",
        },
        "2b44fffa37b53736abf496acad963755": {
            "type": "ConvergeGateway",
            "outgoing": "d270d72afa01388aa908d346b360b04d",
            "incoming": ["e23e182a1f6a37dbbb137ea5b5437361", "0627917d731f381e8ada8ce92395f360"],
            "id": "2b44fffa37b53736abf496acad963755",
            "name": "product_ready",
        },
        "24ffb6dd945831878fca3dfec9eb3140": {
            "outgoing": ["6978366a50df35329890fc8e8d81d86f", "47c4644b26003afeb486786b76fc4ab0"],
            "incoming": ["da906b13e6d43aea8025e9cc272502a2"],
            "name": "prepare",
            "converge_gateway_id": "2b44fffa37b53736abf496acad963755",
            "type": "ParallelGateway",
            "id": "24ffb6dd945831878fca3dfec9eb3140",
        },
        "ae16a7d842a533f38aefd12c17605a43": {
            "outgoing": ["aa4749b6d5b33f21a2dc0bfd53d32004", "9aa992dbe6793dce87f934fa3ae23e5e"],
            "incoming": ["c6e5c4bc547b3821a0e3dc0813da4fb5"],
            "name": "test_ok?",
            "conditions": {
                "9aa992dbe6793dce87f934fa3ae23e5e": {"evaluate": "1==0"},
                "aa4749b6d5b33f21a2dc0bfd53d32004": {"evaluate": "1==1"},
            },
            "type": "ExclusiveGateway",
            "id": "ae16a7d842a533f38aefd12c17605a43",
        },
    },
    "start_event": {
        "type": "EmptyStartEvent",
        "outgoing": "aaf6795dd8413e5096ee139e7fb2a9dd",
        "incoming": "",
        "id": "b5b4f395db00334e862bacb56e7828e2",
        "name": "start",
    },
    "data": {"inputs": {}, "outputs": []},
    "id": "b7f54e7db52439159cebabc1f93e3b61",
}
