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

# 执行app初始化操作，步骤位于migrate操作后，需要print信息到标准输出
# http://www.koopman.me/2015/01/django-signals-example/

from django.apps import AppConfig
from django.db.models.signals import post_migrate, post_save, pre_save
from itsm.trigger.signal import post_action_finish


def app_ready_handler(sender, **kwargs):
    from itsm.ticket.models import TicketComment

    TicketComment.fix_comments()
    # Ticket.objects.upgrade_running_tickets()


class TicketConfig(AppConfig):
    name = "itsm.ticket"

    def ready(self):
        from itsm.ticket.models import Ticket
        from itsm.ticket.handlers import before_ticket_status_updated, after_ticket_created, create_trigger_action_log

        # 耗时数据迁移初始化方案：在启动celery的时候，下放到celery中，确保可以重入
        # if sys.argv[1] == 'celery' and sys.argv[2] == 'worker':
        #     print 'app[%s] ready in celery worker' % self.name
        #     from itsm.ticket.tasks import auto_comment
        #     auto_comment.delay()
        post_migrate.connect(app_ready_handler, sender=self)
        post_save.connect(after_ticket_created, sender=Ticket)
        pre_save.connect(before_ticket_status_updated, sender=Ticket)
        post_action_finish.connect(create_trigger_action_log)
