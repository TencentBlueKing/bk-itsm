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
    nodeStatus: false,
    versionStatus: true,
    contentStatus: true,
    nodeInfo: {},
  },
  mutations: {
    changeNodeStatus(state, value) {
      state.nodeStatus = value;
    },
    changeVersion(state, value) {
      state.versionStatus = value;
    },
    changeContent(state, value) {
      state.contentStatus = value;
    },
    // 保存当前移动节点的信息
    changeNodeInfo(state, value) {
      state.nodeInfo = value;
    },
  },
  actions: {
    // 获取流程设计表
    getList({ commit, state, dispatch }, params) {
      return ajax.get(`workflow/templates/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取流程的线条和节点
    getStates({ commit, state, dispatch }, params) {
      return ajax.get(`workflow/states/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 按执行顺序获取流程节点
    getOrderedStates({ commit, state, dispatch }, params) {
      const { id } = params;
      return ajax.get(`workflow/states/${id}/post_states/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getChartLink({ commit, state, dispatch }, params) {
      return ajax.get(`workflow/transitions/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 新增节点
    creatNode({ commit, state, dispatch }, { params }) {
      return ajax.post(`workflow/states/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 新增节点
    copyNode({ commit, state, dispatch }, id) {
      return ajax.post(`workflow/states/${id}/clone/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 删除节点
    deleteNode({ commit, state, dispatch }, id) {
      return ajax.delete(`workflow/states/${id}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 更新节点的位置
    updateNodeAxis({ commit, state, dispatch }, { params, id }) {
      return ajax.patch(`workflow/states/${id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 创建连线
    createLine({ commit, state, dispatch }, { lineParams }) {
      return ajax.post(`workflow/transitions/`, lineParams).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 删除线条
    deleteLine({ commit, state, dispatch }, id) {
      return ajax.delete(`workflow/transitions/${id}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },

    // 节点配置 - 字段配置接口
    // 字段列表
    getFieldList({ commit, state, dispatch }, params) {
      return ajax.get(`workflow/fields/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 删除字段
    deleteField({ commit, state, dispatch }, { params, id }) {
      return ajax.delete(`workflow/fields/${id}/`, { data: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 节点配置 - 基本信息接口
    // 角色关联
    getUser({ commit, state, dispatch }, params) {
      return ajax.get(`role/types/`, { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getSecondUser({ commit, state, dispatch }, params) {
      return ajax.get(`role/users/`, { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 更新配置
    updateNode({ commit, state, dispatch }, { params, id }) {
      return ajax.put(`workflow/states/${id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 节点配置 - 线条配置接口
    getLineField({ commit, state, dispatch }, { id }) {
      return ajax.get(`workflow/transitions/${id}/variables/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取线条关系模板
    getLineTemplate({ commit, state, dispatch }, params) {
      return ajax.get(`workflow/transition_template/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 保存线条关系模板
    submitLineTemplate({ commit, state, dispatch }, { params }) {
      return ajax.post(`workflow/transition_template/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 更新模板
    updateLineTemplate({ commit, state, dispatch }, { params }) {
      return ajax.put(`workflow/transition_template/${params.id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 更新线条信息
    updateLine({ commit, state, dispatch }, { lineParams, id }) {
      return ajax.put(`workflow/transitions/${id}/`, lineParams).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 节点线条版本信息
    getNodeVersion({ commit, state, dispatch }, { id }) {
      return ajax.get(`workflow/versions/${id}/states/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getLineVersion({ commit, state, dispatch }, { id }) {
      return ajax.get(`workflow/versions/${id}/transitions/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 更新画布的连线位置（输入和输出）
    updateFlowLine({ commit, state, dispatch }, { params }) {
      return ajax.post(`workflow/transitions/batch_update/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getPreStates({ commit, state, dispatch }, { id }) {
      return ajax.get(`workflow/states/${id}/pre_states/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取单个节点信息
    getOneStateInfo({ commit, state, dispatch }, { id }) {
      return ajax.get(`workflow/states/${id}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取所有触发器
    getAllTriggers({ commit, state, dispatch }) {
      return ajax.get(`trigger/components/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取所有按钮
    getAllActions({ commit, state, dispatch }, params) {
      return ajax.get(`workflow/triggers/`, { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 添加按钮
    addAction({ commit, state, dispatch }, { id, batchAddList }) {
      return ajax.post(`workflow/states/${id}/set_actions/`, batchAddList).then((response) => {
        const res = response.data;
        return res;
      });
    },
  },
};
