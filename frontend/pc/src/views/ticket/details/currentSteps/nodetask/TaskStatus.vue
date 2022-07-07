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
    :class="extCls"
    :title="statusMap[status].name"
    class="bk-status-color-info">
    <template v-if="type === 'text'">
      <span :class="['status-text', statusMap[status].cls]">{{ statusMap[status].name }}</span>
    </template>
    <span v-else-if="type === 'block'" :class="['status-block', statusMap[status].cls]">
      <i v-if="statusIcon === 'loading'" class="bk-itsm-icon icon-icon-loading"></i>
      <i v-else-if="statusIcon === 'success'" class="bk-itsm-icon icon-icon-finish"></i>
      <i v-else-if="statusIcon === 'failed'" class="bk-itsm-icon icon-itsm-icon-delete-fill"></i>
      <span :class="['status-text', statusMap[status].cls]">{{ statusMap[status].name }}</span>
    </span>
    <template v-else>
      <i v-if="['RUNNING', 'WAITING_FOR_BACKEND'].includes(status)" class="bk-itsm-icon icon-icon-loading"></i>
      <span v-else class="status-dot" :class="statusMap[status].cls"></span>
      {{ statusMap[status].name }}
    </template>
  </span>
</template>

<script>
  export default {
    name: 'TaskStatus',
    props: {
      status: {
        type: String,
      },
      extCls: {
        type: String,
        default: '',
      },
      type: {
        type: String,
        default: '',
      },
    },
    data() {
      return {
        // 状态列表
        statusMap: {
          NEW: { name: this.$t('m.task[\'新\']') },
          QUEUE: { name: this.$t('m.task[\'待处理\']') },
          WAITING_FOR_OPERATE: { name: this.$t('m.task[\'待处理\']'), cls: 'blue' },
          WAITING_FOR_BACKEND: { name: this.$t('m.task[\'后台处理中\']') },
          RUNNING: { name: this.$t('m.task[\'执行中\']'), cls: 'blue' },
          WAITING_FOR_CONFIRM: { name: this.$t('m.task[\'待总结\']'), cls: 'blue' },
          FINISHED: { name: this.$t('m.task[\'已完成\']'), cls: 'green' },
          FAILED: { name: this.$t('m.deployPage[\'失败\']'), cls: 'red' },
          DELETED: { name: this.$t('m.task[\'已删除\']') },
          REVOKED: { name: this.$t('m.task[\'已撤销\']'), cls: 'red' },
          SUSPENDED: { name: this.$t('m.task[\'已暂停\']'), cls: 'blue' },
        },
        statusIconMap: {
          loading: ['QUEUE', 'WAITING_FOR_OPERATE', 'WAITING_FOR_BACKEND', 'RUNNING', 'WAITING_FOR_CONFIRM'],
          success: ['FINISHED'],
          failed: ['FAILED', 'DELETED', 'REVOKED', 'SUSPENDED'],
          default: [],
        },
      };
    },
    computed: {
      statusIcon() {
        const keys = Object.keys(this.statusIconMap);
        for (let i = 0; i < keys.length; i++) {
          const val = this.statusIconMap[keys[i]];
          if (val.includes(this.status)) {
            return keys[i];
          }
        }
        return '';
      },
    },
  };
</script>

<style lang="scss" scoped>
@import '~@/scss/animation/rotation.scss';
$gray: #dcdee5;
$blue: #3a84ff;
$red: #ea3536;
$green: #2dcb56;
.bk-status-color-info {
    display: inline-block;
    vertical-align: middle;
    font-size: 12px;
    color: #63656E;
    .status-text {
        &.blue {
            color: $blue;
        }
        &.red {
            color: $red;
        }
        &.green {
            color: $green;
        }
    }
    .status-dot {
        margin-right: 6px;
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #dcdee5;
        &.blue {
            background: $blue;
        }
        &.red {
            background: $red;
        }
        &.green {
            background: $green;
        }
    }
    .bk-itsm-icon.icon-icon-loading {
        display: inline-block;
        @include rotation;
        font-size: 14px;
        color: #3A84FF;
    }
    .status-block {
        display: inline-block;
        height: 22px;
        line-height: 22px;
        overflow: hidden;
        vertical-align: middle;
        padding: 0 4px;
        background: #dcdee5;
        border-radius: 2px;
        > i {
            display: inline-block;
            vertical-align: middle;
            font-size: 17px;
        }
        &.blue {
            color: $blue;
            background: rgba($color: $blue, $alpha: 0.15);
        }
        &.red {
            color: $red;
            background: rgba($color: $red, $alpha: 0.15);
        }
        &.green {
            color: $green;
            background: rgba($color: $green, $alpha: 0.15);
        }
    }
}
</style>
