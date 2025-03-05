# -*- coding: utf-8 -*-
import os
import environ

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# 支持从local.env文件中获取环境变量，方便命令行启动项目
django_env = environ.Env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
environ.Env.read_env(os.path.join(BASE_DIR, os.getenv("ENV_FILE", "local.env")))


def get_type_env(key, default, var_type=str):
    """
    获取环境变量并转为目标类型
    :param key: 变量名
    :param default: 默认值，若获取不到环境变量会默认使用该值
    :param var_type: 环境变量需要转换的类型，不会转 default
    """

    # 支持直接从local.env文件加载变量
    value = django_env.get_value(key, cast=var_type, default=default)
    if value is not None:
        return value

    return default

