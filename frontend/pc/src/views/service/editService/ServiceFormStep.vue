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
    <div class="service-form" :class="{ 'hide-field-option': !showFieldOption }">
        <!-- 字段选择 -->
        <div class="field-option" v-show="showFieldOption">
            <bk-tab data-test-id="service_tab_servcieField" :active.sync="active" type="unborder-card" ext-cls="field-tab">
                <bk-tab-panel name="library-fields">
                    <template slot="label">
                        <i class="panel-icon bk-icon icon-apps"></i>
                        <span class="panel-name">{{ $t(`m.tickets['控件库']`) }}</span>
                    </template>
                    <ul class="field-list">
                        <li class="field-item" v-for="(field, index) in fieldsLibrary" :key="index" @click="onAddFormClick(field)">
                            <i class="bk-icon" :class="field.icon"></i><span class="field-name">{{ field.name }}</span>
                        </li>
                    </ul>
                </bk-tab-panel>
                <bk-tab-panel name="public-fields">
                    <template slot="label">
                        <i class="panel-icon bk-icon icon-cog-shape"></i>
                        <span class="panel-name">{{ $t(`m.tickets['已有字段']`) }}</span>
                    </template>
                    <ul class="field-list">
                        <li class="field-item" v-for="(field, index) in publicFields" :key="index" @click="addField(field)">
                            <i class="bk-icon icon-apps"></i><span class="field-name">{{ field.name }}</span>
                        </li>
                    </ul>
                </bk-tab-panel>
            </bk-tab>
        </div>
        <!-- 基础信息 -->
        <div class="basic-body">
            <section data-test-id="servie_section_serviceBasicInformation" class="settion-card basic-info-card">
                <h2 class="card-title">{{ $t(`m.tickets['服务基础信息']`) }}</h2>
                <div class="card-content">
                    <!-- 编辑状态 -->
                    <div v-if="isBasicFormEditting" class="service-basic-form">
                        <bk-form ref="basicForm" form-type="vertical" class="basic-form" :rules="rules" :model="formData">
                            <bk-form-item :label="$t(`m.newCommon['服务名称']`)" :required="true" property="name">
                                <bk-input v-model="formData.name"></bk-input>
                            </bk-form-item>
                            <bk-form-item :label="$t(`m.serviceConfig['服务描述']`)" property="desc">
                                <bk-input v-model="formData.desc" type="textarea" :row="3" :maxlength="100"></bk-input>
                            </bk-form-item>
                            <bk-form-item :label="$t(`m.tickets['所属目录']`)" :required="true" property="catalog_id">
                                <select-tree
                                    v-model="formData.catalog_id"
                                    :list="dirList"
                                    ext-cls="bk-form-width">
                                </select-tree>
                            </bk-form-item>
                            <bk-form-item :label="$t(`m.serviceConfig['服务类型']`)" :required="true" property="key">
                                <bk-select v-model="formData.key"
                                    :placeholder="$t(`m.serviceConfig['请选择服务类型']`)"
                                    :clearable="false"
                                    searchable
                                    :font-size="'medium'">
                                    <bk-option v-for="option in serviceTypeList"
                                        :key="option.key"
                                        :id="option.key"
                                        :name="option.name">
                                    </bk-option>
                                </bk-select>
                            </bk-form-item>
                        </bk-form>
                        <div class="sbmit-buttons">
                            <bk-button ext-cls="button-item"
                                theme="default"
                                :title="$t(`m.treeinfo['取消']`)"
                                :disabled="isSubmitting"
                                @click="onBasicFormCancel()">
                                {{ $t(`m.treeinfo['取消']`) }}
                            </bk-button>
                            <bk-button ext-cls="button-item"
                                theme="primary"
                                :loading="isSubmitting"
                                :title="$t(`m.eventdeploy['确认']`)"
                                @click="onBasicFormSubmit()">
                                {{ $t(`m.eventdeploy['确认']`) }}
                            </bk-button>
                        </div>
                    </div>
                    <!-- 显示状态 -->
                    <div v-else class="service-basic-info">
                        <h2 class="service-title">{{ serviceInfo.name }}<span class="service-dir">({{ catalogDisplayName || '--' }})</span></h2>
                        <p class="service-desc">{{ serviceInfo.desc || '--' }}</p>
                        <div class="mask"></div>
                        <div class="opt-btns">
                            <i class="btn-item bk-itsm-icon icon-itsm-icon-three-four" @click="isBasicFormEditting = true"></i>
                        </div>
                    </div>
                </div>
            </section>
            <section data-test-id="servie_section_serviceticketInformation" class="settion-card create-info-card">
                <h2 class="card-title">
                    <span>{{ $t(`m.tickets['服务提单信息']`) }}</span>
                    <bk-popover
                        placement="bottom-end"
                        ext-cls="create-service-popover"
                        theme="light"
                        :arrow="false"
                        :distance="0"
                        :tippy-options="{
                            hideOnClick: false
                        }"
                        :disabled="!serviceTemplateDisable"
                        :on-show="createServicePopoverShow"
                        :on-hide="createServicePopoverHide">
                        <span class="dropdown-trigger-text">
                            快速创建表单
                            <i :class="['bk-icon icon-angle-down', { 'icon-flip': isDropdownShow }]"></i>
                        </span>
                        <ul class="bk-dropdown-list" slot="content">
                            <li v-for="(way, index) in serviceFormCreateWays.slice(0, 2)"
                                :key="index"
                                data-test-id="servie_section_QuicklyCreateForm"
                                @click="onCreateFormWayCLick(way)">
                                {{ way.name }}
                            </li>
                        </ul>
                    </bk-popover>
                </h2>
                <ul class="create-way" v-if="!showFieldOption">
                    <li class="create-way-item" v-for="way in serviceFormCreateWays" :key="way.key">
                        <i class="bk-icon" :class="way.icon"></i>
                        <p class="create-way-desc">{{ way.name }}</p>
                        <div class="button-tips"
                            v-bk-tooltips.top="{
                                content: $t(`m['请先创建服务后再进行操作']`),
                                boundary: 'window',
                                disabled: serviceTemplateDisable,
                                always: true
                            }">
                            <bk-button
                                data-test-id="service_button_selectServiceForm"
                                :disabled="!serviceTemplateDisable"
                                ext-cls="button-item"
                                theme="default"
                                @click="onCreateFormWayCLick(way)">
                                {{ $t(`m.tickets['选择']`) }}
                            </bk-button>
                        </div>
                    </li>
                </ul>
                <div v-else class="create-service-form" v-bkloading="{ isLoading: formLoading }">
                    <ServiceForm
                        ref="serviceForm"
                        :service-info="serviceInfo"
                        :node-id="createTicketNodeId"
                        :forms="ticketNodeForm"
                        :crt-form.sync="crtForm"
                        @dragUpdateList="dragUpdateList"
                        @cancelAdd="cancelAddField"
                        @fieldClone="fieldClone"
                        @fieldDelete="fieldDelete"
                        @saveField="saveField">
                    </ServiceForm>
                </div>
            </section>
        </div>
        <!-- 选择服务模板 -->
        <choose-service-template-dialog
            :is-show.sync="isShowChooseSerTempDialog"
            :create-info="currCreateFormWay"
            :service-id="serviceId"
            @updateServiceSource="updateServiceSource">
        </choose-service-template-dialog>
    </div>
