# -*- coding: utf-8 -*-

# ==============================================================================
# 加载环境差异化配置
# ==============================================================================

import importlib

from django.conf import settings

bkchat_config = importlib.import_module(
    "platform_config.{}.bkchat.config".format(settings.RUN_VER)
)
moa_config = importlib.import_module(
    "platform_config.{}.moa.config".format(settings.RUN_VER)
)


BaseBkchatConfig = bkchat_config.BaseBkchatConfig
BaseMoaConfig = moa_config.BaseMoaConfig


class BaseTicket(BaseMoaConfig, BaseBkchatConfig):
    pass
