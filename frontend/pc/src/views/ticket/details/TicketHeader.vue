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
  <header class="ticket-header">
    <arrows-left-icon @click="onBackClick"></arrows-left-icon>
    <span
      :style="{ backgroundColor: headerInfo.statusColor }"
      :title="ticketInfo.current_status_display"
      class="ticket-status"
    >
      {{
        localeCookie
          ? ticketInfo.current_status
          : ticketInfo.current_status_display
      }}
    </span>
    <span
      class="ticket-status comments-info"
      v-if="ticketInfo.is_commented || ticketInfo.can_commen"
    >
      <span v-if="ticketInfo.is_commented">{{
        $t('m.newCommon["已评价"]')
      }}</span>
      <span v-if="ticketInfo.can_comment">{{
        $t('m.newCommon["待评论"]')
      }}</span>
    </span>
    <!-- 关注 -->
    <span class="bk-operation-focus">
      <bk-popover
        :content="
          !hasAttention
            ? $t(`m.manageCommon['关注单据']`)
            : $t(`m.manageCommon['取消关注']`)
        "
        :interactive="false"
        placement="top"
      >
        <i
          :class="[
            'bk-itsm-icon',
            !hasAttention ? 'icon-rate' : 'icon-favorite'
          ]"
          @click="onAttention"
        >
        </i>
      </bk-popover>
    </span>
    <!-- SN单号 -->
    <span class="ticket-sn mr10">{{ ticketInfo.sn }}</span>
    <!-- 标题 -->
    <span class="ticket-title" :title="ticketInfo.title">
      {{ ticketInfo.title || "--" }}
    </span>
    <div class="operation-group">
      <!-- 刷新 -->
      <bk-button
        data-test-id="ticket_button_refreshTicketDetail"
        size="small"
        class="mr10 operation-refresh"
        :class="{ rotate: rotate, 'not-rotate': !rotate }"
        icon="icon-refresh"
        theme="default"
        @click="onRefreshBtnClick"
      >
        {{ $t(`m.newCommon["刷新"]`) }}
      </bk-button>
      <bk-popover
        :content="$t(`m.tickets['只有提单人才能撤单']`)"
        :disabled="ticketInfo.can_withdraw"
      >
        <bk-button
          data-test-id="ticket_button_removeTicket"
          size="small"
          class="mr10"
          theme="default"
          :disabled="!ticketInfo.can_withdraw"
          @click="onTicketBtnClick('widthdraw')"
        >
          {{ $t(`m.newCommon["撤单"]`) }}
        </bk-button>
      </bk-popover>
      <bk-popover
        :content="ticketInfo.can_supervise ? $t(`m.newCommon['执行催办操作后，将发送信息至处理人。']`) : disabledText"
      >
        <bk-button
          data-test-id="ticket_button_superviseTicket"
          size="small"
          class="mr10"
          theme="default"
          :disabled="!ticketInfo.can_supervise"
          @click="onTicketBtnClick('supervise')"
        >
          {{ $t(`m.newCommon["催办"]`) }}
        </bk-button>
      </bk-popover>
      <bk-popover
        :content="getDisabledContentText(ticketInfo.is_commented)"
        :disabled="
          !(ticketInfo.is_commented || !ticketInfo.can_comment)
        "
      >
        <bk-button
          data-test-id="ticket_button_appraiseTicket"
          v-if="Number(ticketInfo.comment_id) !== -1"
          size="small"
          class="mr10"
          theme="default"
          :disabled="
            ticketInfo.is_commented ||
              !ticketInfo.can_comment ||
              ticketInfo.comment_id === -1
          "
          @click="onTicketBtnClick('comment')"
        >
          {{ $t(`m.newCommon["评价"]`) }}
        </bk-button>
      </bk-popover>
      <bk-dropdown-menu
        ref="dropdown"
        :align="'right'"
        :font-size="'medium'"
        class="bk-dropdown-menu-cus mr10"
        @show="isDropdownShow = true"
        @hide="isDropdownShow = false"
      >
        <div
          class="dropdown-trigger-btn"
          slot="dropdown-trigger"
          style="width: auto"
        >
          <span>{{ $t(`m.newCommon['更多操作']`) }}</span>
          <i
            :class="[
              'bk-icon icon-angle-down',
              { 'icon-flip': isDropdownShow }
            ]"
          ></i>
        </div>
        <ul class="bk-dropdown-list-cus" slot="dropdown-content">
          <li>
            <bk-button
              data-test-id="ticket_button_ticketPrint"
              class="bk-dropdown-list-btn"
              theme="default"
              :text="true"
              @click="onTicketBtnClick('print')"
            >
              {{ $t(`m.newCommon["打印"]`) }}
            </bk-button>
          </li>
          <li>
            <bk-popover
              :content="disabledText"
              :disabled="
                ticketInfo.can_operate &&
                  ticketInfo.current_status !== 'SUSPENDED'
              "
              placement="left-end"
            >
              <bk-button
                data-test-id="ticket_button_ticketPending"
                class="bk-dropdown-list-btn"
                theme="default"
                :text="true"
                :disabled="
                  !(
                    ticketInfo.can_operate &&
                    ticketInfo.current_status !==
                    'SUSPENDED'
                  )
                "
                @click="onTicketBtnClick('suspend')"
              >
                {{ $t(`m.newCommon["挂起"]`) }}
              </bk-button>
            </bk-popover>
          </li>
          <li>
            <bk-popover
              :content="disabledText"
              :disabled="
                ticketInfo.can_operate &&
                  ticketInfo.current_status === 'SUSPENDED'
              "
              placement="left-end"
            >
              <bk-button
                data-test-id="ticket_button_ticketRecover"
                class="bk-dropdown-list-btn"
                :text="true"
                :disabled="
                  !(
                    ticketInfo.can_operate &&
                    ticketInfo.current_status ===
                    'SUSPENDED'
                  )
                "
                @click="onTicketBtnClick('restore')"
              >
                {{ $t(`m.newCommon["恢复"]`) }}
              </bk-button>
            </bk-popover>
          </li>
          <li>
            <bk-popover
              :content="disabledText"
              :disabled="ticketInfo.can_close"
              placement="left-end"
            >
              <bk-button
                data-test-id="ticket_button_ticketClose"
                class="bk-dropdown-list-btn"
                :text="true"
                :disabled="!ticketInfo.can_close"
                @click="onTicketBtnClick('close')"
              >
                {{ $t(`m.newCommon["关单"]`) }}
              </bk-button>
            </bk-popover>
          </li>
          <!-- 触发器列表 -->
          <li
            v-for="(ticketTrigger, index) in ticketTriggerList"
            :key="index"
          >
            <bk-popover
              :content="disabledText"
              :disabled="ticketInfo.can_operate"
              placement="left-end"
            >
              <bk-button
                data-test-id="ticket_button_trigger"
                class="bk-dropdown-list-btn"
                :text="true"
                :disabled="!ticketInfo.can_operate"
                @click="
                  onTicketBtnClick('trigger', ticketTrigger)
                "
              >
                {{ ticketTrigger.display_name }}
              </bk-button>
            </bk-popover>
          </li>
          <li>
            <bk-button
              data-test-id="ticket_button_ticketService"
              class="bk-dropdown-list-btn"
              :text="true"
              @click="onTicketBtnClick('service')"
            >
              {{ $t(`m["服务"]`) }}
            </bk-button>
          </li>
        </ul>
      </bk-dropdown-menu>
    </div>
    <!-- 单据触发器 dialog -->
    <ticket-trigger-dialog
      ref="ticketTriggerDialog"
      @init-info="triggerSuccessCallback"
    >
    </ticket-trigger-dialog>
    <!-- 评价弹窗 -->
    <evaluation-ticket-modal
      ref="evaluationModal"
      :ticket-info="ticketInfo"
      @submitSuccess="evaluationSubmitSuccess"
    >
    </evaluation-ticket-modal>
    <!-- suspend|close|restore -->
    <step-submit-dialog
      ref="ticketOperate"
      :ticket-info="ticketInfo"
      :ticket-operate-type="ticketOperateType"
      @submitSuccess="reloadTicket"
    >
    </step-submit-dialog>
  </header>
