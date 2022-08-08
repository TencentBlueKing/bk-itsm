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
import base64
import importlib
from urllib.parse import urljoin

from blueapps.conf.default_settings import *  # noqa
from blueapps.conf.log import get_logging_config_dict
from blueapps.opentelemetry.utils import inject_logging_trace_info
from django.http import HttpResponseRedirect
from django.urls import reverse

from config import (
    APP_CODE,
    BASE_DIR,
    BK_URL,
    PROJECT_ROOT,
    BK_PAAS_HOST,
    BK_PAAS_INNER_HOST,
    RUN_VER,
)

# 标准运维页面服务地址
SITE_URL_SOPS = "/o/bk_sops/"

# 针对 paas_v3 容器化差异化配置
ENGINE_REGION = os.environ.get("BKPAAS_ENGINE_REGION", "open")
if ENGINE_REGION == "default":
    env_settings = importlib.import_module("adapter.config.sites.%s.env" % "v3")
    for _setting in dir(env_settings):
        if _setting.upper() == _setting:
            locals()[_setting] = getattr(env_settings, _setting)
    SITE_URL_SOPS = "/bk--sops/"

# 请在这里加入你的自定义 APP
INSTALLED_APPS += (
    # 配置项
    "itsm.iadmin",
    # 引擎相关的内容
    "pipeline",
    "pipeline.log",
    "pipeline.engine",
    "pipeline.component_framework",
    "pipeline.variable_framework",
    # "pipeline.contrib.periodic_task",
    "django_signal_valve",
    # itsm
    "itsm.gateway",
    "itsm.role",
    "itsm.pipeline_plugins",
    "itsm.ticket",
    "itsm.service",
    "itsm.project",
    "itsm.workflow",
    "itsm.sla",
    "itsm.ticket_status",
    "itsm.sla_engine",
    "itsm.postman",
    "itsm.misc",
    "itsm.trigger",
    "itsm.task",
    "itsm.openapi",
    "data_migration",
    # 'silk',
    "mptt",
    "apigw_manager.apigw",
    "django_mptt_admin",
    "django_extensions",
    "rest_framework",
    "corsheaders",
    "django_filters",
    # "autofixture",
    # wiki
    "django.contrib.humanize.apps.HumanizeConfig",
    "django_nyt.apps.DjangoNytConfig",
    "sekizai",
    "sorl.thumbnail",
    "simplemde",
    "weixin.core",
    "weixin",
    # 'flower',
    # 'monitors',
    "itsm.monitor",
    "blueapps.opentelemetry.instrument_app",
    "itsm.plugin_service",
)

INSTALLED_APPS = ("itsm.helper",) + INSTALLED_APPS

AUTHENTICATION_BACKENDS += ("itsm.openapi.authentication.backend.CustomUserBackend",)

IS_PAAS_V3 = int(os.getenv("BKPAAS_MAJOR_VERSION", False)) == 3
IS_OPEN_V3 = IS_PAAS_V3 and RUN_VER == "open"

# IAM 开启开关
USE_IAM = True if os.getenv("USE_IAM", "true").lower() == "true" else False
if USE_IAM:
    INSTALLED_APPS += (
        "iam",
        "iam.contrib.iam_migration",
        "itsm.auth_iam",
    )

