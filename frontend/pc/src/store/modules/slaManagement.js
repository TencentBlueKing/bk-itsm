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
  state: {},
  mutations: {},
  actions: {
    // 优先级管理
    // 获取优先级列表
    getPriorityList({ commit, state, dispatch }, { params }) {
      return ajax.post(`sla/matrixs/matrix_of_service_type/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 保存Sla优先级
    submitPriority({ commit, state, dispatch }, { params }) {
      return ajax.put(`sla/matrixs/batch_update/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 服务协议管理
    // 获取服务协议列表
    getProtocolsList({ commit, state, dispatch }, { params }) {
      return ajax.get(`sla/protocols/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取服务优先级列表
    getPriority({ commit, state, dispatch }, { params }) {
      return ajax.get(`service/dictdatas/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 新增一个服务协议
    addProtocol({ commit, state, dispatch }, { params }) {
      return ajax.post(`sla/protocols/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 修改一个服务协议
    putProtocol({ commit, state, dispatch }, { params, id }) {
      return ajax.put(`sla/protocols/${id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 删除一个服务协议
    deleteProtocol({ commit, state, dispatch }, id) {
      return ajax.delete(`sla/protocols/${id}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getNoticeTemplate({ commit, state, dispatch }, params) {
      return ajax.get(`sla/protocols/sla_notify_templates/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
  },
};
