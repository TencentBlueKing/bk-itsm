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

import json
from threading import Thread

import requests

from common.log import logger
from common.sub_string import sub_string


WEB_HOOK_URL = "http://in.qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}"


class Announcement(Thread):
    def __init__(self, web_hook_id, content, mentioned_list, chat_ids):
        super(Announcement, self).__init__()
        self.web_hook_id = web_hook_id
        self.content = content
        self.mentioned_list = mentioned_list
        self.status_code = 200
        self.result = None
        self.chat_ids = chat_ids

    def run(self):

        try:
            logger.info("[ROBOT] call robot begin")
            session = requests.session()
            content = self.content.encode()
            while len(content) > 0:
                sub_content, index = sub_string(content, 5120)
                data = {
                    "msgtype": "text",
                    "text": {
                        "content": sub_content.decode(),
                        "mentioned_list": self.mentioned_list,
                    },
                }
                if self.chat_ids is not None:
                    data["chatid"] = self.chat_ids
                resp = session.post(
                    url=WEB_HOOK_URL.format(self.web_hook_id),
                    data=json.dumps(data),
                    verify=False,
                )
                self.status_code = resp.status_code
                self.result = resp.json()
                if self.status_code != 200 or self.result["errcode"] != 0:
                    raise Exception(self.result)
                if index == -1:
                    break
                else:
                    content = content[index:]
            logger.info(
                "[ROBOT] call robot end, status_code is {}, result is {}".format(
                    self.status_code, self.result
                )
            )
        except Exception as err:
            logger.error(
                "[ROBOT] call robot {} error, message is {}".format(
                    self.web_hook_id, err
                )
            )
            self.status_code = 500
            self.result = {"errcode": 500, "errmsg": err}

    def get_error_msg(self):
        return self.result["errmsg"]

    def is_success(self):
        return self.status_code == 200 and self.result["errcode"] == 0