# 这里是默认的中间件，大部分情况下，不需要改动
# 如果你已经了解每个默认 MIDDLEWARE 的作用，确实需要去掉某些 MIDDLEWARE，或者改动先后顺序，请去掉下面的注释，然后修改
MIDDLEWARE = (
    # 手动关闭服务中间件，需要到admin里设置key='SERVICE_SWITCH'这条数据的value
    "itsm.component.misc_middlewares.HttpsMiddleware",
    "itsm.component.misc_middlewares.ServiceSwitchCheck",
    # api网关接口豁免
    "itsm.component.misc_middlewares.ApiIgnoreCheck",
    "itsm.component.misc_middlewares.WikiIamAuthMiddleware",
    # 微信登录patch中间件
    "weixin.core.middlewares.WeixinProxyPatchMiddleware",
    # 全局request
    "blueapps.middleware.request_provider.RequestProvider",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # "django.contrib.auth.middleware.SessionAuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # 去掉后页面可被任何站点嵌入
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    # 蓝鲸静态资源服务，内部依赖
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # 企业/微信登录中间件
    "blueapps.account.middlewares.RioLoginRequiredMiddleware",
    "weixin.core.middlewares.WeixinAuthenticationMiddleware",
    "weixin.core.middlewares.WeixinLoginMiddleware",
    # 'blueapps.account.middlewares.WeixinLoginRequiredMiddleware',
    "blueapps.account.middlewares.LoginRequiredMiddleware",
    # 'blueapps.middleware.xss.middlewares.CheckXssMiddleware',
    # exception middleware
    "blueapps.core.exceptions.middleware.AppExceptionMiddleware",
    "iam.contrib.django.middlewares.AuthFailedExceptionMiddleware",
    # enable nginx http-auth
    # 'itsm.component.misc_middlewares.NginxAuthProxy',
    "itsm.component.misc_middlewares.InstrumentProfilerMiddleware",
    "apigw_manager.apigw.authentication.ApiGatewayJWTGenericMiddleware",  # JWT 认证
    "apigw_manager.apigw.authentication.ApiGatewayJWTAppMiddleware",  # JWT 透传的应用信息
    "apigw_manager.apigw.authentication.ApiGatewayJWTUserMiddleware",  # JWT 透传的用户信息
)

# 所有环境的日志级别可以在这里配置
# LOG_LEVEL = 'DEBUG'

# STATIC_VERSION_BEGIN
# 静态资源文件(js,css等）在APP上线更新后, 由于浏览器有缓存,
# 可能会造成没更新的情况. 所以在引用静态资源的地方，都把这个加上
# Django 模板中：<script src="/a.js?v={{ STATIC_VERSION }}"></script>
# mako 模板中：<script src="/a.js?v=${ STATIC_VERSION }"></script>
# 如果静态资源修改了以后，上线前改这个版本号即可
# STATIC_VERSION_END
STATIC_VERSION = "LATEST_STATIC_VERSION"

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# ln -s static static_root
# python manage.py collectstatic
STATIC_ROOT = os.path.join(PROJECT_ROOT, "staticfiles/")

# CELERY 开关，使用时请改为 True，修改项目目录下的 Procfile 文件，添加以下两行命令：
# worker: python manage.py celery worker -l info
# beat: python manage.py celery beat -l info
# 不使用时，请修改为 False，并删除项目目录下的 Procfile 文件中 celery 配置
IS_USE_CELERY = True

# CELERY 并发数，默认为 2，可以通过环境变量或者 Procfile 设置
CELERYD_CONCURRENCY = os.getenv("BK_CELERYD_CONCURRENCY", 2)

# CELERY 配置，申明任务的文件路径，即包含有 @task 装饰器的函数文件
CELERY_IMPORTS = (
    "itsm.helper.tasks",
    "itsm.ticket.tasks",
    "itsm.service.tasks",
    "itsm.sla_engine.monitor",
    "itsm.trigger.tasks",
    "itsm.task.tasks",
)

# CELERYD_PREFETCH_MULTIPLIER = 1
# CELERY_ACKS_LATE = True

# load logging settings
LOGGING = get_logging_config_dict(locals())

# 需要添加的 trace 相关信息格式
inject_formatters = ("verbose",)
# 注入到日志配置，会直接在对应 formatter 格式之后添加 trace_format
# 日志中添加trace_id
ENABLE_OTEL_TRACE = True if os.getenv("BKAPP_ENABLE_OTEL_TRACE", "0") == "1" else False
BK_APP_OTEL_INSTRUMENT_DB_API = (
    True if os.getenv("BKAPP_OTEL_INSTRUMENT_DB_API", "0") == "1" else False
)
if ENABLE_OTEL_TRACE:
    trace_format = "[trace_id]: %(otelTraceID)s [span_id]: %(otelSpanID)s [resource.service.name]: %(otelServiceName)s"
    inject_logging_trace_info(LOGGING, inject_formatters, trace_format)

