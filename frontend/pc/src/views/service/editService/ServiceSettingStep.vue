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
  <div class="service-setting">
    <section class="settion-card">
      <h2 class="card-title">{{ $t(`m.tickets['服务设置']`) }}</h2>
      <div class="card-content">
        <bk-form data-test-id="service_form_serviceSetting" ref="serviceSetting" form-type="vertical" :model="formData" class="service-setting-form">
          <bk-form-item :label="$t(`m.serviceConfig['可见范围']`)">
            <deal-person
              style="width: 600px;"
              class="display-range"
              form-type="inline-auto-width"
              ref="displayRange"
              :value="formData.visibleRange"
              :show-role-type-list="displayRangeTypes">
            </deal-person>
          </bk-form-item>
          <bk-form-item :label="$t(`m.tickets['撤回方式']`)" class="auto-with-form-item mt20">
            <bk-select v-model="formData.revokeWay">
              <bk-option v-for="option in revokeWayList"
                :key="option.id"
                :id="option.id"
                :name="option.name">
              </bk-option>
            </bk-select>
            <bk-select
              v-if="formData.revokeWay === 'specify_node'"
              v-model="formData.revokeState"
              :placeholder="$t(`m.treeinfo['请选择撤单节点']`)"
              :loading="nodeListLoading"
              searchable>
              <bk-option v-for="option in nodeList"
                :key="option.id"
                :id="option.id"
                :name="option.name">
              </bk-option>
            </bk-select>
          </bk-form-item>
          <bk-form-item :label="$t(`m.treeinfo['自动处理']`)">
            <bk-checkbox
              :true-value="true"
              :false-value="false"
              v-model="formData.is_auto_approve">
              {{ $t(`m['当审批节点的审批人为申请人时，自动通过']`) }}
            </bk-checkbox>
          </bk-form-item>
        </bk-form>
      </div>
    </section>
    <section class="settion-card notic-card">
      <h2 class="card-title">{{ $t(`m.tickets['通知设置']`) }}</h2>
      <div class="card-content">
        <bk-form data-test-id="service_form_serviceSettingNotification" form-type="vertical" :model="formData" class="service-setting-form">
          <bk-form-item :label="$t(`m.treeinfo['通知方式']`)">
            <bk-checkbox-group v-model="formData.notify">
              <!-- <bk-checkbox :value="'WEIXIN'" :ext-cls="'mr40'">
                                {{ $t(`m.treeinfo["企业微信"]`) }}
                            </bk-checkbox>
                            <bk-checkbox :value="'EMAIL'" :ext-cls="'mr40'">
                                {{ $t(`m.treeinfo["邮件"]`) }}
                            </bk-checkbox>
                            <bk-checkbox :value="'SMS'">
                                {{ $t('m.treeinfo["手机短信"]') }}
                            </bk-checkbox> -->
              <bk-checkbox v-for="item in noticeType" :key="item.id" :value="item.typeName" :ext-cls="'mr40'">
                {{ item.name }}
              </bk-checkbox>
            </bk-checkbox-group>
          </bk-form-item>
          <!-- <bk-form-item :label-width="80" :label="$t(`m.treeinfo['通知频率']`)" v-if="formData.notify.length">
                        <bk-radio-group v-model="formData.notify_rule">
                            <bk-radio :value="'ONCE'"
                                :ext-cls="'mr20 bk-line-radio'">
                                {{ $t('m.treeinfo["首次通知，以后不再通知"]') }}
                            </bk-radio>
                            <div class="bk-line-radio">
                                <bk-radio :value="'RETRY'" :ext-cls="'mr20 bk-float-radio'">
                                    {{ $t('m.treeinfo["首次通知后，次日起每天定时通知"]') }}
                                </bk-radio>
                                <bk-select v-if="formData.notify_rule === 'RETRY'"
                                    style="float: left; width: 200px;"
                                    v-model="formData.notify_freq"
                                    :clearable="false"
                                    searchable
                                    :font-size="'medium'">
                                    <bk-option v-for="option in frequencyList"
                                        :key="option.id"
                                        :id="option.id"
                                        :name="option.name">
                                    </bk-option>
                                </bk-select>
                            </div>
                        </bk-radio-group>
                    </bk-form-item> -->
        </bk-form>
      </div>
    </section>
    <section class="settion-card" v-if="openFunction.TRIGGER_SWITCH || openFunction.TASK_SWITCH">
      <div
        class="card-title more-configuration mt20" data-test-id="editService-div-showMoreConfig" @click="showMoreConfig = !showMoreConfig">
        <i v-if="!showMoreConfig" class="bk-icon icon-down-shape"></i>
        <i v-else class="bk-icon icon-up-shape"></i>
        <span>{{$t(`m.taskTemplate['高级配置']`)}}</span>
      </div>
      <div v-if="showMoreConfig">
        <collapse-transition>
          <div>
            <basic-card class="mt20"
              :card-label="$t(`m.newCommon['触发器']`)"
              :card-desc="$t(`m.taskTemplate['满足触发条件后要完成的特定动作']`)">
              <common-trigger-list
                :origin="'workflow'"
                :source-id="processId"
                :table="flowInfo.table">
              </common-trigger-list>
            </basic-card>
            <basic-card class="mt20"
              :card-label="$t(`m.taskTemplate['任务配置']`)"
              :card-desc="$t(`m.taskTemplate['如果需要在流程中调用标准运维的业务流程进而创建任务，请在第一步的流程字段配置中，将已有字段中的“关联业务” 字段添加至流程中。']`)">
              <TaskConfigPanel ref="taskConfigPanel" :service-info="serviceInfo"></TaskConfigPanel>
            </basic-card>
          </div>
        </collapse-transition>
      </div>
    </section>
    <bk-dialog
      v-model="slaValidateDialogShow"
      :mask-close="false"
      :show-footer="false"
      @cancel="goToServiceList">
      <div class="sla-validate-msg">
        <i class="bk-icon icon-check-circle"></i>
        <h4>{{ $t(`m['保存成功']`) }}</h4>
        <p v-for="(item, index) in slaValidateMsg" :key="index">{{ item }}</p>
        <div class="operate-btns">
          <bk-button theme="primary" @click="slaValidateDialogShow = false">{{ $t(`m['确定']`) }}</bk-button>
          <bk-button @click="goToServiceList">{{ $t(`m['取消']`) }}</bk-button>
        </div>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
  import DealPerson from '@/views/processManagement/processDesign/nodeConfigue/components/dealPerson';
  import collapseTransition from '@/views/commonMix/collapse-transition.js';
  import BasicCard from '@/components/common/layout/BasicCard.vue';
  import commonTriggerList from '@/views/processManagement/taskTemplate/components/commonTriggerList.vue';
  import TaskConfigPanel from './TaskConfigPanel.vue';
  import { errorHandler } from '../../../utils/errorHandler';
  import { mapState } from 'vuex';
  const frequencyList = [
    { id: 0, name: '00:00' },
    { id: 1, name: '01:00' },
    { id: 2, name: '02:00' },
    { id: 3, name: '03:00' },
    { id: 4, name: '04:00' },
    { id: 5, name: '05:00' },
    { id: 6, name: '06:00' },
    { id: 7, name: '07:00' },
    { id: 8, name: '08:00' },
    { id: 9, name: '09:00' },
    { id: 10, name: '10:00' },
    { id: 11, name: '11:00' },
    { id: 12, name: '12:00' },
    { id: 13, name: '13:00' },
    { id: 14, name: '14:00' },
    { id: 15, name: '15:00' },
    { id: 16, name: '16:00' },
    { id: 17, name: '17:00' },
    { id: 18, name: '18:00' },
    { id: 19, name: '19:00' },
    { id: 20, name: '20:00' },
    { id: 21, name: '21:00' },
    { id: 22, name: '22:00' },
    { id: 23, name: '23:00' },
  ];
  export default {
    name: 'ServiceSettingStep',
    components: {
      DealPerson,
      BasicCard,
      collapseTransition,
      commonTriggerList,
      TaskConfigPanel,
    },
    props: {
      serviceInfo: {
        type: Object,
        default: () => ({}),
      },
      flowInfo: {
        type: Object,
        default: () => ({}),
      },
    },
    data() {
      return {
        frequencyList,
        showMoreConfig: false,
        revokeWayList: [
          { name: '不支持撤回', id: 'not_support', key: 0 },
          { name: this.$t('m.treeinfo[\'提单后，单据未被处理流转前，提单人可以撤回\']'), id: 'before_flow', key: 2 },
          { name: this.$t('m.treeinfo[\'任何节点，提单人都可撤回单据\']'), id: 'all_node', key: 1 },
          { name: this.$t('m.treeinfo[\'指定节点前可以撤回\']'), id: 'specify_node', key: 3 },
        ],
        displayRangeTypes: ['OPEN', 'ORGANIZATION', 'GENERAL', 'API'],
        // notifyList: [
        //     { name: this.$t(`m.treeinfo["企业微信"]`), type: 'WEIXIN' },
        //     { name: this.$t(`m.treeinfo["邮件"]`), type: 'EMAIL' },
        //     { name: this.$t(`m.treeinfo["SMS短信"]`), type: 'SMS' }
        // ],
        nodeListLoading: false,
        nodeList: [],
        formData: {
          visibleRange: {
            type: 'OPEN',
            value: '',
          },
          revokeWay: 'before_flow',
          revokeState: 0,
          otherSettings: [],
          notify_rule: 'ONCE',
          notify_freq: '',
          notify: ['WEIXIN', 'EMAIL'],
          is_auto_approve: false,
        },
        superviseTypes: ['PERSON', 'GENERAL', 'STARTER'],
        supervisePerson: {
          type: 'STARTER',
          value: '',
        },
        slaValidateMsg: [],
        slaValidateDialogShow: false,
      };
    },
    computed: {
      openFunction() {
        return this.$store.state.openFunction;
      },
      processId() {
        return this.serviceInfo.workflow_id;
      },
      ...mapState({
        noticeType: state => state.common.configurInfo.notify_type,
      }),
    },
    watch: {
      'formData.revokeWay'(val) {
        if (val === 'specify_node' && !this.nodeList.length) {
          this.getNodeList();
        }
      },
    },
    mounted() {
      this.initData();
    },
    methods: {
      initData() {
        const {
          notify,
          display_type,
          display_role,
          supervisor,
          revoke_config: revokeConfig,
          can_ticket_agency: canTicketAgency,
          is_supervise_needed: isSuperviseNeeded,
          notify_rule: notifyRule,
          notify_freq: notifyFreq,
          supervise_type,
        } = this.serviceInfo;
        try {
          const revokeWayItem = this.revokeWayList.find(m => m.key === revokeConfig.type);
          this.formData.revokeWay = revokeWayItem ? revokeWayItem.id : 'not_support';
          this.formData.revokeState = revokeConfig.state;
        } catch (error) {
          console.log(error);
        }
        this.formData.is_auto_approve = this.flowInfo.is_auto_approve;
        this.formData.visibleRange = {
          type: display_type,
          value: display_role,
        };
        this.formData.otherSettings = [];
        if (canTicketAgency) {
          this.formData.otherSettings.push('can_ticket_agency');
        }
        if (isSuperviseNeeded) {
          this.formData.otherSettings.push('is_supervise_needed');
        }
        this.formData.notify = (notify || []).map(m => m.type);
        if (this.formData.notify.length) {
          this.formData.notify_rule = notifyRule;
          this.formData.notify_freq = Number(notifyFreq) / 3600;
        }
        this.supervisePerson = {
          type: supervise_type === 'EMPTY' ? 'STARTER' : supervise_type,
          value: supervisor,
        };
      },
      // 获取流程节点
      getNodeList() {
        this.nodeListLoading = true;
        this.$store.dispatch('deployCommon/getStates', { workflow: this.serviceInfo.workflow_id }).then(res => {
          this.nodeList = res.data.filter(node => !node.is_builtin && node.type !== 'ROUTER-P' && node.type !== 'COVERAGE');
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.nodeListLoading = false;
          });
      },
      saveAndActionService(params) {
        return this.$store.dispatch('service/saveAndActionService', {
          id: this.serviceInfo.id,
          params,
        }).catch(res => {
          errorHandler(res, this);
        })
          .finally(() => {
            this.nodeListLoading = false;
          });
      },
      goToServiceList() {
        this.$router.push({
          name: 'projectServiceList',
          query: {
            project_id: this.$store.state.project.id,
          },
        });
      },
      async validate() {
        const {
          supervisor,
          can_ticket_agency: canTicketAgency,
          is_supervise_needed: isSuperviseNeede,
          supervise_type: superviseType,
        } = this.serviceInfo;
        const params = {
          workflow_config: {
            supervise_type: superviseType || 'EMPTY',
            supervisor: supervisor || '',
            revoke_config: {
              type: 0, // 默认值
              state: 0,
            },
            is_auto_approve: this.formData.is_auto_approve,
          },
        };
        const workflow = params.workflow_config; // 之前存在流程上的参数
        // 可见范围
        if (this.$refs.displayRange && !this.$refs.displayRange.verifyValue()) {
          return false;
        }
        if (this.$refs.taskConfigPanel) {
          await this.$refs.taskConfigPanel.validate();
        }
        if (this.$refs.displayRange) {
          const data = this.$refs.displayRange.getValue();
          params.display_type = data.type;
          params.display_role = data.value || undefined;
        }
        workflow.is_auto_approve = this.formData.is_auto_approve;
        // 撤单方式
        const {
          revokeWay,
          revokeState,
          notify,
        } = this.formData;
        if (revokeWay === 'not_support') {
          workflow.is_revocable = false;
          // 这是字段
        } else {
          workflow.is_revocable = true;
          const type = this.revokeWayList.find(item => item.id === revokeWay).key;
          workflow.revoke_config = {
            type,
            state: revokeWay === 'specify_node' ? revokeState : 0,
          };
        }
        // 其他设置 写死
        params.can_ticket_agency = canTicketAgency || false;
        workflow.is_supervise_needed = isSuperviseNeede || true;
        // 通知方式
        workflow.notify = this.noticeType.filter(notifyItem => notify.some(item => notifyItem.typeName === item));
        workflow.notify.forEach(item => {
          item.type = item.typeName;
        });
        workflow.notify_freq = 0;
        workflow.notify_rule = 'ONCE';

        // const canNotice = !!notify.length
        // if (canNotice) {
        //     workflow.notify_rule = notifyRule
        //     workflow.notify_freq = notifyRule === 'ONCE' ? 0 : notifyFreq * 3600
        // } else {
        //     workflow.notify_rule = 'NONE'
        //     workflow.notify_freq = 0
        // }

        // 任务配置
        if (this.$refs.taskConfigPanel) {
          workflow.extras = {};
          workflow.extras.task_settings = this.$refs.taskConfigPanel.getPostParams();
        }
        const checkResult = await this.saveAndActionService(params);
        await this.$store.dispatch('service/slaValidate', this.serviceInfo.id);
        if (!checkResult.result) {
          this.slaValidateMsg = checkResult.data.messages;
          this.slaValidateDialogShow = true;
          return { data: { result: false } };
        }
        return true;
      },
    },
  };
