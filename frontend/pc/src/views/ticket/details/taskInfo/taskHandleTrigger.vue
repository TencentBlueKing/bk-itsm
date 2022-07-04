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
  <div class="trigger-handle">
    <div class="left-content">
      <span class="handle-title mr10">{{ title }}</span>
      <task-status v-if="showStatus" ext-cls="mr30" :status="taskInfo.status" type="block"></task-status>
      <bk-dropdown-menu
        v-if="triggerList.length" @show="dropdownShow = true" @hide="dropdownShow = false">
        <bk-button slot="dropdown-trigger" :loading="gettingTriggers">
          <span>{{ $t('m.newCommon["更多操作"]') }}</span>
          <i :class="['bk-icon icon-angle-down',{ 'icon-flip': dropdownShow }]"></i>
        </bk-button>
        <ul slot="dropdown-content" class="bk-dropdown-list trigger-ul">
          <li v-for="(trigger, tIndex) in triggerList" :key="tIndex">
            <a href="javascript:;" @click="openTriggerDialog(trigger)">{{trigger.display_name}}</a>
          </li>
        </ul>
      </bk-dropdown-menu>
    </div>
    <div class="right-content">
      <slot name="right-content"></slot>
    </div>
    <ticket-trigger-dialog ref="triggerDialog" @init-info="refreshTicket"></ticket-trigger-dialog>
  </div>
</template>

<script>
  import TicketTriggerDialog from '@/components/ticket/TicketTriggerDialog.vue';
  import { errorHandler } from '@/utils/errorHandler';
  import taskStatus from '../currentSteps/nodetask/TaskStatus.vue';

  export default {
    name: 'taskHandleTrigger',
    components: {
      TicketTriggerDialog,
      taskStatus,
    },
    inject: ['reloadTicket'],
    props: {
      taskInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      title: {
        type: String,
        default: '',
      },
      showStatus: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        dropdownShow: false,
        gettingTriggers: true,
        triggerList: [],
      };
    },
    mounted() {
      this.getHandleList();
    },
    methods: {
      getHandleList() {
        const params = {
          source_id: this.taskInfo.id,
          source_type: 'task',
          operate_type: 'MANUAL',
        };
        this.$store.dispatch('trigger/getTaskHandleTriggers', params).then((res) => {
          this.triggerList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.gettingTriggers = false;
          });
      },
      openTriggerDialog(trigger) {
        this.$refs.triggerDialog.openDialog(trigger);
      },
      refreshTicket() {
        this.$emit('close-slider');
        this.reloadTicket();
      },
    },
  };
</script>

<style scoped lang='scss'>
    .trigger-handle{
        .left-content {
            float: left;
            display: flex;
            align-items: center;
        }
        .right-content {
            float: right;
        }
        .handle-title{
            color: #333C48;
            font-size: 16px;
        }
        .trigger-ul{
            line-height: normal;
            font-weight: normal;
        }
        /deep/ .bk-button{
            & span{
                font-size: 14px;
                font-weight: normal;
            }
        }
    }
</style>
