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
  <div class="step-wrap" :class="{ 'is_current': isCurrentNode }">
    <!-- 展开/收起按钮 -->
    <template v-if="node.type === 'mobile-steps-button'">
      <div class="step-icon">
        <i class="itsm-mobile-icon" :class="isExtendSteps ? 'icon-arrows-up' : 'icon-arrows-down'" />
      </div>
      <span class="toggle-btn" @click="$emit('toggle-extend')">
        {{ isExtendSteps ? '收起前置节点' : '展开前置节点' }}
      </span>
    </template>
    <!-- 任务节点 -->
    <template v-else>
      <div class="step-icon">
        <van-icon v-if="!isCurrentNode" name="passed" />
        <span v-else class="current-node-icon" />
      </div>
      <!-- 已处理节点 -->
      <processed-node
        v-if="!isCurrentNode"
        :node="node"
        :is-multiple-process-node="isMultipleProcessNode"
        :is-single-process-node="isSingleProcessNode" />
      <!-- 当前处理节点 -->
      <template v-else>
        <!-- 当前处理节点处理信息 -->
        <current-node-info :node="node" :can-operate="node.can_operate" />
        <!-- 任务列表 -->
        <task-list v-if="node.can_create_task || node.can_execute_task" :id="id" />
        <!-- 表单编辑区域 -->
        <render-field
          v-if="node.can_operate"
          ref="renderField"
          :is-view-mode="!isCurrentNode"
          :fields="node.fields"
          :class="['step-render-form', { 'has-field': node.fields.length }]" />
        <!-- 操作按钮区域 -->
        <div v-if="isCurrentNode && node.operations.length > 0 && node.can_operate" class="operation-btns">
          <template v-for="(operate, index) in node.operations" :key="operate.key">
            <van-button
              v-if="operate.can_operate && !['SUSPEND', 'TERMINATE'].includes(operate.key)"
              :type="index === 0 ? 'primary' : 'default'"
              plain
              @click="handleOperateBtnClick(operate)">
              {{ operate.name }}
            </van-button>
          </template>
        </div>
      </template>
    </template>
    <div v-if="isCirculationPanelShow" class="circulation-panel-wrap">
      <circulation-panel
        :node="node"
        :operate="operate"
        :is-biz-need="isBizNeed"
        @confirm="handleCirculation"
        @cancel="isCirculationPanelShow = false" />
    </div>
    <van-dialog
      v-model:show="isSubmitDialogShow"
      class-name="common-dialog"
      confirm-button-color="#3a84ff"
      cancel-button-color="#3a84ff"
      :title="submitDialogTitle"
      :show-cancel-button="true"
      :before-close="beforeSubmitClose">
      <div class="van-dialog__message">{{ submitDialogMsg }}</div>
    </van-dialog>
  </div>
</template>
<script lang="ts">
import { computed, defineComponent, ref, toRefs } from 'vue'
import { useStore } from 'vuex'
import { Toast } from 'vant'
import RenderField from '../../components/renderField/index.vue'
import TaskList from './taskList.vue'
import CirculationPanel from './circulationPanel.vue'
import ProcessedNode from './processedNode.vue'
import CurrentNodeInfo from './currentNodeInfo.vue'
import { IOperation } from '../../typings/ticket'

