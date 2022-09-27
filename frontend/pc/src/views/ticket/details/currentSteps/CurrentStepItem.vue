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
    :class="['bk-content-node', `state_id_${nodeInfo.state_id}`]">
    <!-- 线条 -->
    <div class="bk-content-line" v-if="!isLastNode"></div>
    <!-- 圆圈 -->
    <!-- <div class="bk-node-circle"></div> -->
    <!-- content -->
    <div :class="['bk-node-info', { 'full-screen': isFullScreen }]">
      <div class="bk-node-header">
        <!-- sla 时间 -->
        <p class="sla-time-info" v-if="nodeInfo.sla_task_status === 2" :style="{ 'background': slaInfo.isTimeOut ? '#ffeded' : '#fafbfd' }">
          <span
            class="bk-operation-timeout"
            :style="'color: ' + slaInfo.color">
            <i :class="['bk-itsm-icon', slaInfo.isTimeOut ? 'icon-itsm-icon-mark-eight' : 'icon-clock-new']"></i>
            <span style="margin-left: 8px;">
              {{ slaInfo.isTimeOut ? $t('m.newCommon["超时："]') : $t('m.newCommon["剩余："]') }}{{ nodeInfo.sla_timeout }}
            </span>
            <span style="margin-left: 5px;">
              {{ $t('m.newCommon["计划完成时间："]') }}{{nodeInfo.sla_deadline || '--'}}
            </span>
          </span>
        </p>
        <p class="bk-node-title">
          <!-- 折叠 icon -->
          <!-- <template v-if="hasNodeOptAuth">
                        <i v-if="unfold" class="bk-icon icon-down-shape icon-default"></i>
                        <i v-else class="bk-icon icon-right-shape icon-default"></i>
                    </template> -->
          <!-- 无权限提示 icon -->
          <!-- <i v-else
                        class="bk-itsm-icon icon-icon-no-permissions"
                        style="margin-left: 5px;"
                        v-bk-tooltips.top="$t(`m.newCommon['您暂无权限处理']`)">
                    </i> -->
          <!-- <span class="node-name">{{ nodeInfo.name }}</span> -->
          <span class="node-name">{{ nodeAutoPass() ? `(${ nodeInfo.name })` + $t(`m['审批节点已自动处理']`) : nodeInfo.name }}</span>
          <!-- 当前节点处理人 -->
          <span
            :ref="'processorsSpan' + index"
            class="node-title-processor"
            v-bk-tooltips="{
              allowHtml: true,
              theme: 'light',
              content: '#processor-tips-content',
              placement: 'top',
              duration: 300
            }">
            {{$t(`m.newCommon['处理人：']`)}}{{!!currSignProcessorInfo ? signProcessors : nodeInfo.processors}}
          </span>
          <!-- 会签人员信息 -->
          <bk-popover placement="top" theme="light" trigger="click">
            <span
              v-if="nodeInfo.type === 'SIGN'"
              class="bk-processor-check">
              {{ nodeInfo.is_sequential ? $t(`m.newCommon['点击查看']`) : $t(`m.newCommon['查看会签顺序']`) }}
            </span>
            <div class="bk-processor-content" slot="content">
              <div v-for="(processor, pIndex) in nodeInfo.tasks" :key="pIndex" class="bk-processor-one">
                <div v-if="nodeInfo.is_sequential && pIndex" class="bk-arrow">
                  <i class="bk-itsm-icon icon-arrow-long arrow-cus"></i>
                </div>
                <div class="bk-processor-span">
                  <span class="mr5 ml5">{{processor.processor}}</span>
                  <span>
                    <i v-if="processor.status === 'FINISHED'"
                      class="bk-itsm-icon icon-icon-finish icon-icon-finish-cus"></i>
                    <span
                      v-if="nodeInfo.is_sequential
                        && processor.status === 'WAIT'
                        && ((nodeInfo.tasks[pIndex - 1]
                        && nodeInfo.tasks[pIndex - 1].status === 'FINISHED')
                        || !pIndex)"
                      class="loading">
                      <i class="bk-itsm-icon icon-icon-loading icon-icon-loading-cus"></i>
                    </span>
                  </span>
                </div>
              </div>
            </div>
          </bk-popover>
          <!-- 状态 icon, API 节点和标准运维节点才显示 -->
          <task-status :status="nodeInfo.status" :node-type="nodeInfo.type"></task-status>
        </p>
        <p v-if="nodeInfo.desc" class="bk-node-desc"><i style="margin-right: 6px; padding-top: 2px;" class="bk-itsm-icon icon-itsm-icon-speak"></i><span>{{nodeInfo.desc}}</span></p>
        <span class="right-float">
          <!-- 响应按钮 -->
          <bk-button
            v-if="nodeInfo.is_reply_need"
            class="bk-sla-respons mr10"
            :disabled="nodeInfo.is_replied"
            :icon="nodeInfo.is_replied ? 'bk-icon icon-check-1' : ''"
            :loading="replyBtnLoading"
            @click="replyAssignDeliver()">
            {{ $t(`m['响应']`)}}
          </bk-button>
          <span class="full-screen-wrap">
            <i v-if="!isFullScreen" class="bk-itsm-icon icon-order-open" @click.stop="openFullScreen(nodeInfo)"></i>
            <span v-else class="exit-full-screen" @click.stop="onCloseFullScreen">
              <i class="bk-itsm-icon icon-order-close"></i>
              <span class="exit-text">{{$t(`m.common['退出全屏']`)}}</span>
            </span>
          </span>
        </span>
      </div>
      <collapse-transition v-if="!readOnly">
        <div class="bk-node-form" v-show="unfold">
          <!-- 禁用遮罩 -->
          <div class="bk-node-disabled" v-if="nodeInfo.status === 'SUSPEND'"></div>
          <div class="bk-form bk-form-vertical" v-if="hasNodeOptAuth">
            <!-- 节点任务 -->
            <node-task-list
              v-if="(nodeInfo.can_create_task || nodeInfo.can_execute_task)"
              :node-info="nodeInfo"
              :ticket-info="ticketInfo"
              @updateCurrentStep="successFn">
            </node-task-list>
            <sops-and-devops-task
              v-if="nodeInfo.status === 'FAILED' && (nodeInfo.type === 'TASK-SOPS' || nodeInfo.type === 'TASK-DEVOPS' || nodeInfo.type === 'WEBHOOK')"
              :constants="constants"
              :hooked-var-list="hookedVarList"
              :node-info="nodeInfo"
              :pipeline-list="pipelineList"
              :constant-default-value="constantDefaultValue"
              :ticket-info="ticketInfo"
              :workflow="workflow"
              :pipeline-constants="pipelineConstants"
              :pipeline-stages="pipelineStages"
              :pipeline-rules="pipelineRules"
              @reloadTicket="reloadTicket"
              @onChangeHook="onChangeHook">
            </sops-and-devops-task>
            <bkPluginTask
              v-if="nodeInfo.type === 'BK-PLUGIN' && nodeInfo.status === 'FAILED'"
              :ticket-info="ticketInfo"
              :node-info="nodeInfo"
              :workflow="workflow"
              @reloadTicket="reloadTicket"
              @onChangeHook="onChangeHook">
            </bkPluginTask>
            <!-- api 节点处理 -->
            <api-node-handle-body
              v-if="nodeInfo.type === 'TASK'"
              :node-info="nodeInfo"
              :basic-infomation="ticketInfo"
              @updateOrderStatus="successFn">
              <!-- 节点触发器 -->
              <template #button-extend v-if="triggers && triggers.length && nodeInfo.can_operate">
                <bk-dropdown-menu
                  ref="dropdown"
                  class="bk-node-trigger"
                  :align="'right'"
                  :font-size="'medium'"
                  @show="isDropdownShow = true"
                  @hide="isDropdownShow = false">
                  <bk-button class="node-trigger-btn" slot="dropdown-trigger" style="width:auto;">
                    <span>{{ $t('m.newCommon["更多操作"]') }}</span>
                    <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShow }]"></i>
                  </bk-button>
                  <ul class="bk-dropdown-list" slot="dropdown-content">
                    <li v-for="(trigger, tIndex) in triggers" :key="tIndex">
                      <a href="javascript:;" @click="openTriggerDialog(trigger)">{{trigger.display_name}}</a>
                    </li>
                  </ul>
                </bk-dropdown-menu>
              </template>
            </api-node-handle-body>
            <div v-else-if="currSignProcessorInfo" class="bk-area-show-back">
              <!-- 静态展示 -->
              <template v-for="(ite, fIndex) in currSignProcessorInfo.fields">
                <fields-done
                  :key="fIndex"
                  :item="ite"
                  origin="log">
                </fields-done>
              </template>
            </div>
            <!-- 字段列表 -->
            <field-info
              v-else
              ref="fieldInfo"
              :fields="nodeInfo.fields"
              :all-field-list="allFieldList">
            </field-info>
          </div>
          <div class="bk-form-btn" v-if="nodeInfo.type !== 'TASK'">
            <!-- 响应后才能处理 -->
            <template v-if="isShowDealBtns">
              <template v-for="(btn, btnIndex) in nodeInfo.operations">
                <bk-button class="mr10"
                  v-if="ignoreOperations.indexOf(btn.key) === -1"
                  :key="btn.key"
                  :theme="btnIndex === 0 ? 'primary' : 'default'"
                  :title="btn.name"
                  :disabled="!btn.can_operate || !nodeInfo.is_schedule_ready"
                  :loading="isBtnLoading(nodeInfo) || submitting"
                  @click="clickBtn(btn)">
                  <template v-if="!nodeInfo.is_schedule_ready">
                    <span v-bk-tooltips.top="'请将任务列表中的任务全部处理完成之后再进行处理提交'">{{btn.name}}</span>
                  </template>
                  <template v-else>
                    {{btn.name}}
                  </template>
                </bk-button>
              </template>
              <bk-button style="margin-right: 8px" v-if="!nodeAutoPass() && isShowAssgin && (nodeInfo.type === 'APPROVAL' || nodeInfo.type === 'NORMAL')" @click="clickBtn({ can_operate: true, key: 'EXCEPTION_DISTRIBUTE' ,name: '异常分派' })">{{ $t(`m['异常分派']`) }}</bk-button>
            </template>
            <!-- 节点触发器 -->
            <bk-dropdown-menu
              v-if="triggers && triggers.length && nodeInfo.can_operate"
              ref="dropdown"
              class="bk-node-trigger"
              :align="'right'"
              :font-size="'medium'"
              @show="isDropdownShow = true"
              @hide="isDropdownShow = false">
              <bk-button class="node-trigger-btn" slot="dropdown-trigger" style="width:auto;">
                <span>{{ $t('m.newCommon["更多操作"]') }}</span>
                <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShow }]"></i>
              </bk-button>
              <ul class="bk-dropdown-list" slot="dropdown-content">
                <li v-for="(trigger, tIndex) in triggers" :key="tIndex">
                  <a href="javascript:;" @click="openTriggerDialog(trigger)">{{trigger.display_name}}</a>
                </li>
              </ul>
            </bk-dropdown-menu>
          </div>
        </div>
      </collapse-transition>
    </div>
    <!-- 处理人 tips 内容 -->
    <div id="processor-tips-content" class="bk-processor-content">
      <div class="bk-processor-one" v-for="name in tipsProcessorsInfo.list" :key="name">
        <div class="bk-processor-span">{{ name }}</div>
      </div>
      <div
        v-if="tipsProcessorsInfo.extend"
        class="bk-processor-one">
        <div class="bk-processor-span" style="background: none;">{{ tipsProcessorsInfo.extend }}</div>
      </div>
    </div>
    <ticket-trigger-dialog ref="triggerDialog" :item="triggerInfo" @init-info="reloadTicket"></ticket-trigger-dialog>
    <node-deal-dialog
      :node-info="nodeInfo"
      :submitting="submitting"
      :open-form-info="openFormInfo"
      :all-groups="allGroups"
      :ticket-info="ticketInfo"
      @submitFormAjax="submitFormAjax"></node-deal-dialog>
  </div>
