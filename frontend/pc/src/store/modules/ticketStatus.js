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
    statusColorMap: {},
  },
  mutations: {},
  actions: {
    // 获取四种类型的列表信息
    getFourTypesList({ commit, state, dispatch }, params) {
      return ajax.get(`ticket_status/status/get_configs/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取指定类型的列表信息
    getTypeStatus({ commit, state, dispatch }, { type, params }) {
      if (state.statusColorMap[type]) {
        return state.statusColorMap[type];
      }
      return ajax.get(`ticket_status/status/?service_type=${type}&ordering=order`, { params }).then((response) => {
        const res = response.data;
        state.statusColorMap[type] = res;
        return res;
      });
    },
    // 新增指定服务类型下的工单状态
    addTypeState({ commit, state, dispatch }, params) {
      return ajax.post(`ticket_status/status/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 编辑指定服务类型下的工单状态
    editTypeState({ commit, state, dispatch }, { params, id }) {
      return ajax.patch(`ticket_status/status/${id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 删除指定服务类型下的工单状态
    deleteTypeState({ commit, state, dispatch }, id) {
      return ajax.delete(`ticket_status/status/${id}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 保存指定服务类型下的工单状态
    saveTypeState({ commit, state, dispatch }, params) {
      return ajax.post(`ticket_status/status/save_status_of_service_type/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取指定服务类型下的工单流转状态
    getTypeFlow({ commit, state, dispatch }, type) {
      return ajax.get(`ticket_status/transit/?service_type=${type}`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 保存指定服务类型下的工单自动流转状态
    saveTypeFlow({ commit, state, dispatch }, params) {
      return ajax.post(`ticket_status/transit/save_transit_of_service_type/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取指定服务类型下的工单自动流转状态
    getTypeAutoFlow({ commit, state, dispatch }, type) {
      return ajax.get(`ticket_status/transit/is_auto/?service_type=${type}`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 设置指定服务类型下的工单自动流转状态
    setAutoFlow({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`ticket_status/status/${id}/set_transit_rule/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 取消指定服务类型下的工单自动流转状态
    closeAutoFlow({ commit, state, dispatch }, id) {
      return ajax.post(`ticket_status/status/${id}/close_transit_rule/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 取消指定服务类型下的工单自动流转状态
    getOneAutoFlow({ commit, state, dispatch }, id) {
      return ajax.get(`ticket_status/transit/get_auto_detail/?from_status_id=${id}`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取
    getSubmitFlow({ commit, state, dispatch }, type) {
      return ajax.get(`sla/policy/timers/?service_type=${type}`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 更新
    endSubmitFlow({ commit, state, dispatch }, params) {
      return ajax.post(`sla/policy/timers/batch_update/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取全局视图的工单状态
    getOverallTicketStatuses({ commit, state, dispatch }, type) {
      return ajax.get(`ticket_status/status/overall_ticket_statuses/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
  },
};
