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
    class="bk-flow-location"
    :class="{ 'bk-error-flow': (node.nodeInfo && node.nodeInfo.errorInfo) }"
    @mousedown="moveDoneFn(node)"
    @mousemove="moveFn"
    @mouseup="onNodeClick(node, $event)"
    @contextmenu.prevent="rightClickNode(node, $event)"
    @click="clickNode(node, $event)"
    @mouseout="hoverNode(node)"
    v-bk-clickoutside="closeNode">
    <div v-if="node.type === 'START'" class="startpoint" data-test-id="start">
      {{ $t(`m.treeinfo['开始']`) }}
    </div>
    <div v-if="node.type === 'END'" class="endpoint">
      {{ $t('m.treeinfo["结束"]') }}
    </div>
    <!-- 手动节点 -->
    <template v-for="(item, index) in typeList">
      <template v-if="node.type === item.type">
        <div class="common-node" :key="index">
          <span class="common-auto-icon"
            :class="{ 'bk-is-draft': (node.nodeInfo && node.nodeInfo.is_draft) }"
            @click.stop="openconfigu">
            <i class="bk-itsm-icon" :class="item.iconStyle" v-if="item.type !== 'TASK'"></i>
            <span v-else style="font-size: 11px; font-weight: bold;">API</span>
          </span>
          <span class="bk-more-word" :title="(node.name || $t(`m.treeinfo['新增节点']`))">{{node.name || $t(`m.treeinfo['新增节点']`)}}</span>
          <span class="bk-node-delete"
            v-if="!(node.nodeInfo && node.nodeInfo.is_builtin)"
            @click.stop="clickDelete(node)"
            @mouseup.stop
            @mousedown.stop>×</span>
          <div class="bk-toop-info" v-if="!toolStatus && (node.nodeInfo && node.nodeInfo.is_builtin)">
            <p><span>{{$t(`m.treeinfo['单击：']`)}}</span>{{$t(`m.treeinfo['快速配置节点']`)}}</p>
            <p><span>{{$t(`m.treeinfo['右键：']`)}}</span>{{$t(`m.treeinfo['调出快速添加节点菜单']`)}}</p>
            <i class="bk-icon icon-close" @click.stop="closeTool"></i>
            <i class="bk-squrae"></i>
          </div>
        </div>
      </template>
    </template>
    <!-- 网关节点 -->
    <div v-if="node.type === 'ROUTER-P'" class="common-branch">
      <i class="bk-itsm-icon icon-flow-convergence"></i>
      <span class="bk-node-delete" @click.stop="clickDelete(node)">×</span>
    </div>
    <!-- 汇聚节点 -->
    <div v-if="node.type === 'COVERAGE'" class="common-branch">
      <i class="bk-itsm-icon icon-flow-branch"></i>
      <span class="bk-node-delete" @click.stop="clickDelete(node)">×</span>
    </div>
    <!-- 更多操作 -->
    <div class="bk-flow-fast" v-show="node.showMore && node.type !== 'START' && node.type !== 'END'">
      <div class="bk-engine-node">
        <ul>
          <li v-for="(item, index) in clickList"
            class="tool"
            :key="index"
            @click.stop="addNormal(node, item)" :title="item.name">
            <i class="bk-itsm-icon"
              :class="[
                item.iconStyle,
                { 'bk-font-style': [
                  'icon-icon-artificial',
                  'icon-api-node',
                  'icon-task-icon',
                  'con-copy-new',
                  'icon-sign-node',
                  'icon-approval-node'
                ].includes(item.iconStyle) }
              ]">
            </i>
          </li>
        </ul>
      </div>
      <div class="bk-engine-word">
        <span class="bk-canvas-span bk-engine-configur"
          :class="{ 'bk-engine-builtin': (node.type === 'ROUTER-P' || node.type === 'COVERAGE') }"
          @click.stop="openconfigu">{{ $t('m.treeinfo["配置"]') }}</span>
        <span class="bk-canvas-span bk-engine-delete"
          :class="{ 'bk-engine-builtin': (node.nodeInfo && node.nodeInfo.is_builtin) }"
          @click.stop="clickDelete(node)">{{ $t('m.treeinfo["删除"]') }}</span>
      </div>
    </div>
  </div>
