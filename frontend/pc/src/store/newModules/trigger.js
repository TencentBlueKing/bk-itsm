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
    // 流程内引用触发器，保存流程信息
    triggerVariables: [],
  },
  mutations: {
    changeTriggerVariables(state, list) {
      state.triggerVariables = list;
    },
  },
  actions: {
    // 获取触发器列表
    getTriggerTable({ commit, state, dispatch }, params) {
      return ajax.get(`/trigger/triggers/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 删除一个触发器
    deleteTrigger({ commit, state, dispatch }, id) {
      return ajax.delete(`/trigger/triggers/${id}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 根据ID获取一个触发器的详细信息
    getTriggerInfo({ commit, state, dispatch }, id) {
      return ajax.get(`/trigger/triggers/${id}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取响应事件列表信息
    getTriggerList({ commit, state, dispatch }, params) {
      return ajax.get(`/trigger/triggers/signals/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 通过触发器ID获取触发器创建下的所以规则
    getTriggerRules({ commit, state, dispatch }, params) {
      return ajax.get(`/trigger/rules/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取响应事件列表信息
    getResponseList({ commit, state, dispatch }) {
      return ajax.get(`/trigger/components/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 通过id获取响应事件的内容
    getResponseListById({ commit, state, dispatch }, params) {
      return ajax.get(`/trigger/action_schemas/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取触发器的内容
    getTriggerContent({ commit, state, dispatch }, id) {
      return ajax.get(`/trigger/actions/${id}/fields/`).then((response) => response.data);
    },
    // 获取触发器的内容
    getTriggerParams({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`/trigger/actions/${id}/params/`, params).then((response) => response.data);
    },
    executeTrigger({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`/trigger/actions/${id}/run/`, params).then((response) => response.data);
    },
    // 创建一个触发器规则
    createTriggerRule({ commit, state, dispatch }, params) {
      return ajax.post(`/trigger/triggers/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    createRespond({ commit, state, dispatch }, { id, params }) {
      return ajax.post(`trigger/triggers/${id}/create_or_update_action_schemas/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 一个触发器下创建多条规则
    createTriggerCondition({ commit, state, dispatch }, params) {
      return ajax.post(`/trigger/rules/batch_create_or_update/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 新一个触发器下创建多条规则
    batchTriggerCondition({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`/trigger/triggers/${id}/create_or_update_rules/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 全量修改一个触发器规则
    putTriggerRule({ commit, state, dispatch }, { params, id }) {
      return ajax.put(`/trigger/triggers/${id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取触发器变量
    getTriggerVariables({ commit, state, dispatch }, { id, type, params }) {
      return ajax.get(`workflow/${type}/${id}/variables/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取单据手动触发器
    getTicketHandleTriggers({ commit, state, dispatch }, { id, params }) {
      return ajax.get(`ticket/receipts/${id}/trigger_actions/`, { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取单据触发器记录
    getTicketTriggerRecord({ commit, state, dispatch }, { id, params }) {
      return ajax.get(`ticket/receipts/${id}/trigger_actions_group/`, { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取单据手动触发器
    executeHandleTriggers({ commit, state, dispatch }, id) {
      return ajax.post(`trigger/actions/${id}/run/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取任务手动触发器
    getTaskHandleTriggers({ commit, state, dispatch }, params) {
      return ajax.get(`trigger/actions/`, { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
  },
};
