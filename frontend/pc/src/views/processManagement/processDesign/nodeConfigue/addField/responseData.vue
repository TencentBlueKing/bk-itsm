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
    <div class="bk-params-title">
      {{ $t('m.treeinfo["返回数据"]') }}
    </div>
    <!-- new -->
    <div class="bk-param-three">
      <!-- tree -->
      <bk-form-item :label="$t(`m.treeinfo['选取数组']`)" :required="true">
        <div class="bk-form-content bk-dialog-input">
          <div ref="cascader">
            <!-- 组织架构 -->
            <template>
              <div class="bk-search-tree" style="width: 100%; float: left;"
                v-bk-clickoutside="closeOther0">
                <template>
                  <div class="bk-search-tree-wrapper"
                    v-if="(changeInfo.is_builtin || formInfo.isModule) && formInfo.key !== 'bk_biz_id'"
                    :class="{ 'bk-border-red': checkInfo.assignors, 'bk-back-color': (changeInfo.is_builtin || formInfo.isModule) && formInfo.key !== 'bk_biz_id' }">
                    <span :class="{ 'bk-color-tree': organization.assignorTree.name }">{{organization.assignorTree.name || $t(`m.treeinfo["请选择"]`)}}</span>
                    <i class="bk-select-angle bk-icon icon-framework"></i>
                  </div>
                  <div class="bk-search-tree-wrapper"
                    v-else
                    @click.stop="showTree(0)"
                    :class="{ 'bk-border-red': checkInfo.assignors, 'bk-back-color': (changeInfo.is_builtin || formInfo.isModule) && formInfo.key !== 'bk_biz_id' }">
                    <span :class="{ 'bk-color-tree': organization.assignorTree.name }">{{organization.assignorTree.name || $t(`m.treeinfo["请选择"]`)}}</span>
                    <i class="bk-select-angle bk-icon icon-framework"></i>
                  </div>
                </template>

                <transition name="fade">
                  <div class="bk-search-tree-content" v-if="organizaInfo.assignorShow[0]"
                    :style="{ width: (maxLevelTree[0] * 50) + '%' }">
                    <export-tree
                      :disabled="(changeInfo.is_builtin || formInfo.isModule) && formInfo.key !== 'bk_biz_id'"
                      :tree-data-list="organization.assignorPerson"
                      :is-key-value="0"
                      @toggle="assignorToggle" @toggleChildren="toggleChildren"></export-tree>
                  </div>
                </transition>
              </div>
            </template>
          </div>
        </div>
      </bk-form-item>
      <bk-form-item :label="$t(`m.treeinfo['关键字字段']`)" :required="true">
        <div class="bk-form-content bk-dialog-input">
          <div ref="cascader">
            <template>
              <div class="bk-search-tree" style="width: 100%; float: left;"
                v-bk-clickoutside="closeOther1">
                <template>
                  <div class="bk-search-tree-wrapper"
                    v-if="(changeInfo.is_builtin || formInfo.isModule) && formInfo.key !== 'bk_biz_id'"
                    :class="{ 'bk-back-color': (changeInfo.is_builtin || formInfo.isModule) && formInfo.key !== 'bk_biz_id' }">
                    <span :class="{ 'bk-color-tree': settingKeyName }">{{settingKeyName || $t(`m.treeinfo["请选择"]`)}}</span>
                    <i class="bk-select-angle bk-icon icon-framework"></i>
                  </div>
                  <div class="bk-search-tree-wrapper"
                    v-else
                    @click.stop="showTree(1)"
                    :class="{ 'bk-back-color': (changeInfo.is_builtin || formInfo.isModule) && formInfo.key !== 'bk_biz_id' }">
                    <span :class="{ 'bk-color-tree': settingKeyName }">{{settingKeyName || $t(`m.treeinfo["请选择"]`)}}</span>
                    <i class="bk-select-angle bk-icon icon-framework"></i>
                  </div>
                </template>

                <transition name="fade">
                  <div class="bk-search-tree-content" v-if="organizaInfo.assignorShow[1]"
                    :style="{ width: (maxLevelTree[1] * 50) + '%' }">
                    <export-tree
                      :disabled="(changeInfo.is_builtin || formInfo.isModule) && formInfo.key !== 'bk_biz_id'"
                      :tree-data-list="selectInfo.selectkeylist"
                      :is-key-value="1"
                      @toggle="assignorToggle" @toggleChildren="toggleChildren"></export-tree>
                  </div>
                </transition>
              </div>
            </template>
          </div>
        </div>
      </bk-form-item>
      <bk-form-item :label="$t(`m.treeinfo['显示字段']`)" :required="true">
        <div class="bk-form-content bk-dialog-input">
          <div ref="cascader">
            <template>
              <div class="bk-search-tree" style="width: 100%; float: left;"
                v-bk-clickoutside="closeOther2">
                <template>
                  <div class="bk-search-tree-wrapper"
                    v-if="(changeInfo.is_builtin || formInfo.isModule) && formInfo.key !== 'bk_biz_id'"
                    :class="{ 'bk-back-color': (changeInfo.is_builtin || formInfo.isModule) && formInfo.key !== 'bk_biz_id' }">
                    <span :class="{ 'bk-color-tree': settingValueName }">{{settingValueName || $t(`m.treeinfo["请选择"]`)}}</span>
                    <i class="bk-select-angle bk-icon icon-framework"></i>
                  </div>
                  <div class="bk-search-tree-wrapper"
                    v-else
                    @click.stop="showTree(2)"
                    :class="{ 'bk-back-color': (changeInfo.is_builtin || formInfo.isModule) && formInfo.key !== 'bk_biz_id' }">
                    <span :class="{ 'bk-color-tree': settingValueName }">{{settingValueName || $t(`m.treeinfo["请选择"]`)}}</span>
                    <i class="bk-select-angle bk-icon icon-framework"></i>
                  </div>
                </template>

                <transition name="fade">
                  <div class="bk-search-tree-content" v-if="organizaInfo.assignorShow[2]"
                    :style="{ width: (maxLevelTree[2] * 50) + '%' }">
                    <export-tree
                      :disabled="(changeInfo.is_builtin || formInfo.isModule) && formInfo.key !== 'bk_biz_id'"
                      :tree-data-list="selectInfo.selectvaluelist"
                      :is-key-value="2"
                      @toggle="assignorToggle"
                      @toggleChildren="toggleChildren"></export-tree>
                  </div>
                </transition>
              </div>
            </template>
          </div>
        </div>
      </bk-form-item>
    </div>
  </div>
