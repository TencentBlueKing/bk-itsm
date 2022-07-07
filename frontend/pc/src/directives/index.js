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
import './cursor.js';
// 自定义 外点击/触发
Vue.directive('clickOut', {
  async bind(el, binding) {
    let cascaderFunction = '';
    const documentHandler = await async function (e) {
      if (!el.contains(e.target)) {
        if (!cascaderFunction) {
          cascaderFunction = binding.value;
        } else {
          await binding.value();
          await document.removeEventListener('click', documentHandler);
        }
      } else {
        // ...
      }
    };
    await document.addEventListener('click', documentHandler);
  },
  inserted() {
  },
  async update(el, binding) {
    let cascaderFunction = '';
    const documentHandler = await async function (e) {
      if (!el.contains(e.target)) {
        if (!cascaderFunction) {
          cascaderFunction = binding.value;
        } else {
          await binding.value();
          await document.removeEventListener('click', documentHandler);
        }
      } else {
        // ...
      }
    };
    await document.addEventListener('click', documentHandler);
  },
});
// 绑定值为True时 --》 html元素获取焦点
Vue.directive('focus', {
  update(el, { value }) {
    if (value) {
      el.focus();
    }
  },
});
// 添加自定义锚点 自动滚动到锚点 ??
Vue.directive('anchor', {
  bind(el, binding) {
    // 自定义属性：
    binding.value.el = el;
  },
  update() {
  },
  componentUpdated() {
  },
});
// 记录光标 index, 配合 u utils 方法使用
Vue.directive('cursorIndex', {
  bind: (el, binding) => {
    const dom = el.querySelector('textarea,input');
    if (dom) {
      const handlerFocus = () => {
        sessionStorage.removeItem('cursorIndex');
      };
      const handlerBlur = (e) => {
        const recordJson = {
          name: binding.value,
          start: e.target.selectionStart,
          end: e.target.selectionEnd,
        };
        sessionStorage.setItem('cursorIndex', JSON.stringify(recordJson));
      };
      dom.addEventListener('focus', handlerFocus, false);
      dom.addEventListener('blur', handlerBlur, false);
    }
  },
});

// 自动聚焦
Vue.directive('bk-focus', {
  inserted(el) {
    const dom = el.querySelector('textarea,input');
    if (['textarea', 'input'].includes(el.tagName)) {
      el.focus();
    } else if (dom) {
      dom.focus();
    }
  },
});
