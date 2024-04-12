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
  <div class="ticket-detail-panel" v-bkloading="{ isLoading: loading.ticketLoading }">
    <template v-if="!ticketErrorMessage">
      <ticket-header
        ref="ticketHeader"
        v-if="!loading.ticketLoading"
        :header-info="headerInfo"
        :ticket-info="ticketInfo"
        :ticket-trigger-list="ticketTriggerList"
        @reloadTicket="reloadTicket">
      </ticket-header>

      <div class="ticket-container">
        <div class="ticket-container-left">
          <!-- 基础信息/工单预览 -->
          <left-ticket-content
            ref="leftTicketContent"
            :comment-list="commentList"
            :comment-id="commentId"
            :loading="loading"
            :ticket-info="ticketInfo"
            :node-list="nodeList"
            :first-state-fields="firstStateFields"
            :node-trigger-list="nodeTriggerList"
            :ticket-id="ticketId"
            :is-page-over="isPageOver"
            :has-node-opt-auth="hasNodeOptAuth"
            :is-show-assgin="isShowAssgin"
            :comment-loading="commentLoading"
            :more-loading="moreLoading"
            @addTargetComment="addTargetComment"
            @refreshComment="refreshComment"
            @getBacicInfoStatus="getBacicInfoStatus">
          </left-ticket-content>
        </div>
        <!-- 分屏拖拽线 -->
        <div data-test-id="ticket_line_screen_drag" class="drag-line" @mousedown="handleLineMouseDown" v-show="showRightTabs"></div>
        <div class="show-right-icon" @click="onShowRightContent" v-show="!showRightTabs">
          <i data-v-639c8670="" class="bk-icon icon-angle-left"></i>
        </div>
        <div id="ticketContainerRight" class="ticket-container-right" v-show="showRightTabs">
          <div v-if="openFunction.SLA_SWITCH && hasNodeOptAuth" :class="['sla-information', isShowSla ? 'hide' : '']">
            <div class="sla-view">
              <div class="sla-title" @click="handleClickShowSla">
                <i :class="['bk-itsm-icon', !isShowSla ? 'icon-xiangxia' : 'icon-xiangyou']"></i>
                <span>{{ $t('m["SLA信息"]') }}</span>
              </div>
              <span class="view-sla-rule" @click="viewSlaRule">{{ $t('m["规则查看"]') }}</span>
            </div>
            <sla-record-tab
              v-if="!isShowSla"
              :threshold="threshold"
              :ticket-id="ticketId"
              :basic-infomation="ticketInfo"
              :node-list="nodeList">
            </sla-record-tab>
          </div>
          <right-ticket-tabs
            class="right-ticket-tabs"
            v-if="!loading.ticketLoading"
            :is-show-sla="isShowSla"
            :ticket-info="ticketInfo"
            :has-node-opt-auth="hasNodeOptAuth"
            :node-list="nodeList"
            @ticketFinishAppraise="ticketFinishAppraise"
            @viewProcess="viewProcess">
          </right-ticket-tabs>
        </div>
      </div>
    </template>
    <!-- 403 | 404 -->
    <no-ticket-content v-else
      :message="ticketErrorMessage">
    </no-ticket-content>
    <bk-dialog
      v-model="isShowDialog"
      ext-cls="processed-info-dialog"
      :width="800"
      :show-header="false"
      :show-footer="false"
      :mask-close="false"
      @cancel="goToHome">
      <div class="processed-info-content">
        <div class="header-area">
          <bk-icon class="info-icon" type="info-circle-shape" />
          <span class="tips">{{ $t('m["单据已由processor处理,您无需操作"]', { processor: processedUser }) }}</span>
        </div>
        <p class="section-title">{{ $t('m["单据基本信息"]') }}</p>
        <div class="ticket-detail">
          <div class="form-item">
            <div class="label">{{ $t('m.tickets["标题"]') }}</div>{{ $t('m[":"]') }}
            <div class="value-content"><span>{{ processedInfo.title }}</span></div>
          </div>
          <div class="form-item">
            <div class="label">{{ $t('m.tickets["单号"]') }}</div>{{ $t('m[":"]') }}
            <div class="value-content"><span>{{ processedInfo.sn }}</span></div>
          </div>
          <div class="form-item">
            <div class="label">{{ $t('m.tickets["提单人"]') }}</div>{{ $t('m[":"]') }}
            <div class="value-content"><span>{{ processedInfo.creator }}</span></div>
          </div>
          <div v-for="field in processedInfo.fields" class="form-item" :key="field.id">
            <div class="label">{{ field.name }}</div>{{ $t('m[":"]') }}
            <div class="value-content">
              <bk-table v-if="field.type === 'TABLE'" :data="field.display_value">
                <bk-table-column v-for="col in field.choice" :key="col.key" :label="col.name" :prop="col.key"></bk-table-column>
              </bk-table>
              <div v-else-if="field.type === 'CUSTOM-FORM'" class="custom-form-wrapper">
                <div v-for="(table, index) in field.tables" class="table-item" :key="index">
                  <p v-if="table.label" class="table-label">{{ table.label }}</p>
                  <bk-table :data="table.values">
                    <bk-table-column v-for="col in table.cols" :key="col.key" :label="col.name" :prop="col.key"></bk-table-column>
                  </bk-table>
                </div>
              </div>
              <span v-else>{{ field.display_value }}</span>
            </div>
          </div>
        </div>
        <div class="action-btn">
          <bk-button theme="primary" @click="goToHome">{{ $t('m["我知道了"]') }}</bk-button>
        </div>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
  import SlaRecordTab from './rightTicketTabs/SlaRecordTab.vue';
  import TicketHeader from './TicketHeader.vue';
  import NoTicketContent from './components/NoTicketContent.vue';
  import RightTicketTabs from './rightTicketTabs/RightTicketTabs.vue';
  import commonMix from '@/views/commonMix/common.js';
  import apiFieldsWatch from '@/views/commonMix/api_fields_watch.js';
  import fieldMix from '@/views/commonMix/field.js';
  import { mapState } from 'vuex';
  import { errorHandler } from '@/utils/errorHandler.js';
  import { deepClone, transCustomFormToTable } from '@/utils/util';
  import leftTicketContent from './leftTicketContent.vue';
  import bus from '@/utils/bus';

  export default {
    name: 'TicketDetail',
    components: {
      NoTicketContent,
      leftTicketContent,
      TicketHeader,
      SlaRecordTab,
      RightTicketTabs,
    },
    inject: ['reload'],
    provide() {
      return {
        reloadTicket: this.reloadTicket,
      };
    },
    mixins: [fieldMix, commonMix, apiFieldsWatch],
    data() {
      const approveDict = {
        审批意见: this.$t('m.managePage["审批意见"]'),
        通过: this.$t('m.managePage["通过"]'),
        拒绝: this.$t('m.manageCommon["拒绝"]'),
        备注: this.$t('m["备注"]'),
      };
      return {
        moreLoading: false, // 底部加载loading
        leftTicketDom: '',
        isPageOver: false,
        isThrottled: false,
        isRequsetComment: false,
        curCommentLength: 10, // 默认为10条
        totalPages: 0, // 评论总页数
        page: 1, // 评论当前页数
        page_size: 10,
        commentCount: 0,
        isShowSla: true,
        showRightTabs: true,
        processedUser: '',
        commentLoading: false,
        ticketTimer: null, // 单据详情轮询器
        containerLeftWidth: 0,
        ticketId: '',
        ticketErrorMessage: '',
        noPermitResp: {},
        // 移动布局信息
        dragLine: {
          base: 0,
          move: 0,
          startX: null,
          maxLength: 0,
          canMove: false,
        },
        // 单据详情信息
        ticketInfo: {},
        // 头部信息
        headerInfo: {
          statusColor: '',
        },
        // 通知链接进入，但节点已被其他人处理提示
        isShowDialog: false,
        noticeInfo: {
          is_processed: false,
          processed_user: '',
        },
        loading: {
          ticketLoading: true,
          nodeInfoLoading: false,
        },
        // 节点列表
        nodeList: [],
        // 单据触发器列表
        ticketTriggerList: [],
        // 节点触发器列表
        nodeTriggerList: [],
        // 提单节点字段信息
        firstStateFields: [],
        // 所有字段列表
        allFieldList: [],
        commentList: [],
        commentId: '',
        threshold: [],
        hasNodeOptAuth: false,
        isShowAssgin: false,
        basicStatus: true,
        approveDict,
        processedInfo: {},
      };
    },
    computed: {
      ...mapState({
        openFunction: state => state.openFunction,
      }),
      token() {
        return this.$route.query.token;
      },
    },
    watch: {
      isShowSla(val) {
        if (val) {
          const slaCount = this.ticketInfo.sla.Length;
          const slaDom = document.querySelector('.sla-information');
          slaDom.style.height = `${134 * slaCount}px`;
        }
      },
      commentList(val) {
        if (val.length > 0) {
          this.curCommentLength = val.length;
        }
      },
      ticketInfo: {
        handler(val) {
          if (Object.keys(val).length !== 0) {
            const stepIdList = val.current_steps.map(item => item.id);
            if (stepIdList.length !== 0) {
              this.$router.replace({
                path: this.$route.path,
                query: Object.assign({}, this.$route.query, { step_id: stepIdList.toString() }),
              });
            }
          } else {
            this.initData();
          }
        },
        immediate: true,
      },
    },
    created() {
      bus.$on('getIsProcessStatus', data => {
        this.noPermitResp = deepClone(data);
        const { id, step_id } = data.config.params;
        const params = {
          id,
          step_id,
        };
        this.$store.dispatch('ticket/getStepProcessInfo', { params }).then(res => {
          if (res.data.is_processor) {
            res.data.detail.fields.forEach(field => {
              if (field.type === 'CUSTOM-FORM') {
                field.tables = transCustomFormToTable(field.value);
              }
            });
            this.processedUser = res.data.processed_user;
            this.processedInfo = res.data.detail;
            this.isShowDialog = true;
          } else {
            bus.$emit('processData', this.noPermitResp);
          }
        });
      });
    },
    async mounted() {
      let isCanOperate = false;
      let isHistoryOperator = false;
      await this.initData();
      this.getProtocolsList();
      this.$nextTick(function () {
        this.leftTicketDom = document.querySelector('.comment-list');
        this.leftTicketDom.addEventListener('scroll', this.handleTicketScroll);
      });
      if (this.$refs.leftTicketContent && this.$refs.leftTicketContent.currentStepList[0]) {
        isCanOperate = this.$refs.leftTicketContent.currentStepList.some(item => item.can_operate);
      }
      // 判断是否历史处理人
      isHistoryOperator = this.ticketInfo.updated_by.split(',').includes(window.username);
      this.hasNodeOptAuth = isCanOperate || isHistoryOperator;
      this.$store.commit('ticket/setHasTicketNodeOptAuth', this.hasNodeOptAuth);
      if (this.ticketInfo && this.ticketInfo.auth_actions) {
        // 当前节点有权限不显示异常分派
        this.isShowAssgin = this.ticketInfo.auth_actions.includes('ticket_management');
      }
      this.$store.commit('project/setProjectId', this.ticketInfo.project_key);
    },
    beforeDestroy() {
      this.clearTicketTimer();
      this.$store.commit('project/setProjectId', window.DEFAULT_PROJECT);
    },
    methods: {
      // 同步数据，需等待 ticketInfo 返回
      async initData() {
        this.ticketId = this.$route.query.id;
        await this.getTicketDetailInfo();
        if (this.ticketErrorMessage) {
          this.clearTicketTimer();
          return false;
        }
        this.getTriggers();
        await this.getNodeList();
        this.getCurrTickeStatusColor();
        this.initCurrentStepData();
        this.initTicketTimer();
        this.initComments();
      },
      handleClickShowSla() {
        this.isShowSla = !this.isShowSla;
      },
      viewSlaRule() {
        this.$router.push({
          name: 'slaAgreement',
          query: {
            project_id: this.$route.query.project_id || 0,
          },
        });
      },
      async initComments() {
        try {
          this.commentLoading = true;
          // 获取root id
          const rootRes = await this.$store.dispatch('ticket/getTicketAllComments', { ticket_id: this.ticketId, show_type: '' });
          this.commentId = rootRes.data.items.find(item => item.remark_type === 'ROOT').id;
          this.commentList = await this.getComments(1, 10);
        } catch (e) {
          console.log(e);
        } finally {
          this.commentLoading = false;
        }
      },
      getBacicInfoStatus(val) {
        this.basicStatus = val;
      },
      async getComments(page, page_size) {
        this.commentLoading = true;
        const commentList = [];
        const is_history_processor = this.ticketInfo.updated_by.split(',').includes(window.username);
        const current_processors = [];
        this.ticketInfo.current_processors.split(',').forEach((item) => {
          current_processors.push(item.split('(')[0]);
        });
        const is_current_processor = current_processors.includes(window.username);
        const commmentRes = await this.$store.dispatch('ticket/getTicketAllComments', {
          ticket_id: this.ticketId,
          show_type: (is_current_processor || is_history_processor) ? 'ALL' : 'PUBLIC',
          page,
          page_size,
        });
        commmentRes.data.items.forEach((item, index) => {
          if (item.parent__id !== this.commentId) {
            this.getReplyCommet(item.parent__id, index);
          }
        });
        this.commentCount = commmentRes.data.count;
        this.totalPages = Math.ceil((commmentRes.data.count - 1) / page_size) || 1;
        commentList.push(...commmentRes.data.items);
        commentList.sort((a, b) => b.id - a.id);
        this.commentLoading = false;
        return commentList.filter(item => item.remark_type !== 'ROOT');
      },
      async getReplyCommet(id, index) {
        if (id) {
          const res = await this.$store.dispatch('ticket/getReplyComment', { ticket_id: this.ticketId, id });
          this.$set(this.commentList[index], 'parent_creator', res.data.creator);
          this.$set(this.commentList[index], 'parent_content', res.data.content);
        }
      },
      async addTargetComment(curComment) {
        if (this.commentId !== curComment.parent__id) {
          const res = await this.$store.dispatch('ticket/getReplyComment', { ticket_id: this.ticketId, id: curComment.parent__id });
          this.commentList.push(res.data);
          this.$refs.leftTicketContent.$refs.comment.jumpTargetComment(curComment);
        }
      },
      handleTicketScroll() {
        if (this.totalPages === 1) return;
        if (!this.isPageOver && !this.isThrottled && this.$refs.leftTicketContent.stepActiveTab === 'allComments') {
          this.isThrottled = true;
          const timer = setTimeout(async () => {
            this.isThrottled = false;
            const el = this.leftTicketDom;
            if (el.scrollHeight - el.offsetHeight - el.scrollTop < 10) {
              this.moreLoading = true;
              this.page += 1;
              clearTimeout(timer);
              const result = await this.getComments(this.page, this.page_size);
              this.commentList.push(...result);
              this.isPageOver = this.page === this.totalPages;
              this.moreLoading = false;
            }
          }, 500);
        }
      },
      async refreshComment() {
        this.commentList = await this.getComments(1, this.curCommentLength + 1);
        this.page = 1;
      },
      getProtocolsList() {
        const params = {
          project_id: this.ticketInfo.project_key,
        };
        this.$store.dispatch('slaManagement/getProtocolsList', params).then(res => {
          const curSlas = res.data.filter(item => this.ticketInfo.sla.includes(item.name));
          const slathreshold = curSlas.map(item => {
            const condition = item.action_policies.map(ite => {
              const obj = {};
              obj[ite.type] = ite.condition.expressions[0].value;
              return obj;
            });
            // 1 3 2 4
            // type 1  2 为响应
            // type 3  4 为处理
            return item.action_policies.length === 0 ? {
              sla_name: item.name,
              rWarningThreshold: 1,
              pWarningThreshold: 1,
              rTimeOutThreshold: 1,
              pTimeOutThreshold: 1,
            } : {
              sla_name: item.name,
              rWarningThreshold: condition[0][1] / 100 || 1, // 1为100%
              pWarningThreshold: condition[1][3] / 100 || 1,
              rTimeOutThreshold: Object.prototype.hasOwnProperty.call(condition[2], 2) ? condition[2][2] / 100 : 1,
              pTimeOutThreshold: Object.prototype.hasOwnProperty.call(condition[2], 2) ? condition[3][4] / 100 : condition[2][4] / 100,
            };
          });
          this.threshold = [...slathreshold];
        });
      },
      // 展示完整流程
      viewProcess(val) {
        this.$refs.leftTicketContent.changeDialogStatus(val);
      },
      // 单据完成评价
      ticketFinishAppraise() {
        this.$refs.ticketHeader.onTicketBtnClick('comment');
      },
      // 是否需要循环
      isNeedToLoop() {
        const isNeedLoop = this.nodeList.some(item => {
          // 标准运维任务节点为 RUNNING 状态时
          if (['TASK', 'TASK-SOPS'].includes(item.type) && item.status === 'RUNNING') {
            return true;
          }
          // 排队状态
          if (item.status === 'QUEUEING') {
            return true;
          }
          // 特殊场景，等待当前操作人处理任务
          if (item.is_schedule_ready === false) {
            return true;
          }
          // 会签或审批节点提交后，当前处理人task 为 RUNNING|EXECUTED状态，则继续轮询 FINISHED
          const currUserDealTask = (item.tasks && item.tasks.find(task => {
            const splitName = task.processor.replace(/\((.?)\)/, '');
            return splitName === window.username;
          })) || {};
          if (['SIGN', 'APPROVAL'].includes(item.type) && ['RUNNING', 'EXECUTED'].includes(currUserDealTask.status)) {
            return true;
          }
          return false;
        });
        return isNeedLoop;
      },
      // 判断当前状态是否需要轮询
      initTicketTimer() {
        this.ticketTimer = setInterval(() => {
          const isNeedLoop = this.isNeedToLoop();
          if (isNeedLoop && this.ticketInfo.current_status !== 'FINISHED') {
            this.startTicketTimer();
          } else {
            this.clearTicketTimer();
          }
        }, 5000);
      },
      clearTicketTimer() {
        clearInterval(this.ticketTimer);
        this.ticketTimer = null;
      },
      // 开始循环
      startTicketTimer() {
        const params = {
          id: this.ticketId,
          token: this.token || undefined,
        };
        this.$store.dispatch('deployOrder/getOnlyTicketNodeInfo', params).then(async res => {
          const newNodeList = res.data;
          const oldNodeList = this.nodeList;
          const nodeStatusHasUpdate = newNodeList.some(node => !oldNodeList.find(item => this.isSameStatusNode(node, item)));
          if (nodeStatusHasUpdate) {
            // 节点状态有更新
            this.nodeList = newNodeList;
            this.updateNodeList(newNodeList);
            this.getTriggers();
            await this.getTicketDetailInfo();
            this.initCurrentStepData();
            await this.getCurrTickeStatusColor();
          }
        });
      },
      // 获取单据信息详情
      async getTicketDetailInfo() {
        this.loading.ticketLoading = true;
        const params = {
          id: this.ticketId,
          step_id: this.$route.query.step_id || undefined,
          token: this.token || undefined,
        };

        await this.$store.dispatch('change/getOrderDetails', params).then((res) => {
          this.ticketInfo = res.data;
        })
          .catch((res) => {
            // 显示 404 页面
            this.ticketErrorMessage = res.data.code === 'OBJECT_NOT_EXIST' ? this.$t('m.wiki["单据不存在或已被撤销"]') : this.$t('m.wiki["您没有权限访问"]');
          })
          .finally(() => {
            this.loading.ticketLoading = false;
          });
      },
      // 获取单据节点的详情
      getNodeList() {
        this.loading.nodeInfoLoading = true;
        const params = {
          id: this.ticketId,
          token: this.token || undefined,
        };
        return this.$store.dispatch('deployOrder/getOnlyTicketNodeInfo', params).then((res) => {
          this.updateNodeList(res.data);
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.loading.nodeInfoLoading = false;
          });
      },
      // 更新节点信息
      updateNodeList(newNodeList) {
        const copyList = deepClone(newNodeList);
        if (this.openFunction.FIRST_STATE_SWITCH) {
          this.firstStateFields = copyList.find(item => item.state_id === Number(this.ticketInfo.first_state_id)).fields;
          this.firstStateFields.forEach(item => {
            this.$set(item, 'val', (item.value || ''));
            this.conditionField(item, this.firstStateFields);
          });
        }
        copyList.forEach(item => {
          if (item.status === 'AUTO_SUCCESS') {
            item.status = 'FINISHED';
          }
          if (item.type === 'APPROVAL') {
            item.fields.forEach(field => {
              field.name = this.approveDict[field.name] || field.name;
              field.choice.forEach(choice => {
                choice.name = this.approveDict[choice.name] || choice.name;
              });
            });
          }
        });
        this.nodeList = copyList;
        this.$store.commit('deployOrder/setNodeList', this.nodeList);
        this.initCurrentStepData();
      },
      // 获取当前单据状态颜色
      getCurrTickeStatusColor() {
        const status = this.ticketInfo.current_status;
        const type = this.ticketInfo.service_type;

        this.$store.dispatch('ticketStatus/getTypeStatus', { type }).then((res) => {
          const item = res.data.find(m => m.key === status);
          this.$set(this.headerInfo, 'statusColor', item ? item.color_hex : '');
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      // 获取单据手动触发器
      getTriggers() {
        this.$store.dispatch('trigger/getTicketHandleTriggers', { id: this.ticketId }).then(res => {
          this.nodeTriggerList = res.data.filter(trigger => trigger.signal_type === 'STATE');
          this.ticketTriggerList = res.data.filter(trigger => trigger.signal_type === 'FLOW');
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 初始化当前步骤列表信息
      initCurrentStepData() {
        this.$refs.leftTicketContent && this.$refs.leftTicketContent.initCurrentStepData();
      },
      // 重新加载
      reloadTicket() {
        this.reload();
      },
      // 按下拖拽线
      handleLineMouseDown(e) {
        document.addEventListener('mouseup', this.handleMouseUp, false);
        document.addEventListener('mousemove', this.handleLineMouseMove, false);

        const minTabWidth = document.querySelector('.ticket-container-right .bk-tab-header .bk-tab-label-wrapper .bk-tab-label-list').clientWidth;
        const currTabWidth = document.querySelector('.ticket-container-right .bk-tab-header').clientWidth;
        if (!this.dragLine.maxLength) {
          // 误差
          const offset = 4;
          this.dragLine.maxLength = currTabWidth - minTabWidth - offset;
        }
        this.dragLine.startX = e.pageX;
        this.dragLine.canMove = true;
      },
      // 鼠标弹起
      handleMouseUp() {
        document.removeEventListener('mouseup', this.handleMouseUp, false);
        document.removeEventListener('mousemove', this.handleLineMouseMove, false);
        this.dragLine.base = this.dragLine.move;
        this.dragLine.canMove = false;
      },
      // 拖拽分屏
      handleLineMouseMove(e) {
        if (!this.dragLine.canMove) {
          return;
        }
        const el = document.getElementById('ticketContainerRight');
        const { startX, base, maxLength } = this.dragLine;
        const offsetX = e.pageX - startX;
        const moveX = base + offsetX;
        // 正向超出可移动最大长度，隐藏右侧面板
        if (offsetX > 0 && maxLength - moveX <= 0) {
          this.showRightTabs = false;
          this.dragLine.move = maxLength;
          el.style.display = 'none';
          return;
        }
        window.requestAnimationFrame(() => {
          this.dragLine.move = moveX;
          el.style.width = `calc(320px - ${moveX}px)`;
        });
      },
      onShowRightContent() {
        this.showRightTabs = true;
        // 还原到最小宽度
        this.$nextTick(() => {
          const el = document.getElementById('ticketContainerRight');
          el.style.width = `calc(320px - ${this.dragLine.base}px)`;
        });
      },
      goToHome() {
        this.$router.push({
          name: 'home',
        });
        location.reload();
      },
    },
  };
</script>

<style lang="scss" scoped>
@import '../../../scss/mixins/scroller.scss';
.ticket-detail-panel {
    width: 100%;
    height: 100%;
    min-width: 900px;
}
.ticket-container {
    display: flex;
    padding: 24px;
    height: calc(100% - 50px);
    .ticket-container-left {
        flex: 1;
        margin-right: 22px;
        height: 100%;
        overflow: auto;
        background-color: #f5f7fa;
        @include scroller;
    }
    .drag-line {
        width: 2px;
        height: 100%;
        cursor: col-resize;
        &:hover {
            background-color: #3a84ff;
        }
    }
    .show-right-icon {
        position: absolute;
        top: 50%;
        right: -14px;
        width: 27px;
        height: 100px;
        background: #c4c6cc;
        border-radius: 14px;
        transform: translateY(-50%);
        line-height: 100px;
        color: #fff;
        cursor: pointer;
        font-size: 12px;
        &:hover {
            background-color: #3a84ff;
        }
        .icon-angle-left {
            position: absolute;
            left: -4px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 20px;
        }
    }
    .ticket-container-right {
        width: 320px;
        margin-left: 4px;
        height: 100%;
        display: flex;
        flex-direction: column;
        .sla-information {
            transition: all 0.5s;
            box-shadow: 0px 2px 6px 0px rgba(0,0,0,0.1);
            background: #ffffff;
            margin-bottom: 24px;
            .sla-view {
                height: 54px;
                line-height: 20px;
                padding: 17px 24px;
                .sla-title {
                    font-size: 14px;
                    font-weight: 700;
                    display: inline-block;
                    color: #63656e;
                    i {
                        color: #c4c6cc;
                        display: inline-block;
                        font-size: 12px;
                        margin-right: 8px;
                    }
                }
                .view-sla-rule {
                    cursor: pointer;
                    float: right;
                    color: #3a84ff;
                    font-size: 12px;
                }
            }
        }
        .hide {
            height: 54px;
        }
        .right-ticket-tabs {
            flex: 1;
        }
    }
}
.processed-info-content {
  .header-area {
    display: flex;
    align-items: center;
    padding: 0 24px;
    font-size: 18px;
    font-weight: 700;
    color: #313238;
    .info-icon {
      margin-right: 8px;
      color: #3a84ff;
    }
  }
  .section-title {
    margin: 24px 0 18px;
    padding: 0 24px 0 50px;
    font-size: 14px;
    font-weight: 700;
    color: #313238;
  }
  .ticket-detail {
    padding: 0 24px;
    max-height: calc(100vh * 0.6 - 100px);
    overflow: auto;
    @include scroller;
  }
  .form-item {
    display: flex;
    align-items: flex-start;
    margin-bottom: 16px;
    color: #63656e;
    .label {
      flex-shrink: 0;
      padding-right: 2px;
      width: 100px;
      text-align: right;
      word-break: break-all;
    }
    .value-content {
      flex: 1;
      word-break: break-all;
      margin-left: 20px;
      overflow: hidden;
    }
    .custom-form-wrapper {
      .table-item {
        margin-bottom: 12px;
      }
      .table-label {
        margin-bottom: 8px;
        font-size: 14px;
        font-weight: 600;
      }
    }
  }
  .action-btn {
    padding: 12px 24px 0;
    text-align: right;
  }
}

</style>
<style lang="scss">
  @import '../../../scss/mixins/scroller.scss';
  .processed-info-dialog.bk-dialog-wrapper .bk-dialog-body {
    padding: 3px 0 24px;
  }
</style>
