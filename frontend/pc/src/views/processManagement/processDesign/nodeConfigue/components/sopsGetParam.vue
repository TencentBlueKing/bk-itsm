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
    <div class="bk-get-param">
        <!-- <bk-table :ext-cls="'bk-editor-table'"
            :data="paramTableShow"
            :size="'small'">
            <bk-table-column :label="$t(`m.treeinfo['字段名']`)" prop="name"></bk-table-column>
            <template v-if="!isStatic">
                <bk-table-column :label="$t(`m.treeinfo['字段类型']`)" prop="custom_type"></bk-table-column>
            </template>
            <bk-table-column :label="$t(`m.treeinfo['参数值']`)" width="400">
                <template slot-scope="props">
                    <template v-if="!isStatic">
                        <div style="width: 120px; position: absolute; top: 5px; left: 15px;">
                            <bk-select v-model="props.row.source_type"
                                :clearable="false"
                                searchable
                                :font-size="'medium'">
                                <bk-option v-for="option in sourceTypeList"
                                    :key="option.key"
                                    :id="option.key"
                                    :name="option.name">
                                </bk-option>
                            </bk-select>
                        </div>
                        <div class="bk-normal-textarea"
                            v-if="!props.row.source_type || (props.row.source_type === 'custom')"
                            style="width: 240px; position: absolute; top: 4px; right: 15px;">
                            <textarea style="width: 240px;"
                                class="bk-form-textarea bk-textarea-tanble"
                                :placeholder="$t(`m.treeinfo['请输入参数值，换行分隔']`)"
                                v-model.trim="props.row.value">
                            </textarea>
                        </div>
                        <div v-else style="width: 240px; position: absolute; top: 4px; right: 15px;">
                            <bk-select :ref="'selectSops' + props.row.key"
                                v-model="props.row.value"
                                :clearable="false"
                                searchable
                                :font-size="'medium'">
                                <bk-option v-for="option in stateList"
                                    :key="option.key"
                                    :id="option.key"
                                    :name="option.name">
                                </bk-option>
                                <div slot="extension" @click="addNewItem(props.row)" style="cursor: pointer;">
                                    <i class="bk-icon icon-plus-circle mr10"></i>{{ $t('m.treeinfo["添加变量"]') }}
                                </div>
                            </bk-select>
                        </div>
                    </template>
                    <template v-else>
                        <span>{{props.row.value || '--'}}</span>
                    </template>
                </template>
            </bk-table-column>
        </bk-table> -->
        <div class="sops-form">
            <render-form
                ref="renderForm"
                :form-option="formOptions"
                :constants="constants"
                :context="context"
                :key="renderKey"
                v-model="formData">
            </render-form>
        </div>
        <div class="bk-add-slider" v-if="sliderInfo.show && isStatic === false">
            <bk-sideslider
                :is-show.sync="sliderInfo.show"
                :title="sliderInfo.title"
                :width="sliderInfo.width">
                <div class="p20" slot="content">
                    <add-field
                        :change-info="changeInfo"
                        :sosp-info="showTabData"
                        :workflow="flowInfo.id"
                        :state="configur.id"
                        @closeShade="closeShade"
                        @getRelatedFields="getRelatedFields">
                    </add-field>
                </div>
            </bk-sideslider>
        </div>
    </div>
</template>

<script>
    import addField from '../addField/index.vue'

    export default {
        name: 'sopsGetParam',
        components: {
            addField
        },
        props: {
            context: {
                type: Object,
                default () {
                    return {}
                }
            },
            constants: {
                type: Array,
                default () {
                    return []
                }
            },
            isStaticData: {
                type: Array,
                default () {
                    return []
                }
            },
            configur: {
                type: Object,
                default () {
                    return {}
                }
            }, // 流程信息
            flowInfo: {
                type: Object,
                default () {
                    return {}
                }
            },
            // 节点信息
            stateList: {
                type: Array,
                default () {
                    return []
                }
            },
            // 是否仅展示 数据
            isStatic: {
                type: Boolean,
                default () {
                    return false
                }
            }
        },
        data () {
            return {
                renderKey: '',
                formData: {},
                formOptions: {
                    showRequired: true,
                    showGroup: true,
                    showLabel: true,
                    showHook: false,
                    showDesc: true
                },
                fieldList: [],
                checkInfo: {
                    name: '',
                    road: ''
                },
                biz: [
                    {
                        name: this.$t(`m.treeinfo["业务"]`),
                        custom_type: '',
                        source_type: 'custom',
                        value: '--',
                        key: 1
                    }
                ],
                changeInfo: {
                    workflow: '',
                    id: '',
                    key: '',
                    name: '',
                    type: 'STRING',
                    desc: '',
                    layout: 'COL_12',
                    validate_type: 'REQUIRE',
                    choice: [],
                    is_builtin: false,
                    source_type: 'CUSTOM',
                    source_uri: '',
                    regex: 'EMPTY',
                    custom_regex: '',
                    is_tips: false,
                    tips: ''
                },
                sourceTypeList: [
                    {
                        id: 1,
                        key: 'custom',
                        name: this.$t(`m.treeinfo["自定义"]`)
                    },
                    {
                        id: 2,
                        key: 'component_inputs',
                        name: this.$t(`m.treeinfo["引用变量"]`)
                    }
                ],
                sliderInfo: {
                    title: this.$t(`m.treeinfo["添加变量"]`),
                    show: false,
                    width: 700
                },
                showTabData: {}
            }
        },
        computed: {},
        watch: {
            // paramTableData: {
            //     handler (newValue) {
            //         this.paramTableShow = []
            //         this.paramTableShow = this.paramTableShow.concat(this.biz, newValue)
            //         this.paramTableShow.forEach(item => {
            //             item.value = ''
            //             if (item.source_type === 'component_outputs') {
            //                 item.source_type = 'component_inputs'
            //             }
            //         })
            //         if (this.configur.extras
            //             && this.configur.extras.sops_info
            //             && this.configur.extras.sops_info.template_id) {
            //             this.paramTableShow.forEach(
            //                 (item, index) => {
            //                     if (!index && this.configur.extras.sops_info.bk_biz_id) {
            //                         item.source_type = this.configur.extras.sops_info.bk_biz_id['value_type']

            //                         item.value = this.configur.extras.sops_info.bk_biz_id['value']
            //                     } else {
            //                         const current = this.configur.extras.sops_info.constants.filter(
            //                             ite => {
            //                                 return ite.key === item.key
            //                             }
            //                         )[0]
            //                         if (current) {
            //                             item.source_type = current['value_type']
            //                             item.value = current['value']
            //                         }
            //                     }
            //                     if (item.source_type === 'variable') {
            //                         item.source_type = 'component_inputs'
            //                     }
            //                 }
            //             )
            //         }
            //     },
            //     deep: false
            // },
            constants () {
                this.renderKey = new Date().getTime()
            }
        },
        methods: {
            getRenderFormValidate () {
                return this.$refs.renderForm.validate()
            },
            getRelatedFields () {
                this.$parent.getRelatedFields()
            },
            addNewItem (data) {
                this.showTabData = data
                this.sliderInfo.show = true
                this.$refs['selectSops' + data.key].close()
            },
            closeShade () {
                this.sliderInfo.show = false
            },
            showNew (sopsinfo, res) {
                this.paramTableShow.forEach((item) => {
                    if (item.key === sopsinfo.key) {
                        item.value = res.data.key
                    }
                })
            }
        }
    }
</script>

<style lang="scss" scoped>

</style>
