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
  <div class="deal-task">
    <!-- 基础信息 -->
    <div class="base-info">
      <h3 class="setion-title">{{ $t(`m.task['任务信息']`) }}</h3>
      <ul class="basic-list">
        <li
          class="basic-item"
          v-for="(item, index) in taskInfoList"
          :key="index"
        >
          <span class="basic-name">{{ item.name }}：</span>
          <span class="basic-value">
            <template v-if="item.key !== 'status'">
              {{ item.value }}
            </template>
            <template v-else>
              <task-status
                :status="taskInfo[item.key]"
                type="text"
              ></task-status>
            </template>
          </span>
        </li>
      </ul>
    </div>
    <!-- 标准运维执行基础信息 -->
    <div class="base-info mt30" v-if="isShowSopsExecInfo">
      <h3 class="setion-title">{{ $t(`m.task['标准运维信息']`) }}</h3>
      <ul
        class="basic-list"
        v-bkloading="{ isLoading: taskStatusInfoLoading }"
      >
        <li
          class="basic-item"
          v-for="(item, index) in sopsBaseList"
          :key="index"
        >
          <span class="basic-name">{{ item.name }}：</span>
          <span class="basic-value">
            <template v-if="item.key === 'task_name'">
              <a
                :href="taskStatusInfo.sops_task_url"
                target="_blank"
                style="color: #3a84ff"
              >
                {{ taskStatusInfo[item.key] || "--" }}
              </a>
            </template>
            <template v-else-if="item.key === 'state'">
              <span
                :class="
                  getSopsStatusInfo(taskStatusInfo.state)
                    .color
                "
              >
                {{
                  getSopsStatusInfo(taskStatusInfo.state).name
                }}
              </span>
              <i
                v-if="taskStatusInfo[item.key] !== 'FINISHED'"
                class="bk-icon left-icon icon-refresh"
                style="
                                    margin-left: 5px;
                                    cursor: pointer;
                                    font-size: 16px;
                                    color: #3a84ff;
                                "
                @click="getTaskStatusInfo"
              ></i>
            </template>
            <template v-else>
              {{ taskStatusInfo[item.key] || "--" }}
            </template>
          </span>
        </li>
      </ul>
    </div>

    <!-- 创建任务-基础字段信息-->
    <div class="field-info">
      <field-preview class="mb30" :fields="createFields"></field-preview>
    </div>
    <!-- 创建任务-特殊字段信息:标准运维/蓝盾... -->
    <div class="bk-field-info">
      <field-info
        v-if="createTaskTemplateFields.length"
        :fields="createTaskTemplateFields"
        :basic-infomation="basicInfomation"
        :disabled="true"
        :type-info="dealType"
      ></field-info>
    </div>

    <!-- 处理字段信息 -->
    <div
      class="base-info"
      v-if="
        taskInfo.status !== 'NEW' &&
          taskInfo.status !== 'WAITING_FOR_OPERATE'
      "
    >
      <h3 class="setion-title">{{ $t(`m.task['处理信息']`) }}</h3>
      <!-- 已处理 -->
      <template
        v-if="
          taskInfo.status === 'WAITING_FOR_CONFIRM' ||
            taskInfo.status === 'FINISHED'
        "
      >
        <ul class="basic-list">
          <li class="basic-item">
            <span class="basic-name">
              {{ $t(`m.task['处理人：']`) }}
            </span>
            <span
              class="basic-value"
              :title="
                taskDetail.executor ||
                  taskDetail.processor_users
              "
            >
              {{
                taskDetail.executor ||
                  taskDetail.processor_users
              }}
            </span>
          </li>
          <li class="basic-item">
            <span class="basic-name">
              {{ $t(`m.task['处理时间：']`) }}
            </span>
            <span class="basic-value" :title="taskDetail.start_at">
              {{ taskDetail.start_at || "--" }}
            </span>
          </li>
        </ul>
        <field-preview :fields="dealFields"></field-preview>
      </template>
      <!-- 未处理 -->
      <template v-else>
        <div
          class="bk-field-info mb30"
          v-bkloading="{ isLoading: taskDetailLoading }"
        >
          <!-- 查看的时候禁用表单,总结的时候也需要禁用表单 -->
          <field-info
            v-if="!taskDetailLoading"
            ref="fieldInfo"
            :fields="dealFields"
            :disabled="
              dealType === 'SEE' ||
                taskInfo.status === 'WAITING_FOR_CONFIRM' ||
                taskInfo.status === 'FINISHED'
            "
          ></field-info>
        </div>
      </template>
    </div>

    <!-- 总结信息 -->
    <div
      class="base-info mt30"
      v-if="
        (taskInfo.status === 'WAITING_FOR_CONFIRM' ||
          taskInfo.status === 'FINISHED') &&
          taskType !== 'DEVOPS'
      "
    >
      <h3 class="setion-title">{{ $t(`m.task['总结信息']`) }}</h3>
      <!-- 已总结 -->
      <template v-if="taskInfo.status === 'FINISHED'">
        <div class="bk-task-basic mb30">
          <field-preview :fields="confirmList"></field-preview>
          <ul class="basic-list">
            <li class="basic-item">
              <span class="basic-name">
                {{ $t(`m.task['总结人：']`) }}
              </span>
              <span
                class="basic-value"
                :title="
                  taskDetail.confirmer ||
                    taskDetail.processor_users
                "
              >
                {{
                  taskDetail.confirmer ||
                    taskDetail.processor_users
                }}
              </span>
            </li>
            <li class="basic-item">
              <span class="basic-name">
                {{ $t(`m.task['总结时间：']`) }}
              </span>
              <span
                class="basic-value"
                :title="taskDetail.end_at"
              >
                {{ taskDetail.end_at || "--" }}
              </span>
            </li>
          </ul>
          <div class="bk-field-info">
            <field-info
              v-if="confirmTaskTemplateFields.length"
              :fields="confirmTaskTemplateFields"
              :disabled="true"
            ></field-info>
          </div>
        </div>
      </template>
      <!-- 未总结 -->
      <template v-else>
        <div
          class="bk-field-info mb30"
          v-bkloading="{ isLoading: taskDetailLoading }"
        >
          <!-- 查看的时候禁用表单 -->
          <field-info
            v-if="!taskDetailLoading"
            ref="fieldInfo"
            :fields="confirmFields"
            :disabled="dealType === 'SEE'"
          ></field-info>
        </div>
      </template>
    </div>
    <div class="bk-submit-task" v-if="dealType !== 'SEE'">
      <!-- 查看的时候隐藏确认按钮 -->
      <bk-button
        :theme="'primary'"
        :title="confirmText"
        :disabled="btnLoading || taskDetailLoading"
        class="mr10"
        @click="submitDeal"
      >
        {{ confirmText }}
      </bk-button>
      <bk-button
        v-if="dealType === 'OPERATE' || dealType === 'CONFIRM'"
        :theme="'default'"
        :disabled="btnLoading"
        :title="$t(`m.task['取消']`)"
        @click="closeSideslider"
      >
        {{ $t(`m.task['取消']`) }}
      </bk-button>
    </div>
  </div>