export default defineComponent({
  name: 'StepItem',
  components: {
    RenderField,
    CirculationPanel,
    ProcessedNode,
    CurrentNodeInfo,
    TaskList
  },
  props: {
    status: { // 单据状态
      type: String,
      default: ''
    },
    id: { // 单据id
      type: Number,
      default: 0
    },
    node: { // 当前节点详情
      type: Object,
      default: () => ({})
    },
    isExtendSteps: {
      type: Boolean,
      default: false
    },
    isBizNeed: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update-nodes', 'toggle-extend'],
  setup(props, { emit }) {
    const store = useStore()
    const { node, status, id: ticketId } = toRefs(props)
    const isExtended = ref(false) // 是否展开节点详情
    const operate = ref<IOperation>({})
    const isSubmitDialogShow = ref(false)
    const submitDialogTitle = ref('')
    const submitDialogMsg = ref('')
    const isCirculationPanelShow = ref<boolean>(false)
    const renderField = ref(null) // 字段类型组件模板引用

    // 是否为当前处理节点
    const isCurrentNode = computed(() => !['REVOKED', 'FINISHED'].includes(status.value) && node.value.status === 'RUNNING')
    // 是否为审批多签、顺序会签节点
    const isMultipleProcessNode = computed(() => {
      const { type, is_sequential, is_multi } = node.value
      return (type === 'SIGN' && is_sequential) || (type === 'APPROVAL' && is_multi)
    })
    // 是否为审批或签、随机会签节点
    const isSingleProcessNode = computed(() => {
      const { type, is_sequential, is_multi } = node.value
      return (type === 'SIGN' && !is_sequential) || (type === 'APPROVAL' && !is_multi)
    })

    // 提交操作按钮
    const beforeSubmitClose = async (action) => {
      if (action === 'cancel') {
        isSubmitDialogShow.value = false
      } else {
        if (operate.value.key === 'TRANSITION') { // 通过
          const fields = renderField.value.getValue()
          const params = {
            state_id: node.value.state_id,
            fields: fields.map((item) => {
              const { type, value, id, key, choice } = item
              return {
                id,
                key,
                type,
                choice,
                value: type === 'FILE' ? value.toString() : value
              }
            })
          }
          try {
            await store.dispatch('ticket/proceed', { id: ticketId.value, params })
            emit('update-nodes')
          } catch (error) {
            console.error(error)
          } finally {
            operate.value = {}
            isSubmitDialogShow.value = false
          }
        } else if (operate.value.key === 'CLAIM') { // 认领
          const params = {
            state_id: node.value.state_id,
            action_type: 'CLAIM',
            processors: window.username,
            processors_type: 'PERSON'
          }
          try {
            await store.dispatch('ticket/operate', { id: ticketId.value, params })
            Toast.success({
              message: '提交成功',
              icon: 'passed',
              className: 'common-toast'
            })
            emit('update-nodes')
          } catch (error) {
            console.log(error)
          } finally {
            operate.value = {}
            isSubmitDialogShow.value = false
          }
        }
      }
    }

    // 点击操作按钮回调
    const handleOperateBtnClick = (opt) => {
      operate.value = opt
      const isTransition = operate.value.key === 'TRANSITION' // 是否是提交操作
      let fieldValid = true
      if (isTransition) {
        if (renderField.value.hasNotSupportRequiredField()) {
          Toast({
            message: '有不支持的必填字段，请至PC端处理'
          })
        }
        fieldValid = renderField.value.validate()
      }
      if (!fieldValid) {
        return
      }

      if (['TRANSITION', 'CLAIM'].includes(operate.value.key)) {
        isSubmitDialogShow.value = true
        submitDialogTitle.value = isTransition ? '是否提交' : '是否认领'
        submitDialogMsg.value = isTransition ? '提交后，流程将转入下一环节，当前提交的部分内容将无法修改' : '执行认领操作后，单据将流入我的待办'
      } else if (['DELIVER', 'DISTRIBUTE'].includes(operate.value.key)) {
        isCirculationPanelShow.value = true
      }
    }
    // 提交转单、分派
    const handleCirculation = async (data) => {
      const params = {
        state_id: node.value.state_id,
        action_type: operate.value.key, // 转单/分派
        processors: data.processors,
        processors_type: data.processors_type
      }
      if (operate.value.key === 'DELIVER') {
        params.action_message = data.reason
      }

      try {
        await store.dispatch('ticket/operate', { id: ticketId.value, params })
        emit('update-nodes')
      } catch (error) {
        console.error(error)
      } finally {
        isCirculationPanelShow.value = false
      }
    }

    return {
      isExtended,
      isCurrentNode,
      isMultipleProcessNode,
      isSingleProcessNode,
      isCirculationPanelShow,
      isSubmitDialogShow,
      submitDialogTitle,
      submitDialogMsg,
      renderField,
      operate,
      beforeSubmitClose,
      handleOperateBtnClick,
      handleCirculation
    }
  }
})
</script>
<style lang="postcss" scoped>
  .step-wrap {
    position: relative;
    padding: 34px 40px 48px 90px;
    &:before {
      position: absolute;
      box-sizing: border-box;
      content: " ";
      width: 2px;
      height: 100%;
      pointer-events: none;
      top: 0;
      left: 50px;
      background: #699df4;
      z-index: 1;
    }
    &.is_current {
      background: #f5f6fa;
      .step-render-form {
        margin: 10px 0;
        padding: 0 24px;
        background: #fff;
        &.has-field {
          border: 1px solid #d8d8d8;
        }
      }
      .step-icon {
        background: #3a84ff;
      }
      .node-name {
        font-weight: 700;
        color: #222222;
      }
    }
    &:first-of-type:before {
      top: 38px;
    }
    &:last-of-type:before {
      height: 38px;
    }
    .step-icon {
      position: absolute;
      left: 38px;
      top: 38px;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 24px;
      width: 24px;
      border-radius: 50%;
      background: #ffffff;
      color: #3ecb55;
      z-index: 2;
      .current-node-icon {
        display: inline-block;
        width: 12px;
        height: 12px;
        border: 2px solid #ffffff;
        border-radius: 50%;
      }
      i {
        font-size: 24px;
      }
    }
    .toggle-btn {
      display: inline-block;
      padding: 0 20px;
      min-width: 190px;
      height: 40px;
      line-height: 40px;
      font-size: 22px;
      color: #3a84ff;
      border: 1px solid #3a84ff;
      border-radius: 20px;
      text-align: center;
    }
    .node-name {
      position: relative;
      margin-bottom: 18px;
      padding-right: 40px;
      line-height: 44px;
      color: #63656e;
      font-size: 28px;
      .van-icon {
        position: absolute;
        right: 0px;
        top: 10px;
        font-size: 32px;
        color: #979ba5;
      }
    }
    .current-processors {
      display: flex;
      justify-content: space-between;
      font-size: 24px;
      color: #979ba5;
      text-align: left;
      line-height: 40px;
      .label {
        width: 240px;
        white-space: nowrap;
      }
      .value {
        width: calc(100% - 240px);
        text-align: right;
        word-break: break-all;
        &.tag-card {
          text-align: left;
        }
      }
      .processor-item {
        display: inline-flex;
        align-items: center;
        margin-right: 8px;
        margin-bottom: 8px;
        padding: 8px 16px;
        background: #ffffff;
        color: #63656e;
        font-size: 24px;
        border-radius: 2px;
        &.running {
          color: #3a84ff;
        }
      }
    }
    .operation-btns {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      margin-top: 40px;
      .van-button {
        margin-bottom: 20px;
        width: 48%;
        height: 60px;
        font-size: 26px;
      }
    }
  }
  .circulation-panel-wrap {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    background: #f5f6fa;
    overflow: auto;
    line-height: initial;
    z-index: 1000;
  }
</style>
