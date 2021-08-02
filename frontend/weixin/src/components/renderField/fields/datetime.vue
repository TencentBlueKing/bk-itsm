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
  <div class="datetime-field">
    <van-field
      v-if="!isViewMode"
      v-model="state.value"
      name="datepicker"
      readonly
      :error="error"
      :clickable="!isViewMode"
      :label="item.name"
      :required="isRequire"
      placeholder="请选择时间"
      @click="handleFieldClick" />
    <p v-else class="common-view-field">
      <label class="view-label">{{ item.name }}</label>
      <span class="view-value">{{ state.value || '--' }}</span>
    </p>
    <van-popup v-model:show="state.showPicker" position="bottom">
      <van-datetime-picker
        type="datetime"
        :model-value="state.dateValue"
        :formatter="formatter"
        :min-date="state.minDate"
        @confirm="onConfirm"
        @cancel="state.showPicker = false" />
    </van-popup>
  </div>
</template>
<script lang="ts">
import { defineComponent, toRefs, reactive, computed } from 'vue'
import dayjs from 'dayjs'

export default defineComponent({
  name: 'FieldDateTime',
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
  emits: ['change'],
  setup(props, { emit }) {
    const { item, isViewMode } =  toRefs(props)
    const isRequire = computed(() => item.value.validate_type === 'REQUIRE')
    const state = reactive({
      value: item.value.value,
      dateValue: new Date(item.value.value),
      minDate: dayjs().subtract(3, 'year').toDate(),
      showPicker: false
    })
    const checkInfo = reactive({
      error: false,
      errorMessage: ''
    })

    const dateStrMap = {
      year: '年',
      month: '月',
      day: '日',
      hour: '时',
      minute: '分'
    }

    const formatter = (type, val) => `${val}${dateStrMap[type]}`

    const handleFieldClick = () => {
      if (!isViewMode.value) {
        state.showPicker = true
      }
    }

    const onConfirm = (val) => {
      state.value = dayjs(val).format('YYYY-MM-DD HH:mm:ss')
      state.dateValue = new Date(val)
      state.showPicker = false
      emit('change', state.value)
    }

    // 校验规则
    const validate = (): boolean => {
      if (isRequire.value && !state.value) {
        checkInfo.error = true
        checkInfo.errorMessage = '必填字段'
        return false
      }
      checkInfo.error = false
      checkInfo.errorMessage = ''
      return true
    }

    return {
      state,
      isRequire,
      handleFieldClick,
      onConfirm,
      validate,
      formatter,
      ...toRefs(checkInfo)
    }
  }
})
</script>
<style lang="postcss" scoped>
  .datetime-field {
    width: 100%;
  }
</style>

