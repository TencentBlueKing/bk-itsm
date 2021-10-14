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
    <div class="bk-basic-node" v-bkloading="{ isLoading: isLoading }">
        <basic-card :card-label="$t(`m.treeinfo['基本信息']`)">
            <bk-form
                :label-width="150"
                :model="formInfo"
                :rules="nodeInfoRule" ref="nodeInfoForm">
                <bk-form-item
                    :label="$t(`m.treeinfo['节点名称：']`)"
                    :required="true"
                    :property="'name'"
                    :ext-cls="'bk-form-width'">
                    <bk-input v-model="formInfo.name"
                        maxlength="120">
                    </bk-input>
                </bk-form-item>
                <bk-form-item
                    :label="$t(`m.treeinfo['节点标签：']`)"
                    :required="true"
                    :ext-cls="'bk-form-width'">
                    <bk-select
                        v-model="formInfo.tag"
                        :clearable="false"
                        searchable
                        :font-size="'medium'">
                        <bk-option v-for="option in nodeTagList"
                            :key="option.key"
                            :id="option.key"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item
                    :label="$t(`m.treeinfo['审批方式：']`)"
                    :required="true"
                    :property="'nodeType'">
                    <bk-radio-group v-model="formInfo.is_multi">
                        <bk-radio :value="false" :ext-cls="'mr40 pr40'">{{$t(`m.treeinfo['或签']`)}}
                            <i class="bk-itsm-icon icon-icon-info tooltip-icon"
                                v-bk-tooltips="$t(`m.treeinfo['任一处理人完成审批即可。']`)"></i>
                        </bk-radio>
                        <bk-radio :value="true">{{$t(`m.treeinfo['多签']`)}}
                            <i class="bk-itsm-icon icon-icon-info tooltip-icon"
                                v-bk-tooltips="$t(`m.treeinfo['所有处理人均要进行审批。']`)"></i>
                        </bk-radio>
                    </bk-radio-group>
                </bk-form-item>
                <bk-form-item :label="$t(`m.treeinfo['处理人：']`)" :required="true">
                    <div @click="checkStatus.processors = false">
                        <deal-person
                            ref="processors"
                            :value="processorsInfo"
                            :node-info="configur"
                            :exclude-role-type-list="excludeProcessor">
                        </deal-person>
                    </div>
                </bk-form-item>
                <bk-form-item :label="$t(`m.treeinfo['设置单据状态：']`)" :required="true" :ext-cls="'bk-form-width'">
                    <bk-select :ext-cls="'inline-form-width'"
                        v-model="formInfo.ticket_type"
                        :clearable="false"
                        searchable
                        :font-size="'medium'"
                        @selected="handleTicket">
                        <bk-option v-for="option in billStatusList"
                            :key="option.type"
                            :id="option.type"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                    <template v-if="formInfo.ticket_type === 'custom'">
                        <bk-select :ext-cls="'inline-form-width'"
                            v-model="formInfo.ticket_key"
                            :loading="ticketKeyLoading"
                            :clearable="false"
                            searchable
                            :font-size="'medium'">
                            <bk-option v-for="option in secondLevelList"
                                :key="option.key"
                                :id="option.key"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                    </template>
                </bk-form-item>
                <template v-if="!configur.is_builtin">
                    <bk-form-item :label="$t(`m.treeinfo['是否可转单：']`)" :required="true">
                        <bk-radio-group v-model="formInfo.can_deliver">
                            <bk-radio :value="true" :ext-cls="'mr20'">{{ $t('m.treeinfo["是"]') }}</bk-radio>
                            <bk-radio :value="false">{{ $t('m.treeinfo["否"]') }}</bk-radio>
                        </bk-radio-group>
                    </bk-form-item>
                </template>
                <template v-if="formInfo.can_deliver">
                    <bk-form-item :label="$t(`m.treeinfo['转单人：']`)" :required="true">
                        <div @click="checkStatus.delivers = false">
                            <deal-person
                                ref="delivers"
                                :value="deliversInfo"
                                :exclude-role-type-list="deliversExclude">
                            </deal-person>
                        </div>
                    </bk-form-item>
                </template>
            </bk-form>
        </basic-card>
        <basic-card :card-label="$t(`m.treeinfo['字段配置']`)" class="mt20">
            <field-config
                ref="field"
                :flow-info="flowInfo"
                :configur="configur">
            </field-config>
        </basic-card>
        <common-trigger-list :origin="'state'"
            :node-type="configur.type"
            :source-id="flowInfo.id"
            :sender="configur.id"
            :table="flowInfo.table">
        </common-trigger-list>
        <div class="bk-node-btn">
            <bk-button :theme="'primary'"
                :title="$t(`m.treeinfo['确定']`)"
                :loading="secondClick"
                class="mr10"
                @click="submitNode">
                {{$t(`m.treeinfo['确定']`)}}
            </bk-button>
            <bk-button :theme="'default'"
                :title="$t(`m.treeinfo['取消']`)"
                :loading="secondClick"
                class="mr10"
                @click="closeNode">
                {{$t(`m.treeinfo['取消']`)}}
            </bk-button>
        </div>
    </div>