</template>

<script>
  import mixins from '../../../../commonMix/mixins_api.js';
  import exportTree from './exportApiTree.vue';
  import _ from 'lodash';

  export default {
    name: 'responseData',
    components: {
      exportTree,
    },
    mixins: [mixins],
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
      remoteApiIid: {
        type: [String, Number],
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
        // apiDetail: this.apiDetailOri,
        // 组织架构
        organization: {
          processorPerson: [],
          processorTree: {},
          assignorPerson: [],
          assignorTree: {},
        },
        organizaInfo: {
          assignorShow: [false, false, false],
        },
        cascaderData: [],
        bodyTableData: [],
        responseTableData: [],
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
        selectInfo: {
          selectkeylist: [],
          selectkey: '',
          selectvaluelist: [],
          selectvalue: '',
        },
        isShow: false,
        // 临时值 中转用 选中的 // 关键字字段/显示字段
        tampFormInfo: {
          ancestorsList_str: '',
          isSelectedKey: '',
          isSelectedValue: '',
          settingKeyName: '',
          settingValueName: '',
        },
        isCheck: false,
        maxLevel: 1,
        maxLevelTree: [1, 1, 1],
        settingKeyName: '',
        settingValueName: '',
      };
    },
    computed: {},
    watch: {
      'apiDetail.rsp_data':
        {
          handler() {
            this.initData();
          },
          deep: true,
        },
    },
    mounted() {
      this.initData();
    },
    methods: {
      initData() {
        this.responseTableDataChange();
      },
      async responseTableDataChange() {
        this.selectInfo = {
          selectkeylist: [],
          selectkey: '',
          selectvaluelist: [],
          selectvalue: '',
        };
        this.organization = {
          processorPerson: [],
          processorTree: {},
          assignorPerson: [],
          assignorTree: {},
        };
        this.maxLevel = 1;
        this.maxLevelTree = [1, 1, 1];
        this.settingKeyName = '';
        this.settingValueName = '';
        await this.changeInfo;
        // 初始化数据
        if (!Object.keys(this.apiDetail.rsp_data).length) {
          this.apiDetail.responseTreeDataList = [{
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
          this.apiDetail.responseTableData = [];
        } else {
          this.apiDetail.responseTreeDataList = await this.jsonschemaToList({
            root: JSON.parse(JSON.stringify(this.apiDetail.rsp_data)), // root初始 Jsonschema数据结构
          });
          // 生成table表格数据
          this.apiDetail.responseTableData = await this.treeToTableList(JSON.parse(JSON.stringify(this.apiDetail.responseTreeDataList[0].children)));
        }
        const responseTableData = await JSON.parse(JSON.stringify(this.apiDetail.responseTableData));
        // 构造 引用变量
        await responseTableData.forEach((item) => {
          item.children = [];
          // 数据来源
          item.source_type = 'CUSTOM';
          // 值
          item.value = '';
          // 属性
          item.name = item.key;
          // 是否可选
          item.isSelectAbled = false;
          // 是否选中
          item.isSelectedKey = false;
          // 是否禁用可选
          item.isSelectedKeyDisabled = false;
          // 是否选中
          item.isSelectedValue = false;
          // 是否禁用可选
          item.isSelectedValueDisabled = !this.changeInfo.api_info;
        });
        // 多层列表数据 关联 table表格数据
        await this.recordChildren(responseTableData);
        // 标记父级元素 方便数据处理
        await this.recordParent(responseTableData);
        // 标记可选 string/boolean/number // 已过滤多重列表
        const canUseArray = await this.showSelectAbled(responseTableData);
        // 根据标记的可选非对象数据 向上逐级寻找可用array父级并标记  生成标记可用数组路径
        await canUseArray.forEach(async (item) => {
          await this.markCanUseArray(item);
        });
        this.responseTableData = await responseTableData;
        // 根据标记可用数组路径 拼接可用数组
        const tempList = this.responseTableData.filter(item => (!item.level && item.key === 'data'));
        this.cascaderData = await this.makeArrayTree(tempList);
        // 派单人组织架构 - tree数据
        this.organization.assignorPerson = this.cascaderData[0] || [];
        // 。。。赋值  。。。
        if (this.changeInfo.api_info && this.changeInfo.api_info.remote_api_id === this.apiDetail.id) {
          // 赋值
          const rspData = await this.changeInfo.api_info.rsp_data.split('.');
          const rspDataList = await rspData.map((item, index) => {
            item = `${index}_${item}`;
            return item;
          });
          const lastObj = `${rspDataList.length}_items_0`;
          rspDataList.push(lastObj);
          const kvKeyAncestorsStr = `${rspDataList.toString()},${rspDataList.length}_${this.changeInfo.kv_relation.key}`;
          const kvNameAncestorsStr = `${rspDataList.toString()},${rspDataList.length}_${this.changeInfo.kv_relation.name}`;
          this.tampFormInfo.ancestorsList_str = rspDataList.toString(); // 记录、标记已选中Array --> tree组件/选取数租
          this.responseTableData.forEach((ite) => {
            // 关键字字段
            if (ite.ancestorsList_str === kvKeyAncestorsStr) {
              ite.isSelectedKey = true;
              this.tampFormInfo.isSelectedKey = ite.ancestorsList_str;
              this.tampFormInfo.settingKeyName = ite.name;
            }
            // 显示字段
            if (ite.ancestorsList_str === kvNameAncestorsStr) {
              ite.isSelectedValue = true;
              this.tampFormInfo.isSelectedValue = ite.ancestorsList_str;
              this.tampFormInfo.settingValueName = ite.name;
            }
          });
          await this.organization.assignorPerson.forEach((tree) => {
            this.treeData(tree, 'assignors');
          });
          // 关键字字段/显示字段 及 相应列表
          this.selectInfo.selectkeylist = this.responseTableData.filter(ite => ite.ancestorsList.join() === rspDataList.join());
          this.selectInfo.selectkey = this.tampFormInfo.isSelectedKey;
          this.selectInfo.selectvaluelist = _.cloneDeep(this.selectInfo.selectkeylist);
          this.selectInfo.selectvalue = this.tampFormInfo.isSelectedValue;
          this.settingValueName = this.tampFormInfo.settingValueName;
          this.settingKeyName = this.tampFormInfo.settingKeyName;
          this.giveFirstCheckInfo(this.selectInfo.selectkeylist, kvKeyAncestorsStr);
          this.giveFirstCheckInfo(this.selectInfo.selectvaluelist, kvNameAncestorsStr);
        }
      },
      giveFirstCheckInfo(list, way) {
        list.forEach((item) => {
          if (item.ancestorsList_str === way) {
            item.checkInfo = true;
          }
          if ((item.has_children && item.children.length) && item.type === 'object') {
            this.giveFirstCheckInfo(item.children, way);
          }
        });
      },
      treeData(tree, type) {
        tree.checkInfo = false;
        tree.has_children = !!(tree.children && tree.children.length);
        tree.showChildren = true;
        // 选中操作角色
        if (String(this.tampFormInfo.ancestorsList_str.split(',').slice(0, -1)
          .toString()) === String(tree.ancestorsList_str) && type === 'assignors') {
          tree.checkInfo = true;
          this.organization.assignorTree = tree;
        }
        if (!tree.has_children) {
          return;
        }
        tree.children.forEach((item) => {
          this.treeData(item, type);
        });
      },
      // 多层列表数据 关联 table表格数据
      recordChildren(tableData, levelInitial) {
        const levelList = tableData.map(item => item.level);
        this.maxLevel = Math.max(...levelList);
        const recordChildrenStep = function (tableData, item) {
          tableData.filter(ite => (ite.level === item.level - 1 && ite.primaryKey === item.parentPrimaryKey && ite.ancestorsList.toString() === item.ancestorsList.slice(0, -1).toString()))[0].children.push(item);
        };
        for (let i = this.maxLevel; i > (levelInitial || 0); i--) {
          tableData.filter(item => item.level === i).forEach((ite) => {
            recordChildrenStep(tableData, ite);
          });
        }
      },
      // 标记父级元素 方便数据处理
      recordParent(tableData, levelInitial) {
        const maxLevelFun = this.maxLevel;
        const recordParentStep = function (tableData, item) {
          // tree.parentInfo = parentInfo
          if (!item.level) {
            item.parentInfo = '';
          } else {
            item.parentInfo = tableData.filter(ite => (ite.level === item.level - 1 && ite.primaryKey === item.parentPrimaryKey && ite.ancestorsList.toString() === item.ancestorsList.slice(0, -1).toString()))[0];
          }
        };
        for (let i = 0; i <= (levelInitial || maxLevelFun); i++) {
          tableData.filter(item => item.level === i).forEach((ite) => {
            recordParentStep(tableData, ite);
          });
        }
      },
      // 根据标记的可选非对象数据 向上逐级寻找可用array父级并标记  生成标记可用数组路径
      markCanUseArray(data) {
        data.isCanUseArray = true;
        if (data.level) {
          this.markCanUseArray(data.parentInfo);
        }
      },
      // 根据标记可用数组路径 拼接可用数组
      makeArrayTree(dataOri) {
        const treeList = [];
        const makeArrayTreeStep = function (treeListOri, data) {
          data.forEach((item) => {
            data.name = item.name;
            data.isSelect = false;
            data.ancestorsList_str = item.ancestorsList_str;
            const { children } = item;
            data.children = [];
            treeListOri.push(data);
            if (children && children.length) {
              makeArrayTreeStep(data.children, children);
            }
          });
        };
        makeArrayTreeStep(treeList, dataOri);
        return treeList;
      },
      changeState(item) {
        item.showChildren = !item.showChildren;
        item.children.forEach((ite) => {
          ite.isShow = item.showChildren;
          // this.$set(ite, 'isShow', item.showChildren)
        });
        if (!item.showChildren) {
          this.closeChildren(item);
        }
      },
      closeChildren(item) {
        item.children.forEach((ite) => {
          ite.isShow = false;
          // this.$set(ite, 'isShow', item.showChildren)
          if (ite.has_children) {
            ite.showChildren = false;
            this.closeChildren(ite);
          }
        });
      },
      changeType() {
        // ...
      },
      // old table选中key
      selectOneKey(itemData) {
        const { isSelectedKey } = itemData;
        this.responseTableData.forEach((item) => {
          item.isSelectedKey = false;
        });
        itemData.isSelectedKey = !isSelectedKey;
        this.responseTableData.filter(item => (item.isSelectAbled)).forEach((item) => {
          item.isSelectedKeyDisabled = false;
          item.isSelectedValueDisabled = item.parentInfo !== itemData.parentInfo;
        });
        this.responseTableData.filter(item => (item.isSelectAbled && item.parentInfo !== itemData.parentInfo)).forEach((item) => {
          item.isSelectedValue = false;
        });
      },
      // old table选中value
      selectOneValue(itemData) {
        const { isSelectedValue } = itemData;
        this.responseTableData.forEach((item) => {
          item.isSelectedValue = false;
        });
        itemData.isSelectedValue = !isSelectedValue;
      },
      // 计算祖先元素有几个是Array
      countArrayAncestors(data) {
        const ids = [];
        const countArrayAncestorsStep = function (item) {
          if (item.parentInfo.type === 'array') {
            ids.push(item.parentInfo);
            countArrayAncestorsStep(item.parentInfo);
          }
          if (item.parentInfo.type === 'object') {
            countArrayAncestorsStep(item.parentInfo);
          }
        };
        countArrayAncestorsStep(data);
        return ids;
      },
      // 标记可选 string/boolean/number
      async showSelectAbled(responseTableData) {
        const canUseArray = [];
        // list结构字段 是否可用
        // 1.祖先元素是否有list结构--1对1--（有则该字段不能用）
        const isArrayList = responseTableData.filter(item => (
          item.type !== 'array' && item.type !== 'object' && item.level && (!item.children || !item.children.length)
          && item.ancestorsList.indexOf('0_data') !== -1
        ));
        const isArrayListUp = isArrayList.filter((item) => {
          const parentArray = this.countArrayAncestors(item);
          const count = parentArray.length;
          const isabled = count === 1 && (item.parentInfo.type === 'array' || item.parentInfo.parentInfo.type === 'array'); // && 后台不支持多层选值
          if (isabled && canUseArray.indexOf(parentArray[0]) === -1) {
            canUseArray.push(parentArray[0]);
          }
          return isabled;
        });
        isArrayListUp.forEach((item) => {
          item.isSelectAbled = true;
        });
        return canUseArray;
      },
      showTree(index) {
        if (!index) {
          const levelList = this.organization.assignorPerson.map(item => item.level);
          this.$set(this.maxLevelTree, 0, Math.max(...levelList) - 1);
        } else {
          const levelList = this.selectInfo.selectkeylist.map(item => item.level);
          this.$set(this.maxLevelTree, 1, Math.max(...levelList) - 1);
          this.$set(this.maxLevelTree, 2, Math.max(...levelList) - 1);
        }
        const temp = this.organizaInfo.assignorShow[index];
        for (let i = 0; i < 3; i++) {
          this.$set(this.organizaInfo.assignorShow, i, false);
        }
        this.$set(this.organizaInfo.assignorShow, index, !temp);
      },
      closeOther0() {
        this.$set(this.organizaInfo.assignorShow, 0, false);
      },
      closeOther1() {
        this.$set(this.organizaInfo.assignorShow, 1, false);
      },
      closeOther2() {
        this.$set(this.organizaInfo.assignorShow, 2, false);
      },
      recordCheckFn(tree) {
        tree.checkInfo = false;
        if (tree.children === null || (tree.children && !tree.children.length)) {
          return;
        }
        tree.children.forEach((item) => {
          this.recordCheckFn(item);
        });
      },
      assignorToggle(value, index) {
        if (value.type === 'object' || (index && value.type === 'array')) {
          return;
        }
        if (!index) {
          this.organization.assignorPerson.forEach((tree) => {
            this.recordCheckFn(tree);
          });
          this.selectInfo.selectkeylist = value.children[0].children;
          this.selectInfo.selectvaluelist = _.cloneDeep(this.selectInfo.selectkeylist);
          // 选中的数据
          this.organization.assignorTree = value;
          this.tampFormInfo.assignors = value.id;
          this.checkInfo.assignors = false;
        } else if (index === 1) {
          this.selectInfo.selectkeylist.forEach((tree) => {
            this.recordCheckFn(tree);
          });
          this.selectInfo.selectkey = value.ancestorsList_str;
          this.settingKeyName = value.name;
          this.responseTableData.forEach((item) => {
            item.isSelectedKey = false;
          });
          this.responseTableData.filter(item => item.ancestorsList_str === value.ancestorsList_str)[0].isSelectedKey = true;
        } else {
          this.selectInfo.selectvaluelist.forEach((tree) => {
            this.recordCheckFn(tree);
          });
          this.selectInfo.selectvalue = value.ancestorsList_str;
          this.settingValueName = value.name;
          this.responseTableData.forEach((item) => {
            item.isSelectedValue = false;
          });
          this.responseTableData.filter(item => item.ancestorsList_str === value.ancestorsList_str)[0].isSelectedValue = true;
        }
        value.checkInfo = true;
        // 关闭窗口
        this.closeTree(index);
      },
      closeTree(index) {
        this.$set(this.organizaInfo.assignorShow, index, false);
      },
      toggleChildren() {
        arguments[0].showChildren = !arguments[0].showChildren;
      },
    },
  };
</script>

<style lang="scss" scoped>
    @import '../../../../../scss/mixins/clearfix.scss';
    @import '../../../../../scss/mixins/scroller.scss';

    .bk-params-title {
        margin-bottom: 0px;
        margin-top: 20px;
        color: #666;
        line-height: 30px;
        font-size: 14px;
    }
    .bk-more {
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

    .bk-param-three {
        display: flex;
        justify-content: space-between;
        align-items: center;

        div.bk-form-item {
            width: 32%;
            margin-top: 0px !important;
            .bk-label {
                color: #424950;
                font-weight: normal;
            }
            .bk-form-content {
                width: 180px;
                margin-left: -200px;
            }
        }

        .bk-tem-cascader {
            position: absolute;
            background: white;
            border: 1px solid #DDE4EB;
            box-shadow: 0px 0px 7px rgba(0, 0, 0, 0.1);
            min-width: 200px;
            height: 100px;
            z-index: 1;
            overflow: auto;
            @include scroller;
        }
    }

    .bk-search-tree {
        position: relative;
        width: 100%;

        .bk-search-tree-wrapper {
            border: 1px solid #c3cdd7;
            width: 100%;
            height: 36px;
            line-height: 34px;
            cursor: pointer;
            color: #c3cdd7;
            position: relative;
            padding: 0 32px 0 10px;
            font-size: 13px;

            &.bk-back-color {
                cursor: not-allowed;
                color: #aaa;
                background: #fafafa;

                &:hover {
                    border-color: #c3cdd7;
                    color: #aaa;
                }

                .bk-color-tree {
                    color: #aaa !important;
                    font-size: 14px;
                }
            }

            &:hover {
                border-color: #0082ff;
                color: #3c96ff;
            }

            .bk-select-angle {
                position: absolute;
                top: 12px;
                right: 10px;
            }
        }

        .bk-border-red {
            border-color: #ff5656;
        }

        .bk-search-tree-content {
            width: 100%;
            min-width: 180px;
            height: 207px;
            position: absolute;
            top: 40px;
            left: 0;
            box-shadow: 0 0 8px 1px rgba(0, 0, 0, 0.1);
            background-color: #fff;
            z-index: 100;
            overflow: auto;
            @include scroller;
            border-radius: 2px;
        }

        .bk-color-tree {
            color: #666 !important;
            font-size: 14px;
        }
    }

    .fade-leave-active, .fade-enter-active {
        transition: all 0.3s ease;
    }

    .fade-leave-active, .fade-enter {
        height: 0px !important;
    }

    .fade-leave, .fade-enter-active {
        height: 207px;
    }
</style>
