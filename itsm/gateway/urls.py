# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2025 Tencent.  All rights reserved.

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

__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2025 Tencent BlueKing. All Rights Reserved."

from django.urls import re_path

from itsm.gateway import views

urlpatterns = [
    re_path(r"^bk_login/get_batch_users/$", views.get_batch_users),
    re_path(r"^bk_login/get_all_users/$", views.get_all_users),
    re_path(r"^cmdb/get_app_list/$", views.get_app_list),
    re_path(r"^usermanage/get_departments/$", views.get_departments),
    re_path(
        r"^usermanage/get_first_level_departments/$", views.get_first_level_departments
    ),
    re_path(r"^usermanage/get_department_info/$", views.get_department_info),
    re_path(r"^usermanage/get_department_users/$", views.get_department_users),
    re_path(
        r"^usermanage/get_department_users_count/$", views.get_department_users_count
    ),
    re_path(r"^usermanage/get_user_info/$", views.get_user_info),
    re_path(r"^sops/get_user_project_list/$", views.get_user_project_list),
    re_path(r"^sops/get_template_list/$", views.get_template_list),
    re_path(r"^sops/get_template_detail/$", views.get_template_detail),
    re_path(r"^sops/get_unfinished_sops_tasks/$", views.get_unfinished_sops_tasks),
    re_path(r"^sops/get_sops_tasks/$", views.get_sops_tasks),
    re_path(r"^sops/get_sops_tasks_detail/$", views.get_sops_tasks_detail),
    re_path(r"^sops/get_sops_template_schemes/$", views.get_sops_template_schemes),
    re_path(r"^sops/get_sops_preview_task_tree/$", views.get_sops_preview_task_tree),
    re_path(
        r"^sops/get_sops_preview_common_task_tree/$",
        views.get_sops_preview_common_task_tree,
    ),
    re_path(r"^devops/get_user_pipeline_list/$", views.get_user_pipeline_list),
    re_path(r"^devops/get_user_projects/$", views.get_user_projects),
    re_path(
        r"^devops/get_pipeline_build_start_info/$", views.get_pipeline_build_start_info
    ),
    re_path(r"^devops/get_user_pipeline_detail/$", views.get_user_pipeline_detail),
    re_path(r"^devops/get_pipeline_build_list/$", views.get_pipeline_build_list),
    re_path(r"^devops/start_user_pipeline/$", views.start_user_pipeline),
    re_path(
        r"^devops/get_user_pipeline_build_status/$",
        views.get_user_pipeline_build_status,
    ),
    re_path(
        r"^devops/get_user_pipeline_build_detail/$",
        views.get_user_pipeline_build_detail,
    ),
    re_path(
        r"^devops/get_pipeline_build_artifactory/$",
        views.get_pipeline_build_artifactory,
    ),
    re_path(
        r"^devops/get_pipeline_build_artifactory_download_url/$",
        views.get_pipeline_build_artifactory_download_url,
    ),
]
