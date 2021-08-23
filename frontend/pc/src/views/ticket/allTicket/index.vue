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
    <div class="all-ticket-page" v-bkloading="{ isLoading: loading }">
        <template v-if="!loading">
            <div class="ticket-tab">
                <nav-title :title-name="titleName">
                    <bk-tab :active.sync="currentTab" type="unborder-card" @tab-change="changeTag" slot="tab">
                        <bk-tab-panel
                            v-for="(panel) in serviceList"
                            v-bind="panel"
                            :key="panel.key">
                            <template slot="label">
                                <div class="list-wrapper">
                                    <span>{{ panel.name }}</span>
                                    <span class="ticket-file-count">{{ counts[panel.key] }}</span>
                                </div>
                            </template>
                            <div class="ticket-content" v-if="sereveType === panel.key">
                                <div class="operate-wrapper">
                                    <advanced-search
                                        class="advanced-search"
                                        ref="advancedSearch"
                                        :forms="searchForms"
                                        @search="handleSearch"
                                        @onChangeHihtLight="onChangeHihtLight"
                                        @formChange="handleSearchFormChange"
                                        @clear="handleClearSearch">
                                        <div class="slot-content">
                                            <bk-button
                                                class="export"
                                                :title="$t(`m.tickets['导出']`)"
                                                @click="openExportList">
                                                {{ $t('m.tickets["导出"]') }}</bk-button>
                                            <!-- <div class="checkbox-wapper">
                                                <span><bk-checkbox @change="onWarnTicketChange">{{ $t(`m.tickets['预警单据']`) }}</bk-checkbox></span>
                                                <span><bk-checkbox @change="onTimeoutTicketChange">{{ $t(`m.tickets['超时单据']`) }}</bk-checkbox></span>
                                            </div> -->
                                        </div>
                                    </advanced-search>
                                </div>
                                <div class="table-wrapper">
                                    <table-content
                                        v-bkloading="{ isLoading: tableLoading }"
                                        :data-list="dataList"
                                        :pagination="pagination"
                                        :color-hex-list="colorHexList"
                                        :sereve-type="sereveType"
                                        @submitSuccess="evaluationSubmitSuccess"
                                        @orderingClick="orderingClick"
                                        @handlePageLimitChange="handlePageLimitChange"
                                        @handlePageChange="handlePageChange">
                                    </table-content>
                                </div>
                            </div>
                        </bk-tab-panel>
                    </bk-tab>
                </nav-title>
            </div>
        </template>
       
        <!-- 导出 -->
        <export-ticket-dialog
            :is-show="isExportDialogShow"
            :pagination="pagination"
            :view-type="''"
            :search-params="searchParams"
            @close="isExportDialogShow = false">
        </export-ticket-dialog>
    </div>