# 初始化管理员列表，列表中的人员将拥有预发布环境和正式环境的管理员权限
# 注意：请在首次提测和上线前修改，之后的修改将不会生效
BKAPP_ITSM_ADMIN = os.environ.get("BKAPP_ITSM_ADMIN", "")
INIT_SUPERUSER = set(
    ["admin"] + [username for username in BKAPP_ITSM_ADMIN.split(",") if username]
)

# BKUI是否使用了history模式
IS_BKUI_HISTORY_MODE = False

# 开启登录弹窗
IS_AJAX_PLAIN_MODE = True

"""
以下为框架代码 请勿修改
"""

if IS_USE_CELERY:
    INSTALLED_APPS = locals().get("INSTALLED_APPS", [])
    INSTALLED_APPS += ("django_celery_beat", "django_celery_results")

    CELERYBEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"
    # 队列划分配置，勿动!
    from pipeline.celery.settings import *  # noqa

    STATSD_HOST = os.environ.get("STATSD_HOST", "localhost")
    STATSD_PORT = os.environ.get("STATSD_PORT", 8125)
    STATSD_PREFIX = os.environ.get("STATSD_PREFIX", None)

# remove disabled apps
if locals().get("DISABLED_APPS"):
    INSTALLED_APPS = locals().get("INSTALLED_APPS", [])
    DISABLED_APPS = locals().get("DISABLED_APPS", [])

    INSTALLED_APPS = [_app for _app in INSTALLED_APPS if _app not in DISABLED_APPS]

    _keys = (
        "AUTHENTICATION_BACKENDS",
        "DATABASE_ROUTERS",
        "FILE_UPLOAD_HANDLERS",
        "MIDDLEWARE",
        "PASSWORD_HASHERS",
        "TEMPLATE_LOADERS",
        "STATICFILES_FINDERS",
        "TEMPLATE_CONTEXT_PROCESSORS",
    )

    import itertools

    for _app, _key in itertools.product(DISABLED_APPS, _keys):
        if locals().get(_key) is None:
            continue
        locals()[_key] = tuple(
            [_item for _item in locals()[_key] if not _item.startswith(_app + ".")]
        )

# ==============================================================================
# Django 项目配置 - i18n
# ==============================================================================
TIME_ZONE = "Asia/Shanghai"
LANGUAGE_CODE = os.environ.get("BKAPP_BACKEND_LANGUAGE", "zh-hans")
SITE_ID = 1
USE_I18N = True
USE_L10N = True

# 设定使用根目录的locale
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

LOCALEURL_USE_ACCEPT_LANGUAGE = True


def _(s):
    return s


LANGUAGES = (
    ("en", _("English")),
    ("zh-cn", _("简体中文")),
)

LANGUAGE_SESSION_KEY = "blueking_language"
LANGUAGE_COOKIE_NAME = "blueking_language"

# ==============================================================================
# REST FRAMEWORK SETTING
# ==============================================================================
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "itsm.component.generics.exception_handler",
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "itsm.component.drf.pagination.CustomPageNumberPagination",
    "PAGE_SIZE": 10,
    # 'DEFAULT_PAGINATION_CLASS': None,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "itsm.component.drf.filters.OrderingFilter",
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
    "NON_FIELD_ERRORS_KEY": "params_error",
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "itsm.component.drf.parsers.ExtraJSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
}

# ==============================================================================
# CACHE SETTINGS
# ==============================================================================
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache",
    },
    # this cache backend will be used by django-debug-panel
    "debug-panel": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache",
    },
}

REDIS_HOST = os.environ.get("BKAPP_REDIS_HOST")
IS_USE_REDIS = REDIS_HOST is not None

