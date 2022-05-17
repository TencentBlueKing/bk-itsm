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
  <div class="thirdStep">
    <div class="bk-itsm-version" style="margin: 0 0 10px 0;" v-if="versionStatus">
      <i class="bk-icon icon-info-circle"></i>
      <span>{{$t(`m.slaContent['服务时长 = 单据更改为“结束计时状态”的时间 - 不计时的状态停留时长']`)}}</span>
      <i class="bk-icon icon-close" @click="closeVersion"></i>
    </div>
    <bk-form
      :label-width="350"
      form-type="vertical"
      :model="formDataInfo.endStatus"
      ref="timeRules">
      <bk-form-item class="bk-time-width"
        :label="$t(`m.slaContent['结束计时的单据状态']`)">
        <bk-select
          v-model="formDataInfo.endStatus.info"
          :clearable="false"
          multiple
          searchable
          :font-size="'medium'"
          @selected="endSelectFn">
          <bk-option v-for="option in endCheckboxList"
            :key="option.id"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
        <i class="bk-itsm-icon ml5 icon-icon-info icon-cus" v-bk-tooltips="$t(`m.slaContent['说明： 单据结束状态默认为SLA停止计时的状态：']`) + endTips"></i>
      </bk-form-item>
      <bk-form-item class="bk-time-width mt20"
        :label="$t(`m.slaContent['流转过程中不计入时长统计的单据状态']`)">
        <bk-select
          v-model="formDataInfo.ignoreStatus.info"
          :clearable="false"
          multiple
          searchable
          :font-size="'medium'"
          @selected="ignoreSelectFn">
          <bk-option v-for="option in ignoreCheckboxList"
            :key="option.id"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
      </bk-form-item>
    </bk-form>
    <div class="mt20">
      <bk-button theme="default"
        :title="$t(`m.slaContent['上一步']`)"
        class="mr10"
        :disabled="secondClick"
        @click="previousStep">
        {{$t(`m.slaContent['上一步']`)}}
      </bk-button>
      <bk-button theme="primary"
        :title="$t(`m.slaContent['提交']`)"
        :loading="secondClick"
        @click="submit">
        {{$t(`m.slaContent['提交']`)}}
      </bk-button>
    </div>
  </div>
</template>

