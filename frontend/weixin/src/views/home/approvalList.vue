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
  <div id="home-todo-list" class="home-todo-list">
    <van-skeleton
      :row="5"
      :row-width="['100%', '60%', '60%', '60%', '100%']"
      :loading="firstPageLoading">
      <van-pull-refresh
        v-model="refreshing"
        pulling-text="释放刷新列表..."
        @refresh="onRefresh">
        <list-empty v-if="!loading && todoList.length === 0" />
        <van-list
          v-else
          v-model:loading="loading"
          :finished="finished"
          finished-text="没有更多了"
          loading-text="加载中..."
          @load="getTodoList('next')">
          <div v-if="type !== 'all'" class="specific-type-num">当前类别共有 {{ pagination.count }} 条单据 </div>
          <div v-for="item in todoList" :key="item.sn" @click="goTicketDetail(item.id)">
            <div class="ticket-card van-hairline--bottom">
              <h3 class="ticket-title">{{ item.title }}</h3>
              <p class="ticket-info">{{ item.sn }} | 提单人：{{ item.creator }}</p>
              <p class="serve-info">服务：{{ item.service_name || '--' }}</p>
              <p class="opt-btn-group">
                <van-button
                  class="appro-btn"
                  icon="cross"
                  type="default"
                  :disabled="crtTicket && crtTicket.id === item.id && confirmPending"
                  @click.stop="onApproval(false, item)">
                  拒绝
                </van-button>
                <van-button
                  class="appro-btn"
                  icon="success"
                  type="default"
                  :disabled="crtTicket && crtTicket.id === item.id && refusePending"
                  @click.stop="onApproval(true, item)">
                  通过
                </van-button>
              </p>
            </div>
          </div>
        </van-list>
      </van-pull-refresh>
    </van-skeleton>
    <van-action-sheet
      v-model:show="isShowApprovalPanel"
      :closeable="false"
      class="approval-panel"
      @click.stop>
      <div class="panel-opt-btn">
        <span @click="isShowApprovalPanel = false">取消</span>
        <span class="ui-color-blue" @click="confirmApproval">确认</span>
      </div>
      <div class="approval-text">
        <van-field
          v-model="approvalText"
          rows="6"
          type="textarea"
          maxlength="200"
          placeholder="请填写拒绝理由"
          show-word-limit />
      </div>
      <ul class="fill-text-list">
        <li
          v-for="text in approvalFillTextList"
          :key="text"
          class="text-item"
          @click="insertText(text)">
          {{ text }}
        </li>
      </ul>
    </van-action-sheet>
  </div>
</template>
<script lang="ts">
import { defineComponent, reactive, ref, toRefs, watch } from 'vue'
import { useStore } from 'vuex'
import { ITicketItem } from './../../typings/ticket'
import { useRouter } from 'vue-router'
import { Toast, Notify } from 'vant'
import ListEmpty from './listEmpty.vue'

interface IApprovalId {
  // eslint-disable-next-line camelcase
  ticket_id: string | number
}

interface IApprovalData {
  result: string | undefined,
  opinion?: string,
  // eslint-disable-next-line camelcase
  approval_list: Array<IApprovalId>
}