</template>

<script>
  import bkPluginTask from './nodetask/bkPlugintask.vue';
  import collapseTransition from '@/utils/collapse-transition.js';
  import fieldInfo from '@/views/managePage/billCom/fieldInfo.vue';
  import fieldsDone from '../components/fieldsDone.vue';
  import TaskStatus from '@/components/task/TaskStatus.vue';
  import apiNodeHandleBody from './apiNodeHandleBody.vue';
  import TicketTriggerDialog from '@/components/ticket/TicketTriggerDialog.vue';
  import NodeDealDialog from './NodeDealDialog.vue';
  import NodeTaskList from './nodetask/NodeTaskList.vue';
  import sopsAndDevopsTask from './nodetask/sopsDevopsTask.vue';
  import commonMix from '@/views/commonMix/common.js';
  import { errorHandler } from '@/utils/errorHandler.js';
  import { convertTimeArrToMS, convertTimeArrToString, convertMStoString } from '@/utils/util.js';
  import i18n from '@/i18n/index.js';

  export default {
    name: 'CurrentStepItem',
    components: {
      fieldsDone,
      fieldInfo,
      collapseTransition,
      TaskStatus,
      apiNodeHandleBody,
      TicketTriggerDialog,
      NodeDealDialog,
      NodeTaskList,
      sopsAndDevopsTask,
      bkPluginTask,
    },
    mixins: [commonMix],
    inject: ['reload'],
    props: {
      ticketInfo: {
        type: Object,
        default: () => ({}),
      },
      nodeInfo: {
        type: Object,
        default: () => ({}),
      },
      index: {
        type: Number,
      },
      nodeList: {
        type: Array,
        default() {
          return [];
        },
      },
      allFieldList: {
        type: Array,
        default() {
          return [];
        },
      },
      allGroups: {
        type: Array,
        default: () => ([]),
      },
      nodeTriggerList: {
        type: Array,
        default: () => ([]),
      },
      isLastNode: {
        type: Boolean,
        default: false,
      },
      readOnly: {
        type: Boolean,
        default: false,
      },
      isShowAssgin: Boolean,
    },
    data() {
      return {
        constants: [],
        hookedVarList: {},
        pipelineList: [],
        pipelineRules: {},
        pipelineStages: [],
        pipelineConstants: [],
        constantDefaultValue: {},
        convertTimeArrToString,
        replyBtnLoading: false,
        unfold: false, // 是否展开
        isFullScreen: false,
        submitting: false,
        isDropdownShow: false,
        ignoreOperations: ['SUSPEND', 'TERMINATE'],
        validatePopInfo: {
          openShow: false,
          content: '',
          title: this.$t('m.newCommon["缺少必填信息"]'),
        },
        // 弹窗处理信息(填写表单)
        openFormInfo: {
          isShow: false,
          title: '',
          width: 700,
          headerPosition: 'left',
          autoClose: false,
          precision: 0,
          btnInfo: {},
        },
        openSubmitInfo: {
          openShow: false,
          content: '',
        },
        slaInfo: {
          color: '',
          isTimeOut: false,
        },
        workflow: '',
        // 触发器
        triggerInfo: {},
      };
    },
    computed: {
      // 会签人信息
      currSignProcessorInfo() {
        if (!this.nodeInfo.can_operate && this.nodeInfo.type === 'SIGN') {
          return this.nodeInfo.tasks.find(task => task.can_view);
        }
        return undefined;
      },
      // tips 显示的处理人列表
      tipsProcessorsInfo() {
        // 把 `(共2人, 已处理0人)` 字符串从处理人中提取出来
        let completedStr = '';
        const processors = this.nodeInfo.processors_type === 'ORGANIZATION'
          ? this.nodeInfo.members
          : this.nodeInfo.processors;
        const replaceStr = processors.replace(/ \(共\d+人, 已处理\d+人\)/, (match) => {
          completedStr = match;
          return '';
        });
        const list = replaceStr.split(',').filter(name => !!name);
        if (list.length >= 30 && this.nodeInfo.processors_type === 'ORGANIZATION') {
          list.push('...');
        }
        return {
          list,
          extend: completedStr,
        };
      },
      // 会签完成信息
      signProcessors() {
        const tasks = this.nodeInfo.tasks;
        if (this.currSignProcessorInfo) {
          return this.currSignProcessorInfo.processor
            + this.$t('m.newCommon["(共"]')
            + tasks.length
            + this.$t('m.newCommon["人，已处理"]')
            + tasks.filter(task => task.status === 'FINISHED').length + this.$t('m.newCommon["人)"]');
        }
        return '';
      },
      // 当前节点触发器列表
      triggers() {
        return this.nodeTriggerList.filter(trigger => Number(trigger.sender) === Number(this.nodeInfo.state_id));
      },
      // 节点操作权限
      hasNodeOptAuth() {
        return this.nodeInfo.can_operate || !!this.currSignProcessorInfo || this.nodeInfo.can_execute_task;
      },
      // 是否显示处理按钮
      isShowDealBtns() {
        // 失败任务（主要是标准运维失败时），有单独处理
        if (this.nodeInfo.status === 'FAILED') {
          return false;
        }
        // SLA 需要响应后才显示处理按钮
        if (this.nodeInfo.sla_task_status === 2 && this.nodeInfo.is_reply_need === true) {
          return false;
        }
        const nodeType = ['TASK-SOPS', 'TASK-DEVOPS', 'BK-PLUGIN', 'WEBHOOK'];
        if (nodeType.includes(this.nodeInfo.type) && this.nodeInfo.status === 'RUNNING') return false;
        return true;
      },
    },
    created() {
      this.initData();
      this.$store.commit('ticket/setHasTicketNodeOptAuth', this.hasNodeOptAuth);
    },
    methods: {
      initData() {
        this.unfold = !this.nodeAutoPass();
        const item = this.nodeInfo;
        if (item.sla_task_status === 2) {
          if (item.sla_status === 2) {
            this.slaInfo.color = '#FE9C00';
          }
          if (item.sla_status === 4) {
            this.slaInfo.color = '#EA3536';
            this.slaInfo.isTimeOut = true;
          }
          this.runTime();
        }
        this.workflow = this.ticketInfo.table_fields[0].workflow_id;
        this.getSopsPreview();
        this.getpipelineDetail();
      },
      reloadTicket() {
        this.reload();
      },
      // 获取sops Constants
      async getSopsPreview() {
        if (Object.prototype.hasOwnProperty.call(this.nodeInfo.contexts, 'task_params')) {
          const { bk_biz_id, template_id, exclude_task_nodes_id, template_source } = this.nodeInfo.contexts.task_params;
          const params = {
            bk_biz_id,
            template_id,
            exclude_task_nodes_id,
          };
          const url = template_source === 'common' ? 'taskFlow/getSopsCommonPreview' : 'taskFlow/getSopsPreview';
          const res = await this.$store.dispatch(url, params);
          const constants = Object.keys(res.data.pipeline_tree.constants).map(item => {
            this.$set(this.hookedVarList, item, false);
            this.constantDefaultValue[item] = this.nodeInfo.contexts.task_params.constants[item];
            res.data.pipeline_tree.constants[item].value = this.nodeInfo.contexts.task_params.constants[item];
            return res.data.pipeline_tree.constants[item];
          });
          this.constants = constants;
        }
      },
      // 改变hook
      onChangeHook(key, value) {
        this.hookedVarList[key] = value;
      },
      // 获取流水线
      getpipelineDetail() {
        if (Object.prototype.hasOwnProperty.call(this.nodeInfo, 'api_info') && this.nodeInfo.type === 'TASK-DEVOPS') {
          const project_id = this.nodeInfo.api_info.devops_info.find(item => item.key === 'project_id');
          const pipeline_id = this.nodeInfo.api_info.devops_info.find(item => item.key === 'pipeline_id');
          this.$store.dispatch('ticket/getDevopsPipelineStartInfo', { project_id: project_id.value, pipeline_id: pipeline_id.value }).then(res => {
            this.pipelineList = res.data.properties;
            this.pipelineConstants = res.data.properties.map(item => {
              const constants = {
                key: '',
                value: '',
              };
              const findKey = this.nodeInfo.api_info.devops_info.find(ite => ite.key === item.id);
              if (findKey) {
                constants.key = findKey.key;
                constants.value = findKey.value;
              }
              return constants;
            });
            res.data.properties.forEach(item => {
              this.pipelineRules[item.id] = [{
                required: item.required,
                message: i18n.t('m.treeinfo["字段必填"]'),
                trigger: 'blur',
              }];
            });
          });
          this.$store.dispatch('ticket/getDevopsPipelineDetail', { project_id: project_id.value, pipeline_id: pipeline_id.value }).then(res => {
            this.pipelineStages = res.data.stages;
          });
        }
      },
      // 自动通过
      nodeAutoPass() {
        if (Object.prototype.hasOwnProperty.call(this.ticketInfo, 'is_auto_approve') && this.nodeInfo.type === 'APPROVAL') {
          return this.ticketInfo.is_auto_approve && window.username === this.ticketInfo.creator.split('(')[0] && this.nodeInfo.tasks.some(item => item.processor === this.ticketInfo.creator);
        }
        return false;
      },
      // 按钮操作
      clickBtn(btn) {
        // 字段校验
        if (
          btn.key === 'TRANSITION'
          && this.$refs.fieldInfo
          && !this.$refs.fieldInfo.checkValue()) {
          return;
        }
        this.openFormInfo.btnInfo = btn;
        this.openFormInfo.title = btn.name;
        // 二次确认弹窗的样式不同
        if (['TRANSITION', 'CLAIM', 'UNSUSPEND'].includes(this.openFormInfo.btnInfo.key)) {
          const contentMap = {
            TRANSITION: this.$t('m.newCommon["提交后，流程将转入下一环节，当前提交的部分内容将无法修改"]'),
            CLAIM: this.$t('m.newCommon["执行认领操作后，单据将流入我的待办"]'),
            UNSUSPEND: this.$t('m.newCommon["执行恢复操作后，单据将可以继续处理"]'),
          };
          this.openSubmitInfo.content = contentMap[this.openFormInfo.btnInfo.key];
          this.$bkInfo({
            type: 'warning',
            title: btn.key === 'TRANSITION' ? this.$t('m.memberSelect["是否"]') + this.openFormInfo.title : this.openFormInfo.title,
            subTitle: this.openSubmitInfo.content,
            confirmFn: () => {
              this.submitFormAjax();
            },
          });
        } else {
          this.openFormInfo.isShow = true;
          this.openFormInfo.title = btn.name;
        }
      },
      submitFormAjax(submitFormData) {
        const id = this.nodeInfo.ticket_id;
        // 终止
        if (this.openFormInfo.btnInfo.key === 'TERMINATE') {
          const params = {
            state_id: this.nodeInfo.state_id,
            terminate_message: submitFormData.terminate_message,
          };
          this.submitAjax('terminableOrder', params, id);
        }
        // 审批、通过
        if (this.openFormInfo.btnInfo.key === 'TRANSITION') {
          // 将字段中的时间转换一遍
          this.fieldFormatting(this.nodeInfo.fields);
          const params = {
            state_id: this.nodeInfo.state_id,
            fields: this.nodeInfo.fields.filter(ite => !ite.is_readonly && ite.showFeild).map(item => {
              if (item.type === 'FILE') {
                item.value = item.value.toString();
              }
              return {
                id: item.id,
                key: item.key,
                type: item.type,
                choice: item.choice,
                value: item.showFeild ? item.value : '',
              };
            }),
          };
          this.submitAjax('proceedOrder', params, id);
        }
        // 转单，挂起，恢复，分派，认领
        if (this.openFormInfo.btnInfo.key === 'SUSPEND' || this.openFormInfo.btnInfo.key === 'UNSUSPEND' || this.openFormInfo.btnInfo.key === 'CLAIM') {
          const params = {
            state_id: this.nodeInfo.state_id,
            processors: '',
            processors_type: '',
            action_type: this.openFormInfo.btnInfo.key,
          };
          // 挂起
          if (this.openFormInfo.btnInfo.key === 'SUSPEND') {
            params.processors = window.username;
            params.processors_type = 'PERSON';
            params.action_message = submitFormData.suspend_message;
          }
          // 恢复，认领
          if (this.openFormInfo.btnInfo.key === 'UNSUSPEND' || this.openFormInfo.btnInfo.key === 'CLAIM') {
            params.processors = window.username;
            params.processors_type = 'PERSON';
          }
          this.submitAjax('distributeOrder', params, id);
        }
        if (this.openFormInfo.btnInfo.key === 'DELIVER' || this.openFormInfo.btnInfo.key === 'DISTRIBUTE') {
          const params = {
            state_id: this.nodeInfo.state_id,
            action_type: this.openFormInfo.btnInfo.key,
            processors: '',
            processors_type: '',
          };
          // 转单
          if (this.openFormInfo.btnInfo.key === 'DELIVER') {
            params.processors = submitFormData.person.value;
            params.processors_type = submitFormData.person.type;
            params.action_message = submitFormData.deliverReason;
          }
          // 分派
          if (this.openFormInfo.btnInfo.key === 'DISTRIBUTE') {
            params.processors = submitFormData.person.value;
            params.processors_type = submitFormData.person.type;
          }
          this.submitAjax('newAssignDeliver', params, id);
        }
        if (this.openFormInfo.btnInfo.key === 'EXCEPTION_DISTRIBUTE') {
          const params = {
            state_id: this.nodeInfo.state_id,
            processors: submitFormData.person.value,
            processors_type: submitFormData.person.type,
            action_type: this.openFormInfo.btnInfo.key,
          };
          this.submitAjax('exceptionDistribute', params, id);
        }
      },
      submitAjax(type, params, id) {
        if (this.submitting) {
          return;
        }
        this.submitting = true;
        const valueParams = {
          params,
          id,
        };
        this.$store.dispatch(`deployOrder/${type}`, valueParams).then(() => {
          this.$bkMessage({
            message: this.openFormInfo.title + this.$t('m.newCommon["成功"]'),
            theme: 'success',
          });
          this.cancelForm();
          this.successFn();
          this.$emit('closeSlider');
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.submitting = false;
            const typeList = ['TRANSITION', 'SUSPEND', 'UNSUSPEND', 'CLAIM'];
            if (typeList.some(item => item === this.openFormInfo.btnInfo.key)) {
              this.cancelForm();
            }
            setTimeout(() => {
              this.reloadTicket();
            }, 500);
          });
      },
      // 当前操作节点打开全屏
      openFullScreen() {
        this.isFullScreen = true;
        this.$bkMessage({
          message: this.$t('m.common["按 ESC 键退出全屏"]'),
        });
        document.addEventListener('keydown', this.handlerKeyDown);
      },
      // 关闭全屏
      onCloseFullScreen() {
        this.isFullScreen = false;
      },
      // 关闭全屏 - esc
      handlerKeyDown(event) {
        if (event.keyCode === 27) {
          this.onCloseFullScreen();
          document.removeEventListener('keydown', this.handlerKeyDown);
        }
      },
      // 展开收起
      closeUnflod(e) {
        // 禁止冒泡
        if (this.nodeAutoPass()) return;
        if (e.target.className.indexOf('bk-processor-check') === -1) {
          if (!this.nodeInfo.can_operate && !this.currSignProcessorInfo) {
            return;
          }
          this.unfold = !this.unfold;
        }
      },
      // 操作成功
      successFn() {
        this.$emit('successFn');
      },
      cancelForm() {
        this.openFormInfo.isShow = false;
      },
      openTriggerDialog(trigger) {
        const context = {};
        this.nodeInfo.fields.forEach((item) => {
          context[item.key] = item.val;
        });
        const getTriggerParams = this.$store.dispatch('trigger/getTriggerParams', { params: { context }, id: trigger.id });
        const getResponseList = this.$store.dispatch('trigger/getResponseList');
        Promise.all([getTriggerParams, getResponseList]).then(res => {
          const curTrigger = res[0].data;
          this.triggerInfo = res[1].data.find(item => item.name === trigger.component_name);
          if (this.triggerInfo.key === 'api') {
            const wayInfo = {
              contentStatus: false,
              isLoading: false,
              key: 'api',
              wayInfo: this.triggerInfo,
            };
            this.triggerInfo = wayInfo;
            this.triggerInfo.wayInfo.field_schema.forEach(schema => {
              const cur = curTrigger.find(item => item.key === schema.key);
              if (schema.key === 'api_source') {
                this.$set(schema, 'systemId', '');
                this.$set(schema, 'apiId', '');
                this.$set(schema, 'value', cur.value);
              } else {
                this.$set(schema, 'apiContent', {});
                this.$set(schema, 'value', cur.value);
              }
            });
          } else {
            this.triggerInfo.field_schema.forEach(schema => {
              const cur = curTrigger.find(item => item.key === schema.key);
              let valueInfo = cur.value || '';
              if (schema.type === 'MEMBERS' || schema.type === 'MULTI_MEMBERS') {
                valueInfo = [];
                if (schema.value) {
                  schema.value.forEach(schemaValue => {
                    if (schemaValue.value) {
                      const itemValue = {
                        key: schemaValue.value.member_type,
                        value: schemaValue.value.members,
                        secondLevelList: [],
                        isLoading: false,
                      };
                      valueInfo.push(itemValue);
                    }
                  });
                } else {
                  const itemValue = {
                    key: cur.value[0].value.member_type,
                    value: cur.value[0].value.members,
                    secondLevelList: [],
                    isLoading: false,
                  };
                  valueInfo.push(itemValue);
                }
              }
              this.$set(schema, 'value', valueInfo);
              // 对于发通知的数据格式
              if (schema.type === 'SUBCOMPONENT' && schema.sub_components && schema.sub_components.length) {
                schema.sub_components.forEach(subComponent => {
                  subComponent.field_schema.forEach(subField => {
                    const cur = curTrigger[0].sub_components.find(item => item.key === subComponent.key);
                    let subFieldValue = subField.value || '';
                    if (cur) {
                      const subCur = cur.params.find(ite => ite.key === subField.key);
                      subFieldValue = subCur.value;
                    }
                    if (subField.type === 'MEMBERS' || subField.type === 'MULTI_MEMBERS') {
                      if (cur) {
                        subComponent.checked = true;
                        const subCur = cur.params.find(ite => ite.key === subField.key);
                        if (Array.isArray(subField.value)) {
                          subField.value.forEach(schemaValue => {
                            const itemValue = {
                              key: schemaValue.value.member_type,
                              value: schemaValue.value.members,
                              secondLevelList: [],
                              isLoading: false,
                            };
                            subFieldValue.push(itemValue);
                          });
                        } else {
                          subFieldValue = [];
                          subCur.value.forEach(item => {
                            subFieldValue.push({
                              key: item.value.member_type,
                              value: item.value.members,
                              secondLevelList: [],
                              isLoading: false,
                            });
                          });
                        }
                      } else {
                        subFieldValue = [
                          {
                            key: '',
                            value: '',
                            secondLevelList: [],
                            isLoading: false,
                          },
                        ];
                      }
                    }
                    this.$set(subField, 'value', subFieldValue);
                  });
                });
              }
            });
          }
        })
          .finally(() => {
            this.$refs.triggerDialog.openDialog(trigger);
          });
      },
      // 提交按钮 loading 状态
      isBtnLoading(item) {
        // 会签或审批节点提交后，当前处理人task 为 RUNNING|EXECUTED状态，则继续轮询 FINISHED
        const currUserDealTask = (item.tasks && item.tasks.find(task => {
          const splitName = task.processor.replace(/\((.+?)\)/, '');
          return splitName === window.username;
        })) || {};
        if (['SIGN', 'APPROVAL'].includes(item.type) && ['RUNNING', 'EXECUTED'].includes(currUserDealTask.status)) {
          return true;
        }
        return false;
      },
      runTime() {
        let slaTime = this.slaInfo.slaTime;
        if (!slaTime) {
          slaTime = convertTimeArrToMS(this.nodeInfo.sla_timeout.map(num => Math.abs(num)));
          this.nodeInfo.sla_timeout = convertMStoString(slaTime * 1000);
        }
        this.myInterval(() => {
          // eslint-disable-next-line
          this.slaInfo.isTimeOut ? slaTime++ : slaTime--;
          if (slaTime <= 0) {
            this.slaInfo.isTimeOut = true;
            this.slaInfo.color = '#EA3536';
          }
          this.nodeInfo.sla_timeout = convertMStoString(slaTime * 1000);
        }, 1000);
      },
      myInterval(fn, time) {
        if (this._isDestroyed === true) return false;
        const outTimeKey = setTimeout(() => {
          fn();
          clearTimeout(outTimeKey);
          this.myInterval(fn, time);
        }, time);
      },
      // 响应按钮
      replyAssignDeliver() {
        const ticketId = this.ticketInfo.id;
        const stateId = this.nodeInfo.state_id;
        const valueParams = {
          params: {
            state_id: stateId,
          },
          id: ticketId,
        };
        this.replyBtnLoading = true;
        this.$store.dispatch('deployOrder/replyAssignDeliver', valueParams).then(() => {
          this.$bkMessage({
            message: this.$t('m.newCommon["响应成功"]'),
            theme: 'success',
          });
          this.cancelForm();
          this.successFn();
          this.$emit('closeSlider');
        })
          .catch((res) => {
            this.$bkMessage({
              message: res.data.msg || this.$t('m.newCommon["响应失败！"]'),
              theme: 'error',
              ellipsisLine: 0,
            });
          })
          .finally(() => {
            this.replyBtnLoading = false;
          });
      },
    },
  };
