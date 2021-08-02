# coding: utf-8
# !/usr/bin/env python

import argparse
import json
import re
import time

import requests


# silice insecure warning when login unverified ssl certificates
# from requests.packages.urllib3.exceptions import InsecureRequestWarning
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 全局session
session = requests.Session()

# 全局参数
LOGIN_TOKEN_NAME = "bklogin_csrftoken"
PAAS_TOKEN_NAME = "bk_csrftoken"

# 异常定义


class BasicException(Exception):
    """异常"""

    pass


class LoginException(BasicException):
    """登录异常"""

    pass


class DeployException(BasicException):
    """部署异常"""

    pass


class CsrfException(BasicException):
    """csrftoken获取异常"""

    pass


def is_status_ok(resp):
    return resp.status_code == 200


def is_domain_valid(dial_url):
    """校验domain有效性"""

    print("check if {} is valid to access".format(dial_url))

    try:
        # 关闭重定向开关，否则拿到的是302目标页面的响应，状态码为200
        resp = requests.get(dial_url, allow_redirects=False, verify=False)
        print("{}({})".format(dial_url, resp.status_code))

        # 登录重定向
        if resp.status_code == 302:
            return True

    except Exception as e:
        print(e)
        return False

    return False


def get_csrftoken(url, token_name):
    """通过GET请求获取csrftoken"""

    resp = session.get(url, verify=False)

    print(url, resp.status_code, resp.cookies.get(token_name))

    token = resp.cookies.get(token_name)

    if not is_status_ok(resp) or token is None:
        raise CsrfException("get {} from {} failed({}):{}".format(token_name, url, resp.status_code, resp.text))

    return token


def auto_login_paas(paas_domain, username, password):
    """通过用户名和密码自动登录paas_domain"""

    # 获取login的csrftoken
    login_url = "{}/login/".format(paas_domain)
    csrftoken = get_csrftoken(login_url, LOGIN_TOKEN_NAME)

    # 自动登录
    login_data = {"csrfmiddlewaretoken": csrftoken, "username": username, "password": password}

    print("login {} with params: \n{}".format(login_url, json.dumps(login_data, indent=2)))
    # add Referer to fix 403 error in https
    """
    https://stackoverflow.com/questions/13567507/passing-csrftoken-with-python-requests
    https://security.stackexchange.com/questions/96114/why-is-referer-checking-needed-for-django-to-prevent-csrf
    https://docs.djangoproject.com/en/1.8/ref/csrf/#how-it-works
    https://code.djangoproject.com/ticket/16870

    In addition, for HTTPS requests, strict referer checking is done by CsrfViewMiddleware.
    This is necessary to address a Man-In-The-Middle attack that is possible under HTTPS when using a session
    independent nonce, due to the fact that HTTP ‘Set-Cookie’ headers are (unfortunately) accepted by clients
    that are talking to a site under HTTPS. (Referer checking is not done for HTTP requests because the presence of
    the Referer header is not reliable enough under HTTP.)
    """
    # Django's CSRF protection uses referer header checking in addition to
    # checking a hidden form field against a cookie
    resp = session.post(login_url, data=login_data, headers={"Referer": login_url})

    if is_status_ok(resp) and username in resp.text:
        print("login {} success.".format(paas_domain))
        return True

    raise LoginException("login {} failed({}): {}.".format(paas_domain, resp.status_code, resp.text))


