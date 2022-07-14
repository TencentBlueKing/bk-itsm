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
    // 获取公共字段列表
    get_tables({ commit, state, dispatch }, params) {
      return ajax.get(`workflow/tables/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    add_tables({ commit, state, dispatch }, { params }) {
      return ajax.post(`workflow/tables/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    update_tables({ commit, state, dispatch }, { params, id }) {
      return ajax.put(`workflow/tables/${id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    delet_tables({ commit, state, dispatch }, params) {
      return ajax.delete(`workflow/tables/${params.id}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // http://dev.paas-poc.o.qcloud.com:8000/api/workflow/templates/33/table/
    // 流程模型字段源
    get_ticket_tables({ commit, state, dispatch }, { params, id }) {
      return ajax.get(`workflow/templates/${id}/table/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // http://dev.paas-poc.o.qcloud.com:8000/api/workflow/states/118/add_fields_from_table/
    // 节点从基础模型添加字段
    add_fields_from_table({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`workflow/states/${id}/add_fields_from_table/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // http://dev.paas-poc.o.qcloud.com:8000/api/ticket/receipts/15/edit_field/
    // 修改单个字段
    edit_field({ commit, state, dispatch }, { params, id }) {
      return ajax.post(`ticket/receipts/${id}/edit_field/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取公共触发器基础模型字段
    get_trigger_tables({ commit, state, dispatch }, id) {
      return ajax.get(`workflow/tables/${id}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
  },
};
