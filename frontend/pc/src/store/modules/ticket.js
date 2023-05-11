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
    /**
     * 我的单据列表已选字段缓存
     * todo: { size: '', fields: [] }
     */
    settingCache: {},
    hasTicketNodeOptAuth: true,
  },
  mutations: {
    setSettingCache(state, { type, value }) {
      state.settingCache[type] = value;
    },
    getTicketSettingformLocalStorage(state) {
      state.settingCache = JSON.parse(localStorage.getItem('ticketSetting')) || {};
    },
    setTicketSettingToLocalStorage(state) {
      localStorage.setItem('ticketSetting', JSON.stringify(state.settingCache));
    },
    clearSettingCache() {
      state.settingCache = {};
    },
    setHasTicketNodeOptAuth(state, value) {
      state.hasTicketNodeOptAuth = value;
    },
  },
  actions: {
    getTriggerStatus({ commit, state, dispatch }, id) {
      return ajax.get(`/trigger/actions/${id}/`).then((response) => response.data);
    },
    // 获取单据数量（待办、审批）
    getTicketsCount({ commit, state, dispatch }) {
      return ajax.get("ticket/receipts/total_count/").then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 审批、批量审批获取审批状态
    getTicketsApproveStatus({ commit, state, dispatch }, params) {
      return ajax.get("/ticket/receipts/batch_waiting_approve/", { params }).then((response) => response.data);
    },
    // 批量实例化工单列表-工单处理人
    // params.ids
    getTicketsProcessors({ commit, state, dispatch }, params) {
      return ajax.get("ticket/receipts/tickets_processors/", { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 批量实例化工单列表-工单创建人
    // params.ids
    getTicketsCreator({ commit, state, dispatch }, params) {
      return ajax.get("ticket/receipts/tickets_creator/", { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 批量查询当前工单是否可以操作（获取工单列表 can_operate 参数）
    // params.ids
    getTicketscanOperate({ commit, state, dispatch }, params) {
      return ajax.get("ticket/receipts/tickets_can_operate/", { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取蓝盾-用户的项目列表
    getDevopsUserProjectList({ commit, state, dispatch }, params) {
      return ajax.get("gateway/devops/get_user_projects/", { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取蓝盾-流水线列表
    getDevopsPipelineList({ commit, state, dispatch }, params) {
      return ajax.get("gateway/devops/get_user_pipeline_list/", { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取蓝盾-流水线启动信息
    getDevopsPipelineStartInfo({ commit, state, dispatch }, params) {
      return ajax.get("gateway/devops/get_pipeline_build_start_info/", { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取蓝盾-流水线详情
    getDevopsPipelineDetail({ commit, state, dispatch }, params) {
      return ajax.get("gateway/devops/get_user_pipeline_detail/", { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取蓝盾-构建状态信息
    getDevopsBuildStatus({ commit, state, dispatch }, params) {
      return ajax.get("gateway/devops/get_user_pipeline_build_status/", { params }).then((response) => {
        const res = response.data;

        return res;
      });
    },
    // 获取蓝盾-构建历史
    getDevopsBuildList({ commit, state, dispatch }, params) {
      return ajax.get("gateway/devops/get_pipeline_build_list/", { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取可引用变量
    getTicketOutput({ commit }, id) {
      return ajax.get(`ticket/receipts/${id}/get_ticket_output/`).then((response) => response.data);
    },
    // 获取单据下的所有评论
    getTicketAllComments({ commit, state, dispatch }, params) {
      return ajax.get("ticket/remark/", { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取有回复的评论
    getReplyComment({ commit, state, dispatch }, params) {
      const { id } = params;
      return ajax.get(`ticket/remark/${id}/`, { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 单据新增评论
    addTicketComment({ commit, state, dispatch }, params) {
      return ajax.post("ticket/remark/", params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 单据修改评论
    updateTicketComment({ commit, state, dispatch }, params) {
      const { id } = params;
      return ajax.put(`ticket/remark/${id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 单据删除评论
    deleteTicketComment({ commit, state, dispatch }, params) {
      const id = params;
      return ajax.delete(`ticket/remark/${id}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取单据评价
    getTicktComment({ commit, state, dispatch }, params) {
      const id = params;
      return ajax.get(`ticket/comments/${id}/`).then((response) => response.data);
    },
    // 获取是否单据处理人
    getTicketProcessStatus({ commit, state, dispatch }, { params }) {
      const { id, step_id: stepId } = params;
      return ajax.get(`ticket/receipts/${id}/is_processor/?step_id=${stepId}`).then((response) => response.data);
    },
  },
};
