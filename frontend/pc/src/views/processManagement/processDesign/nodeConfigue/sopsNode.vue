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
            <bk-form :label-width="150" :model="basicsFormData" ref="basicsForm" :rules="rules" :ext-cls="'bk-form'">
                <bk-form-item :label="$t(`m.treeinfo['节点名称：']`)" :required="true" :property="'name'">
                    <bk-input
                        :ext-cls="'bk-form-width'"
                        v-model="basicsFormData.name"
                        maxlength="120">
                    </bk-input>
                </bk-form-item>
                <bk-form-item :label="$t(`m['流程类型：']`)" :required="true" :property="'processType'">
                    <bk-select
                        :ext-cls="'bk-form-width bk-form-display'"
                        v-model="basicsFormData.processType"
                        :placeholder="$t(`m['请选择流程类型']`)"
                        searchable
                        @selected="getTemplateList">
                        <bk-option
                            v-for="process in processOptions"
                            :key="process.id"
                            :id="process.id"
                            :name="process.name">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item :label="$t(`m['关联业务：']`)" :required="true" :property="'projectId'">
                    <bk-select
                        :ext-cls="'bk-form-width bk-form-display'"
                        v-model="basicsFormData.projectId"
                        :placeholder="$t(`m['请选择关联业务']`)"
                        searchable
                        :disabled="processDisable"
                        @clear="onClearProcess"
                        @selected="getProjectTemplateList">
                        <bk-option
                            v-for="project in projectList"
                            :key="project.bk_biz_id"
                            :id="project.bk_biz_id"
                            :name="project.name">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item :label="$t(`m['流程模板：']`)" :required="true" :property="'templateId'">
                    <bk-select
                        :ext-cls="'bk-form-width bk-form-display'"
                        v-model="basicsFormData.templateId"
                        :placeholder="$t(`m['请选择流程模板']`)"
                        searchable
                        :disabled="templateDisable"
                        :loading="processesLoading"
                        @clear="onClearTemplate"
                        @selected="getTemplateDetail">
                        <bk-option
                            v-for="template in templateList"
                            :key="template.id"
                            :id="template.id"
                            :name="template.name">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item :label="$t(`m['执行方案：']`)">
                    <bk-select
                        :ext-cls="'bk-form-width bk-form-display'"
                        :disabled="planDisable"
                        :placeholder="$t(`m['选择执行方案，默认选择全部任务节点']`)"
                        v-model="basicsFormData.planId"
                        multiple
                        :clearable="true"
                        :loading="planLoading"
                        @selected="onplanSelect">
                        <bk-option
                            v-for="options in planList"
                            :key="options.id"
                            :id="options.id"
                            :name="options.name">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
            </bk-form>
        </basic-card>
        <basic-card class="mt20"
            :card-label="$t(`m.treeinfo['输入参数']`)"
            :card-desc="$t(`m.treeinfo['调用该API需要传递的参数信息']`)">
            <div class="bk-param" v-bkloading="{ isLoading: sopsFormLoading }">
                <sops-get-param
                    v-if="constants.length !== 0"
                    ref="getParam"
                    :configur="configur"
                    :param-table-data="paramTableData"
                    :state-list="stateList"
                    :fields="fieldList"
                    :context="context"
                    :constants="constants"
                    :constant-default-value="constantDefaultValue"
                    :quote-vars="quoteVars"
                    :flow-info="flowInfo">
                </sops-get-param>
                <no-data v-else></no-data>
            </div>
        </basic-card>
        <common-trigger-list :origin="'state'"
            :node-type="configur.type"
            :source-id="flowInfo.id"
            :sender="configur.id"
            :table="flowInfo.table">
        </common-trigger-list>
        <div class="mt20" style="font-size: 0">
            <bk-button :theme="'primary'"
                :title="$t(`m.treeinfo['确定']`)"
                class="mr10"
                @click="submit">
                {{$t(`m.treeinfo['确定']`)}}
            </bk-button>
            <bk-button :theme="'default'"
                :title="$t(`m.treeinfo['取消']`)"
                class="mr10"
                @click="closeNode">
                {{$t(`m.treeinfo['取消']`)}}
            </bk-button>
        </div>
    </div>
