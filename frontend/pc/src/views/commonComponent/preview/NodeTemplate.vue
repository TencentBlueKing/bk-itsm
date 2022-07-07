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
    data-test-id="node_template_view"
    class="bk-flow-location"
    @mousedown="movdeDoneFn"
    @mousemove="moveFn"
    @mouseup="onNodeClick(node, $event)">
    <div v-if="node.type === 'START'" class="startpoint">
      {{ $t('m.treeinfo["开始"]') }}
    </div>
    <div v-if="node.type === 'END'" class="endpoint">
      {{ $t('m.treeinfo["结束"]') }}
    </div>
    <template v-for="(item, index) in typeList" v-if="node.type === item.type">
      <div class="common-node" :class="{ 'common-auto': item.type === 'TASK' }" :key="index">
        <span
          class="bk-tool-span"
          v-if="node.nodeInfo.statusInfo === 'WAIT'"
          v-bk-tooltips.top="$t(`m.treeinfo['任务未执行，无法查看']`)"></span>
        <span
          class="common-auto-icon"
          :class="{
            'bk-is-draft': node.nodeInfo.is_draft,
            'bk-is-success': node.nodeInfo.statusInfo === 'FINISHED',
            'bk-is-error': node.nodeInfo.statusInfo === 'TERMINATED' || node.nodeInfo.statusInfo === 'FAILED',
            'bk-is-preview': node.nodeInfo.statusInfo === 'WAIT'
          }">
          <i class="bk-itsm-icon" :class="item.iconStyle" v-if="item.type !== 'TASK'"></i>
          <span v-else style="font-size: 12px; font-weight: bold">API</span>
        </span>
        <span
          class="bk-more-word"
          :class="{
            'bk-more-padding': previewInfo.canClick && node.nodeInfo.statusInfo !== 'WAIT',
            'bk-word-success': node.nodeInfo.statusInfo === 'FINISHED',
            'bk-word-error': node.nodeInfo.statusInfo === 'TERMINATED' || node.nodeInfo.statusInfo === 'FAILED',
            'bk-word-preview': node.nodeInfo.statusInfo === 'WAIT',
            'bk-word-normal': normalColor
          }">
          {{ node.name || $t(`m.treeinfo["新增节点"]`) }}</span
        >
        <template v-if="previewInfo.canClick && node.nodeInfo.statusInfo !== 'WAIT'">
          <div
            class="bk-icon-status"
            :class="{
              'bk-icon-success': node.nodeInfo.statusInfo === 'FINISHED',
              'bk-icon-error': node.nodeInfo.statusInfo === 'TERMINATED' || node.nodeInfo.statusInfo === 'FAILED'
            }">
            <i
              class="bk-icon icon-check-1"
              v-if="node.nodeInfo.statusInfo === 'FINISHED'"
              v-bk-tooltips.top="$t(`m.treeinfo['已通过']`)"></i>
            <i
              class="bk-icon icon-close"
              v-if="node.nodeInfo.statusInfo === 'TERMINATED' || node.nodeInfo.statusInfo === 'FAILED'"
              v-bk-tooltips.top="
                node.nodeInfo.statusInfo === 'TERMINATED' ? $t(`m.treeinfo['被终止']`) : $t(`m.treeinfo['失败']`)
              "></i>
            <img
              src="../../../images/loading_info.svg"
              v-if="node.nodeInfo.statusInfo === 'RUNNING' || node.nodeInfo.statusInfo === 'SUSPEND'"
              class="bk-rotation" />
          </div>
        </template>
      </div>
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
    name: 'NodeTemplate',
    props: {
      node: {
        type: Object,
        default() {
          return {};
        },
      },
      previewInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      normalColor: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        moveFlag: false,
        typeList: [
          { type: 'NORMAL', iconStyle: 'icon-icon-person' },
          { type: 'ROUTER', iconStyle: 'icon-icon-person' },
          { type: 'TASK', iconStyle: 'icon-api-icon' },
          { type: 'TASK-SOPS', iconStyle: 'icon-task-node' },
          { type: 'TASK-DEVOPS', iconStyle: 'icon-devops-task-icon' },
          { type: 'SIGN', iconStyle: 'icon-sign-node-white' },
          { type: 'WEBHOOK', iconStyle: 'icon-webhook-icon' },
          { type: 'BK-PLUGIN', iconStyle: 'icon-chajian-icon' },
          { type: 'APPROVAL', iconStyle: 'icon-approval-node' },
        ],
      };
    },
    mounted() {},
    methods: {
      movdeDoneFn() {
        this.moveFlag = false;
      },
      moveFn() {
        this.moveFlag = true;
      },
      onNodeClick(node) {
        if (!this.moveFlag) {
          // 对于开始，结束，网关，汇聚不弹出信息
          if (node.type === 'START' || node.type === 'END' || node.type === 'ROUTER-P' || node.type === 'COVERAGE') {
            return;
          }
          this.$emit('clickNodeInfo', node);
        } else {
          this.$emit('submitNodeValue', node);
        }
        this.moveFlag = false;
      },
    },
  };
</script>
<style lang="scss" scoped>
@import "./nodeTemplate.scss";
@import "../../../scss/animation/rotation.scss";

.bk-more-padding {
  padding-right: 35px;
}

.bk-is-success {
  background-color: #2dcb56 !important;
}

.bk-is-error {
  background-color: #ff5656 !important;
}

.bk-is-preview {
  background-color: #c4c6cc !important;
  cursor: not-allowed;
}

/* 文字 */
.bk-more-word {
  color: #3c96ff;
}

.bk-word-success {
  color: #2dcb56;
}

.bk-word-error {
  color: #ff5656;
}

.bk-word-preview {
  color: #c4c6cc;
}

.bk-word-normal {
  color: #63656e;
}

.bk-tool-span {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: not-allowed;
}

.common-node {
  position: relative;

  &:hover {
    .bk-is-success {
      box-shadow: 0px 2px 4px 0px rgba(45, 203, 86, 0.5) !important;
    }

    .bk-is-error {
      box-shadow: 0px 2px 4px 0px rgba(255, 86, 86, 0.5) !important;
    }

    .bk-is-preview {
      box-shadow: 0px 2px 4px 0px rgba(196, 198, 204, 0.5) !important;
    }

    /* 文字 */
    .bk-more-word {
      color: #3c96ff;
      border: 1px solid #3a84ff !important;
      border-radius: 0 20px 20px 0;
    }

    .bk-word-success {
      color: #2dcb56;
      border: 1px solid #2dcb56 !important;
      border-radius: 0 20px 20px 0;
    }

    .bk-word-error {
      color: #ff5656;
      border: 1px solid #ff5656 !important;
      border-radius: 0 20px 20px 0;
    }

    .bk-word-preview {
      color: #c4c6cc;
      border-color: #c4c6cc !important;
      border-radius: 0 20px 20px 0;
    }
  }

  .bk-icon-status {
    position: absolute;
    top: 10px;
    right: 6px;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    color: #fff;
    font-size: 12px;
    background-color: #3a84ff;

    .bk-icon {
      position: absolute;
      top: 2px;
      right: 1px;
      font-size: 18px;
    }

    img {
      position: absolute;
      top: 4px;
      right: 4px;
      width: 12px;
    }
  }

  .bk-icon-success {
    background-color: #2dcb56;
  }

  .bk-icon-error {
    background-color: #ff5656;
  }
}

.bk-rotation {
  @include rotation;
}
</style>