# redis cache backend
if IS_USE_REDIS:
    CACHE_BACKEND_TYPE = os.environ.get("CACHE_BACKEND_TYPE", "RedisCache")
    REDIS_PORT = os.environ.get("BKAPP_REDIS_PORT", 6379)
    REDIS_PASSWORD = os.environ.get("BKAPP_REDIS_PASSWORD", "")  # 密码中不能包括敏感字符,例如":"
    REDIS_SERVICE_NAME = os.environ.get("BKAPP_REDIS_SERVICE_NAME", "mymaster")
    REDIS_MODE = os.environ.get("BKAPP_REDIS_MODE", "single")
    REDIS_DB = os.environ.get("BKAPP_REDIS_DB", 0)
    REDIS_SENTINEL_PASSWORD = os.environ.get(
        "BKAPP_REDIS_SENTINEL_PASSWORD", REDIS_PASSWORD
    )
    # 哨兵
    replication_caches = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "{}/{}:{}/{}".format(
                REDIS_SERVICE_NAME, REDIS_HOST, REDIS_PORT, REDIS_DB
            ),
            "OPTIONS": {
                "CLIENT_CLASS": "itsm.component.data.sentinel.SentinelClient",
                "PASSWORD": REDIS_PASSWORD,
                "SENTINEL_PASSWORD": REDIS_SENTINEL_PASSWORD,
            },
        },
    }
    # 单机
    single_caches = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://{}:{}/{}".format(REDIS_HOST, REDIS_PORT, REDIS_DB),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "PASSWORD": REDIS_PASSWORD,
            },
        },
    }
    CACHES_GETTER = {"replication": replication_caches, "single": single_caches}
    CACHES = CACHES_GETTER[REDIS_MODE]

# mysql cache backend
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "django_cache",
        }
    }

CACHES.update(
    {
        "db": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "django_cache",
        },
        "login_db": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "account_cache",
        },
        "dummy": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        },
        "locmem": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        },
    }
)

# ==============================================================================
# Django 项目配置 - 其他
# ==============================================================================
CSRF_COOKIE_PATH = "/"
CSRF_COOKIE_NAME = "bkitsm_csrftoken"
SESSION_COOKIE_NAME = "bkitsm_sessionid"

# Template
MAKO_DIR_NAME = "mako_templates"
# 使用mako模板时，默认打开的过滤器：h(过滤html)
MAKO_DEFAULT_FILTERS = None
MAKO_TEMPLATE_DIR = (
    os.path.join(BASE_DIR, MAKO_DIR_NAME),
    os.path.join(BASE_DIR, "static", "dist"),
)
MAKO_TEMPLATE_MODULE_DIR = os.path.join(
    os.path.dirname(BASE_DIR), "templates_module", APP_CODE
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": (
            os.path.join(BASE_DIR, "static", "assets"),
            os.path.join(BASE_DIR, "templates"),
            os.path.join(BASE_DIR, "static", "weixin"),
        ),
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "blueapps.template.context_processors.blue_settings",
                "common.context_processors.mysetting",
                "blueapps.template.context_processors.blue_settings",
                "sekizai.context_processors.sekizai",
                "weixin.core.context_processors.basic",
            ],
        },
    },
    {
        "BACKEND": "blueapps.template.backends.mako.MakoTemplates",
        "DIRS": MAKO_TEMPLATE_DIR,
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "blueapps.template.context_processors.blue_settings",
                "common.context_processors.mysetting",
                "django.template.context_processors.i18n",
                "sekizai.context_processors.sekizai",
                "weixin.core.context_processors.basic",
            ],
            # mako templates cache, None means not using cache
            "module_directory": MAKO_TEMPLATE_MODULE_DIR,
        },
    },
]

# Django Template Date/Datetime display format
DATETIME_FORMAT = "Y-m-d H:i:s"
DATE_FORMAT = "Y-m-d"

# 默认为false, 为true时,SESSION_COOKIE_AGE对session_id无效
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# NOTE 不要改动，否则，可能会改成和其他app的一样，这样会影响登录
# SESSION_COOKIE_PATH = SITE_URL
# Age of cookie, in seconds (default: 60 * 60 * 24 * 7 * 2  <2 weeks>).
# SESSION_COOKIE_AGE = 60 * 60 * 24 * 1 * 1  # 设置cookie有效期为1小时

MEDIA_ROOT = os.path.join(PROJECT_ROOT, "USERRES")
# MEDIA_URL = '/media/'

# ==============================================================================
# WIKI SETTINGS
# ==============================================================================

# 调整nginx配置，增加media文件路由，不建议用django来托管静态资源
# 如果必须由django来托管，则需要修改wiki的图片渲染模板，在url前加上{{ SITE_URL }}
# 比如：{{ SITE_URL }}{% url 'wiki:images_index' ... %}

