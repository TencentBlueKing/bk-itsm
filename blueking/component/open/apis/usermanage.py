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

from ..base import ComponentAPI


class CollectionsUSERMANAGE(object):
    """Collections of USERMANAGE APIS"""

    def __init__(self, client):
        self.client = client

        self.department_ancestor = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/usermanage/department_ancestor/',
            description=u'查询部门全部祖先'
        )
        self.list_department_profiles = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/usermanage/list_department_profiles/',
            description=u'查询部门的用户信息 (v2)'
        )
        self.list_departments = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/usermanage/list_departments/',
            description=u'查询部门 (v2)'
        )
        self.list_profile_departments = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/usermanage/list_profile_departments/',
            description=u'查询用户的部门信息 (v2)'
        )
        self.list_users = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/usermanage/list_users/',
            description=u'查询用户 (v2)'
        )
        self.retrieve_department = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/usermanage/retrieve_department/',
            description=u'查询单个部门信息 (v2)'
        )
        self.retrieve_user = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/usermanage/retrieve_user/',
            description=u'查询单个用户信息 (v2)'
        )

        # 废弃的
        self.department_list = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/usermanage/department_list/',
            description='查询部门列表'
        )
        self.department_profile = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/usermanage/department_profile/',
            description='查询指定部门成员信息'
        )
        self.department = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/usermanage/department/',
            description='查询指定部门信息'
        )
        self.profile = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/usermanage/profile/',
            description='查询成员详情信息'
        )
