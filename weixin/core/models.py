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
from django.utils import timezone


class BkWeixinUserManager(models.Manager):
    def create_user(self, openid, **extra_fields):
        now = timezone.now()
        if not openid:
            raise ValueError('The given openid must be set')
        user = self.model(openid=openid, date_joined=now, **extra_fields)
        user.save()
        return user

    def get_update_or_create_user(self, openid, **extra_fields):
        """
        获取用户，无则创建，有则更新
        """
        try:
            user = self.get(openid=openid)
            update_fields = ['nickname', 'gender', 'country', 'city', 'province', 'avatar_url',
                             'mobile', 'qr_code', 'email', 'userid']
            for field in update_fields:
                field_value = extra_fields.get(field) or ''
                if field_value:
                    setattr(user, field, field_value)
            user.save()
        except self.model.DoesNotExist:
            user = self.create_user(openid, **extra_fields)
        return user


class BkWeixinUser(models.Model):
    """微信公众号用户"""
    openid = models.CharField("微信用户应用唯一标识", max_length=128, null=True)
    userid = models.CharField("企业微信用户应用唯一标识", max_length=128, null=True)
    nickname = models.CharField("昵称", max_length=127, blank=True)
    gender = models.CharField("性别", max_length=15, blank=True)
    country = models.CharField("国家", max_length=63, blank=True)
    province = models.CharField("省份", max_length=63, blank=True)
    city = models.CharField("城市", max_length=63, blank=True)
    avatar_url = models.CharField("头像", max_length=255, blank=True)

    # 企业微信
    mobile = models.CharField("手机号", max_length=11, blank=True)
    qr_code = models.CharField("二维码链接", max_length=128, blank=True)
    email = models.CharField("邮箱", max_length=128, blank=True)
    date_joined = models.DateTimeField("加入时间", default=timezone.now)

    class Meta:
        unique_together = ('openid', 'userid')
        db_table = 'bk_weixin_user'
        verbose_name = "微信用户"
        verbose_name_plural = "微信用户"

    objects = BkWeixinUserManager()

    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True
