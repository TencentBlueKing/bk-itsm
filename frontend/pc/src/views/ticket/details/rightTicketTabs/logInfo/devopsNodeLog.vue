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
  <div class="bk-page bk-auto-node-basic">
    <p class="bk-header-bold">{{ $t('m.newCommon["任务参数"]') }}</p>
    <div>
      <div class="bk-param">
        <bk-table
          :data="nodeInfo"
          :ext-cls="'bk-editor-table'">
          <bk-table-column :label="$t(`m.treeinfo['字段名']`)" prop="name"></bk-table-column>
          <bk-table-column :label="$t(`m.treeinfo['参数值']`)" width="400">
            <template slot-scope="props">
              <span>{{props.row.value || '--'}}</span>
            </template>
          </bk-table-column>
        </bk-table>
      </div>
    </div>
  </div>
</template>

<script>

  export default {
    name: 'devopsNodeLog',
    props: {
      nodeInfo: {
        type: Array,
        default: () => ({}),
      },
    },
  };
</script>

<style lang="scss" scoped>
    .bk-page {
        display: block;
        height: auto;
        margin-bottom: 10px;
        .bk-header-bold {
            font-weight: bold;
            padding: 10px 0;
        }
    }
</style>
