from django.conf import settings


def get_apigw_url_format():
    """延迟获取 APIGW_URL_FORMAT，避免循环导入问题"""
    return "{}/{{stage}}".format(settings.BK_API_URL_TMPL)


CONCURRENCY_NUMS = 1

PAGE_SIZE = 10
LIMIT = 500
