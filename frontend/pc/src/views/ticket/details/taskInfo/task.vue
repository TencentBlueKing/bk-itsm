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
  <div class="bk-task">
    <div class="task-header">
      <template v-if="basicInfomation.can_create_task">
        <bk-dropdown-menu
          class="bk-dropdown-menu-cus"
          trigger="click"
          @show="dropdownShow = true"
          @hide="dropdownShow = false"
        >
          <bk-button
            slot="dropdown-trigger"
            v-bk-tooltips="$t(`m.task['点击创建任务']`)"
          >
            <span>{{ $t(`m.task['新建任务']`) }}</span>
            <i
              :class="[
                'bk-icon icon-angle-down',
                { 'icon-flip': dropdownShow }
              ]"
            ></i>
          </bk-button>
          <ul
            class="bk-dropdown-list bk-dropdown-list-cus"
            slot="dropdown-content"
          >
            <li>
              <a
                href="javascript:;"
                :class="{
                  'list-a-disable':
                    !basicInfomation.can_create_task
                }"
                @click="newTaskSlider({})"
              >
                {{ $t(`m.task['直接创建']`) }}
              </a>
            </li>
            <li>
              <a
                href="javascript:;"
                :class="{
                  'list-a-disable': !libraryList.length
                }"
                @click="newTaskLibrary"
              >
                {{ $t(`m.task['从任务库创建']`) }}
              </a>
            </li>
          </ul>
        </bk-dropdown-menu>
        <div
          class="bk-task-library"
          :class="{ 'bk-task-disabled': !taskList.length }"
          v-bk-tooltips.top="$t(`m.task['将任务列表保存为任务库']`)"
          @click="openLibrary"
        >
          <i class="bk-itsm-icon icon-task-library-line"></i>
          <div class="bk-library-content" v-if="libraryShow">
            <p class="bk-library-name">
              {{ $t(`m.task['任务库名称']`) }}
            </p>
            <p class="bk-library-input">
              <bk-input
                :clearable="true"
                v-model="libraryName"
              ></bk-input>
            </p>
            <p class="bk-library-btn">
              <span @click.stop="submitLibrary">{{
                $t(`m.task['确认']`)
              }}</span>
              <span @click.stop="closeLibrary">{{
                $t(`m.task['取消']`)
              }}</span>
            </p>
          </div>
        </div>
      </template>
      <div
        class="bk-task-my"
        :class="{ 'bk-task-float': !basicInfomation.can_create_task }"
      >
        <bk-checkbox
          :true-value="trueStatus"
          :false-value="falseStatus"
          v-model="myTask"
          @change="getTaskList"
        >
          <span style="font-size: 12px">{{
            $t(`m.task['仅显示我的任务']`)
          }}</span>
        </bk-checkbox>
      </div>
    </div>
    <div class="task-table">
      <bk-table
        v-bkloading="{ isLoading: listLoading }"
        :data="taskList"
        :size="'small'"
        ext-cls="task-table-wrap"
        @sort-change="orderingClick"
      >
        <bk-table-column
          :label="$t(`m.task['顺序']`)"
          :min-width="minWidth"
          :sortable="'custom'"
        >
          <template slot-scope="props">
            <template v-if="!basicInfomation.can_create_task">
              <span :title="props.row.order">{{
                props.row.order
              }}</span>
            </template>
            <template v-else>
              <template v-if="props.row.orderStatus">
                <span
                  class="bk-task-order"
                  @click="changeOrderStatus(props.row)"
                >{{ props.row.order }}</span
                >
              </template>
              <template v-else>
                <bk-input
                  style="display: inline-block; width: 60px"
                  type="number"
                  :min="0"
                  :precision="precision"
                  v-model="props.row.orderInfo"
                >
                </bk-input>
                <p class="order-opt-btns">
                  <span
                    class="submit-btn"
                    @click="submitOrder(props.row)"
                  >{{ $t(`m.task['确认']`) }}</span
                  >
                  <span
                    class="cancel-btn"
                    @click="closeOrder(props.row)"
                  >{{ $t(`m.task['取消']`) }}</span
                  >
                </p>
              </template>
            </template>
            <i
              class="bk-itsm-icon icon-itsm-icon-sops"
              v-if="props.row.component_type !== 'NORMAL'"
            ></i>
          </template>
        </bk-table-column>
        <!-- </template> -->
        <bk-table-column :label="$t(`m.task['任务名称']`)">
          <template slot-scope="props">
            <span
              v-bk-tooltips.top="props.row.name"
              class="task-name"
              @click="dealTaskSlider(props.row, 'SEE')"
            >
              {{ props.row.name || "--" }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.task['处理人']`)">
          <template slot-scope="props">
            <span v-bk-tooltips.top="props.row.processor_users">{{
              props.row.processor_users || "--"
            }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.task['状态']`)">
          <template slot-scope="props">
            <span
              class="bk-status-color-info"
              :class="{
                'bk-status-over':
                  props.row.status === 'FINISHED',
                'bk-status-summary':
                  props.row.status === 'WAITING_FOR_CONFIRM',
                'bk-status-error':
                  props.row.status === 'FAILED'
              }"
              v-for="(status, statusIndex) in statusList"
              :key="statusIndex"
              v-if="props.row.status === status.key"
              :title="status.name"
            >
              {{ status.name }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.task['操作']`)" min-width="120">
          <template slot-scope="props">
            <bk-button
              theme="primary"
              text
              @click="newTaskSlider(props.row)"
              v-if="
                props.row.status === 'NEW' &&
                  basicInfomation.can_create_task
              "
            >
              {{ $t(`m.task['编辑']`) }}
            </bk-button>
            <bk-button
              theme="primary"
              text
              v-if="
                !(
                  basicInfomation.can_create_task ||
                  basicInfomation.can_execute_task
                )
              "
              @click="dealTaskSlider(props.row, 'SEE')"
            >
              {{ $t(`m.task['查看']`) }}
            </bk-button>
            <template v-if="basicInfomation.can_execute_task">
              <bk-button
                theme="primary"
                text
                @click="dealTaskSlider(props.row, 'OPERATE')"
                v-if="
                  props.row.status === 'WAITING_FOR_OPERATE'
                "
                :disabled="!props.row.can_process"
              >
                <template v-if="!props.row.can_process">
                  <span
                    v-bk-tooltips.top="
                      $t(`m.task['无处理权限']`)
                    "
                  >{{ $t(`m.task['处理']`) }}</span
                  >
                </template>
                <template v-else>
                  {{ $t(`m.task['处理']`) }}
                </template>
              </bk-button>
              <bk-button
                theme="primary"
                text
                v-if="
                  props.row.status ===
                    'WAITING_FOR_BACKEND' ||
                    props.row.status === 'RUNNING'
                "
                @click="dealTaskSlider(props.row, 'SEE')"
              >
                {{ $t(`m.task['处理中']`) }}
              </bk-button>
              <bk-button
                theme="primary"
                text
                @click="dealTaskSlider(props.row, 'OPERATE')"
                v-if="props.row.status === 'QUEUE'"
                disabled
              >
                <span
                  v-bk-tooltips.top="
                    $t(`m.task['请先处理前置任务']`)
                  "
                >{{ $t(`m.task['处理']`) }}</span
                >
              </bk-button>
              <bk-button
                theme="primary"
                text
                @click="dealTaskSlider(props.row, 'CONFIRM')"
                v-if="
                  props.row.status === 'WAITING_FOR_CONFIRM'
                "
                :disabled="!props.row.can_process"
              >
                <template v-if="!props.row.can_process">
                  <span
                    v-bk-tooltips.top="
                      $t(`m.task['无处理权限']`)
                    "
                  >{{ $t(`m.task['总结']`) }}</span
                  >
                </template>
                <template v-else>
                  {{ $t(`m.task['总结']`) }}
                </template>
              </bk-button>
            </template>
            <!-- 重试和忽略 -->
            <template v-if="props.row.status === 'FAILED'">
              <bk-button
                theme="primary"
                text
                @click="dealTaskSlider(props.row, 'RETRY')"
              >
                {{ $t(`m.task['重试']`) }}
              </bk-button>
              <bk-button
                theme="primary"
                text
                @click="ignoreTask(props.row)"
              >
                {{ $t(`m.task['忽略']`) }}
              </bk-button>
            </template>
            <bk-button
              theme="primary"
              v-if="props.row.status === 'NEW'"
              text
              @click="deleteTask(props.row)"
            >
              {{ $t('m.user["删除"]') }}
            </bk-button>
          </template>
        </bk-table-column>
      </bk-table>
    </div>
    <bk-sideslider
      :is-show.sync="taskInfo.show"
      :quick-close="true"
      :title="taskInfo.title"
      :width="taskInfo.width"
    >
      <div
        slot="content"
        v-bkloading="{ isLoading: taskInfo.addLoading }"
        style="min-height: 300px"
      >
        <new-task
          v-if="taskInfo.show"
          :basic-infomation="basicInfomation"
          :item-content="taskInfo.itemContent"
          @closeSlider="closeSlider"
          @getTaskList="getTaskList"
        >
        </new-task>
      </div>
    </bk-sideslider>
    <bk-sideslider
      :quick-close="true"
      :is-show.sync="dealTaskInfo.show"
      :width="dealTaskInfo.width"
    >
      <div slot="header">
        <task-handle-trigger
          v-if="dealTaskInfo.show"
          :task-info="dealTaskInfo.itemContent"
          :title="dealTaskInfo.title"
          @close-slider="dealTaskInfo.show = false"
        ></task-handle-trigger>
      </div>
      <div
        slot="content"
        v-bkloading="{ isLoading: dealTaskInfo.addLoading }"
        style="min-height: 300px"
      >
        <deal-task
          v-if="dealTaskInfo.show"
          :deal-type="dealTaskInfo.type"
          :task-info="dealTaskInfo.itemContent"
          :basic-infomation="basicInfomation"
          @close="closeTask"
          @dealSuccess="dealSuccess"
        >
        </deal-task>
      </div>
    </bk-sideslider>
    <bk-sideslider
      :is-show.sync="libraryInfo.show"
      :title="libraryInfo.title"
      :quick-close="true"
      :width="libraryInfo.width"
    >
      <div
        slot="content"
        v-bkloading="{ isLoading: libraryInfo.loading }"
      >
        <task-library
          v-if="libraryInfo.show"
          :ticket-id="basicInfomation.id"
          :basic-infomation="basicInfomation"
          @closeTaskLibrary="closeTaskLibrary"
          @getTaskList="getTaskList"
        >
        </task-library>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import newTask from './newTask.vue';
  import dealTask from './dealTask.vue';
  import taskLibrary from './taskLibrary.vue';
  import taskHandleTrigger from './taskHandleTrigger';
  import { errorHandler } from '@/utils/errorHandler';

  export default {
    name: 'task',
    components: {
      newTask,
      dealTask,
      taskLibrary,
      taskHandleTrigger,
    },
    props: {
      basicInfomation: {
        type: Object,
        default() {
          return {};
        },
      },
      nodeList: {
        type: Array,
        default() {
          return [];
        },
      },
    },
    data() {
      return {
        trueStatus: true,
        falseStatus: false,
        firstInitPage: true,
        precision: 0,
        minWidth: 180,
        // 新建任务
        taskInfo: {
          show: false,
          title: this.$t('m.task[\'新建任务\']'),
          addLoading: false,
          width: 660,
          itemContent: {},
        },
        // 头部数据
        dropdownShow: false,
        myTask: false,
        // 数据列表
        listLoading: false,
        taskList: [],
        // 状态列表
        statusList: [
          { key: 'NEW', name: this.$t('m.task[\'新\']') },
          { key: 'QUEUE', name: this.$t('m.task[\'待处理\']') },
          {
            key: 'WAITING_FOR_OPERATE',
            name: this.$t('m.task[\'待处理\']'),
          },
          {
            key: 'WAITING_FOR_BACKEND',
            name: this.$t('m.task[\'后台处理中\']'),
          },
          { key: 'RUNNING', name: this.$t('m.task[\'执行中\']') },
          {
            key: 'WAITING_FOR_CONFIRM',
            name: this.$t('m.task[\'待总结\']'),
          },
          { key: 'FINISHED', name: this.$t('m.task[\'已完成\']') },
          { key: 'FAILED', name: this.$t('m.deployPage[\'失败\']') },
        ],
        // 处理任务
        dealTaskInfo: {
          show: false,
          title: this.$t('m.task[\'处理任务\']'),
          loading: false,
          width: 660,
          itemContent: {},
          type: '',
        },
        // 任务库弹窗
        libraryList: [],
        libraryInfo: {
          show: false,
          title: this.$t('m.task[\'从任务库创建\']'),
          loading: false,
          width: 660,
        },
        libraryName: '',
        libraryShow: false,
      };
    },
    computed: {
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
      refreshTask() {
        return this.$store.state.taskFlow.refreshTask;
      },
    },
    watch: {
      refreshTask() {
        if (this.refreshTask) {
          this.getTaskList();
          this.getLibraryList();
        }
      },
    },
    mounted() {
      this.getTaskList();
      this.getLibraryList();
      // 轮询单据详情的数据
      clearInterval(this.$store.state.taskFlow.intervalInfo);
      this.$store.state.taskFlow.intervalInfo = setInterval(() => {
        this.intervalTask();
      }, 5000);
    },
    methods: {
      orderingClick(value) {
        this.taskList.sort(this.sortCompare('order', value.order));
      },
      sortCompare(prop, type) {
        return (obj1, obj2) => {
          let val1 = obj1[prop];
          let val2 = obj2[prop];
          if (!isNaN(Number(val1)) && !isNaN(Number(val2))) {
            val1 = Number(val1);
            val2 = Number(val2);
          }
          if (val1 < val2) {
            return type === 'ascending' ? -1 : 1;
          }
          if (val1 > val2) {
            return type === 'ascending' ? 1 : -1;
          }
          return 0;
        };
      },
      // 修改task任务（new）
      newTaskSlider(item) {
        if (!this.basicInfomation.can_create_task) {
          return;
        }
        this.taskInfo.itemContent = item;
        this.taskInfo.title = item.id
          ? this.$t('m.task[\'编辑任务\']')
          : this.$t('m.task[\'新建任务\']');
        this.taskInfo.show = true;
      },
      closeSlider() {
        this.taskInfo.show = false;
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
      closeTask() {
        this.dealTaskInfo.show = false;
      },
      // 获取任务列表表格
      getTaskList() {
        const params = {
          ticket_id: this.basicInfomation.id,
          username: this.myTask ? window.username : '',
        };
        this.listLoading = true;
        this.$store
          .dispatch('taskFlow/getTaskList', params)
          .then((res) => {
            this.taskList = res.data;
            this.taskList.forEach((item) => {
              this.$set(item, 'orderStatus', true);
              this.$set(item, 'orderInfo', item.order);
            });
            this.minWidth = 80;
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.listLoading = false;
            this.$store.commit('taskFlow/changeTaskStatus', false);
          });
      },
      intervalTask() {
        const params = {
          ticket_id: this.basicInfomation.id,
          username: this.myTask ? window.username : '',
        };
        this.$store
          .dispatch('taskFlow/getTaskList', params)
          .then((res) => {
            this.taskList.forEach((item) => {
              res.data.forEach((node) => {
                if (item.id === node.id) {
                  item.status = node.status;
                }
              });
            });
            // 如果当前的状态为QUEUE、RUNNING、WAITING_FOR_XXX则轮询
            const listInfo = [
              'QUEUE',
              'RUNNING',
              'WAITING_FOR_OPERATE',
              'WAITING_FOR_BACKEND',
              'WAITING_FOR_CONFIRM',
            ];
            if (
              !res.data.some(item => listInfo.some(node => node === item.status))
            ) {
              clearInterval(this.$store.state.taskFlow.intervalInfo);
              // 处理完成刷新工单状态
              if (res.data.length && !this.firstInitPage) {
                this.$emit('updateCurrentStep');
              }
            }
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.firstInitPage = false;
          });
      },
      // 删除列表数据
      deleteTask(item) {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.task[\'确认删除任务？\']'),
          subTitle: this.$t('m.task[\'任务如果被删除，与任务相关的触发动作将会一并删除。\']'),
          confirmFn: () => {
            const { id } = item;
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
              })
              .finally(() => {});
          },
        });
      },
      // 处理任务成功回调
      dealSuccess() {
        this.dealTaskInfo.show = false;
        this.getTaskList();
        this.$emit('updateCurrentStep');
      },
      // 忽略任务数据
      ignoreTask(item) {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.task[\'确认忽略任务？\']'),
          confirmFn: () => {
            const { id } = item;
            this.$store
              .dispatch('taskFlow/ignoreTask', id)
              .then(() => {
                this.$bkMessage({
                  message: this.$t('m.newCommon[\'成功\']'),
                  theme: 'success',
                });
                this.getTaskList();
              })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {});
          },
        });
      },
      // 改变处理顺序
      changeOrderStatus(value) {
        this.taskList.forEach((item) => {
          item.orderStatus = true;
        });
        value.orderStatus = false;
        this.minWidth = 180;
      },
      submitOrder(value) {
        const { id } = value;
        const params = {
          order: Number(value.orderInfo),
        };
        this.$store
          .dispatch('taskFlow/editorTask', { params, id })
          .then(() => {
            value.order = Number(value.orderInfo);
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            value.orderStatus = true;
            this.minWidth = 80;
          });
      },
      closeOrder(value) {
        const orderValue = this.taskList.filter(item => item.id === value.id)[0].order;
        value.orderInfo = orderValue;
        value.orderStatus = true;
        this.minWidth = 80;
      },
      // 从任务库创建
      newTaskLibrary() {
        if (!this.libraryList.length) {
          return;
        }
        this.libraryInfo.show = true;
      },
      closeTaskLibrary() {
        this.libraryInfo.show = false;
      },
      // 任务库名称
      openLibrary() {
        if (!this.taskList.length) {
          return;
        }
        this.libraryShow = true;
      },
      submitLibrary() {
        if (!this.libraryName) {
          return;
        }
        const params = {
          name: this.libraryName,
          tasks: this.taskList,
        };
        this.$store
          .dispatch('taskFlow/creatLibrary', params)
          .then(() => {
            this.$bkMessage({
              message: this.$t('m.task[\'任务库创建成功\']'),
              theme: 'success',
            });
            this.closeLibrary();
            this.getLibraryList();
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {});
      },
      closeLibrary() {
        this.libraryName = '';
        this.libraryShow = false;
      },
      // 获取任务库列表数据
      getLibraryList() {
        this.$store
          .dispatch('taskFlow/getLibraryList')
          .then((res) => {
            this.libraryList = res.data;
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {});
      },
    },
  };
</script>

<style scoped lang="scss">
@import "./taskLog";
@import "../../../scss/mixins/clearfix.scss";
@import "../../../scss/mixins/scroller";
@import "../../../scss/mixins/table.scss";

.bk-dropdown-menu-cus {
    float: left;
    /deep/ .bk-dropdown-content {
        overflow: visible;
    }
    .bk-dropdown-list-cus {
        max-height: 400px;
        .list-a-disable {
            color: #c4c6cc;
            background-color: #fafbfd;
            cursor: not-allowed;
        }
    }
}

.task-header {
    position: relative;
    height: 32px;
    .bk-task-library {
        float: left;
        position: relative;
        width: 32px;
        height: 32px;
        text-align: center;
        line-height: 30px;
        border: 1px solid #c4c6cc;
        background-color: #fff;
        color: #979ba5;
        font-size: 16px;
        cursor: pointer;
        margin-left: 9px;
        border-radius: 2px;
    }
    .bk-task-disabled {
        cursor: not-allowed;
    }
    .bk-library-content {
        position: absolute;
        top: 37px;
        left: -54px;
        padding: 10px;
        border: 1px solid #dcdee5;
        width: 230px;
        z-index: 10;
        background-color: #fff;
        cursor: auto;
        border-radius: 2px;
        .bk-library-name {
            line-height: 20px;
            color: #63656e;
            margin-bottom: 8px;
            font-size: 12px;
            text-align: left;
        }
        .bk-library-input {
            margin-bottom: 10px;
        }
        .bk-library-btn {
            color: #3a84ff;
            text-align: right;
            padding-right: 8px;
            font-size: 12px;
            span {
                margin-left: 8px;
                cursor: pointer;
            }
        }
    }
    .bk-task-my {
        float: right;
        line-height: 32px;
        font-size: 12px;
    }
    .bk-task-float {
        float: left;
    }
}

.task-table {
    margin-top: 12px;
    .bk-task-order {
        line-height: 26px;
        display: inline-block;
        width: 50px;
        padding-left: 5px;
        &:hover {
            background-color: #dcdee5;
            cursor: pointer;
        }
    }
    .icon-itsm-icon-sops {
        position: absolute;
        top: 0;
        left: 0;
        font-size: 22px;
        color: #979ba5;
    }
    .task-table-wrap {
        /deep/ .cell {
            white-space: nowrap !important;
        }
        .order-opt-btns {
            display: inline-block;
            font-size: 12px;
            .submit-btn {
                margin-right: 5px;
                margin-left: 5px;
                cursor: pointer;
                color: #3a84ff;
            }
            .cancel-btn {
                cursor: pointer;
                color: #3a84ff;
            }
        }
        .task-name {
            color: #3a84ff;
            cursor: pointer;
        }
    }
}
.bk-status-color-info {
    display: inline-block;
    padding: 0 4px;
    vertical-align: middle;
    min-width: 45px;
    max-width: 70px;
    height: 22px;
    line-height: 22px;
    border: 1px solid #3c96ff;
    border-radius: 2px;
    color: #3c96ff;
    font-size: 12px;
    text-align: center;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
}
.bk-status-over {
    color: #dcdee5;
    border: 1px solid #dcdee5;
}
.bk-status-summary {
    color: #2dcb56;
    border: 1px solid #2dcb56;
}
.bk-status-error {
    color: #ff5656;
    border: 1px solid #ff5656;
}

.v-enter,
.v-leave-to {
    height: 100px;
}

.v-enter-to,
.v-leave {
    height: auto;
}

.v-enter-active,
.v-leave-active {
    transition: all 0.5s ease;
}
</style>
