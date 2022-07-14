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
    refreshTask: false,
    intervalInfo: "",
  },
  mutations: {
    // 缓存数据
    changeTaskStatus(state, value) {
      state.refreshTask = value;
    },
  },
  actions: {
    // 获取触发器列表
    getTaskField({ commit, state, dispatch }, params) {
      return ajax.get(`/workflow/task_field_schemas/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取当前单据的节点详情
    getTicketNodeInfo({ commit, state, dispatch }, { params, id }) {
      return ajax.get(`/ticket/receipts/${id}/states/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取单个任务详细信息
    getTaskInfo({ commit, state, dispatch }, id) {
      return ajax.get(`/task/tasks/${id}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 创建单个任务(批量创建任务)
    createTask({ commit, state, dispatch }, { params }) {
      return ajax.post(`/task/tasks/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 编辑单个任务,更新任务顺序
    editorTask({ commit, state, dispatch }, { params, id }) {
      return ajax.patch(`/task/tasks/${id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getSopsTask({ commit, state, dispatch }, params) {
      return ajax.get(`/gateway/sops/get_sops_tasks/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取标准运维未执行的任务
    getSopsUnfinishedTask({ commit, state, dispatch }, params) {
      return ajax.get(`/gateway/sops/get_unfinished_sops_tasks/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取标准运维任务详情
    getSopsTaskDetail({ commit, state, dispatch }, params) {
      return ajax.get(`/gateway/sops/get_sops_tasks_detail/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取标准运维模板预览数据
    getSopsPreview({ commit }, params) {
      return ajax.post(`/gateway/sops/get_sops_preview_task_tree/`, params).then((response) => response.data);
    },
    getSopsCommonPreview({ commit }, params) {
      return ajax.post(`/gateway/sops/get_sops_preview_common_task_tree/`, params).then((response) => response.data);
    },
    // 同步标准运维任务状态
    syncSopsTaskStatus({ commit, state, dispatch }, params) {
      return ajax.get(`/task/tasks/sync_task_status/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 根据条件获取任务列表
    getTaskList({ commit, state, dispatch }, params) {
      return ajax.get(`/task/tasks/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 删除任务
    deleteTask({ commit, state, dispatch }, id) {
      return ajax.delete(`/task/tasks/${id}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 忽略任务
    ignoreTask({ commit, state, dispatch }, id) {
      return ajax.post(`/task/tasks/${id}/skip/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 重试任务
    retryTask({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`/task/tasks/${id}/retry/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 处理，总结任务
    dealTask({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`/task/tasks/${id}/proceed/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 创建任务库
    creatLibrary({ commit, state, dispatch }, params) {
      return ajax.post(`/task/libs/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取任务库下拉框数据
    getLibraryList({ commit, state, dispatch }, params) {
      return ajax.get(`/task/libs/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 根据任务库id获取任务详情
    getLibraryInfo({ commit, state, dispatch }, { params, id }) {
      return ajax.get(`/task/libs/${id}/tasks/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 删除某个任务库
    deleteLibrary({ commit, state, dispatch }, id) {
      return ajax.delete(`/task/libs/${id}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 更新任务库
    updataLibrary({ commit, state, dispatch }, { params, id }) {
      return ajax.put(`/task/libs/${id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取标准运维信息
    getTaskStatusInfo({ commit, state, dispatch }, id) {
      return ajax.get(`/task/tasks/${id}/get_task_status/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getHistoryDetail({ commit, state, dispatch }, id) {
      return ajax.get(`/trigger/actions/${id}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
  },
};
