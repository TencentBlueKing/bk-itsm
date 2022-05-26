# -*- coding: utf-8 -*-
from itsm.iadmin.models import SystemSettings
from itsm.monitor.healthz.check.base import checker


@checker(collect_metric="database.status")
def mysql_checker():
    try:
        SystemSettings.objects.count()
    except Exception as e:
        return False, str(e)

    return True, ""
