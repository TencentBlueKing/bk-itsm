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
  <div v-if="item.showFeild">
    <bk-form-item :label="item.name" :required="item.validate_type === 'REQUIRE'" :desc="item.tips" desc-type="icon">
      <div class="bk-search-tree bk-form-width"
        :class="{ 'bk-border-error': item.checkValue }"
        v-bk-clickoutside="closeTree">
        <div class="bk-search-tree-wrapper"
          :class="{ 'bkdisabled': disabled }"
          @click.stop="showTree">
          <span :class="{ 'bk-color-tree': treeSlectInfo.info.name }">
            {{treeSlectInfo.info.showName || $t(`m.newCommon["请选择"]`)}}
          </span>
          <i class="bk-select-angle bk-icon icon-framework"></i>
        </div>
        <transition name="common-fade">
          <template v-if="treeSlectInfo.show">
            <div class="bk-search-tree-content" v-if="treeSlectInfo.treeDataList.length">
              <export-tree
                :tree-data-list="treeSlectInfo.treeDataList"
                @toggle="toggleInfo"
                @toggleChildren="toggleChildren">
              </export-tree>
            </div>
            <div class="bk-search-tree-content" v-else>
              <p class="bk-search-tree-nodata">{{ $t('m.treeinfo["暂无数据"]') }}</p>
            </div>
          </template>
        </transition>
      </div>
    </bk-form-item>
    <template v-if="item.checkValue">
      <p class="bk-task-error" v-if="item.checkMessage">{{ item.checkMessage }}</p>
      <p class="bk-task-error" v-else>{{ item.name }}{{$t('m.newCommon["为必填项！"]')}}</p>
    </template>
  </div>
</template>

<script>
  import exportTree from '../treeInfo/exportTree.vue';
  import mixins from '../../commonMix/field.js';
  import { errorHandler } from '../../../utils/errorHandler';

  export default {
    name: 'TREESELECT',
    components: {
      exportTree,
    },
    mixins: [mixins],
    props: {
      item: {
        type: Object,
        required: true,
        default: () => {},
      },
      fields: {
        type: Array,
        required: true,
        default: () => [],
      },
      isCurrent: {
        type: Boolean,
        default: false,
      },
      disabled: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        options: [],
        treeSlectInfo: {
          show: false,
          treeDataList: [],
          info: {},
        },
      };
    },
    computed: {

    },
    watch: {
      'item.val'() {
        this.treeSlectInfo.treeDataList.forEach((tree) => {
          this.treeData(tree);
        });
        this.conditionField(this.item, this.fields);
      },
    },
    async mounted() {
      this.$nextTick(() => {
        this.getTreeInfo();
        this.conditionField(this.item, this.fields);
      });
    },
    methods: {
      getTreeInfo() {
        // const params = {
        //     key: this.item.source_uri,
        //     view_type: 'tree'
        // }
        let params = {};
        let url = '';
        if (this.item.source_type === 'RPC') {
          url = 'apiRemote/getRpcData';
          params = {
            source_uri: this.item.source_uri,
          };
        } else if (this.item.source_type === 'DATADICT') {
          url = 'dictdata/getTreeInfo';
          params = {
            key: this.item.source_uri,
            view_type: 'tree',
          };
        }
        this.$store.dispatch(url, params).then((res) => {
          this.treeSlectInfo.treeDataList = res.data;
          this.item.choice = res.data;
          this.treeSlectInfo.treeDataList.forEach((tree) => {
            this.treeData(tree);
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      showTree() {
        if (this.disabled) return;
        this.item.checkValue = false;
        this.treeSlectInfo.show = !this.treeSlectInfo.show;
        let valueIndex = '';
        this.fields.forEach((node, index) => {
          if (node.id === this.item.id) {
            valueIndex = index;
          }
        });
        if (valueIndex === this.fields.length - 1) {
          if (document.getElementById('bkPreview')) {
            setTimeout(() => {
              document.getElementById('bkPreview').scrollTop += 100;
            }, 100);
          }
        }
      },
      closeTree() {
        this.treeSlectInfo.show = false;
      },
      toggleInfo(value) {
        this.treeSlectInfo.treeDataList.forEach((tree) => {
          this.recordCheckFn(tree);
        });
        value.checkInfo = true;
        this.treeSlectInfo.treeDataList = JSON.parse(JSON.stringify(this.treeSlectInfo.treeDataList));
        // 选中的数据
        this.treeSlectInfo.info = value;
        this.item.val = this.treeSlectInfo.info.id;
        // 关闭窗口
        this.closeTree();
      },
      treeData(tree) {
        tree.showChildren = false;
        tree.checkInfo = false;
        tree.has_children = !!tree.children.length;
        if (String(this.item.val) === String(tree.id)) {
          tree.checkInfo = true;
          this.treeSlectInfo.info = tree;
          const nameList = [];
          if (this.treeSlectInfo.info.route && this.treeSlectInfo.info.route.length) {
            this.treeSlectInfo.info.route.forEach((node) => {
              nameList.push(node.name);
            });
          }
          nameList.push(this.treeSlectInfo.info.name);
          this.treeSlectInfo.info.showName = nameList.join(' / ');
        }
        if (!tree.has_children || !tree.children.length) {
          return;
        }
        tree.children.forEach((item) => {
          if (item.parent_id === tree.id) {
            tree.showChildren = true;
          }
          this.treeData(item);
        });
      },
      recordCheckFn(tree) {
        tree.checkInfo = false;
        if (!tree.children || !tree.children.length) {
          return;
        }
        tree.children.forEach((item) => {
          this.recordCheckFn(item);
        });
      },
      toggleChildren(item) {
        item.showChildren = !item.showChildren;
        this.treeSlectInfo.treeDataList = JSON.parse(JSON.stringify(this.treeSlectInfo.treeDataList));
      },
    },
  };
</script>

<style lang="scss" scoped>
    .bk-search-tree-nodata{
        text-align: center;
        line-height: 42px;
        color: #737987;
    }
</style>
