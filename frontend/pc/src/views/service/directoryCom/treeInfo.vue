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
  <div class="bk-tree-info" @click="hidden">
    <div class="bk-tree-content" v-bkloading="{ isLoading: isTreeLoading }">
      <div style="overflow: hidden">
        <div class="bk-tree-addService">
          <span>{{ $t(`m['服务目录']`) }}</span>
          <i class="bk-itsm-icon icon-jia-2" @click="openAdd('root')"></i>
        </div>
        <div class="bk-tree-search">
          <bk-input
            class="bk-tree-input"
            data-test-id="directory-input-search"
            :placeholder="$t(`m.serviceConfig['请输入搜索关键字']`)"
            :clearable="true"
            :right-icon="'bk-icon icon-search'"
            v-model="searchWord"
            @enter="searchInfo"
            @clear="clearInfo">
          </bk-input>
        </div>
      </div>
      <div class="bk-tree-div" id="treeOther">
        <div ref="treeTree">
          <tree
            ref="tree5"
            class="bk-tree-class"
            :data="treeList"
            :node-key="'id'"
            :has-border="true"
            @on-click="nodeClick"
            @on-expanded="nodeExpand"
            @on-icon="iconNode"
            @on-drag-node="onDragNode">
          </tree>
          <Empty v-if="fliterArr.length === 0 && searchWord && $refs.tree5.searchFlag" :is-search="!!searchWord" @onClearSearch="clearInfo"></Empty>
        </div>
        <div class="bk-tree-more" ref="treeOperat" v-show="showMore">
          <ul>
            <li
              data-test-id="directoty-li-addCatalogue"
              v-cursor="{ active: !hasPermission(['catalog_create'], $store.state.project.projectAuthActions), zIndex: 3001 }"
              :title="$t(`m.serviceConfig['新增']`)"
              :class="{
                'bk-disabled-add': String(treeInfo.node.level) === '3',
                'text-permission-disable': !hasPermission(['catalog_create'], $store.state.project.projectAuthActions)
              }"
              @click="openAdd">
              <span>{{ $t('m.serviceConfig["新增"]') }}</span>
            </li>
            <li
              data-test-id="directoty-li-editCatalogue"
              v-cursor="{ active: !hasPermission(['catalog_edit'], $store.state.project.projectAuthActions) }"
              :title="$t(`m.serviceConfig['编辑']`)"
              :class="{
                'text-permission-disable': !hasPermission(['catalog_edit'], $store.state.project.projectAuthActions)
              }"
              @click="openUpdate">
              <span>{{ $t('m.serviceConfig["编辑"]') }}</span>
            </li>
            <li
              data-test-id="directoty-li-delCatalogue"
              v-cursor="{ active: !hasPermission(['catalog_delete'], $store.state.project.projectAuthActions) }"
              :title="$t(`m.serviceConfig['删除']`)"
              :class="{
                'text-permission-disable': !hasPermission(['catalog_delete'], $store.state.project.projectAuthActions)
              }"
              @click="openDelete">
              <span>{{ $t('m.serviceConfig["删除"]') }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
    <!-- 新增条目 -->
    <bk-dialog
      width="480"
      :value.sync="addDirectory.show"
      :title="addDirectory.title"
      :mask-close="false"
      :auto-close="false"
      @confirm="submitAdd"
      @cancel="toggleDialog">
      <bk-form
        :label-width="200"
        form-type="vertical"
        :model="addDirectory.formInfo"
        :rules="rules"
        ref="dynamicForm">
        <bk-form-item
          v-if="addDirectory.formInfo.parent__id !== 1"
          :label="$t(`m.serviceConfig['父级目录']`)"
          :required="true">
          <bk-input disabled
            v-model.trim="addDirectory.formInfo.parent___name">
          </bk-input>
        </bk-form-item>
        <bk-form-item
          :label="$t(`m.serviceConfig['目录名称']`)"
          :required="true"
          error-display-type="normal"
          :property="'name'">
          <bk-input v-model.trim="addDirectory.formInfo.name"
            :maxlength="120"
            :show-word-limit="true"
            :placeholder="$t(`m.serviceConfig['请输入目录名称']`)">
          </bk-input>
        </bk-form-item>
        <bk-form-item
          :label="$t(`m.serviceConfig['目录描述']`)">
          <bk-input
            :placeholder="$t(`m.serviceConfig['请输入目录描述']`)"
            :type="'textarea'"
            :rows="3"
            :maxlength="255"
            v-model="addDirectory.formInfo.desc">
          </bk-input>
        </bk-form-item>
      </bk-form>
    </bk-dialog>
  </div>
</template>
<script>
  import tree from './commonTree/tree.vue';
  import commonMix from '../../commonMix/common.js';
  import { errorHandler } from '../../../utils/errorHandler';
  import permission from '@/mixins/permission.js';
  import Empty from '../../../components/common/Empty.vue';

  export default {
    name: 'treeInfo',
    components: {
      tree,
      Empty,
    },
    mixins: [commonMix, permission],
    props: {
      treeInfo: {
        type: Object,
        default() {
          return { node: {} };
        },
      },
    },
    data() {
      return {
        isTreeLoading: false,
        firstStatus: false,
        // 二次点击
        clickSecond: false,
        // 树组件
        searchWord: '',
        treeList: [],
        expandIdList: [],
        // 新增信息
        addDirectory: {
          optType: 'add',
          show: false,
          title: '',
          width: 600,
          formInfo: {
            parent__id: '',
            parent___name: '',
            name: '',
            desc: '',
          },
        },
        // 校验规则
        rules: {},
        parentIds: [],
        fliterArr: [],
      };
    },
    computed: {
      showMore() {
        return this.$store.state.serviceCatalog.treeMore;
      },
    },
    watch: {
      treeList: {
        handler(val) {
          this.fliterArr = [];
          this.filterNodeInfo(val, this.fliterArr);
        },
        deep: true,
      },
    },
    mounted() {
      this.getTreeList();
      this.rules.name = this.checkCommonRules('name').name;
    },
    methods: {
      // 获取树信息
      getTreeList() {
        this.isTreeLoading = true;
        this.$store.dispatch('serviceCatalog/getTreeData', {
          show_deleted: true,
          project_key: this.$store.state.project.id,
        }).then(res => {
          this.treeList = res.data;
          this.getTreeParentId(res.data, this.$route.query.catalog_id);
          if (!this.firstStatus) {
            this.treeInfo.node = this.treeList[0];
          }
          this.treeList.forEach(item => {
            this.recordCheckFn(item);
            if (!this.firstStatus) {
              this.$set(item, 'selected', true);
            }
          });
          this.firstStatus = true;
          if (this.treeInfo.node.id) {
            this.treeList.forEach(item => {
              this.getNodeTree(item);
            });
          }
          if (this.$route.query.catalog_id !== 1) {
            this.treeList[0].selected = false;
          }
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isTreeLoading = false;
          });
      },
      // 获取当前目录id 和parents id
      getTreeParentId(list, id) {
        for (let i = 0; i < list.length; i++) {
          const node = list[i];
          if (node.id === id) {
            node.route.forEach(item => {
              this.parentIds.push(item.id);
            });
          } else {
            if (node.children && node.children.length > 0) {
              this.getTreeParentId(node.children, id);
            }
          }
        }
      },
      // 点击节点方法
      nodeClick(node) {
        this.treeInfo.node = node;
        this.$route.query.catalog_id = node.id;
        this.$store.commit('serviceCatalog/changeTreeOperat', false);
      },
      iconNode(node) {
        this.treeInfo.node = node.node;
        this.$store.commit('serviceCatalog/changeTreeOperat', true);
        const treeOperat = this.$refs.treeOperat;
        if (window.innerHeight - 108 <= node.event.pageY) {
          treeOperat.style.top = `${node.event.pageY - 240}px`;
        } else {
          treeOperat.style.top = `${node.event.pageY - 144}px`;
        }
      },
      hidden(event) {
        const treePanel = this.$refs.treeTree;
        if (treePanel && !treePanel.contains(event.target)) {
          this.$store.commit('serviceCatalog/changeTreeOperat', false);
        }
      },
      // 节点展开收起
      nodeExpand(node, expanded) {
        let expendIndex = -1;
        for (let i = 0; i < this.expandIdList.length; i++) {
          if (node.id === this.expandIdList[i]) {
            expendIndex = i;
          }
        }
        if (expanded) {
          if (expendIndex === -1) {
            this.expandIdList.push(node.id);
          }
        } else {
          if (expendIndex !== -1) {
            this.expandIdList.splice(expendIndex, 1);
          }
        }
      },
      recordCheckFn(tree) {
        this.expandIdList.forEach(selectItem => {
          if (selectItem === tree.id) {
            tree.expanded = true;
          }
        });
        if (this.treeInfo.node.id === tree.id) {
          this.$set(tree, 'selected', true);
        }
        if (tree.children === null || (tree.children && !tree.children.length)) {
          return;
        }
        tree.children.forEach(item => {
          this.recordCheckFn(item);
        });
      },
      getNodeTree(tree) {
        if (this.parentIds.includes(tree.id)) {
          this.$set(tree, 'expanded', true);
        }
        if (this.$route.query.catalog_id === tree.id && tree.id !== 1) {
          this.$set(tree, 'expanded', true);
          this.$set(tree, 'selected', true);
        }
        if (tree.children === null || (tree.children && !tree.children.length)) {
          return;
        }
        tree.children.forEach(item => {
          if (item.parent_id === tree.id && this.$route.query.catalog_id === item.id) {
            this.$set(tree, 'expanded', true);
          }
          this.getNodeTree(item);
        });
      },
      // 搜索
      searchInfo() {
        this.$refs.tree5.searchNode(this.searchWord);
      },
      clearInfo() {
        this.searchWord = '';
        this.$refs.tree5.searchNode(this.searchWord);
      },
      filterNodeInfo(data, arr) {
        data.forEach(item => {
          if (item.searched) {
            arr.push(item);
          } else {
            this.filterNodeInfo(item.children, arr);
          }
        });
      },
      // 新增目录
      openAdd() {
        if (!this.hasPermission(['catalog_create'], this.$store.state.project.projectAuthActions)) {
          const projectInfo = this.$store.state.project.projectInfo;
          const resourceData = {
            project: [{
              id: projectInfo.key,
              name: projectInfo.name,
            }],
          };
          this.applyForPermission(['catalog_create'], this.$store.state.project.projectAuthActions, resourceData);
          return;
        }
        if (String(this.treeInfo.node.level) === '3') {
          return;
        }
        if (!this.treeInfo.node.id) {
          this.$bkMessage({
            message: this.$t('m.serviceConfig["请选择父级目录再进行新增"]'),
            theme: 'warning',
          });
          return;
        }
        this.toggleDialog('add');
        this.addDirectory.optType = 'add';
        this.addDirectory.formInfo = {
          parent__id: this.treeInfo.node.id,
          parent___name: this.treeInfo.node.name,
          name: '',
          desc: '',
        };
      },
      toggleDialog(optType) {
        if (optType === 'add') {
          this.addDirectory.title = this.$t('m.serviceConfig["新增服务目录"]');
        } else if (optType === 'update') {
          this.addDirectory.title = this.$t('m.serviceConfig["编辑服务目录"]');
        }
        this.addDirectory.show = !this.addDirectory.show;
        this.$refs.dynamicForm.clearError();
      },
      submitAdd() {
        this.$refs.dynamicForm.validate().then(() => {
          const params = this.addDirectory.formInfo;
          params.project_key = this.$store.state.project.id;
          if (this.clickSecond) {
            return;
          }
          this.clickSecond = true;
          if (this.addDirectory.optType === 'add') {
            this.$store.dispatch('serviceCatalog/create', params).then(() => {
              this.$bkMessage({
                message: this.$t('m.serviceConfig["新增目录成功"]'),
                theme: 'success',
              });
              // TODO 局部刷新
              this.getTreeList();
              this.toggleDialog();
              // 确认保存后清空节点数据
            })
              .catch(res => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.clickSecond = false;
              });
          } else if (this.addDirectory.optType === 'update') {
            if (this.addDirectory.formInfo.parent__id === '') {
              delete this.addDirectory.formInfo.parent__id;
            }

            this.$store.dispatch('serviceCatalog/update', params).then(() => {
              this.$bkMessage({
                message: this.$t('m.serviceConfig["更新目录成功"]'),
                theme: 'success',
              });
              // TODO 局部刷新
              this.getTreeList();
              this.toggleDialog();
              // 确认保存后清空节点数据
              // this.treeInfo.node = {}
            })
              .catch(res => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.clickSecond = false;
              });
          }
        }, () => {

        });
      },
      // 编辑目录
      openUpdate() {
        if (!this.hasPermission(['catalog_edit'], this.$store.state.project.projectAuthActions)) {
          const projectInfo = this.$store.state.project.projectInfo;
          const resourceData = {
            project: [{
              id: projectInfo.key,
              name: projectInfo.name,
            }],
          };
          this.applyForPermission(['catalog_edit'], this.$store.state.project.projectAuthActions, resourceData);
          return;
        }
        if (!this.treeInfo.node.id) {
          this.$bkMessage({
            message: this.$t('m.serviceConfig["请选择需要编辑的目录"]'),
            theme: 'warning',
          });
          return;
        }
        this.addDirectory.optType = 'update';
        this.addDirectory.formInfo = {
          parent__id: this.treeInfo.node.parent_id,
          parent___name: this.treeInfo.node.parent_name,
          id: this.treeInfo.node.id,
          name: this.treeInfo.node.name,
          desc: this.treeInfo.node.desc,
        };

        this.toggleDialog('update');
      },
      // 删除
      openDelete() {
        if (!this.hasPermission(['catalog_delete'], this.$store.state.project.projectAuthActions)) {
          const projectInfo = this.$store.state.project.projectInfo;
          const resourceData = {
            project: [{
              id: projectInfo.key,
              name: projectInfo.name,
            }],
          };
          this.applyForPermission(['catalog_delete'], this.$store.state.project.projectAuthActions, resourceData);
          return;
        }
        if (!this.treeInfo.node.id) {
          this.$bkMessage({
            message: this.$t('m.serviceConfig["请选择要删除的目录"]'),
            theme: 'warning',
          });
          return;
        }
        if (this.treeInfo.node.children && this.treeInfo.node.children.length) {
          this.$bkMessage({
            message: this.$t('m.serviceConfig["请先删除子目录"]'),
            theme: 'warning',
          });
          return;
        }
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.serviceConfig["确认删除此服务目录？"]'),
          subTitle: this.$t('m.serviceConfig["服务目录一旦删除，此服务目录将不可用，请谨慎操作。"]'),
          confirmFn: () => {
            if (this.clickSecond) {
              return;
            }
            this.clickSecond = true;
            this.$store.dispatch('serviceCatalog/delete', this.treeInfo.node.id).then(() => {
              this.$bkMessage({
                message: this.$t('m.serviceConfig["删除目录成功"]'),
                theme: 'success',
              });
              this.getTreeList();
              this.firstStatus = false;
            })
              .catch(res => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.clickSecond = false;
              });
          },
        });
      },
      onDragNode() {
        if (arguments[0].currentParent.children.length <= 1) {
          return;
        }
        if (this.clickSecond) {
          return;
        }
        this.clickSecond = true;
        const params = {
          new_order: arguments[0].currentParent.children.map(item => item.id),
        };
        const id = arguments[0].dragNode.id;
        this.$store.dispatch('serviceCatalog/moveNode', { params, id }).then(() => {
          // ...
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.clickSecond = false;
          });
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../scss/mixins/clearfix.scss';
    @import '../../../scss/mixins/scroller.scss';

    .bk-tree-info {
        // overflow: hidden;
        height: 100%;
        .bk-tree-div {
            height: calc(100% - 56px);
            width: 100%;
            overflow: auto;
            @include scroller;
        }
    }
    .bk-tree-content {
        height: 100%;
        padding: 0px 16px;
        @include scroller;
        @include clearfix;
        .bk-tree-search {
            margin-bottom: 20px;
        }
        .bk-tree-class {
            color: #737987;
        }
        .bk-tree-addService {
            height: 20px;
            margin: 14px 0;
            line-height: 20px;
            font-size: 12px;
            color: #979ba5;
            span {
                float: left;
            }
            i {
                margin: 5px 5px 2px 2px;
                float: right;
                font-size: 12px;
                cursor: pointer;
            }
        }
    }

    .bk-tree-btn {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        border-top: 1px solid #dde4eb;
        padding: 20px;
        text-align: right;
        background-color: #fff;
    }

    .bk-tree-more {
        position: absolute;
        top: 0;
        right: -70px;
        width: 79px;
        height: 108px;
        background: #fff;
        box-shadow: 0px 2px 2px 2px rgba(227,225,225,0.5);
        border-radius: 2px;
        z-index: 3000;
        ul {
            width: 100%;
            height: 100%;
            li {
                width: 100%;
                height: 36px;
                line-height: 36px;
                color: #63656E;
                text-align: center;
                cursor: pointer;
                font-size: 14px;
                &:hover {
                    background: rgba(163,197,253,0.2);
                    color: #3A84FF;
                }
            }
            .bk-disabled-add {
                background-color: #fafafa !important;
                border-color: #e6e6e6 !important;
                color: #cccccc !important;
                cursor: not-allowed !important;
            }
        }
    }
</style>
