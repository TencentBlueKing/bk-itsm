<template>
  <div class="left-ticket">
    <div class="base-info-content " v-bkloading="{ isLoading: loading.nodeInfoLoading }">
      <div class="ticket-base-info">
        <div class="ticket-creator" @click="isShowBasicInfo = !isShowBasicInfo">
          <i :class="['bk-itsm-icon', isShowBasicInfo ? 'icon-xiangxia' : 'icon-xiangyou']"></i>
          <span class="ticket-title">{{ $t(`m['单据信息']`) }}</span>
          <span>{{ $t(`m['提单人']`) }}: {{ ticketInfo.creator}}</span>
          <span>{{ $t(`m['提单时间']`) }}: {{ ticketInfo.create_at}}</span>
        </div>
        <div :class="['basic-content', isShowBasicInfo ? '' : 'hide']">
          <basic-information
            ref="basicInfo"
            v-if="ticketId && !loading.ticketLoading && !loading.nodeInfoLoading"
            :basic-infomation="ticketInfo"
            :first-state-fields="firstStateFields">
          </basic-information>
        </div>
        <!-- <bk-collapse v-model="activeName">
                    <bk-collapse-item name="ticket">
                        <span class="ticket-title">提单信息</span>
                        <div class="ticket-creator">
                            <span>提单人: {{ ticketInfo.creator}}</span><span>提单时间: {{ ticketInfo.create_at}}</span>
                        </div>
                        <div slot="content" class="f13">
                            <basic-information
                                ref="basicInfo"
                                v-if="ticketId && !loading.ticketLoading && !loading.nodeInfoLoading"
                                :basic-infomation="ticketInfo"
                                :first-state-fields="firstStateFields">
                            </basic-information>
                        </div>
                    </bk-collapse-item>
                </bk-collapse> -->
      </div>
    </div>
    <div class="current-step-content" v-bkloading="{ isLoading: currentStepLoading }">
      <bk-tab :active.sync="stepActiveTab" type="unborder-card" v-if="!currentStepLoading" :validate-active="true">
        <!-- 当前步骤 -->
        <bk-tab-panel
          v-if="hasNodeOptAuth || isShowAssgin || currSetpIsIframe"
          name="currentStep"
          :label="$t(`m['单据处理']`)">
          <!-- 当前节点 -->
          <template slot="label">
            <span class="panel-name">{{ $t(`m['单据处理']`) }}</span>
            <i class="panel-count">{{ currStepNodeNum }}</i>
          </template>
          <current-steps
            v-if="!loading.ticketLoading && !loading.nodeInfoLoading"
            ref="currentNode"
            :is-show-basic-info="isShowBasicInfo"
            :loading="loading.ticketLoading"
            :basic-infomation="ticketInfo"
            :node-list="nodeList"
            :is-show-assgin="isShowAssgin"
            :current-step-list="currentStepList"
            :node-trigger-list="nodeTriggerList"
            @handlerSubmitSuccess="reloadTicket">
          </current-steps>
        </bk-tab-panel>
        <!-- 全部评论 TODO -->
        <bk-tab-panel
          v-if="isShowComment"
          name="allComments"
          :label="$t(`m.newCommon['所有评论']`)">
          <template v-slot:label>
            <span class="panel-name">{{ $t(`m.newCommon['所有评论']`) }}</span>
            <i class="panel-count">{{ commentList.length }}</i>
          </template>
          <wang-editor
            ref="comment"
            :is-show-basic-info="isShowBasicInfo"
            :comment-list="commentList"
            :comment-id="commentId"
            :ticket-info="ticketInfo"
            :ticket-id="ticketId"
            :is-page-over="isPageOver"
            :step-active-tab="stepActiveTab"
            :has-node-opt-auth="hasNodeOptAuth"
            :comment-loading="commentLoading"
            :more-loading="moreLoading"
            @addTargetComment="addTargetComment"
            @refreshComment="refreshComment"
          ></wang-editor>
        </bk-tab-panel>
      </bk-tab>
    </div>
    <!-- v-model="$store.state.ticket.ticketProcessMap" -->
    <bk-dialog
      width="1280"
      :mask-close="false"
      :close-icon="true"
      :show-footer="false"
      v-model="isShow"
      :title="$t(`m['查看完整流程']`)">
      <order-preview
        v-if="isShow"
        :basic-infomation="ticketInfo"
        :current-step-list="currentStepList"
        @reloadTicket="reloadTicket">
      </order-preview>
    </bk-dialog>
  </div>
</template>

