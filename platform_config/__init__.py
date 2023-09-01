# -*- coding: utf-8 -*-

# ==============================================================================
# 加载环境差异化配置
# ==============================================================================

import importlib

from django.conf import settings

from itsm.component.bkchat.config import BaseBkchatConfig

moa_config = importlib.import_module(
    "platform_config.{}.moa.config".format(settings.RUN_VER)
)

BaseMoaConfig = moa_config.BaseMoaConfig


class BaseTicket(BaseMoaConfig, BaseBkchatConfig):
    pass
