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
    <div class="ticket-detail-panel" v-bkloading="{ isLoading: loading.ticketLoading }">
        <template v-if="!ticketErrorMessage">
            <ticket-header
                v-if="!loading.ticketLoading"
                :header-info="headerInfo"
                :ticket-info="ticketInfo"
                :ticket-trigger-list="ticketTriggerList"
                @reloadTicket="reloadTicket">
            </ticket-header>
            
            <div class="ticket-container">
                <div class="ticket-container-left">
                    <!-- 基础信息/工单预览 -->
                    <left-ticket-content
                        ref="leftTicketContent"
                        :loading="loading"
                        :ticket-info="ticketInfo"
                        :node-list="nodeList"
                        :first-state-fields="firstStateFields"
                        :node-trigger-list="nodeTriggerList"
                        :ticket-id="ticketId">
                    </left-ticket-content>
                </div>
                <!-- 分屏拖拽线 -->
                <div data-test-id="ticket_line_screen_drag" class="drag-line" @mousedown="handleLineMouseDown" v-show="showRightTabs"></div>
                <div class="show-right-icon" @click="onShowRightContent" v-show="!showRightTabs">
                    <i data-v-639c8670="" class="bk-icon icon-angle-left"></i>
                </div>
                <div id="ticketContainerRight" class="ticket-container-right" v-show="showRightTabs">
                    <right-ticket-tabs
                        v-if="!loading.ticketLoading"
                        :ticket-info="ticketInfo"
                        :node-list="nodeList">
                    </right-ticket-tabs>
                </div>
            </div>
        </template>
        <!-- 403 | 404 -->
        <no-ticket-content v-else
            :message="ticketErrorMessage">
        </no-ticket-content>
        <bk-dialog v-model="isShowNoticeDialog"
            theme="primary"
            :mask-close="false"
            header-position="left"
            title="提示"
            @confirm="onNoticeConfirm">
            {{$t(`m.newCommon['您要处理的节点已被']`)}} {{ noticeInfo.processed_user }} {{$t(`m.newCommon['处理完成，可在流转日志中查看详情。']`)}}
        </bk-dialog>
    </div>
</template>

