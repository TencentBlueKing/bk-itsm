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
            </div>
          </div>
        </van-list>
      </van-pull-refresh>
    </van-skeleton>
  </div>
</template>
<script lang="ts">
import { defineComponent, reactive, ref, toRefs, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import ListEmpty from './listEmpty.vue'
import { ITicketItem } from './../../typings/ticket'

interface IState {
  todoList: Array<ITicketItem>;
  pagination: {
    page: number,
    totalPage: number,
    count: number
  }
}
export default defineComponent({
  name: 'TodoList',
  components: {
    ListEmpty
  },
  props: {
    type: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    const store = useStore()
    const router  = useRouter()
    const loading = ref(true)
    const refreshing = ref(false)
    const finished = ref(false)
    const firstPageLoading = ref(false)
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
        view_type: 'my_todo',
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
    const handleSubmitted = () => {
      onRefresh()
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
      onRefresh,
      handleSubmitted,
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
      text-overflow: ellipsis;
      overflow: hidden;
      word-break: keep-all;
      white-space: nowrap;
    }
  }
}
</style>
