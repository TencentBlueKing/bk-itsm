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

import Vue from 'vue';
import axios from 'axios';
import bus from './bus.js';
import { checkDataType } from './getDataType.js';
import isCrossOriginIFrame from './isCrossOriginIFrame.js';
const isCrossOrigin = isCrossOriginIFrame();
const topWindow = isCrossOrigin ? window : window.top;

const instance = axios.create({
  validateStatus: (status) => status >= 200 && status <= 505,
  baseURL: `${window.SITE_URL}api/`,
  // `headers` are custom headers to be sent
  headers: { 'X-Requested-With': 'XMLHttpRequest' },
  // csrftoken变量名
  xsrfCookieName: 'bkitsm_csrftoken',
  // cookie中的csrftoken信息名称
  xsrfHeaderName: 'X-CSRFToken',
  withCredentials: true,
});

if (location.hash.indexOf('token') !== -1) {
  const token = location.hash.split('token=')[1].split('&')[0];
  sessionStorage.setItem('itsm_token', token);
}
bus.$on('processData', (response) => {
  const permissions = response.data.permission;
  let isViewApply = false;
  let viewType = 'other';
  if (permissions.actions.find((item) => item.id === 'project_view')) {
    viewType = 'project';
    isViewApply = true;
  } else {
    isViewApply = permissions.actions.some((item) => ['project_view', 'operational_data_view'].includes(item.id));
  }
  if (isViewApply) {
    bus.$emit('togglePermissionApplyPage', true, viewType, permissions);
  } else {
    bus.$emit('showPermissionModal', permissions);
  }
});

/**
 * request interceptor
 */
instance.interceptors.request.use(
  (config) => {
    // 添加工单查看权限
    const token = sessionStorage.getItem('itsm_token');
    if (token && config.url.indexOf('ticket/') === 0) {
      const prefix = config.url.indexOf('?') === -1 ? '?' : '&';
      config.url += `${prefix}token=${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

instance.interceptors.response.use(
  (response) => {
    // status >= 200 && status <= 505
    if ('result' in response.data && !response.data.result && 'message' in response.data) {
      window.app.$bkMessage({
        message: response.data.message,
        theme: 'error',
      });
    }
    if (!response.data || typeof response.data === 'string') {
      const msg = window.app.$t('m.js["接口请求异常，请联系管理员"]');
      console.warn(window.app.$t('m.js["接口异常，"]'), window.app.$t('m.js["HTTP状态码："]'), response.status);
      if (!response.data) {
        console.error(msg);
      }
      response.data = {
        code: response.status,
        msg,
      };
    } else if (response.status > 300) {
      if (response.status !== 499) {
        console.error(window.app.$t('m.js["HTTP请求出错，状态码为："]'), response.status);
        console.warn(window.app.$t('m.js["请求信息："]'), response);
      }
      switch (response.status) {
        case 401: {
          // 登录控制
          const data = response.data;
          if (data.has_plain) {
            topWindow.BLUEKING.corefunc.open_login_dialog(
              data.login_url,
              data.width,
              data.height,
              response.config.method
            );
          }
          break;
        }
        case 403: {
          // 权限控制
          bus.$emit('api-error:user-permission-denied');
          break;
        }
        case 502: {
          bus.$emit('api-error:application-deployed');
          break;
        }
        case 499: {
          if (response.config.url.match(/^(ticket\/receipts\/)*[0-9]*\/$/)) {
            if ('step_id' in response.config.params) {
              if (response.config.params.step_id) {
                bus.$emit('getIsProcessStatus', response);
              } else {
                bus.$emit('processData', response);
              }
            } else {
              bus.$emit('processData', response);
            }
          } else {
            bus.$emit('processData', response);
          }
          break;
        }
      }
      let msg = response.statusText;
      if (response.data && response.data.message) {
        msg = response.data.message;
      }
      response.data = {
        code: response.status,
        msg,
      };
    }

    if (response.request.responseURL.includes('/api/plugin_service/')) {
      return response;
    }

    if (response.data.code !== 'OK' && response.data.code !== 0) {
      if (response.data.message) {
        response.data.msg = response.data.message;
      } else if (response.data.messages) {
        if (checkDataType(response.data.messages) === 'Object') {
          const messages = [];
          for (const key in response.data.messages) {
            messages.push(response.data.messages[key]);
          }
          response.data.msg = messages.join('; ');
        } else if (checkDataType(response.data.messages) === 'Array') {
          response.data.msg = response.data.messages.join(';');
        } else {
          response.data.msg = response.data.message;
        }
      }

      if (response.data.code === 'NGINX_SETTING_ERROR') {
        bus.$emit('show-nginx-modal');
      }

      return Promise.reject(response);
    }

    return response;
  },
  (error) => Promise.reject(error)
);

Vue.prototype.$http = instance;

export default instance;
