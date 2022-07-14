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
  <div class="right-content">
    <bk-tab
      data-test-id="ticket_tab_rightMenu"
      :active.sync="activeTab"
      type="unborder-card"
      ext-cls="right-tiket-tabs"
    >
      <bk-tab-panel name="log" :label="$t(`m.newCommon['流水日志']`)">
        <log-tab
          v-if="activeTab === 'log'"
          :ticket-info="ticketInfo"
          :node="nodeList"
          :is-show-sla="isShowSla"
          @ticketFinishAppraise="$emit('ticketFinishAppraise')"
          @viewProcess="viewProcess"
        >
        </log-tab>
      </bk-tab-panel>
      <!-- 待设计稿 -->
      <!-- <bk-tab-panel
                name="log"
                :label="$t(`m.newCommon['流转进程']`)">
                <log-tab
                    v-if="activeTab === 'process'"
                    :ticket-info="ticketInfo"
                    @ticketFinishAppraise="$emit('ticketFinishAppraise')"
                    @viewProcess="viewProcess">
                </log-tab>
            </bk-tab-panel> -->
      <template v-if="hasNodeOptAuth">
        <bk-tab-panel
          name="all-task"
          :label="$t(`m.newCommon['所有任务']`)"
        >
          <all-task-tab
            v-if="activeTab === 'all-task'"
            :ticket-info="ticketInfo"
          >
          </all-task-tab>
        </bk-tab-panel>
        <bk-tab-panel
          name="triggerLog"
          :label="$t(`m.task['触发器记录']`)"
        >
          <task-history
            v-if="activeTab === 'triggerLog'"
            :is-show-sla="isShowSla"
            :basic-infomation="ticketInfo"
            :node-list="nodeList"
          ></task-history>
        </bk-tab-panel>
        <bk-tab-panel
          v-if="ticketInfo.can_invite_followers"
          name="email-notice"
          :label="$t(`m.newCommon['邮件通知']`)"
        >
          <email-notice-tab
            v-if="activeTab === 'email-notice'"
            :ticket-info="ticketInfo"
          >
          </email-notice-tab>
        </bk-tab-panel>
        <bk-tab-panel
          v-if="Number(ticketInfo.comment_id) !== -1"
          name="comment"
          :label="$t(`m.newCommon['评价']`)"
        >
          <comment-tab
            v-if="activeTab === 'comment'"
            :ticket-info="ticketInfo"
          >
          </comment-tab>
        </bk-tab-panel>
        <bk-tab-panel
          v-if="openFunction.CHILD_TICKET_SWITCH"
          name="mother-child"
          :label="$t(`m.newCommon['母子单']`)"
        >
          <div
            class="bk-log-flow"
            v-if="activeTab === 'mother-child'"
          >
            <inherit-ticket
              :ticket-info="ticketInfo"
            ></inherit-ticket>
          </div>
        </bk-tab-panel>
        <bk-tab-panel
          name="related-ticket"
          :label="$t(`m.newCommon['关联单']`)"
        >
          <associated-tab
            v-if="activeTab === 'related-ticket'"
            :ticket-info="ticketInfo"
          >
          </associated-tab>
        </bk-tab-panel>
      </template>
    </bk-tab>
  </div>
</template>

<script>
  import { mapState } from 'vuex';
  import LogTab from './LogTab.vue';
  import AssociatedTab from './AssociatedTab/AssociatedTab.vue';
  import InheritTicket from './InheritTicketTab.vue';
  import EmailNoticeTab from './EmailNoticeTab.vue';
  import CommentTab from './CommentTab.vue';
  import AllTaskTab from './AllTaskTab.vue';
  import taskHistory from '../taskInfo/taskHistory.vue';

  export default {
    name: 'RightTiketTabs',
    components: {
      LogTab,
      AssociatedTab,
      InheritTicket,
      EmailNoticeTab,
      CommentTab,
      AllTaskTab,
      taskHistory,
    },
    props: {
      ticketInfo: {
        type: Object,
        default: () => ({}),
      },
      nodeList: {
        type: Array,
        default: () => [],
      },
      hasNodeOptAuth: Boolean,
      isShowSla: Boolean,
    },
    data() {
      return {
        activeTab: 'log',
        isUseSla: true,
        isResponseTimeout: true,
        isDisposeTimeout: false,
        isNormal: false, // sla正常时间内
      };
    },
    computed: {
      ...mapState({
        openFunction: state => state.openFunction,
      }),
    },
    methods: {
      // 跳转对应项目下sla
      viewSlaRule() {
        this.$router.push({
          name: 'slaAgreement',
          query: {
            project_id: this.$route.query.project_id || 0,
          },
        });
      },
      viewProcess(val) {
        this.$emit('viewProcess', val);
      },
    },
  };
</script>

<style lang="scss" scoped>
@import "../../../../scss/mixins/scroller.scss";
.icon-itsm-icon-mark-eight {
    color: red;
}
.icon-itsm-icon-three-eight {
    color: #ff9c01;
}
.right-content {
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-shadow: 0px 2px 6px 0px rgba(0, 0, 0, 0.1);
}
.right-tiket-tabs {
    flex: 1;
    background: #ffffff;
    /deep/ .bk-tab-section {
        overflow: auto;
        @include scroller;
    }
    /deep/ .bk-tab-label-item {
        min-width: auto;
    }
}
</style>
