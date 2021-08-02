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
from django.utils.translation import gettext_lazy as _
from django.conf import settings


def get_doc_url():
    from itsm.component.esb.esbclient import client_backend

    try:
        res = client_backend.doc_center.get_doc_link_by_path({"md_path": "流程服务/产品白皮书/产品简介/README.md"})
        return os.path.join(settings.BK_PAAS_HOST, "o/bk_docs_center/", res)
    except Exception as err:
        print(err)
        return os.path.join(settings.BK_PAAS_HOST, "o/bk_docs_center/markdown/流程服务/产品白皮书/产品简介/README.md")


if settings.OPEN_VER == "enterprise":
    TITLE = "{} | {}".format(_("流程服务"), _("蓝鲸智云企业版"))
    DOC_URL = get_doc_url()
else:
    TITLE = "{} | {}".format(_("流程服务"), _("蓝鲸智云社区版"))
    DOC_URL = "https://bk.tencent.com/docs/markdown/流程服务/产品白皮书/产品简介/README.md"

FOOTER = """
        <div class="copyright">
            <ul class="link-list">
                <a href="tencent://message/?uin=800802001&site=qq&menu=yes" class="link-item">{}(800802001)</a>
                <a href="http://bk.tencent.com/s-mart/community/" class="link-item" target="_blank">{}</a>
                <a href="http://bk.tencent.com/" class="link-item" target="_blank">{}</a>
                <a href="{}" class="link-item" target="_blank">{}</a>
            </ul>
            <div class="desc">Copyright &copy; 2012-${{year}} Tencent BlueKing. All Rights Reserved.</div>
        </div>
        """.format(
    _("QQ咨询"), _("蓝鲸论坛"), _("蓝鲸官网"), settings.BK_PAAS_HOST, _("蓝鲸智云桌面")
)

LOGIN_URL = settings.BK_PAAS_HOST + "/login/"
