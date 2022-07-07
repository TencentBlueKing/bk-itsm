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
  <div class="bk-second-flow bk-preview-flow">
    <js-flow
      ref="previewFlow"
      v-model="canvasData"
      selector="entry-item"
      :endpoint-options="endpointOptions"
      :connector-options="connectorOptions"
      :node-options="nodeOptions"
      :show-palette="false"
      @onNodeMoveStop="onNodeMoveStop">
      <template slot="toolPanel">
        <tool-panel
          @onZoomIn="onZoomIn"
          @onZoomOut="onZoomOut"
          @onResetPosition="onResetPosition"
          :full-status="fullStatus">
        </tool-panel>
      </template>
      <template slot="nodeTemplate" slot-scope="{ node }">
        <node-template
          ref="templateNode"
          :node="node"
          :canvas-data="canvasData"
          :preview-info="previewInfo"
          :normal-color="normalColor"
          @clickNodeInfo="clickNodeInfo"
          @submitNodeValue="submitNodeValue">
        </node-template>
      </template>
    </js-flow>
  </div>
</template>
<script>
  import JsFlow from '@/assets/jsflow';
  import NodeTemplate from './NodeTemplate.vue';
  import toolPanel from './toolPanel.vue';

  const endpointOptions = {
    endpoint: 'Dot',
    connector: ['Flowchart', { stub: [10, 16], alwaysRespectStub: true, gap: 2, cornerRadius: 10 }],
    // connector: ['Bezier', { curviness: 60, stub: [0, 10], gap: 3, cornerRadius: 3, alwaysRespectStubs: true }],
    connectorOverlays: [
      ['PlainArrow', { width: 8, length: 6, location: 1, id: 'arrow' }],
    ],
    paintStyle: { fill: 'rgba(0, 0, 0, 0)', stroke: '', strokeWidth: 1, radius: 6 },
    hoverPaintStyle: { fill: '#EE8F62', stroke: '#EE8F62', radius: 8 },
    cssClass: 'template-canvas-endpoint',
    hoverClass: 'template-canvas-endpoint-hover',
    isSource: true, // 端点是否可以作为拖动源
    isTarget: true, // 端点是否可以作为拖动目标
    maxConnections: -1,
  };
  const nodeOptions = {
    grid: [5, 5],
  };
  const connectorOptions = {
    paintStyle: { fill: 'transparent', stroke: '#a9adb6', strokeWidth: 1 },
    hoverPaintStyle: { fill: 'transparent', stroke: '#3a84ff', strokeWidth: 2 },
    cssClass: 'bk-sops-connector',
    hoverClass: 'bk-sops-connector-hover',
    detachable: true, // 是否可以通过鼠标拖动连线
  };
  export default {
    components: {
      JsFlow,
      NodeTemplate,
      toolPanel,
    },
    props: {
      addList: {
        type: Array,
        default() {
          return [];
        },
      },
      lineList: {
        type: Array,
        default() {
          return [];
        },
      },
      previewInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      fullStatus: {
        type: Boolean,
        default() {
          return false;
        },
      },
      normalColor: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        endpointOptions,
        connectorOptions,
        nodeOptions,
        canvasData: {
          nodes: [],
          lines: [],
        },
        nodeInfo: {},
        // 放大缩小极限
        toolLimit: 4,
        currentNode: {},
      };
    },
    computed: {
      nodeStatus() {
        return this.$store.state.deployCommon.nodeStatus;
      },
    },
    created() {
      this.initDate();
    },
    mounted() {
      this.addLineOverlay();
      // window.addEventListener('mousewheel', this.handleScroll, false)
      this.$refs.previewFlow.zoomOut(this.previewInfo.narrowSize);
    },
    methods: {
      // 初始化数据
      initDate() {
        this.addList.forEach((item, index) => {
          const xValue = item.axis.x ? item.axis.x : (165 + index * 250);
          const yValue = item.axis.y ? item.axis.y : (195 + (index % 2 === 1 ? 5 : 0));
          this.canvasData.nodes.push({
            id: `node_${item.id}`,
            x: xValue,
            y: yValue,
            type: item.type,
            name: item.name,
            showMore: false,
            nodeInfo: item,
          });
          this.$set(this.nodeInfo, `node_${item.id}`, item);
        });
        this.lineList.forEach((item) => {
          this.canvasData.lines.push({
            source: {
              arrow: item.axis.start || 'Right',
              id: `node_${item.from_state}`,
            },
            target: {
              arrow: item.axis.end || 'Left',
              id: `node_${item.to_state}`,
            },
            lineInfo: item,
            options: {
              paintStyle: {
                fill: 'transparent',
                stroke: item.lineStatus === 'SUCCESS' ? '#2DCB56' : '#a9adb6',
                strokeWidth: 1,
              },
            },
          });
        });
      },
      // 修改数据状态
      changeDataStatus() {
        // 更新节点的颜色
        this.canvasData.nodes.forEach((item) => {
          this.addList.forEach((node) => {
            if (item.nodeInfo.id === node.id) {
              item.nodeInfo = node;
            }
          });
        });
        // 更新线条的颜色
        // this.canvasData.lines.forEach(item => {
        //     this.lineList.forEach(node => {
        //         // ID相同，线条颜色不匹配
        //         if (item.lineInfo.id === node.id && item.options.paintStyle.stroke === '#a9adb6' && node.lineStatus === 'RUNNING') {
        //             // 1：删除线条
        //             this.$refs.previewFlow.removeConnector({
        //                 source: {
        //                     id: item.source.id
        //                 },
        //                 target: {
        //                     id: item.target.id
        //                 }
        //             })
        //             // 2：新增连线
        //             this.$refs.previewFlow.createConnector({
        //                 source: {
        //                     arrow: item.source.arrow,
        //                     id: item.source.id
        //                 },
        //                 target: {
        //                     arrow: item.target.arrow,
        //                     id: item.target.id
        //                 },
        //                 options: {
        //                     paintStyle: {
        //                         fill: 'transparent',
        //                         stroke: node.lineStatus === 'RUNNING' ? '#2DCB56' : '#a9adb6',
        //                         strokeWidth: 1
        //                     }
        //                 },
        //                 lineInfo: node
        //             })
        //             // 3:原先存在的label则继续保留label
        //             setTimeout(() => {
        //                 const value = {
        //                     id: 'label_' + item.lineInfo.id,
        //                     type: 'Label',
        //                     name: `<span class="bk-label-test-name">${item.lineInfo.name || '默认'}</span>`,
        //                     cls: 'label-test ' + ((node.lineStatus === 'RUNNING') ? 'label-success' : ''),
        //                     location: 0.5
        //                 }
        //                 if ((item.lineInfo.name !== '默认' && item.lineInfo.name !== 'Default') && item.lineInfo.name) {
        //                     this.$refs.previewFlow.addLineOverlay(item, value)
        //                 }
        //             }, 100)
        //         }
        //     })
        // })
      },
      // 注册线条的Lable
      addLineOverlay() {
        this.canvasData.lines.forEach((item) => {
          const value = {
            id: `label_${item.lineInfo.id}`,
            type: 'Label',
            name: `<span class="bk-label-test-name">${item.lineInfo.name || this.$t('m.treeinfo["默认"]')}</span>`,
            cls: 'label-test',
            location: 0.5,
          };
          if ((item.lineInfo.name !== '默认' && item.lineInfo.name !== 'Default') && item.lineInfo.name) {
            this.$refs.previewFlow.addLineOverlay(item, value);
          }
        });
      },
      // 画布操作
      onZoomIn() {
        if (this.toolLimit > 9) {
          return;
        }
        this.toolLimit += 1;
        if (this.$refs.previewFlow) {
          this.$refs.previewFlow.zoomIn();
        }
      },
      onZoomOut() {
        if (this.toolLimit === 0) {
          return;
        }
        this.toolLimit -= 1;
        if (this.$refs.previewFlow) {
          this.$refs.previewFlow.zoomOut();
        }
      },
      onResetPosition() {
        this.$refs.jsFlow.resetPosition();
      },
      // 鼠标滚轮事件
      handleScroll(e) {
        if (e.deltaY > 0) {
          this.onZoomOut();
        } else {
          this.onZoomIn();
        }
      },
      // 点击节点操作
      clickNodeInfo(node) {
        if (!this.previewInfo.canClick) {
          return;
        }
        this.$parent.openNodeContent(node);
      },
      submitNodeValue(node) {
        this.currentNode = node;
      },
      onNodeMoveStop(node) {
        if (node.x === this.currentNode.x && node.y === this.currentNode.y) {
          this.$parent.openNodeContent(node);
        }
      },
    },
  };
</script>

<style lang='scss' scoped>
    .bk-second-flow {
        width: 100%;
        height: 100%;
    }
</style>
