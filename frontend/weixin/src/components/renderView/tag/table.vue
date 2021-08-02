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
  <h4 class="header-title">{{ form.label }}</h4>
  <div class="tag-table-wrap">
    <!-- 固定列 -->
    <table
      v-if="fixedFirstColumn"
      class="tag-table table-fixed"
      cellspacing="0"
      ellpadding="0"
      border="0">
      <colgroup>
        <col class="frist-clo" :width="columns[0].width">
        <col>
      </colgroup>
      <thead>
        <tr>
          <th>
            <div class="table-cell">{{ columns[0].name }}</div>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in data" :key="index">
          <td><div class="table-cell"><TableText :form="item[columns[0].key]" /></div></td>
        </tr>
      </tbody>
    </table>
    <!-- 表格 -->
    <div class="base-table-body">
      <table class="tag-table" cellspacing="0" cellpadding="0" border="0">
        <colgroup>
          <col v-for="(column, index) in columns" :key="index" :width="column.width">
        </colgroup>
        <thead>
          <tr>
            <th v-for="(column, index) in columns" :key="index"><div class="table-cell">{{ column.name }}</div></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in data" :key="index">
            <td v-for="(column, i) in columns" :key="i">
              <div class="table-cell">
                <TableText :form="item[column.key]" />
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
<script lang="ts">
import { defineComponent, inject, toRefs } from 'vue'
import { IContext, IColumn } from '../types'
import TableText from './tableText.vue'

export default defineComponent({
  name: 'ViewTable',
  components: {
    TableText
  },
  props: {
    form: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props) {
    const { form }  = toRefs(props)
    const context: any = inject<IContext>('context')
    const columns = context.schemes[form.value.scheme].attrs.column.map((m: IColumn) => ({
      ...m,
      width: '140px'
    }))
    const data = form.value.value
    // TODO 固定列待优化，先关闭
    const fixedFirstColumn = false
    return {
      columns,
      data,
      fixedFirstColumn
    }
  }
})
</script>
<style lang="postcss" scoped>
.tag-table-cell {
  color: #63656e;
  font-size: 24px;
  line-height: 64px;
  background: #fafafa;
  /deep/ .van-cell__title {
    font-size: 24px !important;
  }
}
.tag-table-wrap {
  width: 100%;
  overflow-x: auto;
  position: relative;
}
.base-table-body {
  position: relative;
  overflow-x: auto;
}
.tag-table {
  width: 100%;
  margin: 10px 0;
  table-layout: fixed;
  border-collapse: separate;
  border: 1px solid #e6e6e6;
  thead {
    background: #f5f6fa;
  }
  tr {
    .table-cell {
      padding: 26px 32px;
      box-sizing: border-box;
      line-height: 40px;
    }
    td,th {
      border-right: 1px solid #e6e6e6;
      border-bottom: 1px solid #e6e6e6;
    }
    td:last-child, th:last-child {
      border-right: none;
    }
    &:last-child {
      td {
        border-bottom: none;
      }
    }
  }
}
.table-fixed {
  width: auto;
  margin: 0;
  position: absolute;
  left: 0;
  top: 10px;
  z-index: 1;
  box-shadow: 0 0 10px rgba(0,0,0,.12);
  background: #fff;
}
</style>
