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
  <div class="circulation-panel">
    <div class="btn-area">
      <span class="cancel-btn" @click="$emit('cancel')">取消</span>
      <van-button type="primary" class="confirm-btn" @click="onConfirm">确定</van-button>
    </div>
    <div class="processor-wrap">
      <transfer-order
        v-model:firstInfo="formData.processorsType"
        v-model:secondInfo="formData.processors"
        :first-include-list="includeList.firstIncludeList"
        :second-include-list="includeList.secondIncludeList"
        :title="transferTitle" />
    </div>
    <template v-if="isDelive">
      <van-field
        v-model="formData.reason"
        class="reason-textarea"
        type="textarea"
        placeholder="请输入转单原因"
        maxlength="200"
        rows="8"
        show-word-limit />
      <div class="fast-select">
        <span
          v-for="(item, index) in fastReason"
          :Key="index"
          class="reason-item"
          @click="formData.reason = item">
          {{ item }}
        </span>
      </div>
    </template>
  </div>
</template>
<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue'
import TransferOrder from '../../components/common/transferOrder/index.vue'
import emitter from '../../utils/emitter'

export default defineComponent({
  name: 'CirculationPanel',
  components: {
    TransferOrder
  },
  props: {
    operate: {
      type: Object,
      default: () => ({})
    },
    node: {
      type: Object,
      default: () => ({})
    },
    isBizNeed: { // 单据是否关联业务
      type: Boolean,
      default: false
    }
  },
  emits: {
    cancel: null,
    confirm: formData => !!formData
  },
  setup(props, { emit }) {
    const { operate, node, isBizNeed } = toRefs(props)
    const { processors_type: processorsType } = node.value
    const isDelive = computed<boolean>(() => operate.value.key === 'DELIVER') // 是否为转单
    const word = isDelive.value ? '转单' : '派单'
    const transferTitle = {
      firstTitle: `${word}至`,
      secondTitle: `${word}人`,
      popupTitle: `选择${word}人`
    }
    const formData = reactive({
      processorsType,
      processors: [],
      reason: ''
    })
    const fastReason = ['理由不充分', '时间问题', '更换处理人']

    const onConfirm = () => {
      const { processorsType, processors, reason } = formData

      if (processorsType === '') { // 角色类型不能为空
        emitter.emit('notify', { type: 'warning', message: `请选择${isDelive.value ? '转单' : '派单'}角色类型` })
        return
      }

      if (!['EMPTY', 'OPEN', 'STARTER', 'BY_ASSIGNOR', 'STARTER_LEADER'].includes(processorsType) && processors.length === 0) {
        emitter.emit('notify', { type: 'warning', message: `请选择${isDelive.value ? '转单' : '派单'}角色` })
        return
      }

      if (isDelive.value && reason === '') {
        emitter.emit('notify', { type: 'warning', message: '请填写转单原因' })
        return
      }

      const data = {
        reason,
        processors_type: processorsType,
        processors: processors.length > 0 ? processors.join(',') : ''
      }
      emit('confirm', data)
    }

    const includeList = reactive<{ firstIncludeList: string [], secondIncludeList: any [] }>({
      firstIncludeList: [],
      secondIncludeList: []
    })
    const initData = () => {
      // 初始化 分派/转单 类型
      const specialType = ['OPEN', 'BY_ASSIGNOR']
      const {
        assignors, // 分派人（username + display_name）
        assignors_type: assignorsType, // 分派类型
        origin_assignors: originAssignors, // 原始分派人(id)
        delivers,
        delivers_type: deliversType,
        origin_delivers: originDelivers
      } = node.value

      const handler = isDelive.value ? delivers : assignors
      const originHandler = isDelive.value ? originDelivers : originAssignors
      const handlerType = isDelive.value ? deliversType : assignorsType

      if (specialType.includes(handlerType)) { // 特殊类型, 不限制选择
        includeList.firstIncludeList = ['PERSON', 'GENERAL', 'ORGANIZATION']
        includeList.secondIncludeList  = []
        if (!isDelive.value) { // 分派时
          includeList.firstIncludeList.push('STARTER')
        }
        if (isBizNeed.value) { // 关联业务
          includeList.firstIncludeList.push('CMDB')
        }
      } else if (handlerType === 'PERSON') { // 类型为个人, 只能在 originHandler 中选
        includeList.firstIncludeList = ['PERSON']
        includeList.secondIncludeList = [
          { type: handlerType, list: originHandler.split(',') }
        ]
      } else { // 其他默认类型（通用角色、组织架构、cmdb 角色...）, PERSON 只能在 handler 中选，`handlerType` 只能在 originHandler 中选
        includeList.firstIncludeList = ['PERSON', handlerType]
        // eslint-disable-next-line no-case-declarations
        const includePerson = handler.split(',').map((fullName: string) => fullName.replace(/\(.+\)/g, ''))
        includeList.secondIncludeList = [
          { type: 'PERSON', list: includePerson },
          { type: handlerType, list: originHandler.split(',') }
        ]
      }
    }
    initData()

    return { isDelive, formData, includeList, transferTitle, fastReason, onConfirm, initData }
  }
})
</script>
<style lang="postcss" scoped>
  .btn-area {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 24px 40px;
    line-height: 1;
    background: #ffffff;
  }
  .cancel-btn {
    font-size: 32px;
    color: #63656e;
  }
  .confirm-btn {
    padding: 0 34px;
    height: 64px;
    background: #3a84ff;
    color: #ffffff;
    font-size: 26px;
    border-radius: 6px;
  }
  .processor-wrap {
    background: #ffffff;
  }
  .reason-textarea {
    font-size: 28px;
    color: #8c8c8c;
    line-height: 48px;
    &:after {
      border: none;
    }
  }
  .fast-select {
    padding: 12px 40px 0;
    background: #ffffff;
    border-top: 1px solid #e6e6e6;
    .reason-item {
      display: inline-block;
      margin-right: 16px;
      margin-bottom: 16px;
      padding: 4px 9px;
      line-height: 30px;
      font-size: 24px;
      color: #63656e;
      background: #f0f1f5;
    }
  }
</style>