</template>
<script>
    import dealPerson from './components/dealPerson.vue'
    import fieldConfig from './components/fieldConfig.vue'
    import commonTriggerList from '../../taskTemplate/components/commonTriggerList'
    import BasicCard from '@/components/common/layout/BasicCard.vue'
    import { errorHandler } from '../../../../utils/errorHandler'
    
    export default {
        name: 'ApprovalNode',
        components: {
            BasicCard,
            dealPerson,
            fieldConfig,
            commonTriggerList
        },
        props: {
            // 流程信息
            flowInfo: {
                type: Object,
                default () {
                    return {}
                }
            },
            // 节点信息
            configur: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        data () {
            return {
                isLoading: false,
                secondClick: false,
                getConditionFlag: false,
                ticketKeyLoading: false,
                formInfo: {
                    name: '',
                    tag: '',
                    ticket_type: '',
                    ticket_key: '',
                    is_sequential: false,
                    is_multi: true,
                    processors: []
                },
                nodeTagList: [],
                allCondition: [],
                secondLevelList: [],
                excludeProcessor: [], // 处理人排除类型
                deliversExclude: ['BY_ASSIGNOR', 'EMPTY', 'STARTER', 'VARIABLE', 'API', 'ASSIGN_LEADER', 'STARTER_LEADER'], // 转单人排除类型
                // 单据状态
                billStatusList: [
                    { type: 'keep', name: this.$t('m.treeinfo["延续上个节点"]') },
                    { type: 'custom', name: this.$t('m.treeinfo["自定义"]') }
                ],
                processorsInfo: {
                    type: '',
                    value: ''
                },
                deliversInfo: {
                    type: '',
                    value: ''
                },
                checkStatus: {
                    delivers: false,
                    processors: false
                },
                nodeInfoRule: {
                    name: [
                        {
                            required: true,
                            message: this.$t(`m.newCommon['请输入节点名称']`),
                            trigger: 'blur'
                        }
                    ],
                    processors: [
                        {
                            validator: function (val) {
                                return val.length
                            },
                            message: this.$t(`m.newCommon['请选择处理人']`),
                            trigger: 'blur'
                        }
                    ]
                }
            }
        },
        mounted () {
            this.initData()
        },
        methods: {
            initData () {
                this.isLoading = true
                let getSecondLevelList
                // name
                this.formInfo.name = this.configur.name
                // 节点标签
                this.formInfo.tag = this.configur.tag || ''
                this.formInfo.is_multi = this.configur.is_multi === true
                // this.formInfo.can_deliver = this.configur.can_deliver === true
                this.formInfo.is_sequential = this.configur.is_sequential
                this.formInfo.processors = this.configur.processors ? this.configur.processors.split(',') : []
                this.formInfo.ticket_type = this.configur.extras.ticket_status ? this.configur.extras.ticket_status.type : 'keep'
                this.formInfo.ticket_key = this.configur.extras.ticket_status ? this.configur.extras.ticket_status.name : ''
                this.$set(this.formInfo, 'can_deliver', this.configur.can_deliver === true)
                if (this.formInfo.ticket_type === 'custom') {
                    getSecondLevelList = this.getSecondLevelList()
                }
                if (this.formInfo.can_deliver) {
                    this.deliversInfo = {
                        type: this.configur.delivers_type,
                        value: this.configur.delivers
                    }
                }
                // 处理人
                this.processorsInfo = {
                    type: this.configur.processors_type,
                    value: this.configur.processors
                }
                const getNodeTagList = this.getNodeTagList()
                this.getExcludeRoleTypeList()
                Promise.all([getSecondLevelList, getNodeTagList]).then(() => {
                    this.isLoading = false
                })
            },
            // 获取节点标签数据
            getNodeTagList () {
                const params = {
                    key: 'STATE_TAG_TYPE'
                }
                return this.$store.dispatch('datadict/get_data_by_key', params).then((res) => {
                    this.nodeTagList = res.data
                }).catch(res => {
                    errorHandler(res, this)
                }).finally(() => {

                })
            },
            // 获取等级
            getSecondLevelList () {
                this.ticketKeyLoading = true
                return this.$store.dispatch('ticketStatus/getOverallTicketStatuses').then(res => {
                    this.secondLevelList = res.data
                }).catch(res => {
                    errorHandler(res, this)
                }).finally(() => {
                    this.ticketKeyLoading = false
                })
            },
            // 计算处理人类型需要排除的类型
            getExcludeRoleTypeList () {
                // 不显示的人员类型
                let excludeProcessor = []
                // 内置节点
                if (this.configur.is_builtin) {
                    excludeProcessor = ['BY_ASSIGNOR', 'STARTER', 'VARIABLE']
                } else {
                    excludeProcessor = ['OPEN']
                }
                // 是否使用权限中心角色
                if (!this.flowInfo.is_iam_used) {
                    excludeProcessor.push('IAM')
                    this.deliversExclude.push('IAM')
                }
                // 处理场景如果不是'DISTRIBUTE_THEN_PROCESS' || 'DISTRIBUTE_THEN_CLAIM'，则去掉派单人指定
                if (this.configur.distribute_type !== 'DISTRIBUTE_THEN_PROCESS' && this.configur.distribute_type !== 'DISTRIBUTE_THEN_CLAIM') {
                    excludeProcessor.push('BY_ASSIGNOR')
                }
                if (!this.flowInfo.is_biz_needed) {
                    excludeProcessor.push('CMDB')
                    this.deliversExclude.push('CMDB')
                }
                this.excludeProcessor = [...['EMPTY', 'API'], ...excludeProcessor]
            },
            // 确认
            async submitNode () {
                const validates = [this.$refs.nodeInfoForm.validate()]
                await Promise.all(validates).then(() => {
                    const params = {
                        is_draft: false,
                        workflow: this.flowInfo.id,
                        type: this.configur.type,
                        is_terminable: false,
                        processors_type: 'PERSON'
                    }
                    // 基本信息
                    params.name = this.formInfo.name
                    params.is_sequential = this.formInfo.is_sequential
                    params.processors_type = ''
                    params.processors = ''
                    // 处理人为空校验
                    if (this.$refs.processors && !this.$refs.processors.verifyValue()) {
                        this.checkStatus.processors = true
                        return
                    }
                    if (this.$refs.processors) {
                        const data = this.$refs.processors.getValue()
                        params.processors_type = data.type
                        params.processors = data.value
                    }
                    // 转单人为空校验
                    if (this.$refs.delivers && !this.$refs.delivers.verifyValue()) {
                        this.checkStatus.delivers = true
                        return
                    }
                    if (this.$refs.delivers) {
                        const data = this.$refs.delivers.getValue()
                        params.delivers_type = data.type
                        params.delivers = data.value
                    }
                    params.is_multi = this.formInfo.is_multi
                    params.tag = this.formInfo.tag
                    params.can_deliver = this.formInfo.can_deliver
                    params.ticket_type = this.formInfo.ticket_type
                    params.extras = {
                        ticket_status: {
                            name: this.formInfo.ticket_key,
                            type: this.formInfo.ticket_type
                        }
                    }
                    // 字段配置
                    const fieldInfo = this.$refs.field.showTabList
                    params.fields = fieldInfo.map(item => {
                        return item.id
                    })
                    const id = this.configur.id
                    if (this.secondClick) {
                        return
                    }
                    this.secondClick = true
                    this.$store.dispatch('deployCommon/updateNode', { params, id }).then((res) => {
                        this.$bkMessage({
                            message: this.$t(`m.treeinfo["保存成功"]`),
                            theme: 'success'
                        })
                        this.$emit('closeConfigur', true)
                    }).catch(res => {
                        errorHandler(res, this)
                    }).finally(() => {
                        this.secondClick = false
                    })
                }).catch((validator) => {
                    // 防止出现Uncaught
                    console.log(validator)
                })
            },
            // 取消
            closeNode () {
                this.$emit('closeConfigur', false)
            },
            // 获取二级状态数据
            handleTicket (value) {
                this.formInfo.ticket_key = ''
                if (value === 'custom') {
                    if (!this.secondLevelList.length) {
                        this.getSecondLevelList()
                    }
                }
            }
        }
    }
</script>

<style lang='scss' scoped>
    @import '../../../../scss/mixins/scroller.scss';
    .bk-error-info {
        color: #ff5656;
        font-size: 12px;
        line-height: 30px;
    }
    .bk-basic-node {
        padding: 20px;
        height: 100%;
        background-color: #FAFBFD;
        overflow: auto;
        @include scroller;

        .bk-node-btn{
            font-size: 0;
        }

        .bk-service-name{
            h1{
                padding-left: 10px;
            }
        }

        .tooltip-icon{
            font-size: 15px;
            vertical-align: inherit;
            &:before{
                color: #979BA5;
            }
        }

        .bk-form-width {
            width: 480px;
        }
        .inline-form-width {
            float: left;
            width: 330px;
            margin-right: 10px;
        }
        .form-cus-height{
            & div:first-child{
                height: auto!important;
            }
        }

        .bk-processor-width {
            width: 760px;
        }

        .bk-sign-info{

            .bk-service-title{
                display: flex;
                align-items: center;
                margin-top: 40px;
            }

            .bk-condition-content{
                height: auto;
                max-width: 750px;

                .bk-condition-group{
                    width: 100%;

                    .bk-group-title{
                        color: #63656E;
                        font-weight: bold;
                        font-size: 14px;
                        margin-bottom: 6px;
                        margin-top: 30px;
                    }

                    .bk-group-content{
                        display: flex;
                        width: fit-content;
                        align-items: center;
                        flex-wrap: wrap;
                        padding: 0 20px 20px 20px;
                        border: 1px solid #DCDEE5;
                        position: relative;
                        background-color: #fff;

                        .bk-condition{
                            display: flex;
                            align-items: center;
                            padding-top: 20px;
                            width: 100%;

                            .bk-form-item-cus{

                                /deep/ .bk-form-content{
                                    display: inline-flex;
                                    align-items: center;
                                }

                                /deep/ .bk-select-dropdown{
                                    width: 100%;
                                }

                                .bk-form-width-long{
                                    display: inline-flex;
                                    width: 250px;
                                }

                                .buttonIcon{
                                    position: absolute;
                                    display: inline-flex;
                                    justify-content: center;
                                    align-items: center;
                                    height: 30px;
                                    width: 30px;
                                    right: 1px;
                                    color: #63656e;
                                    font-size: 12px;
                                    border-left: 1px solid #c4c6cc;
                                    background: #f2f4f8;
                                }

                                .bk-form-width-short{
                                    width: 100px
                                }

                                .bk-operate-expression{
                                    width: 50px;
                                    display: inline-flex;
                                    align-items: center;

                                    .bk-icon-disable{
                                        cursor: no-drop;
                                        &:before{
                                            color: #DCDEE5;
                                        }
                                    }
                                }
                            }
                        }

                        .bk-delete-group {
                            position: absolute;
                            top: 6px;
                            right: 6px;
                            text-align: center;
                            cursor: pointer;
                            font-weight: 700;
                            color: #979ba5;
                            border-radius: 50%;
                            font-size: 18px;
                            display: none;
                        }

                        &:hover {
                            .bk-delete-group {
                                display: block;
                            }
                        }
                    }

                    .bk-group-contents{
                        padding: 14px 34px 34px 22px;

                        .bk-left-block{
                            position: relative;
                            display: inline-flex;
                            height: 32px;
                            width: 20px;
                            flex-wrap: wrap;

                            .left-top-default, .left-bottom-default{
                                height: 50%;
                                width: 100%;
                                border: 1px dashed #DCDEE5;
                                border-right: none;
                            }

                            .left-top-default{
                                border-top: none;
                            }

                            .left-bottom-default{
                                border-bottom: none;
                                border-top: none;
                            }

                            .bk-left-letter{
                                position: absolute;
                                height: 18px;
                                width: 28px;
                                line-height: 18px;
                                font-size: 12px;
                                color: #FFFFFF;
                                background: #C4C6CC;
                                text-align: center;
                                top: 100%;
                                left: -13px;
                                border-radius: 2px;
                            }

                            .no-left-border{
                                border-left: none;
                            }
                        }
                    }
                }

                .bk-add-group{
                    display: flex;
                    align-items: center;
                    color: #3A84FF;
                    margin-top: 15px;
                    cursor: pointer;
                    height: 20px;
                    line-height: 20px;
                    font-size: 14px;
                    width: fit-content;

                    .icon-add-new:before{
                        color: #3A84FF;
                    }
                }
            }
        }
    }
</style>
