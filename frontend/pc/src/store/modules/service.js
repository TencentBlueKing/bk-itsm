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
import dayjs from "dayjs";
import ajax from "../../utils/ajax";
import bus from "../../utils/bus";

export default {
  namespaced: true,
  state: {},
  mutations: {},
  actions: {
    // 获取服务目录
    getService({ commit, state, dispatch }, params) {
      return ajax.get(`service/public/service_category/records/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 新增目录
    addService({ commit, state, dispatch }, { params }) {
      return ajax.post(`service/public/service_category/records/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 删除目录信息
    deleteService({ commit, state, dispatch }, { params }) {
      return ajax.delete(`service/public/service_category/records/${params}`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 修改目录信息
    modifyService({ commit, state, dispatch }, { params, id }) {
      return ajax.put(`service/public/service_category/records/${id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取收藏
    getfavorites({ commit, state, dispatch }, params) {
      return ajax.get(`service/favorites/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 创建/更新
    updatefavorites({ commit, state, dispatch }, params) {
      return ajax.post(`service/favorites/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 收藏/取消收藏服务
    toggleServiceFavorite({ }, params) {
      const { id, favorite } = params;
      return ajax.post(`service/projects/${id}/operate_favorite/`, { favorite }).then((response) => {
        return response.data;
      });
    },
    // 获取单个服务信息
    getServiceDetail({ commit, state, dispatch }, id) {
      return ajax.get(`service/projects/${id}/`).then((response) => {
        return response.data;
      });
    },
    // 获取全部服务
    getServiceList() {
      return ajax.get(`/service/projects/all/`).then((response) => {
        response.data.data = response.data.data.filter((item) => item.bounded_catalogs.length > 0);
        return response.data;
      });
    },
    // 获取收藏的服务
    getServiceFavorites() {
      return ajax.get(`service/projects/get_favorite_service/`).then((response) => {
        return response.data;
      });
    },
    // 获取最新使用的服务
    getRecentlyFavorite({ }, params) {
      const now = dayjs(new Date());
      const curTime = now.format("YYYY-MM-DD HH:mm:ss");
      const startTime = now.subtract(1, "month").format("YYYY-MM-DD HH:mm:ss");
      return ajax
        .get(`ticket/receipts/recently_used_service/`, {
          params: {
            create_at__gte: startTime,
            create_at__lte: curTime,
          },
        })
        .then((response) => {
          return response.data;
        });
    },
    // 从已有的服务复制表单信息到当前服务
    importFromService({ }, params) {
      return ajax
        .post(`/service/projects/${params.id}/import_from_service/`, {
          service_id: params.service_id,
        })
        .then((response) => {
          return response.data;
        });
    },
    // 从已有的服务复制表单信息到当前服务
    importFromTemplate({ }, params) {
      return ajax
        .post(`/service/projects/${params.id}/import_from_template/`, {
          table_id: params.table_id,
        })
        .then((response) => {
          return response.data;
        });
    },
    // 保存并启用服务
    saveAndActionService({ }, { id, params }) {
      return ajax.post(`/service/projects/${id}/save_configs/`, params).then((response) => {
        return response.data;
      });
    },
    // 更新/修改 服务创建来源
    updateServiceSource({ }, { id, params }) {
      return ajax.post(`/service/projects/${id}/source/`, params).then((response) => {
        return response.data;
      });
    },
    // 校验项目流程是否需要更新sla
    slaValidate({ commit }, id) {
      return ajax.post(`service/projects/${id}/sla_validate/`).then((response) => response.data);
    },
  },
};