if __name__ == "__main__":
    tt = """
## 3.5.29
- feature
  - 任务节点样式调整，增加步骤填写
- improvement
  - 修改任务详情页开始按钮图标大小
- bugfix
  - 修复 创建模块 插件服务模版名称中带有下划线导致解析失败问题

## 3.5.28
- bugfix
  - 变量KEY长度计算校验时，不考虑${}字符
  - 公共流程模板编辑页面，请求类型变量列表不需要带 project_id  - 修复业务下没有空闲机模块时 IP 选择器加载静态数据 500 的问题
  - 修复解析变 MAKO 变量值时没有捕获所有可能异常的问题
  - 修复各插件中业务选择下拉框被勾选成变量时相关联动请求失效的问题
  - 量引用次数统计正则回溯问题修复
  - 修复旧版 IP 选择器解析的值不是 IP 的问题
  - 任务节点执行失败后重试、跳过操作按钮绑定错误修复
  - 下拉框变量无法编辑问题修复
  - 添加收藏弹框，修改bk-search-selector组件下拉框层递问题
  - 表格tag变量引用计数统计支持变量后拼接其他变量或者字符串
  - 表格tag单元格输入框焦点丢失问题修复
- improvement
  - 变量KEY长度扩展到50个字符
  - 兼容应用部署到跨域环境下的小窗登录
  - 输入框tag增加密码模式显示模式
  - 全局变量被节点引用数据，增加表格、combine内使用等多级嵌套的情况统计
  - 节点详情页节点日志设置单行最大长度限制
- feature
  - 项目全局变量下,ip选择器静态拓扑支持跨页全选
  - 表格 tag 支持同一行单元格间的事件交互
  - 节点详情页面的执行历史记录添加节点日志展示
  - 任务执行页面支持展示流程模板数据 pipeline_tree  - 新增人员分组注册接口

## 3.5.27
- bugfix
  - 任务列表默认查询不到公共流程创建的任务问题修复
  - 任务填写页面 下拉列表，表格拓宽异常问题
  - 公共流程创建任务页面返回按钮链接不正确修复
  - 子流程更新表单类型变更后勾选状态未清空问题修复
- improvement
  - 全局变量被节点引用数据，增加表格、combine内使用等多级嵌套的情况统计
  - 代码编辑器在各系统平台下EOL统一设置为


## 3.5.26

- feature
  - 表格 tag 支持同一行单元格间的事件交互
- bugfix 
  - 修复全局变量中存在对 IP 选择器的引用链时变量值解析错误的问题
  - 管理员视图周期任务执行历史跳转链接不正确修复
  - 节点配置输入、输出参数勾选状态可能未被清空的问题修复
  - 选择插件搜索结果后节点名称展示异常修复
  - 由公共流程创建的周期任务执行记录拉取任务列表时请求参数错误修复
- improvement
  - tag 组件支持获取当表单项勾选为全局变量时的实际 value 值
  - 模板编辑名称错误时提示方式优化
  - 计算画布偏移量方法优化，解决模板画布边界异常问题
  - 节点输入参数勾选变量复用规则调整

## 3.5.25
- improvement 
  - 表格内tagtextarea查看模式文本水平居中
  - tagselect增加是否显示清除表单值icon  - 修改节点树父节点不添加选中态  任务节点添加选中态
  - 点击未执行节点打开任务详情面板
  - 修改参数面板添加关闭按钮  修改按钮位置
  - 修改插件开发字体图标
  - 去掉 pipeline.models.Snapshot 相同数据引用逻辑，不再根据数据md5值进行判断，直接创建新数据
  - 优化任务统计查询接口的查询速度
  - 节点详情页修复导包错误和提醒和功能块重叠
  - 开发者对于下拉框远程数据源可配置自定义转换函数，对应于REMOTE_SOURCE_DATA_TRANSFORM_FUNCTION配置变量
  - 人员选择器查询接口host由变量传入
  - 导入模板时支持导入带执行方案的数据
  - 自动编排算法优化，修复并行网关换行后可能重叠的为题，优化节点横坐标计算策略
  - 创建任务参数填写页面拓宽
  - 节点配置侧滑组件操作按钮固定在底部
  - 对外提供的 API 移除对用户存在性的校验
  - 资源筛选变量增加开区个数和开区ip列表字段，改用`,`作为列表拼接分隔符
  - JOB-执行作业插件优化(IP数量校验，加日志)- bugfix
  - 弹窗组件遮罩不显示问题修复
  - 关闭节点配置面板后全局变量icon小红点提示一直显示修复
  - 由任务跳转到模板编辑时，返回按钮无法回到模板列表页面问题修复
  - 轻应用编辑弹窗tooltip层级问题修复
  - 子流程模板变量类型更新后勾选的输入参数取值不正确修复
  - 修复队列划分后没有修改 supervisor 配置导致周期任务和 api 任务不执行的问题
  - 分支条件编辑时光标跳转问题修复
  - 修复 BKAPP_API_JWT_EXEMPT 环境变量存在时 API 从 HTTP 头部中获取不到 APP CODE 的问题
  - 修复分发本地文件插件无权限时没有生成权限申请链接的问题
  - 修复调用 api 时不传递用户名会导致系统 500 的问题
  - IP选择器保存筛选、排除条件后，编辑状态下不显示问题修复
  - 修复ip选择器筛选条件引用输入框变量失效问题
- feature
  - 新增人员分组选择器变量
  - 提取消息通知插件内函数 get_notify_receivers 到 gcloud/utils/cmdb.py 中
  - mako 渲染上下文支持使用 datetime, re, hashlib random 模块
  - tagDatatable支持表格分页展示
  - 新增 日期 和 时间 两个变量.  - 节点详情页给非admin用户添加执行节点日志查看面板
  - 新增对只显示在特定业务上插件的支持，由系统管理员进行设置
  - 新增 tagTime 组件
  - tagDatatime 组件支持配置日期展示类型
  - 模板编辑、任务执行画布页面任务节点增加插件生命周期标记
  - 新增 集群模块选择器 变量.  - 添加资源配置方案模型和导入迁移工具
  - 节点详情页面给非管理员用户添加原始值功能
  - 画布导出图片按钮和小地图样式调整
  - API接口增强，get_task_status支持获取失败节点的异常数据
"""
    t = Announcement("caf235f1-f7fe-4e1b-adde-2c3ba324ae57", tt)
    t.start()
    t.join()
    print(t.is_success())
