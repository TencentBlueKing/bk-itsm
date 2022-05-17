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
  <!-- 当前步骤 -->
  <div v-if="row.current_steps.length > 0"
    class="current-steps-wrap">
    <bk-popover
      placement="top"
      :theme="'light'"
      :interactive="false">
      <span
        class="bk-current-step">
        {{row.current_steps[0].name}}
      </span>
      <div slot="content" style="max-width: 200px;">
        <span class="bk-current-step auto-width"
          v-for="(othernode, otherNodeIndex) in row.current_steps"
          :key="otherNodeIndex">
          {{othernode.name}}
        </span>
      </div>
    </bk-popover>
  </div>
  <span v-else>--</span>
</template>

<script>

  export default {
    name: 'ColumnCurrentStep',
    props: {
      row: {
        type: Object,
        default: () => ({}),
      },
    },
  };
</script>
<style lang='scss' scoped>
.current-steps-wrap /deep/ {
    .bk-tooltip, .bk-tooltip-ref {
        width: 100%;
    }
}
.bk-current-step {
    width: 100%;
    padding: 0 4px;
    display: inline-block;
    border: 1px solid #DCDEE5;
    height: 22px;
    line-height: 20px;
    border-radius: 2px;
    background-color: #FAFBFD;
    text-align: center;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    &.auto-width {
        margin-right: 5px;
        color: #424950;
        white-space:nowrap;
        width: auto;
    }
}
</style>
