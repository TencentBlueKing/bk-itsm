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

# 请不要修改该文件
# 如果你需要对settings里的内容做修改，config/default.py 文件中 添加即可
# 如有任何疑问，请联系 【蓝鲸助手】

import os

# V3判断环境的环境变量为BKPAAS_ENVIRONMENT
if 'BKPAAS_ENVIRONMENT' in os.environ:
    ENVIRONMENT = os.getenv('BKPAAS_ENVIRONMENT', 'dev')
# V2判断环境的环境变量为BK_ENV
else:
    PAAS_V2_ENVIRONMENT = os.environ.get('BK_ENV', 'development')
    ENVIRONMENT = {
        'development': 'dev',
        'testing': 'stag',
        'production': 'prod',
    }.get(PAAS_V2_ENVIRONMENT)
DJANGO_CONF_MODULE = 'config.{env}'.format(env=ENVIRONMENT)

try:
    _module = __import__(DJANGO_CONF_MODULE, globals(), locals(), ['*'])
except ImportError as e:
    raise ImportError("Could not import config '%s' (Is it on sys.path?): %s"
                      % (DJANGO_CONF_MODULE, e))

for _setting in dir(_module):
    if _setting == _setting.upper():
        locals()[_setting] = getattr(_module, _setting)

# check saas app  settings
try:
    saas_conf_module = "config.settings_saas"
    saas_module = __import__(saas_conf_module, globals(), locals(), ['*'])
    for saas_setting in dir(saas_module):
        if saas_setting == saas_setting.upper():
            locals()[saas_setting] = getattr(saas_module, saas_setting)
except BaseException:
    pass

# check weixin settings
try:
    weixin_conf_module = "weixin.core.settings"
    weixin_module = __import__(weixin_conf_module, globals(), locals(), ['*'])
    for weixin_setting in dir(weixin_module):
        if weixin_setting == weixin_setting.upper():
            locals()[weixin_setting] = getattr(weixin_module, weixin_setting)
except Exception:
    pass

# check mini weixin settings
try:
    miniweixin_conf_module = "miniweixin.core.settings"
    miniweixin_module = __import__(
        miniweixin_conf_module, globals(), locals(), ['*']
    )
    for miniweixin_setting in dir(miniweixin_module):
        if miniweixin_setting == miniweixin_setting.upper():
            locals()[miniweixin_setting] = getattr(
                miniweixin_module, miniweixin_setting
            )
except Exception:
    pass
