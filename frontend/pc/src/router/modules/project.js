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

const ProjectHome = () => import('../../views/project/index.vue');
const ProjectList = () => import('../../views/project/list.vue');
const ProjectGuide = () => import('../../views/project/guide.vue');
const ProjectTicket = () => import('../../views/project/ticket.vue');
const ProjectService = () => import('../../views/service/index.vue');
const ProjectServiceList = () => import('../../views/service/serviceList.vue');
const ProjectServiceEdit = () => import('../../views/service/editService/index.vue');
const ProjectServiceSla = () => import('../../views/service/sla/index.vue');
const ServiceDirectory = () => import('../../views/service/directory.vue');
const Field = () => import('../../views/project/fields.vue');
const Role = () => import('../../views/project/role.vue');
const Trigger = () => import('../../views/project/trigger.vue');
const Notice = () => import('../../views/project/notice.vue');
const API = () => import('../../views/project/api.vue');
const SlaManage = () => import('../../views/slaManager/slaManager.vue');
const SlaAgreement = () => import('../../views/slaManager/agreement.vue');

const ProjectOperationData = () => import('../../views/operation/index.vue');
const ProjectOperationHome = () => import('../../views/operation/home.vue');
const ProjectOperationService = () => import('../../views/operation/service.vue');

export default [
  {
    path: '/project_list',
    name: 'ProjectList',
    component: ProjectList,
  },

  {
    path: '/project_guide',
    name: 'ProjectGuide',
    component: ProjectGuide,
  },
  {
    path: '/project_empty',
    name: 'ProjectEmpty',
    component: ProjectList,
  },
  {
    path: '/project',
    name: 'projectHome',
    component: ProjectHome,
    children: [
      {
        path: 'ticket',
        name: 'projectTicket',
        component: ProjectTicket,
      },
      // {
      //     path: 'service',
      //     name: 'serviceList',
      //     component: ProjectService
      // },
      {
        path: 'service',
        name: 'projectService',
        component: ProjectService,
        children: [
          {
            path: 'list',
            name: 'projectServiceList',
            component: ProjectServiceList,
          },
          {
            path: ':type(new|edit)/:step(basic|process|setting)',
            name: 'projectServiceEdit',
            component: ProjectServiceEdit,
            props: route => ({
              serviceId: route.query.serviceId,
              type: route.params.type,
              step: route.params.step,
            }),
          },
          {
            path: 'sla/:id',
            name: 'projectServiceSla',
            component: ProjectServiceSla,
          },
        ],
      },
      {
        path: 'service_directory',
        name: 'serviceDirectory',
        component: ServiceDirectory,
      },
      {
        path: 'roles',
        name: 'projectRoles',
        component: Role,
      },
      {
        path: 'trigger',
        name: 'projectTrigger',
        component: Trigger,
      },
      {
        path: 'notice',
        name: 'projectNotice',
        component: Notice,
      },
      {
        path: 'fields',
        name: 'projectFields',
        component: Field,
      },
      {
        path: 'api',
        name: 'projectApi',
        component: API,
      },
      {
        path: 'sla_manage',
        name: 'slaManage',
        component: SlaManage,
      },
      {
        path: 'sla_agreement',
        name: 'slaAgreement',
        component: SlaAgreement,
      },
      {
        path: 'projectOperation',
        name: 'projectAnalysisData',
        component: ProjectOperationData,
        children: [
          {
            path: 'home',
            name: 'projectOperationHome',
            component: ProjectOperationHome,
          },
          {
            path: 'service',
            name: 'projectOperationService',
            component: ProjectOperationService,
          },
        ],
      },
    ],
  },
];
