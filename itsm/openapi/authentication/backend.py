# -*- coding: utf-8 -*-


from apigw_manager.apigw.authentication import UserModelBackend
from django.contrib.auth import get_user_model
from django.conf import settings

from common.log import logger

adapter_api = settings.ADAPTER_API


class CustomUserBackend(UserModelBackend):
    def check_user(self, bk_username):
        try:
            users = adapter_api.get_batch_users([bk_username], None)
        except Exception as e:
            logger.info(
                "[CustomUserBackend] 同步失败，用户管理接口请求异常, bk_username={}, error={}".format(
                    bk_username, str(e)
                )
            )
            return False
        if len(users) > 0:
            return True
        return False

    def authenticate(self, request, api_name, bk_username, verified, **credentials):
        if not verified:
            return self.make_anonymous_user(bk_username=bk_username)
        try:
            return self.user_maker(bk_username)
        except Exception:
            logger.info(
                "[CustomUserBackend] 检测到当前用户不存在，开始同步用户 , bk_username={}".format(
                    bk_username
                )
            )
            if not self.check_user(bk_username):
                logger.info(
                    "[CustomUserBackend] 同步失败，当前用户在用户管理中未搜索到或请求异常, bk_username={}".format(
                        bk_username
                    )
                )
            User = get_user_model()
            user = User.objects.create(username=bk_username, nickname=bk_username)
            return user