# 注意：放到这里不会生效，需要转移到各个环境额配置文件中
# MEDIA_URL = '%smedia/' % SITE_URL

WIKI_MARKDOWN_HTML_WHITELIST = ["center", "style", "div"]

WIKI_MARKDOWN_HTML_ATTRIBUTES = {"*": ["style"]}

WIKI_MARKDOWN_HTML_STYLES = [
    "padding",
    "width",
    "color",
    "float",
    "clear",
    "background",
]

WIKI_ATTACHMENTS_EXTENSIONS = [
    "pdf",
    "doc",
    "odt",
    "docx",
    "txt",
    "pptx",
    "ppt",
    "zip",
    "gz",
    "jpeg",
    "jpg",
    "png",
    "gif",
]

WIKI_ANONYMOUS = True
WIKI_ACCOUNT_HANDLING = True
WIKI_ACCOUNT_SIGNUP_ALLOWED = False
WIKI_ANONYMOUS_WRITE = False
WIKI_ANONYMOUS_CREATE = False

# 每分钟30篇，每小时30*60篇
REVISIONS_PER_MINUTES = 30
REVISIONS_PER_HOUR = REVISIONS_PER_MINUTES * 60

WIKI_EDITOR_INCLUDE_JAVASCRIPT = True

SIMPLEMDE_OPTIONS = {
    "hideIcons": ["guide", "heading"],
    "showIcons": ["heading-2"],
    "promptURLs": True,
    "spellChecker": False,
    "placeholder": "",
    "status": False,
    "autosave": {"enabled": True},
}


# article permission handling
def is_owner_or_readonly(article, user):
    """文章只能作者本人或者超级管理员操作"""

    if user.is_wiki_superuser:
        return True

    return not user.is_anonymous and user == article.owner


WIKI_CAN_DELETE = is_owner_or_readonly
WIKI_CAN_ASSIGN = is_owner_or_readonly
WIKI_ASSIGN_OWNER = is_owner_or_readonly
WIKI_CAN_CHANGE_PERMISSIONS = is_owner_or_readonly
WIKI_CAN_MODERATE = is_owner_or_readonly
WIKI_CAN_ADMIN = is_owner_or_readonly

# ==============================================================================
# 微信端环境变量注入
# ==============================================================================
# 独立部署设置
USE_X_FORWARDED_HOST = True

# check weixin settings
try:
    weixin_conf_module = "weixin.core.settings"
    weixin_module = __import__(weixin_conf_module, globals(), locals(), ["*"])
    for weixin_setting in dir(weixin_module):
        if weixin_setting == weixin_setting.upper():
            locals()[weixin_setting] = getattr(weixin_module, weixin_setting)
except BaseException:
    pass

# ==============================================================================
# 数据存储 配置
# ==============================================================================
if IS_USE_REDIS:
    ITSM_DATA_BACKEND = "itsm.component.data.redis_backend.RedisDataBackend"
    PIPELINE_DATA_BACKEND = "pipeline.engine.core.data.redis_backend.RedisDataBackend"
    PIPELINE_DATA_CANDIDATE_BACKEND = os.getenv(
        "BKAPP_PIPELINE_DATA_CANDIDATE_BACKEND",
        "pipeline.engine.core.data.mysql_backend.MySQLDataBackend",
    )

    PIPELINE_DATA_BACKEND_AUTO_EXPIRE = True
else:
    ITSM_DATA_BACKEND = "itsm.component.data.mysql_backend.MySQLDataBackend"
    PIPELINE_DATA_BACKEND = "pipeline.engine.core.data.mysql_backend.MySQLDataBackend"

# ==============================================================================
# PIPELINE 配置
# ==============================================================================
PIPELINE_END_HANDLER = "itsm.ticket.handlers.pipeline_end_handler"
ENABLE_EXAMPLE_COMPONENTS = True

# ==============================================================================
# RPC 配置
# ==============================================================================
PRC_AUTO_DISCOVER_PATH = [
    "rpc.components",
]

# ==============================================================================
# Trigger 配置
# ==============================================================================
TRIGGER_AUTO_DISCOVER_PATH = [
    "action.components",
]

