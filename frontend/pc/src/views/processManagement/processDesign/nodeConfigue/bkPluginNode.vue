<template>
    <div class="bk-basic-node" v-bkloading="{ isLoading: isLoading }">
        <basic-card>
            <bk-form ref="basicInfo" :model="basicInfo" :label-width="150" :rules="basicInfoRules" :ext-cls="'bk-form'" form-type="vertical">
                <bk-form-item
                    data-test-id="devops-input-name"
                    :label="$t(`m.treeinfo['节点名称：']`)"
                    :required="true"
                    error-display-type="normal"
                    :ext-cls="'bk-form-width bk-form-display'"
                    :property="'nodeName'">
                    <bk-input :clearable="true" v-model="basicInfo.nodeName"></bk-input>
                </bk-form-item>
                <bk-form-item
                    data-test-id="devops-select-project"
                    :label="$t(`m['第三方插件']`)"
                    :required="true"
                    error-display-type="normal"
                    :ext-cls="'bk-form-width bk-form-display'"
                    :property="'plugin'">
                    <bk-select
                        v-model="basicInfo.plugin"
                        searchable
                        :disabled="false"
                        @selected="onSelectplugin">
                        <bk-option v-for="plugin in pluginList"
                            :key="plugin.code"
                            :id="plugin.code"
                            :name="plugin.name">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item
                    data-test-id="devops-select-pipeline"
                    :label="$t(`m['版本']`)"
                    :required="true"
                    :property="'version'"
                    error-display-type="normal"
                    :ext-cls="'bk-form-width bk-form-display'">
                    <bk-select
                        searchable
                        v-model="basicInfo.version"
                        :loading="versionListLoading"
                        :disabled="versionListDisabled"
                        @selected="getFormInfo">
                        <bk-option v-for="version in versionList"
                            :key="version"
                            :id="version"
                            :name="version">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item
                    data-test-id="devops-component-processor"
                    :label="$t(`m.treeinfo['处理人：']`)"
                    :required="true">
                    <div @click="checkStatus.processors = false">
                        <deal-person
                            ref="processors"
                            :value="processorsInfo"
                            :node-info="configur"
                            :exclude-role-type-list="excludeProcessor">
                        </deal-person>
                    </div>
                </bk-form-item>
            </bk-form>
            <div class="bk-params-title">
                <p>{{ $t(`m.treeinfo['输入参数']`) }}:</p>
                <p>{{ $t(`m['执行蓝鲸插件需要填写的参数信息，可以使用 {{ 来使用流程内的变量']`) }}</p>
            </div>
            <BkRenderForm
                class="bk-form-plugin"
                v-model="formData"
                ref="bkForm"
                :schema="schema"
                :layout="layout"
                :rules="rules"
                :form-type="formType"
                :context="{
                    ...context,
                    rules: {}
                }"
                :http-adapter="{
                    responseParse: {
                        labelKey: 'name',
                        valueKey: 'id'
                    }
                }"
                :key="formKey">
                <template #suffix="{ path, schema: schemaField }">
                    <bk-checkbox
                        ext-cls="select-check"
                        v-model="hookVarList[path]"
                        @change="onChangeChecked($event, path ,schemaField)">
                    </bk-checkbox>
                    <bk-select :disabled="!hookVarList[path]" style="width: 200px;"
                        :value="hookSelectList[path].replace(/^\$\{/, '').replace(/\}$/, '')"
                        ext-cls="select-custom"
                        searchable
                        @selected="changeConstant($event, path ,schemaField)">
                        <bk-option v-for="option in stateList"
                            :key="option.id"
                            :id="option.key"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                </template>
            </BkRenderForm>
            <div class="bk-params-title">
                <p>{{ $t(`m['输出参数']`) }}:</p>
                <p>{{ $t(`m['蓝鲸插件执行之后的输出，可以通过勾选的方式作为引用变量在后面的节点使用']`) }}</p>
            </div>
            <div style="padding: 20px">
                <bk-table
                    :data="outputsData">
                    <bk-table-column label="名称" prop="title"></bk-table-column>
                    <bk-table-column label="设置为引用变量">
                        <template slot-scope="props">
                            <bk-checkbox @change="onchangeOutputCheck($event, props)"></bk-checkbox>
                        </template>
                    </bk-table-column>
                </bk-table>
            </div>
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
        </basic-card>
    </div>
