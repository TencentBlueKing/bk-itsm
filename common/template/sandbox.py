# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

# 模板渲染沙箱

from typing import List, Dict

import importlib
from django.conf import settings

# pipeline mako render settings
MAKO_SANDBOX_SHIELD_WORDS = [
    "ascii",
    "bytearray",
    "bytes",
    "callable",
    "chr",
    "classmethod",
    "compile",
    "delattr",
    "dir",
    "divmod",
    "exec",
    "eval",
    "filter",
    "frozenset",
    "getattr",
    "globals",
    "hasattr",
    "hash",
    "help",
    "id",
    "input",
    "isinstance",
    "issubclass",
    "iter",
    "locals",
    "map",
    "memoryview",
    "next",
    "object",
    "open",
    "print",
    "property",
    "repr",
    "setattr",
    "staticmethod",
    "super",
    "type",
    "vars",
    "__import__",
]


# format: module_path: alias
MAKO_SANDBOX_IMPORT_MODULES = {
    "datetime": "datetime",
    "time": "time",
}


class ModuleObject:
    def __init__(self, sub_paths, module):
        if len(sub_paths) == 1:
            setattr(self, sub_paths[0], module)
            return
        setattr(self, sub_paths[0], ModuleObject(sub_paths[1:], module))


class Sandbox:
    def get(self) -> dict:
        sandbox = {}

        self._shield_words(sandbox, getattr(settings, "MAKO_SANDBOX_SHIELD_WORDS", MAKO_SANDBOX_SHIELD_WORDS))
        self._import_modules(sandbox, getattr(settings, "MAKO_SANDBOX_IMPORT_MODULES", MAKO_SANDBOX_IMPORT_MODULES))

        return sandbox

    @staticmethod
    def _shield_words(sandbox: dict, words: List[str]):
        for shield_word in words:
            sandbox[shield_word] = None

    @staticmethod
    def _import_modules(sandbox: dict, modules: Dict[str, str]):
        for mod_path, alias in modules.items():
            mod = importlib.import_module(mod_path)
            sub_paths = alias.split(".")
            if len(sub_paths) == 1:
                sandbox[alias] = mod
            else:
                sandbox[sub_paths[0]] = ModuleObject(sub_paths[1:], mod)
