# -*- coding: utf-8 -*-


#  eri admin 鉴权
def check_permission_success(request, *args, **kwargs):
    return request.user.is_superuser
