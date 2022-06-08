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

// import Vue from 'vue'
import ajax from "../../utils/ajax";
// import bus from '../../utils/bus'

export default {
  namespaced: true,
  state: {},
  mutations: {},
  actions: {
    getList({ commit, state, dispatch }, params) {
      return ajax
        .get(`service/projects/`, { params: params })
        .then((response) => response.data)
        .catch((error) => console.log(error));
    },
    createService({ commit, state, dispatch }, params) {
      return ajax.post(`service/projects/`, params).then((response) => response.data);
    },
    batchDeleteService({ commit, state, dispatch }, params) {
      return ajax.post(`service/projects/batch_delete/`, params).then((response) => response.data);
    },
    cloneService({ commit, state, dispatch }, id) {
      return ajax.post(`service/projects/${id}/clone/`).then((response) => response.data);
    },
    deleteService({ commit, state, dispatch }, id) {
      return ajax.delete(`service/projects/${id}/`).then((response) => response.data);
    },
    updateService({ commit, state, dispatch }, params) {
      return ajax.put(`service/projects/${params.id}/`, params).then((response) => response.data);
    },
    exportService({ commit, state, dispatch }, id) {
      return ajax.get(`service/projects/${id}/export/`).then((response) => response.data);
    },
    importService({ commit, state, dispatch }, params) {
      return ajax.post(`service/projects/imports/`, params).then((response) => response.data);
    },
  },
};
