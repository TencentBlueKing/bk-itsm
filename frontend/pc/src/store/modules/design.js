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

import Vue from "vue";
import ajax from "../../utils/ajax";
import bus from "../../utils/bus";

export default {
  namespaced: true,
  state: {
    // 流程信息
    processInfo: {},
    requestStatus: false,
    show: "567",
  },
  mutations: {
    // 改变流程信息
    changeInfo(state, value) {
      state.processInfo = value;
    },
    // 检测进入页面是否需要请求数据
    changeRequest(state) {
      state.requestStatus = !state.requestStatus;
    },
    requestInfo(state, value) {
      state.processInfo.request = value;
    },
    // 测试方法
    change(state, value) {
      state.show = value;
    },
  },
  actions: {
    // 获取流程设计表
    getList({ commit, state, dispatch }, { params }) {
      return ajax.get(`workflow/templates/?${params}`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 删除流程设计表数据
    deleteDesign({ commit, state, dispatch }, { params }) {
      return ajax.delete(`workflow/templates/${params}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 流程步骤一
    // 获取某个节点信息
    getFlowDetail({ commit, state, dispatch }, { params }) {
      return ajax.get(`workflow/templates/${params}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取事件类型数据
    getEventList({ commit, state, dispatch }, { params }) {
      return ajax.get(`service/event/${params}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 测试
    changeValue({ commit, state, dispatch }, { value }) {
      state.show = value;
    },
  },
};
