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
                            :key="plugin.id"
                            :id="plugin.id"
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
                            :key="version.id"
                            :id="version.id"
                            :name="version.name">
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
            <!-- <div class="bk-params-title">
                <p>{{ $t(`m['输出参数']`) }}:</p>
                <p>{{ $t(`m['蓝鲸插件执行之后的输出，可以通过勾选的方式作为引用变量在后面的节点使用']`) }}</p>
            </div> -->
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
                :key="formKey"
                @change="changeFormItem">
                <template #suffix="{ path }">
                    <div v-if="hookedVarList[path]" class="var-select">
                        <ul style="width: 100%; height: 100%">
                            <li v-for="varItem in stateList" :key="varItem.key" @click.prevent="handleVarClick(varItem, path)">{{ varItem.name }}</li>
                        </ul>
                    </div>
                </template>
            </BkRenderForm>
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
                    { name: '1', key: '1' },
                    { name: '2', key: '2' }
                ], // 引用变量
                // 这是个测试的schema
                schema: {
                    type: 'object',
                    properties: {
                        items: {
                            title: '标题',
                            type: 'string',
                            default: '这是一个初始值'
                        },
                        items1: {
                            title: '标题1',
                            type: 'string',
                            default: '这是一个初始值1'
                        }
                    }
                },
                layout: [],
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
            // 初始变量下拉选择的状态
            Object.keys(this.schema.properties).map(item => {
                this.$set(this.hookedVarList, item, false)
            })
        },
        methods: {
            async initData () {
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
            changeFormItem (newValue, oldValue) {
                Object.keys(newValue).map(item => {
                    this.hookedVarList[item] = false
                    if (newValue[item] !== oldValue[item]) {
                        if (newValue[item].endsWith('{{')) {
                            this.hookedVarList[item] = true
                        }
                    }
                })
            },
            handleVarClick (item, path) {
                console.log(path)
                this.$set(this.hookedVarList, path, false)
                this.formKey = new Date().getTime()
            },
            onSelectplugin () {
                this.versionListLoading = true
                this.basicInfo.version = ''
                try {
                    //
                } catch (e) {
                    console.log(e)
                } finally {
                    this.versionListLoading = false
                }
            },
            getFormInfo () {
                this.formLoading = true
                try {
                    //
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
                if (this.$refs.processors && !this.$refs.processors.verifyValue()) {
                    this.checkStatus.processors = true
                    return
                }
                const valid = this.$refs.bkForm.validateForm()
                console.log(valid)
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
            .var-select {
                z-index: 999;
                background: #fff;
                width: 99%;
                position: absolute;
                top: 38px;
                left: 5px;
                min-height: 50px;
                max-height: 150px;
                overflow: auto;
                font-size: 12px;
                padding: 5px;
                box-shadow: 0px 2px 6px 0px rgba(0, 0, 0, 0.4);
                border: 1px soild #dcdee5;
                @include scroller;
                ul {
                    li {
                        width: 100%;
                        line-height: 20px;
                        height: 20px;
                        padding: 0 10px;
                        &:hover {
                            background-color: #eaf3ff;
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