# ==============================================================================
# SLA 配置
# ==============================================================================
INTERVAL_TICK_PERCENT = 0.01  # SLA任务后台更新频率: 1%

# ==============================================================================
# 环境变量控制
# ==============================================================================
# 业务关联组件参数
IS_BIZ_GROUP = os.environ.get("BKAPP_IS_BIZ_GROUP", None) == "1"  # 是否做业务分组功能
BIZ_GROUP_CONF = {
    # 单关联在业务中对应的字段key
    "biz_property_id": os.environ.get("BKAPP_BIZ_GROUP_RELATED_KEY", "belong_office"),
    # 分组对应的模型ID
    "biz_obj_id": os.environ.get("BKAPP_BIZ_GROUP_MODULE_KEY", "office"),
}
BIZ_GROUP_DESC = os.environ.get("BKAPP_GROUP_DESC", "请选择分组")

# 业务级联组件定义变量
BIZ_GROUP_ENUM = os.environ.get("BKAPP_BIZ_GROUP_ENUM", "")
BIZ_ENUM = os.environ.get("BKAPP_BIZ_ENUM", "")

# 微信应用外网代理链接
OUT_LINK = os.environ.get("BKAPP_OUT_LINK", "https://test.bksaas.com/")

# 企业微信应用信息
WX_QY_AGENTID = os.environ.get("BKAPP_WX_QY_AGENTID", None)
WX_QY_CORPSECRET = os.environ.get("BKAPP_WX_QY_CORPSECRET", None)

# 微信端调试账号
WX_USER = os.environ.get("BKAPP_WX_USER", None)

# 自定义站点title
CUSTOM_TITLE = os.environ.get("BKAPP_CUSTOM_TITLE", None)
# 自定义log
LOG_NAME = os.environ.get("BKAPP_LOG_NAME", None)
# 关闭通知
CLOSE_NOTIFY = os.environ.get("BKAPP_CLOSE_NOTIFY", None)

# CC和JOB的访问地址
BK_CC_HOST = os.environ.get("BK_CC_HOST", "#")
BK_JOB_HOST = os.environ.get("BK_JOB_HOST", "#")

# 适配容器化
USER_MANGE_HOST = os.environ.get("BK_COMPONENT_API_URL", BK_PAAS_HOST)

BK_USER_MANAGE_HOST = os.environ.get("BK_USER_MANAGE_HOST", USER_MANGE_HOST)

BK_USER_MANAGE_WEIXIN_HOST = os.environ.get("BK_USER_MANAGE_WEIXIN_HOST", BK_PAAS_HOST)

LOGIN_URL = BK_URL + "/login/"

# 是否启用短信评价
IS_USE_INVITE_SMS = os.environ.get("IS_USE_INVITE_SMS", None)

# 单据自动评价间隔天数, 大于0表示开启自动评价
AUTO_COMMENT_DAYS = int(os.environ.get("BKAPP_AUTO_COMMENT_DAYS", 3))

try:
    NEED_PROFILE = bool(int(os.environ.get("BKAPP_NEED_PROFILE", False)))
except Exception:
    NEED_PROFILE = False
PROFILE_TEST_PATH = [
    {"path": path, "method": ["GET"]}
    for path in os.environ.get("BKAPP_PROFILE_TEST_PATH", "").split(",")
    if path
]
PROFILE_OUTPUT = [
    output
    for output in os.environ.get("BKAPP_PROFILE_OUTPUT", "file").split(",")
    if output
]
PROFILER = {
    "enable": NEED_PROFILE,
    "output": PROFILE_OUTPUT,
    "file_location": os.path.join(LOGGING.get("log_dir", "/"), "profiles"),
    "request_paths": PROFILE_TEST_PATH,  # 包含就被输出数据
}

# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
# try:
#     import pymysql
#
#     def mysqldb_escape(value, conv_dict):
#         from pymysql.converters import encoders
#
#         vtype = type(value)
#         # note: you could provide a default:
#         # PY2: encoder = encoders.get(vtype, escape_str)
#         # PY3: encoder = encoders.get(vtype, escape_unicode)
#         encoder = encoders.get(vtype)
#         return encoder(value)
#
#     setattr(pymysql, "escape", mysqldb_escape)
#     del pymysql
# except ImportError as e:
#     raise ImportError("PyMySQL is not installed: %s" % e)

