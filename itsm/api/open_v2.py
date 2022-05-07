# -*- coding: utf-8 -*-
from itertools import chain

from itsm.openapi.base_service.urls import urlpatterns as base_urlpatterns

# 公共URL配置
urlpatterns = list(chain(base_urlpatterns))
