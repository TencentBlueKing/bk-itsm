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
 * @desc router 配置
 * @example 路由组件名统一首字母大写
 */

import Vue from 'vue';
import Router from 'vue-router';
import bus from '../utils/bus';
import routerModules from './modules/index.js';

// 首页
const Home = () => import('../views/home/index.vue');

// 打印页面
const printOrder = () => import('../views/commonComponent/printOrder/index.vue');
// 工单处理页面
const TicketDetail = () => import('../views/ticket/details/index.vue');
// 工单处理页面-iframe
const TicketDetailIframe = () => import('../views/ticket/detailsIframe/index.vue');
const TicketApprovalIframe = () => import('../views/ticket/approvalIframe/index.vue');
// 流程设计
const process = () => import('../views/processManagement/processDesign/index.vue');
const ProcessHome = () => import('../views/processManagement/processDesign/processHome/ProcessHome.vue');
// 流程编辑
const processEdit = () => import('../views/processManagement/processDesign/processEdit/ProcessEdit.vue');
// 流程版本
const flowVersion = () => import('../views/processManagement/version');
// 基础模型
const basicModule = () => import('../views/processManagement/basicModule');
// 数据字典
const dataDictionary = () => import('../views/systemConfig/dataDictionary.vue');
// 系统日志
const systemLogs = () => import('../views/systemConfig/systemLogs.vue');
// 403页面
const limitAccess = () => import('../views/403.vue');
const exception = () => import('../components/common/exception');

// renderview 测试
const RenderViewTest = () => import('../views/test/RenderViewTest.vue');

// 新的路由导航组件
const TicketManage = () => import('../views/ticket/TicketManage.vue');
const MyTicket = () => import('../views/ticket/MyTicket.vue');
const AllTicket = () => import('../views/ticket/allTicket/index.vue');
const CreateTicket = () => import('../views/ticket/CreateTicket.vue');

// 运营数据
const OperationData = () => import('../views/operation/index.vue');
const OperationHome = () => import('../views/operation/home.vue');
const OperationService = () => import('../views/operation/service.vue');

// 服务新路由
// const Service = () => import('../views/service/index.vue')
// const ServiceList = () => import('../views/service/ServiceList.vue')
// const EditService = () => import('../views/service/editService/index.vue')

Vue.use(Router);

// from webpack 2.4
// https://github.com/webpack/webpack/releases/tag/v2.4.0

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  // 工单打印
  {
    path: '/printOrder',
    name: 'PrintOrder',
    component: printOrder,
  },
  // 服务目录
  // {
  //     path: '/service',
  //     name: 'Service',
  //     component: Service,
  //     meta: {
  //         admin: true
  //     },
  //     children: [
  //         {
  //             path: 'list',
  //             name: 'ServiceList',
  //             component: ServiceList,
  //             meta: {
  //                 admin: true
  //             }
  //         },
  //         {
  //             path: ':type(new|edit)/:step(basic|process|setting)/',
  //             name: 'ServiceEdit',
  //             component: EditService,
  //             props: (route) => ({
  //                 serviceId: route.query.serviceId,
  //                 type: route.params.type,
  //                 step: route.params.step
  //             }),
  //             meta: {
  //                 admin: true
  //             }
  //         }
  //     ]
  // },
  // 流程设计
  {
    path: '/process',
    name: 'ProcessDesign',
    component: process,
    children: [
      {
        path: 'home',
        name: 'ProcessHome',
        component: ProcessHome,
        meta: {
          admin: true,
        },
      },
      {
        path: ':type(new|edit)/:step/',
        name: 'ProcessEdit',
        component: processEdit,
        props: route => ({
          processId: route.query.processId,
          type: route.params.type,
          step: route.params.step,
        }),
        meta: {
          admin: true,
        },
      },
    ],
    meta: {
      admin: true,
    },
  },
  // 流程版本
  {
    path: '/flowVersion',
    name: 'FlowVersion',
    component: flowVersion,
    meta: {
      admin: true,
    },
  },
  // 基础模型
  {
    path: '/basicModule',
    name: 'BasicModule',
    component: basicModule,
    meta: {
      admin: true,
    },
  },
  // 流程管理 -- 数据字典
  {
    path: '/dataDictionary',
    name: 'DataDictionary',
    component: dataDictionary,
    meta: {
      admin: true,
    },
  },
  // 系统配置 -- 接口日志
  {
    path: '/systemLogs',
    name: 'SystemLogs',
    component: systemLogs,
    meta: {
      admin: true,
    },
  },
  // 无权限访问页面
  {
    path: '/limitAccess',
    name: 'LimitAccess',
    component: limitAccess,
  },
  // 应用正在部署
  {
    path: '/exception',
    name: 'Exception',
    component: exception,
  },
  {
    path: '/customFormTest',
    name: 'CustomFormTest',
    component: RenderViewTest,
  },
  // 工单管理
  {
    path: '/ticket',
    name: 'TicketManage',
    component: TicketManage,
    children: [
      {
        path: 'my/:type(todo|approval|created|attention|history)', // 我的工单
        name: 'MyTicket',
        component: MyTicket,
      },
      {
        path: 'all', // 所有工单
        name: 'AllTicket',
        component: AllTicket,
      },
      {
        path: 'create', // 提交工单
        name: 'CreateTicket',
        component: CreateTicket,
      },
      {
        path: 'detail', // 工单详情
        name: 'TicketDetail',
        component: TicketDetail,
      },
      {
        path: 'approval-iframe', // 审批工单-iframe
        name: 'TicketApprovalIframe',
        component: TicketApprovalIframe,
        meta: {
          iframe: true,
        },
      },
      {
        path: 'detail-iframe', // 工单详情-iframe
        name: 'TicketDetailIframe',
        component: TicketDetailIframe,
        meta: {
          iframe: true,
        },
      },
    ],
  },
  // 运营数据
  {
    path: '/operation/data',
    name: 'operationAnalysis',
    component: OperationData,
    children: [
      {
        path: '/',
        name: 'OperationHome',
        component: OperationHome,
      },
      {
        path: 'service/:id',
        name: 'OperationService',
        component: OperationService,
      },
    ],
  },
  { // 重定向到新路由-兼容已使用该路由的系统
    path: '/newBill',
    redirect: '/ticket/create',
  },
  ...routerModules,
];

const router = new Router({
  mode: 'hash',
  routes,
});

router.beforeEach((to, from, next) => {
  bus.$on('api-error:user-permission-denied', () => {
    next({ path: '/limitAccess' });
  });
  bus.$on('api-error:application-deployed', () => {
    next({ path: '/exception' });
  });
  next();
});

export default router;
