# 基于蓝鲸SaaS开发框架，微信公众号H5开发指南
## 预先准备
1. 申请微信公众号
    - 公众号AppID/AppSecret, 【“微信公众号 → 开发 → 基本配置 → 公众号开发信息”】
    - 测试可先申请微信公众号测试号：https://mp.weixin.qq.com/debug/cgi-bin/sandboxinfo
2. 申请应用外网域名
    - 建议同时申请https证书，后续可配置为https
3. 配置公众号
    - 网页授权域名配置为应用外网域名【“微信公众号 → 设置 → 公众号设置 → 功能设置”】
    - JS接口安全域名添加应用外网域名【“微信公众号 → 设置 → 公众号设置 → 功能设置”】
## 创建蓝鲸应用
* 基本配置请参考 “蓝鲸智云开发者中心——》新手指南”
## 开发配置
### 获取 framework_weixin_package.tar.gz
> framework_weixin_package.tar.gz 解压
* 确保开发框架版本为1.1.0及以上
    - 将weixin目录复制于工程目录下
    - 将static/weixin的weixin目录复制到工程static目录下
    - 将templates/weixin的weixin目录复制到工程templates目录下
* 修改工程/weixin/core/settings.py配置
    - USE_WEIXIN 为True
    - WEIXIN_APP_ID 为申请的微信公众号的AppID或者企业微信的CorpID
    - WEIXIN_APP_SECRET 为申请的公众号的AppSecret，或者企业微信的应用Secret
    - WEIXIN_APP_EXTERNAL_HOST 为 申请的应用外网域名
### 修改工程配置文件
* 修改conf/default.py文件
```python
# 中间件 （MIDDLEWARE_CLASSES变量）添加
    'weixin.core.middlewares.WeixinAuthenticationMiddleware',
    'weixin.core.middlewares.WeixinLoginMiddleware',
# INSTALLED_APPS 添加
    'weixin.core',
    'weixin',
```
* 修改urls.py文件
```python
# urlpatterns 添加
    url(r'^weixin/login/', include('weixin.core.urls')),
    url(r'^weixin/', include('weixin.urls')),
```
## 蓝鲸应用
* 部署蓝鲸应用
## 运维配置
* 设置企业微信应用的网页授权为`外网域名`
* 设置环境变量`BKAPP_USE_WEIXIN`为`1`
* 设置环境变量`BKAPP_WEIXIN_APP_ID`为企业微信的CorpID
* 设置环境变量`BKAPP_WEIXIN_APP_SECRET`为企业微信应用的Secret
* 需要确保应用服务器能访问到微信API （可以只设置微信API的代理）
    - 微信提供的API 协议均为https
    - 域名为api.weixin.qq.com
* 反向代理，将应用外网域名的部分路径指向内网蓝鲸应用
    - 为了保证安全，必须只反方向代理部分路径
    - 应用正式环境反向代理：/o/{bk_app_id}/weixin/和/o/{bk_app_id}/static/weixin/
    - 应用测试环境反向代理：/t/{bk_app_id}/weixin/和/t/{bk_app_id}/static/weixin/
    - header必需配置X-Forwarded-Host为应用外网域名，Host为蓝鲸内网域名
    - nginx反向代理示例：
```
server {
        listen              80; # http填写80，https填写443 且https还得配置证书
        server_name        paas.external.bking.com; # 填写应用外网域名
        
        # 假设bk_app_id = test_app，且配置应用的正式环境        
        location ^~ /o/test_app/weixin/ {
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Forwarded-Host $http_host;
            proxy_redirect off;
            proxy_read_timeout 180;
            proxy_pass http://paas.bking.com; # 蓝鲸的内网域名，需要dns能解析到，配置host会有问题
        }
        location ^~ /o/test_app/static/weixin/ {
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Forwarded-Host $http_host;
            proxy_redirect off;
            proxy_read_timeout 180;
            proxy_pass http://paas.bking.com; # 蓝鲸的内网域名，需要dns能解析到，配置host可能会有问题
        }
        # 其他不做任何代理，直接返回404即可
        location / {
            return 404;
        }
}
```
## 测试是否OK
* 直接手机微信访问  http://外网域名/o/{bk_app_id}/weixin/ (若https则https://外网域名/o/{bk_app_id}/weixin/)

## 基于微信公众号的移动端开发说明
> 测试OK后，接下来的开发与PC端的开发基本一致

* 微信端CGI请求都得以 /o/{bk_app_id}/weixin/ （测试环境为：/o/{bk_app_id}/weixin/），若Mako模板渲染的页面，可直接使用${WEIXIN_SITE_URL}
* 微信端本地静态文件请求都得以 /o/{bk_app_id}/static/weixin/ （测试环境为：/o/{bk_app_id}/static/weixin/），若Mako模板渲染的页面，可直接使用${WEIXIN_STATIC_URL}
* 若对于不需要微信登录认证的请求，可直接在对应的View函数添加装饰器weixin_login_exempt（from weixin.core.decorators import weixin_login_exempt）
* 微信公众号登录的用户都存储在BkWeixinUser模型（from weixin.core.models import BkWeixinUser）中，即数据库表 bk_weixin_user
* 集成的微信登录默认是静默登录，只能获取用户openid，其他信息需要设置为授权登录，可配置weixin/core/settings.py文件中的WEIXIN_SCOPE 为snsapi_userinfo
* view函数中获取登录的用户方式：request.weixin_user 即为登录的用户的BkWeixinUser对象，具体weixin_user的属性等的可以查看weixin/core/models.py中的BkWeixinUser
