# 企业版如何支持app自定义部署模板？


1. 给部署脚本打补丁


企业版的appt/appo的部署主要是`paas_agent`的部署，目录结构为：


```
/data/bkee/paas_agent/paas_agent
    |
    etc
    ├── build
    │   ├── docker
    │   │   ├── build
    │   │   ├── builder     [patch]
    │   │   ├── pre_starter [patch]
    │   │   ├── saas
    │   │   │   ├── builder     [patch]
    │   │   │   ├── buildsaas
    │   │   │   ├── pre_starter [patch]
    │   │   │   └── starter
    │   │   └── starter
    │   ├── packages
    │   │   └── requirements.txt
    │   └── virtualenv
    │       ├── build
    │       └── saas
    │           └── buildsaas
    ├── nginx
    │   └── paasagent.conf
    ├── paas_agent_config.yaml -> /data/bkee/etc/paas_agent_config.yaml
    └── templates
        ├── docker
        │   ├── supervisord.conf
        │   └── uwsgi.ini
        └── virtualenv
            ├── supervisord.conf
            └── uwsgi.ini
    
```

对于企业版`python`应用，我们主要关注`docker`和`docker/saaas`下的配置：build/builder/starter这三个文件，具体功能如下：

- build：    设置NFS、启动容器运行builder
- builder：  安装yum依赖(yum.txt)、安装python包依赖(requirements.txt)，然后调用starter
- starter：  数据库初始化，启动supervisord，托管uwsgi/celery进程

执行顺序为：build->builder->starter，supervisord的配置文件是paas_agent程序渲染出来的，但是我们又不想修改paas_agent本身，所以我们
需要覆盖默认的conf下的supervisord.conf文件，同时需要提取环境变量到自己的配置文件中：

这里我们选择在最后启动supervisor前加一段逻辑，我们将自己的逻辑写入到`pre_starter`前，并修改`docker/builder`和`docker/saas/builder`，
先调用`pre_starter`，然后调用`starter`：

```
 # 切换到apps用户
 chown -R apps:apps ${APP_CONTAINER_PATH}

 # add pre_starter hook
 [ -f /build/pre_starter ] && su -m apps -c "/build/pre_starter"
 
 su -m apps -c "/build/starter"
```

最后，我们将`support-files/pre_builder`拷贝到`docker`和`docker/saas`目录下



2. 在app根目录下提供自己的`support-files`

我们需要提供自己的`supervisord.con`和`uwsgi.ini`配置文件，其中<APP_CODE>和<ENV>会被实际的app_code和环境变量替换，我们也可以定义其他
执行命令，比如多启动几个celery worker等