</template>

<script>
  import TicketTriggerDialog from '@/components/ticket/TicketTriggerDialog.vue';
  import EvaluationTicketModal from '@/components/ticket/evaluation/EvaluationTicketModal.vue';
  import StepSubmitDialog from './StepSubmitDialog.vue';
  import { errorHandler } from '@/utils/errorHandler';
  import cookie from 'cookie';

  export default {
    name: 'TicketHeader',
    components: {
      StepSubmitDialog,
      TicketTriggerDialog,
      EvaluationTicketModal,
    },
    props: {
      ticketInfo: {
        type: Object,
        default: () => ({}),
      },
      headerInfo: {
        type: Object,
        default: () => ({}),
      },
      ticketTriggerList: {
        type: Array,
        default: () => ({}),
      },
    },
    data() {
      return {
        isSubmitting: false,
        hasAttention: false,
        rotate: false,
        isDropdownShow: false,
        disabledText: this.$t('m.newCommon["暂无权限或单据已结束"]'),
        ticketOperateType: '',
        localeCookie: false,
      };
    },
    mounted() {
      this.initData();
      this.localeCookie =            cookie.parse(document.cookie).blueking_language !== 'zh-cn';
    },
    methods: {
      initData() {
        this.hasAttention = this.ticketInfo.followers
          ? this.ticketInfo.followers.some(name => name === window.username)
          : false;
      },
      // 关注
      onAttention() {
        const { id } = this.ticketInfo;
        const params = {
          attention: !this.hasAttention,
        };
        const bkMessage = this.hasAttention
          ? this.$t('m.manageCommon[\'取消关注成功~\']')
          : this.$t('m.manageCommon[\'添加关注成功~\']');
        this.$store
          .dispatch('deployOrder/setAttention', { params, id })
          .then(() => {
            this.$bkMessage({
              message: bkMessage,
              theme: 'success',
              ellipsisLine: 0,
            });
            this.hasAttention = !this.hasAttention;
          })
          .catch((res) => {
            this.$bkMessage({
              message: res.data.msg,
              theme: 'error',
              ellipsisLine: 0,
            });
          });
      },
      // 单据操作按钮点击
      onTicketBtnClick(type, item) {
        this.$refs.dropdown.hide();

        switch (type) {
          case 'print': {
            const { href } = this.$router.resolve({
              path: `/printOrder?ticket_id=${this.ticketInfo.id}`,
            });
            window.open(href, '_blank');
            break;
          }
          case 'trigger':
            {
              this.openTriggerDialog(item);
            }
            break;
          case 'comment':
            {
              this.$refs.evaluationModal.show();
            }
            break;
          case 'service':
            {
              this.JumpCurTicketService();
            }
            break;
          default: {
            this.ticketOperatingHandler(type);
          }
        }
      },
      JumpCurTicketService() {
        // 判断服务是否存在
        this.$store.dispatch('service/getServiceDetail', this.ticketInfo.service_id).then(res => {
          if (res.result) {
            const routeData = this.$router.resolve({ path: '/project/service/edit/basic', query: { project_id: this.$store.state.project.id, serviceId: this.ticketInfo.service_id } });
            window.open(routeData.href, '_blank');
          }
        });
      },
      // 单据操作
      ticketOperatingHandler(type) {
        // 催办,撤单
        if (type === 'widthdraw' || type === 'supervise') {
          this.confirmOperating(type);
        }
        if (type === 'suspend' || type === 'close' || type === 'restore') {
          this.ticketOperateType = type;
          this.$nextTick(() => {
            this.$refs.ticketOperate.openCel();
          });
        }
      },
      // 二次确认操作
      confirmOperating(type) {
        const infoMap = {
          widthdraw: {
            title: this.$t('m.newCommon["确认撤销此单据？"]'),
            instructions: this.$t('m.newCommon["撤销后，您仍然可以在“我的申请单”中查看单据信息。"]'),
            dispatchAcationPath: 'deployOrder/widthdrawOrder',
            successText: this.$t('m.newCommon["撤单成功"]'),
            params: {
              state_id: this.ticketInfo.id,
            },
          },
          supervise: {
            title: this.$t('m.newCommon["确认催办该节点？"]'),
            instructions: this.$t('m.newCommon["执行催办操作后，将发送信息至处理人。"]'),
            dispatchAcationPath: 'change/submitSupervise',
            successText: this.$t('m.newCommon["催办成功"]'),
            params: {},
          },
        };
        this.$bkInfo({
          type: 'warning',
          title: infoMap[type].title,
          subTitle: infoMap[type].instructions,
          confirmFn: () => {
            this.submitOperating(type, infoMap);
          },
        });
      },
      // 提交操作
      submitOperating(type, infoMap) {
        this.isSubmitting = true;
        const { id } = this.ticketInfo;
        const { dispatchAcationPath, params, successText } = infoMap[type];
        this.$store
          .dispatch(dispatchAcationPath, { params, id })
          .then(() => {
            this.$bkMessage({
              message: successText,
              theme: 'success',
            });
            this.reloadTicket();
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isSubmitting = false;
          });
      },
      // 单据手动触发器
      openTriggerDialog(trigger) {
        this.$refs.ticketTriggerDialog.openDialog(trigger);
      },
      reloadTicket() {
        this.$emit('reloadTicket');
      },
      triggerSuccessCallback() {
        this.reloadTicket();
      },
      onRefreshBtnClick() {
        this.rotate = !this.rotate;
        setTimeout(() => {
          this.reloadTicket();
        }, 500);
      },
      evaluationSubmitSuccess() {
        this.reloadTicket();
      },
      getDisabledContentText(isCommented) {
        return isCommented
          ? this.$t('m.newCommon["已评价"]')
          : this.$t('m.newCommon["单据处理未完成或没有评价权限，不能评价！"]');
      },
      onBackClick() {
        const from = this.$route.query.from || '';
        if (from === 'projectTicket' || from === '') {
          this.$router.push({
            name: 'projectTicket',
            query: {
              project_id: this.$route.query.project_id,
            },
          });
        } else if (from === 'created') {
          this.$router.push({
            name: 'myCreatedTicket',
          });
        } else {
          this.$router.push({
            name: from,
          });
        }
      },
    },
  };