</script>
<style lang="scss">
.processors-tips {
    .tippy-content{
        word-break: break-all;
    }
}
</style>
<style lang="scss" scoped>
    .bk-content-node {
        padding-bottom: 28px;
        margin-bottom: 2px;
        position: relative;

        .bk-node-circle {
            position: absolute;
            top: 16px;
            left: -1px;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #C4C6CC;
            z-index: 1;
        }

        .bk-node-info {
            position: relative;
            font-size: 14px;
            &.full-screen {
                margin-left: 0;
                position: fixed;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                overflow: auto;
                z-index: 500;
                background: #ffffff;
            }
            .bk-node-desc {
              display: flex;
              margin: 15px 40px 15px 15px;
              background-color: #ffffff;
              color: #737987;
              font-size: 12px;
              padding: 0;
              word-wrap:break-word;
            }
            .bk-node-title {
                margin: 17px 10px;
                outline: none;
                background-color: #ffffff;
                color: #737987;
                padding: 0;
                width: 100%;
                display: flex;
                align-items: center;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;

                .node-title-processor{
                    display: inline-block;
                    max-width: 76%;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                    outline: none;
                    font-size: 12px;
                }

                .bk-processor-check{
                    cursor: pointer;
                    font-size: 12px;
                    color: #3a84ff;
                    margin-left: 10px;
                    outline: none;
                }
                .node-name {
                    margin: 0 15px 0 5px;
                    color: #333948;
                    font-size: 14px;
                    font-weight: bold;
                }
            }
            .bk-node-header{
                position: relative;
                padding: 8px 0;
                width: 100%;
                color: #737987;
                background-color: #ffffff;
                border-radius: 2px;
                .icon-angle-down {
                    font-size: 22px;
                }

            }
            .sla-time-info {
                height: 32px;
                font-size: 12px;
                border: 1px solid #ffd2d2;
                color: #63656e;
            }
            .icon-default {
                font-size: 12px;
                color: #979BA5;
            }
            .right-float {
                position: absolute;
                right: 10px;
                top: 50%;
                transform: translateY(-50%);
                margin-left: auto;
            }
            .full-screen-wrap {
                .icon-order-open {
                    font-size: 16px;
                    color: #979BA5;
                    z-index: 2;
                    cursor: pointer;
                    &:hover {
                        color: #63656E;
                    }
                }
                .exit-full-screen {
                    padding: 0px 10px 0px 18px;
                    display: inline-block;
                    height: 40px;
                    line-height: 40px;
                    font-size: 16px;
                    color: #979BA5;
                    z-index: 2;
                    cursor: pointer;
                    .exit-text {
                        font-size: 12px;
                    }
                    &:hover {
                        background-color: #dcdee5;
                    }
                }
            }

            .bk-node-cursor {
                cursor: pointer;
            }

            .bk-node-form {
                position: relative;
                padding: 15px 5px 15px 15px;
                transition: .3s height ease-in-out, .3s padding-top ease-in-out, .3s padding-bottom ease-in-out;
                .bk-node-trigger{
                    display: inline-block;
                    vertical-align: middle;
                    .node-trigger-btn {
                        width:auto;
                    }
                }
                .bk-form-btn {
                    display: flex;
                    margin-top: 10px;
                }

                .bk-form {
                    position: relative;
                }
            }

            .bk-node-disabled {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                cursor: not-allowed;
                z-index: 5;
            }
        }
        .bk-content-line {
            position: absolute;
            top: 20px;
            left: 2px;
            height: 100%;
            border-left: 2px solid #F0F3F6;
        }
    }
    .bk-processor-content{
        display: flex;
        max-width: 600px;
        flex-wrap: wrap;

        .bk-processor-one{
            display: inline-flex;
            align-items: center;
            padding: 6px 0;

            .bk-arrow{
                display: inline-flex;
                align-items: center;
                position: relative;

                .arrow-cus{
                    font-size: 12px;
                    transform: scale(0.6);
                }
            }
        }
        .bk-processor-span{
            background: #F0F1F5;
            display: inline-flex;
            align-items: center;
            height: 22px;
            line-height: 22px;
            margin-right: 5px;
            padding: 0 5px;

            .icon-icon-finish-cus{
                &:before{
                    color: #737987;
                }
            }

            .icon-icon-loading-cus{
                &:before{
                    color: #3A84FF;
                }
            }
        }
    }
    .loading{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        animation: loading 2s linear 0.2s infinite;
    }

    @keyframes loading{
        0%{
            transform: rotate(0deg);
        }
        100%{
            transform: rotate(360deg);
        }
    }
    .bk-operation-timeout {
        display: block;
        width: calc(100% - 26px);
        margin-left: 16px;
        margin-right: 10px;
        margin-bottom: 17px;
        color: #63656e;
        line-height: 32px;
        min-width: 265px;
        text-overflow: ellipsis;
        white-space: nowrap;
        overflow: hidden;
        font-size: 12px;
        .icon-clock-new {
            vertical-align: 1px;
        }
    }
</style>
