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
  <div class="bk-priority-configur">
    <ul class="bk-priority-head">
      <li style="width: 140px;padding-left: 50px"><span>{{ $t('m["提醒事件"]') }}</span></li>
      <li style="width: calc(19% - 35px);"><span>{{ $t('m["提醒规则"]') }}</span></li>
      <li style="width: calc(21% - 35px);"><span>{{ $t('m.slaContent["提醒对象"]') }}</span></li>
      <li style="width: calc(24% - 35px);"><span>{{ $t('m.slaContent["提醒方式"]') }}</span></li>
      <li style="width: calc(36% - 35px);"><span>{{ $t('m.slaContent["提醒频率"]') }}</span></li>
    </ul>

    <ul class="bk-priority-head bk-priority-body" v-for="(item, index) in priorityList" :key="index">
      <li style="width: 140px;padding-right: 10px;" class="bk-transform-10" v-if="!item.hasCheckBox || hasCheckBox">
        <span>
          <bk-checkbox data-test-id="slaAgreement-checkbox-eventName" v-if="item.hasCheckBox" style="padding-right: 10px" v-model="item.isCheck"></bk-checkbox>
          <span v-else style="padding-right: 30px"></span>
          {{item.eventName}}
        </span>
      </li>
      <!-- 提醒规则 -->
      <li style="width: calc(19% - 35px);" class="bk-priority-normal bk-editor-style bk-transform-10" v-if="!item.hasCheckBox || hasCheckBox">
        <bk-form
          :label-width="200"
          form-type="vertical"
          :model="item">
          <bk-form-item>
            {{item.remindRuleText}}
            <span v-if="'remindRuleValue' in item" class="bk-border-bottom">
              <bk-popconfirm data-test-id="slaAgreement-popconfirm-remindRuleValue" placement="bottom" confirm-text="" cancel-text="" trigger="click">
                <div slot="content" style="width: 188px;padding-top: 6px">
                  <bk-slider v-model="item.remindRuleValue"></bk-slider>
                </div>
                {{item.remindRuleValue}}
                {{item.remindRuleUnit}}
              </bk-popconfirm>
            </span>
            <div class="bk-disabled-li" v-if="item.hasCheckBox && !item.isCheck"></div>
          </bk-form-item>
        </bk-form>
      </li>
      <!-- 提醒对象 -->
      <li style="width: calc(21% - 35px);" class="bk-priority-normal bk-editor-style bk-none-radius bk-transform-10" v-if="!item.hasCheckBox || hasCheckBox">
        <bk-form
          :label-width="200"
          form-type="vertical"
          :model="item"
          :rules="receiversRules"
          ref="receivers">
          <bk-form-item
            data-test-id="slaAgreement-select-receivers"
            :property="'receivers'">
            <bk-select v-model="item.receivers" :ext-cls="'cus-align-left'" :clearable="false">
              <bk-option v-for="option in receiversOptionList"
                :key="option.id"
                :id="option.id"
                :name="option.name">
              </bk-option>
            </bk-select>
            <div class="bk-disabled-li" v-if="item.hasCheckBox && !item.isCheck"></div>
          </bk-form-item>
        </bk-form>
      </li>
      <!-- 提醒方式 -->
      <li style="width: calc(24% - 35px);" class="bk-priority-normal bk-editor-style bk-none-radius bk-remind-type" v-if="!item.hasCheckBox || hasCheckBox">
        <bk-form
          :label-width="200"
          form-type="vertical"
          :model="item"
          :rules="notifyTypeRules"
          ref="notifyType">
          <bk-checkbox-group data-test-id="slaAgreement-checkboxGroup-RemindType" v-model="item.notify_type_list" @change="notifyTypeChange(item.notify_type_list, index)">
            <bk-checkbox :value="'email'" style="margin-bottom: 12px">
              {{$t('m.treeinfo["邮件"]')}}
            </bk-checkbox>
            <!-- <bk-checkbox v-for="notice in noticeType" :key="notice.id" :value="notice.typeName.toLowerCase()" style="margin-bottom: 12px">
                            {{ notice.name }}
                        </bk-checkbox> -->
            <bk-checkbox :value="'weixin'">{{$t('m.treeinfo["企业微信"]')}}</bk-checkbox>
            <bk-form-item
              data-test-id="slaAgreement-select-emailNotifyEventList"
              class="cus-email"
              v-if="item.notify_type_list.indexOf('email') !== -1"
              :property="'email_notify'">
              <bk-select
                v-model="item.email_notify"
                :clearable="false"
                :placeholder="$t(`m.slaContent['请选择通知事件']`)"
                size="small"
                :popover-width="150"
                searchable>
                <bk-option v-for="option in notifyEventList['email']"
                  :key="option.id"
                  :id="option.id"
                  :name="option.name">
                </bk-option>
              </bk-select>
            </bk-form-item>
            <bk-form-item
              data-test-id="slaAgreement-select-weixinNotifyEventList"
              class="cus-weixin"
              v-if="item.notify_type_list.indexOf('weixin') !== -1"
              :property="'weixin_notify'">
              <bk-select :clearable="false" :placeholder="$t(`m.slaContent['请选择通知事件']`)" size="small" v-model="item.weixin_notify" searchable>
                <bk-option v-for="option in notifyEventList['weixin']"
                  :key="option.id"
                  :id="option.id"
                  :name="option.name">
                </bk-option>
              </bk-select>
            </bk-form-item>
          </bk-checkbox-group>
          <div class="bk-disabled-li" v-if="item.hasCheckBox && !item.isCheck"></div>
        </bk-form>
      </li>
      <!-- 提醒频率 -->
      <li style="width: calc(36% - 35px);" class="bk-priority-normal bk-editor-style bk-none-radius bk-remind-radio" v-if="!item.hasCheckBox || hasCheckBox">
        <bk-radio-group data-test-id="slaAgreement-radio-notifyRule" v-model="item.notify_rule">
          <bk-radio style="margin-bottom: 6px" :value="'once'">{{$t('m.slaContent["单次提醒"]')}}</bk-radio>
          <bk-radio :value="'retry'">
            {{$t('m.slaContent["递增首次提醒后，耗时每增加"]')}}
            <span class="bk-border-bottom">
              <input data-test-id="slaAgreement-radio-notifyFreq" @change="notifyFreqChange(item.notify_freq, index)" type="number" v-model.number="item.notify_freq">
            </span>
            <span class="freq-unit">
              <bk-dropdown-menu class="group-text"
                @show="dropdownShow()"
                @hide="dropdownHide()"
                :ref="'dropdown' + index"
                slot="append"
                :font-size="'normal'">
                <bk-button type="primary" slot="dropdown-trigger" :ext-cls="'cus-width'">
                  <span v-for="(time, timeIndex) in timeList" :key="timeIndex">
                    <template v-if="item.freq_unit === time.id">{{ time.name }}</template>
                  </span>
                  <i :class="['bk-icon icon-angle-down',{ 'icon-flip': item.isDropdownShow }]"></i>
                </bk-button>
                <ul class="bk-dropdown-list" slot="dropdown-content">
                  <li v-for="(time, timeIndex) in timeList" :key="timeIndex">
                    <a href="javascript:;" :data-test-id="`slaAgreement-a-timeHandler-${timeIndex}`" @click="timeHandler(time, item, index)">{{ time.name }}</a>
                  </li>
                </ul>
              </bk-dropdown-menu>
            </span>
            {{$t('m.slaContent["再次提醒"]')}}</bk-radio>
        </bk-radio-group>
        <div class="bk-disabled-li" v-if="item.hasCheckBox && !item.isCheck"></div>
      </li>
    </ul>
  </div>
