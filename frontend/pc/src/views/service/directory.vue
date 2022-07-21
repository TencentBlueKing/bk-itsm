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
  <div class="bk-itsm-service">
    <div class="is-title" :class="{ 'bk-title-left': !sliderStatus }">
      <p class="bk-come-back">
        <span>{{ $t('m.serviceConfig["服务目录"]') }}</span>
      </p>
    </div>
    <div class="itsm-page-content service-directory">
      <div class="bk-directory-tree">
        <tree-info
          :tree-info="treeInfo"
          ref="treeContent">
        </tree-info>
      </div>
      <div class="bk-directory-table">
        <tree-table
          ref="tableContent"
          :tree-info="treeInfo">
        </tree-table>
      </div>
    </div>
  </div>
</template>
<script>
  import treeInfo from './directoryCom/treeInfo.vue';
  import treeTable from './directoryCom/treeTable.vue';

  export default {
    components: {
      treeInfo,
      treeTable,
    },
    data() {
      return {
        // 节点信息
        treeInfo: {
          node: {},
        },
      };
    },
    computed: {
      sliderStatus() {
        return this.$store.state.common.slideStatus;
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../scss/mixins/scroller.scss';
    .service-directory {
        height: calc(100vh - 105px);
        overflow: auto;
    }
    /* 树组件 */
    .bk-directory-tree {
        height: 100%;
        width: 300px;
        float: left;
        border: 1px solid #dde4eb;
        position: relative;
        background-color: #fff;
    }
    /* 表格样式 */
    .bk-directory-table {
        height: 100%;
        width: calc(100% - 300px);
        border: 1px solid #dde4eb;
        border-left: none;
        background-color: #fff;
        float: left;
        overflow: auto;
        @include scroller;
    }
</style>
