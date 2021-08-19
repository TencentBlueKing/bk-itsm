<template>
    <div class="bk-get-param">
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
            paramTableData: {
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
                paramTableShow: [],
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
            paramTableData: {
                handler (newValue) {
                    this.paramTableShow = []
                    this.paramTableShow = this.paramTableShow.concat(this.biz, newValue)
                    this.paramTableShow.forEach(item => {
                        item.value = ''
                        if (item.source_type === 'component_outputs') {
                            item.source_type = 'component_inputs'
                        }
                    })
                    if (this.configur.extras
                        && this.configur.extras.sops_info
                        && this.configur.extras.sops_info.template_id) {
                        this.paramTableShow.forEach(
                            (item, index) => {
                                if (!index && this.configur.extras.sops_info.bk_biz_id) {
                                    item.source_type = this.configur.extras.sops_info.bk_biz_id['value_type']

                                    item.value = this.configur.extras.sops_info.bk_biz_id['value']
                                } else {
                                    const current = this.configur.extras.sops_info.constants.filter(
                                        ite => {
                                            return ite.key === item.key
                                        }
                                    )[0]
                                    if (current) {
                                        item.source_type = current['value_type']
                                        item.value = current['value']
                                    }
                                }
                                if (item.source_type === 'variable') {
                                    item.source_type = 'component_inputs'
                                }
                            }
                        )
                    }
                },
                deep: false
            },
            constants () {
                this.renderKey = new Date().getTime()
            }
        },
        mounted () {
            this.paramTableShow = this.paramTableShow.concat(this.biz, this.paramTableData)
            if (this.isStatic === true) {
                this.paramTableShow = []
                this.isStaticData.forEach((item) => {
                    const ite = {
                        name: item.name,
                        value: item.value
                    }
                    this.paramTableShow.push(ite)
                })
            }
        },
        methods: {
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
