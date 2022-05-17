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
  <div :class="{ 'bk-second-flow': true, 'bk-full-page': isFullPage }" v-if="isReset">
    <bk-button class="bk-close-btn" :text="true" icon="close" @click="isFullPage = false;onResetPosition()"></bk-button>
    <p class="bk-sla-text">{{$t(`m.serviceConfig['“S”代表协议生效节点，“E”代表协议结束节点，不支持节点间交叉添加协议']`)}}</p>
    <js-flow
      ref="jsFlow"
      v-model="canvasData"
      selector="entry-item"
      :endpoint-options="endpointOptions"
      :connector-options="connectorOptions"
      :node-options="nodeOptions"
      :tools="toolsInfo[+isFullPage]"
      :editable="false"
      @onToolClick="onToolClick"
      @onConnectionClick="onConnectionClick"
      @onConnection="onConnection"
      @onConnectionDragStop="onConnectionDragStop"
      @onBeforeDrop="onBeforeDrop"
      @onNodeMoveStop="onNodeMoveStop"
      @onNodeMoving="onNodeMoving">
      <template slot="nodeTemplate" slot-scope="{ node }">
        <div class="bk-sla-rect">
          <span v-for="(agree, index) in serviceAgreementList" :key="index">
            <span
              v-if="agree.start_node_id === node.nodeInfo.id"
              class="bk-sla-se"
              :style="'background: ' + agree.color"
              @click="slaIconClick(agree)"
              @mouseenter="hoverSlaObj = agree;updateCanvas()"
              @mouseout="hoverSlaObj = {};updateCanvas()"
            >S</span>
            <span
              v-if="agree.end_node_id === node.nodeInfo.id"
              class="bk-sla-se"
              :style="'background: ' + agree.color"
              @click="slaIconClick(agree)"
              @mouseenter="hoverSlaObj = agree;updateCanvas()"
              @mouseout="hoverSlaObj = {};updateCanvas()"
            >E</span>
          </span>
        </div>
        <node-template
          :class="{ 'bk-sla-hover-node-shadow': isHoverNode(node.nodeInfo.id) }"
          ref="templateNode"
          :node="node"
          :canvas-data="canvasData"
          @configuNode="configuNode">
        </node-template>
      </template>
    </js-flow>
  </div>
