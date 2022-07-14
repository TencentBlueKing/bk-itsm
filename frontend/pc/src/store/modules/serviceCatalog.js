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
    treeMore: false,
  },
  mutations: {
    // 改变树操作面板显示隐藏
    changeTreeOperat(state, value) {
      state.treeMore = value;
    },
  },
  actions: {
    getTranslateData({ commit, state, dispatch }, params) {
      return ajax.get(`service/catalogs/translate_view/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getTreeData({ commit, state, dispatch }, params) {
      return ajax.get(`service/catalogs/tree_view/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getList({ commit, state, dispatch }, params) {
      return ajax.get(`service/catalogs/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    create({ commit, state, dispatch }, params) {
      delete params["parent_name"];
      return ajax.post(`service/catalogs/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    delete({ commit, state, dispatch }, id) {
      return ajax.delete(`service/catalogs/${id}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    update({ commit, state, dispatch }, params) {
      const id = params.id;
      return ajax.put(`service/catalogs/${id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 节点排序
    moveNode({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`service/catalogs/${id}/move/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 表格排序
    moveTableNode({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`service/catalog_services/${id}/move/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
  },
};
