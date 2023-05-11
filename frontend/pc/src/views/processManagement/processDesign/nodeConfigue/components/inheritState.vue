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
  <div class="bk-dialog-form">
    <bk-table ref="table"
      v-bkloading="{ isLoading: isDataLoading }"
      :data="dataList"
      :size="'small'"
      @select-all="handleSelectAll"
      @select="handleSelect">
      <bk-table-column type="selection"
        width="60"
        align="center"
        :selectable="disabledFn">
      </bk-table-column>
      <bk-table-column :label="$t(`m.treeinfo['字段名称']`)" prop="name"></bk-table-column>
      <bk-table-column :label="$t(`m.treeinfo['唯一标识']`)" prop="key"></bk-table-column>
      <bk-table-column :label="$t(`m.treeinfo['字段类型']`)" prop="typeName"></bk-table-column>
      <bk-table-column :label="$t(`m.treeinfo['是否只读']`)">
        <template slot-scope="props">
          <bk-radio-group v-model="props.row.is_readonly">
            <bk-radio :value="trueStatus"
              :disabled="props.row.key === 'priority' || props.row.is_disabled"
              class="mr20">
              {{ $t('m.treeinfo["是"]') }}
            </bk-radio>
            <bk-radio :value="falseStatus"
              :disabled="props.row.key === 'priority' || props.row.is_disabled">
              {{ $t('m.treeinfo["否"]') }}
            </bk-radio>
          </bk-radio-group>
        </template>
      </bk-table-column>
    </bk-table>
  </div>
</template>

<script>
  import { errorHandler } from '../../../../../utils/errorHandler';
  export default {
    name: 'inheritState',
    props: {
      workflow: {
        type: [String, Number],
        default() {
          return '';
        },
      },
      state: {
        type: [String, Number],
        default() {
          return '';
        },
      },
      showTabList: {
        type: Array,
        default() {
          return [];
        },
      },
      configur: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        isDataLoading: false,
        trueStatus: true,
        falseStatus: false,
        dataList: [],
        checkList: [],
      };
    },
    computed: {
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
    },
    mounted() {
      this.getTicketTables();
    },
    methods: {
      // 流程模型字段源
      getTicketTables() {
        const params = {};
        const id = this.workflow;
        this.isDataLoading = true;
        this.$store.dispatch('basicModule/get_ticket_tables', { params, id }).then((res) => {
          this.dataList = res.data.fields;
          this.dataList.forEach((item) => {
            // 字段类型
            this.globalChoise.field_type.forEach((node) => {
              if (item.type === node.typeName) {
                this.$set(item, 'typeName', node.name);
              }
            });
            this.$set(item, 'is_readonly', false);
            this.$set(item, 'is_disabled', false);
            this.showTabList.forEach((tableItem) => {
              if (item.key === tableItem.key) {
                item.is_readonly = tableItem.is_readonly;
                item.is_disabled = true;
              }
            });
            // key === 'priority'的is_readonly总为true
            if (item.key === 'priority') {
              item.is_readonly = true;
            }
          });
          // 提单节点去掉key === 'current_status'
          if (this.configur.is_first_state) {
            this.dataList = this.dataList.filter(item => item.key !== 'current_status');
          }
          // 初始化将勾选的数据选上
          this.$nextTick(() => {
            this.dataList.forEach((item) => {
              if (item.is_disabled) {
                this.$refs.table.toggleRowSelection(item, true);
              }
            });
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
      },
      // 全选 半选
      handleSelectAll(selection) {
        this.checkList = selection;
      },
      handleSelect(selection) {
        this.checkList = selection;
      },
      disabledFn(item) {
        const disabledStatus = this.showTabList.some(tableItem => tableItem.key === item.key);
        return !disabledStatus;
      },
    },
  };
</script>

