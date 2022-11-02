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

import { createRouter, createWebHashHistory } from 'vue-router'
const Home = () => import(/* webpackChunkName: "home" */ './views/home/index.vue')
const TodoList = () => import(/* webpackChunkName: "home" */ './views/home/todoList.vue')
const ApprovalList = () => import(/* webpackChunkName: "home" */ './views/home/approvalList.vue')
const ApplicationList = () => import(/* webpackChunkName: "home" */ './views/home/applicationList.vue')
const AttentionList = () => import(/* webpackChunkName: "home" */ './views/home/attentionList.vue')
const Ticket = () => import(/* webpackChunkName: "ticket" */ './views/ticket/index.vue')
const CreateTicket = () => import(/* webpackChunkName: "ticket" */ './views/ticket/createTicket.vue')
const Service = () => import(/* webpackChunkName: "ticket" */ './views/service/index.vue')

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
      children: [
        {
          path: '',
          name: 'homeDefault',
          component: TodoList,
          alias: 'home/todo'
        },
        {
          path: 'home/todo',
          name: 'todo',
          component: TodoList
        },
        {
          path: 'home/approval',
          name: 'approval',
          component: ApprovalList
        },
        {
          path: 'home/application',
          name: 'application',
          component: ApplicationList
        },
        {
          path: 'home/attention',
          name: 'attention',
          component: AttentionList
        }
      ]
    },
    {
      path: '/ticket/:id',
      name: 'ticket',
      component: Ticket,
      meta: {
        title: '单据详情'
      }
    },
    {
      path: '/ticket/create',
      name: 'createTicket',
      component: CreateTicket,
      meta: {
        title: '创建单据'
      }
    },
    {
      path: '/service',
      name: 'service',
      component: Service,
      meta: {
        title: '服务提单'
      }
    }
  ]
})

router.beforeEach((to) => {
  document.title = to.meta.title || window.LOG_NAME
})

export default router
