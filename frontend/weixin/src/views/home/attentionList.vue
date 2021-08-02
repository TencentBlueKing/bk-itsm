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
  <div class="home-attention-list">
    <van-skeleton
      :row="5"
      :row-width="['100%', '60%', '60%', '60%', '100%']"
      :loading="firstPageLoading">
      <van-pull-refresh
        v-model="refreshing"
        pulling-text="释放刷新列表..."
        @refresh="onRefresh">
        <list-empty v-if="!loading && list.length === 0" />
        <van-list
          v-else
          v-model:loading="loading"
          finished-text="没有更多了"
          loading-text="加载中..."
          :finished="finished"
          @load="getTicketList">
          <div v-if="type !== 'all'" class="specific-type-num">当前类别共有 {{ total }} 条单据 </div>
          <div v-for="ticket in list" :key="ticket.sn" class="ticket-item" @click="goTicketDetail(ticket.id)">
            <h4>{{ ticket.title }}</h4>
            <p class="sn-info">
              <span class="ticket-status" :style="getStatusColor(ticket)">{{ ticket.current_status_display }}</span>
              {{ ticket.sn }} | 提单人：{{ ticket.creator }}
            </p>
            <p>服务: {{ ticket.service_name }}</p>
            <p>当前步骤: {{ ticket.current_steps.map(item => item.name).join(';') || '--' }}</p>
            <p class="processors">当前处理人: {{ ticket.current_processors || '--' }}</p>
          </div>
        </van-list>
      </van-pull-refresh>
    </van-skeleton>
  </div>
</template>
<script lang="ts">
import { defineComponent, ref, Ref, toRefs, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import ListEmpty from './listEmpty.vue'

interface Ticket {
  title: string,
  sn: string
}

export default defineComponent({
  name: 'AttentionList',
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
    const router = useRouter()
    const list: Ref<Ticket[]> = ref([])
    const total: Ref<number> = ref(0)
    const refreshing: Ref<boolean> = ref(false)
    const loading: Ref<boolean> = ref(true)
    const firstPageLoading: Ref<boolean> = ref(false)
    const finished: Ref<boolean> = ref(false)
    const page: Ref<number> = ref(0)
    const { type } = toRefs(props)

    watch(type, () => {
      onRefresh()
    })

    const getTicketList = async () => {
      firstPageLoading.value = page.value === 0
      page.value += 1
      loading.value = true
      const params = {
        page: page.value,
        page_size: 10,
        ordering: '-create_at',
        is_draft: 0,
        service_type: props.type === 'all' ? undefined : props.type,
        view_type: 'my_attention'
      }
      try {
        const resp = await store.dispatch('ticket/getTickets', { params })
        list.value = [...list.value, ...resp.data.items]
        total.value = resp.data.count
        finished.value = resp.data.total_page === page.value
      } catch (e) {
        console.error(e)
      } finally {
        loading.value = false
        refreshing.value = false
        firstPageLoading.value = false
      }
    }

    const onRefresh = (): void => {
      page.value = 0
      list.value = []
      getTicketList('refresh')
    }

    const getStatusColor = (ticket) => {
      let color = '#63656e'
      const serviceConfig = store.state.serviceConfig[ticket.service_type]
      if (serviceConfig) {
        color = serviceConfig.find(item => item.key === ticket.current_status).color_hex
      }
      return {
        color,
        borderColor: color
      }
    }

    // 前往单据详情
    const goTicketDetail = (id: number): void => {
      router.push(`/ticket/${id}`)
    }

    return {
      list,
      total,
      refreshing,
      loading,
      firstPageLoading,
      finished,
      onRefresh,
      getTicketList,
      getStatusColor,
      goTicketDetail
    }
  }
})
</script>
<style lang="postcss" scoped>
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
  .ticket-item {
    padding: 24px 32px;
    box-shadow: 0px -1px 0px 0px #e6e6e6 inset;
    h4 {
      margin: 0 0 10px;
      font-size: 32px;
      font-weight: normal;
      color: #222222;
      line-height: 52px;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
    }
    p {
      font-size: 24px;
      color: #8c8c8c;
      line-height: 44px;
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
    }
    .sn-info {
      .ticket-status {
        display: inline-block;
        margin-right: 8px;
        min-width: 64px;
        height: 30px;
        line-height: 30px;
        font-size: 18px;
        text-align: center;
        border: 1px solid #8c8c8c;
        border-radius: 4px;
      }
    }
    .processors {
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
    }
  }
</style>
