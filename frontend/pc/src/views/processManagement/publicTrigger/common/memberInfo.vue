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
  <div class="member-content">
    <bk-select :class="{ 'member-select': true, 'half-member-select': recipientItem.key }"
      v-model="recipientItem.key"
      searchable
      @selected="getSecondLevelList">
      <bk-option v-for="option in recipientKeyList"
        :key="option.typeName"
        :id="option.typeName"
        :name="option.name">
      </bk-option>
    </bk-select>
    <!-- 二级处理人 -->
    <template v-if="recipientItem.key !== 'ORGANIZATION'">
      <template v-if="recipientItem.key === 'VARIABLE'">
        <bk-select v-model="recipientItem.value"
          style="float: left; width: 50%; margin-right: 6px;"
          searchable>
          <bk-option v-for="option in variableList"
            :key="option.key"
            :id="option.key"
            :name="option.name">
          </bk-option>
        </bk-select>
      </template>
      <template v-else-if="recipientItem.key === 'PERSON' && Array.isArray(recipientItem.value)">
        <member-select style="float: left; width: 50%; margin-right: 6px;"
          v-model="recipientItem.value">
        </member-select>
      </template>
      <template v-else-if="(recipientItem.key === 'GENERAL' || recipientItem.key === 'CMDB') && Array.isArray(recipientItem.value)">
        <bk-select style="float: left; width: 50%; margin-right: 6px;"
          v-model="recipientItem.value"
          :loading="recipientItem.isLoading"
          show-select-all
          multiple
          searchable>
          <bk-option v-for="option in recipientItem.secondLevelList"
            :key="option.id"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
      </template>
    </template>
    <!-- 组织架构 -->
    <template v-if="recipientItem.key === 'ORGANIZATION'">
      <div class="bk-search-tree"
        style="float: left; width: 50%; margin-right: 6px;"
        v-bk-clickoutside="closeTree">
        <div class="bk-search-tree-wrapper" @click.stop="showTree('view')">
          <span :class="{ 'bk-color-tree': roles.viewtree.name }">
            {{roles.viewtree.showName || $t(`m.serviceConfig["请选择"]`)}}
          </span>
          <i class="bk-select-angle bk-icon icon-framework"></i>
        </div>
        <transition name="common-fade">
          <div class="bk-search-tree-content" v-if="roles.viewTreeOpen">
            <export-tree
              :tree-data-list="roles.viewTreeDataList"
              @toggle="toggleInfo"
              @toggleChildren="toggleChildren(...arguments,'view')">
            </export-tree>
          </div>
        </transition>
      </div>
    </template>
    <div class="bk-between-operat" v-if="itemInfo.type === 'MULTI_MEMBERS'">
      <i class="bk-itsm-icon icon-flow-add" @click="addRecipient"></i>
      <i class="bk-itsm-icon icon-flow-reduce"
        :class="{ 'bk-no-delete': itemInfo.value.length === 1 }"
        @click="deleteRecipient"></i>
    </div>
  </div>
