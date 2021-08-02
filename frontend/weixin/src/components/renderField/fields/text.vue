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
  <van-field
    v-if="!isViewMode"
    v-model="val"
    type="textarea"
    rows="4"
    :required="isRequire"
    :error="error"
    :label="item.name"
    :placeholder="`请输入${item.name}`"
    @blur="validate" />
  <p v-else class="common-view-field">
    <label class="view-label">{{ item.name }}</label>
    <span class="view-value">{{ item.value || '--' }}</span>
  </p>
</template>
<script lang="ts">
import { defineComponent, toRefs, ref, reactive, computed, watch } from 'vue'

export default defineComponent({
  name: 'FieldText',
  props: {
    item: {
      type: Object,
      default: () => ({})
    },
    isViewMode: {
      type: Boolean,
      default: false
    }
  },
  emits: [
    'change'
  ],
  setup(props, { emit }) {
    const { item } =  toRefs(props)
    const val = ref<string>('')
    const isRequire = computed(() => item.value.validate_type === 'REQUIRE')
    val.value = (item as any).value.value

    // value change
    watch(val, (val) => {
      emit('change', val)
    })

    const checkInfo = reactive({
      error: false,
      errorMessage: ''
    })
    // 校验规则
    const validate = (): boolean => {
      if (isRequire.value && !val.value) {
        checkInfo.error = true
        checkInfo.errorMessage = '必填字段'
        return false
      }
      checkInfo.error = false
      checkInfo.errorMessage = ''
      return true
    }

    return {
      // eslint-disable-next-line vue/no-dupe-keys
      item,
      val,
      validate,
      isRequire,
      ...toRefs(checkInfo)
    }
  }
})
</script>
<style lang="postcss" scoped>

</style>