<script>
    import TicketHeader from './TicketHeader.vue'
    import NoTicketContent from './components/NoTicketContent.vue'
    import RightTicketTabs from './rightTicketTabs/RightTicketTabs.vue'
    import commonMix from '@/views/commonMix/common.js'
    import apiFieldsWatch from '@/views/commonMix/api_fields_watch.js'
    import fieldMix from '@/views/commonMix/field.js'
    import { mapState } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import { deepClone } from '@/utils/util'
    import leftTicketContent from './leftTicketContent.vue'

    export default {
        name: 'TicketDetail',
        components: {
            NoTicketContent,
            leftTicketContent,
            TicketHeader,
            RightTicketTabs
        },
        inject: ['reload'],
        provide () {
            return {
                reloadTicket: this.reloadTicket
            }
        },
        mixins: [fieldMix, commonMix, apiFieldsWatch],
        data () {
            return {
                showRightTabs: true,
                ticketTimer: null, // 单据详情轮询器
                containerLeftWidth: 0,
                ticketId: '',
                ticketErrorMessage: '',
                // 移动布局信息
                dragLine: {
                    base: 0,
                    move: 0,
                    startX: null,
                    maxLength: 0,
                    canMove: false
                },
                // 单据详情信息
                ticketInfo: {},
                // 头部信息
                headerInfo: {
                    statusColor: ''
                },
                // 通知链接进入，但节点已被其他人处理提示
                isShowNoticeDialog: false,
                noticeInfo: {
                    is_processed: false,
                    processed_user: ''
                },
                loading: {
                    ticketLoading: true,
                    nodeInfoLoading: false
                },
                // 节点列表
                nodeList: [],
                // 单据触发器列表
                ticketTriggerList: [],
                // 节点触发器列表
                nodeTriggerList: [],
                // 提单节点字段信息
                firstStateFields: [],
                // 所有字段列表
                allFieldList: []
            }
        },
        computed: {
            ...mapState({
                openFunction: state => state.openFunction
            }),
            token () {
                return this.$route.query.token
            }
        },
        async mounted () {
            await this.initData()
            if (this.$route.query.cache_key) { // 通知链接进入
                this.getTicketNoticeInfo()
            }
        },
        beforeDestroy () {
            this.clearTicketTimer()
        },
        methods: {
            // 同步数据，需等待 ticketInfo 返回
            async initData () {
                this.ticketId = this.$route.query.id
                await this.getTicketDetailInfo()
                if (this.ticketErrorMessage) {
                    this.clearTicketTimer()
                    return false
                }
                this.getTriggers()
                await this.getNodeList()
                this.getCurrTickeStatusColor()
                this.initCurrentStepData()
                this.initTicketTimer()
            },
            // 是否需要循环
            isNeedToLoop () {
                const isNeedLoop = this.nodeList.some(item => {
                    // 标准运维任务节点为 RUNNING 状态时
                    if (['TASK', 'TASK-SOPS'].includes(item.type) && item.status === 'RUNNING') {
                        return true
                    }
                    // 排队状态
                    if (item.status === 'QUEUEING') {
                        return true
                    }
                    // 特殊场景，等待当前操作人处理任务
                    if (item.is_schedule_ready === false) {
                        return true
                    }
                    // 会签或审批节点提交后，当前处理人task 为 RUNNING|EXECUTED状态，则继续轮询 FINISHED
                    const currUserDealTask = (item.tasks && item.tasks.find(task => {
                        const splitName = task.processor.replace(/\((.?)\)/, '')
                        return splitName === window.username
                    })) || {}
                    if (['SIGN', 'APPROVAL'].includes(item.type) && ['RUNNING', 'EXECUTED'].includes(currUserDealTask.status)) {
                        return true
                    }
                    return false
                })
                return isNeedLoop
            },
            // 判断当前状态是否需要轮询
            initTicketTimer () {
                this.ticketTimer = setInterval(() => {
                    const isNeedLoop = this.isNeedToLoop()
                    if (isNeedLoop && this.ticketInfo.current_status !== 'FINISHED') {
                        this.startTicketTimer()
                    } else {
                        this.clearTicketTimer()
                    }
                }, 5000)
            },
            clearTicketTimer () {
                clearInterval(this.ticketTimer)
                this.ticketTimer = null
            },
            // 开始循环
            startTicketTimer () {
                const params = {
                    id: this.ticketId,
                    token: this.token || undefined
                }
                this.$store.dispatch('deployOrder/getNodeList', params).then(async res => {
                    const newNodeList = res.data
                    const oldNodeList = this.nodeList
                    const nodeStatusHasUpdate = newNodeList.some(node => {
                        return !oldNodeList.find(item => this.isSameStatusNode(node, item))
                    })
                    if (nodeStatusHasUpdate) {
                        // 节点状态有更新
                        this.nodeList = newNodeList
                        this.updateNodeList(newNodeList)
                        this.getTriggers()
                        await this.getTicketDetailInfo()
                        this.initCurrentStepData()
                        await this.getCurrTickeStatusColor()
                    }
                })
            },
            // 获取单据信息详情
            async getTicketDetailInfo () {
                this.loading.ticketLoading = true
                const params = {
                    id: this.ticketId,
                    token: this.token || undefined
                }

                await this.$store.dispatch('change/getOrderDetails', params).then((res) => {
                    this.ticketInfo = res.data
                }).catch((res) => {
                    // 显示 404 页面
                    this.ticketErrorMessage = res.data.code === 'OBJECT_NOT_EXIST' ? this.$t('m.wiki["单据不存在或已被撤销"]') : this.$t('m.wiki["您没有权限访问"]')
                }).finally(() => {
                    this.loading.ticketLoading = false
                })
            },
            // 获取单据节点的详情
            getNodeList () {
                this.loading.nodeInfoLoading = true
                const params = {
                    id: this.ticketId,
                    token: this.token || undefined
                }
                return this.$store.dispatch('deployOrder/getNodeList', params).then((res) => {
                    this.updateNodeList(res.data)
                }).catch((res) => {
                    errorHandler(res, this)
                }).finally(() => {
                    this.loading.nodeInfoLoading = false
                })
            },
            // 更新节点信息
            updateNodeList (newNodeList) {
                const copyList = deepClone(newNodeList)
                if (this.openFunction.FIRST_STATE_SWITCH) {
                    this.firstStateFields = copyList.find(item => item.state_id === Number(this.ticketInfo.first_state_id)).fields
                    this.firstStateFields.forEach(item => {
                        this.$set(item, 'showFeild', !!item.show_type)
                        this.$set(item, 'val', (item.value || ''))
                        this.conditionField(item, this.firstStateFields)
                    })
                }
                copyList.forEach(
                    item => {
                        if (item.status === 'AUTO_SUCCESS') {
                            item.status = 'FINISHED'
                        }
                    }
                )
                this.nodeList = copyList
                this.initCurrentStepData()
            },
            // 获取当前单据状态颜色
            getCurrTickeStatusColor () {
                const status = this.ticketInfo.current_status
                const type = this.ticketInfo.service_type

                this.$store.dispatch('ticketStatus/getTypeStatus', { type }).then((res) => {
                    const item = res.data.find(m => m.key === status)
                    this.$set(this.headerInfo, 'statusColor', item ? item.color_hex : '')
                }).catch(res => {
                    errorHandler(res, this)
                })
            },
            // 获取单据手动触发器
            getTriggers () {
                this.$store.dispatch('trigger/getTicketHandleTriggers', { id: this.ticketId }).then(res => {
                    this.nodeTriggerList = res.data.filter(trigger => trigger.signal_type === 'STATE')
                    this.ticketTriggerList = res.data.filter(trigger => trigger.signal_type === 'FLOW')
                }).catch((res) => {
                    errorHandler(res, this)
                })
            },
            // 初始化当前步骤列表信息
            initCurrentStepData (diffNode) {
                this.$refs.leftTicketContent && this.$refs.leftTicketContent.initCurrentStepData()
            },
            // 重新加载
            reloadTicket () {
                this.reload()
            },
            // 按下拖拽线
            handleLineMouseDown (e) {
                document.addEventListener('mouseup', this.handleMouseUp, false)
                document.addEventListener('mousemove', this.handleLineMouseMove, false)

                const minTabWidth = document.querySelector('.ticket-container-right .bk-tab-header .bk-tab-label-wrapper .bk-tab-label-list').clientWidth
                const currTabWidth = document.querySelector('.ticket-container-right .bk-tab-header').clientWidth
                if (!this.dragLine.maxLength) {
                    // 误差
                    const offset = 4
                    this.dragLine.maxLength = currTabWidth - minTabWidth - offset
                }
                this.dragLine.startX = e.pageX
                this.dragLine.canMove = true
            },
            // 鼠标弹起
            handleMouseUp (e) {
                document.removeEventListener('mouseup', this.handleMouseUp, false)
                document.removeEventListener('mousemove', this.handleLineMouseMove, false)
                this.dragLine.base = this.dragLine.move
                this.dragLine.canMove = false
            },
            // 拖拽分屏
            handleLineMouseMove (e) {
                if (!this.dragLine.canMove) {
                    return
                }
                const el = document.getElementById('ticketContainerRight')
                const { startX, base, maxLength } = this.dragLine
                const offsetX = e.pageX - startX
                const moveX = base + offsetX
                // 正向超出可移动最大长度，隐藏右侧面板
                if (offsetX > 0 && maxLength - moveX <= 0) {
                    this.showRightTabs = false
                    this.dragLine.move = maxLength
                    el.style.display = 'none'
                    return
                }
                window.requestAnimationFrame(() => {
                    this.dragLine.move = moveX
                    el.style.width = `calc(32% - ${moveX}px)`
                })
            },
            onShowRightContent () {
                this.showRightTabs = true
                // 还原到最小宽度
                this.$nextTick(() => {
                    const el = document.getElementById('ticketContainerRight')
                    el.style.width = `calc(32% - ${this.dragLine.base}px)`
                })
            },
            getTicketNoticeInfo () {
                this.$store.dispatch('deployOrder/getTicketNoticeInfo', {
                    params: { cache_key: this.$route.query.cache_key }
                }).then(res => {
                    if (res.data && res.data.is_processed) {
                        this.noticeInfo = res.data
                        this.isShowNoticeDialog = true
                    } else {
                        // 删除 url cache_key
                        this.onNoticeConfirm()
                    }
                }).catch((res) => {
                    errorHandler(res, this)
                })
            },
            // 确认
            onNoticeConfirm () {
                const query = deepClone(this.$route.query)
                delete query.cache_key
                this.$router.replace({
                    name: this.$route.name,
                    query
                })
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '../../../scss/mixins/scroller.scss';
.ticket-detail-panel {
    width: 100%;
    height: 100%;
    min-width: 900px;
}
.ticket-container {
    display: flex;
    padding: 12px 20px;
    height: calc(100% - 50px);
    .ticket-container-left {
        flex: 1;
        margin-right: 4px;
        height: 100%;
        overflow: auto;
        @include scroller;
    }
    .drag-line {
        width: 2px;
        height: 100%;
        cursor: col-resize;
        &:hover {
            background-color: #3a84ff;
        }
    }
    .show-right-icon {
        position: absolute;
        top: 50%;
        right: -14px;
        width: 27px;
        height: 100px;
        background: #c4c6cc;
        border-radius: 14px;
        transform: translateY(-50%);
        line-height: 100px;
        color: #fff;
        cursor: pointer;
        font-size: 12px;
        &:hover {
            background-color: #3a84ff;
        }
        .icon-angle-left {
            position: absolute;
            left: -4px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 20px;
        }
    }
    .ticket-container-right {
        margin-left: 4px;
        width: 32%;
        height: 100%;
        box-shadow: 0px 2px 6px 0px rgba(0,0,0,0.1);
        background: #ffffff;
    }
}
</style>
