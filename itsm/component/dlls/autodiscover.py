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

import logging
import pkgutil
import sys
from importlib import import_module

logger = logging.getLogger('root')


def autodiscover_items(module):
    """
    Given a path to discover, auto register all items
    """
    # Workaround for a Python 3.2 bug with pkgutil.iter_modules
    module_dir = module.__path__[0]
    sys.path_importer_cache.pop(module_dir, None)
    modules = [
        name for _, name, is_pkg in pkgutil.iter_modules([module_dir]) if not is_pkg and not name.startswith('_')
    ]
    for name in modules:
        module_path = "{}.{}".format(module.__name__, name)
        try:
            __import__(module_path)
        except Exception as e:
            logger.error(f'[!] module({module_path}) import failed with err: {e}')


def autodiscover_collections(path):
    """
    Auto-discover INSTALLED_APPS modules and fail silently when
    not present. This forces an import on them to register any admin bits they
    may want.
    """
    from django.apps import apps

    for app_config in apps.get_app_configs():
        # Attempt to import the app's module.
        try:

            _module = import_module('%s.%s' % (app_config.name, path))
            autodiscover_items(_module)
        except ImportError as e:
            if not str(e) == 'No module named %s' % path:
                pass