<script>
  import BasicInformation from './BasicInformation.vue';
  import OrderPreview from './OrderPreview.vue';
  import CurrentSteps from './currentSteps/index.vue';
  import { deepClone } from '@/utils/util';
  import commonMix from '@/views/commonMix/common.js';
  import fieldMix from '@/views/commonMix/field.js';
  import apiFieldsWatch from '@/views/commonMix/api_fields_watch.js';
  import WangEditor from './comment/index.vue';

  export default {
    name: 'LeftTicketContent',
    components: {
      BasicInformation,
      OrderPreview,
      CurrentSteps,
      WangEditor,
    },
    mixins: [commonMix, fieldMix, apiFieldsWatch],
    props: {
      commentId: [Number, String],
      commentList: Array,
      loading: Object,
      ticketInfo: Object,
      nodeList: Array,
      firstStateFields: Array,
      nodeTriggerList: Array,
      ticketId: [Number, String],
      commentLoading: Boolean,
      isPageOver: Boolean,
      hasNodeOptAuth: Boolean,
      isShowAssgin: Boolean,
      moreLoading: Boolean,
      isShowComment: {
        type: Boolean,
        default() {
          return true;
        },
      },
    },
    inject: ['reloadTicket'],
    data() {
      return {
        isShowBasicInfo: true,
        baseActiveTab: 'base',
        stepActiveTab: 'currentStep',
        // 当前步骤
        currentStepList: [],
        allFieldList: [],
        currentStepLoading: false,
        activeName: ['ticket'],
        isShow: false,
      };
    },
    computed: {
      currStepNodeNum() {
        if (this.ticketInfo.is_over) { // 已结束单不显示当前步骤
          return 0;
        }
        return this.currentStepList.length;
      },
      currSetpIsIframe() {
        return this.$route.name === 'TicketDetailIframe';
      },
    },
    watch: {
      hasNodeOptAuth(val) {
        if (val) {
          this.stepActiveTab = 'currentStep';
        } else {
          this.stepActiveTab = 'allComments';
        }
      },
      isShowAssgin(val) {
        if (val) {
          this.stepActiveTab = 'currentStep';
        }
      },
      isShowBasicInfo(val) {
        this.$emit('getBacicInfoStatus', val);
      },
    },
    methods: {
      initCurrentStepData() {
        this.currentStepLoading = true;
        const oldCurrentNodeList = deepClone(this.currentStepList);
        const updateList = [];
        this.currentStepList = [];
        this.allFieldList = [];
        // 修改显示隐藏的数据
        this.nodeList.forEach(item => {
          // 过滤显示数据
          if (['RUNNING', 'SUSPEND', 'FAILED', 'SUCCESS'].includes(item.status)) {
            updateList.push(item);
          }
          this.allFieldList = this.allFieldList.concat(item.fields);
        });
        // 刷新某个步骤，避免用户填写时突然刷新打断，新旧节点 diff，如果状态未当前节点状态未更新，不应该刷新
        updateList.forEach(newNode => {
          const oldNode = oldCurrentNodeList.find(old => old.state_id === newNode.state_id);
          if (this.isSameStatusNode(newNode, oldNode) && oldNode.status === 'RUNNING') {
            this.currentStepList.push(oldNode);
          } else {
            this.currentStepList.push(newNode);
          }
        });

        // 隐藏字段显示隐藏判断逻辑
        this.allFieldList.forEach(item => {
          this.$set(item, 'showFeild', !!item.show_type);
          this.$set(item, 'val', (item.value || ''));
        });
        // 关联数据展示的逻辑处理
        this.allFieldList.forEach(item => {
          this.conditionField(item, this.allFieldList);
        });
        this.currentStepList.forEach((item) => {
          if (item.fields && item.fields.length) {
            item.fields.forEach(node => {
              this.$set(node, 'service', this.ticketInfo.service_type);
              if (node.key === 'current_status') {
                this.$set(node, 'ticket_status', this.ticketInfo.current_status);
              }
            });
            this.isNecessaryToWatch(item, '');
          }
          // 顺序会签
          if (item.type === 'SIGN' && !item.is_sequential) {
            const finishedList = item.tasks.filter(task => task.status === 'FINISHED');
            item.tasks = item.tasks.filter(task => finishedList.findIndex(finished => finished.processor === task.processor) === -1);
            item.tasks = [...finishedList, ...item.tasks];
          }
        });
        this.$nextTick(() => {
          this.currentStepLoading = false;
        });
      },
      changeDialogStatus(val) {
        this.isShow = val;
      },
      refreshComment() {
        this.$emit('refreshComment');
      },
      addTargetComment(val) {
        this.$emit('addTargetComment', val);
      },
    },
  };
</script>
<style lang='scss' scoped>
.left-ticket {
    display: flex;
    flex-direction: column;
    // height: 100%;
    .base-info-content {
        padding: 0 10px;
        min-height: 54px;
        box-shadow: 0px 2px 6px 0px rgba(0,0,0,0.1);
        background: #ffffff;
        /deep/ .bk-tab-section {
            padding: 0;
        }
        .ticket-creator {
            width: 100%;
            cursor: pointer;
            line-height: 52px;
            display: inline-block;
            color: #979BA5;
            font-size: 12px;
            .ticket-title {
                font-weight: 700;
                font-size: 14px;
                color: #63656e;
            }
            i {
                color: #c4c6cc;
                font-size: 12px;
                display: inline-block;
                height: 12px;
                width: 12px;
                margin: 0 -22px 0 24px;
            }
            span{
                margin-left: 30px;
            }
        }
        .basic-content {
            overflow: hidden;
            transition: 1s all linear;
        }
        .hide{
            height: 0;
        }
        /deep/ .bk-icon {
            // line-height: 54px;
        }
    }
    .current-step-content {
        flex: auto;
        margin-top: 24px;
        padding: 10px;
        box-shadow: 0px 2px 6px 0px rgba(0,0,0,0.1);
        background: #ffffff;
        /deep/ .bk-tab-section {
            padding: 0;
        }
        .panel-count {
            display: inline-block;
            min-width: 16px;
            height: 16px;
            padding: 0 4px;
            line-height: 16px;
            border-radius: 8px;
            text-align: center;
            font-style: normal;
            font-size: 12px;
            color: #fff;
            background-color: #C4C6CC;
        }
        /deep/ .bk-tab-label-item.active {
            .panel-count {
                color: #3a84ff;
                background: #e1ecff;
            }
        }
    }
}
/deep/ .bk-dialog {
    top: 120px;
}
.bk-order-preview {
    background-color: #f5f7fa;
}
</style>
