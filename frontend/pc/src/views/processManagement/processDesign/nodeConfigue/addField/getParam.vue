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
      :data="paramTableData"
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
          <template v-if="isStatic">
            {{props.row.customValue || '--'}}
          </template>
          <template v-else-if="isCustom">
            <bk-input
              :clearable="true"
              :placeholder="$t(`m.treeinfo['请输入参数值']`)"
              v-model="props.row.customValue">
            </bk-input>
          </template>
          <template v-else>
            <div style="width: 120px; position: absolute; top: 5px; left: 15px;">
              <bk-select v-model="props.row.source_type"
                :clearable="false"
                searchable
                :font-size="'medium'">
                <bk-option v-for="option in sourceTypeList"
                  :key="option.key"
                  :id="option.key"
                  :name="option.name">
                </bk-option>
              </bk-select>
            </div>
            <div v-if="props.row.source_type === 'CUSTOM'"
              style="width: 140px; position: absolute; top: 4px; right: 15px;">
              <bk-input :class="{ 'bk-border-error': props.row.isCheck && !props.row.value.toString() }"
                :clearable="true"
                :placeholder="$t(`m.treeinfo['请输入参数值']`)"
                v-model="props.row.value">
              </bk-input>
            </div>
            <div v-else style="width: 140px; position: absolute; top: 4px; right: 15px;">
              <bk-select :class="{ 'bk-border-error': props.row.isCheck && !props.row.value.toString() }"
                v-model="props.row.value_key"
                :clearable="false"
                searchable
                :font-size="'medium'">
                <bk-option v-for="option in stateList"
                  :key="option.key"
                  :id="option.key"
                  :name="option.name">
                </bk-option>
                <template v-if="entry !== 'addField'">
                  <div slot="extension" @click="addNewItem(props.row)" style="cursor: pointer;">
                    <i class="bk-icon icon-plus-circle mr10"></i>{{ $t('m.treeinfo["添加变量"]') }}
                  </div>
                </template>
              </bk-select>
            </div>
          </template>
        </template>
      </bk-table-column>
    </bk-table>
  </div>
</template>

<script>
  export default {
    name: 'getParam',
    components: {},
    props: {
      changeInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      apiDetail: {
        type: Object,
        default: () => {
        },
      },
      stateList: {
        type: Array,
        default() {
          return [];
        },
      },
      // 是否仅展示 数据
      isStatic: {
        type: Boolean,
        default() {
          return false;
        },
      },
      isCustom: {
        type: Boolean,
        default() {
          return false;
        },
      },
      // 静态展示 -- 参数值
      queryValue: {
        type: Object,
        default() {
          return {};
        },
      },
      entry: {
        type: String,
        default() {
          return '';
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
        paramTableData: [],
        // 校验
        checkInfo: {
          name: '',
          road: '',
        },
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
        paramTableInfo: {
          value: '',
          placeholder: this.$t('m.treeinfo["请选择数据来源"]'),
        },
      };
    },
    computed: {},
    watch: {
      apiDetail() {
        this.initData();
      },
    },
    async mounted() {
      await this.changeInfo;
      await this.isStatic;
      await this.queryValue;
      await this.initData();
    },
    methods: {
      async initData() {
        const paramTableData = await JSON.parse(JSON.stringify(this.apiDetail.req_params)) || [];
        await paramTableData.forEach((item) => {
          item.isCheck = false;
          item.isSatisfied = false;
          // 定位
          item.el = null;
          item.customValue = item.value || '';
          item.source_type = 'CUSTOM';
          item.value_key = '';
          // 赋值
          if (!this.isStatic) {
            // 配置信息（api字段/自动节点配置信息） 赋值
            if (this.changeInfo.api_info && Object.keys(this.changeInfo.api_info.req_params).length
              && this.changeInfo.api_info.remote_api_id === this.apiDetail.id) {
              if (/^\$\{params_.*\}$/.test(this.changeInfo.api_info.req_params[item.name])) {
                item.source_type = 'FIELDS';
                item.value_key = this.changeInfo.api_info.req_params[item.name] ? JSON.parse(JSON.stringify(this.changeInfo.api_info.req_params[item.name])).replace(/^\$\{params_/, '')
                  .replace(/\}$/, '') : '';
              } else {
                const reqParamsName = this.changeInfo.api_info.req_params[item.name];
                item.source_type = 'CUSTOM';
                item.value = reqParamsName;
              }
            }
          } else {
            // 静态展示（自动节点执行信息） 赋值
            item.value = this.queryValue[item.name] || '';
          }
        });
        this.paramTableData = await JSON.parse(JSON.stringify(paramTableData));
      },
      addNewItem(data) {
        this.$emit('addNewItem', data);
      },
    },
  };
</script>

<style lang="scss" scoped>
    @import '../../../../../scss/mixins/clearfix.scss';

    .bk-get-param {
        color: #424950;
        font-size: 14px;
        font-weight: normal;
        @include clearfix;

        .bk-more {
            display: flex;

            &.bk-value {
                position: relative;
            }
        }

        .bk-border-error {
            border-color: #ff5656;
        }
    }
</style>
