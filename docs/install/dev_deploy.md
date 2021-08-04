# 开发环境后台部署

## 部署蓝鲸社区版
流程服务 SaaS 的登录鉴权依赖于蓝鲸智云PaaS平台，业务信息需要从蓝鲸智云配置平台提供的接口获取，所以你需要部署蓝鲸PaaS平台和蓝鲸配置平台，作为开发联调环境。

1）如果你只需要定制开发流程服务，不需要改动蓝鲸PaaS和蓝鲸配置平台的源码，建议你直接从官方下载蓝鲸智云社区版完整包进行。
- [下载网址](https://bk.tencent.com/download/)
- [部署指南](https://docs.bk.tencent.com/bkce_install_guide/)
- [产品论坛](https://bk.tencent.com/s-mart/community)
- QQ交流群:495299374

2）如果你希望使用蓝鲸所有开源产品，进行定制开发，你可以部署开源的蓝鲸智云PaaS平台和蓝鲸智云配置平台。
- [蓝鲸智云PaaS平台](https://github.com/Tencent/bk-PaaS)  
- [蓝鲸智云配置平台](https://github.com/Tencent/bk-cmdb)  

部署方法请参考各个开源产品的相关文档，在蓝鲸智云PaaS平台部署完成后，你还需要上传部署流程服务SaaS并开通应用免登录态验证白名单。
你可以[点击这里](https://github.com/Tencent/bk-sops/releases)下载流程服务Release版本，然后前往蓝鲸PaaS平台的"开发者中心"->"S-mart应用"上传部署新应用。
你可以参考蓝鲸PaaS平台的"开发者中心"->"API网关"->"使用指南"->"API调用说明"页面中"用户认证"文档，添加默认流程服务APP_ID即bk_sops到应用免登录态验证白名单。


## 准备本地 rabbitmq 资源  
在本地安装 rabbitmq，并启动 rabbitmq-server，服务监听的端口保持默认（5672）。


## 准备本地 redis 资源  
在本地安装 redis，并启动 redis-server，服务监听的端口保持默认（6379）。


## 准备本地 mysql  
在本地安装 mysql，并启动 mysql-server，服务监听的端口保持默认（3306）。


## 安装 python 和包
itsm 流程服务所需要的python 版本为 Python3
通过 git 拉取源代码到工程目录后，并进入目录下运行 pip 命令安装 python 包。

```bash
pip install -r requirements.txt
```

## 配置本地环境变量和数据库

1) 设置环境变量  
设置环境变量的目的是让项目运行时能正确获取以下变量的值：

有二种方式设置本地开发需要的环境变量，一是手动设置，即执行如下命令

```bash

export BK_PAAS_HOST="{BK_PAAS_HOST}"
export APP_TOKEN="{APP_TOKEN}"
export APP_ID=bk_itsm
export BKAPP_REDIS_HOST="{BKAPP_REDIS_HOST}"
export BKAPP_REDIS_PORT="{BKAPP_REDIS_PORT}"
export BKAPP_REDIS_PASSWORD="{BKAPP_REDIS_PASSWORD}"
export BKAPP_IAM_INITIAL_FILE="dev"   
```


第二种方式，你可以直接修改项目的 settings 配置，先修改 `config/__init__.py` ，设置项目的基础信息

```python
APP_ID = 'bk_itsm'
APP_TOKEN = '{APP_TOKEN}'
BK_PAAS_HOST = '{BK_PAAS_HOST}'
```

然后修改 config/default.py ，替换Redis的配置
```python
import os
IS_USE_REDIS = True

# redis cache backend
if IS_USE_REDIS:
    CACHE_BACKEND_TYPE = os.environ.get("CACHE_BACKEND_TYPE", "RedisCache")
    REDIS_PORT = os.environ.get("BKAPP_REDIS_PORT", 6379)
    REDIS_PASSWORD = os.environ.get("BKAPP_REDIS_PASSWORD", "")  # 密码中不能包括敏感字符,例如":"
    REDIS_SERVICE_NAME = os.environ.get("BKAPP_REDIS_SERVICE_NAME", "mymaster")
    REDIS_MODE = os.environ.get("BKAPP_REDIS_MODE", "single")
    REDIS_DB = os.environ.get("BKAPP_REDIS_DB", 0)
    REDIS_SENTINEL_PASSWORD = os.environ.get("BKAPP_REDIS_SENTINEL_PASSWORD", REDIS_PASSWORD)
```

2) 在 config 文件夹下新增配置文件 local_settings.py，设置本地开发用的数据库信息。

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "bk_itsm",
        "USER": "", 
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": "3306",
    },
}

```

## 创建并初始化数据库  

1) 在 mysql 中创建名为 bk_sops 的数据库
```sql
CREATE DATABASE `bk_itsm` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
```

2) 在工程目录下执行以下命令初始化数据库
```bash
python manage.py migrate
python manage.py createcachetable django_cache
```

## 打包并收集前端静态资源

1）安装依赖包  
进入 frontend/pc/，执行以下命令安装
```bash
npm install
```

2）本地打包
在 frontend/desktop/ 目录下，继续执行以下命令打包前端静态资源
```bash
npm run build 
```

## 配置本地 hosts  
windows: 在 C:\Windows\System32\drivers\etc\host 文件中添加“127.0.0.1 dev.{BK_PAAS_HOST}”。  
mac: 执行 “sudo vim /etc/hosts”，添加“127.0.0.1 dev.{BK_PAAS_HOST}”。


## 启动进程
```bash
python manage.py celery worker -l info
python manage.py celery beat -l info
python manage.py runserver 8000
```

## 访问页面  
使用浏览器开发 http://dev.{BK_PAAS_HOST}:8000/ 访问应用。
