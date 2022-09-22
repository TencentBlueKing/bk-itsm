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
  <div>
    <nav-title :show-icon="true"
      :title-name="serviceInfo.name || $t(`m['新建服务']`)"
      @goBack="onBackIconClick">
      <div slot="step">
        <bk-steps ext-cls="steps-icon"
          data-test-id="service_steps_serviceEditStep"
          :controllable="true"
          line-type="solid"
          :cur-step="currStep"
          :steps="stepList"
          @step-changed="onStepChange">
        </bk-steps>
      </div>
    </nav-title>
    <!-- <div class="steps-container">
            <bk-steps ext-cls="steps-icon"
                data-test-id="service_steps_serviceEditStep"
                :controllable="true"
                line-type="solid"
                :cur-step="currStep"
                :steps="stepList"
                @step-changed="onStepChange">
            </bk-steps>
        </div> -->
    <div :class="['steps-content', { 'steps-content-height': isShowNodeConfig }]" v-bkloading="{ isLoading: serviceLoading || flowInfoLoading }">
      <template v-if="!serviceLoading && !flowInfoLoading">
        <service-form-step v-if="currStep === 1"
          ref="serviceFormStep"
          :type="type"
          :service-id="serviceId"
          :service-info="serviceInfo"
          :create-ticket-node-id="serviceInfo.first_state_id"
          @updateServiceInfo="updateServiceInfo">
        </service-form-step>
        <service-process-step v-else-if="currStep === 2"
          ref="serviceProcessStep"
          :service-info="serviceInfo"
          :flow-info="flowInfo"
          @updateFlowInfo="getFlowDetailInfo"
          @setConfigStatus="setConfigStatus">
        </service-process-step>
        <service-setting-step v-else-if="currStep === 3"
          ref="serviceSettingStep"
          :service-info="serviceInfo"
          @updateFlowInfo="getFlowDetailInfo"
          :flow-info="flowInfo">
        </service-setting-step>
      </template>
    </div>
    <div v-show="!isShowNodeConfig || currStep !== 2" class="submit-footer-bar">
      <bk-button
        data-test-id="service_button_prevStep"
        ext-cls="button-item"
        theme="default"
        :disabled="isSubmitting"
        @click="onPrevStepClick">
        {{ prevStepBtnName }}
      </bk-button>
      <bk-button
        data-test-id="service_button_nextStepAndSave"
        ext-cls="button-item"
        theme="primary"
        :disabled="!serviceId && serviceId !== 0"
        :loading="isSubmitting"
        @click="onNextStepClick">
        {{ nextStepBtnName }}
      </bk-button>
    </div>
  </div>
