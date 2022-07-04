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
  <div class="devops-execut-info">
    <!-- v-if="status === 'RUNNING'" -->
    <div class="running-info" v-if="status === 'RUNNING'" v-bkloading="{ isLoading: taskStatusInfoLoading }">
      <i class="bk-itsm-icon icon-icon-loading"></i>
      <p class="run-info">{{ $t(`m.tickets['任务正在执行中，请稍等']`) }}</p>
      <p class="run-time">
        <span class="time-block">
          {{ $t(`m.tickets['已耗时：']`) }}
          {{ convertMStoString(taskStatusInfo.elapsed_time * 1000) }}
        </span>
      </p>
    </div>
    <!-- 执行成功/执行失败 -->
    <div class="execut-info" v-else>
      <!-- 任务信息 -->
      <div class="base-info">
        <h3 class="setion-title">{{$t(`m.task['任务信息']`)}}</h3>
        <ul class="basic-list" v-bkloading="{ isLoading: taskStatusInfoLoading }">
          <li class="basic-item" v-for="(item, index) in taskInfoList" :key="index">
            <span class="basic-name">{{ item.name }}：</span>
            <span class="basic-value">
              <template v-if="item.key !== 'status'">
                {{ item.value }}
              </template>
              <template v-else>
                <task-status :status="taskInfo[item.key]" type="text"></task-status>
              </template>
            </span>
          </li>
        </ul>
      </div>
      <!-- 执行情况 -->
      <div class="base-info mt30">
        <h3 class="setion-title">{{ $t(`m.tickets['执行情况']`) }}</h3>
        <ul class="basic-list" v-bkloading="{ isLoading: buildStatusLoading }">
          <li class="basic-item" v-for="(item, index) in displayExecutInfoList" :key="index">
            <span class="basic-name">{{ item.name }}：</span>
            <span class="basic-value">
              {{ item.value }}
            </span>
          </li>
        </ul>
      </div>
      <!-- 构件列表 -->
      <div class="base-info mt30">
        <h3 class="setion-title">{{ $t(`m.tickets['构件列表']`) }}</h3>
        <bk-table
          v-bkloading="{ isLoading: buildStatusLoading }"
          :data="buildList">
          <bk-table-column label="构建名称" prop="name">
            <template slot-scope="props">
              <span class="link-ui" @click.stop="openBuildDetail(props.row)">{{ props.row.name }}</span>
            </template>
          </bk-table-column>
          <bk-table-column label="路径" prop="path"></bk-table-column>
          <bk-table-column label="文件大小" prop="size"></bk-table-column>
          <bk-table-column label="仓库类型" prop="artifactoryType"></bk-table-column>
        </bk-table>
      </div>
      <!-- 输出变量 -->
      <div class="base-info mt30">
        <h3 class="setion-title">{{ $t(`m.tickets['输出变量']`) }}</h3>
        <bk-table
          v-bkloading="{ isLoading: buildStatusLoading }"
          :data="outputVariableList">
          <bk-table-column :label="$t(`m.tickets['变量']`)" prop="key" width="180"></bk-table-column>
          <bk-table-column :label="$t(`m.tickets['值']`)" prop="value"></bk-table-column>
        </bk-table>
      </div>
    </div>
    <bk-sideslider
      :is-show.sync="isShowBuildDetailDialog"
      :width="800"
      :quick-close="true"
      :title="openBuildInfo.name">
      <div slot="header">
        {{ $t(`m.tickets['构建详情']`) }} 【{{ openBuildInfo.name }}】
      </div>
      <div slot="content">
        <build-detail-info
          v-if="isShowBuildDetailDialog"
          :build-item="openBuildInfo">
        </build-detail-info>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import dayjs from 'dayjs';
  import i18n from '@/i18n/index.js';
  import taskStatus from './TaskStatus.vue';
  import BuildDetailInfo from './BuildDetailInfo.vue';
  import { errorHandler } from '../../../../../utils/errorHandler';
  import { convertMStoString, convertByteToSize } from '@/utils/util';

  // 任务基础信息
  const baseTaskInfoList = [
    { key: 'component_type', name: i18n.t('m.task[\'任务类型\']'), value: i18n.t('m.tickets[\'蓝盾任务\']') },
    { key: 'task_schema_id', name: i18n.t('m.task[\'任务模板\']'), value: '' },
    { key: 'name', name: i18n.t('m.task[\'任务名称\']'), value: '' },
    { key: 'sub_pipeline_id', name: i18n.t('m.tickets[\'流水线\']'), value: '' },
    { key: 'processor_users', name: i18n.t('m.task[\'处理人\']'), value: '' },
    { key: 'status', name: i18n.t('m.task[\'状态\']'), value: '' },
  ];

  const executInfoList = [
    { key: 'buildNum', name: i18n.t('m.tickets[\'构建号\']'), value: '' },
    { key: 'buildNum', name: i18n.t('m.tickets[\'源材料\']'), value: '' },
    { key: 'startTime', name: i18n.t('m.tickets[\'开始于\']'), value: '' },
    { key: 'trigger', name: i18n.t('m.tickets[\'触发方式\']'), value: '' },
    { key: 'endTime', name: i18n.t('m.tickets[\'完成于\']'), value: '' },
    { key: 'executeTime', name: i18n.t('m.systemConfig[\'耗时\']'), value: '' },
    { key: 'pipelineVersion', name: i18n.t('m.tickets[\'编排版本号\']'), value: '' },
  ];

  export default {
    name: 'DevopsExecutInfo',
    components: {
      taskStatus,
      BuildDetailInfo,
    },
    props: {
      taskInfo: {
        type: Object,
        default: () => ({}),
      },
    },
    data() {
      return {
        baseTaskInfoList,
        executInfoList,
        convertMStoString,
        taskStatusInfoLoading: false,
        isShowBuildDetailDialog: false,
        buildStatusLoading: false,
        taskStatusInfo: {}, // 任务状态信息
        buildStatusInfo: {}, // 构建状态信息
        buildList: [],
        outputVariableList: [], // 输出变量
        openBuildInfo: {}, // 打开的构建信息
      };
    },
    computed: {
      status() {
        return this.taskInfo.status;
      },
      taskInfoList() {
        const { taskStatusInfo } = this;
        const list = this.baseTaskInfoList.map((item) => {
          if (item.key === 'component_type') {
            return item;
          }
          if (item.key === 'task_schema_id' || item.key === 'sub_pipeline_id') {
            item.value = taskStatusInfo[item.key];
            return item;
          }
          item.value = this.taskInfo[item.key];
          return item;
        });
        return list;
      },
      displayExecutInfoList() {
        const { buildStatusInfo } = this;
        this.executInfoList.forEach((item) => {
          switch (item.key) {
            case 'startTime':
            case 'endTime':
              item.value = dayjs(buildStatusInfo[item.key]).format('YYYY-MM-DD hh:mm:ss');
              break;
            case 'executeTime':
              item.value = convertMStoString(buildStatusInfo.executeTime * 1000);
              break;
            default:
              item.value = buildStatusInfo[item.key];
          }
        });
        return this.executInfoList;
      },
    },
    created() {
    },
    async mounted() {
      await this.getTaskStatusInfo();
      this.getDevopsBuildStatus();
    },
    methods: {
      // 获取任务状态信息
      getTaskStatusInfo() {
        this.taskStatusInfoLoading = true;
        const { id } = this.taskInfo;
        return this.$store.dispatch('taskFlow/getTaskStatusInfo', id).then((res) => {
          this.taskStatusInfo = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.taskStatusInfoLoading = false;
          });
      },
      // 构建状态信息
      getDevopsBuildStatus() {
        this.buildStatusLoading = true;
        const {
          project_id: projectId,
          sub_pipeline_id: pipelineId,
          sub_task_id: buildId,
        } = this.taskStatusInfo;
        const params = {
          project_id: projectId,
          pipeline_id: pipelineId,
          build_id: buildId,
        };
        this.$store.dispatch('ticket/getDevopsBuildStatus', params).then((res) => {
          this.buildStatusInfo = res.data;
          this.buildList = (res.data.artifactList || []).map((item) => {
            item.size = convertByteToSize(item.size);
            return item;
          });
          this.outputVariableList = Object.keys(res.data.variables).map(key => ({
            key,
            value: res.data.variables[key],
          }));
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.buildStatusLoading = false;
          });
      },
      openBuildDetail(row) {
        this.isShowBuildDetailDialog = true;
        this.openBuildInfo = row;
      },
    },
  };
</script>
<style lang='scss' scoped>
@import '~@/scss/animation/rotation.scss';
@import '~@/scss/mixins/form.scss';
.link-ui {
    color: #3A84FF;
    cursor: pointer;
}
.devops-execut-info {
    .running-info {
        margin-top: 90px;
        text-align: center;
        color: #63656e;
        .bk-itsm-icon.icon-icon-loading {
            font-size: 32px;
            color: #3A84FF;
            display: inline-block;
            @include rotation;
        }
        .run-info {
            margin-top: 15px;
            font-size: 16px;
        }
        .run-time {
            margin-top: 15px;
            font-size: 14px;
            font-weight: 600;
            .time-block {
                padding: 6px 17px 6px 17px;
                display: inline-block;
                background: #f0f1f5;
                border-radius: 16px;
            }
        }
    }

    .execut-info {
        padding: 24px 27px;
    }
}
</style>
