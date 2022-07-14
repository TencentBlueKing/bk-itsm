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
  <div class="bk-add-agreement">
    <!-- title -->
    <div class="is-title" :class="{ 'bk-title-left': !sliderStatus }">
      <p class="bk-come-back" @click="closeAgreement(false)">
        <i class="bk-icon icon-arrows-left"></i>
        {{ changeInfo.info.id ? changeInfo.info.name : $t('m.slaContent["新建服务协议"]') }}
      </p>
    </div>
    <!-- content -->
    <div class="bk-add-content">
      <div class="bk-content-group" style="width: 400px;">
        <p class="bk-group-title">{{ $t('m.slaContent["基本信息"]') }}</p>
        <bk-form
          :label-width="250"
          form-type="vertical"
          :model="formInfo"
          :rules="nameRules"
          ref="dynamicForm">
          <bk-form-item
            :label="$t(`m.slaContent['服务协议名称']`)"
            :required="true"
            error-display-type="normal"
            style="width: 540px;"
            :property="'name'">
            <bk-input v-model.trim="formInfo.name"
              :maxlength="120"
              :show-word-limit="true"
              :placeholder="$t(`m.slaContent['请输入服务协议名称']`)"
              :disabled="changeInfo.info.is_builtin">
            </bk-input>
          </bk-form-item>
        </bk-form>
      </div>
      <div class="bk-content-group">
        <p class="bk-group-title">{{ $t('m["服务承诺设定"]') }}</p>
        <priority-configur
          ref="priorityConfigur"
          :model-list="modelList"
          :model-priority="modelPriority"
          :change-info="changeInfo">
        </priority-configur>
      </div>
      <div class="bk-content-group">
        <p class="bk-group-title">{{ $t('m["预警提醒"]') }}</p>
        <event-remind
          ref="eventRemind1"
          :model-list="modelList"
          :model-priority="testPriority1"
          :has-check-box="changeInfo.is_reply_need"
          :notify-event-list="notifyEventList"
          :change-info="changeInfo">
        </event-remind>
      </div>
      <div class="bk-content-group">
        <p class="bk-group-title">{{ $t('m["超时提醒"]') }}</p>
        <event-remind
          ref="eventRemind3"
          :model-list="modelList"
          :has-check-box="changeInfo.is_reply_need"
          :notify-event-list="notifyEventList"
          :model-priority="testPriority3"
          :change-info="changeInfo">
        </event-remind>
      </div>
      <div>
        <p class="bk-group-title">
          <span data-test-id="sla_span_isUseAgreement" style="margin-right: 15px;">{{ $t('m.slaContent["是否启用该协议"]') }}</span>
          <bk-switcher v-model="formInfo.agreementStatus" size="small" theme="primary"></bk-switcher>
        </p>
      </div>
    </div>
    <div class="bk-priority-btn">
      <bk-button
        data-test-id="sla_button_submitAgreement"
        theme="primary"
        :title="$t(`m.slaContent['提交']`)"
        class="mr10"
        :loading="secondClick"
        @click="submitInfo">{{ $t(`m.slaContent['提交']`) }}
      </bk-button>
      <bk-button
        data-test-id="sla_button_closeAgreement"
        theme="default"
        :title="$t(`m.eventdeploy['取消']`)"
        class="mr10"
        :loading="secondClick"
        @click="closeAgreement(false)">{{ $t('m.eventdeploy["取消"]') }}
      </bk-button>
    </div>
  </div>
</template>

