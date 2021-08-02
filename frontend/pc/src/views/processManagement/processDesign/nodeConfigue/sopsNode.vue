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
            <bk-form :label-width="150" :model="configur">
                <bk-form-item :label="$t(`m.treeinfo['节点名称：']`)" :required="true">
                    <bk-input :ext-cls="'bk-form-width'"
                        v-model="configur.name"
                        maxlength="120">
                    </bk-input>
                </bk-form-item>
                <bk-form-item :label="$t(`m.treeinfo['流程/原子']`)" :required="true">
                    <bk-select :ext-cls="'bk-form-width bk-form-display'"
                        v-model="templateId"
                        :clearable="false"
                        :placeholder="$t(`m.treeinfo['请选择流程/原子']`)"
                        searchable
                        @selected="showTemplateDetail">
                        <bk-option v-for="option in templateList"
                            :key="option.id"
                            :id="option.id"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
            </bk-form>
        </basic-card>

        <basic-card class="mt20"
            :card-label="$t(`m.treeinfo['输入参数']`)"
            :card-desc="$t(`m.treeinfo['调用该API需要传递的参数信息']`)">
            <div class="bk-param">
                <sops-get-param
                    ref="getParam"
                    :configur="configur"
                    :param-table-data="paramTableData"
                    :state-list="stateList"
                    :flow-info="flowInfo">
                </sops-get-param>
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
    import sopsGetParam from './components/sopsGetParam.vue'
    import commonTriggerList from '../../taskTemplate/components/commonTriggerList'
    import BasicCard from '@/components/common/layout/BasicCard.vue'
    import { errorHandler } from '../../../../utils/errorHandler'

    export default {
        name: 'sopsNode',
        components: {
            BasicCard,
            sopsGetParam,
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
                templateId: '',
                templateList: [],
                paramTableData: [],
                stateList: []
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
                await this.configur
                await this.flowInfo
                await this.getRelatedFields()
                await this.$store.dispatch('cdeploy/getSopsTemplate').then((res) => {
                    if (res.code === 'OK') {
                        this.templateList = res.data
                        if (this.configur.extras
                            && this.configur.extras.sops_info
                            && this.configur.extras.sops_info.template_id) {
                            this.templateId = this.configur.extras.sops_info.template_id
                            this.showTemplateDetail()
                        }
                    }
                }).catch(res => {
                    errorHandler(res, this)
                }).finally(() => {
                })
            },
            async showTemplateDetail (key, templateData) {
                const params = {
                    template_id: this.templateId
                }
                this.isLoading = true
                await this.$store.dispatch('cdeploy/getTemplateDetail', params).then((res) => {
                    this.paramTableData = res.data.constants
                }).catch(res => {
                    errorHandler(res, this)
                }).finally(() => {
                    this.isLoading = false
                })
                // 过滤value
                this.paramTableData.forEach((item) => {
                    if (item.custom_type === 'input') {
                        item.custom_type = 'STRING'
                    } else {
                        item.custom_type = item.custom_type.toUpperCase()
                    }
                })
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
            closeNode () {
                this.$emit('closeConfigur', false)
            },
            submit () {
                const paramsTable = []
                this.$refs.getParam.paramTableShow.forEach((item, index) => {
                    const vt = item.source_type === 'custom' ? 'custom' : 'variable'
                    const ite = {
                        value: item.value,
                        name: item.name,
                        key: item.key || 1,
                        value_type: vt,
                        type: item.custom_type
                    }
                    paramsTable.push(ite)
                })
                const biz = paramsTable.splice(0, 1)[0]
                const params = {
                    'extras': {
                        'sops_info': {
                            'bk_biz_id': biz,
                            'template_id': this.templateId,
                            'constants': paramsTable
                        }
                    },
                    'is_draft': false,
                    'is_terminable': false,
                    'name': this.configur.name,
                    'type': 'TASK-SOPS',
                    'workflow': this.configur.workflow
                }
                const stateId = this.configur.id
                this.$store.dispatch('cdeploy/putSopsInfo', { params, stateId }).then((res) => {
                    this.$bkMessage({
                        message: this.$t(`m.treeinfo["保存成功"]`),
                        theme: 'success'
                    })
                    this.$emit('closeConfigur', true)
                }, (res) => {
                    errorHandler(res, this)
                }).finally(() => {
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
    .bk-form-width {
        width: 340px;
    }
    .bk-form-display {
        float: left;
        margin-right: 10px;
    }
</style>
