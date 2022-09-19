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
  <div class="bk-correlationsla-info" v-bkloading="{ isLoading: loading }">
    <div
      class="bk-correlationsla-li"
      v-for="(sla, index) in slaList"
      :key="index"
    >
      <div class="bk-corr-sla-name">
        <span
          v-if="sla.task_status === 2 && sla.sla_status === 4"
          class="bk-corr-sla-status"
          :style="
            'color: ' +
              taskStatusColor[5].textColor +
              '; background-color: ' +
              taskStatusColor[5].backgroundColor
          "
        >
          {{ taskStatusList[5] }}
        </span>
        <span
          v-else
          class="bk-corr-sla-status"
          :style="
            'color: ' +
              taskStatusColor[sla.task_status].textColor +
              '; background-color: ' +
              taskStatusColor[sla.task_status].backgroundColor
          "
        >
          {{ taskStatusList[sla.task_status] }}
        </span>
        : {{ sla.name }}
      </div>
      <div class="bk-time-box">
        <i class="bk-itsm-icon icon-itsm-icon-two-five"></i>&nbsp;
        <span
          v-bk-tooltips.top="{
            content: '首次响应时间' + sla.begin_at
          }"
          class="underline time-type"
        >{{ $t('m["响应"]')
        }}{{
          sla.isResponseTimeout
            ? $t('m["已超时"]')
            : $t('m["倒计时"]')
        }}</span
        >
        <span
          :class="[
            'time',
            sla.isResponseNormal
              ? ''
              : sla.isResponseTimeout
                ? 'timeout'
                : 'warn'
          ]"
        >{{ sla.sla_responseTime[3] }}</span
        >&nbsp;:
        <span
          :class="[
            'time',
            sla.isResponseNormal
              ? ''
              : sla.isResponseTimeout
                ? 'timeout'
                : 'warn'
          ]"
        >{{ sla.sla_responseTime[4] }}</span
        >&nbsp;:
        <span
          :class="[
            'time',
            sla.isResponseNormal
              ? ''
              : sla.isResponseTimeout
                ? 'timeout'
                : 'warn'
          ]"
        >{{ sla.sla_responseTime[5] }}</span
        >
        <i
          v-if="!sla.isResponseNormal"
          :class="[
            'status-icon',
            'bk-itsm-icon',
            sla.isResponseTimeout
              ? 'icon-itsm-icon-square-one'
              : 'icon-chaoshigaojing'
          ]"
        ></i>
      </div>
      <div class="bk-time-box">
        <i class="bk-itsm-icon icon-itsm-icon-two-five"></i>&nbsp;
        <span
          v-bk-tooltips.top="{
            content:
              '首次处理时间' +
              (sla.replied_at || '00-00-00 00:00:00')
          }"
          class="underline time-type"
        >{{ $t('m["处理"]')
        }}{{
          sla.isProcessTimeout
            ? $t('m["已超时"]')
            : $t('m["倒计时"]')
        }}</span
        >
        <span
          :class="[
            'time',
            sla.isProcessNormal
              ? ''
              : sla.isProcessTimeout
                ? 'timeout'
                : 'warn'
          ]"
        >{{ sla.sla_processTime[3] }}</span
        >&nbsp;:
        <span
          :class="[
            'time',
            sla.isProcessNormal
              ? ''
              : sla.isProcessTimeout
                ? 'timeout'
                : 'warn'
          ]"
        >{{ sla.sla_processTime[4] }}</span
        >&nbsp;:
        <span
          :class="[
            'time',
            sla.isProcessNormal
              ? ''
              : sla.isProcessTimeout
                ? 'timeout'
                : 'warn'
          ]"
        >{{ sla.sla_processTime[5] }}</span
        >
        <i
          v-if="!sla.isProcessNormal"
          :class="[
            'status-icon',
            'bk-itsm-icon',
            sla.isProcessTimeout
              ? 'icon-itsm-icon-square-one'
              : 'icon-chaoshigaojing'
          ]"
        ></i>
      </div>
    </div>
    <div class="bk-no-content" v-if="slaList.length === 0 && !loading">
      <img src="@/images/box.png" />
      <p>
        {{ $t('m["暂时没有设置SLA"]')
        }}<span @click="goToSla">{{ $t('m["去设置"]') }}</span>
      </p>
    </div>
  </div>
