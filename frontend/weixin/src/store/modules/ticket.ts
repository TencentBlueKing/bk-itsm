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

// import { Store } from 'vuex'
import $api from '../../apis'
import { IResponse } from '../../typings/api'

interface ICounts {
  todo: number,
  approval: number,
  created: number
}
export interface ITicketstate {
  counts: ICounts,
  countLoading: boolean
}

type TTicketType = 'todo' | 'approval' | 'created'

const state: ITicketstate = {
  counts: {
    todo: 0,
    approval: 0,
    created: 0
  },
  countLoading: true
}
const ticket = {
  namespaced: true,
  state,
  mutations: {
    setCounts(state: ITicketstate, payload: { type: TTicketType, val: number }) {
      state.counts[payload.type] = payload.val
    },
    setCountLoading(state: ITicketstate, val: boolean) {
      state.countLoading = val
    }
  },
  actions: {
    getTickets(context: any, payload: any): Promise<IResponse> {
      return $api.get('ticket/receipts/', { params: payload.params })
    },
    // 单据审批
    approvalTicket(context: any, payload: any) {
	  return $api.get('ticket/receipts/', { params: payload.params })
    },
    // 获取单据数量（待办、审批）
    getTicketsCount(context: any) {
      context.commit('setCountLoading', true)
      return $api.get('ticket/receipts/total_count/').then((response) => {
        context.commit('setCounts', { type: 'approval', val: response.data.my_approval })
        context.commit('setCounts', { type: 'todo', val: response.data.my_todo })
        context.commit('setCounts', { type: 'created', val: response.data.my_created })
        context.commit('setCountLoading', false)
      })
    },
    // 批量审批单据
    batchApproval(context: any, payload: any) {
      return $api.post('ticket/receipts/batch_approval/', payload)
    },
    // 撤单
    withdraw(context: any, payload: any): Promise<IResponse> {
      return $api.post(`ticket/receipts/${payload.id}/withdraw/`)
    },
    // 催办
    supervise(context: any, payload: any): Promise<IResponse> {
      return $api.post(`ticket/receipts/${payload.id}/supervise/`)
    },
    // 关注
    addFollower(context: any, payload: any): Promise<IResponse> {
      return $api.post(`ticket/receipts/${payload.id}/add_follower/`, payload)
    },
    // 提交
    proceed(context: any, payload: any): Promise<IResponse> {
      return $api.post(`/ticket/receipts/${payload.id}/proceed/`, payload.params)
    },
    // 认领、转单、分派
    operate(context: any, payload: any): Promise<IResponse> {
      return $api.post(`/ticket/receipts/${payload.id}/operate/`, payload.params)
    },
    // 获取节点状态列表
    getNodeList(context: any, payload: any): Promise<IResponse> {
      return $api.get(`ticket/receipts/${payload.id}/states/`, { params: payload })
    },
    // 单据详情
    getTicketDetail(context: any, payload: any): Promise<IResponse> {
      return $api.get(`ticket/receipts/${payload.id}/`, { params: payload })
    },
    // 获取任务列表
    getTaskList(context: any, payload: any): Promise<IResponse> {
      return $api.get('task/tasks/', { params: payload })
    },
    // 获取任务记录
    getTicketLog(context: any, payload: any): Promise<IResponse> {
      return $api.get('tasks/receipts/', { params: payload })
    },
    // 节点配置 - 基本信息接口
    // 角色关联
    getUser(context: any, payload: any): Promise<IResponse> {
      return $api.get('role/types/', { params: payload })
    },
    // 处理人列表
    getSecondUser(context: any, payload: any): Promise<IResponse> {
      return $api.get('role/users/', { params: payload })
    },
    // 组织架构
    getTreeInfo(): Promise<IResponse> {
      return $api.get('gateway/usermanage/get_departments/')
    },
    getSubmitFields(context: any, params: any): Promise<IResponse> {
      return $api.get(`ticket/receipts/get_first_state_fields/?service_id=${params.service_id}`)
    },
    createTicketSubmit(content:any, params: any): Promise<IResponse> {
      return $api.post('ticket/receipts/', params)
    },
    getServiceDetail(content:any, id: number): Promise<IResponse> {
      return $api.get(`service/projects/${id}/`)
    }
  }
}
export default ticket
