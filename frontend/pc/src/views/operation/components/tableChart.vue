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
  <div class="table-chart">
    <bk-table
      :data="chartData"
      :pagination="pagination"
      :outer-border="false"
      @sort-change="handleSortChange"
      @page-change="handlePageChange">
      <bk-table-column
        v-for="col in columns"
        :key="col.key"
        :label="col.name"
        :render-header="$renderHeader"
        :show-overflow-tooltip="col.key !== 'organization'"
        :sortable="col.sort ? 'custom' : false"
        :align="col.align || 'left'"
        :prop="col.key"
        :width="('width' in col) ? col.width : 'auto'">
        <div
          slot-scope="props"
          :class="{ 'padding-right-adjust': col.align === 'right' && col.sort }">
          <div v-if="col.key === 'order'" class="order" :class="getOrderCls(props.$index)">
            <span class="order-num">{{ getRowOrder(props.$index) }}</span>
          </div>
          <template v-else-if="typeof col.format === 'function'">
            <span style="font-weigth: 700;">{{ col.format.call(this, props.row) }}</span>
          </template>
          <template v-else-if="col.key === 'organization' && props.row.organization_full">
            <span
              v-bk-tooltips="{
                content: props.row.organization_full,
                position: 'top',
                theme: 'light'
              }">
              {{ props.row.organization }}
            </span>
          </template>
          <template v-else>
            <span v-if="col.link" class="link" @click="handlerCellClick(col, props.row)">{{ props.row[col.key] }}</span>
            <span v-else>{{ props.row[col.key] }}</span>
          </template>
        </div>
      </bk-table-column>
      <div class="empty" slot="empty">
        <empty
          :is-error="listError"
          :is-search="searchToggle"
          @onRefresh="refresh(0)"
          @onClearSearch="refresh(1)">
        </empty>
      </div>
    </bk-table>
  </div>
</template>
<script>
  import Empty from '../../../components/common/Empty.vue';
  export default {
    name: 'TableChart',
    components: {
      Empty,
    },
    props: {
      title: {
        type: String,
        default: '',
      },
      desc: {
        type: String,
        default: '',
      },
      showSearchInput: {
        type: Boolean,
        default: false,
      },
      listError: {
        type: Boolean,
        default: false,
      },
      showPagination: {
        type: Boolean,
        default: false,
      },
      searchToggle: {
        type: Boolean,
        default: false,
      },
      pagination: {
        type: Object,
        default() {
          return {
            current: 1,
            count: 0,
            limit: 10,
          };
        },
      },
      showTop3Color: {
        type: Boolean,
        default: true,
      },
      columns: {
        type: Array,
        default: () => ([]),
      },
      chartData: {
        type: Array,
        default: () => ([]),
      },
      loading: {
        type: Boolean,
        default: false,
      },
    },
    methods: {
      refresh(type) {
        this.$parent.searchStr = '';
        if (type) {
          this.$parent.$emit('clear');
        } else {
          this.$parent.$emit('search');
        }
      },
      getRowOrder(index) {
        return index + (this.pagination.current - 1) * this.pagination.limit + 1;
      },
      getOrderCls(index) {
        let cls = '';
        if (this.pagination.current === 1 && index <= 2) {
          if (index === 0) {
            cls = 'first-order';
          } else if (index === 1) {
            cls = 'second-order';
          } else {
            cls = 'third-order';
          }
        }
        return cls;
      },
      handleSortChange(data) {
        const { prop, order } = data;
        let sortCondition;
        if (order === 'ascending') {
          sortCondition = prop;
        } else if (order === 'descending') {
          sortCondition = `-${prop}`;
        }
        this.$emit('onOrderChange', sortCondition);
      },
      handlePageChange(page) {
        this.$emit('onPageChange', page);
      },
      handlerCellClick(col, data) {
        if (typeof col.handler === 'function') {
          col.handler.call(this, data);
        }
      },
    },
  };
</script>
<style lang="scss" scoped>
    .order {
        padding: 2px;
        width: 20px;
        height: 20px;
        font-weight: 700;
        text-align: center;
        color: #63656e;
        &.first-order,
        &.second-order,
        &.third-order {
            border-radius: 50%;
            text-align: center;
            vertical-align: middle;
            .order-num {
                display: inline-block;
                width: 16px;
                height: 16px;
                color: #ffffff;
                border-radius: 50%;
                text-align: center;
            }
        }
        &.first-order {
            background: #ffd694;
            .order-num {
                background: #ffae10;
            }
        }
        &.second-order {
            background: #fedddc;
            .order-num {
                background: #fd5353;
            }
        }
        &.third-order {
            background: #f0f1f5;
            .order-num {
                background: #979ba5;
            }
        }
    }
    .link {
        color: #3a84ff;
        cursor: pointer;
    }
    .padding-right-adjust {
        padding-right: 20px;
    }
</style>
