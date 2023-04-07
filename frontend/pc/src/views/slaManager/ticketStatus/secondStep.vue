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
  <div class="secondStep">
    <div class="bk-itsm-version" style="margin: 0 0 10px 0;" v-if="versionStatus">
      <i class="bk-icon icon-info-circle"></i>
      <span>{{$t(`m.slaContent['流转设定，是设置工作状态间的先后流转关系。如果需要设置该流转，请在两个状态间的复选框内打勾。结束状态（如已完成，被终止，被撤销）无法逆向流转。']`)}}</span>
      <i class="bk-icon icon-close" @click="closeVersion"></i>
    </div>
    <bk-table
      :data="dataList"
      :size="'small'"
      v-bkloading="{ isLoading: isDataLoading }">
      <bk-table-column :render-header="$renderHeader" :label="$t(`m.slaContent['状态名']`)" :min-width="150" :show-overflow-tooltip="true">
        <template slot-scope="props">
          <span :title="nameFilter(props.row.name)">{{ nameFilter(props.row.name) }}</span>
        </template>
      </bk-table-column>
      <template v-for="item in statusOwnList">
        <bk-table-column :render-header="$renderHeader" :label="localeCookie ? item.name : item.flow_status" :key="item.id" :show-overflow-tooltip="true">
          <template slot-scope="props">
            <template v-if="props.row.checkBoxStatus">
              <bk-checkbox class="bk-outline-none"
                v-model="props.row.checkBoxStatus[item.key]"
                :true-value="trueStatus"
                :false-value="falseStatus"
                @change="selectFlowTo(props.row, item)">
              </bk-checkbox>
            </template>
          </template>
        </bk-table-column>
      </template>
      <bk-table-column :label="$t(`m.slaContent['开启自动流转']`)">
        <template slot-scope="props">
          <bk-checkbox class="bk-outline-none"
            v-model="props.row.is_auto"
            :true-value="trueStatus"
            :false-value="falseStatus">
          </bk-checkbox>
          <div class="bk-outline-mont" @click="isAutoChange(props.row)"></div>
          <i v-if="props.row.is_auto"
            class="bk-itsm-icon icon-edit-new flow-icon"
            @click.stop="editRule(props.row)">
          </i>
        </template>
      </bk-table-column>
      <div class="empty" slot="empty">
        <empty :is-error="listError" @onRefresh="getTypeStatus()"> </empty>
      </div>
    </bk-table>
    <div class="mt20">
      <bk-button theme="default"
        class="mr10"
        :title="$t(`m.slaContent['上一步']`)"
        :disabled="secondClick"
        @click="previousStep">
        {{ $t('m.slaContent["上一步"]') }}
      </bk-button>
      <bk-button theme="default"
        class="mr10"
        :title="$t(`m.deployPage['取消']`)"
        :disabled="secondClick"
        @click="backButton">
        {{ $t('m.deployPage["取消"]') }}
      </bk-button>
      <bk-button theme="primary"
        :title="$t(`m.slaContent['提交']`)"
        :loading="secondClick"
        @click="ajaxSubmit">
        {{$t(`m.slaContent['提交']`)}}
      </bk-button>
    </div>
    <bk-dialog
      v-model="autoConfigDialog.isShow"
      :render-directive="'if'"
      :width="autoConfigDialog.width"
      :header-position="autoConfigDialog.headerPosition"
      :auto-close="autoConfigDialog.autoClose"
      :mask-close="autoConfigDialog.autoClose"
      @confirm="confirmFn"
      @cancel="cancelFn">
      <p slot="header">
        {{ $t(`m.slaContent['自动流转设置']`) }}
      </p>
      <div class="bk-auto-conten">
        <bk-form
          :label-width="200"
          form-type="vertical"
          :model="isAutoTemp.info"
          :rules="rules"
          ref="autoForm">
          <p class="bk-auto-p">
            {{$t(`m.slaContent['单据在']`)}}【{{isAutoTemp.item.name}}】{{$t(`m.slaContent['停留时间超过']`)}}
          </p>
          <bk-form-item class="bk-auto-time"
            :property="'threshold'"
            :icon-offset="75">
            <bk-input v-model="isAutoTemp.info.threshold"
              :font-size="'normal'"
              :type="'number'"
              :min="0">
              <bk-dropdown-menu class="group-text"
                @show="dropdownShow"
                @hide="dropdownHide"
                slot="append"
                :font-size="'normal'"
                ref="dropdown">
                <bk-button type="primary" slot="dropdown-trigger">
                  <span v-for="(time, timeIndex) in timeList" :key="timeIndex">
                    <template v-if="isAutoTemp.info.timeSpace === time.id">{{ time.name }}</template>
                  </span>
                  <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShow }]"></i>
                </bk-button>
                <ul class="bk-dropdown-list" slot="dropdown-content">
                  <li v-for="(time, timeIndex) in timeList" :key="timeIndex">
                    <a href="javascript:;" @click="timeHandler(time)">{{ time.name }}</a>
                  </li>
                </ul>
              </bk-dropdown-menu>
            </bk-input>
          </bk-form-item>
          <p class="bk-auto-p">{{$t(`m.slaContent['时，将自动流转至']`)}}</p>
          <bk-form-item style="width: 100px;"
            class="bk-auto-select"
            :property="'id'">
            <bk-select v-model="isAutoTemp.info.id"
              searchable
              :font-size="'medium'"
              :clearable="falseStatus">
              <bk-option v-for="option in flowList"
                :key="option.id"
                :id="option.id"
                :name="option.name">
              </bk-option>
            </bk-select>
          </bk-form-item>
        </bk-form>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
  import { errorHandler } from '../../../utils/errorHandler.js';
  import commonMix from '../../commonMix/common.js';
  import cookie from 'cookie';
  export default {
    name: 'secondStep',
    mixins: [commonMix],
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
        isDataLoading: false,
        trueStatus: true,
        falseStatus: false,
        autoConfigDialog: {
          isShow: false,
          hasHeader: true,
          width: 700,
          headerPosition: 'left',
          autoClose: false,
        },
        timeList: [
          { id: 'm', name: this.$t('m.slaContent[\'分钟\']') },
          { id: 'h', name: this.$t('m.slaContent[\'小时\']') },
          { id: 'd', name: this.$t('m.slaContent[\'天\']') },
        ],
        isAutoTemp: {
          item: {},
          info: {
            threshold: null,
            id: '',
            timeSpace: 'd',
          },
        },
        statusOwnList: [],
        dataList: [],
        flowList: [],
        isDropdownShow: false,
        rules: {},
        localeCookie: false,
        listError: false,
      };
    },
    async mounted() {
      this.localeCookie = cookie.parse(document.cookie).blueking_language === 'zh-cn';
      // 列表数据添加流转信息
      await this.getTypeStatus();
      await this.listAddFlow();
      // 将数据转换
      this.dataList = this.dataList.filter(item => !item.is_over);
      this.dataList.forEach(item => {
        this.$set(item, 'checkBoxStatus', {});
        this.statusOwnList.forEach(statusItem => {
          item.checkBoxStatus[statusItem.key] = item.can_flow_to.indexOf(statusItem.id) !== -1;
        });
      });
      this.rules.threshold = this.checkCommonRules('select').select;
      this.rules.id = this.checkCommonRules('select').select;
    },
    methods: {
      // 返回
      backButton() {
        this.$parent.backTab();
      },
      async ajaxSubmit() {
        await this.saveTypeFlow();
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
          .catch(res => {
            this.$bkMessage({
              message: res.data.msg,
              theme: 'error',
            });
          })
          .finally(() => {
            this.secondClick = false;
          });
      },
      nameFilter(val) {
        return `${this.$t('m.slaContent[\'从\']')}【${val}】${this.$t('m.slaContent[\'可以流转至\']')}`;
      },
      async getTypeStatus() {
        this.isDataLoading = true;
        this.listError = false;
        const params = {
          // flow_status: 'RUNNING'
        };
        await this.$store.dispatch('ticketStatus/getTypeStatus', {
          type: this.statusType,
          params,
        }).then((res) => {
          this.statusOwnList = res.data;
          this.dataList = res.data;
        })
          .catch(res => {
            this.listError = true;
            errorHandler(res, this);
          })
          .finally(() => {
          });
      },
      initIsAutoTemp() {
        this.isAutoTemp.info.threshold = null;
        this.isAutoTemp.info.id = '';
        this.isAutoTemp.info.timeSpace = 'd';
      },
      // 列表数据添加流转信息
      async listAddFlow() {
        this.isDataLoading = true;
        this.dataList.forEach(item => {
          this.$set(item, 'can_flow_to', []);
          this.$set(item, 'is_auto', false);
        });
        await this.$store.dispatch('ticketStatus/getTypeFlow', this.statusType).then((res) => {
          const flowList = res.data;
          flowList.forEach(item => {
            for (let i = 0; i < this.dataList.length; i++) {
              if (this.dataList[i].id === item.from_status) {
                this.dataList[i].can_flow_to.push(item.to_status);
                return;
              }
            }
          });
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
          });
        await this.$store.dispatch('ticketStatus/getTypeAutoFlow', this.statusType).then((res) => {
          const autoList = res.data;
          for (const key in autoList) {
            for (let i = 0; i < this.dataList.length; i++) {
              if (this.dataList[i].id === Number(key)) {
                this.dataList[i].is_auto = autoList[key];
              }
            }
          }
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
      },
      selectFlowTo(itemRow, itemCol) {
        const flag = itemRow.can_flow_to.indexOf(itemCol.id);
        if (flag !== -1) {
          itemRow.can_flow_to.splice(flag, 1);
        } else {
          itemRow.can_flow_to.push(itemCol.id);
        }
      },
      previousStep() {
        this.$parent.changeTree(1, 'back');
      },
      async stepNext() {
        await this.saveTypeFlow();
        this.$parent.changeTree(1, 'next');
      },
      // 保存指定服务类型下的工单自动流转状态
      async saveTypeFlow() {
        const transits = [];
        const type = this.statusType;
        this.dataList.forEach(item => {
          item.can_flow_to.forEach(ite => {
            const tempTransits = {
              from_status: item.id,
              to_status: ite,
            };
            transits.push(tempTransits);
          });
        });
        const params = {
          service_type: type,
          transits,
        };
        await this.$store.dispatch('ticketStatus/saveTypeFlow', params).then(() => {
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
          });
      },
      // 自动流传设置点击事件
      isAutoChange(itemRow) {
        this.saveTypeFlow();
        if (itemRow.is_auto) {
          // 取消自动流转弹窗
          this.$bkInfo({
            type: 'warning',
            title: this.$t('m.slaContent["确认取消？"]'),
            subTitle: this.$t('m.slaContent["确认后，将取消自动流转！"]'),
            confirmFn: () => {
              const id = itemRow.id;
              if (this.secondClick) {
                return;
              }
              this.secondClick = true;
              this.$store.dispatch('ticketStatus/closeAutoFlow', id).then(() => {
                this.$bkMessage({
                  message: this.$t('m.manageCommon["取消成功"]'),
                  theme: 'success',
                });
                this.listAddFlow();
              })
                .catch((res) => {
                  errorHandler(res, this);
                })
                .finally(() => {
                  this.secondClick = false;
                });
            },
          });
        } else {
          // 编辑自动流转弹窗
          this.getFlowList(itemRow);
          this.isAutoTemp.item = itemRow;
          this.autoConfigDialog.isShow = true;
        }
      },
      async editRule(itemRow) {
        this.saveTypeFlow();
        this.getFlowList(itemRow);
        const id = itemRow.id;
        await this.$store.dispatch('ticketStatus/getOneAutoFlow', id).then((res) => {
          this.isAutoTemp.item = itemRow;
          this.isAutoTemp.info.threshold = res.data.threshold;
          this.isAutoTemp.info.timeSpace = res.data.threshold_unit;
          this.isAutoTemp.info.id = res.data.to_status;
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
          });
        this.isAutoTemp.item = itemRow;
        this.autoConfigDialog.isShow = true;
      },
      getFlowList(itemRow) {
        this.flowList = [];
        itemRow.can_flow_to.forEach(item => {
          const temp = {
            name: '',
            id: item,
          };
          for (let i = 0; i < this.statusOwnList.length; i++) {
            if (this.statusOwnList[i].id === item) {
              temp.name = this.statusOwnList[i].name;
            }
          }
          this.flowList.push(temp);
        });
      },
      // 流转设定弹窗
      confirmFn() {
        this.$refs.autoForm.validate().then(() => {
          this.ajaxConfirmFn();
        }, validator => {
          console.warn(validator);
        });
      },
      ajaxConfirmFn() {
        const params = {
          to_status: this.isAutoTemp.info.id,
          threshold: this.isAutoTemp.info.threshold,
          threshold_unit: this.isAutoTemp.info.timeSpace,
        };
        const id = this.isAutoTemp.item.id;
        this.$store.dispatch('ticketStatus/setAutoFlow', { params, id }).then(() => {
          this.$bkMessage({
            message: '操作成功',
            theme: 'success',
          });
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.autoConfigDialog.isShow = false;
            this.isAutoTemp.item.is_auto = true;
            this.listAddFlow();
            this.initIsAutoTemp();
          });
      },
      cancelFn() {
        this.autoConfigDialog.isShow = false;
        this.initIsAutoTemp();
      },
      closeVersion() {
        this.versionStatus = false;
      },
      dropdownShow() {
        this.isDropdownShow = true;
      },
      dropdownHide() {
        this.isDropdownShow = false;
      },
      timeHandler(time) {
        this.$refs.dropdown.hide();
        this.isAutoTemp.info.timeSpace = time.id;
      },
    },
  };
</script>

<style scoped lang="scss">
    .bk-outline-mont {
        position: absolute;
        top: 12px;
        left: 14px;
        width: 18px;
        height: 18px;
        opacity: 0;
        z-index: 5;
        cursor: pointer;
    }
    .flow-icon {
        left: 35px;
        position: absolute;
        font-size: 28px;
        top: 7px;
        cursor: pointer;
    }
    .icon-edit-new:before {
        color: #3A84FF;
    }
    .bk-auto-conten {
        height: 150px;
        padding-top: 60px;
        .bk-auto-p {
            float: left;
            margin-right: 10px;
            line-height: 32px;
        }
        .bk-auto-time {
            float: left;
            width: 200px;
            margin-right: 10px;
        }
        .bk-auto-select {
            width: 200px;
            float: left;
        }
    }
</style>
