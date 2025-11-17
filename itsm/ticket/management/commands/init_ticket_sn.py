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
import datetime
import logging

from django.core.management.base import BaseCommand
from django.conf import settings

from itsm.component.constants import PREFIX_KEY
from itsm.component.utils.basic import now

logger = logging.getLogger("root")


class Command(BaseCommand):
    help = "初始化工单序号Redis Key，根据今天已有的工单数量设置初始值"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制删除现有的 Redis key 并重新初始化（用于测试）',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅检查 Redis key 是否存在，不进行初始化（用于测试）',
        )

    def handle(self, *args, **kwargs):
        """
        检查并初始化各个服务类型的 Redis SN key
        如果 key 不存在，则根据今天已有的工单数量设置初始值，并设置过期时间为第二天 0 点
        """
        from itsm.ticket.models import Ticket
        from itsm.component.data import exists
        
        # 获取参数
        force_delete = kwargs.get('force', False)
        dry_run = kwargs.get('dry_run', False)

        service_types = ["event", "request", "change", "question"]
        prefix_mapping = {
            "event": "INC",
            "request": "REQ",
            "change": "CRQ",
            "question": "PBI",
        }

        now_time = now()
        today_start = datetime.datetime(
            year=now_time.year, month=now_time.month, day=now_time.day
        )
        tomorrow = today_start + datetime.timedelta(days=1)

        self.stdout.write(
            self.style.SUCCESS(
                f"[init_ticket_sn] 开始检查工单序号 Redis Key (当前时间: "
                f"{now_time.strftime('%Y-%m-%d %H:%M:%S')}, 时区: {now_time.tzinfo})"
            )
        )

        for service_type in service_types:
            key = PREFIX_KEY + service_type
            prefix = prefix_mapping[service_type]

            if force_delete and exists(key):
                settings.REDIS_INST.delete(key)
                self.stdout.write(
                    self.style.WARNING(
                        f"[init_ticket_sn] 强制模式已启用，将删除现有的 Redis key '{key}'"
                    )
                )
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f"[init_ticket_sn] 干跑模式已启用，将检查 Redis key '{key}' 是否存在，不进行初始化"
                    )
                )
                if exists(key):
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"[init_ticket_sn] {service_type}: Redis key '{key}' 已存在"
                        )
                    )
                today_sn_prefix = prefix + now_time.strftime("%Y%m%d")
                today_ticket_count = Ticket.objects.filter(
                    service_type=service_type,
                    sn__startswith=today_sn_prefix,
                    create_at__gte=today_start,
                    create_at__lt=tomorrow,
                ).count()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[init_ticket_sn] {service_type}: 初始化成功\n"
                        f"工单前缀: {prefix}\n"
                        f"今日已有工单数: {today_ticket_count}\n"
                        f"Redis Key: '{key}'\n"
                        f"初始值: {today_ticket_count}\n"
                        f"过期时间: {tomorrow.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"-----------------------------------------------------\n"
                    )
                )
                continue

            # 检查 Redis key 是否存在
            if exists(key):
                self.stdout.write(
                    self.style.WARNING(
                        f"[init_ticket_sn] {service_type} 的 Redis Key '{key}' 已存在，跳过初始化"
                    )
                )
                continue

            # 统计今天已有的工单数量
            today_sn_prefix = prefix + now_time.strftime("%Y%m%d")
            today_ticket_count = Ticket.objects.filter(
                service_type=service_type,
                sn__startswith=today_sn_prefix,
                create_at__gte=today_start,
                create_at__lt=tomorrow,
            ).count()

            # 设置 Redis key 的初始值和过期时间
            when = tomorrow  # 第二天 0:00:00
            
            try:
                # 直接设置 Redis key 的值和过期时间            
                settings.REDIS_INST.set(key, today_ticket_count)
                settings.REDIS_INST.expireat(key, when)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[init_ticket_sn] {service_type}: 初始化成功 - "
                        f"今日已有工单数: {today_ticket_count}, "
                        f"Redis Key: '{key}', "
                        f"初始值: {today_ticket_count}, "
                        f"过期时间: {when.strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"[init_ticket_sn] {service_type}: 初始化失败 - {str(e)}"
                    )
                )
                logger.error(f"[init_ticket_sn] {service_type} 初始化失败: {e}")

        self.stdout.write(
            self.style.SUCCESS("[init_ticket_sn] 工单序号 Redis Key 检查完成")
        )
