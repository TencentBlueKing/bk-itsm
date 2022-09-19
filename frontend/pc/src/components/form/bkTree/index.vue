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
  <div
    v-bk-clickoutside="closeTree"
    class="bk-search-tree"
    :class="extCls">
    <div
      class="bk-search-tree-wrapper"
      @click.stop="showTree('view')">
      <span :class="{ 'bk-color-tree': displayName }">
        {{ displayName || $t(`m.serviceConfig["请选择"]`)}}
      </span>
      <i v-if="organizationLoading" class="bk-select-angle bk-itsm-icon icon-icon-loading"></i>
    </div>
    <transition name="common-fade">
      <div class="bk-search-tree-content" v-show="isShowTree">
        <bk-tree
          ref="tree1"
          :ext-cls="'bk-tree'"
          :data="displayList"
          :node-key="'id'"
          :show-icon="false"
          :has-border="false"
          @on-click="nodeClickOne"
          @async-load-nodes="asyncLoadNodes">
        </bk-tree>
      </div>
    </transition>
  </div>
</template>

<script>
  import { deepClone } from '../../../utils/util.js';
  export default {
    name: 'SelectTree',
    components: {
    },
    model: {
      prop: 'value',
      event: 'selected',
    },
    props: {
      list: {
        type: Array,
        default: () => ([]),
      },
      value: {
        type: [Number, String, Array],
        default: '',
      },
      extCls: {
        type: String,
        default: '',
      },
      organizationLoading: Boolean,
    },
    data() {
      return {
        isShowTree: false,
        displayName: '',
        displayList: [],
        checked: null,
      };
    },
    watch: {
      list() {
        this.initData();
      },
      // value() {
      //   this.initData();
      // },
      // loading() {
      //   this.initData();
      // },
      isShowTree(val) {
        if (val) {
          this.setTreeNodeTitle();
        }
      },
    },
    created() {
      this.initData();
    },
    methods: {
      nodeClickOne(node) {
        this.checked = node;
        this.$emit('toggle', node);
        this.$emit('selected', node.id);
        this.setDispalyName();
        this.closeTree();
      },
      asyncLoadNodes(node) {
        this.$set(node, 'loading', true);
        this.$store.dispatch('cdeploy/getTreeInfoChildren', { id: node.id }).then((res) => {
          res.data.children.forEach(ite => {
            this.setCheckedValue(ite);
          });
          this.$set(node, 'children', res.data.children || []);
        });
        this.setTreeNodeTitle();
        this.$set(node, 'loading', false);
      },
      setDispalyName() {
        this.displayName = this.checked.full_name;
      },
      setTreeNodeTitle() {
        this.$nextTick(() => {
          const list = document.querySelectorAll('.tree-node');
          list.forEach(dom => {
            dom.title = dom.innerText;
          });
        });
      },
      setinitValue(id) {
        this.$store.dispatch('cdeploy/getTreeInfoChildren', { id }).then((res) => {
          this.checked = res.data;
          this.setDispalyName();
        });
      },
      initData() {
        this.displayList = deepClone(this.list);
        if (this.displayList.length) {
          this.displayList.forEach((tree) => {
            this.setCheckedValue(tree);
          });
        }
        if (this.value && this.value.length !== 0) {
          this.setinitValue(Number(this.value));
        }
        if (this.checked) {
          this.$emit('change', deepClone(this.checked));
        }
      },
      setCheckedValue(tree) {
        this.$set(tree, 'expanded', false);
        this.$set(tree, 'async', tree.has_children);
      },
      showTree() {
        if (this.loading) {
          return;
        }
        this.isShowTree = true;
      },
      closeTree() {
        this.isShowTree = false;
      },
    },
  };
</script>

<style lang="scss" scoped>
/* 图片动画 */
@keyframes rotation {
    from {
        -webkit-transform: rotate(0deg);
    }
    to {
        -webkit-transform: rotate(360deg);
    }
}
@-webkit-keyframes rotation {
    from {
        -webkit-transform: rotate(0deg);
    }
    to {
        -webkit-transform: rotate(360deg);
    }
}
.bk-search-tree {
    background: #ffffff;
    .bk-color-tree {
        display: block;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .bk-select-angle {
        margin-top: -4px;
        font-size: 16px;
        display: inline-block;
        -webkit-transform: rotate(360deg);
        animation: rotation 1.5s linear infinite;
        -moz-animation: rotation 1.5s linear infinite;
        -webkit-animation: rotation 1.5s linear infinite;
        -o-animation: rotation 1.5s linear infinite;
    }
}
.bk-search-tree-content {
    height: 170px;
}
.bk-tree {
  background-color: #fff;
  padding: 5px 10px;
  color: #63656e;
  // .single {
  //   /deep/ .tree-drag-node {
  //     &:hover {
  //       background-color: #cfe8fc;
  //     }
  //   }
  // }
}
.bk-tree /deep/ .tree-drag-node {
  display: flex;
  align-items: center;
  .tree-node {
    flex: 1;
    overflow: hidden;
    .node-title {
      width: 100%;
    }
  }
  &:hover {
    background-color: #cfe8fc;
  }
}
</style>
