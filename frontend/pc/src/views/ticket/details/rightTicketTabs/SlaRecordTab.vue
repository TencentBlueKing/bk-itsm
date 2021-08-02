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
        <div class="bk-correlationsla-li" v-for="(sla, index) in slaList" :key="index">
            <div class="bk-corr-sla-name">
                <span
                    v-if="sla.task_status === 2 && sla.sla_status === 4"
                    class="bk-corr-sla-status"
                    :style="'color: ' + taskStatusColor[5].textColor + '; background-color: ' + taskStatusColor[5].backgroundColor">
                    {{taskStatusList[5]}}
                </span>
                <span
                    v-else
                    class="bk-corr-sla-status"
                    :style="'color: ' + taskStatusColor[sla.task_status].textColor + '; background-color: ' + taskStatusColor[sla.task_status].backgroundColor"
                >
                    {{taskStatusList[sla.task_status]}}
                </span>
                {{sla.name}}
            </div>
            <div class="bk-argeement-norm">
                {{ $t('m.newCommon["协议标准"]') }} : {{sla.protocol_name}}
            </div>
            <div class="bk-startend-state">
                {{ $t('m.newCommon["起止节点"]') }} : <span>{{sla.start_node_name}}</span> 至 <span>{{sla.end_node_name}}</span>
            </div>
            <div class="bk-time-box">
                {{ $t('m.newCommon["开始计时时间"]') }} :
                <span v-if="sla.task_status === 1" style="color: #3A84FF">{{$t('m.newCommon["未开启"]')}}</span>
                <span v-else>{{sla.begin_at}}</span>
            </div>
            <div class="bk-time-box">
                {{ $t('m.newCommon["计划完成时间"]') }} :
                <span v-if="sla.task_status === 1" style="color: #3A84FF">{{$t('m.newCommon["未开启"]')}}</span>
                <span v-else>{{sla.deadline}}</span>
            </div>
            <div class="bk-time-box">
                {{ $t('m.newCommon["实际响应时间"]') }} :
                <span v-if="sla.task_status === 1" style="color: #3A84FF">{{$t('m.newCommon["未开启"]')}}</span>
                <span v-else-if="!sla.is_replied" style="color: #3A84FF">{{$t('m.newCommon["未响应"]')}}</span>
                <span v-else-if="sla.sla_status === 2" style="color: #EA3536">{{sla.replied_at || $t('m.newCommon["未响应"]')}}</span>
                <span v-else>{{sla.replied_at}}</span>
            </div>
            <div class="bk-time-box">
                {{ $t('m.newCommon["实际完成时间"]') }} :
                <span v-if="sla.task_status === 1" style="color: #3A84FF">{{$t('m.newCommon["未开启"]')}}</span>
                <span v-else-if="sla.task_status === 2 || sla.task_status === 3" style="color: #3A84FF">{{$t('m.newCommon["未完成"]')}}</span>
                <span v-else-if="sla.sla_status === 4" style="color: #EA3536">{{sla.end_at || $t('m.newCommon["未完成"]')}}</span>
                <span v-else>{{sla.end_at}}</span>
            </div>
            <div class="bk-time-box">
                {{ $t('m.newCommon["实际响应时长"]') }} :
                <span v-if="sla.task_status === 1" style="color: #3A84FF">{{$t('m.newCommon["未开启"]')}}</span>
                <span v-else-if="!sla.is_replied" style="color: #3A84FF">{{$t('m.newCommon["未响应"]')}}</span>
                <span v-else-if="sla.sla_status === 2" style="color: #EA3536">{{sla.reply_cost || $t('m.newCommon["未响应"]')}}</span>
                <span v-else>{{sla.reply_cost}}</span>
            </div>
            <div class="bk-time-box">
                {{ $t('m.newCommon["实际处理时长"]') }} :
                <span v-if="sla.task_status === 1" style="color: #3A84FF">{{$t('m.newCommon["未开启"]')}}</span>
                <!-- 计时中-->
                <span v-else-if="sla.task_status === 2" :style="{ 'color': (sla.sla_status === 4 ? '#EA3536' : '#3A84FF') }">{{convertTimeArrToString(sla.sla_timecost)}}</span>
                <span v-else-if="sla.task_status === 3" :style="{ 'color': (sla.sla_status === 4 ? '#EA3536' : '#FE9C00') }">{{convertTimeArrToString(sla.resovle_cost) || $t('m.newCommon["已暂停"]')}}</span>
                <span v-else :style="{ 'color': (sla.sla_status === 4 ? '#EA3536' : '#63656E') }">{{convertTimeArrToString(sla.resovle_cost)}}</span>
            </div>
        </div>
        <div class="bk-no-content" v-if="!slaList.length">
            <img src="@/images/box.png">
            <p>{{ $t('m.newCommon["未绑定SLA协议"]') }}</p>
        </div>
    </div>
