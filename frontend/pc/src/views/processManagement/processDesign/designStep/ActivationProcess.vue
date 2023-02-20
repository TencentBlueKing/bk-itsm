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
  <div class="bk-design-third" v-bkloading="{ isLoading: isDataLoading }">
    <basic-card :card-label="$t(`m.tickets['启用设置']`)">
      <bk-form :label-width="170" :model="formData" :rules="rules" ref="withdrawForm">
        <bk-form-item :label="$t(`m.treeinfo['是否支持撤回']`)">
          <bk-radio-group v-model="formData.can_withdraw">
            <bk-radio :value="trueStatus" class="mr20">{{ $t('m.treeinfo["是"]') }}</bk-radio>
            <bk-radio :value="falseStatus">{{ $t('m.treeinfo["否"]') }}</bk-radio>
          </bk-radio-group>
          <p class="card-inner-body" v-if="formData.can_withdraw">
            <bk-radio-group v-model="formData.revoke_config.type">
              <bk-radio :value="2" ext-cls="withdraw-type-radio">{{$t(`m.treeinfo['提单后，单据未被处理流转前，提单人可以撤回']`)}}</bk-radio>
              <bk-radio :value="1" ext-cls="withdraw-type-radio">{{$t(`m.treeinfo['任何节点，提单人都可撤回单据']`)}}</bk-radio>
              <bk-radio :value="3" ext-cls="withdraw-type-radio">{{$t(`m.treeinfo['指定节点前可以撤回']`)}}</bk-radio>
            </bk-radio-group>
            <bk-select
              v-if="formData.revoke_config.type === 3"
              v-model="formData.revoke_config.state"
              style="width: 330px;" class="mt10"
              :placeholder="$t(`m.treeinfo['请选择撤单节点']`)"
              :loading="nodeListLoading"
              searchable>
              <bk-option v-for="option in nodeList"
                :key="option.id"
                :id="option.id"
                :name="option.name">
              </bk-option>
            </bk-select>
            <span v-if="revokeStateError" class="bk-task-error">{{$t(`m.treeinfo['请选择撤单节点']`)}}</span>
          </p>
        </bk-form-item>
        <bk-form-item :label="$t(`m.treeinfo['是否立即部署流程']`)">
          <bk-radio-group v-model="formData.can_deploy">
            <!-- 没有部署权限禁用 -->
            <span
              v-if="!hasPermission(['workflow_deploy'], flowInfo.auth_actions)"
              v-cursor
              class="radio-permission-disable"
              @click="checkFlowDeployPerm()">
              {{ $t('m.treeinfo["是"]') }}
            </span>
            <bk-radio
              v-else
              :value="trueStatus"
              class="mr20">
              {{ $t('m.treeinfo["是"]') }}
            </bk-radio>
            <bk-radio :value="falseStatus">{{ $t('m.treeinfo["否"]') }}</bk-radio>
          </bk-radio-group>
          <p class="card-inner-body" v-if="formData.can_deploy">
            <bk-form-item :label-width="100" :label="$t(`m.treeinfo['部署流程名']`)"
              :required="true"
              :property="'deploy_name'"
              style="width: 500px;">
              <bk-input v-model="formData.deploy_name" :placeholder="$t(`m.treeinfo['请输入部署流程名']`)"></bk-input>
            </bk-form-item>
          </p>
        </bk-form-item>
        <bk-form-item :label="$t(`m.treeinfo['自动处理']`)">
          <bk-checkbox
            :true-value="true"
            :false-value="false"
            v-model="formData.is_auto_approve">
            当审批节点的审批人为申请人时，自动通过
          </bk-checkbox>
        </bk-form-item>
      </bk-form>
    </basic-card>

    <basic-card class="mt20" :card-label="'通知策略'">
      <bk-form :label-width="170" :model="noticeData">
        <bk-form-item :label="$t(`m.treeinfo['通知方式']`)">
          <bk-checkbox-group v-model="noticeData.notify">
            <bk-checkbox :value="'WEIXIN'" :ext-cls="'mr30'">
              <img class="notice-option-icon" :src="qwIcon" style="width: 20px" /> {{ $t(`m.treeinfo["企业微信"]`) }}
            </bk-checkbox>
            <bk-checkbox :value="'EMAIL'" :ext-cls="'mr30'">
              <img class="notice-option-icon" :src="emailIcon" style="width: 20px" /> {{ $t(`m.treeinfo["邮件"]`) }}
            </bk-checkbox>
            <bk-checkbox :value="'SMS'" :ext-cls="'mr30'">{{ $t(`m.treeinfo["SMS短信"]`) }}</bk-checkbox>
          </bk-checkbox-group>
        </bk-form-item>
        <bk-form-item :label="$t(`m.treeinfo['是否通知']`)">
          <bk-radio-group v-model="noticeData.can_notice" @change="handleNotice">
            <bk-radio :value="trueStatus" class="mr20">{{ $t('m.treeinfo["是"]') }}</bk-radio>
            <bk-radio :value="falseStatus">{{ $t('m.treeinfo["否"]') }}</bk-radio>
          </bk-radio-group>
          <p class="card-inner-body" v-if="noticeData.can_notice">
            <bk-form-item :label-width="80" :label="$t(`m.treeinfo['通知频率']`)">
              <bk-radio-group v-model="noticeData.notify_rule">
                <bk-radio :value="'ONCE'"
                  :ext-cls="'mr20 bk-line-radio'">
                  {{ $t('m.treeinfo["首次通知，以后不再通知"]') }}
                </bk-radio>
                <div class="bk-line-radio">
                  <bk-radio :value="'RETRY'" :ext-cls="'mr20 bk-float-radio'">
                    {{ $t('m.treeinfo["首次通知后，次日起每天定时通知"]') }}
                  </bk-radio>
                  <bk-select v-if="noticeData.notify_rule === 'RETRY'"
                    style="float: left; width: 200px;"
                    v-model="noticeData.notify_freq"
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
            </bk-form-item>
          </p>
        </bk-form-item>
        <bk-form-item :label="$t(`m.treeinfo['是否催办']`)">
          <bk-radio-group v-model="noticeData.is_supervise_needed">
            <bk-radio :value="trueStatus" class="mr20">{{ $t('m.treeinfo["是"]') }}</bk-radio>
            <bk-radio :value="falseStatus">{{ $t('m.treeinfo["否"]') }}</bk-radio>
          </bk-radio-group>
          <p class="card-inner-body" v-if="noticeData.is_supervise_needed">
            <bk-form-item :label-width="100" :label="$t(`m.treeinfo['其他催办人']`)">
              <bk-select style="float: left; width: 330px; margin-right: 10px;"
                v-model="noticeData.supervise_type"
                :clearable="false"
                searchable
                :font-size="'medium'"
                @selected="changeSupChildList">
                <bk-option v-for="option in roles.grouplist"
                  :key="option.type"
                  :id="option.type"
                  :name="option.name">
                </bk-option>
              </bk-select>
              <div style="float: left; width: 330px;"
                v-if="noticeData.supervise_type !== 'EMPTY'">
                <template v-if="noticeData.supervise_type === 'PERSON'">
                  <member-select
                    v-model="noticeData.personList">
                  </member-select>
                </template>
                <template v-else>
                  <bk-select
                    v-model="noticeData.supervisor"
                    searchable
                    :font-size="'medium'">
                    <bk-option v-for="option in roles.supChildList"
                      :key="option.id"
                      :id="option.id"
                      :name="option.name">
                    </bk-option>
                  </bk-select>
                </template>
              </div>
              <p class="mt5 mb0 bk-revoke-span" v-if="noticeData.supervise_type === 'EMPTY'">
                <i class="bk-icon icon-exclamation-circle" style="padding-right: 5px"></i>
                <span>{{ $t('m.treeinfo["默认催办人：提单人"]') }}</span>
              </p>
            </bk-form-item>
          </p>
        </bk-form-item>
      </bk-form>
    </basic-card>
    <!-- 展开高级配置 -->
    <div
      v-if="openFunction.TRIGGER_SWITCH || openFunction.TASK_SWITCH"
      class="more-configuration mt20" data-test-id="activationProcess-div-showMoreConfig" @click="showMoreConfig = !showMoreConfig">
      <i v-if="!showMoreConfig" class="bk-icon icon-down-shape"></i>
      <i v-else class="bk-icon icon-up-shape"></i>
      <span>{{$t(`m.taskTemplate['高级配置']`)}}</span>
    </div>
    <template v-if="showMoreConfig">
      <collapse-transition>
        <div>
          <basic-card class="mt20"
            :card-label="$t(`m.newCommon['触发器']`)"
            :card-desc="$t(`m.taskTemplate['满足触发条件后要完成的特定动作']`)">
            <common-trigger-list
              v-if="openFunction.TRIGGER_SWITCH"
              :origin="'workflow'"
              :source-id="processId"
              :table="flowInfo.table">
            </common-trigger-list>
          </basic-card>
          <basic-card class="mt20"
            :card-label="$t(`m.taskTemplate['任务配置']`)"
            :card-desc="$t(`m.taskTemplate['如果需要在流程中调用标准运维的业务流程进而创建任务，请在第一步的“填写流程信息”中，打开“是否关联业务”的开关。']`)">
            <TaskConfigPanel ref="taskConfigPanel" :workflow-info="flowInfo"></TaskConfigPanel>
          </basic-card>
        </div>
      </collapse-transition>
    </template>
    <div class="bk-four-btn">
      <bk-button :theme="'default'"
        :title="$t(`m.treeinfo['上一步']`)"
        :disabled="secondClick"
        class="mr10"
        @click="previousStep">
        {{ $t('m.treeinfo["上一步"]') }}
      </bk-button>
      <bk-button :theme="'primary'"
        :title="$t(`m.treeinfo['提交']`)"
        :loading="secondClick"
        class="mr10"
        @click="backTab">
        {{ $t('m.treeinfo["提交"]') }}
      </bk-button>
    </div>
  </div>
