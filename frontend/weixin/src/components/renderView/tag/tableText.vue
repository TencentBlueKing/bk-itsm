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
  <p
    :class="[
      'table-text',
      { 'has-children': form.children && form.children.length }
    ]"
    @click="onInnerLinkClick">
    <label>{{ form.label }}</label>
    <span v-if="!Array.isArray(form.value)">{{ form.value }}</span>
    <template v-else>
      <TableText v-for="(item, i) in form.value" :key="i" :form="item" />
    </template>
  </p>
</template>

<script lang="ts">
import { inject, toRefs } from 'vue'
import { IInnerFormInstance } from '../types'

export default {
  name: 'TableText',
  props: {
    form: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props) {
    const { form }  = toRefs(props)
    const innerFormInstance = inject('innerFormInstance')
    const onInnerLinkClick = (): void => {
      if (!form.value.children || !form.value.children.length) {
        return
      }
      let titleVal = form.value.value
      if (Array.isArray(form.value.value)) {
        titleVal = form.value.value.map((item: any) => (item.label + item.value)).join('')
      }
      (innerFormInstance as IInnerFormInstance).pushToInnerForms({
        title: `${form.value.label || ''}${titleVal}`,
        formData: form.value.children
      })
    }
    return {
      // eslint-disable-next-line vue/no-dupe-keys
      form,
      onInnerLinkClick
    }
  }
}
</script>
<style lang="postcss">
.table-text {
  > label {
    color: #63656e;
  }
}
.has-children {
  > label, > span, > .table-text {
    color: #3A84FF;
  }
}
</style>