</template>
<script>
    import NavTitle from '@/components/common/layout/NavTitle'
    import AdvancedSearch from '@/components/form/advancedSearch/NewAdvancedSearch'
    import TableContent from './tableContent'
    import ExportTicketDialog from '@/components/ticket/ExportTicketDialog.vue'
    import { errorHandler } from '../../../utils/errorHandler'
    import ticketListMixins from '@/mixins/ticketList.js'

    export default {
        name: 'AllTicket',
        components: {
            NavTitle,
            AdvancedSearch,
            TableContent,
            ExportTicketDialog
        },
        mixins: [ticketListMixins],
        props: {
            projectId: String,
            from: String
        },
        data () {
            const SEARCH_FORM = [
                {
                    name: this.$t(`m.tickets['单号/标题']`),
                    desc: this.$t(`m.tickets['单号/标题']`),
                    type: 'input',
                    key: 'keyword',
                    display: true,
                    value: '',
                    list: [],
                    placeholder: this.$t('m.tickets["请选择单号/标题"]')
                },
                {
                    name: this.$t('m.tickets["服务目录"]'),
                    type: 'cascade',
                    key: 'catalog_id',
                    multiSelect: true,
                    display: true,
                    value: [],
                    list: [],
                    placeholder: this.$t('m.tickets["请选择服务目录"]')
                },
                {
                    name: this.$t('m.tickets["服务"]'),
                    type: 'select',
                    key: 'service_id__in',
                    multiSelect: true,
                    display: false,
                    value: [],
                    list: [],
                    placeholder: this.$t('m.tickets["请选择服务"]')
                },
                {
                    name: this.$t('m.tickets["提单人"]'),
                    type: 'member',
                    key: 'creator__in',
                    multiSelect: true,
                    display: true,
                    value: [],
                    list: [],
                    placeholder: this.$t('m.tickets["请选择提单人"]')
                },
                {
                    name: this.$t('m.tickets["处理人"]'),
                    type: 'member',
                    key: 'current_processor',
                    multiSelect: true,
                    display: true,
                    value: [],
                    list: [],
                    placeholder: this.$t('m.tickets["请选择处理人"]')
                },
                {
                    name: this.$t('m.tickets["状态"]'),
                    type: 'select',
                    key: 'current_status__in',
                    multiSelect: true,
                    display: true,
                    value: [],
                    list: [],
                    placeholder: this.$t('m.tickets["请选择状态"]')
                },
                {
                    name: this.$t(`m.tickets["提单时间"]`),
                    key: 'date_update',
                    type: 'datetime',
                    display: true,
                    value: [],
                    list: [],
                    placeholder: this.$t('m.tickets["请选择提单时间"]')
                },
                {
                    name: this.$t(`m.tickets["业务"]`),
                    key: 'bk_biz_id',
                    type: 'select',
                    display: true,
                    value: '',
                    list: [],
                    placeholder: this.$t('m.tickets["请选择业务"]')
                }
            ]
            return {
                isExportDialogShow: false,
                loading: true,
                isTabLoading: false,
                titleName: this.$t('m.managePage["所有单据"]'),
                serviceList: [], // 所有单据列表
                currentTab: '', // 当前选择tab
                counts: {},
                // 当前选择服务
                sereveType: '',
                requestList: [],
                changeList: [],
                eventList: [],
                questionList: [],
                requestLoading: false,
                changeLoading: false,
                eventLoading: false,
                questionLoading: false,
                pagination: {
                    current: 1,
                    count: 10,
                    limit: 10
                },
                // 状态颜色配置list
                colorHexList: [],
                // 查询
                searchForms: SEARCH_FORM.slice(0),
                searchParams: {}, // 高级搜索内容
                orderKey: '-create_at' // 排序
            }
        },
        computed: {
            tableLoading () {
                return this[`${this.sereveType}Loading`]
            },
            dataList () {
                return this[`${this.sereveType}List`]
            }
        },
        created () {
            this.initData()
        },
        methods: {
            async initData () {
                this.loading = true
                // 获取所有服务类型列表
                await this.getServiceTypeList()
                // 获取所有tab的单据列表
                this.getAllTabTicketList()
                // 获取状态颜色接口
                this.getTypeStatus()
                // 查询服务目录级联数据
                this.getServiceTree()
                // 获取全局视图状态
                this.getGlobalStatus()
                this.getBusinessList()
            },
            // 获取所有服务类型列表
            async getServiceTypeList () {
                this.isTabLoading = true
                return this.$store.dispatch('getCustom').then(res => {
                    if (res.result) {
                        this.serviceList = res.data
                        this.serviceList.forEach(item => {
                            item.label = item.name
                            this.$set(this.counts, item.key, 0)
                        })
                        this.sereveType = this.serviceList[0].key
                        this.currentTab = this.serviceList[0].name
                    }
                }).catch((res) => {
                    this.$bkMessage({
                        message: res.data.msg,
                        theme: 'error'
                    })
                }).finally(() => {
                    this.isTabLoading = false
                })
            },
            // 获取所有单据列表
            getAllTicketList (type = this.sereveType) {
                this[`${type}Loading`] = true
                const fixParams = {
                    page_size: this.pagination.limit,
                    page: this.pagination.current,
                    ordering: this.orderKey,
                    is_draft: 0,
                    view_type: '',
                    service_type: type
                }
                // 项目下的所有单据
                if (this.projectId) {
                    fixParams.project_key = this.projectId
                }

                const searchParams = JSON.stringify(this.searchParams) === '{}'
                    ? { service_id__in: this.$route.query.service_id } // 没有参数时默认将 url 参数作为查询参数
                    : this.searchParams
                Object.assign(fixParams, searchParams)
                return this.$store.dispatch('change/getList', fixParams).then(res => {
                    this[`${type}List`] = res.data.items
                    // 异步加载列表中的某些字段信息
                    this.__asyncReplaceTicketListAttr(this[`${type}List`])
                    this.$set(this.counts, type, res.data.count)
                    // 分页
                    this.pagination.current = res.data.page
                    if (this.sereveType === type) {
                        this.pagination.count = res.data.count
                    }
                }).catch((res) => {
                    this.$bkMessage({
                        message: res.data.msg,
                        theme: 'error'
                    })
                }).finally(() => {
                    this[`${type}Loading`] = false
                })
            },
            // 获取所有tab的单据列表
            getAllTabTicketList () {
                this.loading = true
                const tableList = this.serviceList.map(item => {
                    return this.getAllTicketList(item.key)
                })
                Promise.all(tableList).then(data => {
                    this.loading = false
                })
            },
            // 查询级联数据
            getServiceTree () {
                const params = {
                    key: this.sereveType,
                    show_deleted: true
                }
                if (this.projectId) {
                    params.project_key = this.projectId
                }
                this.$store.dispatch('serviceCatalog/getTreeData', params).then(res => {
                    const formItem = this.searchForms.find(item => item.key === 'catalog_id')
                    formItem.list = res.data[0] ? res.data[0]['children'] : []
                }).catch((res) => {
                    this.$bkMessage({
                        message: res.data.msg,
                        theme: 'error'
                    })
                })
            },
            // 获取单据状态
            getGlobalStatus () {
                const params = {
                    source_uri: 'ticket_status'
                }
                this.$store.dispatch('ticketStatus/getOverallTicketStatuses', params).then((res) => {
                    const formItem = this.searchForms.find(item => item.key === 'current_status__in')
                    formItem.list = res.data
                }).catch(res => {
                    this.$bkMessage({
                        message: res.data.msg,
                        theme: 'error'
                    })
                })
            },
            // 获取服务数据
            getServiceData (val) {
                const params = {
                    catalog_id: val,
                    service_key: this.sereveType,
                    is_valid: 1
                }
                if (this.projectId) {
                    params.project_key = this.projectId
                }
                this.$store.dispatch('catalogService/getServices', params).then((res) => {
                    const formItem = this.searchForms.find(item => item.key === 'service_id__in')
                    formItem.list = []
                    res.data.forEach(item => {
                        formItem.list.push({
                            key: item.id,
                            name: item.name
                        })
                    })
                }).catch((res) => {
                    this.$bkMessage({
                        message: res.data.msg,
                        theme: 'error'
                    })
                }).finally(() => {

                })
            },
            // 获取状态颜色接口
            getTypeStatus () {
                const params = {}
                const type = this.sereveType
                this.$store.dispatch('ticketStatus/getTypeStatus', { type, params }).then(res => {
                    this.colorHexList = res.data
                }).catch(res => {
                    errorHandler(res, this)
                })
            },
            getBusinessList () {
                this.$store.dispatch('eventType/getAppList').then((res) => {
                    this.searchForms.find(item => item.key === 'bk_biz_id').list = res.data
                }).catch(res => {
                    errorHandler(res, this)
                })
            },
            // 切换不同的标签卡
            changeTag (val) {
                this.pagination.limit = 10
                this.pagination.current = 1
                this.searchParams = {}
                this.orderKey = '-create_at'
                this.searchForms.forEach(item => {
                    item.value = item.multiSelect ? [] : ''
                })
                const service = this.serviceList.find(item => item.name === val)
                this.sereveType = service.key
                this.getServiceTree()
                this.getAllTicketList(service.key)
            },
            // 导出弹框
            openExportList () {
                this.isExportDialogShow = true
            },
            // 预警单据变化
            // onWarnTicketChange (val) {
            // },
            // 超时单据变化
            // onTimeoutTicketChange (val) {
            // },
            // 查询
            handleSearch (params) {
                this.pagination.limit = 10
                this.pagination.current = 1
                this.searchParams = params
                this.getAllTicketList(this.sereveType)
            },
            // 清空搜索表单
            handleClearSearch () {
                this.searchForms.forEach(item => {
                    if (item.key === 'service_id__in') {
                        item.display = false
                    }
                })
            },
            // 展开高级搜索
            handleSearchFormChange (key, val) {
                if (key === 'catalog_id') {
                    const formItem = this.searchForms.find(item => item.key === 'service_id__in')
                    formItem.display = val.length
                    if (val.length) {
                        const serviceCatalogId = val[val.length - 1].id
                        // 当服务目录的数据发生变化时，清空服务数据
                        formItem.value = []
                        this.getServiceData(serviceCatalogId)
                    }
                }
            },
            onChangeHihtLight (val) {
                this.getAllTicketList()
            },
            // 分页过滤数据
            handlePageLimitChange (limit) {
                this.pagination.current = 1
                this.pagination.limit = limit
                this.getAllTicketList()
            },
            handlePageChange (page) {
                this.pagination.current = page
                this.getAllTicketList()
            },
            // 排序
            orderingClick (order) {
                this.orderKey = order
                this.getAllTicketList(this.sereveType)
            },
            // 评价成功回调
            evaluationSubmitSuccess (val) {
                this.getAllTicketList()
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '~@/scss/mixins/scroller.scss';
    .all-ticket-page {
        height: 100%;
        background: #fafbfd;
        /deep/ .bk-tab-section {
            padding: 0;
            background-color: #f5f7fa;
        }
        .bk-tab-label-item {
            .list-wrapper {
                display: flex;
                align-items: center;
                position: relative;
                .ticket-file-count {
                    display: inline-block;
                    vertical-align: middle;
                    margin: 0 3px;
                    min-width: 24px;
                    height: 16px;
                    padding: 0 4px ;
                    line-height: 16px;
                    border-radius: 8px;
                    text-align: center;
                    font-style: normal;
                    font-size: 12px;
                    font-weight: bold;
                    font-family: Helvetica, Arial;
                    color: #979ba5;
                    background-color: #f0f1f5;
                }
            }
            &.active,
            &:hover {
                .ticket-file-count {
                    background: #e1ecff;
                    color: #3a84ff;
                }
            }
        }
        /deep/ .bk-tab-label-wrapper {
            box-shadow: 0px 2px 2px 0px rgba(0,0,0,0.1);
        }
        .ticket-content {
            padding: 14px 18px 15px 22px;
            height: calc(100vh - 146px);
            overflow: auto;
            @include scroller;
            .operate-wrapper {
                margin-bottom: 14px;
                .slot-content {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    .checkbox-wapper {
                        display: flex;
                        align-items: center;
                    }
                    .export {
                        width: 86px;
                    }
                    .bk-form-checkbox {
                        width: 78px;
                        margin-right: 21px;
                    }
                }
            }
        }
    }
</style>
