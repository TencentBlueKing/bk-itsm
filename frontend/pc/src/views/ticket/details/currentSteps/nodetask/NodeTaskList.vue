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
  <div class="node-task-list">
    <div class="task-header">
      <span class="task-title">{{ $t(`m.task['任务列表']`) }}</span>
      <template v-if="nodeInfo.can_create_task">
        <bk-button
          theme="primary"
          :title="$t(`m.task['创建任务']`)"
          icon="plus"
          size="small"
          class="ml20"
          :disabled="nodeInfo.action_type === 'DISTRIBUTE'"
          @click="onCreateTaskClick"
        >
          {{ $t(`m.task['创建任务']`) }}
        </bk-button>
        <bk-button
          :title="$t(`m.task['从任务库创建']`)"
          size="small"
          class="ml10"
          :disabled="nodeInfo.action_type === 'DISTRIBUTE'"
          @click="onCreateByTaskLibrary"
        >
          {{ $t(`m.task['从任务库创建']`) }}
        </bk-button>
      </template>
      <span class="header-right-content">
        <bk-popover
          ref="taskLibraryPopover"
          placement="bottom-start"
          trigger="manual"
          ext-cls="save-template-pop"
          theme="light"
          :tippy-options="{
            hideOnClick: false
          }"
        >
          <bk-button
            v-if="nodeInfo.can_create_task"
            :title="$t(`m.tickets['存入任务库']`)"
            size="small"
            class="mr10"
            :disabled="nodeInfo.action_type === 'DISTRIBUTE'"
            @click="$refs.taskLibraryPopover.showHandler()"
          >
            {{ $t(`m.tickets['存入任务库']`) }}
          </bk-button>
          <div
            slot="content"
            style="width: 294px"
            class="task-library-manage-panel"
          >
            <task-library-opt-panel
              :task-list="taskList"
              :ticket-info="ticketInfo"
              @close="$refs.taskLibraryPopover.hideHandler()"
            ></task-library-opt-panel>
          </div>
        </bk-popover>
        <span
          class="refresh-tasks-icon"
          @click="refreshTaskList('refreshBtn')"
        >
          <i class="bk-icon icon-refresh"></i>
        </span>
      </span>
    </div>
    <div class="task-list-content">
      <bk-table
        v-bkloading="{ isLoading: isListLoading }"
        :data="taskList"
        :size="'small'"
      >
        <bk-table-column :label="$t(`m.task['顺序']`)" :width="60">
          <template slot-scope="props">
            <bk-input
              v-if="edittingOrderId === props.row.id"
              v-model="props.row.editOrder"
              v-bk-focus
              @blur="onEditOrderBlur(props.row)"
            ></bk-input>
            <span
              v-else
              class="task-order"
              @click="onTaskOrderClick(props.row)"
            >
              {{ props.row.order }}
            </span>
            <!-- <i class="bk-itsm-icon icon-itsm-icon-sops" v-if="props.row.component_type === 'SOPS'"></i> -->
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.task['任务名称']`)">
          <template slot-scope="props">
            <span
              v-bk-tooltips.top="props.row.name"
              class="task-name"
            >
              {{ props.row.name || "--" }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.task['处理人']`)">
          <template slot-scope="props">
            <span v-bk-tooltips.top="props.row.processor_users">
              {{ props.row.processor_users || "--" }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.task['任务类型']`)">
          <template slot-scope="props">
            <span v-bk-tooltips.top="props.row.processor_users">
              {{
                getTaskTypeName(props.row.component_type) ||
                  "--"
              }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.task['状态']`)" :wdith="120">
          <template slot-scope="props">
            <!-- 任务状态组件 -->
            <task-status :status="props.row.status"></task-status>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.task['操作']`)" min-width="140">
          <template slot-scope="props">
            <template
              v-for="(opt, index) in operatingMap[
                props.row.status
              ]"
            >
              <bk-button
                v-if="opt === 'edit'"
                :key="index"
                theme="primary"
                text
                :disabled="!nodeInfo.can_create_task"
                @click="onTaskEditClick(props.row)"
              >
                {{ $t(`m.task['编辑']`) }}
              </bk-button>
              <bk-button
                v-if="opt === 'delete'"
                :key="index"
                theme="primary"
                text
                @click="onTaskDeleteClick(props.row)"
              >
                {{ $t(`m.user['删除']`) }}
              </bk-button>
              <bk-button
                v-if="opt === 'deal'"
                :key="index"
                theme="primary"
                text
                :disabled="
                  !nodeInfo.can_execute_task ||
                    !props.row.can_process ||
                    props.row.status === 'QUEUE'
                "
                @click="dealTaskSlider(props.row, 'OPERATE')"
              >
                <template v-if="!props.row.can_process">
                  <span
                    v-bk-tooltips.top="
                      $t(`m.task['无处理权限']`)
                    "
                  >
                    {{ $t(`m.task['处理']`) }}
                  </span>
                </template>
                <template
                  v-else-if="props.row.status === 'QUEUE'"
                >
                  <span
                    v-bk-tooltips.top="
                      $t(`m.task['请先处理前置任务']`)
                    "
                  >
                    {{ $t(`m.task['处理']`) }}
                  </span>
                </template>
                <template v-else>
                  {{ $t(`m.task['处理']`) }}
                </template>
              </bk-button>
              <bk-button
                v-if="
                  opt === 'to_deal_sops' &&
                    props.row.component_type === 'SOPS'
                "
                :key="index"
                theme="primary"
                text
                @click="onJumpToSopsClick(props.row)"
              >
                {{ $t(`m.task['处理']`) }}
              </bk-button>
              <bk-button
                v-if="opt === 'confiam'"
                :key="index"
                :disabled="!props.row.can_process"
                theme="primary"
                text
                @click="dealTaskSlider(props.row, 'CONFIRM')"
              >
                {{ $t(`m.task['总结']`) }}
              </bk-button>
              <bk-button
                v-if="opt === 'view'"
                :key="index"
                theme="primary"
                text
                @click="dealTaskSlider(props.row, 'SEE')"
              >
                {{ $t(`m.task['查看']`) }}
              </bk-button>
            </template>
            <i
              v-if="isShowJumpIcon(props.row)"
              v-bk-tooltips="
                props.row.component_type === 'DEVOPS'
                  ? $t(`m.tickets['前往蓝盾']`)
                  : $t(`m.tickets['前往标准运维']`)
              "
              class="bk-itsm-icon icon-itsm-icon-three-seven icon-open-sops"
              @click.stop="onJumpToSopsClick(props.row)"
            ></i>
          </template>
        </bk-table-column>
      </bk-table>
    </div>
    <bk-sideslider
      :is-show.sync="createInfo.isShow"
      :title="
        createInfo.isAdd
          ? $t(`m.task['创建任务']`)
          : this.$t(`m.task['编辑任务']`)
      "
      :quick-close="true"
      :before-close="
        () => {
          closeSideslider('newTask');
        }
      "
      :width="800"
    >
      <div slot="content" style="min-height: 300px">
        <new-task
          v-if="createInfo.isShow"
          ref="newTask"
          :node-info="nodeInfo"
          :basic-infomation="ticketInfo"
          :item-content="createInfo.taskInfo"
          @closeSlider="createInfo.isShow = false"
          @getTaskList="getTaskList"
        ></new-task>
      </div>
    </bk-sideslider>
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
          :show-status="true"
          @close-slider="dealTaskInfo.show = false"
        >
          <div
            v-if="isShowJumpIcon(dealTaskInfo.itemContent)"
            slot="right-content"
            class="jump-to-other-system"
            @click.stop="
              onJumpToSopsClick(dealTaskInfo.itemContent)
            "
          >
            <i
              class="bk-itsm-icon icon-itsm-icon-three-seven icon-open-sops"
            ></i>
            <span
              v-if="
                dealTaskInfo.itemContent.component_type ===
                  'SOPS'
              "
            >
              {{ $t(`m.tickets['前往标准运维查看详情']`) }}
            </span>
            <span
              v-if="
                dealTaskInfo.itemContent.component_type ===
                  'DEVOPS'
              "
            >
              {{ $t(`m.tickets['前往蓝盾流水线查看详情']`) }}
            </span>
          </div>
        </task-handle-trigger>
      </div>
      <div
        slot="content"
        v-bkloading="{ isLoading: dealTaskInfo.addLoading }"
        style="height: 100%"
      >
        <template v-if="dealTaskInfo.show">
          <!-- 查看蓝盾任务执行信息 -->
          <devops-execut-info
            v-if="
              dealTaskInfo.itemContent.component_type ===
                'DEVOPS' &&
                ['RUNNING', 'FINISHED', 'FAILED'].includes(
                  dealTaskInfo.itemContent.status
                ) &&
                dealTaskInfo.type === 'SEE'
            "
            :task-info="dealTaskInfo.itemContent"
          ></devops-execut-info>
          <!-- 所有任务的处理、总结、查看 -->
          <deal-task
            v-else
            :deal-type="dealTaskInfo.type"
            :task-info="dealTaskInfo.itemContent"
            :basic-infomation="ticketInfo"
            @close="dealTaskInfo.show = false"
            @dealSuccess="dealSuccess"
          ></deal-task>
        </template>
      </div>
    </bk-sideslider>
    <!-- 任务库创建任务 -->
    <bk-sideslider
      :is-show.sync="taskLibrary.show"
      :title="$t(`m.tickets['从任务库创建任务']`)"
      :before-close="
        () => {
          closeSideslider('taskLibrary');
        }
      "
      :quick-close="true"
      :width="800"
    >
      <div slot="content" style="min-height: 300px">
        <task-library
          ref="taskLibrary"
          v-if="taskLibrary.show"
          :ticket-info="ticketInfo"
          :node-info="nodeInfo"
          @close="handleTaskLibraryClose"
        ></task-library>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import { errorHandler } from '@/utils/errorHandler';
  import newTask from '../../taskInfo/newTask.vue';
  import dealTask from '../../taskInfo/dealTask.vue';
  import TaskStatus from './TaskStatus.vue';
  import taskHandleTrigger from '../../taskInfo/taskHandleTrigger.vue';
  import DevopsExecutInfo from './DevopsExecutInfo.vue';
  import TaskLibrary from './TaskLibrary.vue';
  import TaskLibraryOptPanel from './TaskLibraryOptPanel.vue';
  import { TASK_TEMPLATE_TYPES } from '@/constants/task.js';

  export default {
    name: 'NodeTaskList',
    inject: ['reload'],
    components: {
      TaskStatus,
      newTask,
      dealTask,
      TaskLibrary,
      taskHandleTrigger,
      DevopsExecutInfo,
      TaskLibraryOptPanel,
    },
    props: {
      ticketInfo: {
        type: Object,
        default: () => ({}),
      },
      nodeInfo: {
        type: Object,
        default: () => ({}),
      },
    },
    data() {
      return {
        refreshing: false,
        edittingOrderId: '',
        taskLibrary: {
          show: false,
        },
        // 创建/编辑任务
        createInfo: {
          isShow: false,
          isAdd: true,
          taskInfo: {},
          bk_biz_id: '',
        },
        // 处理任务
        dealTaskInfo: {
          show: false,
          title: this.$t('m.task[\'处理任务\']'),
          loading: false,
          itemContent: {},
          type: '',
        },
        // 查看/处理任务
        viewTask: {
          isShow: false,
          isView: true,
          taskInfo: {},
        },
        isListLoading: false,
        // 状态对应操作列表
        operatingMap: {
          NEW: ['edit', 'delete', 'view'],
          QUEUE: ['deal', 'view'],
          WAITING_FOR_OPERATE: ['deal', 'view'],
          WAITING_FOR_BACKEND: ['view'],
          RUNNING: ['view'],
          WAITING_FOR_CONFIRM: ['confiam', 'view'],
          FINISHED: ['view'],
          FAILED: ['to_deal_sops', 'view'],
          DELETED: [],
          REVOKED: ['view'],
          SUSPENDED: ['view'],
        },
        taskList: [],
        taskTemplateTypes: TASK_TEMPLATE_TYPES,
      };
    },
    mounted() {
      this.refreshTaskList();
    },
    methods: {
      closeSideslider(type) {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m["内容未保存，离开将取消操作！"]'),
          confirmLoading: true,
          confirmFn: () => {
            this.createInfo.isShow = false;
            this.taskLibrary.show = false;
          },
          cancelFn: () => {
            if (type === 'newTask') {
              this.createInfo.isShow = true;
            } else {
              this.taskLibrary.show = true;
            }
          },
        });
      },
      // 获取任务列表
      getTaskList(source) {
        const params = {
          ticket_id: this.ticketInfo.id,
        };
        return this.$store
          .dispatch('taskFlow/getTaskList', params)
          .then((res) => {
            this.taskList = res.data;
            this.taskList.forEach((item) => {
              this.$set(item, 'editOrder', item.order);
            });
            // 如果当前的状态为QUEUE、RUNNING、WAITING_FOR_XXX则轮询,否则为处理完成状态,需刷新单据
            const loopStatusList = [
              'QUEUE',
              'RUNNING',
              'WAITING_FOR_OPERATE',
              'WAITING_FOR_BACKEND',
              'WAITING_FOR_CONFIRM',
            ];
            if (
              !res.data.some(task => loopStatusList.includes(task.status))
              && source === 'refreshBtn'
            ) {
              this.reload();
            }
            // 轮询
            if (
              res.data.some(task => loopStatusList.includes(task.status))
            ) {
              const setTimeoutFunc = setTimeout(() => {
                this.getTaskList(source);
              }, 10000);
              this.$once('hook:beforeDestroy', () => {
                clearInterval(setTimeoutFunc);
              });
            }
          })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 同步标准运维状态
      syncSopsTaskStatus() {
        return this.$store.dispatch('taskFlow/syncSopsTaskStatus', {
          ticket_id: this.ticketInfo.id,
        });
      },
      // 刷新任务列表
      async refreshTaskList(source = 'init') {
        if (this.isListLoading) {
          return;
        }
        this.isListLoading = true;
        await this.syncSopsTaskStatus();
        await this.getTaskList(source);
        this.isListLoading = false;
      },
      // 创建任务
      onCreateTaskClick() {
        this.createInfo = {
          isShow: true,
          isAdd: true,
          taskInfo: {},
          bk_biz_id: this.ticketInfo.bk_biz_id,
        };
      },
      // 编辑任务
      onTaskEditClick(row) {
        this.createInfo = {
          isShow: true,
          isAdd: false,
          taskInfo: row,
          bk_biz_id: this.ticketInfo.bk_biz_id,
        };
      },
      // 删除任务
      onTaskDeleteClick(row) {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.task[\'确认删除任务？\']'),
          subTitle: this.$t('m.task[\'任务如果被删除，与任务相关的触发动作将会一并删除。\']'),
          confirmFn: () => {
            const { id } = row;
            this.$store
              .dispatch('taskFlow/deleteTask', id)
              .then(() => {
                this.$bkMessage({
                  message: this.$t('m.task[\'删除成功\']'),
                  theme: 'success',
                });
                this.getTaskList();
              })
              .catch((res) => {
                errorHandler(res, this);
              });
          },
        });
      },
      // 处理任务
      dealTaskSlider(item, type) {
        this.dealTaskInfo.itemContent = item;
        this.dealTaskInfo.type = type;
        const typeObject = {
          SEE: this.$t('m.task[\'查看任务\']'),
          OPERATE: this.$t('m.task[\'处理任务\']'),
          CONFIRM: this.$t('m.task[\'总结任务\']'),
          RETRY: this.$t('m.task[\'重试任务\']'),
        };
        this.dealTaskInfo.title = typeObject[type];
        this.dealTaskInfo.show = true;
      },
      // 处理任务成功回调
      dealSuccess() {
        this.dealTaskInfo.show = false;
        this.getTaskList();
        this.$emit('updateCurrentStep');
      },
      // 跳转到标准运维
      onJumpToSopsClick(row) {
        window.open(row.task_url);
      },
      // 编辑顺序
      onEditOrderBlur(row) {
        const params = {
          order: Number(row.editOrder),
        };
        this.$store
          .dispatch('taskFlow/editorTask', { params, id: row.id })
          .then(() => {
            row.order = Number(row.editOrder);
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.edittingOrderId = '';
          });
      },
      // 查看任务
      onViewTaskClick(row, type) {
        this.viewTask = {
          isShow: true,
          isView: type !== 'deal',
          taskInfo: row,
          bk_biz_id: this.ticketInfo.bk_biz_id,
        };
      },
      onTaskOrderClick(row) {
        if (row.status !== 'NEW') {
          return false;
        }
        this.edittingOrderId = row.id;
      },
      handleSubmitSuccess() {
        this.createInfo.isShow = false;
        this.getTaskList();
      },
      getTaskTypeName(type) {
        const target = this.taskTemplateTypes.find(m => m.type === type);
        return target ? target.name : type;
      },
      isShowJumpIcon(taskInfo) {
        return (
          !['NEW', 'WAITING_FOR_CONFIRM', 'FINISHED', 'DELETED'].includes(taskInfo.status)
          && ['SOPS', 'DEVOPS'].includes(taskInfo.component_type)
          && taskInfo.component_type === 'DEVOPS'
          && taskInfo.status !== 'WAITING_FOR_OPERATE'
        );
      },
      onCreateByTaskLibrary() {
        this.taskLibrary.show = true;
      },
      // 关闭任务库弹窗
      handleTaskLibraryClose(refech) {
        this.taskLibrary.show = false;
        if (refech) {
          this.refreshTaskList();
        }
      },
    },
  };
</script>

<style lang="scss" scoped>
.node-task-list {
    margin-bottom: 20px;
    .task-header {
        margin-bottom: 10px;
        font-size: 14px;
        color: #63656e;
        .task-title {
            position: relative;
            // &::after {
            //     position: absolute;
            //     right: -15px;
            //     top: 3px;
            //     content: '*';
            //     color: #ea3636;
            // }
        }
        .header-right-content {
            float: right;
        }
        .refresh-tasks-icon {
            cursor: pointer;
            font-size: 16px;
            color: #699df4;
        }
    }

    .task-list-content {
        .icon-itsm-icon-sops {
            position: absolute;
            top: 0;
            left: 0;
            font-size: 22px;
            color: #979ba5;
        }
        .task-order {
            display: inline-block;
            width: 30px;
            cursor: pointer;
            &:hover {
                background-color: #dcdee5;
            }
        }
        .icon-open-sops {
            margin-left: 8px;
            display: inline-block;
            color: #699df4;
            font-size: 16px;
            vertical-align: middle;
            cursor: pointer;
        }
    }
}
.jump-to-other-system {
    padding-right: 15px;
    font-size: 12px;
    color: #3a84ff;
    cursor: pointer;
}
</style>
