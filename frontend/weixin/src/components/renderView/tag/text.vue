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
  <template v-if="form.children && form.children.length">
    <h4 class="header-title">{{ form.label }}</h4>
    <p
      v-for="(item, index) in form.children"
      :key="index"
      class="common-view-field inner-text">
      <label class="view-label">{{ item.label }}</label>
      <span class="view-value">{{ item.value }}</span>
    </p>
  </template>
  <p v-else class="common-view-field">
    <label class="view-label">{{ form.label }}</label>
    <span class="view-value">{{ form.value }}</span>
  </p>
</template>

<script lang="ts">
import { toRefs } from 'vue'
export default {
  name: 'ViewText',
  props: {
    form: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props) {
    const { form }  = toRefs(props)
    return {
      // eslint-disable-next-line vue/no-dupe-keys
      form
    }
  }
}
</script>
<style lang="postcss" scoped>
.tag-text {
  box-sizing: border-box;
  color: #63656e;
  font-size: 24px;
  line-height: 64px;
  &.inner {
    padding-left: 40px;
  }
}
.inner-text {
  padding: 0 40px;
}
</style>
