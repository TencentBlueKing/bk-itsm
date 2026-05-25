# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2025 Tencent. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

# 模板渲染沙箱

import importlib
import logging
from typing import List, Dict

from django.conf import settings

from common.template.mako_utils.exceptions import ForbiddenMakoTemplateException

logger = logging.getLogger("root")

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


class _ForbiddenProxy:
    """
    Mako 沙箱屏蔽词的运行时代理对象。
    任何属性访问 / 调用 / 下标 / 迭代 / 比较 / 转换都会抛出 ForbiddenMakoTemplateException，
    并以 WARNING 级别记录被触达的 token 名，便于事后审计与 SOC 告警。

    设计原则：
    - 不实现 __bool__（默认 True），避免被 `if proxy:` 当成 None 误用导致静默
    - 所有 dunder 拦截，防止攻击者通过 __class__ / __subclasses__ 等绕回真实类型
    """

    __slots__ = ("_token",)

    def __init__(self, token: str):
        # 用 object.__setattr__ 避免触发自身的 __setattr__
        object.__setattr__(self, "_token", token)

    def _deny(self, action: str):
        token = object.__getattribute__(self, "_token")
        logger.warning(
            "[mako-sandbox] forbidden token accessed: token=%s, action=%s",
            token, action,
        )
        raise ForbiddenMakoTemplateException(
            "forbidden builtin '{}' accessed via {}".format(token, action)
        )

    # 关键：拦截所有属性读取（含 __class__ / __dict__ / __bases__ 等）
    def __getattribute__(self, name):
        # 仅放行内部 _deny 自身（用于触发拒绝逻辑），其它一律拒绝
        # 注意：__class__ 也必须拒绝，否则攻击者可通过
        #   ${getattr.__class__.__bases__[0].__subclasses__()} 拿到 object 子类树形成 RCE 跳板
        if name == "_deny":
            return object.__getattribute__(self, name)
        # 直接走 object.__getattribute__ 拿 _deny，避免再次进入本方法导致死循环
        object.__getattribute__(self, "_deny")("getattr:{}".format(name))

    def __setattr__(self, key, value):
        self._deny("setattr:{}".format(key))

    def __delattr__(self, key):
        self._deny("delattr:{}".format(key))

    def __call__(self, *args, **kwargs):
        self._deny("call")

    def __getitem__(self, item):
        self._deny("getitem:{}".format(item))

    def __iter__(self):
        self._deny("iter")

    def __contains__(self, item):
        self._deny("contains")

    def __format__(self, format_spec):
        # 拦截 ${var:fmt} 与 f-string 路径下的 __format__ 调用
        self._deny("format:{}".format(format_spec))

    # 严格模式：任何对屏蔽词的隐式/显式打印都视为越权访问，立即抛异常。
    # 上层 _render_template 的 except Exception 会兜底返回模板原文，确保安全失败。
    # 注意：调用方在 logger 中应避免直接 "%s" 整段 sandbox/data 字典，
    # 否则字典 repr 会触达此处的 __repr__ 进而抛异常，导致这条日志丢失。
    def __repr__(self):
        self._deny("repr")

    def __str__(self):
        self._deny("str")


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
            sandbox[shield_word] = _ForbiddenProxy(shield_word)

    @staticmethod
    def _import_modules(sandbox: dict, modules: Dict[str, str]):
        for mod_path, alias in modules.items():
            mod = importlib.import_module(mod_path)
            sub_paths = alias.split(".")
            if len(sub_paths) == 1:
                sandbox[alias] = mod
            else:
                sandbox[sub_paths[0]] = ModuleObject(sub_paths[1:], mod)
