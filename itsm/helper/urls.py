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

__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved."

from django.conf.urls import url

from itsm.helper import views

urlpatterns = [
    # 统一的升级接口
    url(r'^db_fix_from_1_1_22_to_2_1_16/$', views.db_fix_from_1_1_22_to_2_1_16),
    url(r'^db_fix_from_2_1_x_to_2_2_1/$', views.db_fix_from_2_1_x_to_2_2_1),
    url(r'^db_fix_after_2_2_17/$', views.db_fix_after_2_2_17),
    url(r'^db_fix_after_2_3_1/$', views.db_fix_after_2_3_1),
    # 杂乱的升级接口
    url(r'^fix_ticket_title/$', views.fix_ticket_title),
    url(r'^update_logs_type/$', views.update_logs_type),
    url(r'^db_fix_after_2_0_3/$', views.db_fix_after_2_0_3),
    url(r'^db_fix_ticket_end_at_after_2_0_5/$', views.db_fix_ticket_end_at_after_2_0_5),
    url(r'^db_fix_deal_time_after_2_0_5/$', views.db_fix_deal_time_after_2_0_5),
    url(r'^db_fix_after_2_0_7/$', views.db_fix_after_2_0_7),
    url(r'^db_fix_after_2_0_9/$', views.db_fix_after_2_0_9),
    url(r'^db_fix_after_2_0_14/$', views.db_fix_after_2_0_14),
    url(r'^db_fix_after_2_1_x/$', views.db_fix_after_2_1_x),
    url(r'^db_fix_after_2_1_1/$', views.db_fix_after_2_1_1),
    url(r'^db_fix_sla/$', views.db_fix_sla),
    url(r'^db_fix_after_2_1_9/$', views.db_fix_after_2_1_9),
    url(r'^export_api_system/$', views.export_api_system),
    url(r'^db_fix_for_attachments/$', views.db_fix_for_attachments),
    url(r'^db_fix_for_service_catalog/$', views.db_fix_for_service_catalog),
    url(r'^weekly_statical/$', views.weekly_statical),
    url(r'^db_fix_for_workflow_after_2_5_9/$', views.db_fix_for_workflow_after_2_5_9),
    url(r'^db_fix_for_blueapps_after_2_6_0/$', views.db_fix_for_blueapps_after_2_6_0),
    # 获取settings内容
]

# urlpatterns += [
#     url(r'^dump_db/$', views_common.dump_db),
#     url(r'^drop_table/$', views_common.drop_table),
# ]
