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
    getRoleTypeList({ commit, state, dispatch }, params) {
      return ajax.get(`${window.site}role/types/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getChoices({ commit, state, dispatch }) {
      return ajax.get(`${window.site}role/users/extra/get_global_choices`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getRoleList({ commit, state, dispatch }, params) {
      return ajax.get(`${window.site}role/users/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    submit({ commit, state, dispatch }, params) {
      return ajax.post(`${window.site}role/users/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    update({ commit, state, dispatch }, params) {
      return ajax.put(`${window.site}role/users/${params.id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    delete({ commit, state, dispatch }, id) {
      return ajax.delete(`${window.site}role/users/${id}`).then((response) => {
        const res = response.data;
        return res;
      });
    },
  },
};