# INTERNAL_IPS = ['127.0.0.1']
# PYINSTRUMENT_PROFILE_DIR = 'profiles'

# The name of the class to use to run the test suite
TEST_RUNNER = "itsm.tests.runner.ItsmTestRunner"

# 统一转发前缀
PREFIX_SOPS = ""

# 设置被代理的标准运维插件AJAX请求地址，比如API网关的接口
# 'https://paasee-dev.XX.com/t/bk_sops/apigw/dispatch_plugin_query/'
SOPS_PROXY_URL = os.environ.get(
    "BKAPP_SOPS_PROXY_URL", "{}{}".format(BK_PAAS_INNER_HOST, SITE_URL_SOPS)
)

# 设置被代理的标准运维插件静态资源地址，比如标准运维的site_url或API网关接口
# 'https://paasee-dev.XX.com/t/bk_sops'
SOPS_SITE_URL = os.environ.get(
    "BKAPP_SOPS_SITE_URL", "{}{}".format(BK_PAAS_HOST, SITE_URL_SOPS)
)

# 允许转发的非静态内容路径
SOPS_ALLOW_ACCESS = ["/api/v3/component/", "/api/v3/variable/"]

APIGW_APP_CODE = os.environ.get("BKAPP_APIGW_APP_CODE", "")
APIGW_SECRET_KEY = os.environ.get("BKAPP_APIGW_SECRET_KEY", "")
APIGW_USERNAME = os.environ.get("BKAPP_APIGW_USERNAME", "")


def my_before_proxy_func(request, json_data, request_headers):
    """预留钩子，可修改转发接口的header和body"""
    json_data["app_code"] = APIGW_APP_CODE
    json_data["app_secret"] = APIGW_SECRET_KEY
    json_data["bk_username"] = APIGW_USERNAME


BEFORE_PROXY_FUNC = my_before_proxy_func

BK_API_USE_BKCLOUDS_FIRST = True

DEFAULT_VARIABLE_NAME = "variable_by_name"

# IAM权限中心配置
BK_IAM_SYSTEM_ID = os.getenv("BKAPP_BK_IAM_SYSTEM_ID", APP_CODE)
BK_IAM_SYSTEM_NAME = os.getenv("BKAPP_BK_IAM_SYSTEM_NAME", "ITSM")

# 本地开发需配置环境变量
BK_IAM_INNER_HOST = os.environ.get("BK_IAM_V3_INNER_HOST", None)

# 监控变量
TAM_PROJECT_ID = os.environ.get("TAM_PROJECT_ID", "")

# 是否初始化蓝盾
INIT_DEVOPS_TEMPLATE = os.environ.get("INIT_DEVOPS_TEMPLATE", False)

# 权限中心 SaaS host
BK_IAM_APP_CODE = os.getenv("BK_IAM_V3_APP_CODE", "bk_iam")
BK_IAM_SAAS_HOST = os.environ.get(
    "BK_IAM_V3_SAAS_HOST", urljoin(BK_PAAS_HOST, "/o/{}".format(BK_IAM_APP_CODE))
)

SYSTEM_CALL_USER = "admin"

BK_DESKTOP_URL = os.environ.get("BK_DESKTOP_URL") or BK_PAAS_HOST

BK_IAM_API_PREFIX = SITE_URL + "openapi"
BK_API_USE_TEST_ENV = True if os.environ.get("BK_API_USE_TEST_ENV") == "True" else False

# iam适配容器化
IAM_ESB_PAAS_HOST = os.environ.get("BK_COMPONENT_API_URL", BK_PAAS_INNER_HOST)
BK_IAM_ESB_PAAS_HOST = os.environ.get("BK_IAM_ESB_PAAS_HOST", IAM_ESB_PAAS_HOST)

IAM_INITIAL_FILE = os.environ.get("BKAPP_IAM_INITIAL_FILE", "")

CALLBACK_AES_KEY = "APPROVAL_RESULT"

