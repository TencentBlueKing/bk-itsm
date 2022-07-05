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
  <div class="bk-add-model">
    <!-- title -->
    <div class="is-title" :class="{ 'bk-title-left': !sliderStatus }">
      <p class="bk-come-back" @click="backList">
        <arrows-left-icon></arrows-left-icon>
        {{ isEdit ? changeInfo.info.name : $t('m.slaContent["新增服务模式"]') }}
      </p>
    </div>
    <!-- content -->
    <div class="bk-add-content">
      <div class="bk-content-group" style="width: 400px;">
        <p class="bk-group-title">{{ $t('m.slaContent["基本信息"]') }}</p>
        <bk-form
          :label-width="200"
          form-type="vertical"
          :model="formInfo"
          :rules="nameRules"
          ref="dynamicForm">
          <bk-form-item
            data-test-id="slaModel-input-modelName"
            :label="$t(`m.slaContent['服务模式名称']`)"
            :required="true"
            :property="'name'">
            <bk-input v-model.trim="formInfo.name"
              maxlength="120"
              :placeholder="$t(`m.slaContent['请输入模式名称']`)"
              :disabled="changeInfo.info.is_builtin">
            </bk-input>
          </bk-form-item>
        </bk-form>
      </div>
      <div class="bk-content-group">
        <p class="bk-group-title">{{ $t('m.slaContent["工作时间"]') }}</p>
        <bk-form
          :label-width="200"
          form-type="vertical"
          :model="formInfo"
          ref="daysForm">
          <div class="bk-group-table"
            style="padding-right: 35px;"
            v-for="(item, index) in formInfo.days"
            :key="index">
            <div class="bk-group-select" style="width: 400px; height: 64px;">
              <bk-form-item
                :label="$t(`m.slaContent['星期']`)"
                :required="true"
                :rules="weekRules.week"
                :property="'days.' + index + '.week'">
                <bk-select v-model="item.week"
                  multiple
                  show-select-all
                  searchable>
                  <bk-option v-for="option in weekList"
                    :key="option.id"
                    :id="option.id"
                    :name="option.name">
                  </bk-option>
                </bk-select>
              </bk-form-item>
            </div>
            <ul class="bk-group-time">
              <li v-for="(timeItem, timeIndex) in item.time" :key="timeIndex">
                <p class="bk-width-label">
                  <bk-popconfirm
                    placement="bottom-start"
                    v-if="!timeItem.changStatus"
                    style="line-height: 25px;"
                    trigger="click"
                    :confirm-text="$t(`m.slaContent['确定']`)"
                    :cancel-text="$t(`m.slaContent['取消']`)"
                    @confirm="timeItem.name = timeItemNameTemplate">
                    <div slot="content">
                      <bk-input v-model.trim="timeItemNameTemplate"
                        style="width:226px"
                        maxlength="120"
                        :placeholder="$t(`m.slaContent['请输入时段名称']`)">
                      </bk-input>
                    </div>
                    <span @click="timeItemNameTemplate = timeItem.name" class="cus-ellipsis" :title="timeItem.name">{{ timeItem.name }}</span>
                  </bk-popconfirm>
                  <i class="bk-icon icon-delete"
                    v-if="item.time.length !== 1"
                    @click="deleteTimeName(item.time, timeIndex)"></i>
                </p>
                <div class="bk-form-content bk-sla-time">
                  <bk-time-picker
                    v-model="timeItem.value"
                    :type="'timerange'"
                    :clearable="false">
                  </bk-time-picker>
                  <div class="bk-group-icon" v-if="timeIndex === item.time.length - 1">
                    <i v-if="item.time.length !== 3"
                      class="bk-itsm-icon"
                      v-bk-tooltips="bktooltipsInfo.addTime"
                      @click="addTimeFrame(index,'days')">+</i>
                    <i v-else class="icon-flow-add bk-icon-false"
                      v-bk-tooltips="bktooltipsInfo.overTime"></i>
                  </div>
                </div>
              </li>
            </ul>
            <div class="add-and-reduce-box">
              <div v-if="formInfo.days.length !== 1" class="bk-add-group" @click="deleteLine(item, index, 'days')">
                <i class="bk-itsm-icon icon-flow-reduce"></i>
              </div>
              <div class="bk-add-group" @click="addLine('days')">
                <i class="bk-itsm-icon icon-flow-add"></i>
              </div>
            </div>
          </div>
        </bk-form>
                
      </div>
      <div class="bk-content-group">
        <p class="bk-group-title">{{ $t('m.slaContent["加班时间"]') }}</p>
        <bk-form
          :label-width="200"
          form-type="vertical"
          :model="formInfo"
          ref="workdaysForm">
          <div class="bk-group-table"
            style="padding-right: 35px;"
            v-for="(item, index) in formInfo.workdays"
            :key="index">
            <div class="bk-group-select" style="width: 400px; height: 64px;">
              <bk-form-item
                :label="$t(`m.slaContent['日期']`)"
                :required="true"
                :rules="dayTimeRules.dayTime"
                :property="'workdays.' + index + '.dayTime'">
                <bk-date-picker
                  v-model="item.dayTime"
                  :type="'daterange'"
                  :clearable="false"
                  :ext-cls="'cus-width'">
                </bk-date-picker>
              </bk-form-item>
            </div>
            <ul class="bk-group-time">
              <li v-for="(timeItem, timeIndex) in item.time" :key="timeIndex">
                <p class="bk-width-label">
                  <bk-popconfirm
                    placement="bottom-start"
                    v-if="!timeItem.changStatus"
                    style="line-height: 25px;"
                    trigger="click"
                    :confirm-text="$t(`m.slaContent['确定']`)"
                    :cancel-text="$t(`m.slaContent['取消']`)"
                    @confirm="timeItem.name = timeItemNameTemplate">
                    <div slot="content">
                      <bk-input v-model.trim="timeItemNameTemplate"
                        style="width:226px"
                        maxlength="120"
                        :placeholder="$t(`m.slaContent['请输入时段名称']`)">
                      </bk-input>
                    </div>
                    <span @click="timeItemNameTemplate = timeItem.name" class="cus-ellipsis" :title="timeItem.name">{{ timeItem.name }}</span>
                  </bk-popconfirm>
                  <i class="bk-icon icon-delete"
                    v-if="item.time.length !== 1"
                    @click="deleteTimeName(item.time, timeIndex)"></i>
                </p>
                <div class="bk-form-content bk-sla-time">
                  <bk-time-picker
                    v-model="timeItem.value"
                    :type="'timerange'"
                    :clearable="false">
                  </bk-time-picker>
                  <div class="bk-group-icon" v-if="timeIndex === item.time.length - 1">
                    <i v-if="item.time.length !== 3"
                      class="bk-itsm-icon"
                      v-bk-tooltips="bktooltipsInfo.addTime"
                      @click="addTimeFrame(index,'workdays')">+</i>
                    <i v-else class="icon-flow-add bk-icon-false"
                      v-bk-tooltips="bktooltipsInfo.overTime"></i>
                  </div>
                </div>
              </li>
            </ul>
            <div class="add-and-reduce-box">
              <div class="bk-add-group" @click="deleteLine(item, index, 'workdays')">
                <i class="bk-itsm-icon icon-flow-reduce"></i>
              </div>
              <div class="bk-add-group" @click="addLine('workdays')">
                <i class="bk-itsm-icon icon-flow-add"></i>
              </div>
            </div>
          </div>
          <div class="add-and-reduce-box" v-if="formInfo.workdays.length === 0">
            <div class="bk-add-group" data-test-id="slaPattern_div_addGroup" @click="addLine('workdays')">
              <i class="bk-itsm-icon icon-flow-add"></i>
            </div>
          </div>
        </bk-form>
      </div>
      <!-- 假期时间 -->
      <div class="bk-content-group">
        <p class="bk-group-title">{{ $t('m.slaContent["假期时间"]') }}</p>
        <bk-form
          :label-width="200"
          form-type="vertical"
          :model="formInfo"
          ref="timeOutForm"
          :key="formKey">
          <div class="bk-group-table"
            style="padding-right: 35px;"
            v-for="(item, index) in formInfo.holidays"
            :key="index">
            <div class="bk-group-select" style="width: 400px; height: 64px;">
              <bk-form-item
                :label="$t(`m.slaContent['节日名称']`)"
                :required="true"
                :rules="dayNameRules.dayName"
                :property="'holidays.' + index + '.dayName'">
                <bk-input v-model.trim="item.dayName"
                  :placeholder="$t(`m.slaContent['请输入节假日名称']`)">
                </bk-input>
              </bk-form-item>
            </div>
            <div class="bk-group-select" style="width: 200px; height: 64px;">
              <bk-form-item
                :label="$t(`m.slaContent['节日日期']`)"
                :required="true">
                <bk-date-picker
                  v-model="item.dayTime"
                  :type="'daterange'"
                  :clearable="false">
                </bk-date-picker>
              </bk-form-item>
            </div>
            <ul class="bk-group-time">
              <li v-for="(timeItem, timeIndex) in item.time" :key="timeIndex">
                <p class="bk-width-label">
                  <bk-popconfirm
                    placement="bottom-start"
                    v-if="!timeItem.changStatus"
                    style="line-height: 25px;"
                    trigger="click"
                    :confirm-text="$t(`m.slaContent['确定']`)"
                    :cancel-text="$t(`m.slaContent['取消']`)"
                    @confirm="timeItem.name = timeItemNameTemplate">
                    <div slot="content">
                      <bk-input v-model.trim="timeItemNameTemplate"
                        style="width:226px"
                        maxlength="120"
                        :placeholder="$t(`m.slaContent['请输入时段名称']`)">
                      </bk-input>
                    </div>
                    <span @click="timeItemNameTemplate = timeItem.name" class="cus-ellipsis" :title="timeItem.name">{{ timeItem.name }}</span>
                  </bk-popconfirm>
                  <i class="bk-icon icon-delete"
                    v-if="item.time.length !== 1"
                    @click="deleteTimeName(item.time, timeIndex)"></i>
                </p>
                <div class="bk-form-content bk-sla-time">
                  <bk-time-picker
                    v-model="timeItem.value"
                    :type="'timerange'"
                    :clearable="false">
                  </bk-time-picker>
                  <div class="bk-group-icon" v-if="timeIndex === item.time.length - 1">
                    <i v-if="item.time.length !== 3"
                      class="bk-itsm-icon"
                      v-bk-tooltips="bktooltipsInfo.addTime"
                      @click="addTimeFrame(index,'holidays')">+</i>
                    <i v-else class="icon-flow-add bk-icon-false"
                      v-bk-tooltips="bktooltipsInfo.overTime"></i>
                  </div>
                </div>
              </li>
            </ul>
            <div class="add-and-reduce-box">
              <div class="bk-add-group" @click="deleteLine(item, index, 'holidays')">
                <i class="bk-itsm-icon icon-flow-reduce"></i>
              </div>
              <div class="bk-add-group" @click="addLine('holidays')">
                <i class="bk-itsm-icon icon-flow-add"></i>
              </div>
            </div>
          </div>
          <div class="add-and-reduce-box" v-if="formInfo.holidays.length === 0">
            <div class="bk-add-group" @click="addLine('holidays')">
              <i class="bk-itsm-icon icon-flow-add"></i>
            </div>
          </div>
        </bk-form>
      </div>
      <div class="bk-model-btn">
        <bk-button
          data-test-id="slaModel-button-modelSave"
          v-if="isEdit"
          theme="primary"
          :title="$t(`m.deployPage['保存']`)"
          class="mr10"
          @click="saveSchedule"
          :disabled="clickSecond">{{ $t(`m.deployPage['保存']`) }}
        </bk-button>
        <bk-button
          data-test-id="slaModel-button-modelSubmit"
          v-else
          theme="primary"
          :title="$t(`m.slaContent['提交']`)"
          class="mr10"
          @click="saveSchedule"
          :disabled="clickSecond">{{$t(`m.slaContent['提交']`)}}
        </bk-button>
        <bk-button
          data-test-id="slaModel-button-modelClose"
          theme="default"
          :title="$t(`m.wiki['取消']`)"
          class="mr10"
          :disabled="clickSecond"
          @click="backList">{{ $t(`m.wiki['取消']`) }}
        </bk-button>
      </div>
    </div>
    <!-- 添加时段 -->
    <bk-dialog
      v-model="timeInfo.show"
      :render-directive="'if'"
      :width="timeInfo.width"
      :header-position="timeInfo.headerPosition"
      :auto-close="timeInfo.autoClose"
      :mask-close="timeInfo.autoClose"
      @confirm="TimeFrameComfirm">
      <p slot="header">
        {{tempTime.isEdit ? $t(`m.slaContent["修改时段"]`) : $t(`m.slaContent["添加时段"]`)}}
      </p>
      <div class="bk-add-project bk-add-module">
        <bk-form
          :label-width="200"
          form-type="vertical"
          :model="tempTime.info"
          :rules="nameRules"
          ref="dialogForm">
          <bk-form-item
            :label="$t(`m.slaContent['时段名称']`)"
            :required="true"
            :property="'name'">
            <bk-input v-model.trim="tempTime.info.name"
              maxlength="120"
              :placeholder="$t(`m.slaContent['请输入时段名称']`)">
            </bk-input>
          </bk-form-item>
          <bk-form-item
            :label="$t(`m.slaContent['起止时间']`)"
            :required="true">
            <bk-time-picker
              v-model="tempTime.info.value"
              :type="'timerange'"
              :clearable="false">
            </bk-time-picker>
          </bk-form-item>
        </bk-form>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
  import { errorHandler } from '../../utils/errorHandler.js';
  import commonMix from '../commonMix/common.js';
  export default {
    name: 'addModel',
    mixins: [commonMix],
    props: {
      changeInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      isEdit: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        clickSecond: false,
        formInfo: {
          name: '',
          days: [],
          workdays: [],
          holidays: [],
          id: -1,
        },
        oldForm: {},
        multiSelect: true,
        weekList: [
          { id: '0', name: this.$t('m.slaContent["周一"]') },
          { id: '1', name: this.$t('m.slaContent["周二"]') },
          { id: '2', name: this.$t('m.slaContent["周三"]') },
          { id: '3', name: this.$t('m.slaContent["周四"]') },
          { id: '4', name: this.$t('m.slaContent["周五"]') },
          { id: '5', name: this.$t('m.slaContent["周六"]') },
          { id: '6', name: this.$t('m.slaContent["周日"]') },
        ],
        // 添加时段
        timeInfo: {
          show: false,
          width: 400,
          headerPosition: 'left',
          autoClose: false,
          title: this.$t('m.slaContent["添加时段"]'),
          info: {},
        },
        aaa: '',
        // 添加时段中间数据
        tempTime: {
          index: -1,
          type: '',
          info: {
            name: '',
            value: ['08:00:00', '12:00:00'],
          },
        },
        hasFalse: false,
        // 校验规则
        nameRules: {},
        dayNameRules: {},
        dayTimeRules: {},
        weekRules: {},
        infoStatus: {},
        // toolTips提示
        bktooltipsInfo: {
          addTime: {
            content: this.$t('m.slaContent[\'添加时段\']'),
            showOnInit: false,
            placements: ['top'],
          },
          overTime: {
            content: this.$t('m.slaContent[\'最多只能添加三个时段\']'),
            showOnInit: false,
            placements: ['top'],
          },
        },
        formKey: 0,
        timeItemNameTemplate: '',
      };
    },
    computed: {
      sliderStatus() {
        return this.$store.state.common.slideStatus;
      },
    },
    mounted() {
      if (this.isEdit) {
        this.transferSchedule();
      } else {
        this.addLine('days');
      }
      this.initData();
      // 初始化校验规则
      this.nameRules = this.checkCommonRules('name');
      this.dayNameRules = this.checkCommonRules('dayName');
      this.dayTimeRules = this.checkCommonRules('dayTime');
      this.weekRules = this.checkCommonRules('week');
    },
    methods: {
      initData() {
        this.oldForm = JSON.parse(JSON.stringify(this.formInfo));
      },
      // 继续添加
      addLine(type) {
        const valueInfo = {};
        const timeList = [
          { name: this.$t('m.slaContent["上午"]'), value: ['08:00:00', '12:00:00'], changStatus: false },
          { name: this.$t('m.slaContent["下午"]'), value: ['14:00:00', '18:00:00'], changStatus: false },
        ];
        if (type === 'days') {
          valueInfo.week = [];
          valueInfo.time = timeList;
          if (!this.formInfo.days.length) {
            for (let i = 0; i < 5; i++) {
              valueInfo.week.push(String(i));
            }
          }
        } else if (type === 'workdays') {
          valueInfo.dayTime = [];
          valueInfo.time = timeList;
        } else {
          valueInfo.dayName = '';
          valueInfo.dayTime = '';
          valueInfo.time = [
            { name: this.$t('m.slaContent["全天"]'), value: ['00:00:00', '23:59:59'], changStatus: false },
          ];
        }
        this.formInfo[type].push(valueInfo);
      },
      // 删除组
      deleteLine(item, index, type) {
        this.formInfo[type].splice(index, 1);
        this.formKey = new Date().getTime();
      },
      // 添加时段弹窗按钮
      TimeFrameComfirm() {
        this.$refs.dialogForm.validate().then(() => {
          const temp = {
            name: this.tempTime.info.name,
            changStatus: false,
            value: this.tempTime.info.value,
          };
          // 添加时段模式
          if (!this.tempTime.isEdit) {
            this.formInfo[this.tempTime.type][this.tempTime.index].time.push(temp);
          } else {
            this.formInfo[this.tempTime.type][this.tempTime.index].time.splice(this.tempTime.timeIndex, 1, temp);
          }
          this.timeInfo.show = false;
        });
      },
      // 添加时段
      addTimeFrame(index, type) {
        const temp = {
          name: this.$t('m.slaContent["晚上"]'),
          changStatus: false,
          value: ['08:00:00', '12:00:00'],
        };
        this.formInfo[type][index].time.push(temp);
      },
      // 修改时段名
      changeTimeName(timeItem, timeIndex, index, type) {
        this.tempTime = {
          index,
          timeIndex,
          type,
          info: {
            name: timeItem.name,
            value: timeItem.value,
          },
          isEdit: true,
        };
        this.timeInfo.show = true;
      },
      // 删除时段
      deleteTimeName(timeItem, timeIndex) {
        timeItem.splice(timeIndex, 1);
      },
      // 保存服务模式
      saveSchedule() {
        this.$refs.dynamicForm.validate().then(() => {
          if (this.formInfo.holidays.length) {
            this.$refs.timeOutForm.validate().then(() => {
              if (this.isEdit) {
                this.$bkInfo({
                  type: 'warning',
                  title: this.$t('m.slaContent["确认更新服务模式？"]'),
                  subTitle: this.$t('m.slaContent["更新的内容将会实时应用在关联的服务协议中，请谨慎修改！"]'),
                  confirmFn: () => {
                    this.ajaxSubmit();
                  },
                });
              } else {
                this.ajaxSubmit();
              }
            }, () => {
            });
          } else {
            this.ajaxSubmit();
          }
        }, () => {
        });
      },
      ajaxSubmit() {
        const copyFormInfo = JSON.parse(JSON.stringify(this.formInfo));
        const params = {
          name: copyFormInfo.name,
          is_enabled: true,
          days: [],
          workdays: [],
          holidays: [],
          id: copyFormInfo.id,
          project_key: this.$store.state.project.id,
        };
        // 格式化工作日数据
        for (let i = 0; i < copyFormInfo.days.length; i++) {
          const duration = this.backObject(copyFormInfo.days[i].time);
          const day = {
            type_of_day: 'NORMAL',
            day_of_week: copyFormInfo.days[i].week.join(','),
            duration,
            id: copyFormInfo.days[i].id,
          };
          params.days.push(day);
        }
        if (params.days.length === 0) {
          this.$bkMessage({
            message: this.$t('m.slaContent["工作时间不能为空！"]'),
            theme: 'error',
          });
          return;
        }
        // 格式化加班日数据
        for (let i = 0; i < copyFormInfo.workdays.length; i++) {
          const duration = this.backObject(copyFormInfo.workdays[i].time);
          const workday = {
            type_of_day: 'WORKDAY',
            start_date: this.standardDayTime(copyFormInfo.workdays[i].dayTime[0]),
            end_date: this.standardDayTime(copyFormInfo.workdays[i].dayTime[1]),
            duration,
            id: copyFormInfo.workdays[i].id,
          };
          params.workdays.push(workday);
        }
        // 格式化假期数据
        for (let i = 0; i < copyFormInfo.holidays.length; i++) {
          const duration = this.backObject(copyFormInfo.holidays[i].time);
          const holiday = {
            type_of_day: 'HOLIDAY',
            start_date: this.standardDayTime(copyFormInfo.holidays[i].dayTime[0]),
            end_date: this.standardDayTime(copyFormInfo.holidays[i].dayTime[1]),
            duration,
            name: copyFormInfo.holidays[i].dayName,
            id: copyFormInfo.holidays[i].id,
          };
          params.holidays.push(holiday);
        }
        if (!this.isEdit) {
          params.project_key = this.$store.state.project.id;
          this.$store.dispatch('sla/saveSchedule', params).then(() => {
            this.$bkMessage({
              message: this.$t('m.slaContent["提交成功！"]'),
              theme: 'success',
            });
            this.submitBack();
          }, res => {
            errorHandler(res, this);
          });
        } else {
          this.$store.dispatch('sla/updateSchedule', params).then(() => {
            this.$bkMessage({
              message: this.$t('m.slaContent["修改成功！"]'),
              theme: 'success',
            });
            this.submitBack();
          }, res => {
            errorHandler(res, this);
          });
        }
      },
      // 提取返回数组的列表
      backObject(list) {
        const resultList = list.map(item => ({
          start_time: item.value[0],
          end_time: item.value[1],
          name: item.name,
          id: item.id,
        }));
        return resultList;
      },
      // 编辑时转化格式
      transferSchedule() {
        const copyChangeInfo = JSON.parse(JSON.stringify(this.changeInfo.info));
        this.formInfo.name = copyChangeInfo.name;
        this.formInfo.id = copyChangeInfo.id;
        // days 转换
        if (copyChangeInfo.days.length) {
          copyChangeInfo.days.forEach(item => {
            const tempDay = {
              time: [],
              week: [],
              id: item.id,
            };
            tempDay.week = item.day_of_week.split(',');
            item.duration.forEach(ite => {
              const tempDaytime = {
                changStatus: false,
                name: ite.name,
                id: ite.id,
                value: [],
              };
              tempDaytime.value.push(ite.start_time);
              tempDaytime.value.push(ite.end_time);
              tempDay.time.push(tempDaytime);
            });
            this.formInfo.days.push(tempDay);
          });
        } else {
          const tempDay = {
            time: [
              {
                changStatus: false,
                name: this.$t('m.slaContent["24小时"]'),
                value: ['00:00:00', '23:59:59'],
              },
            ],
            week: [0, 1, 2, 3, 4, 5, 6],
          };
          this.formInfo.days.push(tempDay);
        }
        // workdays转换
        copyChangeInfo.workdays.forEach(item => {
          const tempWorkday = {
            time: [],
            dayTime: [],
            id: item.id,
          };
          tempWorkday.dayTime.push(item.start_date);
          tempWorkday.dayTime.push(item.end_date);
          item.duration.forEach(ite => {
            const tempWorkDaytime = {
              changStatus: false,
              name: ite.name,
              id: ite.id,
              value: [],
            };
            tempWorkDaytime.value.push(ite.start_time);
            tempWorkDaytime.value.push(ite.end_time);
            tempWorkday.time.push(tempWorkDaytime);
          });
          this.formInfo.workdays.push(tempWorkday);
        });
        // holidays转换
        copyChangeInfo.holidays.forEach(item => {
          const tempHolidays = {
            dayName: item.name,
            dayTime: [],
            id: item.id,
            time: [],
          };
          item.duration.forEach(ite => {
            const tempholiDaytime = {
              changStatus: false,
              name: ite.name,
              id: ite.id,
              value: [],
            };
            tempholiDaytime.value.push(ite.start_time);
            tempholiDaytime.value.push(ite.end_time);
            tempHolidays.time.push(tempholiDaytime);
          });
          tempHolidays.dayTime.push(item.start_date);
          tempHolidays.dayTime.push(item.end_date);
          this.formInfo.holidays.push(tempHolidays);
        });
      },
      // 取消（返回列表）
      backList() {
        if (JSON.stringify(this.formInfo) !== JSON.stringify(this.oldForm)) {
          this.$bkInfo({
            type: 'warning',
            title: this.$t('m.slaContent["确认返回？"]'),
            // subTitle: this.$t(`m.slaContent["数据发生更改，确认后将不保存修改的数据！"]`),
            confirmFn: () => {
              this.$parent.changeInfo.isShow = false;
            },
          });
        } else {
          this.$parent.changeInfo.isShow = false;
        }
      },
      submitBack() {
        this.$parent.changeInfo.isShow = false;
        this.$parent.getModelList();
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../scss/mixins/clearfix.scss';
    @import '../../scss/mixins/scroller.scss';

    .bk-add-model {
      padding: 20px;
    }

    .cus-width{
        width: 100%;
    }

    .bk-add-content {
        .bk-content-group {
            width: 100% !important;
            margin-bottom: 18px;
            box-shadow: 0px 2px 6px 0px rgba(6, 6, 6, 0.1);
            border-radius: 2px;
            padding: 16px;
            position: relative;
            background: #fff;

            .bk-group-time{
                .bk-width-label {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    width: 100%;
                    color: #666;
                    font-size: 14px;
                    line-height: 32px;
                    font-weight: 400;

                    &:hover {
                        .bk-icon {
                            opacity: 1;
                        }
                    }
                    .bk-icon {
                        opacity: 0;
                        margin-left: 5px;
                        cursor: pointer;

                        &:hover {
                            color: #3A84FF;
                        }
                    }
                    .cus-ellipsis{
                        display: inline-block;
                        overflow: hidden;
                        white-space: nowrap;
                        text-overflow: ellipsis;
                        cursor: pointer;
                    }
                }
            }

            .bk-change-label {
                padding: 2px 0 7px;
            }
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
    }

    .bk-group-table {
        margin: 0px 0px 10px;
        border: 1px solid #DCDEE5;
        padding: 12px 0px 20px;
        width: fit-content;
        position: relative;
        @include clearfix;

        &:hover {
            .bk-delete-group {
                display: block;
            }
        }

        .bk-group-select {
            float: left;
            width: 300px;
            padding-right: 10px;

            .bk-form {
                padding: 0;
            }
        }

        .bk-group-time {
            float: left;
            @include clearfix;

            li {
                float: left;
                padding-right: 10px;
            }

            .bk-form {
                padding: 0 10px 0 0;
            }
        }
        .bk-delete-group {
            position: absolute;
            top: 10px;
            right: 10px;
            text-align: center;
            cursor: pointer;
            font-weight: 700;
            color: #979ba5;
            border-radius: 50%;
            font-size: 18px;
            display: none;
        }
    }

    .bk-sla-time {
        position: relative;
    }

    .bk-group-icon {
        position: absolute;
        top: 0;
        right: -32px;
        width: 20px;
        height: 20px;
        line-height: 36px;
        font-size: 18px;

        .bk-itsm-icon {
            color: #c0c4cc;
            cursor: pointer;
            font-weight: 700;

            &:hover {
                color: #979BA5;
            }
        }

        .bk-icon-false {
            cursor: no-drop;
            margin-right: 9px;

            &:before {
                color: #F0F1F5;
            }
        }
    }

    .bk-add-group {
        font-size: 14px;
        color: #3A84FF;
        cursor: pointer;
        padding-left: 10px;
        line-height: 20px;
        display: inline-block;

        .bk-icon {
            font-size: 18px;
            float: left;
            margin-right: 5px;
        }
    }

    .bk-model-btn {
        padding: 0 10px 10px;
    }

    .bk-form-border {
        border: 1px solid red;
    }

    .bk-border-error {
        border-color: #ff5656;
    }

</style>
