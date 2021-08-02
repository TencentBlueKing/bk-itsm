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
  <div class="home-search">
    <div v-show="keyword === ''" class="empty-word">
      <search-history :keyword="keyword" @select="updateKeyword" />
    </div>
    <div v-if="keyword !== ''" class="list-wrap">
      <van-loading v-if="firstSearchLoading" class="first-search-loading" size="40" color="#3a84ff" />
      <template v-else>
        <list-empty v-if="!loading && list.length === 0" />
        <van-list
          v-else
          v-model:loading="loading"
          :finished="finished"
          :immediate-check="false"
          finished-text="没有更多了"
          loading-text="加载中..."
          @load="getSearchList">
          <div
            v-for="ticket in list"
            :key="ticket.sn"
            class="ticket-item"
            @click="router.push(`/ticket/${ticket.id}`)">
            <van-icon name="search" class="search-icon" />
            <div class="ticket-info">
              <h4 class="title">{{ ticket.title }}</h4>
              <p class="sn">{{ ticket.sn }}</p>
            </div>
          </div>
        </van-list>
      </template>
    </div>
  </div>
</template>
<script lang="ts">
import { useStore } from 'vuex'
import { ref, Ref, toRefs, watch } from 'vue'
import { useRouter } from 'vue-router'
import ListEmpty from './listEmpty.vue'
import SearchHistory from './searchHistory.vue'

interface Ticket {
  sn: string,
  title: string
}

export default {
  name: 'HomeSearch',
  components: {
    ListEmpty,
    SearchHistory
  },
  props: {
    keyword: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: 'all'
    }
  },
  setup(props, context) {
    const { emit } = context
    const store = useStore()
    const router = useRouter()
    const { keyword } = toRefs(props)
    const firstSearchLoading: Ref<boolean> = ref(false) // 输入关键字后点击搜索
    const loading: Ref<boolean> = ref(false)
    const finished: Ref<boolean> = ref(false)
    const page: Ref<number> = ref(0)
    const list: Ref<Ticket[]> = ref([])

    const getSearchList = async () => {
      if (keyword.value === '') {
        return
      }
      loading.value = true
      page.value += 1
      const params = {
        page: page.value,
        page_size: 10,
        ordering: '-create_at',
        is_draft: 0,
        keyword: props.keyword
      }
      try {
        const resp = await store.dispatch('ticket/getTickets', { params })
        list.value = [...list.value, ...resp.data.items]
        finished.value = resp.data.total_page === page.value
      } catch (e) {
        console.log(e)
      } finally {
        loading.value = false
        firstSearchLoading.value = false
      }
    }
    const onTicketClick = (ticket: Ticket): void => {
      console.log(ticket)
    }

    const updateKeyword = (val: string): void => {
      emit('search', val)
    }

    watch(keyword, () => {
      page.value = 0
      list.value = []
      firstSearchLoading.value = true
      getSearchList()
    })

    return {
      firstSearchLoading,
      loading,
      finished,
      list,
      onTicketClick,
      getSearchList,
      router,
      updateKeyword
    }
  }
}
</script>
<style lang="postcss" scoped>
  .search-str {
    font-size: 28px;
    color: #979ba5;
    padding: 20px 40px;
  }
  .list-wrap {
    height: 100%;
    overflow: auto;
  }
  .ticket-item {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    padding: 20px 40px;
    box-shadow: 0px -1px 0px 0px #e6e6e6 inset;
  }
  .search-icon {
    margin-right: 16px;
    font-size: 34px;
    color: #979ba5;
    line-height: 52px;
  }
  .first-search-loading {
    padding-top: 100px;
    background: #ffffff;
    text-align: center;
  }
  .ticket-info {
    h4 {
      margin: 0;
      font-size: 32px;
      font-weight: normal;
      color: #333333;
      line-height: 52px;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
    }
    p {
      margin: 10px 0 0;
      font-size: 28px;
      color: #8c8c8c;
    }
  }
</style>
