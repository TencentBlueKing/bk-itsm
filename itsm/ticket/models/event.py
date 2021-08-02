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

from django.db import models
from django.utils.translation import ugettext as _

from itsm.component.constants import (
    EMPTY_INT,
    EMPTY_STRING,
    LEN_SHORT,
    LEN_XX_LONG,
    MOBILE,
    SYS,
    SYSTEM_OPERATE,
    WEB,
)
from itsm.component.utils.misc import transform_single_username
from itsm.ticket import managers
from itsm.workflow.models import Event


class TicketEventLog(Event):
    """单据操作日志表"""

    SOURCE_TYPE = [(WEB, _('页面操作')), (MOBILE, _('移动端操作')), (SYS, _('系统操作')), (SYSTEM_OPERATE, _('自动执行'))]

    # id = models.BigAutoField(u'日志大于2^31-1，默认id无法继续创建')
    ticket = models.ForeignKey('ticket.Ticket', help_text=_('关联工单'), related_name='logs', on_delete=models.CASCADE)
    is_valid = models.BooleanField(_('是否有效流程节点'), default=True)
    deal_time = models.IntegerField(_('处理时间'), default=0)
    # 日志固化角色人员， 若角色新增人员，无法添加到快照中，需要手动添加
    processors_snap = models.CharField(_('处理人快照'), max_length=LEN_XX_LONG, default=EMPTY_STRING, null=True, blank=True)
    source = models.CharField(_('日志来源'), max_length=LEN_SHORT, choices=SOURCE_TYPE, default=WEB)
    status = models.IntegerField(_('节点处理状态'), default=EMPTY_INT)

    objects = managers.TicketLogManager()

    class Meta:
        app_label = 'ticket'
        verbose_name = _('单据流转日志')
        verbose_name_plural = _('单据流转日志')
        ordering = ('id',)
        index_together = (("operate_at", "operator", "is_deleted"),)

    def __unicode__(self):
        return '{}({})'.format(self.ticket, self.from_state_id)

    def update_deal_time(self):

        log_ids = list(
            TicketEventLog.objects.filter(ticket_id=self.ticket_id).order_by('id').values_list('id', flat=True)
        )
        last_log_index = log_ids.index(self.id) - 1

        try:
            last_log = TicketEventLog.objects.get(id=log_ids[last_log_index])
        except TicketEventLog.DoesNotExist:
            return

        self.deal_time = (self.operate_at - last_log.operate_at).seconds
        self.save()

    @property
    def translated_message(self):
        """message国际化填充"""

        try:
            return _(self.message).format(
                operator=transform_single_username(self.operator),
                name=self.from_state_name,
                detail_message=self.detail_message,
                action=_(self.action).lower(),
            )
        except Exception:
            return _(self.message)

    @classmethod
    def fix_deal_time(cls, *args, **kwargs):
        """为之前的单据添加处理事件"""
        print('\nfix history ticket deal_time')
        try:
            for log in TicketEventLog.objects.all().exclude(message__in=['流程开始', '单据流程结束']).exclude(type='UNSUSPEND'):
                log.update_deal_time()
        except Exception as e:
            print('\nfix history ticket deal_time exception: %s' % e)