<script>
  import { errorHandler } from '../../../utils/errorHandler';
  export default {
    name: 'thirdStep',
    props: {
      statusType: {
        type: String,
        default: '',
      },
    },
    data() {
      return {
        versionStatus: true,
        secondClick: false,
        formDataInfo: {
          endStatus: {
            info: [],
            endId: '',
          },
          ignoreStatus: {
            info: [],
            ignoreId: '',
          },
        },
        statusList: [],
        threeCheckboxList: [],
        endCheckboxList: [],
        ignoreCheckboxList: [],
        tempEnd: [],
        tempIgnore: [],
        isOverNameList: [],
        endTips: '',
        ignoreTips: '',
        statusLoading: false,
      };
    },
    async mounted() {
      await this.getTypeStatus();
      await this.getInfo();
    },
    methods: {
      endSelectFn(value) {
        this.ignoreCheckboxList = JSON.parse(JSON.stringify(this.threeCheckboxList));
        const itemList = this.endCheckboxList.filter(item => value.indexOf(item.id) !== -1);
        itemList.forEach((item) => {
          this.spliceOne(item, this.ignoreCheckboxList);
        });
        this.tempEnd = JSON.parse(JSON.stringify(itemList));
      },
      ignoreSelectFn(value) {
        this.endCheckboxList = JSON.parse(JSON.stringify(this.threeCheckboxList));
        const itemList = this.ignoreCheckboxList.filter(item => value.indexOf(item.id) !== -1);
        itemList.forEach((item) => {
          this.spliceOne(item, this.endCheckboxList);
        });
        this.tempIgnore = JSON.parse(JSON.stringify(itemList));
      },
      spliceOne(item, list) {
        const temp = list.findIndex(ite => ite.key === item.key);
        list.splice(temp, 1);
      },
      addOne(item, list) {
        list.unshift(item);
      },
      async getInfo() {
        this.statusLoading = true;
        await this.$store.dispatch('ticketStatus/getSubmitFlow', this.statusType).then((res) => {
          const tempList = res.data;
          tempList.forEach((item) => {
            if (item.condition_type === 'STOP') {
              item.condition.expressions.forEach((it) => {
                const temp = this.threeCheckboxList.filter(ite => ite.key === it.value)[0];
                if (temp && temp.id) {
                  this.formDataInfo.endStatus.info.push(temp.id);
                  this.spliceOne(temp, this.ignoreCheckboxList);
                  this.tempEnd.push(temp);
                }
              });
              if (item.id) {
                this.formDataInfo.endStatus.endId = item.id;
              }
            }
            if (item.condition_type === 'PAUSE') {
              item.condition.expressions.forEach((it) => {
                const temp = this.threeCheckboxList.filter(ite => ite.key === it.value)[0];
                if (temp && temp.id) {
                  this.formDataInfo.ignoreStatus.info.push(temp.id);
                  this.spliceOne(temp, this.endCheckboxList);
                  this.tempIgnore.push(temp);
                }
              });
              if (item.id) {
                this.formDataInfo.ignoreStatus.ignoreId = item.id;
              }
            }
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.statusLoading = false;
          });
      },
      async getTypeStatus() {
        this.isDataLoading = true;
        const params = {};
        await this.$store.dispatch('ticketStatus/getTypeStatus', {
          type: this.statusType,
          params,
        }).then((res) => {
          this.statusList = res.data;
          this.statusList.forEach((item) => {
            if (item.is_over) {
              this.isOverNameList.push(item.name);
            } else {
              this.threeCheckboxList.push(item);
            }
          });
          this.endCheckboxList = JSON.parse(JSON.stringify(this.threeCheckboxList));
          this.ignoreCheckboxList = JSON.parse(JSON.stringify(this.threeCheckboxList));
          this.endTips = this.isOverNameList.join('/');
          this.ignoreTips = this.$t('m.slaContent[\'说明： 挂起状态默认为SLA不计入统计时长的状态\']');
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
      },
      previousStep() {
        this.$parent.changeTree(2, 'back');
      },
      submit() {
        this.ajaxSubmit();
      },
      ajaxSubmit() {
        const params = {
          name: '启动',
          service_type: this.statusType,
          batch_create: true,
          rules: [],
        };
        for (let i = 0; i < 2; i++) {
          params.rules.push({
            condition_type: 'STOP',
            condition: {
              type: 'any',
              expressions: [],
            },
          });
        }
        params.rules[1].condition_type = 'PAUSE';
        this.threeCheckboxList.forEach((item) => {
          this.formDataInfo.endStatus.info.forEach((ite) => {
            if (item.id === ite * 1) {
              const temp = {
                name: 'current_status',
                value: item.key,
                operator: 'equal_to',
              };
              params.rules[0].condition.expressions.push(temp);
            }
          });
          if (this.formDataInfo.endStatus.endId) {
            params.rules[0].id = this.formDataInfo.endStatus.endId * 1;
          }
          this.formDataInfo.ignoreStatus.info.forEach((ite) => {
            if (item.id === ite * 1) {
              const temp = {
                name: 'current_status',
                value: item.key,
                operator: 'equal_to',
              };
              params.rules[1].condition.expressions.push(temp);
            }
          });
          if (this.formDataInfo.ignoreStatus.ignoreId) {
            params.rules[1].id = this.formDataInfo.ignoreStatus.ignoreId * 1;
          }
        });
        if (this.secondClick) {
          return;
        }
        this.secondClick = true;
        this.$store.dispatch('ticketStatus/endSubmitFlow', params).then(() => {
          this.$bkMessage({
            message: '保存成功',
            theme: 'success',
          });
          this.$parent.backTab();
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.secondClick = false;
          });
      },
      closeVersion() {
        this.versionStatus = false;
      },
    },
  };
</script>

<style scoped lang="scss">
    .icon-cus{
        position: absolute;
        right: -28px;
        top: 6px;
        font-size: 18px;
    }
    .bk-time-width {
        max-width: 400px
    }
</style>
