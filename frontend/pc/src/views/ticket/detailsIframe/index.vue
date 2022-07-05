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
  <div class="ticket-detail-iframe">
    <left-ticket-content
      v-if="!ticketErrorMessage"
      ref="leftTicketContent"
      :loading="loading"
      :ticket-info="ticketInfo"
      :has-node-opt-auth="hasNodeOptAuth"
      :is-show-comment="isShowComment"
      :node-list="nodeList"
      :first-state-fields="firstStateFields"
      :node-trigger-list="nodeTriggerList"
      :ticket-id="ticketId">
    </left-ticket-content>
    <!-- 403 | 404 -->
    <no-ticket-content v-else
      :message="ticketErrorMessage">
    </no-ticket-content>
    <bk-dialog v-model="isShowNoticeDialog"
      theme="primary"
      :mask-close="false"
      header-position="left"
      title="提示"
      @confirm="onNoticeConfirm">
      {{$t(`m.newCommon['您要处理的节点已被']`)}} {{ noticeInfo.processed_user }} {{$t(`m.newCommon['处理完成，可在流转日志中查看详情。']`)}}
    </bk-dialog>
  </div>
</template>

<script>
  import NoTicketContent from '../details/components/NoTicketContent.vue';
  import leftTicketContent from '../details/leftTicketContent.vue';
  import { errorHandler } from '../../../utils/errorHandler';
  import { deepClone } from '../../../utils/util';
  import { mapState } from 'vuex';
  import fieldMix from '@/views/commonMix/field.js';

  export default {
    name: 'TicketDetailsIframe',
    components: {
      NoTicketContent,
      leftTicketContent,
    },
    mixins: [fieldMix],
    inject: ['reload'],
    provide() {
      return {
        reloadTicket: this.reloadTicket,
      };
    },
    data() {
      return {
        loading: {
          ticketLoading: true,
          nodeInfoLoading: false,
        },
        ticketId: this.$route.query.id,
        ticketErrorMessage: '',
        // 通知链接进入，但节点已被其他人处理提示
        isShowNoticeDialog: false,
        ticketTimer: null, // 单据详情轮询器
        noticeInfo: {
          is_processed: false,
          processed_user: '',
        },
        ticketInfo: {},
        nodeTriggerList: [],
        firstStateFields: [],
        nodeList: [],
        isShowComment: false,
        hasNodeOptAuth: false,
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
    created() {

    },
    async mounted() {
      await this.initData();
      if (this.$route.query.cache_key) { // 通知链接进入
        this.getTicketNoticeInfo();
      }
      if (this.$refs.leftTicketContent && this.$refs.leftTicketContent.currentStepList[0]) {
        this.hasNodeOptAuth = this.$refs.leftTicketContent.currentStepList.some(item => item.can_operate);
        this.$store.commit('ticket/setHasTicketNodeOptAuth', this.hasNodeOptAuth);
      }
    },
    beforeDestroy() {
      this.clearTicketTimer();
    },
    methods: {
      async initData() {
        this.ticketId = this.$route.query.id;
        await this.getTicketDetailInfo();
        if (this.ticketErrorMessage) {
          this.clearTicketTimer();
          return false;
        }
        this.getTriggers();
        await this.getNodeList();
        this.initCurrentStepData();
        this.initTicketTimer();
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
      // 获取单据信息详情
      async getTicketDetailInfo() {
        this.loading.ticketLoading = true;
        const params = {
          id: this.ticketId,
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
      getTicketNoticeInfo() {
        this.$store.dispatch('deployOrder/getTicketNoticeInfo', {
          params: { cache_key: this.$route.query.cache_key },
        }).then(res => {
          if (res.data && res.data.is_processed) {
            this.noticeInfo = res.data;
            this.isShowNoticeDialog = true;
          } else {
            // 删除 url cache_key
            this.onNoticeConfirm();
          }
        })
          .catch((res) => {
            errorHandler(res, this);
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
            this.$set(item, 'showFeild', !!item.show_type);
            this.$set(item, 'val', (item.value || ''));
            this.conditionField(item, this.firstStateFields);
          });
        }
        copyList.forEach(item => {
          if (item.status === 'AUTO_SUCCESS') {
            item.status = 'FINISHED';
          }
        });
        this.nodeList = copyList;
        this.initCurrentStepData();
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
          }
        });
      },
      // 初始化当前步骤列表信息
      initCurrentStepData() {
        this.$refs.leftTicketContent && this.$refs.leftTicketContent.initCurrentStepData();
      },
      // 获取单据手动触发器
      getTriggers() {
        this.$store.dispatch('trigger/getTicketHandleTriggers', { id: this.ticketId }).then(res => {
          this.nodeTriggerList = res.data.filter(trigger => trigger.signal_type === 'STATE');
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 确认
      onNoticeConfirm() {
        const query = deepClone(this.$route.query);
        delete query.cache_key;
        this.$router.replace({
          name: this.$route.name,
          query,
        });
      },
      clearTicketTimer() {
        clearInterval(this.ticketTimer);
        this.ticketTimer = null;
      },
      // 重新加载
      reloadTicket() {
        this.reload();
      },
    },
  };
</script>
<style lang='scss' scoped>
@import '~@/scss/mixins/scroller.scss';
.ticket-detail-iframe {
    height: 100%;
    overflow: auto;
    @include scroller;
}
</style>
