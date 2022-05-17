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
  <div class="bk-approval-node-content">
    <h3 class="bk-basic-h3">{{ $t('m.newCommon["节点信息"]') }}</h3>
    <template v-for="(ite, inde) in nodeInfo.fields">
      <fields-done
        :key="inde"
        :item="ite"
        :origin="'notLog'">
      </fields-done>
    </template>
  </div>
</template>

<script>
  import fieldsDone from '../components/fieldsDone.vue';

  export default {
    name: 'approvalNodeInfo',
    components: {
      fieldsDone,
    },
    props: {
      nodeInfo: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
      };
    },
  };
</script>

<style scoped lang='scss'>
    @import '../../../../scss/mixins/clearfix.scss';
    @import '../../../../scss/mixins/scroller.scss';
    .bk-approval-node-content {
        font-size: 12px;
    }
    .bk-basic-h3 {
        margin: 0;
        padding: 0;
        font-size: 14px;
        font-weight: bold;
        color: #63656E;
        line-height: 19px;
        margin-bottom: 10px;
    }
</style>