</script>
<style lang='scss' scoped>
@import '~@/scss/mixins/scroller.scss';
@import '~@/scss/common-section-card.scss';
.bk-float-radio {
    float: left;
    line-height: 30px;
}
.settion-card {
    margin: auto;
    max-width: 1000px;
    .card-title {
        margin: 0;
        font-size: 14px;
        font-weight: 700;
        color: #63656e;
    }
    .card-content {
        padding: 20px;
        margin-top: 16px;
        background: #ffffff;
        border-radius: 2px;
        box-shadow: 0px 2px 6px 0px rgba(6,6,6,0.10);
        overflow: hidden;
    }
}

.auto-with-form-item {
    /deep/ .bk-form-content {
        display: flex;
        .bk-select {
            flex: 1;
            &:first-child {
                margin-right: 8px;
            }
        }
    }
}
.service-setting {
    padding: 20px;
    .service-setting-form {
        margin: 0 auto;
        width: 600px;
    }
}
.notic-card {
    margin-top: 32px;
}
.sla-validate-msg {
    text-align: center;
    .icon-check-circle {
        display: inline-block;
        height: 58px;
        line-height: 58px;
        width: 58px;
        font-size: 30px;
        color: #ffffff;
        background-color: #2dcb56;
        border-radius: 50%;
    }
    h4 {
        margin: 10px 0;
        font-size: 24px;
        color: #313238;
    }
    p {
        margin-bottom: 8px;
        text-align: left;
    }
    .operate-btns {
        margin-top: 20px;
    }
}
/deep/ .common-section-card-desc {
    width: 100%;
}
</style>
