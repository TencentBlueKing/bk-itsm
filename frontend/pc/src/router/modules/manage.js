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

const Index = () => import('../../views/manage/index.vue');
// const PublicService = () => import('../../views/manage/service.vue')
const PublicFields = () => import('../../views/manage/fields.vue');
const PublicAPI = () => import('../../views/manage/api.vue');
const NotifySetting = () => import('../../views/processManagement/notice/noticeConfigure.vue');
const TaskTpl = () => import('../../views/processManagement/taskTemplate/index.vue');
const SlaPriority = () => import('../../views/slaManager/priority.vue');
// 单据状态管理
const TicketStatus = () => import('../../views/slaManager/ticketStatus.vue');
const GlobalSetting = () => import('../../views/manage/globalSetting.vue');

// const basicModule = () => import('../../views/processManagement/basicModule/index.vue')
// const dataDictionary = () => import('../../views/systemConfig/dataDictionary.vue')

export default [
  {
    path: '/manage',
    name: 'ManageIndex',
    component: Index,
    children: [
      // {
      //     path: 'public_service',
      //     name: 'publicService',
      //     component: PublicService
      // },
      {
        path: 'public_fields',
        name: 'publicFields',
        component: PublicFields,
      },
      {
        path: 'public_api',
        name: 'publicAPI',
        component: PublicAPI,
      },
      {
        path: 'task_tpl',
        name: 'taskTpl',
        component: TaskTpl,
      },
      {
        path: 'notify_setting',
        name: 'notifySetting',
        component: NotifySetting,
      },
      {
        path: 'sla_priority',
        name: 'slaPriority',
        component: SlaPriority,
      },
      {
        path: 'ticket_status',
        name: 'ticketStatus',
        component: TicketStatus,
      },
      {
        path: 'global_setting',
        name: 'globalSetting',
        component: GlobalSetting,
      },
      // {
      //     path: 'basic_module',
      //     name: 'basicModule',
      //     component: basicModule
      // },
      // {
      //     path: 'data_dictionary',
      //     name: 'dataDictionary',
      //     component: dataDictionary
      // }
    ],
  },
];