</template>
<script>
  import memberSelect from '../../../commonComponent/memberSelect';
  import exportTree from '../../../commonComponent/treeInfo/exportTree.vue';
  import { mapState } from 'vuex';
  import { errorHandler } from '../../../../utils/errorHandler';

  export default {
    name: 'changeConductor',
    components: {
      memberSelect,
      exportTree,
    },
    props: {
      itemInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      recipientItem: {
        type: Object,
        default() {
          return {};
        },
      },
      recipientIndex: {
        type: Number,
        default() {
          return '';
        },
      },
    },
    data() {
      return {
        recipientKeyList: [],
        roles: {
          viewTreeDataList: [],
          viewtree: {},
          viewTreeOpen: false,
        },
        variableList: [],
      };
    },
    computed: {
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
      // 处理人去掉（不限，提单人，派单人指定，无）
      const filterList = ['OPEN', 'STARTER', 'BY_ASSIGNOR', 'EMPTY'];
      this.recipientKeyList = this.globalChoise.processor_type.filter(item => !filterList.some(filterName => filterName === item.typeName));
      // 如果一级字段存在值，则调用二级字段列表
      if (this.recipientItem.key) {
        this.recipientItem.secondLevelList = [];
        if (this.recipientItem.key === 'ORGANIZATION') {
          this.getOrganization();
          if (this.recipientItem.value) {
            this.setinitValue(Number(this.recipientItem.value));
          }
        } else if (this.recipientItem.key === 'VARIABLE') {
          this.recipientItem.value = this.recipientItem.value;
        } else if (this.recipientItem.key === 'PERSON') {
          this.recipientItem.secondLevelList = [];
          this.recipientItem.value = Array.isArray(this.recipientItem.value) ? this.recipientItem.value : this.recipientItem.value.split(',');
        } else {
          this.recipientItem.value = Array.isArray(this.recipientItem.value) ? this.recipientItem.value : this.recipientItem.value.split(',');
          this.secondListFn(this.recipientItem);
        }
      }
    },
    mounted() {
      this.variableList = this.triggerVariables;
    },
    methods: {
      setinitValue(id) {
        this.$store.dispatch('cdeploy/getTreeInfoChildren', { id }).then((res) => {
          this.roles.viewtree = res.data;
          this.concatName();
        });
      },
      getSecondLevelList() {
        // 清空二级数据
        this.recipientItem.value = [];
        this.recipientItem.secondLevelList = [];
        if (this.recipientItem.key === 'ORGANIZATION') {
          this.recipientItem.value = '';
          this.getOrganization();
        } else if (this.recipientItem.key === 'VARIABLE') {
          this.recipientItem.value = '';
        } else if (this.recipientItem.key === 'PERSON') {
          this.recipientItem.secondLevelList = [];
        } else {
          this.secondListFn(this.recipientItem);
        }
      },
      // 获取数据
      secondListFn(recipientItem) {
        if (!recipientItem.key) {
          return;
        }
        recipientItem.isLoading = true;
        this.$store.dispatch('deployCommon/getSecondUser', {
          role_type: recipientItem.key,
          project_key: this.$store.state.project.id,
        }).then((res) => {
          const valueList = res.data;
          const userList = [];
          if (recipientItem.key === 'GENERAL') {
            valueList.forEach((item) => {
              userList.push({
                id: String(item.id),
                name: `${item.name}(${item.count})`,
                disabled: (item.count === 0),
              });
            });
          } else {
            valueList.forEach((item) => {
              userList.push({
                id: String(item.id),
                name: item.name,
              });
            });
          }
          recipientItem.secondLevelList = userList;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            recipientItem.isLoading = false;
          });
      },
      // 组织架构
      getOrganization() {
        this.$store.dispatch('cdeploy/getTreeInfo').then((res) => {
          // 操作角色组织架构
          this.roles.viewTreeDataList = res.data;
          this.roles.viewTreeDataList.forEach((tree) => {
            this.setCheckedValue(tree, 'view');
          });
        })
          .catch(() => {

          });
      },
      // 清除不符合value id的选中状态
      recordCheckFn(list = this.roles.viewTreeDataList) {
        list.forEach((tree) => {
          this.$set(tree, 'checkInfo', false);
          if (tree.children && tree.children.length) {
            this.recordCheckFn(tree.children);
          }
        });
      },
      toggleInfo(value) {
        this.recordCheckFn();
        value.checkInfo = true;
        // 选中的数据
        this.roles.viewtree = value;
        this.concatName();
        this.recipientItem.value = value.id;
        // 关闭窗口
        this.closeTree();
      },
      toggleChildren(item, type) {
        if (type === 'view') {
          this.$set(item, 'showChildren', !item.showChildren);
          this.$store.dispatch('cdeploy/getTreeInfoChildren', { id: item.id }).then((res) => {
            res.data.children.forEach(tree => {
              this.setCheckedValue(tree, 'view');
            });
            this.$set(item, 'children', res.data.children || []);
          });
        }
      },
      openChildren(tree, type) {
        tree.showChildren = false;
        if (type === 'view') {
          tree.showChildren = this.roles.viewtree.route.some(item => String(item.id) === String(tree.id));
        }
        if (!(tree.children && tree.children.length)) {
          return;
        }
        tree.children.forEach((item) => {
          this.openChildren(item, type);
        });
      },
      setCheckedValue(tree, type) {
        this.$set(tree, 'checkInfo', false);
        this.$set(tree, 'has_children', tree.has_children);
        if (String(this.recipientItem.value) === String(tree.id) && type === 'view') {
          tree.checkInfo = true;
          this.checked = tree;
          this.concatName();
          return;
        }
        if (tree.has_children) {
          this.$set(tree, 'showChildren', false);
          this.$set(tree, 'children', []);
        }
      },
      showTree(type) {
        if (type === 'view') {
          this.roles.viewTreeOpen = !this.roles.viewTreeOpen;
          this.roles.otherTreeOpen = false;
        }
      },
      closeTree() {
        this.roles.viewTreeOpen = false;
      },
      concatName() {
        this.$set(this.roles.viewtree, 'showName', this.roles.viewtree.full_name);
      },
      addRecipient() {
        this.itemInfo.value.splice(this.recipientIndex + 1, 0, {
          type: '',
          value: '',
          secondLevelList: [],
          isLoading: false,
        });
      },
      deleteRecipient() {
        if (this.itemInfo.value.length === 1) {
          return;
        }
        this.itemInfo.value.splice(this.recipientIndex, 1);
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../../scss/mixins/clearfix.scss';
    .member-content{
        width: 100%;
        height: 32px;
        display: flex;
        flex-wrap: nowrap;
    }
    .member-select{
        float: left;
        width: 100%;
        margin-right: 6px;
    }
    .half-member-select{
        width: 50%;
    }
    .bk-between-operat {
        width: 140px;
        line-height: 32px;
        font-size: 18px;
        margin-left: 10px;
        .bk-itsm-icon {
            color: #C4C6CC;
            margin-right: 9px;
            cursor: pointer;
            &:hover {
                color: #979BA5;
            }
        }
        .bk-no-delete {
            color: #DCDEE5;
            cursor: not-allowed;
            &:hover {
                color: #DCDEE5;
            }
        }
    }
</style>
