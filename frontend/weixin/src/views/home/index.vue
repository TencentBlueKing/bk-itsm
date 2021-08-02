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
  <div class="home-page">
    <home-header
      :keyword="searchStr"
      @change="changeType"
      @toggle-search="onToggleSearchMode"
      @search="onSearch" />
    <router-view :type="type" @update-count="getTicketsCount" />
    <home-tabbar />
    <search-list
      v-show="searchMode"
      class="home-search-list"
      :keyword="searchStr"
      @search="onSearch" />
  </div>
</template>
<script lang="ts">
import { defineComponent } from 'vue'
import HomeHeader from './components/header.vue'
import HomeTabbar from './components/tabbar.vue'
import SearchList from './searchList.vue'

export default defineComponent({
  name: 'Home',
  components: {
    HomeHeader,
    HomeTabbar,
    SearchList
  },
  data() {
    return {
      type: 'all',
      searchMode: false,
      searchStr: ''
    }
  },
  created() {
    this.getTicketsCount()
  },
  methods: {
    getTicketsCount() {
      this.$store.dispatch('ticket/getTicketsCount')
    },
    changeType(type: string): void {
      this.type = type
    },
    onToggleSearchMode(val: boolean): void {
      this.searchMode = val
    },
    onSearch(val: string): void {
      this.searchStr = val
      this.searchMode = true
    }
  }
})
</script>
<style lang="postcss" scoped>
  .home-page {
    position: relative;
    height: 100%;
    overflow: hidden;
    .home-search-list {
      position: absolute;
      top: 112px;
      right: 0;
      left: 0;
      bottom: 0;
      background: #ffffff;
    }
  }
</style>