</template>

<script>
    import { errorHandler } from '../../../utils/errorHandler.js'
    import commonMix from '../../commonMix/common.js'
    import { deepClone } from '../../../utils/util.js'
    import SelectTree from '../../../components/form/selectTree/index.vue'
    import ServiceForm from './ServiceForm.vue'
    import ChooseServiceTemplateDialog from './ChooseServiceTemplateDialog.vue'

    const fieldsLibrary = [
        { name: '单行文本', icon: 'icon-apps', type: 'STRING' },
        { name: '多行文本', icon: 'icon-apps', type: 'TEXT' },
        { name: '数字', icon: 'icon-apps', type: 'INT' },
        { name: '日期', icon: 'icon-apps', type: 'DATE' },
        { name: '时间', icon: 'icon-apps', type: 'DATETIME' },
        { name: '表格', icon: 'icon-apps', type: 'TABLE' },
        { name: '单选下拉框', icon: 'icon-apps', type: 'SELECT' },
        { name: '可输入单选下拉框', icon: 'icon-apps', type: 'INPUTSELECT' },
        { name: '多选下拉框', icon: 'icon-apps', type: 'MULTISELECT' },
        { name: '复选框', icon: 'icon-apps', type: 'CHECKBOX' },
        { name: '单选框', icon: 'icon-apps', type: 'RADIO' },
        { name: '单选人员选择', icon: 'icon-apps', type: 'MEMBER' },
        { name: '多选人员选择', icon: 'icon-apps', type: 'MEMBERS' },
        { name: '富文本', icon: 'icon-apps', type: 'RICHTEXT' },
        { name: '附件上传', icon: 'icon-apps', type: 'FILE' },
        { name: '自定义表格', icon: 'icon-apps', type: 'CUSTOMTABLE' },
        { name: '树形选择', icon: 'icon-apps', type: 'TREESELECT' },
        { name: '链接', icon: 'icon-apps', type: 'LINK' },
        { name: '自定义表单', icon: 'icon-apps', type: 'CUSTOM-FORM' }
    ]
    const serviceFormCreateWays = [
        { name: '选择推荐服务模板', key: 'recom', icon: 'icon-apps' },
        { name: '从已有的服务复制', key: 'created', icon: 'icon-apps' },
        { name: '自定义表单', key: 'custom', icon: 'icon-apps' }
    ]
    export default {
        name: 'ServiceFormStep',
        components: {
            SelectTree,
            ServiceForm,
            ChooseServiceTemplateDialog
        },
        mixins: [commonMix],
        props: {
            type: {
                type: String,
                default: 'new'
            },
            serviceId: {
                type: [String, Number],
                default: ''
            },
            serviceInfo: {
                type: Object,
                default: () => ({})
            },
            createTicketNodeId: Number
        },
        data () {
            return {
                fieldsLibrary,
                serviceFormCreateWays,
                publicFields: [], // 已有字段
                isSubmitting: false,
                isDropdownShow: false,
                showFieldOption: false,
                isBasicFormEditting: true, // 基础信息处于编辑状态
                isShowChooseSerTempDialog: false, // 选择服务模板
                currCreateFormWay: {},
                ticketNodeForm: [], // 提单节点字段列表
                ticketNodeDetail: {}, // 提单节点详情
                formLoading: false,
                detailLoading: false,
                crtForm: '', // 当前编辑的字段
                active: 'library-fields',
                formData: {
                    name: '',
                    desc: '',
                    key: '',
                    catalog_id: ''
                },
                rules: {},
                dirList: [], // 服务目录
                serviceTypeList: [], // 服务类型
                pending: {
                    deleteField: false,
                    saveField: false
                },
                serviceTemplateDisable: false

            }
        },
        computed: {
            catalogDisplayName () {
                return this.serviceInfo.bounded_catalogs ? this.serviceInfo.bounded_catalogs.join('/') : ''
            }
        },
        watch: {
            isBasicFormEditting: {
                handler (val) {
                    if (val) this.getServiceDirectory()
                },
                immediate: true
            }
        },
        created () {
            this.rules.name = this.checkCommonRules('name').name
            this.rules.directory_id = this.checkCommonRules('required').required
            this.rules.key = this.checkCommonRules('required').required
            this.showFieldOption = this.type === 'edit' && !!this.serviceInfo.source
            this.isBasicFormEditting = this.type === 'new'
            this.serviceTemplateDisable = this.serviceId !== ''
        },
        async mounted () {
            this.getPublicFieldList()
            this.getServiceTypes()
            const { name, desc, catalog_id: catalogId, key } = this.serviceInfo
            this.formData.name = name
            this.formData.desc = desc
            this.formData.catalog_id = catalogId
            this.formData.key = key
            if (this.type === 'edit') {
                this.getCreateTicketNodeForm()
                this.getCreateTicketNodeDetail()
            }
        },
        methods: {
            // 获取已有字段（公共字段）
            getPublicFieldList () {
                this.$store.dispatch('publicField/get_template_common_fields', { project_key: this.$store.state.project.id }).then((res) => {
                    this.publicFields = res.data
                }).catch(res => {
                    errorHandler(res, this)
                })
            },
            // 服务类型
            getServiceTypes () {
                this.$store.dispatch('getCustom').then((res) => {
                    this.serviceTypeList = res.data
                }).catch(res => {
                    errorHandler(res, this)
                })
            },
            // 获取提单节点字段
            getCreateTicketNodeForm () {
                this.formLoading = true
                this.$store.dispatch('deployCommon/getFieldList', {
                    workflow: this.serviceInfo.workflow_id,
                    state: this.createTicketNodeId
                }).then(res => {
                    res.data.forEach(item => {
                        item.checkValue = false
                        item.val = item.hasOwnProperty('default') ? deepClone(item.default) : ''
                        item.showFeild = true
                    })
                    this.ticketNodeForm = res.data
                }).catch((res) => {
                    errorHandler(res, this)
                }).finally(() => {
                    this.formLoading = false
                })
            },
            // 获取提单节点详情
            getCreateTicketNodeDetail () {
                this.detailLoading = true
                this.$store.dispatch('deployCommon/getOneStateInfo', {
                    id: this.createTicketNodeId
                }).then(res => {
                    this.ticketNodeDetail = res.data
                }).finally(() => {
                    this.detailLoading = false
                })
            },
            onBasicFormSubmit () {
                if (this.isSubmitting) {
                    return
                }
                this.$refs.basicForm.validate().then(async () => {
                    const params = JSON.parse(JSON.stringify(this.formData))
                    params.id = this.serviceId || undefined
                    params.project_key = this.$store.state.project.id
                    this.isSubmitting = true
                    if (this.type === 'edit') {
                        await this.updateServiceInfo(params)
                    } else {
                        await this.createService(params)
                    }
                    this.isSubmitting = false
                })
            },
            onBasicFormCancel () {
                if (this.type === 'new') {
                    this.$bkInfo({
                        type: 'warning',
                        title: this.$t(`m.slaContent["确认返回？"]`),
                        confirmFn: () => {
                            this.goBackToServiceList()
                        }
                    })
                } else {
                    this.isBasicFormEditting = false
                }
            },
            goBackToServiceList () {
                this.$router.push({
                    name: 'projectServiceList',
                    query: {
                        project_id: this.$store.state.project.id
                    }
                })
            },
            // 创建服务
            createService (params) {
                this.$store.dispatch('serviceEntry/createService', params).then(res => {
                    this.$bkMessage({
                        message: this.$t(`m.deployPage["保存成功"]`),
                        theme: 'success'
                    })
                    this.$router.push({
                        name: 'projectServiceEdit',
                        params: {
                            type: 'edit',
                            step: 'basic'
                        },
                        query: {
                            serviceId: res.data.id,
                            project_id: this.$store.state.project.id
                        }
                    })
                    this.isBasicFormEditting = false
                }).catch(res => {
                    errorHandler(res, this)
                })
            },
            // 修改服务
            updateServiceInfo (params) {
                this.$store.dispatch('serviceEntry/updateService', params).then(res => {
                    this.$bkMessage({
                        message: this.$t(`m.serviceConfig["修改成功"]`),
                        theme: 'success'
                    })
                    this.isBasicFormEditting = false
                    this.$emit('updateServiceInfo', res.data)
                }).catch(res => {
                    errorHandler(res, this)
                })
            },
            // 关联目录树组件
            async getServiceDirectory () {
                await this.$store.dispatch('serviceCatalog/getTreeData', {
                    show_deleted: true,
                    project_key: this.$store.state.project.id
                }).then(res => {
                    this.dirList = (res.data[0] && res.data[0].children) ? res.data[0].children : res.data
                }).catch(res => {
                    errorHandler(res, this)
                })
            },
            async onCreateFormWayCLick (way) {
                if (this.isBasicFormEditting) {
                    try {
                        await this.$refs.basicForm.validate()
                    } catch (error) {
                        return console.warn(error)
                    }
                }
                const key = way.key
                if (key === 'recom' || key === 'created') {
                    this.isShowChooseSerTempDialog = true
                    this.currCreateFormWay = way
                } else {
                    this.updateServiceSource('custom')
                }
                this.showFieldOption = true
            },
            createServicePopoverShow () {
                this.isDropdownShow = true
            },
            createServicePopoverHide () {
                this.isDropdownShow = false
            },
            // 更新原字段列表顺序
            dragUpdateList (targetIndex, field) {
                const index = this.ticketNodeForm.findIndex(item => item.id === field.id)
                this.ticketNodeForm.splice(index, 1)
                this.ticketNodeForm.splice(targetIndex, 0, field)
                if (field.layout === 'COL_6') { // 如果拖动表单存在半行位置字段，则需要保存更新后的位置信息
                    this.saveHalfRowDragPos(field)
                }
            },
            // 点击字段控件
            onAddFormClick (val) {
                const field = {
                    workflow: '',
                    id: '',
                    key: '',
                    name: '',
                    type: val.type,
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
                    tips: '',
                    meta: {},
                    default: ''
                }
                this.addField(field)
            },
            // 添加字段
            addField (field) {
                if (this.crtForm !== '') {
                    return
                }
                const form = Object.assign(deepClone(field), { id: 'add' })
                this.ticketNodeForm.push(form)
                this.crtForm = 'add'
            },
            // 取消添加字段
            cancelAddField () {
                const index = this.ticketNodeForm.findIndex(item => item.id === 'add')
                this.ticketNodeForm.splice(index, 1)
                this.crtForm = ''
            },
            // 字段克隆
            fieldClone (form) {
                const index = this.ticketNodeForm.findIndex(item => item.id === form.id)
                const clonedForm = Object.assign(deepClone(form), { id: 'add' })
                this.ticketNodeForm.splice(index + 1, 0, clonedForm)
                this.crtForm = 'add'
            },
            fieldDelete (form) {
                this.$bkInfo({
                    type: 'warning',
                    title: this.$t(`m.treeinfo["确认删除此字段？"]`),
                    subTitle: this.$t(`m.treeinfo["字段一旦删除，此字段将不在可用。请谨慎操作。"]`),
                    confirmFn: () => {
                        if (this.pending.deleteField) {
                            return
                        }
                        this.pending.deleteField = true

                        const data = {
                            id: form.id,
                            params: {
                                state_id: this.createTicketNodeId
                            }
                        }
                        this.$store.dispatch('deployCommon/deleteField', data).then((res) => {
                            this.$bkMessage({
                                message: this.$t(`m.systemConfig["删除成功"]`),
                                theme: 'success'
                            })
                            const index = this.ticketNodeForm.findIndex(item => item.id === form.id)
                            this.ticketNodeForm.splice(index, 1)
                        }).catch((res) => {
                            errorHandler(res, this)
                        }).finally(() => {
                            this.pending.deleteField = false
                        })
                    }
                })
            },
            // 保存字段
            saveField (field) {
                const index = this.ticketNodeForm.findIndex(item => item.id === field.id)
                field.checkValue = false
                field.showFeild = true
                field.val = field.hasOwnProperty('default') ? deepClone(field.default) : ''
                if (index > -1) { // 编辑
                    this.ticketNodeForm.splice(index, 1, field)
                } else { // 新增
                    this.ticketNodeForm.splice(-1, 1, field)
                }
                this.crtForm = ''
            },
            // 保存字段半行拖拽后的位置
            saveHalfRowDragPos (field) {
                const url = field.source === 'TABLE' ? 'cdeploy/changeNewModuleField' : 'cdeploy/changeNewField'
                this.$store.dispatch(url, { params: field, id: field.id })
            },
            /**
             * 记录服务表单创建来源
             */
            updateServiceSource (source) {
                this.getCreateTicketNodeForm() // 刷新列表
                this.$store.dispatch('service/updateServiceSource', {
                    id: this.serviceId,
                    params: {
                        source
                    }
                }).then(() => {
                    this.serviceInfo.source = source
                }).catch(res => {
                    errorHandler(res, this)
                })
            },
            // 校验当前步骤
            async validate () {
                if (this.isBasicFormEditting) {
                    await this.$refs.basicForm.validate()
                }
                if (!this.showFieldOption) {
                    this.$bkMessage({
                        message: '请选择服务提单信息创建方式',
                        theme: 'error'
                    })
                    return { data: { result: false } }
                }
                if (!this.formLoading && !this.detailLoading && this.$refs.serviceForm) {
                    // 用全量节点详情字段，传到后台接口，会抛出节点 desc 字段不能为空校验失败信息
                    const {
                        assignors, assignors_type, can_deliver, delivers, delivers_type, distribute_type, extras,
                        is_draft, is_terminable, name, processors, processors_type, tag, type, workflow
                    } = this.ticketNodeDetail
                    const fields = this.ticketNodeForm.filter(item => typeof item.id === 'number').map(item => item.id)
                    const nodeDetail = {
                        assignors,
                        assignors_type,
                        can_deliver,
                        delivers,
                        delivers_type,
                        distribute_type,
                        extras,
                        is_draft,
                        is_terminable,
                        name,
                        processors,
                        processors_type,
                        tag,
                        type,
                        workflow,
                        fields
                    }
                    return this.$store.dispatch('deployCommon/updateNode', {
                        params: nodeDetail,
                        id: this.createTicketNodeId
                    }).then(res => {
                        this.$bkMessage({
                            message: this.$t(`m.treeinfo["保存成功"]`),
                            theme: 'success'
                        })
                    }, (res) => {
                        errorHandler(res, this)
                        return Promise.reject(res)
                    })
                }
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '~@/scss/mixins/scroller.scss';
@import '~@/scss/mixins/ellipsis.scss';
.field-tab {
    /deep/ .bk-tab-label-wrapper {
        display: flex;
        justify-content: center;
    }
    /deep/ .bk-tab-section {
        position: relative;
        padding: 0;
        height: calc(100vh - 268px);
        overflow: auto;
        @include scroller;
    }
}
.dropdown-trigger-text {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    color: #737987;
    font-weight: normal;
    cursor: pointer;
}
.dropdown-trigger-text .bk-icon {
    font-size: 22px;
}
.bk-dropdown-list {
    width: 120px;
    background: #ffffff;
    border: 1px solid #dcdee5;
    border-radius: 2px;
    > li {
        padding: 0 10px;
        width: 100%;
        height: 32px;
        line-height: 32px;
        font-size: 12px;
        color: #63656e;
        @include ellipsis(100%);
        cursor: pointer;
        font-weight: normal;
        &:hover {
            color: #3A84FF;
            background: #f4f6fa;
        }
    }
}
.service-form {
    height: 100%;
    &.hide-field-option {
        .basic-body {
            width: 100%;
        }
    }
    .field-option {
        float: left;
        width: 272px;
        background: #fcfcfc;
        border-right: 1px solid #dde4eb;
        border-top: 1px solid #dde4eb;
    }
    .basic-body {
        float: left;
        padding: 15px;
        width: calc(100% - 272px);
        height: calc(100vh - 225px);
        overflow: auto;
        @include scroller;
    }
}
.field-list {
    padding: 10px 12px;
    .field-item {
        margin-top: 4px;
        padding: 0 10px;
        width: 100%;
        height: 32px;
        line-height: 32px;
        background: #ffffff;
        border: 1px solid #e0e0e0;
        color: #63656e;
        font-size: 12px;
        cursor: pointer;
        .bk-icon {
            font-size: 14px;
        }
        .field-name {
            margin-left: 9px;
        }
    }
}
.settion-card {
    margin: auto;
    max-width: 1000px;
    .card-title {
        margin: 0;
        font-size: 14px;
        font-weight: 700;
        color: #63656e;
    }
    .card-content {
        margin-top: 16px;
        background: #ffffff;
        border-radius: 2px;
        box-shadow: 0px 2px 6px 0px rgba(6,6,6,0.10);
        overflow: hidden;
    }
}
.basic-info-card {
    .basic-form {
        margin: auto;
        width: 600px;
    }
    .card-content {
        padding-bottom: 0;
    }
    .sbmit-buttons {
        margin-top: 60px;
        padding: 7px 0;
        display: flex;
        justify-content: flex-end;
        box-shadow: 0px -1px 0px 0px #dde4eb;
        .button-item {
            margin-left: 5px;
        }
    }
    .service-basic-form {
        padding: 32px 20px;
        padding-bottom: 0;
    }
    .service-basic-info {
        padding: 32px 20px;
        position: relative;
        padding-bottom: 31px;
        &:hover {
            background: #fcfcfc;
            .mask {
                display: block;
            }
            .opt-btns {
                right: 0;
            }
        }
        .mask {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            display: block;
            z-index: 1;
        }
        .opt-btns {
            display: flex;
            align-items: center;
            justify-content: center;
            position: absolute;
            right: -32px;
            top: 0;
            width: 32px;
            height: 100%;
            z-index: 2;
            border-left: 1px solid #dde4eb;
            text-align: center;
            transition: right .3s;
            .btn-item {
                margin-top: 8px;
                display: inline-block;
                color: #979ba5;
                cursor: pointer;
                &:hover {
                    color: #63656E;
                }
            }
        }
        .service-title {
            font-size: 16px;
            font-weight: 700;
            color: #313238;
            line-height: 21px;
        }
        .service-dir, .service-desc {
            font-size: 12px;
            color: #737987;
            line-height: 16px;
        }
        .service-dir {
            margin-left: 8px;
            display: inline-block;
        }
    }
}
// 提单信息
.create-info-card {
    margin-top: 32px;
    .card-title {
        display: flex;
        justify-content: space-between;
    }
    .create-way {
        margin-top: 16px;
        display: flex;
        height: 348px;
        border: 1px dashed #dde4eb;
        background: #fcfcfc;
        .create-way-item {
            flex: 1;
            height: 100%;
            display: inline-block;
            text-align: center;
            &:not(:first-child) {
                border-left: 1px dashed #dde4eb;
            }
            .bk-icon {
                display: block;
                margin-top: 96px;
                font-size: 60px;
                color: #dde4eb;
            }
            .create-way-desc {
                margin-top: 50px;
                font-size: 14px;
                color: #737987;
            }
            .button-tips {
                .button-item {
                    margin-top: 25px;
                }
            }
        }
    }
}
</style>
<style lang="scss">
    .create-service-popover {
        .tippy-tooltip {
            padding: 0;
        }
    }
</style>
