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
      <li style="width: 25%;"><span>{{ $t('m.slaContent["优先级"]') }}</span></li>
      <li style="width: 25%;"><span>{{ $t('m.slaContent["服务模式"]') }}</span></li>
      <li style="width: 25%;" class="tooltipsChackbox">
        <bk-checkbox data-test-id="slaManager-checkbox-appointedTime" v-model="changeInfo.is_reply_need">
          <span
            v-bk-tooltips.top="$t(`m.slaContent['从进入开始节点，到完成响应操作的时间。']`)"
            class="textDashed">
            {{ $t('m.slaContent["约定响应时长"]') }}
          </span>
        </bk-checkbox>
      </li>
      <li style="width: 25%;"><span v-bk-tooltips.top="$t(`m.slaContent['从进入开始节点，到离开结束节点的时间。']`)" class="textDashed">{{ $t('m.slaContent["约定处理时长"]') }}</span></li>
    </ul>
    <ul class="bk-priority-head bk-priority-body" v-for="(item, index) in priorityList" :key="index">
      <li style="width: 25%;">
        <span v-for="(typeItem, typeIndex) in modelPriority"
          :key="typeIndex"
          :data-test-id="`slaAgreement-span-modelPriority-${typeIndex}`"
          style="position: relative;">
          <template v-if="typeItem.key === item.priority">
            <span class="in-select-icon" :style="'background-color: ' + typeColorList[item.priority]"></span>{{typeItem.name}}
          </template>
        </span>
      </li>
      <li style="width: 25%;" class="bk-priority-normal bk-editor-style">
        <bk-form
          :label-width="200"
          form-type="vertical"
          :model="item"
          :rules="scheduleRules"
          ref="schedule">
          <bk-form-item
            data-test-id="slaAgreement-select-modelList"
            :property="'schedule'">
            <bk-select v-model="item.schedule" :ext-cls="'cus-align-left'" searchable>
              <bk-option v-for="option in modelList"
                :key="option.id"
                :id="option.id"
                :name="option.name">
              </bk-option>
              <div slot="extension" @click="handleCreate" style="cursor: pointer;">
                <i class="bk-icon icon-plus-circle"></i>{{$t(`m.slaContent['跳转新建']`)}}
              </div>
            </bk-select>
          </bk-form-item>
        </bk-form>
      </li>
      <li style="width: 25%;" class="bk-priority-normal bk-editor-style bk-none-radius">
        <bk-form
          :label-width="200"
          form-type="vertical"
          :model="item"
          :rules="replyTimeRules"
          ref="replyTime">
          <bk-form-item
            data-test-id="slaAgreement-input-replyTime"
            :property="'reply_time'"
            :icon-offset="iconOffset">
            <bk-input v-model.number="item.reply_time"
              :font-size="'normal'"
              :type="'number'"
              :min="0">
              <bk-dropdown-menu class="group-text"
                @show="dropdownShow(item, 'resp')"
                @hide="dropdownHide(item, 'resp')"
                :ref="'dropdown' + index"
                :key="'dropdown' + index"
                slot="append"
                :font-size="'normal'">
                <bk-button type="primary" slot="dropdown-trigger" :ext-cls="'cus-width'">
                  <span v-for="(time, timeIndex) in timeList" :key="timeIndex">
                    <template v-if="item.reply_unit === time.id">{{ time.name }}</template>
                  </span>
                  <i :class="['bk-icon icon-angle-down',{ 'icon-flip': item.isRespDropdownShow }]"></i>
                </bk-button>
                <ul class="bk-dropdown-list" slot="dropdown-content">
                  <li v-for="(time, timeIndex) in timeList" :key="timeIndex">
                    <a href="javascript:;" data-test-id="slaAgreement-a-timeHandler" @click="timeHandler('reply_unit', time, item, index, 0)">{{ time.name }}</a>
                  </li>
                </ul>
              </bk-dropdown-menu>
            </bk-input>
            <div class="bk-disabled-li" v-if="!changeInfo.is_reply_need"></div>
          </bk-form-item>
        </bk-form>
      </li>
      <li style="width: 25%;" class="bk-priority-normal bk-editor-style bk-none-radius">
        <bk-form
          :label-width="200"
          form-type="vertical"
          :model="item"
          :rules="handleTimeRules"
          ref="handleTime">
          <bk-form-item
            :property="'handle_time'"
            data-test-id="slaAgreement-input-handleTime"
            :icon-offset="iconOffset">
            <bk-input v-model.number="item.handle_time"
              :font-size="'normal'"
              :type="'number'"
              :min="0">
              <bk-dropdown-menu class="group-text"
                @show="dropdownShow(item, 'deal')"
                @hide="dropdownHide(item, 'deal')"
                :ref="'dropdown' + index"
                slot="append"
                :font-size="'normal'">
                <bk-button type="primary" slot="dropdown-trigger" :ext-cls="'cus-width'">
                  <span v-for="(time, timeIndex) in timeList" :key="timeIndex">
                    <template v-if="item.handle_unit === time.id">{{ time.name }}</template>
                  </span>
                  <i :class="['bk-icon icon-angle-down',{ 'icon-flip': item.isDealDropdownShow }]"></i>
                </bk-button>
                <ul class="bk-dropdown-list" slot="dropdown-content">
                  <li v-for="(time, timeIndex) in timeList" :key="timeIndex">
                    <a href="javascript:;" @click="timeHandler('handle_unit', time, item, index, 1)">{{ time.name }}</a>
                  </li>
                </ul>
              </bk-dropdown-menu>
            </bk-input>
          </bk-form-item>
        </bk-form>
      </li>
    </ul>
  </div>
