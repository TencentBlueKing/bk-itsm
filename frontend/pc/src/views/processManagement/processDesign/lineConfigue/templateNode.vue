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
  <div class="bk-template-node">
    <div v-if="node.type === 'START'" class="startpoint">
      {{ $t('m.treeinfo["开始"]') }}
    </div>
    <div v-if="node.type === 'END'" class="endpoint">
      {{ $t('m.treeinfo["结束"]') }}
    </div>
    <!-- 手动节点 -->
    <template v-for="(item, index) in typeList">
      <template v-if="node.type === item.type">
        <div class="common-node" :class="{ 'common-auto': item.type === 'TASK' }" :key="index">
          <span class="common-auto-icon" :class="{ 'bk-is-draft': (node.nodeInfo && node.nodeInfo.is_draft) }">
            <i class="bk-itsm-icon" :class="item.iconStyle" v-if="item.type !== 'TASK'"></i>
            <span v-else style="font-size: 12px; font-weight: bold;">API</span>
          </span>
          <span class="bk-more-word">{{node.name || $t(`m.treeinfo["新增节点"]`)}}</span>
        </div>
      </template>
    </template>
    <!-- 网关节点 -->
    <div v-if="node.type === 'ROUTER-P'" class="common-branch">
      <i class="bk-itsm-icon icon-flow-convergence"></i>
    </div>
    <!-- 汇聚节点 -->
    <div v-if="node.type === 'COVERAGE'" class="common-branch">
      <i class="bk-itsm-icon icon-flow-branch"></i>
    </div>
  </div>
</template>
<script>
  export default {
    name: 'templateNode',
    props: {
      node: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        typeList: [
          { type: 'NORMAL', iconStyle: 'icon-icon-person' },
          { type: 'ROUTER', iconStyle: 'icon-icon-person' },
          { type: 'TASK', iconStyle: 'icon-api-icon' },
          { type: 'TASK-SOPS', iconStyle: 'icon-task-node' },
          { type: 'SIGN', iconStyle: 'icon-sign-node-white' },
          { type: 'APPROVAL', iconStyle: 'icon-approval-node' },
        ],
      };
    },
    methods: {

    },
  };
</script>

<style lang='scss' scoped>
    @import '../jsflowCanvas/jsflowCss/nodeTemplate.scss';
    .bk-template-node {
        float: left;
    }
    .common-node,
    .common-branch {
        cursor: default;
    }
</style>
