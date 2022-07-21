<!--
  - Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.
  - Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
  - BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
  -
  - License for BK-ITSM 蓝鲸流程服务:
  - -------------------------------------------------------------------
  -
  - Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
  - documentation files (the "Software"), to deal in the Software without restriction, including without limitation
  - the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
  - and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  - The above copyright notice and this permission notice shall be included in all copies or substantial
  - portions of the Software.
  -
  - THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
  - LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
  - NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  - WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  - SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
  -->

<template>
  <div
    :class="['tag-text', { 'active-link': hasChildren }]" @click="onClick">
    <div v-if="Array.isArray(value)">
      <p class="text-block" v-for="(item, index) in value" :key="index">
        <label v-if="item.label" class="label">
          {{ item.label }}
          <i v-if="item.desc || desc" v-bk-tooltips="item.desc || desc" class="bk-itsm-icon icon-itsm-icon-help"></i>
        </label>
        <span class="value">{{ item.value }}</span>
      </p>
    </div>
    <p v-else>
      <label v-if="label" class="label">
        {{ label }}
        <i v-if="desc" v-bk-tooltips="desc" class="bk-itsm-icon icon-itsm-icon-help"></i>
      </label>
      <span class="value">{{ value }}</span>
    </p>
  </div>
</template>

<script>
  import { getFormMixins } from '../formMixins';
  import Sideslider from '../sideslider/sideslider.js';

  const textAttrs = {
    styles: {
      type: Object,
      default: () => ({}),
    },
    value: {
      type: [String, Array],
      default: '',
    },
  };
  export default {
    name: 'TagText',
    mixins: [getFormMixins(textAttrs)],
    data() {
      return {};
    },
    computed: {
      hasChildren() {
        return this.form.children && Array.isArray(this.form.children) && !!this.form.children.length;
      },
    },
    methods: {
      onClick() {
        if (!this.hasChildren) {
          return;
        }
        let title = '';
        if (Array.isArray(this.value)) {
          title = this.value.map(item => (item.label || '') + item.value).join(',');
        } else {
          title = (this.label || '') + this.value;
        }
        const context = this.getContext();
        if (context.config && context.config.mode === 'combine') {
          const topViewItem = this.getTopViewItem();
          topViewItem.appendCrumbsItem(title, this.form.children);
        } else {
          Sideslider({
            title,
            formData: this.form.children,
            context,
          });
        }
      },
    },
  };
</script>

<style lang="scss" scoped>
.tag-text {
    display: flex;
    color: #63656e;
    font-size: 12px;
    text-align: left;
    &.active-link {
        color: #3a84ff;
        cursor: pointer;
    }
    .label {
        flex: 0 0 60px;
        width: 60px;
        font-weight: bold;
        word-break: break-all;
    }
    .value {
        margin-left: 4px;
    }
    .text-block {
        line-height: 32px;
        display: block;
        width: 100%;
    }
}
</style>
