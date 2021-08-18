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
  <div class="process-steps">
    <step-item
      v-for="node in steps"
      :id="ticket.id"
      :key="`${node.id}_${node.status}`"
      :status="ticket.current_status"
      :is-biz-need="ticket.is_biz_need"
      :node="node"
      :is-extend-steps="isExtendSteps"
      @toggle-extend="toggleNodesExtend"
      @update-nodes="$emit('update-nodes')" />
  </div>
</template>
<script lang="ts">
import { defineComponent, PropType, ref, Ref, toRefs, watch } from 'vue'
import StepItem from './stepItem.vue'
import { INodeInfo, ITicketDetail } from '../../typings/ticket'

export default defineComponent({
  name: 'ProcessSteps',
  components: {
    StepItem
  },
  props: {
    nodeList: {
      type: Object as PropType<INodeInfo[]>,
      default: () => ({})
    },
    ticket: {
      type: Object as PropType<ITicketDetail>,
      default: () => ({})
    }
  },
  emits: ['update-nodes'],
  setup(props) {
    const steps = ref([])
    const isExtendSteps = ref(false)
    const { nodeList, ticket }: { nodeList: Ref<INodeInfo[]>, ticket: Ref<ITicketDetail[]> } = toRefs(props)

    const setSteps = () => {
      steps.value = []
      const currentStepNodes = nodeList.value.filter(item => item.status === 'RUNNING')
      const handledStepsLength = nodeList.value.length - currentStepNodes.length
      if (!ticket.value.is_over && ticket.value.current_status !== 'REVOKED' && handledStepsLength > 1) {
        if (!isExtendSteps.value) {
          const prevStep = nodeList.value[handledStepsLength - 1]
          steps.value.push(...[{ type: 'mobile-steps-button' }, prevStep, ...currentStepNodes])
        } else {
          steps.value.push(...[{ type: 'mobile-steps-button' }, ...nodeList.value])
        }
      } else {
        steps.value = nodeList.value.slice(0)
      }
    }

    const toggleNodesExtend = () => {
      isExtendSteps.value = !isExtendSteps.value
      setSteps()
    }

    watch(nodeList, () => {
      setSteps()
    }, { deep: true })

    watch(ticket, () => {
      setSteps()
    }, { deep: true })

    setSteps()
    return { steps, isExtendSteps, toggleNodesExtend }
  }
})
</script>
