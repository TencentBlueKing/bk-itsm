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

export const COMMON_ATTRS = {
  label: {
    type: String,
    required: false,
  },
  hiddenLabel: {
    type: Boolean,
    default: false,
  },
  form: {
    type: Object,
    default: () => ({}),
  },
  children: {
    type: [String, Array],
    required: false,
  },
  desc: {
    type: String,
    required: false,
  },
};
export function getFormMixins(attrs) {
  const privateProps = {}; // 继承属性
  for (const key in attrs) {
    if (key !== 'value') {
      privateProps[key] = attrs[key];
    }
  }
  return {
    props: {
      ...COMMON_ATTRS,
      ...privateProps,
    },
    inject: ['getContext'],
    data() {
      return {
        value: this.$attrs.value ? this.$attrs.value : attrs.value.default,
      };
    },
    methods: {
      /**
             * 获取最顶层 ViewItem 组件实例
             */
      getTopViewItem() {
        let vueTag = this;
        let isTop = false;
        while (!isTop) {
          if (vueTag.$parent && vueTag.$parent.isRootRenderView) {
            isTop = true;
          } else {
            vueTag = vueTag.$parent;
          }
        }
        return vueTag;
      },
    },
  };
}
