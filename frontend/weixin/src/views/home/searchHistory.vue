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
  <div class="search-history-wrap">
    <div v-if="historyList.length === 0" class="empty-word">
      <p>搜索单号或标题关键字</p>
      <p>搜一搜单据</p>
    </div>
    <div v-else class="history-list">
      <div class="list-title">
        <p>搜索历史</p>
        <van-icon class="delete-icon" name="delete" @click="onClearHistory" />
      </div>
      <div
        v-for="(item, index) in historyList"
        :key="`${item}_${index}`"
        class="history-item"
        @click="$emit('select', item)">
        {{ item }}
      </div>
    </div>
  </div>
</template>
<script lang="ts">
import { defineComponent, ref, toRefs, watch } from 'vue'

export default defineComponent({
  name: 'SearchHistory',
  props: {
    keyword: {
      type: String,
      default: ''
    }
  },
  emits: ['select'],
  setup(props) {
    const historyList = ref([])
    const { keyword } = toRefs(props)

    const getHistory = () => {
      const storageData = JSON.parse(localStorage.getItem('ticketSearchList'))
      historyList.value = storageData || []
    }

    const setHistory = () => {
      const index = historyList.value.findIndex(item => item === keyword.value)
      if (index > -1) {
        historyList.value.splice(index, 1)
      }
      historyList.value.unshift(keyword.value)
      localStorage.setItem('ticketSearchList', JSON.stringify(historyList.value))
    }

    const onClearHistory = () => {
      localStorage.setItem('ticketSearchList', '[]')
      getHistory()
    }

    watch(keyword, () => {
      if (keyword.value !== '') {
        setHistory()
      }
    })

    getHistory()

    return { historyList, onClearHistory }
  }
})
</script>
<style lang="postcss" scoped>
  .empty-word {
    margin-top: 48px;
    font-size: 24px;
    text-align: center;
    line-height: 46px;
    color: #979ba5;
  }
  .history-list {
    padding: 0 35px 0 40px;
    overflow: hidden;
    .list-title {
      display: flex;
      justify-content: space-between;
      margin: 20px 0;
      font-size: 28px;
      color: #979ba5;
      .delete-icon {
        margin-top: 8px;
        color: #979ba5;
        font-size: 28px;
      }
    }
    .history-item {
      float: left;
      margin-right: 16px;
      margin-bottom: 16px;
      padding: 0 20px;
      height: 40px;
      line-height: 40px;
      font-size: 24px;
      color: #63656e;
      background: #f0f1f5;
    }
  }
</style>