<script>
  import commonMix from '../../commonMix/common.js';
  import priorityConfigur from './priorityConfigur.vue';
  import eventRemind from './eventRemind.vue';
  export default {
    name: 'addAgreement',
    components: {
      priorityConfigur,
      eventRemind,
    },
    mixins: [commonMix],
    props: {
      modelList: {
        type: Array,
        default() {
          return [];
        },
      },
      notifyEventList: {
        type: Object,
        default() {
          return {};
        },
      },
      modelPriority: {
        type: Array,
        default() {
          return [];
        },
      },
      changeInfo: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        testPriority1: [
          {
            type: 1,
            eventName: this.$t('m[\'响应提醒\']'),
            hasCheckBox: true,
            isCheck: false,
            remindRuleText: this.$t('m[\'响应时长达到协议标准的\']'),
            remindRuleValue: 20,
            remindRuleUnit: '%',
            receivers: '',
            notify_type_list: ['email', 'weixin'],
            email_notify: '',
            weixin_notify: '',
            notify_rule: 'once',
            notify_freq: 10,
            freq_unit: '%',
          },
          {
            type: 3,
            eventName: this.$t('m[\'处理提醒\']'),
            hasCheckBox: false,
            isCheck: false,
            remindRuleText: this.$t('m[\'处理时长达到协议标准的\']'),
            remindRuleValue: 20,
            remindRuleUnit: '%',
            receivers: '',
            notify_type_list: ['email', 'weixin'],
            email_notify: '',
            weixin_notify: '',
            notify_rule: 'once',
            notify_freq: 10,
            freq_unit: '%',
          },
        ],
        testPriority3: [
          {
            type: 2,
            eventName: this.$t('m[\'超时响应提醒\']'),
            hasCheckBox: true,
            isCheck: false,
            remindRuleText: this.$t('m[\'响应时长超出协议标准还未响应时\']'),
            receivers: '',
            notify_type_list: ['email', 'weixin'],
            email_notify: '',
            weixin_notify: '',
            notify_rule: 'once',
            notify_freq: 10,
            freq_unit: '%',
          },
          {
            type: 4,
            eventName: this.$t('m[\'超时处理提醒\']'),
            hasCheckBox: false,
            isCheck: false,
            remindRuleText: this.$t('m[\'处理时长超出协议标准还未解决时\']'),
            receivers: '',
            notify_type_list: ['email', 'weixin'],
            email_notify: '',
            weixin_notify: '',
            notify_rule: 'once',
            notify_freq: 10,
            freq_unit: '%',
          },
        ],
        secondClick: false,
        formInfo: {
          name: '',
          agreementStatus: true,
          id: '',
        },
        // 校验规则
        nameRules: {},
      };
    },
    computed: {
      sliderStatus() {
        return this.$store.state.common.slideStatus;
      },
    },
    watch: {
      // emailNotifyEventList: {
      //     handler: function (list) {
      //         this.wacthEventList('testPriority1', 'email', list)
      //         this.wacthEventList('testPriority3', 'email', list)
      //     },
      //     immediate: true
      // },
      // weixinNotifyEventList: {
      //     handler: function (list) {
      //         this.wacthEventList('testPriority1', 'weixin', list)
      //         this.wacthEventList('testPriority3', 'weixin', list)
      //     },
      //     immediate: true
      // }
      'changeInfo.is_reply_need'(val) {
        if (!val) {
          this.$refs.priorityConfigur.clearFromError();
        }
      },
    },
    mounted() {
      this.initData();
      this.nameRules = this.checkCommonRules('name');
    },
    methods: {
      // 初始化数据
      initData() {
        const parentInfo = this.changeInfo.info;
        this.formInfo = {
          name: parentInfo.name || '',
          agreementStatus: parentInfo.is_enabled || true,
          id: parentInfo.id,
        };
      },
      wacthEventList(listKey, watchType, eventList) {
        this[listKey] = this[listKey].map(item => {
          if (!this.changeInfo.info.id || !item[`${watchType}_notify`]) {
            item[`${watchType}_notify`] = eventList[0].id;
          }
          return item;
        });
      },
            
      getReminderInfo(id) {
        const priorList = [];
        let priorObj = {};
        this.$refs[`eventRemind${id}`].priorityList.map((prior) => {
          priorObj = {
            type: prior.type,
            condition: {
              type: 'all',
              expressions: [
                {
                  name: 'handle_time_percent',
                  value: prior.remindRuleValue || 100,
                  type: 'INT',
                  operator: 'greater_than',
                },
              ],
            },
            actions: [
              {
                action_type: 'alert',
                config: {
                  receivers: prior.receivers || '',
                  notify_rule: prior.notify_rule || '',
                  notify_freq: prior.notify_freq || 0,
                  freq_unit: prior.freq_unit || '',
                  notify: prior.notify_type_list.map(notifyType => ({
                    notify_type: notifyType,
                    notify_template: prior[`${notifyType}_notify`],
                  })),
                },
              },
            ],
          };
          if (!prior.hasCheckBox || (this.changeInfo.is_reply_need && prior.isCheck)) {
            priorList.push(priorObj);
          }
        });
        return priorList;
      },
      // 提交 取消
      submitFn() {
        const policies = this.$refs.priorityConfigur.priorityList;
        const params = {
          name: this.formInfo.name,
          is_enabled: this.formInfo.agreementStatus,
          is_reply_need: this.changeInfo.is_reply_need || false,
          action_policies: [...this.getReminderInfo(1), ...this.getReminderInfo(3)],
          project_key: this.$store.state.project.id,
          policies,
        };
        // 修改和新建
        const urlValue = this.changeInfo.info.id ? 'putProtocol' : 'addProtocol';
        const paramsValue = {
          params,
        };
        if (this.changeInfo.info.id) {
          paramsValue.id = this.changeInfo.info.id;
        }
        // 请求方法
        if (this.secondClick) {
          return;
        }
        this.secondClick = true;
        this.$store.dispatch(`slaManagement/${urlValue}`, paramsValue).then(() => {
          this.$bkMessage({
            message: this.$t('m.deployPage["保存成功"]'),
            theme: 'success',
          });
          this.closeAgreement(true);
        })
          .catch((res) => {
            this.$bkMessage({
              message: res.data.msg,
              theme: 'error',
            });
          })
          .finally(() => {
            this.secondClick = false;
          });
      },
      closeAgreement(type) {
        if (!type && this.checkDataChange()) {
          this.$bkInfo({
            type: 'warning',
            title: this.$t('m.slaContent["确认返回？"]'),
            // subTitle: this.$t(`m.slaContent["数据发生更改，确认后将不保存修改的数据！"]`),
            confirmFn: () => {
              this.$parent.getList(1);
              this.$parent.closeAgreement();
            },
          });
        } else {
          this.$parent.getList(1);
          this.$parent.closeAgreement();
        }
      },
      // 数据对比
      checkDataChange() {
        return true;
      },
      // 校验
      async submitInfo() {
        const priorityConfigurCheck = await this.$refs.priorityConfigur.checkData();
        const warningEventRemindCheck = await this.$refs.eventRemind1.checkData();
        const timeOutEventRemindCheck = await this.$refs.eventRemind3.checkData();
        this.$refs.dynamicForm.validate().then(() => {
          if (!priorityConfigurCheck && !warningEventRemindCheck && !timeOutEventRemindCheck) {
            if (this.changeInfo.info.id) {
              this.$bkInfo({
                type: 'warning',
                title: this.$t('m.slaContent["确认更新服务协议？"]'),
                // subTitle: this.$t(`m.slaContent["更新的内容将会实时应用在关联的服务中，请谨慎修改！"]`),
                confirmFn: () => {
                  this.submitFn();
                },
              });
            } else {
              this.submitFn();
            }
          }
        });
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../scss/mixins/clearfix.scss';
    @import '../../../scss/mixins/scroller.scss';
    .bk-add-agreement {
        padding: 20px;
    }
    .bk-add-content {
        .bk-content-group {
            width: 100% !important;
            background: white;
            margin-bottom: 18px;
            box-shadow: 0px 2px 6px 0px rgba(6, 6, 6, 0.1);
            border-radius: 2px;
            padding: 16px;
            position: relative;
            .bk-form {
                padding: 0 10px;
            }
            .bk-label {
                font-weight: normal;
            }
        }
        .bk-group-title {
            color: #63656E;
            font-weight: bold;
            line-height: 25px;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .bk-group-title {
            display: inline-block;
            width: 12%;
            color: #63656E;
            font-weight: bold;
            line-height: 25px;
            font-size: 14px;
            margin-bottom: 10px;
            vertical-align: top;
        }
        .bk-form {
            display: inline-block;
            width: 84%;
            position: relative;
            @media screen and (max-width: 1680px){
                display: block !important;
                width: 100% !important;
            }
            .bk-group-table {
                width: 100%;
                border: none;
                position: relative;
            }
            .add-and-reduce-box {
                position: absolute;
                right: -20px;
                top: 50%;
                transform: translateY(-50%);
                .bk-itsm-icon {
                    font-size: 18px;
                    color: #C4C6CC;
                }
            }
            .bk-form-control {
                max-width: 540px;
            }
        }
        .bk-priority-configur {
            display: inline-block;
            box-shadow: 0px 2px 6px 0px rgba(6, 6, 6, 0.1);
            width: 84%;
        }
    }
</style>
