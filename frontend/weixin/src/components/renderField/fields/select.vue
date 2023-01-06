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
  <div class="select">
    <van-field
      v-if="!isViewMode"
      v-model="selectInfo.name"
      :label="item.name"
      :required="isRequire"
      :error="error"
      :error-message="errorMessage"
      :disabled="item.is_readonly"
      placeholder="请选择"
      @click="handelerOpenPopup" />
    <p v-else class="common-view-field">
      <label class="view-label">{{ item.name }}</label>
      <span
        class="view-value"
        :class="{
          'highlight': item.meta && item.meta.code === 'APPROVE_RESULT' && item.value === 'false'
        }">
        {{ selectInfo.name || '--' }}
      </span>
    </p>
    <!-- popup弹出层 -->
    <van-popup v-model:show="showPicker" round position="bottom">
      <van-picker
        ref="pickerRef"
        show-toolbar
        :title="`请选择${item.name}`"
        :columns="item.choice"
        :default-index="columnIndex"
        value-key="name"
        @cancel="onCancel"
        @confirm="onConfirm" />
    </van-popup>
  </div>
</template>
<script lang="ts">
import { defineComponent, toRefs, ref, nextTick, reactive, computed, watch } from 'vue'

interface IFieldInfo {
  id?: number,
  name: string,
  key: string
}
export default defineComponent({
  name: 'FieldSelect',
  props: {
    item: {
      type: Object,
      default: () => ({})
    },
    isViewMode: {
      type: Boolean,
      default: false
    },
    highlightRefuse: {
      type: Boolean,
      default: false
    }
  },
  emits: ['change'],
  setup(props, { emit }) {
    const { item } =  toRefs(props)
    const showPicker = ref(false)
    const columnIndex = ref(0)
    const pickerRef = ref(null)
    const selectInfo = ref<IFieldInfo>({
      id: 0,
      name: '',
      key: ''
    })
    const isRequire = computed(() => item.value.validate_type === 'REQUIRE')
    // 设置默认值
    const setDefaultSelectValue = () => {
      const { choice, value } = item.value
      if (value) {
        const info = choice.find((column: IFieldInfo) => String(column.key) === String(value))
        if (info) {
          selectInfo.value = info
        } else {
          selectInfo.value = {
            name: value,
            key: value
          }
        }
      }
    }
    setDefaultSelectValue()
    watch(item.value, (value) => {
      if (value.key === 'priority' && value.allFill) {
        setDefaultSelectValue()
      }
    }, { deep: true })
    const handelerOpenPopup = () => {
      if (item.value.is_readonly) return
      showPicker.value = true
      nextTick(() => {
        const { choice } = item.value
        const { key } = selectInfo.value
        columnIndex.value = choice.findIndex((column: IFieldInfo) => column.key === key)
        pickerRef.value.setColumnIndex(0, columnIndex.value)
      })
    }

    const onConfirm = (val) => {
      showPicker.value = false
      selectInfo.value = val
      emit('change', selectInfo.value.key)
    }

    const onCancel = () => {
      showPicker.value = false
    }

    const checkInfo = reactive({
      error: false,
      errorMessage: ''
    })
    // 校验规则
    const validate = (): boolean => {
      if (isRequire.value && !selectInfo.value.key) {
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
      showPicker,
      columnIndex,
      pickerRef,
      selectInfo,
      isRequire,
      ...toRefs(checkInfo),
      handelerOpenPopup,
      onConfirm,
      onCancel,
      validate
    }
  }
})
</script>
<style lang="postcss" scoped>
  .select {
    width: 100%;
    .view-value.highlight {
      color: #ff9c01;
    }
    /deep/ .van-cell__title {
      line-height: 4.8vw;
    }
    /deep/ .van-picker {
      .van-picker__toolbar {
        height: 112px;
        button {
          font-size: 32px;
        }
        .van-picker__title {
          font-size: 32px;
          font-weight: 500;
          line-height: 48px;
          color: #262626;
        }
        .van-picker__confirm {
          color: #3a84ff;
        }
      }
      .van-picker-column {
        font-size: 32px;
        color: #262626;
        line-height: 40px;
      }
    }
  }
</style>