</template>
<script>
  import commonMix from '../../../commonMix/common.js';
  import memberSelect from '../../../commonComponent/memberSelect';
  import collapseTransition from '@/utils/collapse-transition.js';
  import commonTriggerList from '../../taskTemplate/components/commonTriggerList';
  import TaskConfigPanel from './components/TaskConfigPanel.vue';
  import BasicCard from '@/components/common/layout/BasicCard.vue';
  import permission from '@/mixins/permission.js';
  import { errorHandler } from '../../../../utils/errorHandler.js';

  export default {
    name: 'ActivationProcess',
    components: {
      BasicCard,
      memberSelect,
      collapseTransition,
      commonTriggerList,
      TaskConfigPanel,
    },
    mixins: [commonMix, permission],
    props: {
      flowInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      processId: {
        type: [String, Number],
        required: true,
      },
      business: {
        type: Boolean,
        default() {
          return false;
        },
      },
    },
    data() {
      return {
        isDataLoading: false,
        secondClick: false,
        // 启用设置
        formData: {
          can_withdraw: true,
          can_deploy: true,
          deploy_name: '',
          revoke_config: {
            type: 2,
            state: '',
          },
          is_auto_approve: false,
        },
        revokeStateError: false,
        nodeListLoading: false,
        nodeList: [],
        trueStatus: true,
        falseStatus: false,
        // 通知设置
        noticeData: {
          can_notice: false,
          is_supervise_needed: false,
          supervise_type: 'EMPTY',
          supervisor: '',
          personList: [],
          notify_rule: '',
          notify_freq: '',
          notify: ['WEIXIN', 'EMAIL'],
        },
        // 催办角色
        roles: {
          grouplist: [],
          supChildList: [],
        },
        notifyList: [
          { name: this.$t('m.treeinfo["企业微信"]'), type: 'WEIXIN' },
          { name: this.$t('m.treeinfo["邮件"]'), type: 'EMAIL' },
          { name: this.$t('m.treeinfo["SMS短信"]'), type: 'SMS' },
        ],
        frequencyList: [
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
        ],
        // 父组件传值
        parentInfo: {
          status: 'success',
          index: 2,
        },
        // 校验
        rules: {},
        showMoreConfig: false,
        qwIcon: require('../../../../images/qw.svg'),
        emailIcon: require('../../../../images/email.svg'),
      };
    },
    computed: {
      openFunction() {
        return this.$store.state.openFunction;
      },
    },
    watch: {
      'flowInfo.auth_actions': {
        handler() {
          if (!this.hasPermission(['workflow_deploy'], this.flowInfo.auth_actions)) {
            this.formData.can_deploy = false;
          }
        },
        deep: true,
        immediate: true,
      },
      'formData.revoke_config.type': {
        handler(val) {
          if (val === 3 && !this.nodeList.length) {
            this.getNodeList();
          }
        },
      },
      'flowInfo.id'() {
        this.initData();
      },
    },
    mounted() {
      this.initData();
    },
    methods: {
      initData() {
        this.getThirdInfo();
        // 部署流程
        this.formData.deploy_name = this.flowInfo.name;
        // 审批节点：审批人为申请人
        this.formData.is_auto_approve = this.flowInfo.is_auto_approve || false;
        // 校验
        this.rules.deploy_name = this.checkCommonRules('name').name;
      },
      // 通过ID获取数据
      getThirdInfo() {
        const params = this.flowInfo.id;
        if (!params) {
          return;
        }
        this.isDataLoading = true;
        this.$store.dispatch('design/getFlowDetail', { params }).then((res) => {
          const value = res.data;
          // 支持撤回
          this.formData.can_withdraw = !!value.is_revocable;
          const { state, type } = value.revoke_config;
          this.formData.revoke_config = {
            state: state === 0 ? '' : state,
            type,
          };
          // 通知
          this.noticeData.can_notice = (value.notify_rule !== 'NONE');
          if (this.noticeData.can_notice) {
            // 通知频率
            this.noticeData.notify_rule = value.notify_rule;
            this.noticeData.notify_freq = Number(value.notify_freq / 3600);
          }
          this.noticeData.notify = value.notify.map(notify => notify.type);
          // 催办
          this.noticeData.is_supervise_needed = value.is_supervise_needed;
          if (this.noticeData.is_supervise_needed) {
            this.noticeData.supervise_type = value.supervise_type;
            this.noticeData.supervisor = value.supervisor || '';
            this.noticeData.personList = this.noticeData.supervise_type === 'PERSON' ? value.supervisor.split(',') : '';
          }
          this.roleGroup();
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.showMoreConfig = (this.flowInfo.extras
              && this.flowInfo.extras.task_settings
              && this.flowInfo.extras.task_settings.length)
              || this.noticeData.can_notice;
            this.isDataLoading = false;
          });
      },
      // 获取流程节点
      getNodeList() {
        this.nodeListLoading = true;
        this.$store.dispatch('deployCommon/getStates', { workflow: this.flowInfo.id }).then((res) => {
          this.nodeList = res.data.filter(node => !node.is_builtin && node.type !== 'ROUTER-P' && node.type !== 'COVERAGE');
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.nodeListLoading = false;
          });
      },
      // 角色分组
      roleGroup() {
        const params = 'is_processor=true';
        this.$store.dispatch('cdeploy/getUser', { params }).then((res) => {
          const selectgroup = ['CMDB', 'PERSON', 'GENERAL', 'EMPTY'];
          const grouplistorigin = res.data.filter(item => selectgroup.indexOf(item.type) !== -1);
          this.roles.grouplist = this.business ? grouplistorigin : grouplistorigin.filter(item => item.type !== 'CMDB');
          this.roles.grouplist.forEach((item) => {
            if (item.type === 'EMPTY') {
              item.name = '提单人';
            }
          });
          // 次级数据
          if (
            this.noticeData.is_supervise_needed
            && !['EMPTY', 'PERSON'].includes(this.noticeData.supervise_type)
          ) {
            this.roleUserList(this.noticeData.supervise_type);
          }
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 获取次级角色列表
      roleUserList(type) {
        this.$store.dispatch('cdeploy/getSecondUser', { role_type: type }).then((res) => {
          this.roles.supChildList = [];
          res.data.forEach((item) => {
            this.roles.supChildList.push({
              id: String(item.id),
              name: item.name,
            });
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 催办选择
      changeSupChildList(value) {
        if (value !== 'EMPTY') {
          this.noticeData.supervisor = '';
          this.noticeData.personList = [];
          this.roleUserList(value);
        } else {
          this.noticeData.supervisor = '';
        }
      },
      // 通知
      handleNotice(val) {
        if (val) {
          this.noticeData.is_supervise_needed = false;
          this.noticeData.supervise_type = 'EMPTY';
          this.noticeData.notify_rule = 'ONCE';
          this.noticeData.notify_freq = 0;
        }
      },
      async backTab() {
        if (this.$refs.taskConfigPanel) {
          await this.$refs.taskConfigPanel.validate();
        }
        this.revokeStateError = false;
        if (this.formData.revoke_config.type === 3 && !this.formData.revoke_config.state) {
          this.revokeStateError = true;
          return false;
        }
        let withdrawFormValid = false;
        await this.$refs.withdrawForm.validate().then(() => {
          withdrawFormValid = true;
        }, () => {});
        if (withdrawFormValid) {
          this.submitFn();
        }
      },
      // 返回列表数据
      submitFn() {
        const id = this.processId;
        const params = {
          partial: true,
          is_revocable: this.formData.can_withdraw,
          is_enabled: true,
          is_draft: false,
          deploy: this.formData.can_deploy,
          deploy_name: this.formData.can_deploy ? this.formData.deploy_name : '',
          is_auto_approve: this.formData.is_auto_approve,
        };
        if (this.formData.can_withdraw) {
          const revokeType = this.formData.revoke_config.type;
          params.revoke_config = {
            type: revokeType,
            state: revokeType === 3 ? this.formData.revoke_config.state : 0,
          };
        }
        // 任务配置
        if (this.$refs.taskConfigPanel) {
          params.extras = {};
          params.extras.task_settings = this.$refs.taskConfigPanel.getPostParams();
        }
        // 通知
        if (this.noticeData.can_notice) {
          params.notify_rule = this.noticeData.notify_rule;
          params.notify_freq = this.noticeData.notify_rule === 'ONCE' ? 0 : this.noticeData.notify_freq * 3600;
        } else {
          params.notify_rule = 'NONE';
          params.notify_freq = 0;
        }
        // 通知方式
        params.notify = this.notifyList.filter(notify => this.noticeData.notify.some(item => notify.type === item));
        // 催办
        params.is_supervise_needed = this.noticeData.is_supervise_needed;
        params.supervise_type = this.noticeData.is_supervise_needed ? this.noticeData.supervise_type : 'EMPTY';
        params.supervisor = this.noticeData.is_supervise_needed ? (this.noticeData.supervise_type === 'PERSON' ? this.noticeData.personList.join(',') : this.noticeData.supervisor) : '';
        // 催办人的校验
        if (params.is_supervise_needed && params.supervise_type !== 'EMPTY' && !params.supervisor) {
          this.$bkMessage({
            message: this.$t('m.treeinfo["催办人为必填"]'),
            theme: 'warning',
          });
          return;
        }

        if (this.secondClick) {
          return;
        }
        this.secondClick = true;
        this.$store.dispatch('cdeploy/changePartInfo', { params, id }).then(() => {
          this.$bkMessage({
            message: this.$t('m.treeinfo["保存成功"]'),
            theme: 'success',
          });
          // 快捷部署成功弹窗提示是否去服务页面
          if (this.formData.can_deploy) {
            this.openService();
          } else {
            this.$router.push({
              name: 'ProcessHome',
            });
          }
        }, (res) => {
          errorHandler(res, this);
        })
          .finally(() => {
            this.secondClick = false;
          });
      },
      openService() {
        this.$bkInfo({
          type: 'success',
          closeIcon: false,
          title: this.$t('m.treeinfo["保存成功"]'),
          subTitle: this.$t('m.treeinfo["流程部署成功，是否去服务页面关联此流程"]'),
          confirmFn: () => {
            this.$router.push({
              name: 'projectServiceList',
              query: {
                project_id: this.$store.state.project.id,
              },
            });
          },
          cancelFn: () => {
            this.$router.push({
              name: 'ProcessHome',
            });
          },
        });
      },
      previousStep() {
        this.$router.push({
          name: 'ProcessEdit',
          params: {
            type: 'edit',
            step: 'pipelineDesign',
          },
          query: {
            processId: this.processId,
          },
        });
      },
      // 验证流程部署权限
      checkFlowDeployPerm() {
        if (!this.hasPermission(['workflow_deploy'], this.flowInfo.auth_actions)) {
          const { projectInfo } = this.$store.state.project;
          const resourceData = {
            project: [{
              id: projectInfo.key,
              name: projectInfo.name,
            }],
            workflow: [{
              id: this.flowInfo.id,
              name: this.flowInfo.name,
            }],
          };
          this.applyForPermission(['workflow_deploy'], this.flowInfo.auth_actions, resourceData);
        }
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../../scss/mixins/clearfix.scss';
    .more-configuration {
        display: flex;
        align-items: center;
        font-size: 14px;
        color: #3a84ff;
        cursor: pointer;
        .bk-icon {
            padding: 0 5px;
            margin-right: 6px;
        }
    }
    .bk-design-third {
        padding: 20px;
        // min-height: calc(100vh - 164px);
    }
    .bk-four-btn {
        margin-top: 20px;
    }
    .bk-line-radio {
        display: block;
        line-height: 30px;
    }
    .bk-float-radio {
        float: left;
        line-height: 30px;
    }
    .card-inner-body {
        margin-top: 12px;
        padding: 18px 30px;
        font-size: 12px;
        color: #A0ADB9;
        background: #fafbfd;
        border-radius: 2px;
    }
    .withdraw-type-radio {
      &:not(:first-child) {
        margin-top: 20px;
      }
      display: block;
    }
    .notice-option-icon {
      margin-left: 10px;
      display: inline-block;
      vertical-align: middle;
    }
</style>