</template>

<script>
    import { convertTimeArrToMS, convertTimeArrToString } from '@/utils/util.js'
    import { errorHandler } from '../../../../utils/errorHandler'
    
    export default {
        name: 'slaRecord',
        components: {
        },
        props: {
            basicInfomation: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        data () {
            return {
                convertTimeArrToString,
                loading: false,
                slaList: [],
                runningTime: [],
                taskStatusColor: [
                    {},
                    {
                        textColor: '#3A84FF',
                        backgroundColor: '#E1ECFF'
                    },
                    {
                        textColor: '#2DCB56',
                        backgroundColor: '#DCFFE2'
                    },
                    {
                        textColor: '#63656E',
                        backgroundColor: '#DCDEE5'
                    },
                    {
                        textColor: '#63656E',
                        backgroundColor: '#DCDEE5'
                    },
                    {
                        textColor: '#EA3536',
                        backgroundColor: '#FEDDDC'
                    }
                ],
                taskStatusList: ['', this.$t('m.newCommon["未开启"]'), this.$t('m.newCommon["计时中"]'), this.$t('m.newCommon["暂停中"]'), this.$t('m.newCommon["已结束"]'), this.$t('m.newCommon["已超时"]')]
            }
        },
        watch: {
        },
        mounted () {
            this.getReceiptsSlaTask()
        },
        methods: {
            getReceiptsSlaTask () {
                this.loading = true
                const params = {
                    id: this.basicInfomation.id
                }
                this.$store.dispatch('change/getReceiptsSlaTask', params).then(res => {
                    this.slaList = res.data
                }).catch(res => {
                    errorHandler(res, this)
                }).finally(() => {
                    this.loading = false
                    this.changeTimeoutStatus()
                })
            },
            changeTimeoutStatus () {
                this.slaList.forEach((item, index) => {
                    if (item.task_status === 2) {
                        const currentCost = convertTimeArrToMS(item.resovle_cost)
                        this.runTime(currentCost, index)
                    }
                    item.reply_cost = convertTimeArrToString(item.reply_cost)
                })
            },
            runTime (currentSec, index) {
                // 启动计时器
                this.myInterval(() => {
                    currentSec++
                    const slaTimecost = [0, 0]
                    const absCurrentSec = Math.abs(currentSec)
                    const day = absCurrentSec / (24 * 60 * 60)
                    const hour = (absCurrentSec % (24 * 60 * 60)) / (60 * 60)
                    const minute = absCurrentSec % (24 * 60 * 60) % (60 * 60) / 60
                    const sec = absCurrentSec % (24 * 60 * 60) % (60 * 60) % 60
                    slaTimecost.push(parseInt(day), parseInt(hour), parseInt(minute), sec)
                    this.slaList[index].sla_timecost = slaTimecost
                    this.$set(this.slaList, index, this.slaList[index])
                }, 1000)
            },
            myInterval (fn, time) {
                if (this._isDestroyed === true) return false
                const outTimeKey = setTimeout(() => {
                    fn()
                    clearTimeout(outTimeKey)
                    this.myInterval(fn, time)
                }, time)
            },
            getCurrentCost (beginTime) {
                const beginTimestamp = new Date(beginTime)
                const nowTimestamp = new Date()
                return Math.round((nowTimestamp - beginTimestamp) / 1000)
            }
        }
    }
</script>

<style scoped lang='scss'>
    .bk-correlationsla-info {
        // padding: 18px 12px;
        color: #63656E;
        .bk-correlationsla-li {
            width: 100%;
            padding: 12px 20px;
            border-radius: 2px;
            border: 1px solid #DCDEE5;
            font-size: 12px;
            margin-bottom: 12px;
            .bk-corr-sla-name {
                font-size: 14px;
                font-weight: 700;
                margin-bottom: 12px;
                .bk-corr-sla-status {
                    display: inline-block;
                    width: 44px;
                    height: 18px;
                    line-height: 18px;
                    font-size: 12px;
                    font-weight: normal;
                    border-radius: 2px;
                    text-align: center;
                }
            }
            .bk-argeement-norm {
                margin-bottom: 12px;
            }
            .bk-startend-state {
                margin-bottom: 12px;
                span {
                    font-weight: 700;
                }
            }
            .bk-time-box {
                display: inline-block;
                width: 250px;
                margin-bottom: 12px;
            }
        }
    }
    .bk-no-content {
        text-align: center;
        padding: 80px 0;

        p {
            font-size: 16px;
            color: #63656E;
            margin-top: 10px;
        }
    }
</style>
