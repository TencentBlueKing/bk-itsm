# -*- coding: utf-8 -*-
from celery.schedules import crontab
from celery.task import periodic_task

from common.log import logger
from itsm.component.constants import PUBLIC_PROJECT_PROJECT_KEY
from itsm.component.utils.lock import share_lock
from itsm.iadmin.models import CustomNotice
from itsm.workflow.models import Notify, settings, Project
from itsm.workflow.utils import init_notify_type_choice


@periodic_task(run_every=(crontab(hour="*/1", minute=0)), ignore_result=True)
@share_lock()
def check_and_update_notify_type():
    choice = init_notify_type_choice()
    # esb 目前的
    esb_notify_set = {item[0] for item in choice}
    # 当前DB 目前的
    current_notify_set = set(Notify.objects.all().values_list("type", flat=True))
    deleted_notify_type_set = current_notify_set - esb_notify_set
    if deleted_notify_type_set:
        logger.info(
            "[check_and_update_notify_type]正在删除相关的通知方式，该通知方式在ESB已经下架 = {}".format(
                deleted_notify_type_set
            )
        )
        # 删除相关的通知方式
        notify_deleted_count = Notify.objects.filter(
            type__in=deleted_notify_type_set
        ).delete()
        logger.info(
            "[check_and_update_notify_type]正在删除相关的通知方式，本次删除成功条数 = {}".format(
                notify_deleted_count
            )
        )
        # 删除相关的通知模板
        custom_notice_deleted_count = CustomNotice.objects.filter(
            notify_type__in=deleted_notify_type_set
        ).delete()
        logger.info(
            "[check_and_update_notify_type]正在删除相关的通知模板，本次删除成功条数 = {}".format(
                custom_notice_deleted_count
            )
        )

    add_notify_set = esb_notify_set - current_notify_set

    if add_notify_set:
        logger.info(
            "[check_and_update_notify_type]正在新增相关的通知方式，该通知方式在ESB是新增的 = {}".format(
                add_notify_set
            )
        )
        for notify_type, notify_name in choice:
            if not settings.OPEN_VOICE_NOTICE:
                if notify_type == "VOICE":
                    continue
            if notify_type in add_notify_set:
                if not Notify.objects.filter(type=notify_type).exists():
                    Notify.objects.create(
                        name="{}通知".format(notify_name), type=notify_type
                    )

    logger.info("开始更新项目通知模板")
    # 更新所有项目的通知方式
    project_keys = Project.objects.filter(is_deleted=False).values_list(
        "key", flat=True
    )
    for project_key in project_keys:
        # 公共项目不参与初始化通知模板
        if project_key == PUBLIC_PROJECT_PROJECT_KEY:
            continue
        CustomNotice.init_project_template(project_key=project_key)
