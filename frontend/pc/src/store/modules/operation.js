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
    // 概览数据总数
    getSummaryTotalData({ commit }, params) {
      return ajax.get("ticket/operational/overview_count/", { params }).then((response) => response.data);
    },
    // 概览数据按周数据
    getSummaryWeekData({ commit }, params) {
      return ajax.get("ticket/operational/compared_same_week/", { params }).then((response) => response.data);
    },
    // 服务使用统计
    getServiceUseData({ commit }, params) {
      return ajax.get("ticket/operational/service_statistics/", { params }).then((response) => response.data);
    },
    // 业务使用统计
    getBizUseData({ commit }, params) {
      return ajax.get("ticket/operational/biz_statistics/", { params }).then((response) => response.data);
    },
    // 按类型统计单据数量
    getTicketClassifyData({ commit }, params) {
      return ajax.get("ticket/operational/category_statistics/", { params }).then((response) => response.data);
    },
    // 单据状态占比
    getTicketStatusData({ commit }, params) {
      return ajax.get("ticket/operational/status_statistics/", { params }).then((response) => response.data);
    },
    // 提单人数、新增单量、新增用户数、新增服务统计
    getResourceCountData({ commit }, params) {
      return ajax.get("ticket/operational/resource_count_statistics/", { params }).then((response) => response.data);
    },
    // top 10 提单用户统计
    getTop10CreateTicketUserData({ commit }, params) {
      return ajax.get("ticket/operational/top_creator_statistics/", { params }).then((response) => response.data);
    },
    // top 10 单据分布占比
    getTop10TicketOrganizationData({ commit }, params) {
      return ajax.get("ticket/operational/distribute_statistics/", { params }).then((response) => response.data);
    },
    // 服务下的新增单量、业务数量统计
    getServiceCountData({ commit }, params) {
      return ajax.get("ticket/operational/service_count_statistics/", { params }).then((response) => response.data);
    },
  },
};