</template>

<script>
  import commonMix from '../../commonMix/common.js';
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
        // 程度颜色
        typeColorList: ['', '#99C5FF', '#FE9C00', '#EA3536'],
        timeList: [
          { id: 'm', name: this.$t('m.slaContent["分钟"]') },
          { id: 'h', name: this.$t('m.slaContent["小时"]') },
          { id: 'd', name: this.$t('m.slaContent["天"]') },
        ],
        priorityList: [],
        historyPriority: [],
        // 校验规则
        scheduleRules: {},
        handleTimeRules: {},
        replyTimeRules: {
          reply_time: [
            {
              message: '字段必填',
              required: true,
              trigger: 'blur',
              type: 'string',
              validator: v => !!v,
            },
          ],
        },
        iconOffset: 75,
      };
    },
    watch: {
      modelPriority() {
        this.initData();
      },
    },
    mounted() {
      this.initData();
      // 初始化校验规则
      this.scheduleRules = this.checkCommonRules('schedule');
      this.handleTimeRules = this.checkCommonRules('handle_time');
    },
    methods: {
      initData() {
        const parentInfo = this.changeInfo.info;
        // 区分初始化和编辑状态priorityList的值不同
        if (!parentInfo.policies.length) {
          this.modelPriority.forEach((item) => {
            this.priorityList.push({
              priority: item.key,
              schedule: '',
              handle_time: '',
              handle_unit: 'h',
              reply_time: '',
              reply_unit: 'h',
              scheduleCheck: false,
              timeCheck: false,
              isRespDropdownShow: false,
              isDealDropdownShow: false,
            });
          });
        } else {
          this.priorityList = [];
          parentInfo.policies.forEach((item) => {
            this.priorityList.push({
              priority: item.priority,
              schedule: item.schedule,
              handle_time: item.handle_time,
              handle_unit: item.handle_unit,
              reply_time: item.reply_time,
              reply_unit: item.reply_unit,
              id: item.id,
              scheduleCheck: false,
              timeCheck: false,
              isRespDropdownShow: false,
              isDealDropdownShow: false,
            });
          });
        }
        // 深拷贝数据
        this.historyPriority = JSON.parse(JSON.stringify(this.priorityList));
      },
      dropdownShow(item, key) {
        if (key === 'resp') {
          item.isRespDropdownShow = true;
        } else if (key === 'deal') {
          item.isDealDropdownShow = true;
        }
      },
      dropdownHide(item, key) {
        if (key === 'resp') {
          item.isRespDropdownShow = false;
        } else if (key === 'deal') {
          item.isDealDropdownShow = false;
        }
      },
      timeHandler(key, time, item, index, order) {
        this.$refs[`dropdown${index}`][order].hide();
        item[key] = time.id;
      },
      // 跳转到新建服务模式
      handleCreate() {
        const routeData = this.$router.resolve({ path: '/project/sla_manage', query: { project_id: this.$store.state.project.id, key: 'create' } });
        window.open(routeData.href, '_blank');
      },
      // 校验
      async checkData() {
        const validates = [];
        let valid = true;
        this.$refs.schedule.forEach((item) => {
          validates.push(item.validate());
        });
        if (this.changeInfo.is_reply_need) {
          this.$refs.replyTime.forEach((item) => {
            validates.push(item.validate());
          });
        }
        this.$refs.handleTime.forEach((item) => {
          validates.push(item.validate());
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
      clearFromError() {
        const refs = ['schedule', 'replyTime', 'handleTime'];
        refs.forEach((item) => {
          this.$refs[item].forEach((ite) => {
            ite.clearError();
          });
        });
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
        background-color: #F0F1F5;
        border-bottom: 1px solid #DCDEE5;
        .cus-align-left{
            text-align: left;
        }
        > li {
            float: left;
            line-height: 46px;
            font-weight: bold;
            padding: 0 20px;
            .in-select-icon {
                display: inline-block;
                width: 8px;
                height: 8px;
                margin-right: 12px;
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
                width: 90px;
            }
        }
        .bk-editor-style {
            padding: 7px 20px;
            .bk-dropdown-list {
                li {
                    font-weight: normal;
                    line-height: 30px;
                    border-right: none;
                }
            }
            /deep/ .bk-label {
                display: none;
            }
        }
    }
</style>

<style lang="scss">
.tooltipsChackbox {
    .bk-form-checkbox {
        vertical-align: sub !important;
    }
    .bk-checkbox-text {
        border-bottom: 1px dashed !important;
        .textDashed {
            border-bottom: none !important;
        }
    }
}
</style>