</template>
<script>
    import NoData from '../../../../components/common/NoData.vue'
    import sopsGetParam from './components/sopsGetParam.vue'
    import commonTriggerList from '../../taskTemplate/components/commonTriggerList'
    import BasicCard from '@/components/common/layout/BasicCard.vue'
    import { errorHandler } from '../../../../utils/errorHandler'
    import { deepClone } from '@/utils/util.js'

    export default {
        name: 'sopsNode',
        components: {
            BasicCard,
            sopsGetParam,
            commonTriggerList,
            NoData
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
            },
            state: {
                type: [String, Number],
                default () {
                    return ''
                }
            }
        },
        data () {
            return {
                quoteVars: [],
                constantDefaultValue: {},
                basicsFormData: {
                    name: '',
                    templateId: '',
                    projectId: '',
                    planId: [],
                    processType: ''
                },
                processOptions: [
                    {
                        id: 'business',
                        name: '项目流程'
                    },
                    {
                        id: 'common',
                        name: '公共流程'
                    }
                ],
                isLoading: false,
                excludeTaskNodesId: [],
                projectList: [],
                templateList: [],
                paramTableData: [],
                stateList: [],
                fieldList: [],
                constants: [],
                context: {
                    project: {
                        id: '',
                        bk_biz_id: '',
                        name: '',
                        from_cmdb: true
                    },
                    bk_biz_id: '',
                    site_url: window.SITE_URL_SOPS + window.PREFIX_SOPS
                },
                sopsFormLoading: false,
                processesLoading: false,
                planLoading: false,
                planList: [],
                optionalNodeIdList: [],
                templateDisable: false,
                planDisable: false,
                processDisable: false,
                renderFormValidate: false,
                biz: [
                    {
                        name: this.$t(`m.treeinfo["业务"]`),
                        custom_type: '',
                        source_type: 'custom',
                        value: '--',
                        key: 1
                    }
                ],
                rules: {
                    name: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'blur'
                        },
                        {
                            max: 50,
                            message: '不能多于50个字符',
                            trigger: 'blur'
                        }
                    ],
                    processType: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'blur'
                        }
                    ],
                    projectId: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'blur'
                        }
                    ],
                    templateId: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'blur'
                        }
                    ]
                }
            }
        },
        computed: {
            globalChoise () {
                return this.$store.state.common.configurInfo
            }
        },
        created () {

        },
        mounted () {
            this.initData()
        },
        methods: {
            async initData () {
                this.isLoading = true
                this.getRelatedFields()
                const userProjectList = await this.$store.dispatch('apiRemote/get_user_project_list')
                if (userProjectList) this.projectList = userProjectList.data
                if (Object.keys(this.configur.extras).length !== 0) {
                    this.basicsFormData.name = this.configur.name
                    // 流程类型
                    this.basicsFormData.processType = this.configur.extras.sops_info.template_source
                    // 跳过执行任务ID
                    this.excludeTaskNodesId = this.configur.extras.sops_info.exclude_task_nodes_id || []
                    // 项目ID
                    this.basicsFormData.projectId = this.configur.extras.sops_info.bk_biz_id.value
                    if (this.basicsFormData.processType === 'common') {
                        await this.getTemplateList(this.basicsFormData.processType)
                    } else {
                        await this.getProjectTemplateList(this.basicsFormData.projectId)
                    }
                    await this.getTemplateDetail(this.configur.extras.sops_info.template_id)
                    this.basicsFormData.templateId = this.configur.extras.sops_info.template_id
                }
                this.isLoading = false
            },
            // 获取common流程类型
            async getTemplateList (key) {
                const isCommonProcess = key === 'common'
                const params = isCommonProcess ? {} : { bk_biz_id: this.basicsFormData.projectId }
                if (!isCommonProcess) this.basicsFormData.projectId = ''
                this.basicsFormData.templateId = ''
                this.basicsFormData.planId = []
                this.templateDisable = !isCommonProcess
                this.planDisable = !isCommonProcess
                if (isCommonProcess) {
                    this.processesLoading = true
                    // 获取流程模板
                    await this.$store.dispatch('getTemplateList', params).then((res) => {
                        this.templateList = res.data
                    }).catch(res => {
                        errorHandler(res, this)
                    }).finally(() => {
                        this.processesLoading = false
                    })
                }
            },
            // 获取项目模板列表
            async getProjectTemplateList (id) {
                const params = {
                    bk_biz_id: id
                }
                if (this.basicsFormData.processType !== 'common') {
                    this.processesLoading = true
                    this.basicsFormData.templateId = ''
                    const res = await this.$store.dispatch('getTemplateList', params)
                    if (res.result) {
                        this.templateList = res.data
                        this.templateDisable = false
                        this.planDisable = false
                        this.processesLoading = false
                    }
                }
            },
            // 获取标准运维模板
            async getTemplateDetail (id) {
                const params = {
                    bk_biz_id: this.basicsFormData.processType === 'common' ? '' : this.basicsFormData.projectId,
                    template_id: id
                }
                const templateInfo = this.templateList.find(item => item.id === id)
                if (templateInfo !== undefined) {
                    this.context.project.bk_biz_id = templateInfo.bk_biz_id
                    this.context.project.id = this.template
                }
                this.constants = []
                this.sopsFormLoading = true
                this.basicsFormData.planId = []
                await this.$store.dispatch('getTemplateDetail', params).then(res => {
                    this.constants = res.data.constants
                    this.optionalNodeIdList = res.data.all_ids || []
                    this.getTempaltePlanList(id)
                }).catch(res => {
                    errorHandler(res, this)
                }).finally(() => {
                    this.sopsFormLoading = false
                })
            },
            // 获取模板任务列表
            getTempaltePlanList (id) {
                const template = this.templateList.find(template => template.id === id)
                this.planList = []
                const params = {
                    bk_biz_id: template.bk_biz_id,
                    template_id: template.id
                }
                this.planLoading = true
                this.$store.dispatch('getTemplatePlanList', params).then(res => {
                    this.planList = res.data
                    if (this.excludeTaskNodesId.length !== 0) {
                        res.data.forEach(item => {
                            if (item.data) {
                                const ids = this.optionalNodeIdList.filter(nodeId => {
                                    return !JSON.parse(item.data).includes(nodeId)
                                })
                                const result = ids.filter(ite => {
                                    return !this.excludeTaskNodesId.includes(ite)
                                })
                                if (result.length === 0 && this.excludeTaskNodesId.length === ids.length) {
                                    this.basicsFormData.planId.push(item.id)
                                }
                            }
                        })
                    }
                    this.onplanSelect(this.basicsFormData.planId)
                }).catch(res => {
                    errorHandler(res, this)
                }).finally(() => {
                    this.planLoading = false
                })
            },
            async onplanSelect (ids) {
                const planList = []
                if (ids.length > 0) {
                    ids.forEach(item => {
                        const plan = this.planList.find(plan => plan.id === item)
                        if (plan.data) {
                            const twPlanList = JSON.parse(plan.data)
                            for (let index = 0; index < twPlanList.length; index++) {
                                if (planList.indexOf(twPlanList[index]) === -1) {
                                    planList.push(twPlanList[index])
                                }
                            }
                        }
                    })
                    this.excludeTaskNodesId = this.optionalNodeIdList.filter(nodeId => {
                        return !planList.includes(nodeId)
                    })
                } else {
                    this.excludeTaskNodesId = []
                }
                const template = this.templateList.find(item => item.id === this.basicsFormData.templateId)
                try {
                    this.sopsFormLoading = true
                    const res = await this.$store.dispatch('taskFlow/getSopsPreview', {
                        bk_biz_id: template.bk_biz_id,
                        template_id: template.id,
                        exclude_task_nodes_id: this.excludeTaskNodesId
                    })
                    const constants = []
                    for (const key in res.data.pipeline_tree.constants) {
                        if (res.data.pipeline_tree.constants[key].show_type === 'show') {
                            constants.push(res.data.pipeline_tree.constants[key])
                        }
                    }
                    constants.forEach(item => {
                        this.configur.extras.sops_info.constants.filter(ite => {
                            if (item.key === ite.key) {
                                item.value = ite.value
                            }
                            this.constantDefaultValue[item.key] = deepClone(item.value)
                        })
                    })
                    constants.sort((a, b) => a.index - b.index)
                    this.constants = constants
                } catch (e) {
                    console.error(e)
                } finally {
                    this.sopsFormLoading = false
                }
            },
            async getRelatedFields () {
                const params = {
                    workflow: this.flowInfo.id,
                    state: this.configur.id,
                    field: ''
                }
                await this.$store.dispatch('apiRemote/get_related_fields', params).then(res => {
                    this.stateList = res.data
                }).catch(res => {
                    errorHandler(res, this)
                }).finally(() => {
                })
            },
            onClearProcess () {
                if (this.basicsFormData.processType !== 'common') {
                    this.templateDisable = true
                    this.planDisable = true
                    this.constants = []
                }
                this.templateList = []
                this.basicsFormData.templateId = ''
                this.planList = []
            },
            onClearTemplate () {
                this.basicsFormData.planId = []
                this.basicsFormData.templateId = ''
                this.constants = []
                this.planList = []
            },
            closeNode () {
                this.$parent.closeConfigur()
            },
            submit () {
                if (this.$refs.getParam) {
                    this.renderFormValidate = this.$refs.getParam.getRenderFormValidate()
                } else {
                    this.renderFormValidate = true
                }
                this.$refs.basicsForm.validate().then(_ => {
                    if (this.renderFormValidate) {
                        const formData = []
                        this.biz.forEach(item => {
                            const vt = item.source_type === 'custom' ? 'custom' : 'variable'
                            const ite = {
                                value: this.basicsFormData.projectId,
                                name: item.name,
                                key: item.key || 1,
                                value_type: vt,
                                type: item.custom_type
                            }
                            formData.push(ite)
                        })
                        const biz = formData.splice(0, 1)[0]
                        this.constants.map(item => {
                            // renderForm的formData与constant匹配的key
                            const formKey = Object.keys(this.$refs.getParam.formData).filter(key => key === item.key)
                            const vt = item.source_type === 'custom' ? 'custom' : 'variable'
                            const { name, key } = item
                            if (item.show_type === 'show') {
                                const formTeamlate = {
                                    value: this.$refs.getParam.formData[formKey],
                                    name,
                                    key: key || 1,
                                    value_type: vt,
                                    type: item.custom_type
                                }
                                formData.push(formTeamlate)
                            }
                        })
                        const params = {
                            'extras': {
                                'sops_info': {
                                    'bk_biz_id': biz,
                                    'template_id': this.basicsFormData.templateId,
                                    'constants': formData,
                                    'exclude_task_nodes_id': this.excludeTaskNodesId,
                                    'template_source': this.basicsFormData.processType
                                }
                            },
                            'is_draft': false,
                            'is_terminable': false,
                            'name': this.basicsFormData.name,
                            'type': 'TASK-SOPS',
                            'workflow': this.configur.workflow
                        }
                        const stateId = this.configur.id
                        this.$store.dispatch('cdeploy/putSopsInfo', { params, stateId }).then((res) => {
                            this.$bkMessage({
                                message: this.$t(`m.treeinfo["保存成功"]`),
                                theme: 'success'
                            })
                            this.$parent.closeConfigur()
                        }, (res) => {
                            errorHandler(res, this)
                        }).finally(() => {
                        })
                    }
                })
            }
        }
    }
</script>

<style lang='scss' scoped>
    @import '../../../../scss/mixins/scroller.scss';
    .bk-basic-node {
        padding: 30px 40px;
        height: 100%;
        background-color: #FAFBFD;
        overflow: auto;
        @include scroller;
    }
    .bk-basic-info {
        padding-bottom: 20px;
        border-bottom: 1px solid #E9EDF1;
        margin-bottom: 20px;
    }
    .bk-form {
        width: 520px;
    }
    .bk-form-width {
        width: 340px;
    }
    .bk-form-display {
        float: left;
        margin-right: 10px;
    }
</style>