</template>
<script>
    import createForm from '@tencent/bkui-form/dist/bkui-form-umd'
    import dealPerson from './components/dealPerson.vue'
    import commonTriggerList from '../../taskTemplate/components/commonTriggerList'
    import BasicCard from '@/components/common/layout/BasicCard.vue'
    // import NoData from '@/components/common/NoData.vue'
    import i18n from '@/i18n/index.js'
    function newRequiredRule () {
        return {
            required: true,
            message: i18n.t('m.treeinfo["字段必填"]'),
            trigger: 'blur'
        }
    }
    const BkRenderForm = createForm()
    export default {
        name: 'devops',
        components: {
            BasicCard,
            commonTriggerList,
            // NoData
            dealPerson,
            BkRenderForm
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
                    plugin: '',
                    version: '',
                    processors: []
                },
                pluginList: [],
                versionList: [],
                hookVarList: {},
                hookSelectList: {},
                versionListLoading: false,
                versionListDisabled: true,
                formLoading: false,
                basicInfoRules: {
                    nodeName: [newRequiredRule()],
                    plugin: [newRequiredRule()],
                    version: [newRequiredRule()]

                },
                checkStatus: {
                    delivers: false,
                    processors: false
                },
                excludeProcessor: [],
                processorsInfo: {
                    type: '',
                    value: ''
                },
                formKey: '',
                hookedVarList: {},
                stateList: [
                ], // 引用变量
                // 这是个测试的schema
                schema: {
                    type: 'object',
                    properties: {
                    }
                },
                layout: [],
                outputsData: [],
                outputsVarList: {},
                primarySchema: {},
                formData: {},
                formType: 'vertical',
                rules: {
                    maxLength20: { validator: '{{ $self.value.length < 20}}', message: '长度必须大于 20' },
                    number: { validator: '/!^[0-9]*$/', message: '必须是数字' },
                    required: { message: '值不能为空', validator: '{{ $self.value !== ""}}' },
                    reservedWord: { validator: '{{ !$self.value.includes("bk") }}', message: '不能使用保留字符' }
                },
                context: {
                    bizId: 1,
                    site_url: '/o/bk_sops/',
                    projectId: 'b37778ec757544868a01e1f01f07037f',
                    baseURL: '',
                    pod_name: 'test_pod_name'
                }
            }
        },
        watch: {
        },
        mounted () {
            this.initData()
            this.getRelatedFields()
            // 初始变量下拉选择的状态
            // Object.keys(this.schema.properties).map(item => {
            //     this.$set(this.hookedVarList, item, false)
            // })
        },
        methods: {
            async initData () {
                this.basicInfo.nodeName = this.configur.name
                this.processorsInfo = {
                    type: this.configur.processors_type,
                    value: this.configur.processors
                }
                this.$store.dispatch('bkPlugin/getPluginList').then(res => {
                    this.pluginList = res.data.plugins
                    this.getExcludeRoleTypeList()
                })
                if (Object.keys(this.configur.extras).length !== 0) {
                    this.basicInfo.plugin = this.configur.extras.bk_plugin_info.plugin_code
                    this.onSelectplugin(this.basicInfo.plugin)
                    this.basicInfo.version = this.configur.extras.bk_plugin_info.version
                    this.getFormInfo(this.basicInfo.version)
                    this.formData = this.configur.extras.bk_plugin_info.inputs
                    this.primarySchema = this.configur.extras.bk_plugin_info.inputs
                    this.schema = this.primarySchema
                    // this.outputsData = Object.keys(this.configur.extras.bk_plugin_info.inputs.properties).map(item => {
                    //     console.log(item)
                    //     return this.configur.extras.bk_plugin_info.inputs.properties[item]
                    // })
                    // console.log(this.outputsData)
                }
            },
            async getRelatedFields () {
                const params = {
                    workflow: this.flowInfo.id,
                    state: this.configur.id,
                    field: ''
                }
                this.$store.dispatch('apiRemote/get_related_fields', params).then(res => {
                    this.stateList = res.data
                })
            },
            onChangeChecked (value, path, schema) {
                console.log(this.schema)
                const data = Object.assign({}, this.formData)
                if (value) {
                    if (schema.type === 'integer') {
                        schema.type = 'string'
                    }
                    Object.assign(schema, { 'ui:component': { name: 'bk-input', props: { disabled: true, value: data[path] } } })
                    console.log(schema, '1111111111')
                } else {
                    Object.assign(schema, { 'ui:component': { name: 'bk-input', props: { disabled: false, value: data[path] } } })
                    console.log(schema, '222222222')
                    // Object.assign(schema, initSchemaItem[path], { default: data })
                }
                // this.schema = JSON.stringify(curSchemaItem, null, 2)
                // console.log(curSchemaItem)
                // console.log(curSchemaItem, initSchemaItem)
                if (!value) {
                    // this.formData[path] = ''
                    this.hookSelectList[path] = ''
                }
                console.log(this.schema)
                this.formKey = new Date().getTime()
            },
            changeConstant (value, path, schema) {
                if (schema.type === 'integer') {
                    schema.type = 'string'
                }
                this.hookSelectList[path] = '${' + value + '}'
                Object.assign(schema, { 'ui:component': { name: 'bk-input', props: { disabled: true, value: this.hookSelectList[path] } } })
                this.formKey = new Date().getTime()
            },
            onchangeOutputCheck (value, props) {
                this.outputsVarList[props.$index] = value
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
                // if (!this.flowInfo.is_iam_used) {
                //     excludeProcessor.push('IAM')
                // }
                // 处理场景如果不是'DISTRIBUTE_THEN_PROCESS' || 'DISTRIBUTE_THEN_CLAIM'，则去掉派单人指定
                if (this.configur.distribute_type !== 'DISTRIBUTE_THEN_PROCESS' && this.configur.distribute_type !== 'DISTRIBUTE_THEN_CLAIM') {
                    excludeProcessor.push('BY_ASSIGNOR')
                }
                if (!this.flowInfo.is_biz_needed) {
                    excludeProcessor.push('CMDB')
                }
                this.excludeProcessor = [...['EMPTY', 'API'], ...excludeProcessor]
            },
            handleVarClick (item, path) {
                this.formData[path] = '{{' + item.key + '}}'
                this.$set(this.hookedVarList, path, false)
                this.formKey = new Date().getTime()
            },
            onSelectplugin (value) {
                this.schema = {}
                this.formData = {}
                this.versionListLoading = true
                this.basicInfo.version = ''
                try {
                    const params = { plugin_code: value }
                    this.$store.dispatch('bkPlugin/getPluginMeta', params).then(res => {
                        this.versionList = res.data.versions
                        this.versionListDisabled = false
                    })
                } catch (e) {
                    console.log(e)
                } finally {
                    this.versionListLoading = false
                }
            },
            getFormInfo: function (value) {
                this.schema = {}
                this.formData = {}
                this.formLoading = true
                try {
                    const params = { plugin_code: this.basicInfo.plugin, plugin_version: value }
                    this.$store.dispatch('bkPlugin/getPluginDetail', params).then(res => {
                        this.schema = res.data.inputs
                        Object.keys(this.schema.properties).map(item => {
                            this.$set(this.hookSelectList, item, '')
                        })
                        this.outputsData = res.data.outputs.properties
                        Object.keys(res.data.outputs.properties).map(item => {
                            this.$set(this.outputsVarList, item, false)
                        })
                    })
                } catch (e) {
                    console.log(e)
                } finally {
                    this.formLoading = false
                }
            },
            handleHook () {
                console.log(arguments)
            },
            onSelectVar () {

            },
            closeNode () {
                this.$parent.closeConfigur()
            },
            submit () {
                console.log(this.formData)
                debugger
                const { value: processors, type: processors_type } = this.$refs.processors.getValue()
                const bk_plugin_info = { plugin_code: this.basicInfo.plugin, version: this.basicInfo.version, inputs: this.formData, context: {} }
                if (this.$refs.processors && !this.$refs.processors.verifyValue()) {
                    this.checkStatus.processors = true
                    return
                }
                const valid = this.$refs.bkForm.validateForm()
                if (!valid) {
                    return
                }
                const params = {
                    name: this.basicInfo.nodeName,
                    processors: processors || '',
                    processors_type: processors_type || '',
                    type: 'BK-PLUGIN',
                    is_draft: false,
                    extras: {
                        bk_plugin_info: bk_plugin_info
                    },
                    variables: { outputs: [] },
                    workflow: this.configur.workflow
                }
                const stateId = this.configur.id
                this.$store.dispatch('cdeploy/putWebHook', { params, stateId }).then((res) => {
                    this.$bkMessage({
                        message: this.$t(`m.treeinfo["保存成功"]`),
                        theme: 'success'
                    })
                    this.$parent.closeConfigur()
                }, e => {
                    console.log(e)
                }).finally(() => {
                    this.secondClick = false
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
        overflow: unset;
        @include scroller;
        /deep/ .common-section-card-label {
            display: none;
        }
        /deep/ .common-section-card-body {
            padding: 20px;
        }
        /deep/ .bk-form-width {
            width: 448px;
        }
        .bk-params-title {
            margin-top: 20px;
            font-size: 14px;
            p:nth-child(1) {
                color: #63656e;
                margin-bottom: 4px;
            }
            p:nth-child(2) {
                font-size: 12px;
                color: #929397;
            }
        }
        .bk-form-plugin {
            padding: 20px;
            /deep/ .bk-schema-form-group {
                overflow: unset !important;
            }
            /deep/ .bk-form-content {
                display: flex;
                align-items: center;
                .bk-form-control {
                    width: 70%;
                }
                .select-check {
                    margin: 0 auto;
                }
                .select-custom {
                    width: 150px;
                }
            }
            .var-select {
                width: 200px;
                height: 230px;
                position: absolute;
                border-radius: 4px;
                background: #fff;
                font-size: 14px;
                border: 1px solid #c4c6cc;
                top: 35px;
                left: 71px;
                z-index: 2000;
                overflow-y: auto;
                @include scroller;
                ul {
                    padding: 5px;
                    li {
                        height: 30px;
                        cursor: pointer;
                        color: #75777f;
                        &:hover {
                            background-color: #e1ecff;
                            color: #3a84ff;
                        }
                    }
                }
            }
        }
    }
    .bk-basic-info {
        padding-bottom: 20px;
        border-bottom: 1px solid #E9EDF1;
        margin-bottom: 20px;
    }
    .bk-form-width {
        width: 448px;
    }
    .bk-form-display {
        float: left;
        margin-right: 10px;
    }
</style>
