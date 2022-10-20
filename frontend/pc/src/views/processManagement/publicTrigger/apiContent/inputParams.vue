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
  <div class="bk-input-params">
    <bk-table
      :data="paramTableData"
      :size="'small'">
      <bk-table-column :label="$t(`m.treeinfo['名称']`)" min-width="150">
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
      <bk-table-column :label="$t(`m.treeinfo['必选']`)" width="60">
        <template slot-scope="props">
          {{ props.row.is_necessary ? $t(`m.treeinfo["是"]`) : $t(`m.treeinfo["否"]`) }}
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.treeinfo['备注']`)" width="200">
        <template slot-scope="props">
          <span :title="props.row.desc">{{props.row.desc || '--'}}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.treeinfo['参数值']`)" width="280">
        <template slot-scope="props">
          <template v-if="(props.row.type !== 'object') && (props.row.type !== 'array')">
            <div style="width: 120px; position: absolute; top: 5px; left: 10px;">
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
            <div v-if="!props.row.source_type || (props.row.source_type === 'CUSTOM')"
              style="width: 120px; position: absolute; top: 4px; right: 10px;">
              <template v-if="props.row.type === 'string' || props.row.type === 'number'">
                <bk-input :type="props.row.type === 'string' ? 'text' : 'number'"
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
            <div v-else style="width: 120px; position: absolute; top: 5px; right: 10px;">
              <bk-select v-model="props.row.value_key"
                :clearable="false"
                searchable>
                <bk-option v-for="option in variableList"
                  :key="option.key"
                  :id="option.key"
                  :name="option.name">
                </bk-option>
              </bk-select>
            </div>
          </template>
        </template>
      </bk-table-column>
      <bk-table-column width="60" class-name="last-add-row-column">
        <template slot-scope="props">
          <div class="bk-between-operat" v-if="props.row.lastType === 'array'">
            <i class="bk-itsm-icon icon-flow-add" @click="addChildren(props.row)"></i>
            <i class="bk-itsm-icon icon-flow-reduce"
              :class="{ 'bk-no-delete': countSon(props.row) }"
              v-if="props.row.lastType === 'array'"
              @click="deletChildren(props.row)"></i>
          </div>
        </template>
      </bk-table-column>
    </bk-table>
  </div>