</template>

<script>
  import commonMix from '../../commonMix/common.js';
  import { mapState } from 'vuex';

  export default {
    name: 'priorityConfigur',
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
      hasCheckBox: {
        type: Boolean,
        default() {
          return false;
        },
      },
    },
    data() {
      return {
        priorityList: [],
        isDropdownShow: false,
        // 程度颜色
        typeColorList: ['', '#99C5FF', '#FE9C00', '#EA3536'],
        timeList: [
          { id: '%', name: '%' },
          { id: 'm', name: this.$t('m.slaContent["分钟"]') },
          { id: 'h', name: this.$t('m.slaContent["小时"]') },
          { id: 'd', name: this.$t('m.slaContent["天"]') },
        ],
        receiversOptionList: [
          {
            id: 'PROCESSORS',
            name: this.$t('m.slaContent["处理人"]'),
          },
          {
            id: 'HISTORY_HANDLER',
            name: this.$t('m.slaContent["历史处理人"]'),
          },
          {
            id: 'ADMIN',
            name: this.$t('m.slaContent["服务管理员"]'),
          },
        ],
        historyPriority: [],
        oldNotifyTypeList: [],
        // 校验规则
        scheduleRules: {},
        selectRules: {},
        receiversRules: {
          receivers: [
            {
              message: '字段必填',
              required: true,
              type: 'string',
              trigger: 'blur',
              validator: (v) => !!v,
            },
          ],
        },
        notifyTypeRules: {
          email_notify: [
            {
              message: '字段必填',
              required: true,
              type: 'string',
              trigger: 'blur',
              validator: (v) => !!v,
            },
          ],
          weixin_notify: [
            {
              message: '字段必填',
              required: true,
              type: 'string',
              trigger: 'blur',
              validator: (v) => !!v,
            },
          ],
        },
        iconOffset: 75,
      };
    },
    computed: {
      ...mapState({
        noticeType: state => state.common.configurInfo.notify_type,
      }),
    },
    watch: {
      modelPriority() {
        if (!this.changeInfo.info.id) {
          this.priorityList = JSON.parse(JSON.stringify(this.modelPriority));
        }
      },
    },
    mounted() {
      this.initData();
      // 初始化校验规则
      this.scheduleRules = this.checkCommonRules('schedule');
      this.selectRules = this.checkCommonRules('select');
    },
    methods: {
      initData() {
        const parentInfo = this.changeInfo.info;
        // 区分初始化和编辑状态priorityList的值不同
        if (!parentInfo.policies.length) {
          this.priorityList = JSON.parse(JSON.stringify(this.modelPriority));
        } else {
          this.priorityList = [];
          let pushData = {};
          let emailNotify = '';
          let weixinNotify = '';
          this.modelPriority.forEach(item => {
            pushData = item;
            parentInfo.action_policies.forEach(policie => {
              if (policie.type === item.type) {
                emailNotify = policie.actions[0].config.notify.find(notifyObj => notifyObj.notify_type === 'email');
                weixinNotify = policie.actions[0].config.notify.find(notifyObj => notifyObj.notify_type === 'weixin');
                pushData = {
                  ...item,
                  isCheck: true,
                  remindRuleValue: policie.condition.expressions[0].value,
                  receivers: policie.actions[0].config.receivers,
                  notify_type_list: policie.actions[0].config.notify.map(notifyObj => notifyObj.notify_type),
                  email_notify: emailNotify && emailNotify.notify_template,
                  weixin_notify: weixinNotify && weixinNotify.notify_template,
                  notify_rule: policie.actions[0].config.notify_rule,
                  notify_freq: policie.actions[0].config.notify_freq,
                  freq_unit: policie.actions[0].config.freq_unit,
                };
              }
            });
            this.priorityList.push(pushData);
          });
        }
      },
      dropdownShow() {
        this.isDropdownShow = true;
      },
      dropdownHide() {
        this.isDropdownShow = false;
      },
      timeHandler(time, item, index) {
        this.$refs[`dropdown${index}`][0].hide();
        item.freq_unit = time.id;
      },
      // 跳转到新建服务模式
      handleCreate() {
        this.$router.push({ name: 'slaManager', params: { key: 'create' } });
      },
      notifyFreqChange(notifyFreq, index) {
        if (notifyFreq <= 0) {
          this.priorityList[index].notify_freq = 10;
          this.$bkMessage({
            message: this.$t('m.slaContent["不可设置小于等于0的数字"]'),
            theme: 'warning',
          });
        }
      },
      notifyTypeChange(notifyTypeList, index) {
        if (notifyTypeList.length === 1) {
          this.oldNotifyTypeList[index] = notifyTypeList;
        }
        if (notifyTypeList.length === 0) {
          this.priorityList[index].notify_type_list = [...this.oldNotifyTypeList[index]];
          this.$bkMessage({
            message: this.$t('m.slaContent["至少选择一项提醒方式"]'),
            theme: 'warning',
          });
        }
      },
      // 校验
      async checkData() {
        const validates = [];
        let valid = true;
        const checkIndexList = [];
        this.priorityList.forEach(mp => {
          if (!mp.hasCheckBox || mp.isCheck) checkIndexList.push(mp.type);
        });
        this.$refs.receivers.forEach(item => {
          if (checkIndexList.indexOf(item.model.type) !== -1) validates.push(item.validate());
        });
        this.$refs.notifyType.forEach(item => {
          if (!item.model.hasCheckBox || item.model.isCheck) validates.push(item.validate());
        });
        await Promise.all(validates).then(() => {
          valid = false;
        })
          .catch(() => {
            // 防止出现Uncaught
            valid = true;
          });
        return valid;
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../scss/mixins/clearfix.scss';
    @import '../../../scss/mixins/scroller.scss';

    .bk-priority-configur {
        color: #63656E;
        font-size: 12px;
        width: 87% !important;
        position: relative;
        @media screen and (max-width: 1680px){
            display: block !important;
            width: 100% !important;
        }
        .textDashed {
            font-size: 12px;
            border-bottom: 1px dashed !important;
            cursor: pointer;
        }
        
    }
    .bk-priority-head {
        @include clearfix;
        max-width: 100%;
        background-color: #F0F1F5;
        border-bottom: 1px solid #DCDEE5;
        .cus-align-left{
            text-align: left;
        }
        >li {
            float: left;
            line-height: 46px;
            font-weight: bold;
            padding: 0 20px;
            .in-select-icon {
                position: absolute;
                left: -20px;
                top: 50%;
                width: 8px;
                height: 8px;
                transform: translateY(-50%);
            }
            .bk-disabled-li {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: #FAFBFD;
                opacity: 0.5;
                cursor: not-allowed;
            }
        }
    }
    .bk-priority-body {
        background-color: #FFFFFF;
        border-top: none;
        .bk-priority-normal {
            font-weight: normal;
            .cus-width {
                display: inline;
                float: none;
                vertical-align: inherit;
                padding: 0 6px;
                font-size: 12px;
                border: none;
                border-radius: 0;
                min-width: 0;
                border-bottom: 1px solid #bdbfc5;
                height: inherit;
                line-height: 18px;
            }
        }
        .bk-editor-style {
            padding: 7px 20px;
            position: relative;
            .bk-dropdown-list {
                li {
                    font-weight: normal;
                    line-height: 30px;
                    border-right: none;
                }
            }
            .bk-border-bottom {
                display: inline-block;
                text-align: center;
                // margin: 0 2px;
                padding: 0 6px;
                border-bottom: 1px solid #bdbfc5;
                cursor: pointer;
                input {
                    border: none;
                    display: inline-block;
                    text-align: center;
                    width: 30px;
                }
                input::-webkit-outer-spin-button, input::-webkit-inner-spin-button{-webkit-appearance: none;}
            }
            .cus-email {
                position: absolute;
                left: 56px;
                top: -4px;
                display: inline-block;
                width: 60%;
                margin-left: 20px;
                vertical-align: middle;
                .bk-form .bk-form-content {
                    min-height: none;
                }
            }
            .cus-weixin {
                position: absolute;
                left: 56px;
                top: 18px;
                display: inline-block;
                width: 60%;
                margin-left: 20px;
                vertical-align: middle;
            }
            /deep/ .bk-label {
                display: none;
            }
        }
        .bk-transform-10 {
            transform: translateY(10px);
        }
    }
</style>

<style lang="scss">
.cus-email,.cus-weixin {
    .bk-form-content {
        .tooltips-icon {
            top: 5px;
        }
    }
}
.bk-remind-type {
    .bk-form-checkbox {
        display: block;
    }
    .bk-checkbox-text {
        font-size: 12px;
    }
}
.bk-remind-radio {
    .bk-form-radio {
        display: block;
        font-size: 12px;
    }
    .bk-form-radio .bk-radio-text {
        display: inline;
        vertical-align: inherit;
    }
    .bk-form-radio:first-of-type .bk-radio-text {
        margin-left: 3px;
    }
}
.freq-unit .bk-dropdown-menu .bk-dropdown-list > li > a {
    height: 26px;
    line-height: 26px;
}
</style>