</template>
<script>
  import NavTitle from '@/components/common/layout/NavTitle';
  import ServiceFormStep from './ServiceFormStep.vue';
  import ServiceProcessStep from './ServiceProcessStep.vue';
  import ServiceSettingStep from './ServiceSettingStep.vue';
  import { errorHandler } from '@/utils/errorHandler';

  export default {
    name: 'ServiceEdit',
    components: {
      NavTitle,
      ServiceFormStep,
      ServiceProcessStep,
      ServiceSettingStep,
    },
    props: {
      type: {
        type: String,
        default: 'new',
      },
      step: {
        type: String,
        default: 'basic',
      },
      serviceId: {
        type: [String, Number],
        default: '',
      },
    },
    data() {
      return {
        serviceLoading: this.type === 'edit',
        flowInfoLoading: false,
        isSubmitting: false,
        serviceInfo: {},
        flowInfo: {},
        isShowNodeConfig: false, // 编辑节点配置
      };
    },
    computed: {
      currStep() {
        const routeMap = ['basic', 'process', 'setting'];
        const index = routeMap.indexOf(this.step);
        return index + 1;
      },
      prevStepBtnName() {
        return this.currStep === 1 ? this.$t('m[\'返回\']') : this.$t('m.treeinfo["上一步"]');
      },
      nextStepBtnName() {
        return this.currStep < 3 ? this.$t('m.common[\'下一步\']') : this.$t('m.newCommon["提交"]');
      },
      stepList() {
        let status1; let status2; let status3;
        if (this.type !== 'new') { // 创建成功
          status1 = 'done';
          status2 = 'done';
        }
        if (this.type !== 'new' && this.serviceInfo.is_valid) { // 已启用
          status3 = 'done';
        }
        const list = [
          { title: this.$t('m.tickets[\'服务表单\']'), icon: 1, status: status1 },
          { title: this.$t('m.tickets[\'服务流程\']'), icon: 2, status: status2 },
          { title: this.$t('m.taskTemplate[\'高级配置\']'), icon: 3, status: status3 },
        ];
        list[this.currStep - 1].status = undefined;
        return list;
      },
    },
    watch: {
      '$route'(to, from) {
        if (to.params.type !== from.params.type) {
          this.initData();
        }
      },
    },
    mounted() {
      this.initData();
    },
    methods: {
      async initData() {
        if (this.type === 'edit') {
          await this.getServiceDetail();
          this.getFlowDetailInfo();
        }
      },
      // 获取服务详情
      getServiceDetail() {
        this.serviceLoading = true;
        return this.$store.dispatch('service/getServiceDetail', this.serviceId).then((res) => {
          this.serviceInfo = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.serviceLoading = false;
          });
      },
      // 获取流程详情
      getFlowDetailInfo() {
        this.flowInfoLoading = true;
        this.$store.dispatch('design/getFlowDetail', { params: this.serviceInfo.workflow_id }).then((res) => {
          this.flowInfo = res.data;
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.flowInfoLoading = false;
          });
      },
      // 更新服务信息
      updateServiceInfo(data) {
        this.serviceInfo = data;
      },
      setConfigStatus(val) {
        this.isShowNodeConfig = val;
      },
      onBackIconClick() {
        // 进入节点配置 返回画布
        if (this.$refs.serviceProcessStep && this.$refs.serviceProcessStep.isShowNodeConfig) {
          this.$refs.serviceProcessStep.isShowNodeConfig = false;
          return;
        }
        this.$router.push({
          name: 'projectServiceList',
          query: {
            project_id: this.$store.state.project.id,
            catalog_id: this.$route.query.catalog_id,
          },
        });
      },
      onStepChange(index) {
        const step = ['basic', 'process', 'setting'];
        if (this.type === 'new') {
          return;
        }
        this.$router.push({
          name: 'projectServiceEdit',
          params: {
            type: 'edit',
            step: step[index - 1],
          },
          query: {
            serviceId: this.serviceId,
            project_id: this.$store.state.project.id,
          },
        });
      },
      // 上一步
      onPrevStepClick() {
        if (this.currStep === 1) {
          this.$router.push({
            name: 'projectServiceList',
            query: {
              project_id: this.$store.state.project.id,
              ...this.$route.query,
            },
          });
        } else {
          this.$router.push({
            name: 'projectServiceEdit',
            params: {
              type: 'edit',
              step: this.currStep === 2 ? 'basic' : 'process',
            },
            query: {
              ...this.$route.query,
            },
          });
        }
      },
      // 下一步
      onNextStepClick() {
        this.isSubmitting = true;
        const stepRefMap = {
          basic: 'serviceFormStep',
          process: 'serviceProcessStep',
          setting: 'serviceSettingStep',
        };
        const refName = stepRefMap[this.step];
        this.$refs[refName].validate().then((res = {}) => {
          if (res.data && res.data.result === false) {
            return;
          }
          // next
          if (this.step !== 'setting') {
            const nextStep = this.step === 'basic' ? 'process' : 'setting';
            if (this.step === 'basic' && !this.serviceInfo.source) {
              this.$refs[refName].updateServiceSource('custom');
            }
            this.$router.push({
              name: 'projectServiceEdit',
              params: {
                type: 'edit',
                step: nextStep,
              },
              query: {
                ...this.$route.query,
              },
            });
          } else {
            this.$bkMessage({
              message: this.$t('m.treeinfo["保存成功"]'),
              theme: 'success',
            });
            this.$router.push({
              name: 'projectServiceList',
              query: {
                project_id: this.$store.state.project.id,
                catalog_id: this.$route.query.catalog_id,
              },
            });
          }
        })
          .finally(() => {
            this.isSubmitting = false;
          });
      },
    },
  };
</script>
<style lang="scss" scoped>
@import '~@/scss/mixins/scroller.scss';
.steps-container {
    position: relative;
    width: 100%;
    background: #ffffff;
    border-top: 1px solid #dde4eb;
    box-shadow: 0px 1px 0px 0px #dde4eb;
    z-index: 1;
    .steps-icon {
        margin: 0 auto;
        width: 60%;
        align-items: center;
        height: 60px;
        .icon-image, .icon-order, .icon-user, .icon-id {
            font-size: 14px;
        }
    }
}
.steps-content {
    height: calc(100vh - 164px);
    overflow: auto;
    @include scroller;
}
.steps-content-height {
    height: calc(100vh - 165px);
}
.submit-footer-bar {
    position: relative;
    padding-right: 24px;
    height: 60px;
    line-height: 60px;
    background: #fafbfd;
    box-shadow: 0px -1px 0px 0px #dcdee5;
    text-align: right;
    .button-item {
        width: 104px;
        margin-left: 16px;
    }
}
</style>
