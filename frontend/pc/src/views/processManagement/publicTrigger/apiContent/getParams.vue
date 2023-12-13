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
  <div class="bk-get-param">
    <bk-table :data="tableData">
      <bk-table-column :label="$t(`m.treeinfo['名称']`)" prop="name"></bk-table-column>
      <bk-table-column :label="$t(`m.treeinfo['必选']`)">
        <template slot-scope="props">
          {{ props.row.is_necessary ? $t(`m.treeinfo["是"]`) : $t(`m.treeinfo["否"]`) }}
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.treeinfo['备注']`)" width="150">
        <template slot-scope="props">
          <span :title="props.row.desc">{{props.row.desc || '--'}}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.treeinfo['参数值']`)" width="300">
        <template slot-scope="props">
          <div style="width: 120px; position: absolute; top: 5px; left: 15px;">
            <bk-select
              v-model="props.row.sourceType"
              :clearable="false"
              @change="handleSourceTypeChange(props.row)">
              <bk-option
                v-for="option in sourceTypeList"
                :key="option.key"
                :id="option.key"
                :name="option.name">
              </bk-option>
            </bk-select>
          </div>
          <div
            v-if="props.row.sourceType === 'CUSTOM'"
            style="width: 140px; position: absolute; top: 4px; right: 15px;">
            <bk-input
              v-model="localVal[props.row.name]"
              :clearable="true"
              :placeholder="$t(`m.treeinfo['请输入参数值']`)"
              @change="change">
            </bk-input>
          </div>
          <div v-else style="width: 140px; position: absolute; top: 4px; right: 15px;">
            <bk-select
              v-model="localVal[props.row.name]"
              :clearable="false"
              :searchable="true"
              @change="change">
              <bk-option
                v-for="option in triggerVariables"
                :key="option.key"
                :id="option.key"
                :name="option.name">
              </bk-option>
            </bk-select>
          </div>
        </template>
      </bk-table-column>
    </bk-table>
  </div>
</template>

<script>
  import { mapState } from 'vuex';

  export default {
    name: 'getParam',
    components: {},
    props: {
      params: {
        type: Array,
        default: () => [],
      },
      value: {
        type: Object,
        default: () => ({}),
      },
    },
    data() {
      return {
        tableData: [],
        localVal: {},
        sourceTypeList: [
          {
            key: 'CUSTOM',
            name: this.$t('m.treeinfo["自定义"]'),
          },
          {
            key: 'FIELDS',
            name: this.$t('m.treeinfo["引用变量"]'),
          },
        ],
      };
    },
    computed: {
      ...mapState('trigger', {
        triggerVariables: state => state.triggerVariables.map(item => {
          const { key, name } = item;
          return {
            key: `\$\{params_${key}\}`,
            name,
          };
        }),
      }),
    },
    watch: {
      params() {
        this.localVal = {};
        this.initData();
      },
    },
    created() {
      this.initData();
    },
    methods: {
      initData() {
        const tableData = [];
        this.params.forEach(item => {
          const { desc, is_necessary, name, sample, value } = item;
          const val = (name in this.value) ? this.value[name] : value;
          const sourceType = /\$\{params_\w+\}/.test(val) ? 'FIELDS' : 'CUSTOM';
          tableData.push({ desc, is_necessary, name, sample, sourceType });
          this.$set(this.localVal, name, val);
        });
        this.tableData = tableData;
        this.change();
      },
      handleSourceTypeChange(row) {
        row.value = '';
        this.change();
      },
      change() {
        this.$emit('change', this.localVal);
      },
    },
  };
</script>

<style lang="scss" scoped>
    @import '../../../../scss/mixins/clearfix.scss';

    .bk-get-param {
        color: #424950;
        font-size: 14px;
        font-weight: normal;
        @include clearfix;
        .bk-border-error {
            border-color: #ff5656;
        }
    }
</style>