</script>

<style lang="scss" scoped>
.ticket-header {
    display: flex;
    align-items: center;
    padding: 0 19px 0 14px;
    height: 50px;
    box-shadow: 0px 2px 2px 0px rgba(0, 0, 0, 0.1);
    background: #ffffff;
    .ticket-status {
        margin-right: 10px;
        padding: 3px 6px;
        max-width: 75px;
        color: #fff;
        font-size: 12px;
        background-color: #e1ecff;
        text-overflow: ellipsis;
        white-space: nowrap;
        overflow: hidden;
        &.comments-info {
            padding: 1px 4px;
            color: #3a84ff;
            border: 1px solid #3a84ff;
            background-color: #fff;
        }
    }
    .bk-operation-focus {
        margin-top: -4px;
        margin-right: 10px;
        font-size: 16px;
        cursor: pointer;
        .icon-rate {
            font-size: 16px;
            color: #979ba5;
            &:hover {
                color: #ffb848;
                &::before {
                    content: "\E1F1";
                }
            }
        }
        .icon-favorite {
            color: #ffb848;
            cursor: pointer;
            font-size: 16px;
        }
    }
    .ticket-sn {
        color: #63656e;
        font-size: 16px;
        font-weight: bold;
    }
    .ticket-title {
        flex: 1;
        color: #63656e;
        font-size: 16px;
        font-weight: bold;
        text-overflow: ellipsis;
        white-space: nowrap;
        overflow: hidden;
    }
    .operation-group {
        margin-left: auto;
        .operation-refresh {
            /deep/ .icon-refresh {
                transition: all 1s;
                font-size: 14px;
                vertical-align: 1px;
            }
            &.rotate {
                /deep/ .icon-refresh {
                    transform: rotate(360deg);
                }
            }
            &.not-rotate {
                /deep/ .icon-refresh {
                    transform: rotate(0);
                }
            }
        }
        .dropdown-trigger-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #c4c6cc;
            height: 26px;
            min-width: 68px;
            font-size: 12px;
            border-radius: 2px;
            padding: 0 15px;
            color: #63656e;
        }
        .dropdown-trigger-btn.bk-icon {
            font-size: 16px;
        }
        .dropdown-trigger-btn .bk-icon {
            font-size: 18px;
        }
        .dropdown-trigger-btn:hover {
            cursor: pointer;
            border-color: #979ba5;
        }
        .bk-dropdown-menu-cus {
            /deep/ .bk-dropdown-content {
                overflow: visible;
            }
            .bk-dropdown-list-cus {
                max-height: 400px;
                li {
                    padding: 4px 18px;
                    .bk-dropdown-list-btn {
                        width: 100%;
                        font-size: 12px;
                        text-align: left;
                        &:not(.is-disabled) {
                            color: #63656e;
                            &:hover {
                                color: #3a84ff;
                            }
                        }
                    }
                }
            }
        }
    }
}
</style>
