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
  <span
    v-if="info"
    class="node-status"
    :class="info.cls">
    <i class="status-icon" :class="info.icon"></i>
    <span class="node-status-text">{{ info.text }}</span>
  </span>
</template>

<script>

  export default {
    name: 'TaskStatus',
    props: {
      status: {
        type: String,
        default: '',
      },
      nodeType: {
        type: String,
      },
    },
    data() {
      return {
        info: '',
      };
    },
    watch: {
      status() {
        this.getStatusInfo();
      },
    },
    created() {
      this.getStatusInfo();
    },
    methods: {
      getStatusInfo() {
        const runningStatusMap = {
          APPROVAL: this.$t('m.task["等待审批中"]'),
          NORMAL: this.$t('m.task["等待处理中"]'),
        };
        const statusMap = {
          RUNNING: {
            cls: 'running',
            icon: 'bk-itsm-icon icon-icon-loading',
            text: runningStatusMap[this.nodeType] || this.$t('m.task["执行中"]'),
          },
          SUCCESS: {
            cls: 'success',
            icon: 'bk-icon icon-check-circle-shape',
            text: this.$t('m.task["执行成功"]'),
          },
          FAILED: {
            cls: 'failed',
            icon: 'bk-itsm-icon icon-itsm-icon-square-one',
            text: this.$t('m.task["执行失败"]'),
          },
        };
        this.info = statusMap[this.status] || '';
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
    .node-status {
        margin-left: 15px;
        font-size: 14px;
        .node-status-text {
            font-size: 12px;
        }
        &.success {
            color: #4EBB49;
        }
        &.running {
            color: #4C7CF4;
            .status-icon {
                display: inline-block;
                -webkit-transform: rotate(360deg);
                animation: rotation 1.5s linear infinite;
                -moz-animation: rotation 1.5s linear infinite;
                -webkit-animation: rotation 1.5s linear infinite;
                -o-animation: rotation 1.5s linear infinite;
            }
        }
        &.failed {
            color: #ea3536;
            font-size: 14px;
            // .status-icon {
            //     font-size: 12px;
            //     padding: 1px;
            //     color: #ffffff;
            //     background: #ea3536;
            //     // border-radius: 50%;
            // }
        }
    }
</style>
