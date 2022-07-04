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
    // 后台缓存
    clearStorage({ commit, state, dispatch }, params) {
      return ajax.get("misc/clean_cache/", { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 文件存储位置
    getattachmentStorage({ commit, state, dispatch }, params) {
      return ajax.get("iadmin/system_settings/", { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    putattachmentStorage({ commit, state, dispatch }, { params, id }) {
      return ajax.put(`iadmin/system_settings/${id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 组织结构开关
    get_organization_structure({ commit, state, dispatch }, params) {
      return ajax.get("iadmin/system_settings/", { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    enable_organization_structure({ commit, state, dispatch }, { params, id }) {
      return ajax.put(`iadmin/system_settings/${id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    getEnableStatus({ commit, state, dispatch }, params) {
      return ajax.get("iadmin/system_settings/").then((response) => {
        const res = response.data;
        return res;
      });
    },
    putEnableStatus({ commit, state, dispatch }, { params, id }) {
      return ajax.put(`iadmin/system_settings/${id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
  },
};
