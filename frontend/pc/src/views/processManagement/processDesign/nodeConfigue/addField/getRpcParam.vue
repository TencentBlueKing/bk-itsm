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
    <bk-table
      :data="prcTable"
      :size="'small'">
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
            <bk-select v-model="props.row.source_type"
              :clearable="false"
              searchable>
              <bk-option v-for="option in sourceTypeList"
                :key="option.key"
                :id="option.key"
                :name="option.name">
              </bk-option>
            </bk-select>
          </div>
          <div v-if="props.row.source_type === 'CUSTOM'"
            style="width: 140px; position: absolute; top: 4px; right: 15px;">
            <bk-input :clearable="true"
              :placeholder="$t(`m.treeinfo['请输入参数值']`)"
              v-model="props.row.value">
            </bk-input>
          </div>
          <div v-else style="width: 140px; position: absolute; top: 4px; right: 15px;">
            <bk-select v-model="props.row.value_key"
              :clearable="false"
              searchable>
              <bk-option v-for="option in stateList"
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
  export default {
    name: 'getRpcParam',
    components: {},
    props: {
      prcTable: {
        type: Array,
        default() {
          return [];
        },
      },
      changeInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      stateList: {
        type: Array,
        default() {
          return [];
        },
      },
      formInfo: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        sourceTypeList: [
          {
            id: 1,
            key: 'CUSTOM',
            name: this.$t('m.treeinfo["自定义"]'),
          },
          {
            id: 2,
            key: 'FIELDS',
            name: this.$t('m.treeinfo["引用变量"]'),
          },
        ],
      };
    },
    computed: {},
    watch: {
      prcTable() {
        this.initData();
      },
    },
    async mounted() {
      await this.changeInfo;
      this.initData();
    },
    methods: {
      initData() {
        this.prcTable.forEach((item) => {
          this.$set(item, 'isCheck', false);
          this.$set(item, 'isSatisfied', false);
          this.$set(item, 'el', null);
          this.$set(item, 'source_type', 'CUSTOM');
          this.$set(item, 'value_key', '');
          // 赋值
          for (const key in this.changeInfo.meta) {
            if (item.name === key) {
              if (this.changeInfo.meta[key].indexOf('{params_') !== -1) {
                item.source_type = 'FIELDS';
                item.value_key = this.changeInfo.meta[key].split('${params_')[1].split('}')[0];
              } else {
                item.source_type = 'CUSTOM';
                item.value = this.changeInfo.meta[key];
              }
            }
          }
        });
      },
    },
  };
</script>

<style lang="scss" scoped>

</style>
