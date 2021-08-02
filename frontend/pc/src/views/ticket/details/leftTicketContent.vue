<template>
    <div>
        <div class="base-info-content " v-bkloading="{ isLoading: loading.nodeInfoLoading }">
            <div class="ticket-base-info">
                <bk-tab :active.sync="baseActiveTab" type="unborder-card">
                    <bk-tab-panel
                        name="base"
                        :label="$t(`m.slaContent['基本信息']`)">
                        <!-- 基础信息 -->
                        <basic-information
                            ref="basicInfo"
                            v-if="ticketId && !loading.ticketLoading && !loading.nodeInfoLoading"
                            :basic-infomation="ticketInfo"
                            :first-state-fields="firstStateFields">
                        </basic-information>
                    </bk-tab-panel>
                    <bk-tab-panel
                        name="preview"
                        :label="$t(`m.newCommon['工单进度预览']`)">
                        <!-- 工单预览 -->
                        <order-preview
                            v-if="baseActiveTab === 'preview' && !loading.ticketLoading && !loading.nodeInfoLoading"
                            :basic-infomation="ticketInfo"
                            :node-list="nodeList"
                            :current-step-list="currentStepList"
                            @reloadTicket="reloadTicket">
                        </order-preview>
                    </bk-tab-panel>
                </bk-tab>
            </div>
        </div>
        <div class="current-step-content" v-bkloading="{ isLoading: currentStepLoading }">
            <bk-tab :active.sync="stepActiveTab" type="unborder-card" v-if="!currentStepLoading">
                <!-- 当前步骤 -->
                <bk-tab-panel
                    name="currentStep"
                    :label="$t(`m.newCommon['当前步骤']`)">
                    <!-- 当前节点 -->
                    <template slot="label">
                        <span class="panel-name">{{ $t(`m.newCommon['当前步骤']`) }}</span>
                        <i class="panel-count">{{ currStepNodeNum }}</i>
                    </template>
                    <current-steps
                        v-if="!loading.ticketLoading && !loading.nodeInfoLoading"
                        ref="currentNode"
                        :loading="loading.ticketLoading"
                        :basic-infomation="ticketInfo"
                        :node-list="nodeList"
                        :current-step-list="currentStepList"
                        :node-trigger-list="nodeTriggerList"
                        @handlerSubmitSuccess="reloadTicket">
                    </current-steps>
                </bk-tab-panel>
                <!-- 全部评论 TODO -->
                <!-- <bk-tab-panel
                    name="allComments"
                    :label="$t(`m.newCommon['所有评论']`)">
                    111
                </bk-tab-panel> -->
            </bk-tab>
        </div>
    </div>
</template>

<script>
    import BasicInformation from './BasicInformation.vue'
    import OrderPreview from './OrderPreview.vue'
    import CurrentSteps from './currentSteps/index.vue'
    import { deepClone } from '@/utils/util'
    import commonMix from '@/views/commonMix/common.js'
    import fieldMix from '@/views/commonMix/field.js'
    import apiFieldsWatch from '@/views/commonMix/api_fields_watch.js'

    export default {
        name: 'LeftTicketContent',
        components: {
            BasicInformation,
            OrderPreview,
            CurrentSteps
        },
        mixins: [commonMix, fieldMix, apiFieldsWatch],
        props: {
            loading: Object,
            ticketInfo: Object,
            nodeList: Array,
            firstStateFields: Array,
            nodeTriggerList: Array,
            ticketId: [Number, String]
        },
        inject: ['reloadTicket'],
        data () {
            return {
                baseActiveTab: 'base',
                stepActiveTab: 'currentStep',
                // 当前步骤
                currentStepList: [],
                allFieldList: [],
                currentStepLoading: false
            }
        },
        computed: {
            currStepNodeNum () {
                if (this.ticketInfo.is_over) { // 已结束单不显示当前步骤
                    return 0
                }
                return this.currentStepList.length
            }
        },
        methods: {
            initCurrentStepData () {
                this.currentStepLoading = true
                const oldCurrentNodeList = deepClone(this.currentStepList)
                const updateList = []
                this.currentStepList = []
                this.allFieldList = []
                // 修改显示隐藏的数据
                this.nodeList.forEach(item => {
                    // 过滤显示数据
                    if (['RUNNING', 'SUSPEND', 'FAILED', 'SUCCESS'].includes(item.status)) {
                        updateList.push(item)
                    }
                    this.allFieldList = this.allFieldList.concat(item.fields)
                })
                // 刷新某个步骤，避免用户填写时突然刷新打断，新旧节点 diff，如果状态未当前节点状态未更新，不应该刷新
                updateList.forEach(newNode => {
                    const oldNode = oldCurrentNodeList.find(old => old.state_id === newNode.state_id)
                    if (this.isSameStatusNode(newNode, oldNode) && oldNode.status === 'RUNNING') {
                        this.currentStepList.push(oldNode)
                    } else {
                        this.currentStepList.push(newNode)
                    }
                })

                // 隐藏字段显示隐藏判断逻辑
                this.allFieldList.forEach(item => {
                    this.$set(item, 'showFeild', !!item.show_type)
                    this.$set(item, 'val', (item.value || ''))
                })
                // 关联数据展示的逻辑处理
                this.allFieldList.forEach(item => {
                    this.conditionField(item, this.allFieldList)
                })
                this.currentStepList.forEach((item, index) => {
                    if (item.fields && item.fields.length) {
                        item.fields.forEach(node => {
                            this.$set(node, 'service', this.ticketInfo.service_type)
                            if (node.key === 'current_status') {
                                this.$set(node, 'ticket_status', this.ticketInfo.current_status)
                            }
                        })
                        this.isNecessaryToWatch(item, '')
                    }
                    // 顺序会签
                    if (item.type === 'SIGN' && !item.is_sequential) {
                        const finishedList = item.tasks.filter(task => task.status === 'FINISHED')
                        item.tasks = item.tasks.filter(task => finishedList.findIndex(finished => finished.processor === task.processor) === -1)
                        item.tasks = [...finishedList, ...item.tasks]
                    }
                })
                this.$nextTick(() => {
                    this.currentStepLoading = false
                })
            }
        }
    }
</script>
<style lang='scss' scoped>
.base-info-content {
    padding: 0 10px;
    min-height: 145px;
    box-shadow: 0px 2px 6px 0px rgba(0,0,0,0.1);
    background: #ffffff;
    /deep/ .bk-tab-section {
        padding: 0;
    }
}
.current-step-content {
    margin-top: 16px;
    padding: 10px;
    box-shadow: 0px 2px 6px 0px rgba(0,0,0,0.1);
    background: #ffffff;
    /deep/ .bk-tab-section {
        padding: 0;
    }
    .panel-count {
        display: inline-block;
        min-width: 16px;
        height: 16px;
        padding: 0 4px;
        line-height: 16px;
        border-radius: 8px;
        text-align: center;
        font-style: normal;
        font-size: 12px;
        color: #fff;
        background-color: #C4C6CC;
    }
    /deep/ .bk-tab-label-item.active {
        .panel-count {
            color: #3a84ff;
            background: #e1ecff;
        }
    }
}
</style>
