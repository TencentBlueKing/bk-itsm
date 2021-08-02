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

import { createStore, useStore as baseUseStore, Store } from 'vuex'
import { InjectionKey } from 'vue'
import service from './modules/service'
import ticket from './modules/ticket'
import field from './modules/field'
import $api from '../apis/index'

interface State {
  username: string,
  serviceConfig: object
}

const store = createStore<State>({
  state: {
    username: '',
    serviceConfig: {}
  },
  modules: {
    service,
    ticket,
    field
  },
  mutations: {
    setServiceConfig(state, data) {
      state.serviceConfig = data
    }
  },
  actions: {
    getServiceConfig({ commit }) {
      return $api.get('ticket_status/status/?ordering=order').then((res) => {
        const data = {}
        res.data.forEach((item) => {
          if (data[item.service_type]) {
            data[item.service_type].push(item)
          } else {
            data[item.service_type] = [item]
          }
        })
        commit('setServiceConfig', data)
      })
    }
  }
})

export const key: InjectionKey<Store<State>> = Symbol()
export function useStore() {
  return baseUseStore(key)
}

export default store
