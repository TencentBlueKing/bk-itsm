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
  <footer id="page-footer-wrapper">
    <template v-if="bkSharedResUrl">
      <p class="link-list" v-html="platformInfo.i18n.footerInfoHTML"></p>
      <p class="copyright" v-html="platformInfo.footerCopyrightContent"></p>
    </template>
    <p v-else v-html="footer" class="common-footer"></p>
  </footer>
</template>
<script>
  import { mapState } from 'vuex';

  export default {
    name: 'CopyrightFooter',
    data() {
      return {
        bkSharedResUrl: window.BK_SHARED_RES_URL,
      };
    },
    computed: {
      ...mapState({
        footer: state => state.common.footer,
        platformInfo: state => state.platformInfo,
      }),
    },
  };
</script>
<style lang="scss">
#page-footer-wrapper {
    margin-top: 50px;
    padding-bottom: 30px;
    .copyright {
        font-size: 12px;
        color: #999999;
        text-align: center;
    }
    .link-list {
      margin-bottom: 6px;
      font-size: 12px;
      text-align: center;
    }
    .link-item {
        display: inline-block;
        padding: 0 4px;
        line-height: 1;
        color: #3480fe;
    }
    .common-footer {
      .link-item {
        color: #3480fe;
        margin-left: -4px;
        &:not(:last-child) {
          border-right: 1px solid #3480fe;
        }
      }
    }
    .desc {
        margin-bottom: 8px;
        line-height: 1;
    }
}
</style>
