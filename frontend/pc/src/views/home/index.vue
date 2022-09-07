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
  <div class="home-page-wrapper">
    <div class="home-page-view">
      <div class="home-background">
        <p class="welcome-tips">Hi，{{ userName }}，{{ $t(`m.home['欢迎使用流程服务！']`) }}</p>
      </div>
      <div class="main-content">
        <service-list></service-list>
        <!-- <ticket-table></ticket-table> -->
      </div>
      <copyright-footer></copyright-footer>
    </div>
  </div>
</template>
<script>
  import ServiceList from './serviceList.vue';
  // import TicketTable from './ticketTable.vue';
  import CopyrightFooter from '@/components/common/layout/CopyrightFooter.vue';

  export default {
    name: 'Home',
    components: {
      ServiceList,
      // TicketTable,
      CopyrightFooter,
    },
    data() {
      return {
        userName: window.username || '--',
      };
    },
  };
</script>
<style lang="scss" scoped>
    .home-page-view {
        min-height: calc(100vh - 52px);
    }
    .home-background {
        height: 160px;
        background: url('../../images/homeBackground.png') #131820 center no-repeat;
        overflow: hidden;
        .welcome-tips {
            margin: 40px auto 0;
            width: 1300px;
            font-size: 12px;
            color: #fafbfd;
        }
    }
    .main-content {
        width: 1300px;
        margin: -88px auto 0;
        min-height: calc(100vh - 247px);
    }
</style>