</template>
<script>
  import { deepClone } from '@/utils/util.js';
  import { errorHandler } from '../../../../utils/errorHandler';
  export default {
    name: 'NodeTemplate',
    props: {
      node: {
        type: Object,
        default() {
          return {};
        },
      },
      canvasData: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        moveFlag: false,
        clickSecond: false,
        toolStatus: false,
        valueInfo: {
          node: {},
          line: {},
        },
        typeList: [
          { type: 'NORMAL', iconStyle: 'icon-icon-person' },
          { type: 'ROUTER', iconStyle: 'icon-icon-person' },
          { type: 'TASK', iconStyle: 'icon-api-icon' },
          { type: 'TASK-SOPS', iconStyle: 'icon-task-node' },
          { type: 'APPROVAL', iconStyle: 'icon-approval-node' },
          { type: 'WEBHOOK', iconStyle: 'icon-icon-webhook-2' },
          { type: 'SIGN', iconStyle: 'icon-sign-node-white f18' },
        ],
        clickList: [
          { type: 'NORMAL', name: this.$t('m.treeinfo["手动节点"]'), iconStyle: 'icon-icon-artificial' },
          { type: 'TASK', name: this.$t('m.treeinfo["API节点"]'), iconStyle: 'icon-api-node' },
          { type: 'TASK-SOPS', name: this.$t('m.treeinfo["标准运维节点"]'), iconStyle: 'icon-task-icon' },
          { type: 'SIGN', name: this.$t('m.treeinfo[\'会签节点\']'), iconStyle: 'icon-sign-node' },
          { type: 'WEBHOOK', name: this.$t('m[\'WEBHOOK节点\']'), iconStyle: 'icon-icon-webhook-2' },
          { type: 'APPROVAL', name: this.$t('m.treeinfo[\'审批节点\']'), iconStyle: 'icon-approval-node' },
          { type: 'COVERAGE', name: this.$t('m.treeinfo["汇聚网关"]'), iconStyle: 'icon-flow-branch' },
          { type: 'ROUTER-P', name: this.$t('m.treeinfo["并行网关"]'), iconStyle: 'icon-flow-convergence' },
          { type: 'COPY', name: this.$t('m.treeinfo["复制节点"]'), iconStyle: 'icon-copy-new' },
        ],
        currentNode: {},
      };
    },
    mounted() {
      this.toolStatus = localStorage.getItem('toolStatus') || false;
    },
    methods: {
      hoverNode(node) {
        if (node.nodeInfo && node.nodeInfo.errorInfo) {
          node.nodeInfo.errorInfo = false;
        }
      },
      moveDoneFn(node) {
        this.moveFlag = false;
        // 将拖拽节点的层级设置最高
        const listInfo = document.getElementsByClassName('jsflow-node');
        for (let i = 0; i < listInfo.length; i++) {
          listInfo[i].style['z-index'] = 101;
        }
        if (document.getElementById(node.id)) {
          document.getElementById(node.id).style['z-index'] = 102;
        }
      },
      moveFn() {
        this.moveFlag = true;
      },
      onNodeClick(node) {
        this.currentNode = node;
        // 往数组中添加数据属性
        const showValue = Boolean(node.showMore);
        this.$set(node, 'showMore', showValue);
        // 操作节点时往数据中添加
        if (!this.moveFlag) {
          // 点击节点操作(将点击节点的操作放到右键上实现)
        } else {
          const valueNode = this.canvasData.nodes.find(item => item.id === node.id);
          this.$store.commit('deployCommon/changeNodeInfo', valueNode);
        }
        this.moveFlag = false;
      },
      clickNode() {
        this.openconfigu();
      },
      // 右键事件
      rightClickNode(node) {
        if (!node) {
          return;
        }
        this.$emit('closeShow');
        node.showMore = true;
      },
      // 配置详情
      openconfigu() {
        const node = deepClone(this.node);
        const deviation = 3; // 允许偏差值
        // 如果是move节点，则不触发点击事件
        if (
          Math.abs(node.x - this.currentNode.x) > deviation
          || Math.abs(node.y - this.currentNode.y) > deviation
        ) {
          return;
        }
        // 如果是汇聚网关和并行网关则不触发事件
        if (node.type === 'ROUTER-P' || node.type === 'COVERAGE' || node.type === 'START' || node.type === 'END') {
          return;
        }
        this.$emit('configuNode', node.nodeInfo);
      },
      closeNode() {
        this.node.showMore = false;
      },
      // 新增节点
      addNormal(node, value) {
        if (this.clickSecond) {
          return;
        }
        this.clickSecond = true;
        this.$store.commit('deployCommon/changeNodeStatus', true);
        if (value.type !== 'COPY') {
          // 获取当前节点的输出连线
          const lineList = this.canvasData.lines.filter(item => item.source.id === node.id);
          const xValue = (node.type === 'NORMAL' || node.type === 'TASK') ? 310 : 210;
          // 节点前后id值
          const params = {
            workflow: node.nodeInfo.workflow,
            name: '',
            type: value.type,
            is_terminable: false,
            axis: {
              x: node.x + xValue,
              y: node.y + lineList.length * 80,
            },
            extras: {},
          };
          this.$store.dispatch('deployCommon/creatNode', { params }).then((res) => {
            this.valueInfo.node = {
              id: `node_${res.data.id}`,
              x: node.x + xValue,
              y: node.y + lineList.length * 80,
              type: value.type,
              name: res.data.name,
              showMore: false,
              nodeInfo: res.data,
            };
            this.$emit('closeShow');
            this.$emit('updateNode', this.valueInfo);
            this.addNewLine(node, res.data.id);
          })
            .catch(res => {
              errorHandler(res, this);
            })
            .finally(() => {
              this.clickSecond = false;
              this.$store.commit('deployCommon/changeNodeStatus', false);
            });
        } else {
          const id = this.node.nodeInfo.id;
          this.$store.dispatch('deployCommon/copyNode', id).then((res) => {
            this.valueInfo.node = {
              id: `node_${res.data.id}`,
              x: res.data.axis.x,
              y: res.data.axis.y,
              type: res.data.type,
              name: res.data.name,
              showMore: false,
              nodeInfo: res.data,
            };
            this.$emit('closeShow');
            this.$emit('updateNode', this.valueInfo);
            // this.addNewLine(node, res.data.id)
          })
            .catch(res => {
              errorHandler(res, this);
            })
            .finally(() => {
              this.clickSecond = false;
              this.$store.commit('deployCommon/changeNodeStatus', false);
            });
        }
      },
      // 新增线条
      addNewLine(fromNode, toState) {
        const lineParams = {
          workflow: fromNode.nodeInfo.workflow,
          name: this.$t('m.treeinfo["默认"]'),
          axis: {
            start: 'Right',
            end: 'Left',
          },
          from_state: fromNode.nodeInfo.id,
          to_state: toState,
        };
        this.$store.dispatch('deployCommon/createLine', { lineParams }).then((res) => {
          this.valueInfo.line = {
            source: {
              arrow: 'Right',
              id: fromNode.id,
            },
            target: {
              arrow: 'Left',
              id: this.valueInfo.node.id,
            },
            lineInfo: res.data,
          };
          this.$emit('fastAddNode', this.valueInfo);
          this.$emit('updateLine', this.valueInfo.line, 'add');
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      // 删除线条
      clickDelete(node) {
        this.$emit('openDelete', node);
      },
      // 隐藏提示
      closeTool() {
        this.toolStatus = true;
        localStorage.setItem('toolStatus', true);
      },
    },
  };
</script>
<style lang="scss" scoped>
    @import './jsflowCss/nodeTemplate.scss';

    .bk-font-style {
        font-size: 24px;
    }
</style>
