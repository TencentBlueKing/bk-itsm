# 附件下载路径安全修复

本次只修改附件下载的文件系统边界和 misc 下载目标，不迁移配置或附件，不移除存储后端。

- open/v3 原有存储配置保持原位置，包含 BKREPO_ENDPOINT_URL 等变量。
- RepoStorage、CephStorage、上传逻辑、SYS_FILE_PATH 配置页面及目录复制逻辑保持原样。
- 下载使用文件系统存储时，按 SYS_FILE_PATH 构造受限读取对象；BKRepo/Ceph 继续使用原适配器和原有路径前缀。
- misc 下载打开与检查相同的文件，修正原先打开目录路径的问题。

## NFS 目录要求

SYS_FILE_PATH 必须是非空、非 `/` 的绝对附件目录。空配置不能确定安全边界，下载将失败；管理员须先配置目录。目录内历史绝对路径和相对路径继续支持。

读取逐级使用目录描述符和 O_NOFOLLOW，拒绝父目录段、目录外路径、目录内符号链接及非普通文件，避免检查后替换链接绕过保护。配置的挂载根本身可以是链接，根内链接均拒绝，升级前需核对历史链接文件。管理员应限制其他进程对目录的写权限。

## 验证范围

隔离测试执行实际下载函数体，使用临时目录验证正常文件、历史路径、路径穿越、链接与链接替换、特殊文件、后端选择、对象存储路径前缀及 misc 实际下载目标。无需数据库或存储服务：

```sh
DJANGO_SETTINGS_MODULE=itsm.tests.storage_settings PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -c /dev/null --confcutdir=itsm/tests itsm/tests/test_attachment_storage.py -q
```

不把上述测试等同于真实 Django/ORM/IAM、NFS 挂载、BKRepo/Ceph 集成验证；上线前需抽样验证。原有资源权限检查保留，本次不增加跨流程附件归属模型。
