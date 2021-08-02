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
  <div class="home-tabbar van-hairline--top">
    <router-link class="tab-nav" to="/home/todo">
      <div class="tab-icon"><i class="itsm-mobile-icon icon-daiban" /></div>
      <div class="tab-name">我的待办</div>
      <span v-if="totalCount.todo > 0" class="number">{{ totalCount.todo }}</span>
    </router-link>
    <router-link class="tab-nav" to="/home/approval">
      <div class="tab-icon"><i class="itsm-mobile-icon icon-quanxian" /></div>
      <div class="tab-name">待我审批</div>
      <span v-if="totalCount.approval > 0" class="number">{{ totalCount.approval }}</span>
    </router-link>
    <router-link class="tab-nav" to="/home/application">
      <div class="tab-icon"><i class="itsm-mobile-icon icon-tidan" /></div>
      <div class="tab-name">我的申请</div>
    </router-link>
    <router-link class="tab-nav" to="/home/attention">
      <div class="tab-icon"><i class="itsm-mobile-icon icon-favorite-o" /></div>
      <div class="tab-name">我的关注</div>
    </router-link>
  </div>
</template>
<script lang="ts">
import { computed } from 'vue'
import { useStore } from 'vuex'
export default {
  name: 'HomeTabbar',
  setup() {
    const store = useStore()
    return {
      totalCount: computed(() => store.state.ticket.counts)
    }
  }
}
</script>
<style lang="postcss" scoped>
  .home-tabbar {
    display: flex;
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    background: #f9f9f9;
    overflow: hidden;
    &:after {
      border-color: #c4c6cc;
    }
  }
  .tab-nav {
    position: relative;
    flex: 1;
    height: 104px;
    text-align: center;
    &.router-link-exact-active {
      background: #ffffff;
      .tab-icon i {
        color: #3a84ff;
      }
      .tab-name {
        color: #3a84ff;
        font-weight: 700;
      }
    }
    .tab-icon {
      margin-top: 20px;
      i {
        font-size: 40px;
        color: #63656e;
      }
    }
    .tab-name {
      font-size: 22px;
      color: #222222;
    }
    .number {
      position: absolute;
      top: 18px;
      left: calc(50% + 16px);
      padding: 0 8px;
      min-width: 32px;
      height: 28px;
      line-height: 28px;
      font-size: 22px;
      color: #ffffff;
      text-align: center;
      vertical-align: middle;
      border-radius: 16px;
      background: #ff4444;
    }
  }
</style>
