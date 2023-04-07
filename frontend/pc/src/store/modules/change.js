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
import { i18n } from "../../main";

export default {
  namespaced: true,
  state: {
    fields: [],
    statusList: [
      { key: "RUNNING", pk_value: "处理中" },
      // {key: 'TIMEOUT', pk_value: '处理中(已超时)'},
      // {key: 'TIMEOUT_FINISHED', pk_value: '超时结束'},
      { key: "SUSPEND", pk_value: "挂起" },
      { key: "FINISHED", pk_value: "已结束" },
    ],
  },
  mutations: {
    setFields(state, list) {
      state.fields = list;
    },
  },
  actions: {
    getList({ commit, state, dispatch }, params) {
      return ajax.get("ticket/receipts/", { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getExportFields({ commit, state, dispatch }, params) {
      return ajax.get("ticket/receipts/export_fields/", { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getOrderDetails({ commit, state, dispatch }, params) {
      return ajax.get(`ticket/receipts/${params.id}/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getStepList({ commit, state, dispatch }, params) {
      return ajax.get(`ticket/receipts/${params.id}/states/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getStepFields({ commit, state, dispatch }, params) {
      return ajax.get(`ticket/fields/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getLog({ commit, state, dispatch }, params) {
      return ajax.get("ticket/logs/", { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getFields({ commit, state, dispatch }, params) {
      return ajax
        .get(`ticket/receipts/${params.ticket_id}/fields/?state_id=${params.first_state_id}`)
        .then((response) => {
          const res = response.data;
          return res;
        });
    },
    getSubmitFields({ commit, state, dispatch }, params) {
      return ajax.get(`ticket/receipts/get_first_state_fields/?service_id=${params.service_id}`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 转建单获取所有字段 带有value
    getAllFields({ commit, state, dispatch }, ticketId) {
      return ajax.get(`ticket/receipts/${ticketId}/all_fields/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getButtons({ commit, state, dispatch }, params) {
      return ajax.get(`ticket/receipts/${params.ticket_id}/transitions/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    submit({ commit, state, dispatch }, params) {
      return ajax.post("ticket/receipts/", params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    bindTicket({ commit, state, dispatch }, params) {
      return ajax.post("ticket/receipts/bind_derive_tickets/", params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    unbindTicket({ commit, state, dispatch }, params) {
      return ajax.post("ticket/receipts/unbind_derive_ticket/", params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    submitField({ commit, state, dispatch }, params) {
      return ajax.post(`ticket/receipts/${params.ticket_id}/proceed/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    deliverTo({ commit, state, dispatch }, params) {
      return ajax.post(`ticket/receipts/${params.ticket_id}/deliver/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    terminate({ commit, state, dispatch }, params) {
      return ajax.post(`ticket/receipts/${params.ticket_id}/terminate/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    update({ commit, state, dispatch }, params) {
      return ajax.put(params.id, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    delete({ commit, state, dispatch }, id) {
      return ajax.delete(id).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 挂起单据接口
    hangBill({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`ticket/receipts/${id}/suspend/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 恢复单据接口
    restoreBill({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`ticket/receipts/${id}/unsuspend/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 恢复单据接口
    widthdrawBill({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`ticket/receipts/${id}/withdraw/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取模板列表数据
    getTemplateList({ commit, state, dispatch }, params) {
      return ajax.get(`ticket/templates/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 保存为模板
    submitTemplate({ commit, state, dispatch }, params) {
      return ajax.post(`ticket/templates/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 更新模板
    updateTemplate({ commit, state, dispatch }, { params, id }) {
      return ajax.put(`ticket/templates/${id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 删除模板
    deleteTemplate({ commit, state, dispatch }, { params, id }) {
      return ajax.delete(`ticket/templates/${id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 认领单据
    claimBill({ commit, state, dispatch }, params) {
      return ajax.post(`ticket/receipts/claim_ticket/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 提交催办
    submitSupervise({ commit, state, dispatch }, params) {
      return ajax.post(`ticket/receipts/${params.id}/supervise/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 分配单据
    distributionBill({ commit, state, dispatch }, params) {
      return ajax.post(`ticket/receipts/distribute_ticket/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 保存草稿
    getDraft({ commit, state, dispatch }, { id }) {
      return ajax.get(`ticket/draft/${id}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    saveDraft({ commit, state, dispatch }, params) {
      return ajax.post(`ticket/draft/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    updateDraft({ commit, state, dispatch }, { params, id }) {
      return ajax.put(`ticket/draft/${id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 新建母子单
    mergeTickets({ commit, state, dispatch }, params) {
      return ajax.post(`ticket/receipts/merge_tickets/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 查询母子单
    getInheritState({ commit, state, dispatch }, params) {
      return ajax.get(`ticket/receipts/${params.id}/master_or_slave/`, { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    unBindInherit({ commit, state, dispatch }, params) {
      return ajax.post(`ticket/receipts/unmerge_tickets/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getBindHistory({ commit, state, dispatch }, params) {
      return ajax.get(`ticket/receipts/${params.id}/unbind_history/?related_type=${params.type}`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getReceiptsSlaTask({ commit, state, dispatch }, params) {
      return ajax.get(`ticket/receipts/${params.id}/sla_task/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 重新提单，获取参数信息
    getCreateTicektParams({ commit, state, dispatch }, { id }) {
      return ajax.get(`ticket/receipts/${id}/ticket_base_info/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
  },
};
