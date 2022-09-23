/*
 * Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 * BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
 *
 * License for BK-ITSM 蓝鲸流程服务:
 * --------------------------------------------------------------------
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
 * LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
 * NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
 */

/**
 * 顶部主导航和侧边栏导航配置
 *
 * 侧边导航的子导航 prefix 字段是为了处理不规范路由页面的导航是否展示和选中态
 * 例如提单页面、工单处理页面需要收纳到 工单管理 -> 全局视图下，则需要把这两个页面的路径前缀添加到 prefix 字段下
 * 导航组件在做选中态匹配时优先级为：path 字段、prefix 字段
 */

import i18n from '@/i18n/index.js';

const ROUTE_LIST = [
  {
    name: i18n.t('m["服务台"]'),
    id: 'home',
    path: '/',
  },
  {
    name: i18n.t('m["我的单据"]'),
    id: 'workbench',
    path: '/workbench/ticket/todo',
    subRouters: [
      {
        name: i18n.t('m[\'我的待办\']'),
        id: 'myTodoTicket',
        icon: 'bk-itsm-icon icon-order-process',
        path: '/workbench/ticket/todo',
      },
      {
        name: i18n.t('m[\'待我审批\']'),
        id: 'myApprovalTicket',
        icon: 'bk-itsm-icon icon-ticket_time',
        path: '/workbench/ticket/approval',
      },
      {
        name: i18n.t('m[\'我发起的\']'),
        id: 'myCreatedTicket',
        icon: 'bk-itsm-icon icon-ticket_plus',
        path: '/workbench/ticket/created',
      },
      {
        name: i18n.t('m[\'我关注的\']'),
        id: 'myAttentionTicket',
        icon: 'bk-itsm-icon icon-ticket_star',
        path: '/workbench/ticket/attention',
      },
      {
        name: i18n.t('m[\'所有单据\']'),
        id: 'allUserTicket',
        icon: 'bk-itsm-icon icon-ticket_4',
        path: '/workbench/ticket/all',
      },
    ],
  },
  {
    name: i18n.t('m["项目"]'),
    id: 'project',
    path: '/project/service/list',
    subRouters: [
      {
        name: i18n.t('m["服务"]'),
        abbrName: 'Ser.',
        id: 'service',
        subRouters: [
          // {
          //   name: i18n.t('m["单据"]'),
          //   id: 'projectTicket',
          //   icon: 'bk-itsm-icon icon-ticket_4',
          //   path: '/project/ticket',
          //   prefix: ['/ticket/detail', '/ticket/create'],
          // },
          {
            name: i18n.t('m["服务"]'),
            id: 'projectServiceList',
            icon: 'bk-itsm-icon icon-it-new-sevice',
            path: '/project/service/list',
            prefix: ['/project/service/'],
          },
          // {
          //     name: i18n.t(`m["服务目录"]`),
          //     id: 'serviceDirectory',
          //     icon: 'bk-itsm-icon icon-ticket_2',
          //     path: '/project/service_directory'
          // }
        ],
      },
      {
        name: i18n.t('m["元素"]'),
        abbrName: 'Ele.',
        id: 'element',
        subRouters: [
          {
            name: 'API',
            id: 'projectApi',
            icon: 'bk-itsm-icon icon-api-3',
            path: '/project/api',
          },
          {
            name: i18n.t('m["字段"]'),
            id: 'projectFields',
            icon: 'bk-itsm-icon icon-aphabet_t',
            path: '/project/fields',
          },
        ],
      },
      {
        name: 'SLA',
        id: 'sla',
        abbrName: 'SLA',
        subRouters: [
          {
            name: i18n.t('m["协议"]'),
            id: 'slaAgreement',
            icon: 'bk-itsm-icon icon-sla',
            path: '/project/sla_agreement',
          },
          {
            name: i18n.t('m["模式"]'),
            id: 'slaManage',
            icon: 'bk-itsm-icon icon-sla',
            path: '/project/sla_manage',
          },
          // {
          //     name: i18n.t(`m["单据状态管理"]`),
          //     id: 'slaTicketStatus',
          //     path: 'project/ticketStatus'
          // }
        ],
      },
      {
        name: i18n.t('m["管理"]'),
        abbrName: 'Man',
        id: 'projectManage',
        subRouters: [
          {
            name: i18n.t('m["触发器"]'),
            id: 'projectTrigger',
            icon: 'bk-itsm-icon icon-slide',
            path: '/project/trigger',
          },
          {
            name: i18n.t('m["通知模板"]'),
            id: 'projectNotice',
            icon: 'bk-itsm-icon icon-icon-notice-new',
            path: '/project/notice',
          },
          {
            name: i18n.t('m["自定义角色组"]'),
            id: 'projectRoles',
            icon: 'bk-itsm-icon icon-itsm-icon-two-zero',
            path: '/project/roles',
          },
        ],
      },
      // 2.6.0 等权限校验后显示
      {
        name: i18n.t('m["分析"]'),
        abbrName: 'Ana',
        id: 'analysis',
        subRouters: [
          {
            name: i18n.t('m["运营分析"]'),
            id: 'projectOperationHome',
            icon: 'bk-itsm-icon icon-operational-data',
            path: '/project/projectOperation/home',
            prefix: ['/project/projectOperation/service'],
          },
        ],
      },
    ],
  },
  {
    name: i18n.t('m["运营分析"]'),
    id: 'operationAnalysis',
    icon: 'bk-itsm-icon icon-operational-data',
    path: '/operation/data',
  },
  {
    name: i18n.t('m["平台管理"]'),
    id: 'manage',
    path: '/manage/public_fields',
    subRouters: [
      {
        name: i18n.t('m["公共字段"]'),
        id: 'publicFields',
        icon: 'bk-itsm-icon icon-public_fields',
        path: '/manage/public_fields',
      },
      {
        name: i18n.t('m["公共API"]'),
        id: 'publicAPI',
        icon: 'bk-itsm-icon icon-api-3',
        path: '/manage/public_api',
      },
      {
        name: i18n.t('m["任务模板"]'),
        id: 'taskTpl',
        icon: 'bk-itsm-icon icon-itsm-icon-file',
        path: '/manage/task_tpl',
      },
      {
        name: i18n.t('m["通知配置"]'),
        id: 'notifySetting',
        icon: 'bk-itsm-icon icon-itsm-icon-three-eight',
        path: '/manage/notify_setting',
      },
      {
        name: i18n.t('m["优先级"]'),
        id: 'slaPriority',
        icon: 'bk-itsm-icon icon-sla',
        path: '/manage/sla_priority',
      },
      {
        name: i18n.t('m["单据状态"]'),
        id: 'ticketStatus',
        icon: 'bk-itsm-icon icon-sla',
        path: '/manage/ticket_status',
      },
      {
        name: i18n.t('m["全局配置"]'),
        id: 'globalSetting',
        icon: 'bk-itsm-icon icon-pc_setting',
        path: '/manage/global_setting',
      },
      // {
      //     name: i18n.t(`m["基础模型"]`),
      //     id: 'basicModule',
      //     icon: 'bk-itsm-icon icon-itsm-icon-tasks',
      //     path: '/manage/basic_module'
      // },
      // {
      //     name: i18n.t(`m["数据字典"]`),
      //     id: 'dataDictionary',
      //     icon: 'bk-itsm-icon icon-itsm-icon-open-folder',
      //     path: '/manage/data_dictionary'
      // }
    ],
  },
];

export default ROUTE_LIST;
