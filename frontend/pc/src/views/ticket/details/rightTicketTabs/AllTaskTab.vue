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
  <div class="all-task-list">
    <bk-table
      v-bkloading="{ isLoading: isListLoading }"
      :data="taskList"
      :size="'small'"
    >
      <bk-table-column :label="$t(`m.task['顺序']`)" :width="60">
        <template slot-scope="props">
          <span>{{ props.row.order || "--" }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.task['任务名称']`)" :render-header="$renderHeader" :show-overflow-tooltip="true">
        <template slot-scope="props">
          <span v-bk-tooltips.top="props.row.name" class="task-name">
            {{ props.row.name || "--" }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.task['处理人']`)" :render-header="$renderHeader" :show-overflow-tooltip="true">
        <template slot-scope="props">
          <span v-bk-tooltips.top="props.row.processor_users">{{
            props.row.processor_users || "--"
          }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.task['任务类型']`)" :render-header="$renderHeader" :show-overflow-tooltip="true">
        <template slot-scope="props">
          <span v-bk-tooltips.top="props.row.processor_users">{{
            getTaskTypeName(props.row.component_type) || "--"
          }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.task['状态']`)" :render-header="$renderHeader" :wdith="120" :show-overflow-tooltip="true">
        <template slot-scope="props">
          <!-- 任务状态组件 -->
          <task-status :status="props.row.status"></task-status>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.task['操作']`)" min-width="60">
        <template slot-scope="props">
          <bk-button
            theme="primary"
            text
            @click="onViewTask(props.row)"
          >
            {{ $t(`m.task['查看']`) }}
          </bk-button>
        </template>
      </bk-table-column>
      <div class="empty" slot="empty">
        <empty
          :is-error="listError"
          @onRefresh="getTaskList()">
        </empty>
      </div>
    </bk-table>
    <bk-sideslider
      :is-show.sync="dealTaskInfo.show"
      :quick-close="true"
      :width="800"
    >
      <div slot="header">
        <task-handle-trigger
          v-if="dealTaskInfo.show"
          :task-info="dealTaskInfo.itemContent"
          :title="dealTaskInfo.title"
          @close-slider="dealTaskInfo.show = false"
        ></task-handle-trigger>
      </div>
      <div slot="content" style="min-height: 300px">
        <deal-task
          v-if="dealTaskInfo.show"
          :deal-type="dealTaskInfo.type"
          :task-info="dealTaskInfo.itemContent"
          :basic-infomation="ticketInfo"
          @close="dealTaskInfo.show = false"
        >
        </deal-task>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import { errorHandler } from '@/utils/errorHandler';
  import TaskStatus from '../currentSteps/nodetask/TaskStatus.vue';
  import dealTask from '../taskInfo/dealTask.vue';
  import taskHandleTrigger from '../taskInfo/taskHandleTrigger.vue';
  import { TASK_TEMPLATE_TYPES } from '@/constants/task.js';
  import Empty from '../../../../components/common/Empty.vue';

  export default {
    name: '',
    components: {
      dealTask,
      TaskStatus,
      taskHandleTrigger,
      Empty,
    },
    props: {
      ticketInfo: {
        type: Object,
        default: () => ({}),
      },
    },
    data() {
      return {
        isListLoading: false,
        taskList: [],
        dealTaskInfo: {
          show: false,
          itemContent: {},
          title: this.$t('m.task[\'查看任务\']'),
          type: 'SEE',
        },
        taskTemplateTypes: TASK_TEMPLATE_TYPES,
        listError: false,
      };
    },
    mounted() {
      this.getTaskList();
    },
    methods: {
      // 获取任务列表
      getTaskList() {
        this.isListLoading = true;
        const params = {
          ticket_id: this.ticketInfo.id,
        };
        this.listError = false;
        return this.$store
          .dispatch('taskFlow/getTaskList', params)
          .then((res) => {
            this.taskList = res.data;
          })
          .catch((res) => {
            this.listError = true;
            errorHandler(res, this);
          })
          .finally(() => {
            this.isListLoading = false;
          });
      },
      onViewTask(row) {
        this.dealTaskInfo.show = true;
        this.dealTaskInfo.itemContent = row;
      },
      getTaskTypeName(type) {
        const target = this.taskTemplateTypes.find(m => m.type === type);
        return target ? target.name : type;
      },
    },
  };
</script>
<style lang="scss" scoped>
.all-task-list {
    width: 100%;
    height: 100%;
    .icon-itsm-icon-sops {
        position: absolute;
        top: 0;
        left: 0;
        font-size: 22px;
        color: #979ba5;
    }
}
</style>
