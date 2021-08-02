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


# mako模板的render方法等

import json

from django.conf import settings
from django.http import HttpResponse
from django.template.context import Context
from mako.lookup import TemplateLookup

from common.log import logger

# mylookup 也可以单独使用：
# @Example:
#              mako_temp = mylookup.get_template(template_name)
#              mako_temp.render(**data)

mylookup = TemplateLookup(directories=settings.MAKO_TEMPLATE_DIR,
                          module_directory=settings.MAKO_TEMPLATE_MODULE_DIR,
                          output_encoding='utf-8',
                          input_encoding='utf-8',
                          encoding_errors='replace',
                          collection_size=500,
                          )


def render_mako(template_name, dictionary=None, context_instance=None):
    """
    render the mako template and return the HttpResponse

    @param template_name: 模板名字
    @param dictionary: context字典
    @param context_instance: 初始化context，如果要使用 TEMPLATE_CONTEXT_PROCESSORS，则要使用RequestContext(request)
    @note: 因为返回是HttpResponse，所以这个方法也适合给ajax用(dataType不是json的ajax)
    @Example:
                 render_mako('mako_temp.html',{'form':form})
            or
                 render_mako('mako_temp.html',{'form':form},RequestContext(request))
            or
                 render_mako('mako_temp.html',{},RequestContext(request，{'form':form}))
    """

    if dictionary is None:
        dictionary = {}
    mako_temp = mylookup.get_template(template_name)
    if context_instance:
        # RequestContext(request)
        context_instance.update(dictionary)
    else:
        # 默认为Context
        context_instance = Context(dictionary)
    data = {}
    # construct date dictory
    for d in context_instance:
        data.update(d)
    # return response
    # .replace('\r','').replace('\n','').replace('\t','')
    return HttpResponse(mako_temp.render_unicode(**data))


def render_mako_context(request, template_name, dictionary=None):
    """
    render the mako template with the RequestContext and return the HttpResponse
    """
    if dictionary is None:
        dictionary = {}
    context_instance = get_context_processors_content(request)
    # ===========================================================================
    # # you can add csrf_token here
    # from django.core.context_processors import csrf
    # context_instance['csrf_token'] = csrf(request)['csrf_token']
    # ===========================================================================
    # render
    return render_mako(template_name, dictionary=dictionary,
                       context_instance=context_instance)


def render_mako_tostring(template_name, dictionary=None, context_instance=None):
    """
    render_mako_tostring without RequestContext
    @note: 因为返回是string，所以这个方法适合include的子页面用
    """
    if dictionary is None:
        dictionary = {}
    mako_temp = mylookup.get_template(template_name)
    if context_instance:
        # RequestContext(request)
        context_instance.update(dictionary)
    else:
        # 默认为Context
        context_instance = Context(dictionary)
    data = {}
    # construct date dictory
    for d in context_instance:
        data.update(d)
    # return string
    # .replace('\t','').replace('\n','').replace('\r','')
    return mako_temp.render_unicode(**data)


def render_mako_tostring_context(request, template_name, dictionary=None):
    """
    render_mako_tostring with RequestContext
    """
    if dictionary is None:
        dictionary = {}
    context_instance = get_context_processors_content(request)
    return render_mako_tostring(
        template_name, dictionary=dictionary, context_instance=context_instance)


def render_json(dictionary=None):
    """
    return the json string for response
    @summary: dictionary也可以是string, list数据
    @note:  返回结果是个dict, 请注意默认数据格式:
                                    {'result': '',
                                     'message':''
                                    }
    """
    if dictionary is None:
        dictionary = {}
    if not isinstance(dictionary, dict):
        # 如果参数不是dict,则组合成dict
        dictionary = {
            'result': True,
            'message': dictionary,
        }
    return HttpResponse(json.dumps(dictionary),
                        content_type='application/json')


def get_context_processors_content(request):
    """
    return the context_processors dict context
    """
    context = Context()
    try:
        from django.utils.module_loading import import_string
        from django.template.context import _builtin_context_processors
        context_processors = _builtin_context_processors
        for i in settings.TEMPLATES:
            context_processors += tuple(i.get('OPTIONS',
                                              {}).get('context_processors', []))
        cp_func_list = tuple(import_string(path)
                             for path in context_processors)
        for processors in cp_func_list:
            context.update(processors(request))
    except Exception as e:
        logger.error("Mako: get_context_processors_content error info:%s" % e)
        context = Context()
    return context
