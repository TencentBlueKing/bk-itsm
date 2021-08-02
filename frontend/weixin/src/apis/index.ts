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

import axios from 'axios'
import emitter from '../utils/emitter'

const axiosInstance = axios.create({
  withCredentials: true,
  headers: {
    'X-REQUESTED-WITH': 'XMLHttpRequest'
  },
  xsrfHeaderName: 'X-CSRFTOKEN',
  xsrfCookieName: 'bkitsm_csrftoken',
  baseURL: `${(window as any).SITE_URL}weixin/api/`
  // baseURL: 'https://www.fastmock.site/mock/bc91484926ba3302b89b1be19ea66e77/724mock'
})

axiosInstance.interceptors.request.use(config => config, error => Promise.reject(error))

axiosInstance.interceptors.response.use(
  (response) => {
    if ('result' in response.data) {
      if (response.data.result) {
        return response.data
      }
      emitter.emit('notify', { type: 'danger', message: response.data.message, duration: 5000 })
      return Promise.reject(response.data.message)
    }
    return response.data
  },
  (error) => {
    emitter.emit('notify', { type: 'danger', message: '接口返回异常', duration: 5000 })
    console.error(error)
    return Promise.reject(error)
  }
)

export default axiosInstance
