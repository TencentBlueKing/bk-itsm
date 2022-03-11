# 正式环境源码部署

## Fork 源代码到自己的仓库  
通过 Fork 源代码到自己的仓库，可以进行二次开发和定制。建议公共特性开发和 bug 修复通过 Pull requests 及时提交到官方仓库。如果不需要进行二次开发，请下载相关smart包进行部署。

## 源码部署分为两种情况

## 第一种情况，你未部署了Smart包版本的ITSM：

在这种情况下，您可以直接进行源码部署，但是处于Paas对于蓝鲸应用APP_CODE的要求，你将无法使用bk_itsm的APP_CODE,  这将导致权限中心，流程服务等第三方对接ITSM出现问题。如果你的场景不需要流程服务和权限中心，并且是admin身份使用，那你大可进行源码部署。否则，改方式会有风险。因为对于普通用户而言，使用ITSM需要到权限中心申请权限，权限中心的审批又是走的ITSM。这样的回路将无法完成。因为权限中心使用的是ESB对接的ITSM。

### 第二种情况，你已经部署了Smart包版本的ITSM:

 在这种情况下，你依然无法直接通过源码部署的方式，取代正在运行的Smart包版本的ITSM。在这样的场景下，会出现两套ITSM同时运行的情况。一套是默认的ITSM,  权限中心依赖的是此ITSM。一个是你自己源码部署的ITSM。也就是，当普通用户需要使用你源码部署的ITSM时，需要到权限中心申请权限，然后相关的人在Smart包版本的ITSM上进行审批。除了权限中心与流程服务无法调用到你源码部署的ITSM之外，其他功能不会收到影响。

如果使用这种方式部署ITSM, 需要将系统内所有的bk_itsm 替换为 你源码部署的 app_code， 比如 `bk-itsm`。同时将项目下的`support-files/iam/initial.json`文件中所有的`bk_itsm`替换为你源码部署的`app_code`。

下面是具体的源码部署步骤:


## 打包并收集前端静态资源
1）安装依赖包  
进入 `frontend/weixin`，执行以下命令安装。如果您需要使用移动端的话，则需要在` frontend/weixin`执行相同的操作。

```bash
npm install
```

2）打包前端资源
在 frontend/目录下，继续执行以下命令打包前端静态资源

```bash
npm run build
```

3）将打包好的前端文件提交到github上。

## 创建应用  

前往你部署的蓝鲸PaaS平台，在"开发者中心"点击"应用创建"，填写需要的参数，注意代码仓库填写你的 Github 仓库地址，账号和密码。注意，由于官方已经存在一个名为"流程服务"的应用，你只能填写不一样的应用名称和应用 ID，如"流程服务定制版"、bk-itsm-ce。
后续文档中bk-itsm-ce都代表你创建的应用的应用ID，如和文档示例不一致，请以你的应用ID为准。


## 修改配置  
前往你部署的蓝鲸PaaS平台，在"开发者中心"点击"新手指南"，按照文档指引进行操作，主要是数据库配置修改和设置APP_ID, APP_TOKEN, BK_PAAS_HOST 等变量。


## 开通 API 白名单
手动在你部署的蓝鲸社区版的中控机执行如下命令，开通流程服务访问蓝鲸PaaS平台API网关的白名单，以便标准插件可以正常调用 API。
```bash
source /data/install/utils.fc
add_app_token bk-sops-ce "$(_app_token bk-itsm-ce)" "流程服务定制版"
```
注意把"流程服务定制版" 和 bk-itsm-ce 改为你创建的应用名称和应用 ID。


# 准备 redis 资源
在你部署的蓝鲸社区版的运行环境找一台机器，新建一个 redis 服务账号和密码。也可以公用部署蓝鲸社区版时已经有的 redis 服务。


## 部署应用  
前往你部署的蓝鲸PaaS平台，在"开发者中心"点击"我的应用"，找到你刚才创建的应用，点击"应用部署"，请勾选"启用celery"和"启用周期性任务"。这样你就可以在测试环境访问你新建的"流程服务定制版"应用了。


## 修改环境变量配置
```bash
BKAPP_REDIS_HOST="{BKAPP_REDIS_HOST}"
BKAPP_REDIS_PORT="{BKAPP_REDIS_PORT}"
BKAPP_REDIS_PASSWORD="{BKAPP_REDIS_PASSWORD}"
BKAPP_REDIS_MODE=single
BKAPP_REDIS_DB=1
```


## 重新部署应用
由于环境变量只有在项目启动时才会加载，所以修改后必须重新部署才会生效，请进入开发者中心，找到你创建的应用，点击"发布部署"，请勾选"启用celery"和"启用周期性任务"。


## 替换官方流程服务 SaaS  
按照前面的步骤操作后，你已经在蓝鲸社区版 PaaS 上创建了一个ITSM的定制版本，如果功能测试正常（请主要测试审批等核心功能)

1) 如果需要保留官方流程服务应用的所有数据，你需要修改数据库配置  
获取你部署的蓝鲸官方流程服务应用的数据库名、数据库账号密码，默认测试环境是 bk_itsm_bkt，正式环境是 bk_itsm。修改代码的 config/stag.py 和 config/prod.py，分别修改为官方流程服务应用的数据库信息。
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 默认用mysql
        'NAME': 'bk_itsm',                     # 数据库名 (测试环境写 bk_sops_bkt)
        'USER': '',                            # 官方流程服务应用数据库user
        'PASSWORD': '',                        # 官方流程服务应用数据库password
        'HOST': '',                   		   # 官方流程服务应用数据库HOST
        'PORT': '',                            # 官方流程服务应用数据库PORT
    },
}

```

2) 由于流程服务接入了蓝鲸PaaS平台API网关，你需要修改流程服务网关配置
请参考[API网关替换方式](https://docs.bk.tencent.com/bk_osed/guide.html#SaaS)文档，把流程服务 API 转发到你的定制版本的接口。