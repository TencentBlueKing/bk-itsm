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
        <template v-if="slaList.length">
            <div>
                <i class="bk-itsm-icon icon-itsm-icon-two-five"></i>&nbsp;
                <span v-bk-tooltips.top="{ content: '首次响应时间' + slaList[0].begin_at }" class="underline time-type">{{ $t('m["响应"]') }}{{ isResponseTimeout ? $t('m["已超时"]') : $t('m["倒计时"]')}}</span>
                <span :class="['time', isResponseNormal ? '' : isResponseTimeout ? 'timeout' : 'warn']">{{responseTime[3]}}</span>&nbsp;:&nbsp;
                <span :class="['time', isResponseNormal ? '' : isResponseTimeout ? 'timeout' : 'warn']">{{responseTime[4]}}</span>&nbsp;:&nbsp;
                <span :class="['time', isResponseNormal ? '' : isResponseTimeout ? 'timeout' : 'warn']">{{responseTime[5]}}</span>
                <i v-if="!isResponseNormal" :class="['bk-itsm-icon', isResponseTimeout ? 'icon-itsm-icon-mark-eight' : 'icon-itsm-icon-three-eight']"></i>
            </div>
            <div>
                <i class="bk-itsm-icon icon-itsm-icon-two-five"></i>&nbsp;
                <span v-bk-tooltips.top="{ content: '首次处理时间' + slaList[0].replied_at }" class="underline time-type">{{ $t('m["处理"]') }}{{ isProcessTimeout ? $t('m["已超时"]') : $t('m["倒计时"]')}}</span>
                <span :class="['time', isProcessNormal ? '' : isProcessTimeout ? 'timeout' : 'warn']">{{processingTime[3]}}</span>&nbsp;:&nbsp;
                <span :class="['time', isProcessNormal ? '' : isProcessTimeout ? 'timeout' : 'warn']">{{processingTime[4]}}</span>&nbsp;:&nbsp;
                <span :class="['time', isProcessNormal ? '' : isProcessTimeout ? 'timeout' : 'warn']">{{processingTime[5]}}</span>
                <i v-if="!isProcessNormal" :class="['bk-itsm-icon', isProcessTimeout ? 'icon-itsm-icon-mark-eight' : 'icon-itsm-icon-three-eight']"></i>
            </div>
        </template>
        <!-- <div class="bk-correlationsla-li" v-for="(sla, index) in slaList" :key="index">
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
                <span v-else-if="sla.task_status === 2" :style="{ 'color': (sla.sla_status === 4 ? '#EA3536' : '#3A84FF') }">{{convertTimeArrToString(sla.sla_timecost)}}</span>
                <span v-else-if="sla.task_status === 3" :style="{ 'color': (sla.sla_status === 4 ? '#EA3536' : '#FE9C00') }">{{convertTimeArrToString(sla.resovle_cost) || $t('m.newCommon["已暂停"]')}}</span>
                <span v-else :style="{ 'color': (sla.sla_status === 4 ? '#EA3536' : '#63656E') }">{{convertTimeArrToString(sla.resovle_cost)}}</span>
            </div>
        </div> -->
        <div class="bk-no-content" v-else>
            <img src="@/images/box.png">
            <p>{{ $t('m["暂时没有设置SLA"]') }}<span @click="goToSla">{{ $t('m["去设置"]') }}</span></p>
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
                isResponseTimeout: false,
                isProcessTimeout: false,
                isResponseNormal: true,
                isProcessNormal: true,
                rWarningThreshold: '', // 响应预警阈值
                rTimeOutThreshold: '', // 响应超时阈值
                pWarningThreshold: '', // 处理预警阈值
                pTimeOutThreshold: '', // 处理超时阈值
                convertTimeArrToString,
                loading: false,
                slaList: [],
                runningTime: [],
                curTime: new Date(),
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
                responseTime: [0, 0, 0, 0, 0, 0], // 响应倒计时
                processingTime: [0, 0, 0, 0, 0, 0], // 处理倒计时
                taskStatusList: ['', this.$t('m.newCommon["未开启"]'), this.$t('m.newCommon["计时中"]'), this.$t('m.newCommon["暂停中"]'), this.$t('m.newCommon["已结束"]'), this.$t('m.newCommon["已超时"]')],
                responseCost: '',
                processCost: ''
            }
        },
        watch: {
        },
        mounted () {
            this.getReceiptsSlaTask()
        },
        methods: {
            getProtocolsList () {
                const params = {
                    project_id: this.basicInfomation.project_key
                }
                this.$store.dispatch('slaManagement/getProtocolsList', params).then(res => {
                    const curSla = res.data.find(item => item.name === this.basicInfomation.sla[0])
                    console.log(curSla)
                    const condition = curSla.action_policies.map(item => {
                        return item.condition.expressions[0].value
                    })
                    this.rWarningThreshold = condition[0] / 100
                    this.rTimeOutThreshold = condition[1] / 100
                    this.pWarningThreshold = condition[2] / 100
                    this.pTimeOutThreshold = condition[3] / 100
                })
            },
            getReceiptsSlaTask () {
                this.getProtocolsList()
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
                        // 当前时间
                        const curTime = convertTimeArrToMS(new Date().toLocaleDateString().split('/').concat(new Date().toTimeString().split(' ')[0].split(':')))
                        // 响应倒计时
                        const Rtime = convertTimeArrToMS(item.reply_deadline.split(' ')[0].split('-').concat(item.reply_deadline.split(' ')[1].split(':')))
                        // 处理倒计时
                        const Ptime = convertTimeArrToMS(item.deadline.split(' ')[0].split('-').concat(item.deadline.split(' ')[1].split(':')))
                        const responseCost = Rtime - curTime
                        const processCost = Ptime - curTime
                        this.runTime(responseCost, processCost, index)
                    }
                    item.reply_cost = convertTimeArrToString(item.reply_cost)
                })
            },
            changeTime (currentSec) {
                const absCurrentSec = Math.abs(currentSec)
                const day = absCurrentSec / (24 * 60 * 60)
                const hour = (absCurrentSec % (24 * 60 * 60)) / (60 * 60)
                const minute = absCurrentSec % (24 * 60 * 60) % (60 * 60) / 60
                const sec = absCurrentSec % (24 * 60 * 60) % (60 * 60) % 60
                return { day, hour, minute, sec }
            },
            goToSla () {
                this.$router.push({
                    name: 'projectServiceSla',
                    params: {
                        id: this.basicInfomation.service_id
                    },
                    query: {
                        project_id: this.$route.query.project_id
                    }
                })
            },
            // changeTimeFormat () {

            // },
            runTime (responseCost, processCost, index) {
                // 启动计时器
                this.myInterval(() => {
                    responseCost--
                    processCost--
                    if (responseCost < this.responseCost - (this.rTimeOutThreshold * this.responseCost)) {
                        this.isResponseTimeout = true
                        this.isResponseNormal = false
                    } else if (responseCost < this.rWarningThreshold * this.responseCost) {
                        this.isResponseNormal = false
                    }
                    if (processCost < this.processCost - (this.pTimeOutThreshold * this.processCost)) {
                        this.isProcessTimeout = true
                        this.isProcessNormal = false
                    } else if (processCost < this.pWarningThreshold * this.processCost) { // 预警time
                        this.isProcessNormal = false
                    }
                    const responseTime = [0, 0] // 响应时间
                    const processTime = [0, 0] // 处理时间
                    const rTime = this.changeTime(responseCost)
                    const pTime = this.changeTime(processCost)
                    responseTime.push(parseInt(rTime.day), parseInt(rTime.hour), parseInt(rTime.minute), rTime.sec)
                    processTime.push(parseInt(pTime.day), parseInt(pTime.hour), parseInt(pTime.minute), pTime.sec)
                    this.slaList[index].sla_timecost = responseTime
                    this.responseTime = responseTime
                    this.processingTime = processTime
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
        height: 134px;
        display: flex;
        flex-direction: column;
        padding: 26px 28px;
        justify-content: space-between;
        .time {
            text-align: center;
            display: inline-block;
            background-color: #f0f1f5;
            color: #63656E;
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
        .bk-no-content {
            margin: 0 auto;
            text-align: center;
            p {
                font-size: 12px;
                line-height: 20px;
                color: #63656E;
                span {
                    cursor: pointer;
                    color: #3A84FF;
                }
            }
        }
    }
    .icon-itsm-icon-mark-eight {
        color: red;
    }
    .icon-itsm-icon-three-eight {
        color: #ff9c01;
    }
    .underline {
        text-decoration: underline;
    }
</style>
