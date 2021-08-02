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
  <div class="radio-box">
    <van-field
      v-if="!isViewMode"
      :label="item.name"
      :required="isRequire"
      :error="error"
      :error-message="errorMessage"
      class="vant-radio-correct">
      <template #input>
        <van-radio-group v-model="checked" direction="horizontal">
          <van-radio
            v-for="(choiceItem, index) in item.choice"
            :key="index"
            :name="choiceItem.key">
            {{ choiceItem.name }}
          </van-radio>
        </van-radio-group>
      </template>
    </van-field>
    <p v-else class="common-view-field">
      <label class="view-label">{{ item.name }}</label>
      <span class="view-value">{{ isSelectText || '--' }}</span>
    </p>
  </div>
</template>
<script lang="ts">
import { defineComponent, ref, toRefs, reactive, computed, watch } from 'vue'

interface IFieldInfo {
  id: number,
  name: string,
  key: string
}

export default defineComponent({
  name: 'FieldRadio',
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
    const { item } =  toRefs(props)
    const checked = ref('')
    const isRequire = computed(() => item.value.validate_type === 'REQUIRE')
    const isSelectText = ref('')

    // 获取默认选中的
    const getDeafaultCheck = () => {
      const { choice, value } = item.value
      if (value) {
        const checkedList = value.split(',')
        choice.forEach((item: IFieldInfo) => {
          if (checkedList.includes(item.key)) {
            isSelectText.value = item.name
            checked.value = item.key
          }
        })
      }
    }
    getDeafaultCheck()

    watch(checked, (val) => {
      emit('change', val)
    })

    const checkInfo = reactive({
      error: false,
      errorMessage: ''
    })
    // 校验规则
    const validate = (): boolean =>  {
      if (isRequire.value && !checked.value) {
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
      checked,
      isRequire,
      isSelectText,
      ...toRefs(checkInfo),
      getDeafaultCheck,
      validate
    }
  }
})
</script>
<style lang="postcss" scoped>
  .radio-box {
    font-size: 12px;
    height: 100%;
    width: 100%;
    /deep/ .van-field__label {
      line-height: 36px;
    }
    /deep/ .van-radio-group {
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      width: 100%;
      .van-radio {
        width: 50%;
        margin-right: 0;
        .van-radio__icon {
          font-size: 28px;
        }
        .van-radio__label {
          line-height: 36px;
          overflow:hidden;
          text-overflow:ellipsis;
          white-space:nowrap;
          color: #969799;
        }
      }
    }
  }
</style>