</template>

<script>
  import { convertTimeArrToMS, convertTimeArrToString } from '@/utils/util.js';
  import { errorHandler } from '../../../../utils/errorHandler';

  export default {
    name: 'slaRecord',
    props: {
      basicInfomation: {
        type: Object,
        default() {
          return {};
        },
      },
      threshold: Array,
    },
    data() {
      return {
        convertTimeArrToString,
        loading: false,
        slaList: [],
        runningTime: [],
        curTime: new Date(),
        taskStatusColor: [
          {},
          {
            textColor: '#3A84FF',
            backgroundColor: '#E1ECFF',
          },
          {
            textColor: '#2DCB56',
            backgroundColor: '#DCFFE2',
          },
          {
            textColor: '#63656E',
            backgroundColor: '#DCDEE5',
          },
          {
            textColor: '#63656E',
            backgroundColor: '#DCDEE5',
          },
          {
            textColor: '#EA3536',
            backgroundColor: '#FEDDDC',
          },
        ],
        taskStatusList: [
          '',
          this.$t('m.newCommon["未开启"]'),
          this.$t('m.newCommon["计时中"]'),
          this.$t('m.newCommon["暂停中"]'),
          this.$t('m.newCommon["已结束"]'),
          this.$t('m.newCommon["已超时"]'),
        ],
        responseCost: '',
        processCost: '',
      };
    },
    watch: {},
    mounted() {
      this.getReceiptsSlaTask();
    },
    methods: {
      getReceiptsSlaTask() {
        if (
          Object.prototype.hasOwnProperty.call(this.basicInfomation, 'id')
        ) {
          this.loading = true;
          const params = {
            id: this.basicInfomation.id,
          };
          this.$store
            .dispatch('change/getReceiptsSlaTask', params)
            .then((res) => {
              this.slaList = res.data;
              this.slaList.forEach((item) => {
                this.$set(
                  item,
                  'sla_responseTime',
                  [0, 0, 0, 0, 0, 0]
                );
                this.$set(
                  item,
                  'sla_processTime',
                  [0, 0, 0, 0, 0, 0]
                );
              });
            })
            .catch((res) => {
              errorHandler(res, this);
            })
            .finally(() => {
              this.loading = false;
              this.changeTimeoutStatus();
            });
        }
      },
      changeTimeoutStatus() {
        this.slaList.forEach((item, index) => {
          if (item.task_status === 2) {
            // 当前时间
            const curTime = convertTimeArrToMS(new Date()
              .toLocaleDateString()
              .split('/')
              .concat(new Date()
                .toTimeString()
                .split(' ')[0]
                .split(':')));
            // 响应倒计时
            const Rtime = convertTimeArrToMS(item.reply_deadline
              .split(' ')[0]
              .split('-')
              .concat(item.reply_deadline.split(' ')[1].split(':')));
            // 处理倒计时
            const Ptime = convertTimeArrToMS(item.deadline
              .split(' ')[0]
              .split('-')
              .concat(item.deadline.split(' ')[1].split(':')));
            const responseCost = Rtime - curTime;
            const processCost = Ptime - curTime;
            this.runTime(responseCost, processCost, index, item.name);
          }
          item.reply_cost = convertTimeArrToString(item.reply_cost);
        });
      },
      /* eslint-disable */
        changeTime(currentSec) {
            const absCurrentSec = Math.abs(currentSec);
            const day = absCurrentSec / (24 * 60 * 60);
            const hour = (absCurrentSec % (24 * 60 * 60)) / (60 * 60);
            const minute = ((absCurrentSec % (24 * 60 * 60)) % (60 * 60)) / 60;
            const sec = ((absCurrentSec % (24 * 60 * 60)) % (60 * 60)) % 60;
            return { day, hour, minute, sec };
        },
        /* eslint-disable */
        goToSla() {
            this.$router.push({
                name: "projectServiceSla",
                params: {
                    id: this.basicInfomation.service_id,
                },
                query: {
                    project_id: this.$route.query.project_id,
                },
            });
        },
        /* eslint-disable */
        runTime(responseCost, processCost, index, name) {
            let isResponseTimeout = false;
            let isProcessTimeout = false;
            let isResponseNormal = true;
            let isProcessNormal = true;
            // sla的超时预警的阈值
            const threshold = this.threshold.find((item) => item.sla_name === name);
            const curResponseCost = JSON.parse(JSON.stringify(responseCost)); // 当前响应时间
            const curProcessCost = JSON.parse(JSON.stringify(processCost)); // 当前处理时间
            // 启动计时器
            this.myInterval(() => {
                responseCost--;
                processCost--;
                if (
                    responseCost <
                        curResponseCost -
                            threshold.rTimeOutThreshold * curResponseCost ||
                    responseCost < 0
                ) {
                    isResponseTimeout = true;
                    isResponseNormal = false;
                } else if (
                    responseCost <
                    threshold.rWarningThreshold * curResponseCost
                ) {
                    isResponseNormal = false;
                }
                if (
                    processCost <
                        curProcessCost -
                            threshold.pTimeOutThreshold * curProcessCost ||
                    processCost < 0
                ) {
                    isProcessTimeout = true;
                    isProcessNormal = false;
                } else if (
                    processCost <
                    threshold.pWarningThreshold * curProcessCost
                ) {
                    // 预警time
                    isProcessNormal = false;
                }
                const responseTime = [0, 0]; // 响应时间
                const processTime = [0, 0]; // 处理时间
                const rTime = this.changeTime(responseCost);
                const pTime = this.changeTime(processCost);
                responseTime.push(
                    parseInt(rTime.day),
                    parseInt(rTime.hour),
                    parseInt(rTime.minute),
                    rTime.sec
                );
                processTime.push(
                    parseInt(pTime.day),
                    parseInt(pTime.hour),
                    parseInt(pTime.minute),
                    pTime.sec
                );
                this.slaList[index].sla_responseTime = responseTime;
                this.slaList[index].sla_processTime = processTime;
                this.slaList[index].isResponseTimeout = isResponseTimeout;
                this.slaList[index].isProcessTimeout = isProcessTimeout;
                this.slaList[index].isResponseNormal = isResponseNormal;
                this.slaList[index].isProcessNormal = isProcessNormal;
                this.$set(this.slaList, index, this.slaList[index]);
            }, 1000);
        },
        /* eslint-disable */
        myInterval(fn, time) {
            if (this.isDestroyed === true) return false;
            const outTimeKey = setTimeout(() => {
                fn();
                clearTimeout(outTimeKey);
                this.myInterval(fn, time);
            }, time);
        },
        getCurrentCost(beginTime) {
            const beginTimestamp = new Date(beginTime);
            const nowTimestamp = new Date();
            return Math.round((nowTimestamp - beginTimestamp) / 1000);
        },
    },
};
</script>

