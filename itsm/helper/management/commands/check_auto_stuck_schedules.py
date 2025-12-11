# -*- coding: utf-8 -*-
"""
检测API节点可能卡住的调度任务

使用方法:
    python manage.py check_auto_stuck_schedules                                      # 默认超时阈值30分钟
    python manage.py check_auto_stuck_schedules --timeout 60                         # 设置超时阈值为60分钟
    python manage.py check_auto_stuck_schedules --fix                                # 检测并尝试修复所有
    python manage.py check_auto_stuck_schedules --output stuck.csv                   # 导出到CSV文件
    python manage.py check_auto_stuck_schedules --schedule_id <schedule_id> --process_id <process_id> # 修复单个调度任务
"""


from django.core.management.base import BaseCommand

from itsm.helper.utils import AutoSchedules


class Command(BaseCommand):
    help = "检测可能卡住的调度任务（AutoStateService轮询型任务）"

    def add_arguments(self, parser):
        parser.add_argument(
            "--timeout",
            type=int,
            default=30,
            help="超时阈值（分钟），超过该时间未调度视为卡住，默认30分钟",
        )
        parser.add_argument(
            "--fix",
            action="store_true",
            help="尝试修复卡住的调度（重置 is_scheduling 锁并重新触发调度）",
        )
        parser.add_argument(
            "--output",
            type=str,
            default="",
            help="导出结果到CSV文件",
        )
        parser.add_argument(
            "--process_id",
            type=str,
            default="",
            help="修复单个工单的进程id",
        )
        parser.add_argument(
            "--schedule_id",
            type=str,
            default="",
            help="修复单个工单的调度id",
        )

    def handle(self, *args, **options):
        timeout_minutes = options["timeout"]
        fix_mode = options["fix"]
        output_file = options["output"]
        process_id = options["process_id"]
        schedule_id = options["schedule_id"]

        self.stdout.write(
            self.style.NOTICE(f"开始检测卡住的调度任务，超时阈值: {timeout_minutes} 分钟")
        )
        if timeout_minutes:
            auto_schedules = AutoSchedules(timeout_minutes)
        else:
            auto_schedules = AutoSchedules()
        
        if process_id and schedule_id:
            # 修复单个工单的调度任务
            result = auto_schedules.fix_one_schedule(schedule_id, process_id)
            if result:
                self.stdout.write(self.style.SUCCESS(f"修复成功: schedule_id={schedule_id}"))
            else:
                self.stdout.write(self.style.ERROR(f"修复失败: schedule_id={schedule_id}"))
            return
            
        stuck_schedules = auto_schedules.find_stuck_schedules()

        if not stuck_schedules:
            self.stdout.write(self.style.SUCCESS("未发现卡住的调度任务"))
            return

        self.stdout.write(
            self.style.WARNING(f"发现 {len(stuck_schedules)} 个可能卡住的调度任务:")
        )

        # 打印结果
        self.print_results(stuck_schedules)

        # 导出到CSV
        if output_file:
            self.export_to_csv(stuck_schedules, output_file)

        # 修复模式
        if fix_mode:
            fixed_count, failed_count = auto_schedules.fix_stuck_schedules(stuck_schedules)
            self.stdout.write(self.style.SUCCESS(f"修复成功: {fixed_count} 个, 修复失败: {failed_count} 个"))

    def print_results(self, stuck_schedules):
        """打印检测结果"""
        self.stdout.write("\n" + "=" * 200)
        self.stdout.write(
            f"{'ticket_id':<15} {'service_id':<12} {'schedule_id':<40} {'process_id':<40} "
            f"{'poll_time':<10} {'is_scheduling':<15} {'minutes_overdue':<18} {'reason'}"
        )
        self.stdout.write("=" * 200)

        for item in stuck_schedules:
            ticket_id = item.get('ticket_id') or '-'
            service_id = item.get('service_id') or '-'
            process_id = item.get('process_id') or '-'
            self.stdout.write(
                f"{str(ticket_id):<15} {str(service_id):<12} {item['schedule_id']:<40} "
                f"{str(process_id):<40} {item['poll_time']:<10} {str(item['is_scheduling']):<15} "
                f"{item['minutes_overdue']:<18} {item['reason']}"
            )

        self.stdout.write("=" * 200 + "\n")

        # 统计 is_scheduling 锁定的数量
        locked_count = sum(1 for item in stuck_schedules if item["is_scheduling"])
        if locked_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"其中 {locked_count} 个调度任务处于 is_scheduling=True 锁定状态"
                )
            )

    def export_to_csv(self, stuck_schedules, output_file):
        """导出结果到CSV文件"""
        import csv

        fieldnames = [
            "ticket_id",
            "service_id",
            "schedule_id",
            "activity_id",
            "process_id",
            "schedule_times",
            "is_scheduling",
            "poll_time",
            "poll_interval",
            "latest_poll_time",
            "next_poll_time",
            "started_time",
            "minutes_overdue",
            "reason",
        ]

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(stuck_schedules)

        self.stdout.write(self.style.SUCCESS(f"结果已导出到: {output_file}"))
        

