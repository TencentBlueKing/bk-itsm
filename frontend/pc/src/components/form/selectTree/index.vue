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
    v-bkloading="{ isLoading: loading }"
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
        <tree
          :tree-data-list="displayList"
          @toggle="toggleInfo"
          @toggleChildren="toggleChildren(...arguments,'view')">
        </tree>
      </div>
    </transition>
  </div>
</template>

<script>
  import Tree from './Tree.vue';
  import { deepClone } from '../../../utils/util.js';
  export default {
    name: 'SelectTree',
    components: {
      Tree,
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
      placeholder: {
        type: String,
        default: '',
      },
      loading: {
        type: Boolean,
        default: false,
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
      value() {
        this.initData();
      },
      loading() {
        this.initData();
      },
    },
    created() {
      this.initData();
    },
    methods: {
      initData() {
        this.displayList = deepClone(this.list);
        if (this.displayList.length) {
          this.displayList.forEach((tree) => {
            this.setCheckedValue(tree);
          });
        }
        if (this.value && this.checked) {
          this.displayList.forEach((tree) => {
            this.openChildren(tree);
          });
        }
        if (this.checked) {
          this.$emit('change', deepClone(this.checked));
        }
      },
      setCheckedValue(tree) {
        this.$set(tree, 'checkInfo', false);
        this.$set(tree, 'has_children', !!(tree.children && tree.children.length));
        if (this.value && String(this.value) === String(tree.id)) {
          tree.checkInfo = true;
          this.checked = tree;
          this.setDispalyName();
          return;
        }
        if (tree.has_children) {
          this.$set(tree, 'showChildren', false);
          tree.children.forEach((item) => {
            this.setCheckedValue(item);
          });
        }
      },
      openChildren(tree) {
        this.$set(tree, 'showChildren', false);
        this.$set(tree, 'showChildren', this.checked.route.some(item => String(item.id) === String(tree.id)));
        if (!(tree.children && tree.children.length)) {
          return;
        }
        tree.children.forEach((item) => {
          this.openChildren(item);
        });
      },
      setDispalyName() {
        let nameList = [];
        if (this.checked.route.length) {
          nameList = this.checked.route.map(item => item.name);
        }
        nameList.push(this.checked.name);
        this.displayName = nameList.join('/');
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
      toggleInfo(tree) {
        this.checked = tree;
        this.setDispalyName();
        this.cancelAllSectedStatus();
        this.$set(tree, 'checkInfo', true);
        this.$emit('selected', tree.id);
        this.$emit('change', deepClone(tree));
        this.closeTree();
      },
      cancelAllSectedStatus(list = this.displayList) {
        list.forEach((tree) => {
          this.$set(tree, 'checkInfo', false);
          if (tree.children && tree.children.length) {
            this.cancelAllSectedStatus(tree.children);
          }
        });
      },
      toggleChildren(item) {
        this.$set(item, 'showChildren', !item.showChildren);
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
</style>
