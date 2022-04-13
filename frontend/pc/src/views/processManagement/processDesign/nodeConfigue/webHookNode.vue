<template>
    <div class="bk-basic-node" v-bkloading="{ isLoading: isLoading }">
        <basic-card>
            <bk-form
                ref="webForm"
                :label-width="150"
                :model="formData"
                :rules="rules"
                form-type="vertical">
                <bk-form-item :label="'节点名称'" :ext-cls="'bk-form-width bk-form-display'" property="name" error-display-type="normal" required>
                    <bk-input v-model="formData.name"></bk-input>
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
                <bk-form-item :label="'URL'" :ext-cls="'bk-form-display'" required property="url" error-display-type="normal">
                    <bk-input v-model="formData.url" :clearable="true" :font-size="'medium'">
                        <bk-dropdown-menu class="group-text" @show="isDropdownShow = true" @hide="isDropdownShow = false" ref="dropdown" slot="prepend" :font-size="'medium'">
                            <bk-button type="primary" slot="dropdown-trigger">
                                <template v-for="(item, index) in requestOptions">
                                    <span v-if="curEq === item" :key="index">{{item}}</span>
                                </template>
                                <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShow }]"></i>
                            </bk-button>
                            <ul class="bk-dropdown-list" slot="dropdown-content">
                                <li v-for="(item, index) in requestOptions" :key="index"><a href="javascript:;" @click="selectRequsetOpt(item)">{{ item }}</a></li>
                            </ul>
                        </bk-dropdown-menu>
                    </bk-input>
                    <div class="requset-config">
                        <request-config ref="requestConfig" :type="curEq"></request-config>
                    </div>
                </bk-form-item>
                <bk-form-item :label="'成功条件'" :ext-cls="'bk-form-display'">
                    <bk-input v-model="formData.name"></bk-input>
                </bk-form-item>
                <bk-form-item :label="'返回变量'" :ext-cls="'bk-form-display'">
                    <bk-table :data="returnReslut"
                        :size="'small'">
                        <bk-table-column label="变量名称" prop="name"></bk-table-column>
                        <bk-table-column label="来源" prop="source"></bk-table-column>
                    </bk-table>
                </bk-form-item>
            </bk-form>
            <common-trigger-list
                ref="commonTriggerList"
                :origin="'state'"
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
    import requestConfig from './components/requestConfig.vue'
    import BasicCard from '@/components/common/layout/BasicCard.vue'
    import dealPerson from './components/dealPerson.vue'
    import commonTriggerList from '../../taskTemplate/components/commonTriggerList'
    export default {
        name: 'webHookNode',
        components: {
            BasicCard,
            dealPerson,
            commonTriggerList,
            requestConfig
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
                isDropdownShow: false,
                curEq: 'GET',
                requestOptions: ['GET', 'POST'],
                formData: {
                    name: '',
                    url: ''
                },
                rules: {
                    name: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'blur'
                        }
                    ],
                    url: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'blur'
                        }
                    ]
                },
                returnReslut: [
                    {
                        name: '执行结果',
                        source: 'iefs'
                    },
                    {
                        name: '宿舍地址',
                        source: 'iefs---dz'
                    }
                ],
                processorsInfo: {
                    type: '',
                    value: ''
                },
                checkStatus: {
                    delivers: false,
                    processors: false
                },
                excludeProcessor: []
            }
        },
        methods: {
            selectRequsetOpt (item) {
                this.curEq = item
            },
            closeNode () {
                this.$parent.closeConfigur()
            },
            submit () {
                Promise.all([this.$refs.processors.verifyValue(), this.$refs.webForm.validate()]).then(_ => {
                    const { value: processors, type: processors_type } = this.$refs.processors.getValue()
                    const { queryParams, auth, headers, body, settings, bodyValue } = this.$refs.requestConfig.config
                    console.log(queryParams, auth, headers, body, settings, bodyValue)
                    
                    const params = {
                        name: this.formData.name,
                        processors: processors || '',
                        processors_type: processors_type || '',
                        type: 'WEBHOOK',
                        variables: {
                            method: this.curEq,
                            url: this.formData.url,
                            query_params: [],
                            auth: '',
                            headers: [],
                            body: {
                                type: '',
                                row_type: '',
                                value: ''
                            },
                            settings: {},
                            success_exp: ''
                        }
                    }
                    console.log(params)
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
        /deep/ .common-section-card-label {
            display: none;
        }
        /deep/ .common-section-card-body {
            padding: 20px;
        }
        /deep/ .bk-form-width {
            width: 448px;
        }
        .piprline-title {
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
    }
    .requset-config {
        min-height: 188px;
        margin: 10px 0;
        padding: 0 16px;
        background-color: #f5f7fa;
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
    .setion-title-icon {
        margin-top: 5px;
    }
</style>