FRONTEND_URL = os.environ.get("BKAPP_FRONTEND_URL") or os.path.join(
    BK_PAAS_HOST, os.environ.get("BKAPP_ITSM_URL", "o/bk_itsm/")
)

MY_OA_CALLBACK_URL = os.environ.get("MY_OA_CALLBACK_URL", "")

WEIXIN_APP_EXTERNAL_SHARE_HOST = "{}weixin/".format(
    os.environ.get("BKAPP_WEIXIN_APP_EXTERNAL_HOST", FRONTEND_URL)
)
TICKET_NOTIFY_HOST = WEIXIN_APP_EXTERNAL_SHARE_HOST

FILE_CHARSET = "utf-8"
# LANGUAGE_CODE = "zh-hans"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# celery允许接收的数据格式，可以是一个字符串，比如'json'
CELERY_ACCEPT_CONTENT = ["pickle", "json"]
# 异步任务的序列化器，也可以是json
CELERY_TASK_SERIALIZER = "pickle"
# 任务结果的数据格式，也可以是json
CELERY_RESULT_SERIALIZER = "pickle"

DJANGO_CELERY_BEAT_TZ_AWARE = False
timezone = "Asia/Shanghai"

CELERY_TIMEZONE = "Asia/Shanghai"
USE_TZ = False

# 通知消息模版
CONTENT_CREATOR_WITH_TRANSLATION = (
    True
    if os.getenv("CONTENT_CREATOR_WITH_TRANSLATION", "true").lower() == "true"
    else False
)

# 系统api调用账户
SYSTEM_USE_API_ACCOUNT = "admin"

# 蓝盾
DEVOPS_CLIENT_URL = os.environ.get("DEVOPS_CLIENT_URL", "")
DEVOPS_BASE_URL = os.environ.get("DEVOPS_BASE_URL", "")

api_public_key = os.environ.get("APIGW_PUBLIC_KEY", "")
APIGW_PUBLIC_KEY = base64.b64decode(api_public_key)

# show.py 敏感信息处理, 内部白皮书地址，内部登陆地址
BK_IEOD_DOC_URL = os.environ.get("BK_IEOD_DOC_URL", "")
BK_IEOD_LOGIN_URL = os.environ.get("BK_IEOD_LOGIN_URL", "")

# itsm-tapd 网关API地址
ITSM_TAPD_APIGW = os.environ.get("ITSM_TAPD_APIGW", "")
# tapd 项目授权链接
TAPD_OAUTH_URL = os.environ.get("TAPD_OAUTH_URL", "")

# bkchat快速审批
USE_BKCHAT = True if os.getenv("USE_BKCHAT", "true").lower() == "true" else False
if USE_BKCHAT:
    IM_TOKEN = os.environ.get("BKCHAT_IM_TOKEN", "")
    BKCHAT_URL = os.environ.get("BKCHAT_URL", "")
    BKCHAT_APPID = os.environ.get("BKCHAT_APPID", "")
    BKCHAT_APPKEY = os.environ.get("BKCHAT_APPKEY", "")


def redirect_func(request):
    login_page_url = reverse("account:login_page")
    next_url = "{}?refer_url={}".format(login_page_url, request.path)
    return HttpResponseRedirect(next_url)


BLUEAPPS_PAGE_401_RESPONSE_FUNC = redirect_func

try:
    # 自动过单时间，默认为20
    AUTO_APPROVE_TIME = int(os.environ.get("AUTO_APPROVE_TIME", 20))
except Exception:
    AUTO_APPROVE_TIME = 20

OPEN_VOICE_NOTICE = (
    True if os.getenv("BKAPP_OPEN_VOICE_NOTICE", "false").lower() == "true" else False
)

# apigw的配置
BK_APIGW_NAME = os.getenv("BK_APIGW_NAME", "bk-itsm")
# APIGW 访问地址
BK_API_URL_TMPL = os.getenv("BK_API_URL_TMPL")

# 蓝鲸插件授权过滤 APP
PLUGIN_DISTRIBUTOR_NAME = os.getenv("BKAPP_PLUGIN_DISTRIBUTOR_NAME", APP_CODE)
