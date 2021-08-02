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

# 单元测试mock，跑单元测定时候记得打开
# from django import apps
# from django.conf import settings
# from django.core.signals import setting_changed
# from django.test import override_settings
# import django
# 
# 
# class override_settings(override_settings):
# 
#     def enable(self):
#         # Keep this code at the beginning to leave the settings unchanged
#         # in case it raises an exception because INSTALLED_APPS is invalid.
#         if 'INSTALLED_APPS' in self.options:
#             try:
#                 apps.set_installed_apps(self.options['INSTALLED_APPS'])
#             except Exception:
#                 apps.unset_installed_apps()
#                 raise
#         for key, new_value in self.options.items():
#             setattr(settings, key, new_value)
# 
#         for key, new_value in self.options.items():
#             try:
#                 setting_changed.send(
#                     sender=settings._wrapped.__class__,
#                     setting=key, value=new_value, enter=True,
#                 )
#             except Exception as exc:
#                 self.enable_exception = exc
#                 self.disable()
# 
#     def disable(self):
#         if 'INSTALLED_APPS' in self.options:
#             apps.unset_installed_apps()
#         responses = []
#         for key in self.options:
#             new_value = getattr(settings, key, None)
#             responses_for_setting = setting_changed.send_robust(
#                 sender=settings._wrapped.__class__,
#                 setting=key, value=new_value, enter=False,
#             )
#             responses.extend(responses_for_setting)
#         if self.enable_exception is not None:
#             exc = self.enable_exception
#             self.enable_exception = None
#             raise exc
#         for _, response in responses:
#             if isinstance(response, Exception):
#                 raise response
# 
# 
# django.test.override_settings = override_settings
# 
