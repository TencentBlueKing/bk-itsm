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

import ajax from "../../utils/ajax";

export default {
  namespaced: true,
  state: {
    // 轮询变量
    intervalInfo: {
      basic: "",
      lines: "",
      timeOut: "",
    },
    nodeList: [],
  },
  mutations: {
    setNodeList(state, value) {
      state.nodeList = value || [];
    },
  },
  actions: {
    // 获取线条流转颜色
    getLineStatus({ commit, state, dispatch }, { basicId }) {
      return ajax.get(`ticket/receipts/${basicId}/transitions/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取节点状态列表
    getNodeList({ commit, state, dispatch }, params) {
      return ajax.get(`ticket/receipts/${params.id}/states/`, { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 仅在单据内获取单据节点状态列表
    getOnlyTicketNodeInfo({ commit, state, dispatch }, params) {
      return ajax.get(`ticket/receipts/${params.id}/details_states/`, { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 仅在单据内获取单据节点状态列表
    getOnlyStateStatus({ commit, state, dispatch }, { params, id }) {
      return ajax.get(`ticket/receipts/${id}/states_status/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取节点字段列表
    getTicketNodeInfo({ commit, state, dispatch }, { params, id }) {
      return ajax.get(`ticket/receipts/${id}/states/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 终止单据
    terminableOrder({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`ticket/receipts/${id}/terminate/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 转处理人
    proceedOrder({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`ticket/receipts/${id}/proceed/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    widthdrawOrder({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`ticket/receipts/${id}/withdraw/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 分派单据
    distributeOrder({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`ticket/receipts/${id}/operate/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    newAssignDeliver({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`ticket/receipts/${id}/operate/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 异常分派
    exceptionDistribute({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`ticket/receipts/${id}/exception_distribute/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 响应
    replyAssignDeliver({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`ticket/receipts/${id}/reply/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取所有关联单据
    getAssociatedTickets({ commit, state, dispatch }, params) {
      return ajax.get(`ticket/receipts/${params.id}/derive_tickets/`, { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 关单
    closeTickets({ commit, state, dispatch }, { id, params }) {
      return ajax.post(`ticket/receipts/${id}/close/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 挂起单据
    suspendTickets({ commit, state, dispatch }, { id, params }) {
      return ajax.post(`ticket/receipts/${id}/suspend/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 恢复单据
    restoreTickets({ commit, state, dispatch }, id) {
      return ajax.post(`ticket/receipts/${id}/unsuspend/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取结束状态
    getEndStatus({ commit, state, dispatch }, { type, key }) {
      return ajax.get(`ticket_status/status/next_over_status/?service_type=${type}&key=${key}`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 执行自定义按钮
    executeCusButton({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`ticket/receipts/${id}/trigger_state_button/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 关注&取关
    setAttention({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`ticket/receipts/${id}/add_follower/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 节点重试
    retryNode({ commit, state, dispatch }, { params, ticketId }) {
      return ajax.post(`/ticket/receipts/${ticketId}/retry/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 节点忽略
    ignoreNode({ commit, state, dispatch }, { params, ticketId }) {
      return ajax.post(`/ticket/receipts/${ticketId}/ignore/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 节点日志(执行信息)
    getNodeLog({ commit, state, dispatch }, { params }) {
      return ajax.get(`ticket/logs/`, { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 通过通知url进入，获取节点是否已处理信息
    getTicketNoticeInfo({ commit, state, dispatch }, { params }) {
      return ajax.get(`ticket/receipts/operate_check/`, { params }).then((response) => {
        let res = response.data;
        return res;
      });
    },
  },
};