</template>
<script>
  import JsFlow from '@/assets/jsflow';
  import NodeTemplate from '../../../processManagement/processDesign/jsflowCanvas/NodeTemplate';
  import { errorHandler } from '../../../../utils/errorHandler';

  const endpointOptions = {
    endpoint: 'Dot',
    connector: ['Flowchart', { stub: [10, 16], alwaysRespectStub: true, gap: 2, cornerRadius: 10 }],
    // connector: ['Bezier', { curviness: 60, stub: [0, 10], gap: 3, cornerRadius: 3, alwaysRespectStubs: true }],
    connectorOverlays: [
      ['PlainArrow', { width: 8, length: 6, location: 1, id: 'arrow' }],
    ],
    paintStyle: { fill: 'rgba(0, 0, 0, 0)', stroke: '', strokeWidth: 1, radius: 8 },
    hoverPaintStyle: { fill: '#EE8F62', stroke: '#EE8F62', radius: 8 },
    cssClass: 'template-canvas-endpoint',
    hoverClass: 'template-canvas-endpoint-hover',
    isSource: false, // 端点是否可以作为拖动源
    isTarget: false, // 端点是否可以作为拖动目标
    maxConnections: -1,
  };
  const nodeOptions = {
    grid: [5, 5],
    stop: true,
  };
  const connectorOptions = {
    paintStyle: { fill: 'transparent', stroke: '#a9adb6', strokeWidth: 1 },
    hoverPaintStyle: { fill: 'transparent', stroke: '#3a84ff', strokeWidth: 2 },
    cssClass: 'bk-sops-connector',
    hoverClass: 'bk-sops-connector-hover',
    detachable: false, // 是否可以通过鼠标拖动连线
  };
  export default {
    name: 'SecondFlow',
    components: {
      JsFlow,
      NodeTemplate,
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
      serviceAgreementList: {
        type: Array,
        default() {
          return [];
        },
      },
      flowInfo: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        hoverSlaObj: {},
        clickSecond: false,
        isReset: true,
        endpointOptions,
        connectorOptions,
        nodeOptions,
        canvasData: {
          nodes: [],
          lines: [],
        },
        toolsInfo: [
          [
            {
              type: 'zoomIn',
              name: ' ',
              title: this.$t('m.treeinfo[\'放大\']'),
              cls: 'bk-itsm-icon icon-flow-other-add',
            },
            {
              type: 'zoomOut',
              name: ' ',
              title: this.$t('m.treeinfo[\'缩小\']'),
              cls: 'bk-itsm-icon icon-flow-other-reduc',
            },
            {
              type: 'fullPagePosition',
              name: ' ',
              title: this.$t('m.treeinfo[\'全屏\']'),
              cls: 'bk-itsm-icon icon-flow-restore',
            },
            {
              type: 'frameSelect',
              name: ' ',
              title: this.$t('m.treeinfo[\'框选\']'),
              cls: 'bk-itsm-icon icon-choose-node',
            },
          ],
          [
            {
              type: 'zoomIn',
              name: ' ',
              title: this.$t('m.treeinfo[\'放大\']'),
              cls: 'bk-itsm-icon icon-flow-other-add',
            },
            {
              type: 'zoomOut',
              name: ' ',
              title: this.$t('m.treeinfo[\'缩小\']'),
              cls: 'bk-itsm-icon icon-flow-other-reduc',
            },
            {
              type: 'frameSelect',
              name: ' ',
              title: this.$t('m.treeinfo[\'框选\']'),
              cls: 'bk-itsm-icon icon-choose-node',
            },
          ],
        ],
        nodeInfo: {},
        // 放大缩小极限
        toolLimit: 4,
        // 删除节点
        deleteInfo: {
          isShow: false,
          title: this.$t('m.treeinfo["确认删除"]'),
          content: this.$t('m.treeinfo["确认后，此节点将从该流程中移除！"]'),
          info: {},
        },
        drawStatus: false,
        isFullPage: false,
        currentNode: {},
        instance: [],
      };
    },
    computed: {
      nodeStatus() {
        return this.$store.state.deployCommon.nodeStatus;
      },
      stateNodeInfo() {
        return this.$store.state.deployCommon.nodeInfo;
      },
    },
    created() {
      this.initDate();
    },
    mounted() {
      this.addLineOverlay();
      this.instance = this.$refs.jsFlow.instance;
      this.$refs.jsFlow.zoomOut(this.flowInfo.narrowSize);
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
            options: {
              paintStyle: {
                fill: 'rgba(0, 0, 0, 0)',
                stroke: 'rgba(52, 138, 243, 0.15)',
                strokeWidth: 1,
                radius: 7,
              },
            },
          });
          this.$set(this.nodeInfo, `node_${item.id}`, item);
        });
        this.getLineData();
      },
      getLineData() {
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
                stroke: this.getLineColor(item.id),
                strokeWidth: this.getLineColor(item.id) === '#a9adb6' ? 1 : 2,
              },
            },
          });
        });
      },
      updateCanvas() {
        this.removeAllConnector();
        this.getLineData();
        this.renderLineData();
      },
      slaIconClick(agree) {
        this.$emit('slaIconClick', agree);
      },
      renderLineData() {
        this.instance.batch(() => {
          this.canvasData.lines.forEach((line) => {
            this.$refs.jsFlow.createConnector(line);
          });
        });
        this.addLineOverlay();
      },
      // 删除所有连接线
      removeAllConnector() {
        this.instance.deleteEveryConnection();
        this.canvasData.lines = [];
      },
      getLineColor(lineId) {
        if ('color' in this.hoverSlaObj && 'lines' in this.hoverSlaObj) {
          return this.hoverSlaObj.lines.indexOf(lineId) !== -1 ? this.hoverSlaObj.color : 'rgba(176, 180, 189, 0.3)';
        }
        return '#a9adb6';
      },
      getLabelColor(lineId) {
        if ('color' in this.hoverSlaObj && 'lines' in this.hoverSlaObj) {
          return this.hoverSlaObj.lines.indexOf(lineId) !== -1 ? '#a9adb6' : 'rgba(176, 180, 189, 0.3)';
        }
        return '#a9adb6';
      },
      isHoverNode(nodeId) {
        if ('color' in this.hoverSlaObj && 'lines' in this.hoverSlaObj) {
          return this.hoverSlaObj.states.indexOf(nodeId) === -1;
        }
        return false;
      },
      // 保存节点报错 给错误节点标红
      errorNodes(valueList) {
        this.canvasData.nodes.forEach((item) => {
          valueList.forEach((node) => {
            if (item.nodeInfo.id === node) {
              this.$set(item.nodeInfo, 'errorInfo', true);
            }
          });
        });
      },
      // 注册线条的Lable
      addLineOverlay() {
        this.canvasData.lines.forEach((item) => {
          const value = {
            source: item.source,
            target: item.target,
            lineInfo: item.lineInfo,
            id: item.lineInfo.id,
            name: item.lineInfo.name,
          };
          this.lineOverlay(value);
        });
      },
      lineOverlay(value) {
        // 如果输出节点为开始节点，输入节点为提单节点，则不提供Label样式
        const startNode = this.canvasData.nodes.some(item => (value.source.id === item.id && item.type === 'START'));
        // const billNode = this.canvasData.nodes.some(item => (value.target.id === item.id && item.name === '提单'))
        if (startNode) {
          return;
        }
        const labelColor = this.getLabelColor(value.id);
        // 判断label的样式(两个以上线条的时候显示label样式)
        const labelName = `<span class="bk-label-test-name" style="color: ${labelColor}; border-color: ${labelColor}">${value.name || this.$t('m.treeinfo["默认"]')}</span>`;
        const lineInfo = {
          id: `label_${value.id}`,
          type: 'Label',
          name: labelName,
          cls: 'label-test',
          location: 0.5,
        };
        this.$refs.jsFlow.addLineOverlay(value, lineInfo);
      },
      removerLine(value) {
        this.$refs.jsFlow.removeConnector({
          source: {
            id: value.sourceId,
          },
          target: {
            id: value.targetId,
          },
        });
      },
      // 点击tool事件
      onToolClick(tool) {
        if (tool.type === 'fullPagePosition') {
          this.isFullPage = true;
        }
      },
      onResetPosition() {
        this.$refs.jsFlow.resetPosition();
      },
      // 单机连线
      onConnectionClick() {
        // ...
      },
      // 连线吸附后
      onConnection(connection) {
        if (!this.drawStatus) {
          return;
        }
        this.drawLine(connection);
        this.drawStatus = false;
      },
      // 连线拖动到节点
      onConnectionDragStop(source, targetId, event) {
        const params = {
          sourceId: source.id,
          targetId,
        };
        if (!this.checkLineInfo(params)) {
          return;
        }
        let arrow;
        const line = {
          source,
          target: {
            id: targetId,
          },
        };
        const nodeEl = document.getElementById(targetId);
        const nodeRects = nodeEl.getBoundingClientRect();
        const offsetX = event.clientX - nodeRects.left;
        const offsetY = event.clientY - nodeRects.Top;
        if (offsetX < nodeRects.width / 2) {
          if (offsetY < nodeRects.height / 2) {
            arrow = offsetX > offsetY ? 'Top' : 'Left';
          } else {
            arrow = offsetX > (nodeRects.height - offsetY) ? 'Bottom' : 'Left';
          }
        } else {
          if (offsetY < nodeRects.height / 2) {
            arrow = (nodeRects.width - offsetX) > offsetY ? 'Top' : 'Right';
          } else {
            arrow = (nodeRects.width - offsetX) > (nodeRects.height - offsetY) ? 'Bottom' : 'Right';
          }
        }
        line.target.arrow = arrow;
        this.$refs.jsFlow.createConnector(line);
        const connection = {
          sourceId: source.id,
          targetId,
          sourceEndpoint: {
            anchor: {
              type: source.arrow,
            },
          },
          targetEndpoint: {
            anchor: {
              type: arrow,
            },
          },
        };
        this.drawLine(connection);
        this.drawStatus = false;
      },
      // 连线放下之前的回调函数
      onBeforeDrop(params) {
        return this.checkLineInfo(params);
      },
      checkLineInfo(params) {
        // 根据前后ID来获取前后节点的信息
        const fromNode = this.canvasData.nodes.filter(item => (item.id === params.sourceId));
        const toNode = this.canvasData.nodes.filter(item => (item.id === params.targetId));
        const statusValue = {
          status: true,
          msg: '',
        };
        // 开始节点只能输出（且只能单一输出），结束节点只能输入
        if (fromNode[0].type === 'START') {
          const startStatus = this.canvasData.lines.some(item => item.source.id === fromNode[0].id);
          if (startStatus) {
            statusValue.status = false;
            statusValue.msg = this.$t('m.treeinfo["开始节点只能单一输出！"]');
          }
        }
        if (toNode[0].type === 'START') {
          statusValue.status = false;
          statusValue.msg = this.$t('m.treeinfo["开始节点只能输出！"]');
        }
        if (fromNode[0].type === 'END') {
          statusValue.status = false;
          statusValue.msg = this.$t('m.treeinfo["结束节点只能输入！"]');
        }
        if (fromNode[0].type === 'START' && toNode[0].type === 'END') {
          statusValue.status = false;
          statusValue.msg = this.$t('m.treeinfo["开始节点和结束节点不能直接相连！"]');
        }
        if (params.sourceId === params.targetId) {
          statusValue.status = false;
          statusValue.msg = this.$t('m.treeinfo["自身不能相连！"]');
        }
        // 已存在相同的连线不能相连
        for (let i = 0; i < this.canvasData.lines.length; i++) {
          if (params.sourceId === this.canvasData.lines[i].source.id && params.targetId === this.canvasData.lines[i].target.id) {
            statusValue.status = false;
            statusValue.msg = this.$t('m.treeinfo["已存在的连线！"]');
          }
        }
        if (!statusValue.status) {
          this.$bkMessage({
            message: statusValue.msg,
            theme: 'warning',
          });
        }
        // 用于判断是否是手动绘制
        this.drawStatus = true;
        return statusValue.status;
      },
      async drawLine(params) {
        let targetId = '';
        let sourceId = '';
        const errorId = {
          targetId: '',
          sourceId: '',
        };
        this.canvasData.nodes.forEach((item) => {
          if (item.id === params.sourceId) {
            sourceId = item.nodeInfo.id;
            errorId.sourceId = item.id;
          }
          if (item.id === params.targetId) {
            targetId = item.nodeInfo.id;
            errorId.targetId = item.id;
          }
        });
        const lineParams = {
          workflow: this.addList[0].workflow,
          name: this.$t('m.treeinfo["默认"]'),
          axis: {
            start: params.sourceEndpoint.anchor.type,
            end: params.targetEndpoint.anchor.type,
          },
          from_state: sourceId,
          to_state: targetId,
        };
        // 在移动的过程中 可能出现重复的连线
        const errorStatus = this.canvasData.lines.some(item => (item.source.id === errorId.sourceId && item.target.id === errorId.targetId));
        if (errorStatus) {
          return;
        }

        if (this.clickSecond) {
          return;
        }
        this.clickSecond = true;
        await this.$store.dispatch('deployCommon/createLine', { lineParams }).then((res) => {
          const value = [{
            source: {
              arrow: lineParams.axis.start,
              id: params.sourceId,
            },
            target: {
              arrow: lineParams.axis.end,
              id: params.targetId,
            },
            lineInfo: res.data,
            id: res.data.id,
            name: res.data.name,
          }];
          this.updateLine(value, 'add');
          // 新增线条需要注册label事件
          this.lineOverlay(value[0]);
        })
          .catch((res) => {
            errorHandler(res, this);
            const errorStatus = this.canvasData.lines.some(item => (item.source.id === errorId.sourceId && item.target.id === errorId.targetId));
            if (!errorStatus) {
              // 删除画布上的线条
              this.$refs.jsFlow.removeConnector({
                source: {
                  id: errorId.sourceId,
                },
                target: {
                  id: errorId.targetId,
                },
              });
            }
          })
          .finally(() => {
            this.clickSecond = false;
          });
      },
      // 更新线条的数据
      updateLine(params, type) {
        if (type === 'delete') {
          params.forEach((node) => {
            this.canvasData.lines.forEach((item, index) => {
              if (item.source.id === node.source.id && item.target.id === node.target.id) {
                this.canvasData.lines.splice(index, 1);
              }
            });
          });
        } else if (type === 'update') {
          params.forEach((node) => {
            this.canvasData.lines.forEach((item) => {
              if (item.source.id === node.source.id && item.target.id === node.target.id) {
                item.lineInfo = node.lineInfo;
              }
            });
          });
        } else if (type === 'add') {
          this.canvasData.lines = this.canvasData.lines.concat(params);
        }
      },
      // 删除连线回调
      onConnectionDetached() {
        // this.$refs.jsFlow.removeConnector({
        //     source: {
        //         id: connection.sourceId
        //     },
        //     target: {
        //         id: connection.targetId
        //     }
        // })
      },
      // 画布操作
      onZoomIn() {
        if (this.toolLimit > 9) {
          return;
        }
        this.toolLimit += 1;
        if (this.$refs.jsFlow) {
          this.$refs.jsFlow.zoomIn();
        }
      },
      onZoomOut() {
        if (this.toolLimit === 0) {
          return;
        }
        this.toolLimit -= 1;
        if (this.$refs.jsFlow) {
          this.$refs.jsFlow.zoomOut();
        }
      },
      onCanvasFrameSelect() {
        // ...
      },
      // 鼠标滚轮事件
      handleScroll(e) {
        if (e.deltaY > 0) {
          this.onZoomOut();
        } else {
          this.onZoomIn();
        }
      },
      updateNode(value) {
        this.$refs.jsFlow.createNode(value.node);
        // 在快速新增的时候，防止节点跌在一起
        const valueList = [];
        this.canvasData.nodes.forEach((item) => {
          const differenceValue = {
            x: item.x - value.node.x,
            y: item.y - value.node.y,
          };
          if (value.node.id !== item.id && differenceValue.y >= -40 && differenceValue.x >= -150 && differenceValue.x <= 150) {
            const valueInfo = {
              id: item.id,
              nodeInfo: item.nodeInfo,
              x: item.x,
              y: item.y + 100,
            };
            valueList.push(valueInfo);
            setTimeout(() => {
              this.$refs.jsFlow.setNodePosition(valueInfo);
              this.moveNode(valueInfo);
            }, 100);
          }
        });
        // 重置原始数据内容
        this.canvasData.nodes.forEach((item) => {
          valueList.forEach((node) => {
            if (item.id === node.id) {
              item.x = node.x;
              item.y = node.y;
            }
          });
        });
      },
      deleteNode() {
        const { id } = this.deleteInfo.info.nodeInfo;
        if (this.clickSecond) {
          return;
        }
        this.clickSecond = true;
        this.$store.dispatch('deployCommon/deleteNode', id).then(() => {
          if (this.deleteInfo.info.nodeInfo.is_draft) {
            // ...
          } else {
            this.$bkMessage({
              message: this.$t('m.treeinfo["删除成功"]'),
              theme: 'success',
            });
          }
          // 删除节点获取节点上的所以连线，并将连线数组更新
          const valueList = this.$refs.jsFlow.getConnectorsByNodeId(this.deleteInfo.info.id);
          const listInfo = [];
          for (let i = 0; i < valueList.length; i++) {
            listInfo.push({
              source: {
                arrow: 'Left',
                id: valueList[i].sourceId,
              },
              target: {
                arrow: 'Left',
                id: valueList[i].targetId,
              },
              lineInfo: {},
            });
          }
          if (listInfo.length) {
            this.updateLine(listInfo, 'delete');
          }
          // 删除画布上的节点
          this.$refs.jsFlow.removeNode(this.deleteInfo.info);
          this.closeDelete();
        })
          .catch((res) => {
            this.$bkMessage({
              message: res.data.msg,
              theme: 'error',
            });
          })
          .finally(() => {
            this.clickSecond = false;
          });
      },
      closeDelete() {
        this.deleteInfo.isShow = false;
      },
      // 配置操作
      configuNode(value) {
        this.isReset = false;
        this.$emit('configuNode', value);
        this.isReset = true;
      },
      // 移动节点事件回调
      onNodeMoveStop(node) {
        // 如果节点没有移动，这触发点击事件
        if (node.x === this.currentNode.x && node.y === this.currentNode.y) {
          this.canvasData.nodes.forEach((item) => {
            item.showMore = false;
          });
          this.canvasData.nodes.forEach((item) => {
            if (node.id === item.id) {
              item.showMore = true;
            }
          });
          return;
        }
        let moveNodeStatus = false;
        for (let i = 0; i < this.canvasData.nodes.length; i++) {
          const item = this.canvasData.nodes[i];
          if (node.id !== item.id) {
            const differenceValue = {
              x: item.x - node.x,
              y: item.y - node.y,
            };
            // 移动节点为NORMAL，ROUTER，TASK
            if (node.type === 'NORMAL' || node.type === 'ROUTER' || node.type === 'TASK') {
              // 目标节点为NORMAL，ROUTER，TASK
              if (item.type === 'NORMAL' || item.type === 'ROUTER' || item.type === 'TASK') {
                if (differenceValue.x >= -150 && differenceValue.x <= 150 && differenceValue.y >= -40 && differenceValue.y <= 40) {
                  moveNodeStatus = true;
                  break;
                }
              } else {
                if (differenceValue.x >= -40 && differenceValue.x <= 150 && differenceValue.y >= -40 && differenceValue.y <= 40) {
                  moveNodeStatus = true;
                  break;
                }
              }
            } else {
              // 目标节点为NORMAL，ROUTER，TASK
              if (item.type === 'NORMAL' || item.type === 'ROUTER' || item.type === 'TASK') {
                if (differenceValue.x >= -150 && differenceValue.x <= 40 && differenceValue.y >= -40 && differenceValue.y <= 40) {
                  moveNodeStatus = true;
                  break;
                }
              } else {
                if (differenceValue.x >= -40 && differenceValue.x <= 40 && differenceValue.y >= -40 && differenceValue.y <= 40) {
                  moveNodeStatus = true;
                  break;
                }
              }
            }
          }
        }
        if (moveNodeStatus) {
          const valueInfo = {
            id: node.id,
            x: this.stateNodeInfo.x,
            y: this.stateNodeInfo.y,
          };
          this.$refs.jsFlow.setNodePosition(valueInfo);
          for (let i = 0; i < this.canvasData.nodes.length; i++) {
            if (node.id === this.canvasData.nodes[i].id) {
              this.canvasData.nodes[i].x = this.stateNodeInfo.x;
              this.canvasData.nodes[i].y = this.stateNodeInfo.y;
            }
          }
          return;
        }
        this.moveNode(node);
      },
      // 节点拖拽moving回调
      onNodeMoving(node, event) {
        const nodeValue = node;
        nodeValue.x = event.pos[0];
        nodeValue.y = event.pos[1];
        // this.getBestArrow(nodeValue, event)
      },
      // 最优连线
      getBestArrow(node) {
        // 节点ID
        const dataConten = {
          parent: [],
          parentLine: [],
          children: [],
          childrenLine: [],
        };
        // 去掉两条线共存的现象
        const otherList = [];
        this.canvasData.lines.forEach((item) => {
          let otherStatus = false;
          this.canvasData.lines.forEach((node) => {
            if (item.source.id === node.target.id && item.target.id === node.source.id) {
              otherStatus = true;
            }
          });
          if (!otherStatus) {
            otherList.push(item);
          }
        });
        otherList.forEach((item) => {
          if (node.id === item.target.id) {
            dataConten.parent.push(item.source.id);
            dataConten.parentLine.push(item);
          }
          if (node.id === item.source.id) {
            dataConten.children.push(item.target.id);
            dataConten.childrenLine.push(item);
          }
        });
        // 节点EndPoint位置
        const typeList = ['NORMAL', 'ROUTER', 'TASK', 'TASK-SOPS'];
        const currentNodeEndpoints = this.getEndPointInfo(node, typeList);
        const parentNodeEndpoints = {};
        const childrenNodeEndpoints = {};
        dataConten.parent.forEach((item) => {
          this.canvasData.nodes.forEach((pN) => {
            if (item === pN.id) {
              parentNodeEndpoints[item] = this.getEndPointInfo(pN, typeList);
            }
          });
        });
        dataConten.children.forEach((item) => {
          this.canvasData.nodes.forEach((pN) => {
            if (item === pN.id) {
              childrenNodeEndpoints[item] = this.getEndPointInfo(pN, typeList);
            }
          });
        });
        // 计算parent节点的最优连线
        let tempArr = [];
        dataConten.parent.forEach((pN) => {
          tempArr = [];
          currentNodeEndpoints.forEach((c) => {
            parentNodeEndpoints[pN].forEach((p) => {
              tempArr.push({
                cArrow: c.anchor,
                pArrow: p.anchor,
                distance: Math.pow(c.x - p.x, 2) + Math.pow(c.y - p.y, 2),
              });
            });
            tempArr = tempArr.sort(compare('distance'));

            function compare(property) {
              return function (obj1, obj2) {
                const value1 = obj1[property];
                const value2 = obj2[property];
                return value1 - value2;
              };
            }
          });
          const theBestArrowGroup = tempArr[0];
          const lineValue = {
            source: {
              id: pN,
            },
            target: {
              id: node.id,
            },
          };
          this.deleteBestLine(lineValue, theBestArrowGroup);
        });
        // 计算children节点的最优连线
        let tempArr2 = [];
        dataConten.children.forEach((cN) => {
          tempArr2 = [];
          currentNodeEndpoints.forEach((c) => {
            childrenNodeEndpoints[cN].forEach((p) => {
              tempArr2.push({
                cArrow: p.anchor,
                pArrow: c.anchor,
                distance: Math.pow(c.x - p.x, 2) + Math.pow(c.y - p.y, 2),
              });
            });
            tempArr2 = tempArr2.sort(compare('distance'));

            function compare(property) {
              return function (obj1, obj2) {
                const value1 = obj1[property];
                const value2 = obj2[property];
                return value1 - value2;
              };
            }
          });
          const theBestArrowGroup = tempArr2[0];
          const lineValue = {
            source: {
              id: node.id,
            },
            target: {
              id: cN,
            },
          };
          this.deleteBestLine(lineValue, theBestArrowGroup);
        });
      },
      getEndPointInfo(value, typeList) {
        const listInfo = [
          { anchor: 'Top', x: value.x + (typeList.some(item => item === value.type) ? 75 : 20), y: value.y },
          { anchor: 'Left', x: value.x, y: value.y + 20 },
          {
            anchor: 'Right',
            x: value.x + (typeList.some(item => item === value.type) ? 150 : 40),
            y: value.y + 20,
          },
          {
            anchor: 'Bottom',
            x: value.x + (typeList.some(item => item === value.type) ? 75 : 20),
            y: value.y + 40,
          },
        ];
        return listInfo;
      },
      deleteBestLine(lineValue, theBestArrowGroup) {
        // 当最优连线和原连线一样时，则不进行操作
        const valueStuta = this.canvasData.lines.some(item => (item.source.id === lineValue.source.id && item.target.id === lineValue.target.id && item.source.arrow === theBestArrowGroup.pArrow && item.target.arrow === theBestArrowGroup.cArrow));
        if (valueStuta) {
          return;
        }
        this.$refs.jsFlow.removeConnector({
          source: {
            id: lineValue.source.id,
          },
          target: {
            id: lineValue.target.id,
          },
        });
        this.canvasData.lines.forEach((item) => {
          if (item.source.id === lineValue.source.id && item.target.id === lineValue.target.id) {
            item.source.arrow = theBestArrowGroup.pArrow;
            item.target.arrow = theBestArrowGroup.cArrow;
            const value = {
              source: {
                arrow: theBestArrowGroup.pArrow,
                id: lineValue.source.id,
              },
              target: {
                arrow: theBestArrowGroup.cArrow,
                id: lineValue.target.id,
              },
              lineInfo: item.lineInfo,
            };
            this.$refs.jsFlow.createConnector(value);
            // 新增线条需要注册label事件
            const labelValue = {
              source: value.source,
              target: value.target,
              lineInfo: value.lineInfo,
              id: item.lineInfo.id,
              name: item.lineInfo.name,
            };
            this.lineOverlay(labelValue);
          }
        });
      },
      // 移动节点接口保存
      moveNode(node) {
        const params = {
          axis: {
            x: node.x,
            y: node.y,
          },
        };
        const { id } = node.nodeInfo;
        this.$store.dispatch('deployCommon/updateNodeAxis', { params, id }).then(() => {
          // ...
        })
          .catch((res) => {
            this.$bkMessage({
              message: res.data.msg,
              theme: 'error',
            });
          });
      },
    },
  };
</script>

<style lang='scss' scoped>
    .bk-sla-text {
        position: absolute;
        left: 0px;
        top: 0px;
        padding: 4px 14px;
        z-index: 1000;
        background-color: #f5f7fa;
    }
    .bk-sla-rect {
        position: absolute;
        left: 0;
        top: -20px;
    }
    .bk-sla-hover-node-shadow {
        opacity: 0.3;
    }
    .bk-sla-se {
        display: inline-block;
        width: 18px;
        height: 18px;
        color: #fff;
        font-size: 12px;
        border-radius: 2px;
        text-align: center;
    }
    .bk-second-flow {
        width: 100%;
        height: 100%;
        position: relative;
        z-index: 0;
        .bk-close-btn {
            display: none;
        }
    }
    .bk-full-page {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: 999;
        .bk-close-btn {
            display: block;
            position: absolute;
            left: 0;
            top: 0;
            font-size: 40px;
            z-index: 1001;
            color: #63656E;
        }
    }
</style>
<style lang="scss">
.bk-sla-content {
    .bk-flow-fast {
        display: none !important;
    }
}
</style>
