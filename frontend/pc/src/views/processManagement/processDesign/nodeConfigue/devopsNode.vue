<template>
    <div class="bk-basic-node" v-bkloading="{ isLoading: isLoading }">
        <basic-card :card-label="$t(`m.treeinfo['基本信息']`)">
            <bk-form ref="basicInfo" :model="basicInfo" :label-width="150" :rules="basicInfoRules" :ext-cls="'bk-form'">
                <bk-form-item
                    data-test-id="devops-input-name"
                    :label="$t(`m.treeinfo['节点名称：']`)"
                    :required="true"
                    :ext-cls="'bk-form-width bk-form-display'"
                    :property="'nodeName'">
                    <bk-input :clearable="true" v-model="basicInfo.nodeName"></bk-input>
                </bk-form-item>
                <bk-form-item
                    data-test-id="devops-select-project"
                    :label="$t(`m['项目']`)"
                    :required="true"
                    :ext-cls="'bk-form-width bk-form-display'"
                    :property="'businessId'">
                    <bk-select
                        v-model="basicInfo.businessId"
                        searchable
                        :disabled="false"
                        @selected="onSelectBusiness">
                        <bk-option v-for="business in businessList"
                            :key="business.englishName"
                            :id="business.englishName"
                            :name="business.projectName">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item
                    data-test-id="devops-select-pipeline"
                    :label="$t(`m['流水线：']`)"
                    :required="true"
                    :property="'pipelineId'"
                    :ext-cls="'bk-form-width bk-form-display'">
                    <bk-select
                        searchable
                        v-model="basicInfo.pipelineId"
                        :loading="pipelineLoading"
                        :disabled="pipelineDisabled"
                        @selected="getPipelineInfo(0)">
                        <bk-option v-for="pipeline in pipelineList"
                            :key="pipeline.pipelineId"
                            :id="pipeline.pipelineId"
                            :name="pipeline.pipelineName">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
            </bk-form>
        </basic-card>

        <basic-card class="mt20"
            :card-label="$t(`m['流水线参数']`)"
            :card-desc="$t(`m.treeinfo['调用该API需要传递的参数信息']`)">
            <div class="bk-param" v-if="pipelineFormList.length !== 0" v-bkloading="{ isLoading: pipeFormLoading }">
                <bk-form
                    ref="devopsVariable"
                    ext-cls="pipelineForm"
                    form-type="vertical"
                    :model="pipelineData"
                    :rules="pipelineRules"
                    :label-width="200">
                    <bk-form-item v-for="pipeline in pipelineFormList"
                        :key="pipeline.id"
                        :label="pipeline.id"
                        :property="pipeline.id"
                        :rules="pipelineRules[pipeline.id]"
                        :required="pipeline.required">
                        <bk-input
                            v-model="pipelineData[pipeline.id]"
                            :clearable="true">
                        </bk-input>
                    </bk-form-item>
                </bk-form>
                <span class="setion-title-icon" @click.stop="showPipelineStages = !showPipelineStages">
                    <i v-if="showPipelineStages" class="bk-icon icon-angle-down"></i>
                    <i v-else class="bk-icon icon-angle-right"></i>
                    {{ $t(`m.tickets['插件预览']`) }}
                </span>
                <devops-preview
                    v-show="showPipelineStages"
                    :stages="pipelineStages">
                </devops-preview>
            </div>
            <no-data v-else></no-data>
        </basic-card>

        <common-trigger-list :origin="'state'"
            :node-type="configur.type"
            :source-id="flowInfo.id"
            :sender="configur.id"
            :table="flowInfo.table">
        </common-trigger-list>
        
        <div class="mt20" style="font-size: 0">
            <bk-button :theme="'primary'"
                data-test-id="devops-button-submit"
                :title="$t(`m.treeinfo['确定']`)"
                class="mr10"
                @click="submit">
                {{$t(`m.treeinfo['确定']`)}}
            </bk-button>
            <bk-button :theme="'default'"
                data-test-id="devops-button-close"
                :title="$t(`m.treeinfo['取消']`)"
                class="mr10"
                @click="closeNode">
                {{$t(`m.treeinfo['取消']`)}}
            </bk-button>
        </div>
    </div>