</template>
<script>
  import mixins from '../../../commonMix/mixins_api.js';
  import { deepClone } from '../../../../utils/util';
  import { mapState } from 'vuex';
  export default {
    name: 'inputParams',
    mixins: [mixins],
    props: {
      itemInfo: {
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
        variableList: [],
      };
    },
    computed: {
      paramTableData() {
        return this.itemInfo.apiContent.bodyTableData.filter(item => item.isShow);
      },
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
      ...mapState('trigger', {
        triggerVariables: state => state.triggerVariables,
      }),
    },
    watch: {
      triggerVariables(newVal) {
        this.variableList = newVal;
      },
    },
    created() {
      this.initData();
    },
    mounted() {
      this.variableList = this.triggerVariables;
    },
    methods: {
      async initData() {
        this.$set(this.itemInfo.apiContent, 'treeDataList', {});
        this.itemInfo.apiContent.treeDataList = await this.jsonschemaToList({
          root: JSON.parse(JSON.stringify(this.itemInfo.apiContent.req_body)),
        });
        // 如果数据已经存在，则进行表格初始化赋值
        if (this.itemInfo.value) {
          this.itemInfo.apiContent.treeDataList = this.jsonValueTreeList(this.itemInfo.value, JSON.parse(JSON.stringify(this.itemInfo.apiContent.treeDataList)));
        }
        // 生成table表格数据
        this.itemInfo.apiContent.bodyTableData = await this.treeToTableList(JSON.parse(JSON.stringify(this.itemInfo.apiContent.treeDataList[0].children)));
        const bodyTableData = JSON.parse(JSON.stringify(this.itemInfo.apiContent.bodyTableData));
        // 加入/引用变量
        bodyTableData.forEach((item) => {
          item.name = item.key || '';
          item.children = [];
          item.source_type = item.source_type || 'CUSTOM';
          item.value = (item.value !== undefined) ? item.value : '';
          item.value_key = ((item.value_key !== undefined) && item.value_key.toString()) ? item.value_key : '';
        });
        // 多层列表数据 关联 table表格数据
        this.recordChildren(bodyTableData);
        this.itemInfo.apiContent.bodyTableData = await bodyTableData;
      },
      jsonValueTreeList(jsonData, treeDataList) {
        const listToJsonStep = function (lastObject, insertObject, key, item, lastType) {
          if (lastType === 'object') {
            const reqData = insertObject.filter(ite => ite.key === key);
            if (!reqData.length) {
              return;
            }
            // reqData[0]
            if (item.constructor.name.toLowerCase() === 'array') {
              if (!reqData[0].children || !reqData[0].children.length) {
                return;
              }
              const oneItem = JSON.parse(JSON.stringify(Object.assign({ parentInfo: '' }, reqData[0].children[0])));
              for (let i = 1; i < item.length; i++) {
                reqData[0].children.push(deepClone(oneItem));
              }
              for (const j in item) {
                listToJsonStep(reqData[0].children, reqData[0].children[j], 'items', item[j], 'array');
              }
            } else if (item.constructor.name.toLowerCase() === 'object') {
              if (item.ref_type) {
                if (item.ref_type === 'reference') {
                  reqData[0].source_type = 'FIELDS';
                  reqData[0].value_key = item.value;
                  reqData[0].value = item.value;
                } else {
                  reqData[0].source_type = 'CUSTOM';
                  reqData[0].value = item.value;
                  reqData[0].value_key = '';
                  // 改变默认值
                  reqData[0].default_temp = reqData[0].value;
                }
              } else {
                for (const j in item) {
                  listToJsonStep(reqData[0], reqData[0].children, j, item[j], 'object');
                }
              }
            } else {
              if (item.ref_type === 'reference') {
                reqData[0].source_type = 'FIELDS';
                reqData[0].value_key = item.value;
                reqData[0].value = item.value;
              } else {
                reqData[0].source_type = 'CUSTOM';
                reqData[0].value = item.value;
                reqData[0].value_key = '';
                // 改变默认值
                reqData[0].default_temp = reqData[0].value;
              }
            }
          } else if (lastType === 'array') {
            if (item.constructor.name.toLowerCase() === 'array') {
              const reqData = insertObject.filter(ite => ite.key === key);
              if (!reqData.length) {
                return;
              } // 待定？？？
              if (!reqData[0].children || !reqData[0].children.length) {
                return;
              }
              const oneItem = JSON.parse(JSON.stringify(insertObject.children[0]));
              for (let i = 1; i < item.length; i++) {
                insertObject.children.push(oneItem);
              }
              for (const j in item) {
                listToJsonStep(insertObject.children, insertObject.children[j], 'items', item[j], 'array');
              }
            } else if (item.constructor.name.toLowerCase() === 'object') {
              if (item.ref_type) {
                if (item.ref_type === 'reference') {
                  insertObject.source_type = 'FIELDS';
                  insertObject.value_key = item.value;
                } else {
                  insertObject.source_type = 'CUSTOM';
                  insertObject.value = item.value;
                  // 改变默认值
                  insertObject.default_temp = insertObject.value;
                }
              } else {
                for (const j in item) {
                  listToJsonStep(insertObject, insertObject.children, j, item[j], 'object');
                }
              }
            } else {
              if (item.ref_type === 'reference') {
                insertObject.source_type = 'FIELDS';
                insertObject.value_key = item.value;
              } else {
                insertObject.source_type = 'CUSTOM';
                insertObject.value = item.value;
                // 改变默认值
                insertObject.default_temp = insertObject.value;
              }
            }
          }
        };
        for (const key in jsonData) {
          listToJsonStep(treeDataList[0], treeDataList[0].children, key, jsonData[key], 'object', 0);
        }
        return treeDataList;
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
      // 计算子元素
      countSon(itemChildren) {
        const item = this.itemInfo.apiContent.bodyTableData.filter(ite => (ite.level === itemChildren.level - 1 && ite.primaryKey === itemChildren.parentPrimaryKey && ite.ancestorsList.toString() === itemChildren.ancestorsList.slice(0, -1).toString()))[0];
        return item.children.length === 1;
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
      // 添加 array 列表元素
      async addChildren(itemChildren) {
        const item = this.itemInfo.apiContent.bodyTableData.filter(ite => (ite.level === itemChildren.level - 1 && ite.primaryKey === itemChildren.parentPrimaryKey && ite.ancestorsList.toString() === itemChildren.ancestorsList.slice(0, -1).toString()))[0];

        const index = this.itemInfo.apiContent.bodyTableData.indexOf(item) + 1;
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
        this.itemInfo.apiContent.bodyTableData.splice(index, count, ...insertList);
      },
      // 删除元素
      async deletChildren(item) {
        if (this.countSon(item)) {
          return;
        }
        const currentObj = this.itemInfo.apiContent.bodyTableData.filter(ite => (ite.level === item.level - 1 && ite.primaryKey === item.parentPrimaryKey && ite.ancestorsList.toString() === item.ancestorsList.slice(0, -1).toString()))[0].children;
        if (currentObj.length <= 1) {
          return;
        }
        currentObj.splice(currentObj.indexOf(item), 1);
        const index = this.itemInfo.apiContent.bodyTableData.indexOf(item);
        const count = await this.countChildren(item);
        this.itemInfo.apiContent.bodyTableData.splice(index, count + 1);
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../../scss/mixins/clearfix.scss';
    /deep/ .last-add-row-column {
        .cell {
            padding: 0;
        }
        .bk-between-operat {
            font-size: 18px;
            .bk-itsm-icon {
                color: #C4C6CC;
                cursor: pointer;
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
            }
        }
    }
</style>
