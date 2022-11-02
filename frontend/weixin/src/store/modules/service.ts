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

import $api from '../../apis/index'
import dayjs from "dayjs"

const service = {
  state: {},
  mutations: {},
  actions: {
    getCategories() {
      return $api.get('service/categories/').then(res => res)
    },
    getServiceList() {
      return $api.get('service/projects/all/').then(res => res.data)
    },
    getServiceFavorites() {
      return $api.get('service/projects/get_favorite_service/').then(res => res.data)
    },
    getRecentFavorites() {
      const now = dayjs()
      console.log(now)
      const curTime = now.format("YYYY-MM-DD HH:mm:ss")
      const startTime = now.subtract(1, "month").format("YYYY-MM-DD HH:mm:ss")
      return $api
        .get(`ticket/receipts/recently_used_service/`, {
          params: {
            create_at__gte: startTime,
            create_at__lte: curTime
          }
        })
        .then(res => res.data)
    },
    // 收藏/取消收藏服务
    toggleServiceFavorite(context: any, payload: any) {
      const { id, favorite } = payload
      return $api.post(`service/projects/${id}/operate_favorite/`, { favorite }).then(response => response)
    },
    get_priority(content: any, payload: any) {
      return $api.post(`sla/matrixs/priority_value/`, payload).then(res => res.data)
    },
    getStepList(context: any, params: any) {
      console.log(params)
      return $api.get(`ticket/receipts/${params.id}/states/`, { params: params }).then(res => res.data)
    }
  }
}

export default service