</template>
<script>
    import commonTriggerList from '../../taskTemplate/components/commonTriggerList'
    import BasicCard from '@/components/common/layout/BasicCard.vue'
    import DevopsPreview from '@/components/task/DevopsPreview.vue'
    import NoData from '@/components/common/NoData.vue'
    import { errorHandler } from '../../../../utils/errorHandler'
    import i18n from '@/i18n/index.js'
    function newRequiredRule () {
        return {
            required: true,
            message: i18n.t('m.treeinfo["字段必填"]'),
            trigger: 'blur'
        }
    }
    export default {
        name: 'devops',
        components: {
            BasicCard,
            commonTriggerList,
            DevopsPreview,
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
                isLoading: false,
                basicInfo: {
                    nodeName: '',
                    businessId: '',
                    pipelineId: ''
                },
                businessList: [],
                pipelineList: [],
                pipelineDisabled: true,
                pipelineLoading: false,
                constants: [],
                pipelineFormList: [],
                pipelineData: {}, // 流水线参数
                pipeFormLoading: false,
                pipelineStages: [],
                showPipelineStages: true, // 展示预览
                basicInfoRules: {
                    nodeName: [newRequiredRule()],
                    businessId: [newRequiredRule()],
                    pipelineId: [newRequiredRule()]
                   
                },
                pipelineRules: {}
            }
        },
        watch: {
            'basicInfo.businessId' (val) {
                this.pipelineDisabled = !val
                if (!val) {
                    this.pipelineList = []
                    this.pipelineFormList = []
                    this.basicInfo.pipelineId = ''
                }
            },
            'basicInfo.pipelineId' (val) {
                if (!val) {
                    this.pipelineFormList = []
                }
            }
        },
        mounted () {
            this.initData()
        },
        methods: {
            async initData () {
                this.$store.dispatch('ticket/getDevopsUserProjectList').then(res => {
                    this.businessList = res.data
                    if (this.configur && !this.configur.is_draft) {
                        this.basicInfo.nodeName = this.configur.name
                        this.basicInfo.businessId = res.data.filter(item => item.project_name === this.configur.extras.devops_info.project_id.name)[0].englishName
                        this.onSelectBusiness()
                        this.basicInfo.pipelineId = this.configur.extras.devops_info.pipeline_id.value
                        this.getPipelineInfo(1)
                    }
                })
            },
            // 选择项目获取流水线
            onSelectBusiness () {
                this.pipelineLoading = true
                this.basicInfo.pipelineId = ''
                try {
                    this.$store.dispatch('ticket/getDevopsPipelineList', { 'project_id': this.basicInfo.businessId }).then(res => {
                        this.pipelineList = res.data
                    })
                } catch (e) {
                    console.log(e)
                } finally {
                    this.pipelineLoading = false
                }
            },
            // 获取流水线信息
            getPipelineInfo (init) {
                this.pipeFormLoading = true
                Promise.all([
                    this.$store.dispatch('ticket/getDevopsPipelineStartInfo', { 'project_id': this.basicInfo.businessId, 'pipeline_id': this.basicInfo.pipelineId }),
                    this.$store.dispatch('ticket/getDevopsPipelineDetail', { 'project_id': this.basicInfo.businessId, 'pipeline_id': this.basicInfo.pipelineId })
                ]).then(res => {
                    this.pipelineData = {}
                    this.pipelineFormList = res[0].data.properties
                    res[0].data.properties.forEach(item => {
                        if (init) item.defaultValue = this.configur.extras.devops_info.constants.filter(ite => ite.name === item.id)[0].value
                        this.$set(this.pipelineData, item.id, item.defaultValue)
                        this.pipelineRules[item.id] = [{
                            required: item.required,
                            message: i18n.t('m.treeinfo["字段必填"]'),
                            trigger: 'blur'
                        }]
                    })
                    this.pipelineStages = res[1].data.stages
                }).catch(e => {
                    console.log(e)
                }).finally(_ => {
                    this.pipeFormLoading = false
                })
            },
            closeNode () {
                this.$parent.closeConfigur()
            },
            submit () {
                Promise.all([
                    this.$refs.basicInfo.validate(),
                    this.$refs.devopsVariable ? this.$refs.devopsVariable.validate() : null
                ]).then(res => {
                    const basicData = this.businessList.filter(item => item.project_code === this.basicInfo.businessId)[0]
                    const pipelineData = this.pipelineList.filter(item => item.pipelineId === this.basicInfo.pipelineId)[0]
                    const constants = Object.keys(this.pipelineData).map(item => {
                        return {
                            'value': this.pipelineData[item],
                            'name': item,
                            'key': item
                        }
                    })
                    const params = {
                        'extras': {
                            'devops_info': {
                                'username': window.username,
                                'project_id': {
                                    'value': basicData.projectCode,
                                    'name': basicData.projectName,
                                    'key': basicData.project_id
                                },
                                'pipeline_id': {
                                    'value': pipelineData.pipelineId,
                                    'name': pipelineData.pipelineName,
                                    'key': pipelineData.pipeline_id
                                },
                                'constants': constants
                            }
                        },
                        'is_draft': false,
                        'is_terminable': false,
                        'name': this.basicInfo.nodeName,
                        'type': 'TASK-DEVOPS',
                        'workflow': this.configur.workflow
                    }
                    const stateId = this.configur.id
                    this.$store.dispatch('cdeploy/putDevopsInfo', { params, stateId }).then((res) => {
                        this.$bkMessage({
                            message: this.$t(`m.treeinfo["保存成功"]`),
                            theme: 'success'
                        })
                        this.$parent.closeConfigur()
                    }, (res) => {
                        errorHandler(res, this)
                    }).finally(() => {
                    })
                })
            }
        }
    }
</script>

<style lang='scss' scoped>
    @import '../../../../scss/mixins/scroller.scss';
    .bk-form {
        display: flex;
        flex-direction: column;
    }
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
    .bk-form-width {
        width: 480px;
    }
    .bk-form-display {
        float: left;
        margin-right: 10px;
    }
    .setion-title-icon {
        margin-top: 5px;
    }
    .pipelineForm {
        margin-bottom: 10px;
    }
</style>
