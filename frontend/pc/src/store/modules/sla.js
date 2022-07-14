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
    getList({ commit, state, dispatch }, params) {
      return ajax
        .get(`service/slas/`, { params: params })
        .then((response) => {
          const res = response.data;
          return res;
        })
        .catch((error) => {
          console.log(error);
        });
    },
    getSlaLevel({ commit, state, dispatch }, { params }) {
      return ajax
        .get(`service/slas/get_level_choice/`, { params: params })
        .then((response) => {
          const res = response.data;
          return res;
        })
        .catch((error) => {
          console.log(error);
        });
    },
    submitSla({ commit, state, dispatch }, params) {
      return ajax.post("service/slas/", params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    updateSla({ commit, state, dispatch }, params) {
      return ajax.put(`service/slas/${params.id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    deleteSla({ commit, state, dispatch }, id) {
      return ajax.delete(`service/slas/${id}`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 新增模型
    saveSchedule({ commit, state, dispatch }, params) {
      return ajax.post("sla/schedules/", params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取模型列表
    getScheduleList({ commit, state, dispatch }, params) {
      return ajax.get("sla/schedules/", { params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取单据高亮设置
    getTicketHighlight({ commit, state, dispatch }) {
      return ajax.get("sla/ticket_highlight/").then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取单据高亮设置
    updateTicketHighlight({ commit, state, dispatch }, params) {
      return ajax.put("sla/ticket_highlight/1/", params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 删除模型
    deleteSchedule({ commit, state, dispatch }, id) {
      return ajax.delete(`sla/schedules/${id}/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 更新模型
    updateSchedule({ commit, state, dispatch }, params) {
      return ajax.put(`sla/schedules/${params.id}/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 校验流程版本是否支持 sla 协议
    checkProcessCanUseSla({ commit, state, dispatch }, id) {
      return ajax.get(`/workflow/versions/${id}/sla_validate/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
  },
};