</template>

<script>
  import i18n from '@/i18n/index.js';
  import apiFieldsWatch from '@/views/commonMix/api_fields_watch.js';
  import { TASK_TEMPLATE_TYPES } from '@/constants/task.js';
  import { errorHandler } from '../../../../utils/errorHandler';
  import taskStatus from '../currentSteps/nodetask/TaskStatus.vue';
  import fieldInfo from '@/views/managePage/billCom/fieldInfo.vue';
  import fieldPreview from '@/views/commonComponent/fieldPreview/index.vue';

  // 任务基础信息
  const baseTaskInfoList = [
    { key: 'component_type', name: i18n.t('m.task[\'任务类型\']'), value: '' },
    { key: 'name', name: i18n.t('m.task[\'任务名称\']'), value: '' },
    { key: 'status', name: i18n.t('m.task[\'状态\']'), value: '' },
    { key: 'processor_users', name: i18n.t('m.task[\'处理人\']'), value: '' },
    { key: 'create_at', name: i18n.t('m.task[\'创建时间\']'), value: '' },
  ];
  // 标准运维基础信息
  const sopsBaseList = [
    { key: 'task_name', name: i18n.t('m.task[\'任务名\']') },
    { key: 'state', name: i18n.t('m.task[\'状态\']') },
    { key: 'bk_biz_id', name: i18n.t('m.task[\'业务\']') },
    { key: 'creator', name: i18n.t('m.task[\'创建人\']') },
    { key: 'executor', name: i18n.t('m.task[\'执行人\']') },
    { key: 'create_time', name: i18n.t('m.task[\'创建时间\']') },
    { key: 'start_time', name: i18n.t('m.task[\'执行时间\']') },
    { key: 'finish_time', name: i18n.t('m.task[\'完成时间\']') },
  ];
  // 标准运维状态列表
  const sopsStateList = [
    {
      key: 'NOT_CREATED',
      name: i18n.t('m.task[\'未创建\']'),
      color: 'bk-status-over',
    },
    {
      key: 'CREATE_FAILED',
      name: i18n.t('m.task[\'创建失败\']'),
      color: 'bk-status-error',
    },
    {
      key: 'CREATED',
      name: i18n.t('m.task[\'创建成功\']'),
      color: 'bk-status-normal',
    },
    {
      key: 'START_FAILED',
      name: i18n.t('m.task[\'启动失败\']'),
      color: 'bk-status-error',
    },
    {
      key: 'RUNNING',
      name: i18n.t('m.task[\'执行中\']'),
      color: 'bk-status-normal',
    },
    {
      key: 'FAILED',
      name: i18n.t('m.task[\'执行失败\']'),
      color: 'bk-status-error',
    },
    {
      key: 'FINISHED',
      name: i18n.t('m.task[\'执行成功\']'),
      color: 'bk-status-summary',
    },
    {
      key: 'REVOKED',
      name: i18n.t('m.task[\'已撤销\']'),
      color: 'bk-status-over',
    },
    {
      key: 'SUSPENDED',
      name: i18n.t('m.task[\'已暂停\']'),
      color: 'bk-status-normal',
    },
  ];

  const specialFieldTypes = [
    'COMPLEX-MEMBERS', // 人员类型选择
    'SOPS_TEMPLATE', // 标准运维
    'DEVOPS_TEMPLATE', // 蓝盾
  ];
  export default {
    name: 'DealTask',
    components: {
      taskStatus,
      fieldInfo,
      fieldPreview,
    },
    mixins: [apiFieldsWatch],
    props: {
      taskInfo: {
        type: Object,
        default: () => ({}),
      },
      dealType: {
        type: String,
        default: '',
      },
      basicInfomation: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        baseTaskInfoList,
        sopsBaseList,
        sopsStateList,
        specialFieldTypes,
        btnLoading: false,
        taskStatusInfoLoading: false,
        taskDetailLoading: false,
        taskStatusInfo: {}, // 标准运维信息
        taskDetail: {}, // 任务详情信息
        createFields: [], // 创建-字段
        createTaskTemplateFields: [], // 创建-任务模板特有字段
        dealFields: [], // 执行-字段
        confirmFields: [], // 总结-字段
        confirmTaskTemplateFields: [], // 总结-任务模板特有字段
      };
    },
    computed: {
      taskType() {
        return this.taskInfo.component_type;
      },
      taskInfoList() {
        const list = this.baseTaskInfoList.map((item) => {
          if (item.key === 'component_type') {
            item.value = TASK_TEMPLATE_TYPES.find(m => m.type === this.taskType).name;
          } else {
            item.value = this.taskInfo[item.key];
          }
          return item;
        });
        if (['SOPS', 'DEVOPS'].includes(this.taskType)) {
          list.push({
            name: this.$t('m.task[\'任务模板\']'),
            value: this.taskInfo.task_schema_id,
          });
        }
        if (this.taskType === 'DEVOPS') {
          list.push({
            name: this.$t('m.tickets[\'流水线\']'),
            value: '',
          });
        }
        return list;
      },
      isShowSopsExecInfo() {
        return (
          this.taskType === 'SOPS'
          && (this.dealType === 'SEE'
          || this.taskInfo.status === 'WAITING_FOR_CONFIRM')
        );
      },
      confirmText() {
        return this.taskInfo.status === 'WAITING_FOR_OPERATE'
          && ['DEVOPS', 'SOPS'].includes(this.taskType)
          ? this.$t('m.tickets[\'执行\']')
          : this.$t('m.task[\'确认\']');
      },
    },
    created() {
      this.initData();
    },
    mounted() {},
    methods: {
      initData() {
        this.getTaskDetail();
        if (this.isShowSopsExecInfo) {
          this.getTaskStatusInfo();
        }
      },
      // 获取任务详情
      getTaskDetail() {
        this.taskDetailLoading = true;
        const { id } = this.taskInfo;
        this.$store
          .dispatch('taskFlow/getTaskInfo', id)
          .then((res) => {
            this.taskDetail = res.data;
            // 创建信息
            this.createFields = res.data.fields.create_fields.filter(item => !this.specialFieldTypes.includes(item.type));
            this.createTaskTemplateFields =                        res.data.fields.create_fields.filter(item => ['SOPS_TEMPLATE', 'DEVOPS_TEMPLATE'].includes(item.type));
            this.createTaskTemplateFields.forEach((item) => {
              this.$set(item, 'showFeild', true);
              this.$set(item, 'val', item.value || '');
            });
            this.isNecessaryToWatch(
              { fields: this.createFields },
              'submit'
            );

            // 处理信息
            this.dealFields = res.data.fields.operate_fields.filter(item => !this.specialFieldTypes.includes(item.type));
            this.dealFields.forEach((item) => {
              if (item.type === 'CASCADE') {
                item.type = 'SELECT';
              }
              this.$set(item, 'showFeild', true);
              this.$set(item, 'val', item.value || '');
            });
            this.isNecessaryToWatch(
              { fields: this.dealFields },
              'submit'
            );

            // 总结信息
            if (this.taskInfo.status === 'FINISHED') {
              this.confirmFields =                            res.data.fields.confirm_fields.filter(item => !this.specialFieldTypes.includes(item.type));
              this.confirmTaskTemplateFields =                            res.data.fields.confirm_fields.filter(item => ['SOPS_TEMPLATE', 'DEVOPS_TEMPLATE'].includes(item.type));
            } else {
              this.confirmFields =                            res.data.fields.confirm_fields.filter(item => item.type !== 'COMPLEX-MEMBERS');
            }
            this.confirmFields.forEach((item) => {
              if (item.type === 'CASCADE') {
                item.type = 'SELECT';
              }
              this.$set(item, 'showFeild', true);
              this.$set(item, 'val', item.value || '');
            });
            this.isNecessaryToWatch(
              { fields: this.confirmFields },
              'submit'
            );
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.taskDetailLoading = false;
          });
      },
      // 获取任务状态信息
      getTaskStatusInfo() {
        this.taskStatusInfoLoading = true;
        const { id } = this.taskInfo;
        this.$store
          .dispatch('taskFlow/getTaskStatusInfo', id)
          .then((res) => {
            this.taskStatusInfo = res.data;
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.taskStatusInfoLoading = false;
          });
      },
      getSopsStatusInfo(state) {
        const target = this.sopsStateList.find(m => m.key === state);
        return target || {};
      },
      closeSideslider() {
        this.$emit('close');
      },
      // 处理/总结 任务
      submitDeal() {
        if (this.$refs.fieldInfo && !this.$refs.fieldInfo.checkValue()) {
          return false;
        }

        const params = {
          action: this.dealType === 'OPERATE' ? 'operate' : 'confirm',
          fields: [],
        };
        let submitField = [];

        if (
          ['QUEUE', 'WAITING_FOR_OPERATE', 'RUNNING'].includes(this.taskInfo.status)
        ) {
          submitField = this.dealFields;
        } else if (this.taskInfo.status === 'WAITING_FOR_CONFIRM') {
          submitField = this.confirmFields;
        }

        submitField.forEach((item) => {
          if (item.type === 'SOPS_TEMPLATE') {
            item.sopsContent.constants.forEach((contentItem) => {
              this.$set(
                contentItem,
                'value',
                item.sopsContent.formData[contentItem.key]
              );
            });
            params.fields.push({
              key: item.key,
              value: {
                id: item.sopsContent.id,
                template_source: item.sopsContent.context.project
                  .bk_biz_id
                  ? 'business'
                  : 'common',
                bk_biz_id:
                  this.basicInfomation.bk_biz_id !== -1
                    ? this.basicInfomation.bk_biz_id
                    : '',
                constants: item.sopsContent.constants,
              },
            });
          } else {
            params.fields.push({
              key: item.key,
              value: item.value,
            });
          }
        });
        this.btnLoading = true;
        const { id } = this.taskInfo;
        this.$store
          .dispatch('taskFlow/dealTask', { params, id })
          .then(() => {
            this.$bkMessage({
              message: this.$t('m.task[\'操作任务成功\']'),
              theme: 'success',
            });
            // 刷新数据
            this.$emit('dealSuccess');
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.btnLoading = false;
          });
      },
    },
  };
</script>
<style lang="scss" scoped>
@import "~@/scss/mixins/form.scss";
.bk-status-normal {
    color: #3c96ff;
    border: 1px solid #3c96ff;
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
.deal-task {
    position: relative;
    padding: 24px 30px 48px 30px;
    min-height: 100%;
}
.bk-submit-task {
    position: absolute;
    bottom: 0;
    left: 0;
    padding: 8px 32px;
    width: 100%;
    background: #fafbfd;
}
</style>
