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
      :data="tableList"
      :size="'small'">
      <bk-table-column :label="$t(`m.treeinfo['名称']`)" min-width="200">
        <template slot-scope="props">
          <div class="bk-more">
            <span :style="{ paddingLeft: 20 * props.row.level + 'px' }">
              <span
                v-if="props.row.has_children"
                :class="['bk-icon', 'tree-expanded-icon', props.row.showChildren ? 'icon-down-shape' : 'icon-right-shape']"
                @click="changeState(props.row)">
              </span>
              <span class="bk-icon bk-more-icon" v-else> </span>
              <span>{{props.row.key || '--'}}</span>
            </span>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.treeinfo['类型']`)" prop="type"></bk-table-column>
      <bk-table-column :label="$t(`m.treeinfo['是否必须']`)">
        <template slot-scope="props">
          {{ props.row.is_necessary ? $t(`m.treeinfo["是"]`) : $t(`m.treeinfo["否"]`) }}
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.treeinfo['备注']`)" width="100">
        <template slot-scope="props">
          <span :title="props.row.desc">{{props.row.desc || '--'}}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.treeinfo['参数值']`)" width="300">
        <template slot-scope="props">
          <template v-if="isStatic && (props.row.type !== 'object') && (props.row.type !== 'array')">
            {{props.row.customValue || '--'}}
          </template>
          <template v-else-if="isCustom && (props.row.type !== 'object') && (props.row.type !== 'array')">
            <bk-input
              :type="props.row.type === 'string' ? 'text' : 'number'"
              :placeholder="$t(`m.treeinfo['请输入参数值']`)"
              v-model="props.row.customValue">
            </bk-input>
          </template>
          <template v-else>
            <template v-if="(props.row.type !== 'object') && (props.row.type !== 'array')">
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
              <div v-if="!props.row.source_type || (props.row.source_type === 'CUSTOM')"
                style="width: 140px; position: absolute; top: 4px; right: 15px;">
                <template v-if="props.row.type === 'string' || props.row.type === 'number'">
                  <bk-input :class="{ 'bk-border-error': props.row.isCheck && !props.row.value.toString() }"
                    :type="props.row.type === 'string' ? 'text' : 'number'"
                    :placeholder="$t(`m.treeinfo['请输入参数值']`)"
                    v-model="props.row.value">
                  </bk-input>
                </template>
                <template v-if="props.row.type === 'boolean'">
                  <bk-radio-group v-model="props.row.value">
                    <bk-radio :value="trueSatatus">true</bk-radio>
                    <bk-radio :value="falseSatatus">false</bk-radio>
                  </bk-radio-group>
                </template>
              </div>
              <div v-else style="width: 140px; position: absolute; top: 4px; right: 15px;">
                <bk-select :class="{ 'bk-border-error': props.row.isCheck && !props.row.value_key.toString() }"
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
                      <i class="bk-icon icon-plus-circle"></i>{{ $t('m.treeinfo["添加变量"]') }}
                    </div>
                  </template>
                </bk-select>
              </div>
            </template>
            <div class="bk-between-operat" v-if="!isStatic && props.row.lastType === 'array'">
              <i class="bk-itsm-icon icon-flow-add" @click="addChildren(props.row)"></i>
              <i class="bk-itsm-icon icon-flow-reduce"
                :class="{ 'bk-no-delete': countSon(props.row) }"
                @click="deletChildren(props.row)" v-if="props.row.lastType === 'array'"></i>
            </div>
          </template>
        </template>
      </bk-table-column>
    </bk-table>
  </div>
</template>

<script>
  import mixins from '../../../../commonMix/mixins_api.js';

  export default {
    name: 'postParam',
    mixins: [mixins],
    props: {
      // body参数配置信息
      changeInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      // api接口信息
      apiDetail: {
        type: Object,
        default: () => {
        },
      },
      // 引用变量/字段/全局变量
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
      // 自定义数据
      isCustom: {
        type: Boolean,
        default: false,
      },
      // 静态展示 -- 参数值
      bodyValue: {
        type: Object,
        default: () => {
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
        trueSatatus: true,
        falseSatatus: false,
        lala: {
          value: '111',
          offsetTop: '',
        },
        bodyTableData: [],
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
    computed: {
      tableList() {
        return this.bodyTableData.filter(item => item.isShow);
      },
    },
    watch: {
      apiDetail() {
        this.initData();
      },
    },
    async mounted() {
      await this.isStatic;
      await this.bodyValue;
      await this.initData();
    },
    methods: {
      initData() {
        this.bodyTableDataChange();
      },
      async bodyTableDataChange() {
        // 初始化数据 多层列表
        if (!Object.keys(this.apiDetail.req_body).length) {
          this.apiDetail.treeDataList = [{
            has_children: false,
            showChildren: true,
            checkInfo: false,
            key: 'root',
            is_necessary: true,
            type: 'object',
            desc: this.$t('m.treeinfo["初始化数据"]'),
            parentInfo: '',
            children: [],
          }];
          this.apiDetail.bodyTableData = [];
        } else {
          this.apiDetail.treeDataList = await this.jsonschemaToList({
            root: JSON.parse(JSON.stringify(this.apiDetail.req_body)), // root初始 Jsonschema数据结构
          });
          // 赋值
          if (!this.isStatic && !this.isCustom) {
            // 配置信息（api字段/自动节点配置信息） 赋值
            if (this.changeInfo.api_info && this.changeInfo.api_info.remote_api_id === this.apiDetail.id) {
              this.apiDetail.treeDataList = this.jsonValueToTree(this.changeInfo.api_info.req_body, JSON.parse(JSON.stringify(this.apiDetail.treeDataList)));
            }
          } else {
            // 静态展示（自动节点执行信息） 赋值
            this.apiDetail.treeDataList = this.jsonValueToTree(this.bodyValue, JSON.parse(JSON.stringify(this.apiDetail.treeDataList)));
          }
          // 生成table表格数据
          this.apiDetail.bodyTableData = await this.treeToTableList(JSON.parse(JSON.stringify(this.apiDetail.treeDataList[0].children)));
        }
        const bodyTableData = await JSON.parse(JSON.stringify(this.apiDetail.bodyTableData));
        // 加入/引用变量
        await bodyTableData.forEach((item) => {
          // 校验数据
          item.isCheck = false;
          item.isSatisfied = false;
          // 定位
          item.el = null;
          item.customValue = item.value || '';
          item.name = item.key || '';
          item.children = [];
          item.source_type = item.source_type || 'CUSTOM';
          item.value = (item.value !== undefined) ? item.value : '';
          item.value_key = ((item.value_key !== undefined) && item.value_key.toString()) ? item.value_key : '';
        });
        // 多层列表数据 关联 table表格数据
        await this.recordChildren(bodyTableData);
        this.bodyTableData = await bodyTableData;
      },
      recordChildren(tableData, levelInitial) {
        const levelList = tableData.map(item => item.level);
        const maxLevel = Math.max(...levelList);
        const recordChildrenStep = function (tableData, item) {
          tableData.filter(ite => (ite.level === item.level - 1 && ite.primaryKey === item.parentPrimaryKey && ite.ancestorsList.toString() === item.ancestorsList.slice(0, -1).toString()))[0].children.push(item);
        };
        for (let i = maxLevel; i > (levelInitial || 0); i--) {
          tableData.filter(item => item.level === i).forEach((ite) => {
            recordChildrenStep(tableData, ite);
          });
        }
      },
      // 展示子集
      changeState(item) {
        item.showChildren = !item.showChildren;
        item.children.forEach((ite) => {
          ite.isShow = item.showChildren;
        });
        if (!item.showChildren) {
          this.closeChildren(item);
        }
      },
      // 关闭所有子集
      closeChildren(item) {
        item.children.forEach((ite) => {
          ite.isShow = false;
          if (ite.has_children) {
            ite.showChildren = false;
            this.closeChildren(ite);
          }
        });
      },
      changeType() {
      },
      // 计算所有子孙元素
      async countChildren(dataOri) {
        let count = 0;
        const countChildrenStep = function (data) {
          if (data.children && data.children.length) {
            for (let i = 0; i < data.children.length; i++) {
              count += 1;
              countChildrenStep(data.children[i]);
            }
          }
        };
        await countChildrenStep(dataOri);
        return count;
      },
      // 清除变量值
      async cleanValue(item) {
        const copyItem = JSON.parse(JSON.stringify(item));
        const countChildrenStep = function (data) {
          data.value = '';
          data.source_type = 'CUSTOM';
          if (data.children && data.children.length) {
            for (let i = 0; i < data.children.length; i++) {
              countChildrenStep(data.children[i]);
            }
          }
        };
        await countChildrenStep(copyItem);
        return copyItem;
      },
      // 计算子元素
      countSon(itemChildren) {
        const item = this.bodyTableData.filter(ite => (ite.level === itemChildren.level - 1 && ite.primaryKey === itemChildren.parentPrimaryKey))[0];
        return item.children.length === 1;
      },
      // 添加 array 列表元素
      async addChildren(itemChildren) {
        const item = this.bodyTableData.filter(ite => (ite.level === itemChildren.level - 1 && ite.primaryKey === itemChildren.parentPrimaryKey))[0];

        const index = this.bodyTableData.indexOf(item) + 1;
        const count = await this.countChildren(item);
        const copyItem = await this.cleanValue(item.children[0]);
        const insertList = await this.treeToTableList(
          JSON.parse(JSON.stringify([...item.children, copyItem])), item.level + 1,
          item.primaryKey, 'array', item.ancestorsList
        );
        await insertList.forEach((ite) => {
          ite.children = [];
        });
        item.children = insertList.filter(ite => ite.level === item.level + 1);
        await this.recordChildren(insertList, item.level + 1);
        this.bodyTableData.splice(index, count, ...insertList);
      },
      // 删除元素
      async deletChildren(item) {
        if (this.countSon(item)) {
          return;
        }
        const currentObj = this.bodyTableData.filter(ite => (ite.level === item.level - 1 && ite.primaryKey === item.parentPrimaryKey))[0].children;
        if (currentObj.length <= 1) {
          return;
        }
        currentObj.splice(currentObj.indexOf(item), 1);
        const index = this.bodyTableData.indexOf(item);
        const count = await this.countChildren(item);
        this.bodyTableData.splice(index, count + 1);
      },
      async changeField(node, value) {
        await value;
      },
      addNewItem(data) {
        this.$emit('addNewItem', data);
      },
    },
  };
</script>

<style lang="scss" scoped>
    @import '../../../../../scss/mixins/clearfix.scss';
    @import '../../../../../scss/mixins/scroller.scss';

    .bk-more {
        &.bk-value {
            // padding-right: 72px;
            position: relative;
            justify-content: space-between;
        }

        overflow: visible;
        display: flex;
        align-items: center;

        .bk-icon {
            padding-right: 5px;
            color: #c0c4cc;
            cursor: pointer;
        }

        .bk-more-icon {
            width: 17px;
        }
    }

    .bk-body-value {
        width: 100%;
        background: white;
        display: flex;
        justify-content: flex-start;

        .bk-form-radio:nth-child(1) {
            // margin: 0 10px;
            margin-right: 10px;
        }
        & > div {
            display: inherit;
        }
        .bk-form-radio {
            display: inherit;
            margin: 0;
        }
    }

    .bk-between-operat {
        font-size: 18px;
        position: absolute;
        top: 7px;
        right: 10px;
        .bk-itsm-icon {
            color: #C4C6CC;
            margin-right: 5px;

            &:hover {
                color: #979BA5;
            }

            &.bk-no-delete {
                color: #DCDEE5;
                cursor: not-allowed;

                &:hover {
                    color: #DCDEE5;
                }
            }

            cursor: pointer;
        }
    }
    .fade-enter-active, .fade-leave-active {
        transition: all .5s ease;
    }

    .fade-enter, .fade-leave-to {
        transition: all .5s ease;
    }

    .list-enter-active, .list-leave-active {
        transition: all .2s;
    }
</style>