def start_deploy_app_task(paas_domain, appid, env, is_use_celery=True, is_use_celery_beat=True):
    """
        自动部署app
        参数: 是否需要celery，需要：checked，不需要则不传
        返回：{
            "result": True/False,
            "event_id": 任务id,
            "message": 错误信息
        }
    """

    # 获取paas的csrftoken
    app_info_url = "{}/app/status/{}/".format(paas_domain, appid)
    csrftoken = get_csrftoken(app_info_url, PAAS_TOKEN_NAME)

    # 启动部署任务
    print("prepare to deploy {} to {}".format(appid, env))
    deploy_app_url = "{}/release/{}/{}/".format(paas_domain, env, appid)

    deploy_param = {}
    # deploy_param = {
    #     "csrfmiddlewaretoken": csrftoken,
    # }

    if is_use_celery:
        deploy_param.update(is_use_celery="checked")

    if is_use_celery_beat:
        deploy_param.update(is_use_celery_beat="checked")

    resp = session.post(deploy_app_url, data=deploy_param, headers={"X-CSRFToken": csrftoken, "Referer": app_info_url})

    # 启动部署任务接口调用失败
    if not is_status_ok(resp):
        raise DeployException("start deploy {} to {} failed({}):{}".format(appid, env, resp.status_code, resp.text))

    # 接口调用成功
    try:
        deploy_data = resp.json()
        if not deploy_data.get("result", False):
            raise DeployException("start deploy {} to {} failed:{}".format(appid, env, deploy_data.get("msg")))

        print(
            "start deploy {} to {} success:{}, just wait for a moment to access it".format(
                appid, env, deploy_data.get("event_id")
            )
        )
        return deploy_data.get("event_id")
    except ValueError as e:
        print(resp.text)
        raise DeployException("start deploy {} to {} exception:{}".format(appid, env, str(e),))


def poll_deploy_task(paas_domain, appid, event_id):
    """
    轮询部署任务
        参数: event_id：任务id
        返回：{
            "result": 1/2, 1：部署成功, 2：部署中
            "data": "日志页面",
        }
    """

    def print_log(res):
        """打印日志"""
        try:
            for line in res.get("data").split("\n"):
                if not re.findall(r"[\d+\.\d+\.\d+\.\d+]", line):
                    continue
                print("%s" % line)
        except BaseException:
            print("waiting app to deploy over.")
            pass

    task_result_url = "{}/release/get_app_poll_task/{}/?event_id={}".format(paas_domain, appid, event_id)

    # 5min
    retry = 60
    while retry > 0:
        resp = session.get(task_result_url)
        resp_data = resp.json()
        # 部署成功
        if resp_data.get("data").get("status") == 1:
            print("deploy {} to {} successfully, enjoy it!".format(appid, paas_domain))
            break

        print_log(resp_data)
        retry -= 1
        time.sleep(5)
    else:
        print("deploy {} to {} timeout failed!".format(appid, paas_domain))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="login and deploy bk paas app")
    parser.add_argument("app", help="appid in paas developer center")
    parser.add_argument("-e", "--env", choices=["test", "online"], default="test", help="deploy to appo/appt")
    parser.add_argument("-u", "--username", type=str, help="paas username", required=True)
    parser.add_argument("-p", "--password", help="paas user's password", required=True)
    parser.add_argument(
        "-d", "--domain", help="bk paas domain, such as: http://paasee-test.o.qcloud.com:80", required=True
    )
    args = parser.parse_args()

    APP_ID, ENV, USERNAME, PASSWORD, PAAS_DOMAIN = args.app, args.env, args.username, args.password, args.domain

    # validate and format PAAS_DOMAIN
    if not re.match(r"^(http|https):", PAAS_DOMAIN):
        raise TypeError("<{domain}> is not valid, do you mean <http[s]://{domain}> ?".format(domain=PAAS_DOMAIN))

    if PAAS_DOMAIN.endswith("/"):
        PAAS_DOMAIN = PAAS_DOMAIN[:-1]

    print(
        """
        ===========================
        APP_ID:         {},
        ENV:            {},
        USERNAME:       {},
        PAAS_DOMAIN:    {}
        ===========================
    """.format(
            APP_ID, ENV, USERNAME, PAAS_DOMAIN
        )
    )

    # 环境校验
    assert is_domain_valid(args.domain)

    # try:
    # 自动登录paas
    auto_login_paas(PAAS_DOMAIN, USERNAME, PASSWORD)

    # 自动部署app
    event_id = start_deploy_app_task(PAAS_DOMAIN, APP_ID, ENV)

    # 轮询部署任务
    poll_deploy_task(PAAS_DOMAIN, APP_ID, event_id)

    # except BasicException as e:
    #     print str(e)
    #     sys.exit(1)
