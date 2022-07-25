# 蓝鲸流程服务

![](docs/resource/img/logo_zh.png)
---
[![license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://github.com/TencentBlueKing/bk-itsm/master/LICENSE)
[![Release](https://img.shields.io/badge/release-3.3.30-brightgreen.svg)](https://github.com/TencentBlueKing/bk-itsm/releases)
[![codecov](https://codecov.io/gh/TencentBlueKing/bk-itsm/branch/v2.6.x_develop/graph/badge.svg?token=OMFO8UFA21)](https://codecov.io/gh/TencentBlueKing/bk-itsm)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/TencentBlueKing/bk-itsm/pulls)

[(English Documents Available)](readme_en.md)

流程服务（ITSM），是基于蓝鲸智云体系的上层SaaS应用。通过可自定义设计的流程模块，覆盖IT服务中的不同管理活动或应用场景。帮助企业用户规范内部管理流程，提升沟通及管理效率。

蓝鲸智云流程服务(ITSM)，基于蓝鲸智云整体体系架构设计及开发。为用户提供可视化的流程配置服务，以满足用户的服务管理需求。同时，提供第三方对接能力，供用户可以调度蓝鲸体系中其它平台或服务能力的同时（配置平台，标准运维、ESB等），也能根据用户自身诉求实现与第三方服务的对接，降低沟通成本，提升流转效率。

流程服务后台使用 Python 作为开发语言，使用 Django 开发框架；前端使用 Vue 开发页面，通过前后端分离式的开发模式，在提供美观交互性强的界面的同时，提升整体的开发效率。

## Overview

- [设计理念](docs/overview/design.md)

- [架构设计](docs/overview/architecture.md)

- [代码目录](docs/overview/code_structure.md)

## Feature
ITSM (IT 服务管理)是一套帮助企业对 IT 系统的规划、研发、实施和运营进行有效管理的方法论。ITSM 起源于 ITIL(IT Infrastructure Library，IT 基础架构标准库)，ITIL 是 CCTA(英国国家电脑局)于 1980 年开发的一套 IT 服务管理标准库。ITSM 主要通过以流程为导向，从复杂的 IT 管理活动中梳理出核心流程，比如事件管理、问题管理和配置管理等，并将这些流程规范化、标准化，明确定义各个流程的目标和范围、成本和效益、运营步骤、关键成功因素和绩效指标、有关人员的责权利，以及各个流程之间的关系，致力于为企业提供高质量，低成本，高效率的 IT 服务，进而帮助企业提升自身的管理效率。

蓝鲸智云 ITSM 服务流程管理，是基于蓝鲸智云体系的上层 SaaS 应用。通过可自定义设计的流程模块，覆盖 IT 服务中的不同管理活动或应用场景。帮助企业用户规范内部管理流程，提升沟通及管理效率。

## Getting started  
- [开发环境部署](docs/install/dev_deploy.md)
- [正式环境源码部署](docs/install/source_code_deploy.md)
- [正式环境上传部署](docs/install/upload_pack_deploy.md)
- [V2.6.0 -> V2.6.1升级指南](docs/install/V2_6_0_to_V2_6_1_upgrade_guide.md)

## Usage
- [API使用说明](docs/itsm_bkapi/apidocs/readme.md)
- [权限说明](docs/install/permission_description.md)
- [服务&用户组迁移指南](docs/install/service_migrate_guide.md)
- [企业微信移动端配置说明](docs/install/qy_weixin_config.md)
- [自定义表单渲染规则说明](docs/install/custom_form_config.md)
- [API请求沙箱使用说明](docs/install/api_sandbox_guide.md)
- [ITSM 接入指引](docs/wiki/access.md)

## Version plan
- [版本日志](docs/RELEASE.md)
[(English Documents Available)](docs/RELEASE_EN.md)


## Support
- [源码](https://github.com/TencentBlueKing/bk-itsm)
- [wiki](https://github.com/TencentBlueKing/bk-itsm/wiki)
- [白皮书](https://bk.tencent.com/docs/document/6.0/145/6623)
- [蓝鲸论坛](https://bk.tencent.com/s-mart/community)
- [蓝鲸 DevOps 在线视频教程](https://bk.tencent.com/s-mart/video/)
- 联系我们，加入腾讯蓝鲸运维开发交流群：878501914

## BlueKing Community

- [BK-CMDB](https://github.com/Tencent/bk-cmdb)：蓝鲸配置平台（蓝鲸 CMDB）是一个面向资产及应用的企业级配置管理平台。
- [BK-CI](https://github.com/Tencent/bk-ci)：蓝鲸持续集成平台是一个开源的持续集成和持续交付系统，可以轻松将你的研发流程呈现到你面前。
- [BK-BCS](https://github.com/Tencent/bk-bcs)：蓝鲸容器管理平台是以容器技术为基础，为微服务业务提供编排管理的基础服务平台。
- [BK-PaaS](https://github.com/Tencent/bk-PaaS)：蓝鲸 PaaS 平台是一个开放式的开发平台，让开发者可以方便快捷地创建、开发、部署和管理 SaaS 应用。
- [BK-SOPS](https://github.com/Tencent/bk-sops)：标准运维（SOPS）是通过可视化的图形界面进行任务流程编排和执行的系统，是蓝鲸体系中一款轻量级的调度编排类 SaaS 产品。


## Contributing
如果你有好的意见或建议，欢迎给我们提 Issues 或 Pull Requests，为蓝鲸开源社区贡献力量。关于标准运维分支管理、Issue 以及 PR 规范，
请阅读 [Contributing Guide](docs/CONTRIBUTING.md)。

[腾讯开源激励计划](https://opensource.tencent.com/contribution) 鼓励开发者的参与和贡献，期待你的加入。

## FAQ
[FAQ](docs/wiki/faq.md)


## License
流程服务是基于 MIT 协议， 详细请参考 [LICENSE](LICENSE.txt) 。