interface IState {
  todoList: Array<ITicketItem>;
  pagination: {
    page: number,
    totalPage: number,
    count: number
  }
}
export default defineComponent({
  name: 'ApprovalList',
  components: {
    ListEmpty
  },
  props: {
    type: {
      type: String,
      default: ''
    }
  },
  emits: ['update-count'],
  setup(props, context) {
    const store = useStore()
    const router  = useRouter()
    const loading = ref(true)
    const refreshing = ref(false)
    const finished = ref(false)
    const firstPageLoading = ref(false)
    const confirmPending = ref(false)
    const refusePending = ref(false)
    const isShowApprovalPanel = ref(false)
    const approvalText = ref('')
    const approvalFillTextList = ['理由不充分', '时间问题', '更换处理人']
    const crtTicket = ref(null) // 当前处理单据
    const { type } = toRefs(props)

    // ticket list
    const state = reactive<IState>({
      todoList: [],
      pagination: {
        page: 0,
        totalPage: 1,
        count: 0
      }
    })

    watch(type, () => {
      onRefresh()
    })

    // 获取列表数据
    const getTodoList = (type = 'init'): void => {
      firstPageLoading.value = state.pagination.page === 0
      loading.value = true
      const page = type === 'next' ? state.pagination.page += 1 : 1
      const params = {
        view_type: 'my_approval',
        ordering: '-create_at',
        service_type: props.type === 'all' ? undefined : props.type,
        page_size: 10,
        page,
        waiting_approve: false,
        is_draft: 0
      }
      store.dispatch('ticket/getTickets', { params }).then((res: any) => {
        const { data } = res
        if (type === 'init') {
          state.todoList = data.items
        } else {
          state.todoList = [...state.todoList, ...data.items]
        }

        state.pagination.page = data.page
        state.pagination.totalPage = data.total_page
        state.pagination.count = data.count

        finished.value = state.pagination.page === data.total_page
        refreshing.value = false
        loading.value = false
        firstPageLoading.value = false
      })
    }
    // 下拉刷新
    const onRefresh = (): void => {
      state.todoList = []
      state.pagination = {
        page: 0,
        totalPage: 1,
        count: 0
      }
      getTodoList()
    }
    // 通过/拒绝按钮点击回调
    const onApproval = (result: boolean, ticket: ITicketItem): void => {
      crtTicket.value = ticket
      // 通过
      if (result) {
        confirmPending.value = true
        submitForm({
          result: 'true',
          approval_list: [{ ticket_id: ticket.id }]
        })
      } else {
        // 拒绝
        isShowApprovalPanel.value = true
        approvalText.value = ''
      }
    }

    // 提交
    const submitForm  = async (data: IApprovalData) => {
      try {
        const resp = await store.dispatch('ticket/batchApproval', data)
        if (resp.result) {
          Toast({
            message: data.result === 'true' ? '已通过' : '已拒绝',
            icon: 'passed'
          })
          isShowApprovalPanel.value = false
          crtTicket.value = null
          onRefresh()
          context.emit('update-count')
        }
      } catch (error) {
        Toast.fail(error.message)
      } finally {
        confirmPending.value = false
        refusePending.value = false
      }
    }

    // 确认拒绝
    const confirmApproval = (): boolean => {
      if (!approvalText.value) {
        Notify('拒绝理由不能为空')
        crtTicket.value = null
        return false
      }
      refusePending.value = true
      submitForm({
        result: 'false',
        opinion: approvalText.value,
        approval_list: [{ ticket_id: crtTicket.value.id }]
      })
    }

    const insertText = (text: string) => {
      approvalText.value += text
    }

    const goTicketDetail = (id: number): void => {
      router.push({
        name: 'ticket',
        params: {
          id
        }
      })
    }

    return {
      ...toRefs(state),
      loading,
      finished,
      getTodoList,
      refreshing,
      firstPageLoading,
      isShowApprovalPanel,
      insertText,
      approvalFillTextList,
      approvalText,
      crtTicket,
      confirmPending,
      refusePending,
      onApproval,
      confirmApproval,
      onRefresh,
      goTicketDetail
    }
  }
})
</script>
<style lang="postcss" scoped>
.home-todo-list {
  position: relative;
  .van-pull-refresh {
    height: calc(100vh - 202px);
    overflow: auto;
  }
  .specific-type-num {
    padding: 0 32px;
    height: 64px;
    line-height: 64px;
    font-size: 26px;
    color: #63656e;
    background: #f5f6fa;
  }
  .ui-color-blue {
    color: #3A84FF !important;
  }
  .ticket-card {
    padding: 24px 32px 24px;
    &:after {
      border-color: #e6e6e6;
    }
    .ticket-title {
      font-size: 32px;
      text-align: left;
      color: #222222;
      font-weight: normal;
      line-height: 52px;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
    }
    .ticket-info {
      margin-top: 8px;
      font-size: 24px;
      color: #8c8c8c;
      line-height: 44px;
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
      word-break: keep-all;
    }
    .serve-info {
      font-size: 24px;
      color: #8c8c8c;
      line-height: 44px;
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
    }
    .opt-btn-group {
      margin-top: 8px;
      display: flex;
      flex-direction: row-reverse;
      .appro-btn {
        margin-left: 16px;
        padding: 0 8px;
        height: 48px;
        font-size: 26px;
        color: #63656e;
        border-radius: 6px;
        border-color: #c4c6cc;
        /deep/ .van-icon-cross {
          color: #FF5656;
        }
        /deep/ .van-icon-success {
          color: #45E35F;
        }
      }
    }
  }
  .approval-panel {
    .panel-opt-btn {
      display: flex;
      justify-items: center;
      justify-content: space-between;
      padding: 0 40px;
      height: 96px;
      line-height: 96px;
      box-shadow: 0px 1px 0px 0px #e6e6e6;
      span {
        color: #63656E;
        font-size: 32px;
        font-weight: 400;
      }
    }
    .approval-text {
      padding: 25px 40px;
    }
    .fill-text-list {
      display: flex;
      flex-wrap: wrap;
      padding: 16px 50px;
      box-shadow: 0px 1px 0px 0px #e6e6e6 inset;
      .text-item {
        padding: 0 10px;
        display: block;
        height: 40px;
        line-height: 40px;
        font-size: 24px;
        text-align: center;
        color: #63656e;
        background: #f0f1f5;
        &:not(:first-child) {
          margin-left: 16px;
        }
      }
    }
  }
}
</style>
