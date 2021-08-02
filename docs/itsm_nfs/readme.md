## 升级App服务器的环境和App部署脚本

脚本逻辑：配置nfs、升级app部署脚本

更新效果：企业版执行更新后，会默认配置appo挂载nfs服务器上的saas共享目录，
同时会先备份已有saas部署脚本，用新的部署脚本覆盖，支持在部署saas时自动挂载nfs到
`/data/app/code/USERRES/`目录，最后就可以在itsm中配置`附件存储目录`为该目录

备注：企业版>2.4时，无需更新此脚本，直接配置目录即可

### 1. 可运行的版本号

蓝鲸企业版：2.2.x

### 2. 执行方式

将脚本放到中控机`/data/install/`目录下，然后直接执行

### 3. 验证nfs目录
    
登录appo，查看nfs挂载是否正确

```
[root@rbtnode1 projects]# mount |grep share
192.168.1.19:/data/bkee/public/nfs/saas on /data/bkee/public/paas_agent/share
```

重新部署itsm，然后登录两台appo查看：

```
[root@rbtnode1 projects]# ls /data/bkee/paas_agent/apps/projects/bk_itsm/code/bk_itsm/ -l|grep USERRES
lrwxrwxrwx  1 apps apps    42 7月  31 20:46 USERRES -> /data/bkee/public/paas_agent/share/bk_itsm
```
### 4. 验证itsm的附件存储功能

配置附件存储目录（基础配置->附件存储）为`/data/app/code/USERRES/`，然后进行附件上传和下载测试