<style scoped lang="scss">
.bk-correlationsla-info {
    min-height: 118px;
    padding: 10px 28px;
    .bk-correlationsla-li {
        height: 134px;
        width: 270px;
        float: left;
        line-height: 30px;
        .bk-corr-sla-name {
            font-size: 14px;
        }
        .bk-time-box {
            height: 40px;
            .time {
                text-align: center;
                display: inline-block;
                background-color: #f0f1f5;
                color: #63656e;
                font-size: 16px;
                font-weight: 600;
                line-height: 28px;
                width: 28px;
                height: 30px;
            }
            .warn {
                background-color: #fff1db;
            }
            .timeout {
                background-color: #ffebeb;
            }
            .time-type {
                font-size: 14px;
                color: #767880;
                margin-right: 20px;
            }
        }
    }
    .bk-no-content {
        margin: 0 auto;
        text-align: center;
        p {
            font-size: 12px;
            line-height: 20px;
            color: #63656e;
            span {
                cursor: pointer;
                color: #3a84ff;
            }
        }
    }
}
.icon-itsm-icon-square-one {
    color: red;
}
.icon-chaoshigaojing {
    color: #ff9c01;
}
.underline {
    border-bottom: 1px dashed #979ba5;
}
.status-icon {
    margin-left: 4px;
}
</style>
