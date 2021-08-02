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
  <van-skeleton
    :row="16"
    :row-width="['100%', '100%', '30%', '30%', '0%', '100%', '100%', '100%', '0%', '100%']"
    :loading="detailLoading">
    <div ref="ticketPage" class="ticket-page">
      <ticket-base-info :ticket-detail="ticketDetail" @revoke="onTicketRevoke" />
      <create-ticket-info
        :ticket-detail="ticketDetail"
        :fields="firstNodeFields"
        :all-fields="allFields" />
      <div ref="processDetail" class="process-detail" :class="{ 'title-fixed': processTitleFixed }">
        <div class="process-detail-title" @click="handleClickFixedTitle">
          <h4 class="">处理进度</h4>
        </div>
        <process-steps
          v-if="!nodeListLoading"
          :node-list="nodeList"
          :ticket="ticketDetail"
          @update-nodes="getNodeList" />
        <van-loading v-else class="node-list-loading" size="40" color="#3a84ff" />
      </div>
    </div>
    <div class="go-back-home" @click="$router.push({ name: 'homeDefault' })">
      <i class="itsm-mobile-icon icon-index" />
    </div>
  </van-skeleton>
</template>
<script lang="ts">
import { defineComponent, ref, Ref, onBeforeUnmount, nextTick } from 'vue'
import { useStore } from 'vuex'
import { useRoute } from 'vue-router'
import throttle from 'lodash/throttle'
import ticketBaseInfo from './ticketBaseInfo.vue'
import createTicketInfo from './createTicketInfo.vue'
import processSteps from './processSteps.vue'
import { IField } from '../../typings/fields'
import { INodeInfo } from '../../typings/ticket'

export default defineComponent({
  name: 'Ticket',
  components: {
    ticketBaseInfo,
    createTicketInfo,
    processSteps
  },
  setup() {
    const route = useRoute()
    const store = useStore()
    const ticketDetail = ref({})
    const nodeList: Ref<INodeInfo[]> = ref([])
    const allFields = ref<IField []>([])
    const firstNodeFields = ref<IField []>([])
    const detailLoading = ref<boolean>(true)
    const nodeListLoading = ref<boolean>(true)
    const processTitleFixed = ref<boolean>(false)
    const nodeListTimer = ref(null)
    const ticketPage = ref(null)
    const processDetail = ref(null)

    // 获取单据详情
    const getTicketDetail = async () => {
      try {
        detailLoading.value = true
        const resp = await store.dispatch('ticket/getTicketDetail', {
          id: route.params.id
        })
        ticketDetail.value = resp.data
      } catch (error) {
        console.error(error)
      } finally {
        detailLoading.value = false
      }
    }

    // 获取节点状态列表
    const getNodeList = async () => {
      try {
        const resp = await store.dispatch('ticket/getNodeList', {
          id: route.params.id
        })
        firstNodeFields.value = resp.data[resp.data.length - 1].fields
        resp.data.forEach((node: any) => {
          allFields.value = [...allFields.value, ...node.fields]
        })
        nodeList.value = resp.data.reverse()
        setNodeListPoll()
        await nextTick()
        setStepsTitlePosition()
      } catch (error) {
        console.error(error)
      }
    }

    // 撤单成功后更新节点状态
    const onTicketRevoke = () => {
      initData()
    }

    const initData = async () => {
      nodeListLoading.value = true
      getTicketDetail()
      await getNodeList()
      nodeListLoading.value = false
    }

    // 判断节点列表是否需要轮询
    const isNeedToPoll = () => {
      nodeList.value.some((item) => {
        // 标准运维任务节点为 RUNNING 状态时
        if (['TASK', 'TASK-SOPS'].includes(item.type) && item.status === 'RUNNING') {
          return true
        }
        // 排队状态
        if (item.status === 'QUEUEING') {
          return true
        }
        // 特殊场景，等待当前操作人处理任务
        if (item.is_schedule_ready === false) {
          return true
        }
        // 会签或审批节点提交后，当前处理人task 为 RUNNING|EXECUTED状态，则继续轮询 FINISHED
        const currUserDealTask = item.tasks ? item.tasks.find(task => task.processor.replace(/\((.?)\)/, '') === window.username) : {}
        if (['SIGN', 'APPROVAL'].includes(item.type) && currUserDealTask && ['RUNNING', 'EXECUTED'].includes(currUserDealTask.status)) {
          return true
        }
        return false
      })
    }

    // 设置节点列表查询接口轮询
    const setNodeListPoll = () => {
      if (isNeedToPoll() && !nodeListTimer.value) {
        nodeListTimer.value = setTimeout(() => {
          getNodeList()
        }, 5000)
      } else {
        clearTimeout(nodeListTimer.value)
      }
    }

    const handleStepsFixed = throttle(() => {
      const pos = processDetail.value.getBoundingClientRect()
      processTitleFixed.value = pos.top <= 0
    }, 300)

    const setStepsTitlePosition = () => {
      ticketPage.value.addEventListener('scroll', handleStepsFixed, false)
    }

    const handleClickFixedTitle = () => {
      if (processTitleFixed.value) {
        ticketPage.value.scrollTop = 0
      }
    }

    onBeforeUnmount((): void => {
      if (nodeListTimer.value) {
        clearTimeout(nodeListTimer.value)
      }
      ticketPage.value.removeEventListener('scroll', handleStepsFixed, false)
    })

    initData()

    return {
      getNodeList,
      getTicketDetail,
      nodeList,
      ticketDetail,
      detailLoading,
      nodeListLoading,
      allFields,
      firstNodeFields,
      ticketPage,
      processDetail,
      processTitleFixed,
      onTicketRevoke,
      handleClickFixedTitle
    }
  }

})
</script>
<style lang="postcss" scoped>
  .ticket-page {
    position: relative;
    height: 100%;
    background-color: #f5f6fa;
    overflow: auto;
  }
  .process-detail {
    margin-top: 20px;
    background: #ffffff;
    &.title-fixed {
      padding-top: 112px;
      .process-detail-title {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        background: #ffffff;
        z-index: 10;
      }
    }
  }
  .process-detail-title {
    padding: 32px 0;
    border-bottom: 1px solid #e6e6e6;
    h4 {
      position: relative;
      padding: 0 40px;
      line-height: 48px;
      font-size: 32px;
      font-weight: normal;
      color: #262626;
      &:after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 10px;
        height: 100%;
        background: #3a84ff;
      }
    }
  }
  .node-list-loading {
    padding-top: 60px;
    background: #ffffff;
    text-align: center;
  }
  .go-back-home {
    position: fixed;
    bottom: 250px;
    right: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 72px;
    height: 72px;
    border-radius: 50%;
    background: rgba(105,157,244,0.8);
    i {
      color: #ffffff;
      font-size: 40px;
    }
  }
</style>
