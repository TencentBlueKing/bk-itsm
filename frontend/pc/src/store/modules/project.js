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
    // projectAuthActions: [], // 拥有的项目权限列表
    projectAuthActions: [
      // 'project_view',
      // 'project_edit',
      // 'workflow_create',
      // 'service_create',
      // 'role_create',
      // 'sla_manage',
      // 'flow_element_manage',
      // 'system_settings_manage'
    ], // 拥有的项目权限列表
    id: window.DEFAULT_PROJECT,
    projectInfo: {}, // 项目信息
    projectListLoading: false,
    projectList: [],
  },
  mutations: {
    setProjectId(state, value) {
      state.id = value;
    },
    setProjectInfo(state, value) {
      state.projectInfo = value;
      state.projectAuthActions = value.auth_actions;
    },
    setProjectListLoading(state, val) {
      state.projectListLoading = val;
    },
    setProjectList(state, value) {
      state.projectList = value;
    },
  },
  actions: {
    getProjectInfo({ commit }, params) {
      //  目前项目在 ITSM 是虚拟的，所以暂时默认为 0
      const projectId = 0;
      return ajax.get(`/project/projects/${projectId}/info/`, params).then((response) => {
        // const res = response.data
        // commit('setProjectInfo', res.data)
        return response.data;
      });
    },
    // 获取项目列表
    getProjectList({ commit }, params) {
      return ajax.get("/project/projects/", { params }).then((response) => response.data);
    },
    // 获取项目所以列表
    getProjectAllList({ commit }, params) {
      return ajax.get("/project/projects/all/", { params }).then((response) => response.data);
    },
    // 创建项目
    createProject({ commit }, data) {
      return ajax.post("/project/projects/", data).then((response) => response.data);
    },
    // 获取项目详情
    getProjectDetail({ commit }, key) {
      return ajax.get(`/project/projects/${key}/`).then((response) => {
        commit("setProjectInfo", response.data.data);
        return response.data;
      });
    },
    // 更新项目信息
    updateProject({ commit }, data) {
      return ajax.put(`/project/projects/${data.key}/`, data).then((response) => response.data);
    },
    // 删除项目
    deleteProject({ commit }, key) {
      return ajax.delete(`/project/projects/${key}/`).then((response) => response.data);
    },
    // 更改默认项目
    changeDefaultProject({ commit }, id) {
      return ajax.post(`project/projects/${id}/update_project_record/`);
    },
    // 创建指定项目下的tab
    createProjectTab({ commit }, params) {
      return ajax.post("project/tabs/", params).then((response) => response.data);
    },
    // 获取指定项目下的tab
    getProjectTab({ commit }, params) {
      return ajax.get("project/tabs/", { params }).then((response) => response.data);
    },
    // 编辑指定项目下的tab
    editProjectTab({ commit }, params) {
      const { id } = params;
      return ajax.patch(`project/tabs/${id}/`, params).then((response) => response.data);
    },
    // 删除指定项目下的tab
    deleteProjectTab({ commit }, id) {
      return ajax.delete(`project/tabs/${id}/`).then((response) => response.data);
    },
    // 拖拽排序指定项目下的tab
    moveProjectTab({ commit }, params) {
      const { tab_id: tabId } = params;
      return ajax.post(`project/tabs/${tabId}/move/`, params).then((response) => response.data);
    },
    // 获取项目tab列表
    getProjectTabList({ commit }, params) {
      const { page_size: pageSize, page, ordering } = params;
      return ajax
        .post(`ticket/receipts/get_filter_tickets/?page_size=${pageSize}&page=${page}&ordering=${ordering}`, params)
        .then((response) => response.data);
    },
    getAction({ commit }, params) {
      return ajax.get(`iadmin/custom_notify_template/action_type/`, { params }).then((response) => response.data);
    },
    getProjectNotice({ commit }, params) {
      return ajax.get(`iadmin/custom_notify_template/`, params).then((response) => response.data);
    },
    addProjectNotice({ commit }, params) {
      return ajax.post(`iadmin/custom_notify_template/`, params).then((response) => response.data);
    },
    updateProjectNotice({ commit }, params) {
      const { id } = params;
      return ajax.patch(`iadmin/custom_notify_template/${id}/`, params).then((response) => response.data);
    },
    deleteProjectNotice({ commit }, id) {
      return ajax.delete(`iadmin/custom_notify_template/${id}/`).then((response) => response.data);
    },
  },
};
