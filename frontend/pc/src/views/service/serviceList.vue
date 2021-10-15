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
    <div>
        <nav-title :title-name="$t(`m.serviceConfig['服务']`)"></nav-title>
        <div class="page-content">
            <!-- btn -->
            <div class="bk-only-btn">
                <div class="bk-more-search">
                    <bk-button
                        data-test-id="service_button_createService"
                        v-cursor="{ active: !hasPermission(['service_create'], $store.state.project.projectAuthActions) }"
                        :theme="'primary'"
                        icon="plus"
                        :class="['mr10', 'plus-cus', {
                            'btn-permission-disable': !hasPermission(['service_create'], $store.state.project.projectAuthActions)
                        }]"
                        :title="$t(`m.serviceConfig['新增']`)"
                        @click="onServiceCreatePermissonCheck">
                        {{$t(`m.serviceConfig['新增']`)}}
                    </bk-button>
                    <bk-button :theme="'default'"
                        data-test-id="service_button_batchDeleteService"
                        :title="$t(`m.serviceConfig['批量删除']`)"
                        :disabled="!checkList.length"
                        @click="deleteCheck">
                        {{$t(`m.serviceConfig['批量删除']`)}}
                    </bk-button>
                    <div class="bk-search-name">
                        <div class="bk-search-content">
                            <bk-input
                                :placeholder="moreSearch[0].placeholder || $t(`m.serviceConfig['请输入服务名']`)"
                                :clearable="true"
                                :right-icon="'bk-icon icon-search'"
                                v-model="moreSearch[0].value"
                                @enter="searchContent"
                                @clear="clearSearch">
                            </bk-input>
                        </div>
                        <bk-button :title="$t(`m.deployPage['更多筛选条件']`)"
                            icon=" bk-itsm-icon icon-search-more"
                            class="ml10 filter-btn"
                            @click="searchMore">
                        </bk-button>
                    </div>
                </div>
                <search-info
                    ref="searchInfo"
                    :more-search="moreSearch">
                </search-info>
            </div>
            <bk-table
                ref="serviceTable"
                v-bkloading="{ isLoading: isDataLoading }"
                :data="dataList"
                :size="'small'"
                :pagination="pagination"
                @page-change="handlePageChange"
                @page-limit-change="handlePageLimitChange"
                @select-all="handleSelectAll"
                @select="handleSelect">
                <bk-table-column
                    type="selection"
                    width="60"
                    align="center"
                    :selectable="disabledFn">
                    <template slot-scope="props">
                        <template v-if="!hasPermission(['service_manage'], [...$store.state.project.projectAuthActions, ...props.row.auth_actions])">
                            <div style="height: 100%; display: flex; justify-content: center; align-items: center;">
                                <span
                                    v-cursor
                                    class="checkbox-permission-disable"
                                    @click="onServicePermissonCheck(['service_manage'], props.row)">
                                </span>
                            </div>
                        </template>
                        <template v-else>
                            <bk-checkbox
                                data-test-id="service_checkbox_checkService"
                                v-bk-tooltips.right="{
                                    content: $t(`m.serviceConfig['服务已绑定关联目录，请先解绑后在进行删除操作']`),
                                    disabled: !props.row.bounded_catalogs[0],
                                    boundary: 'window',
                                    always: true
                                }"
                                :true-value="trueStatus"
                                :false-value="falseStatus"
                                :disabled="!!props.row.bounded_catalogs[0]"
                                v-model="props.row.checkStatus"
                                @change="changeCheck(props.row)">
                            </bk-checkbox>
                        </template>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.common['ID']`)" min-width="60">
                    <template slot-scope="props">
                        <span :title="props.row.id">{{ props.row.id || '--' }}</span>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.serviceConfig['服务名称']`)" prop="name" min-width="150">
                    <template slot-scope="props">
                        <span
                            v-if="!hasPermission(['service_manage'], [...$store.state.project.projectAuthActions, ...props.row.auth_actions])"
                            v-cursor
                            class="bk-lable-primary text-permission-disable"
                            ::title="props.row.name"
                            @click="onServicePermissonCheck(['service_manage'], props.row)">
                            {{ props.row.name }}
                        </span>
                        <span
                            v-else
                            class="bk-lable-primary"
                            :title="props.row.name"
                            @click="changeEntry(props.row, 'edit')">
                            {{ props.row.name }}
                        </span>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.serviceConfig['服务说明']`)" width="200">
                    <template slot-scope="props">
                        <span :title="props.row.desc">{{ props.row.desc || '--' }}</span>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.serviceConfig['类型']`)">
                    <template slot-scope="props">
                        <template v-for="(type, typeIndex) in serviceTypesMap">
                            <span v-if="props.row.key === type.key"
                                :title="type.name"
                                :key="typeIndex">
                                {{ type.name }}
                            </span>
                        </template>
                    </template>
                </bk-table-column>
                <!-- <bk-table-column :label="$t(`m.serviceConfig['关联流程']`)" min-width="200">
                    <template slot-scope="props">
                        <span class="bk-lable-primary"
                            @click="processShow(props.row)"
                            :title="props.row.workflow_name + '(' + props.row.version_number + ')'">
                            {{ props.row.workflow_name }} ({{ props.row.version_number }})
                        </span>
                    </template>
                </bk-table-column> -->
                <bk-table-column :label="$t(`m.serviceConfig['关联目录']`)">
                    <template slot-scope="props">
                        <span :title="props.row.bounded_catalogs[0]">{{ props.row.bounded_catalogs[0] || '--' }}</span>
                    </template>
                </bk-table-column>

                <bk-table-column :label="$t(`m.common['创建人']`)">
                    <template slot-scope="props">
                        <span :title="props.row.creator">{{props.row.creator || '--'}}</span>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.common['更新人']`)">
                    <template slot-scope="props">
                        <span :title="props.row.updated_by">{{props.row.updated_by || '--'}}</span>
                    </template>
                </bk-table-column>

                <bk-table-column :label="$t(`m.serviceConfig['更新时间']`)" min-width="150">
                    <template slot-scope="props">
                        <span :title="props.row.update_at">{{ props.row.update_at || '--' }}</span>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.serviceConfig['状态']`)" width="80">
                    <template slot-scope="props">
                        <span class="bk-status-color"
                            :class="{ 'bk-status-gray': !props.row.is_valid }"></span>
                        <span style="margin-left: 5px;"
                            :title="props.row.is_valid ? $t(`m.serviceConfig['启用']`) : $t(`m.serviceConfig['关闭']`)">
                            {{(props.row.is_valid ? $t(`m.serviceConfig["启用"]`) : $t(`m.serviceConfig["关闭"]`))}}
                        </span>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.serviceConfig['操作']`)" width="160">
                    <template slot-scope="props">
                        <!-- sla -->
                        <bk-button
                            v-if="!hasPermission(['service_manage'], [...props.row.auth_actions, ...$store.state.project.projectAuthActions])"
                            v-cursor
                            text
                            theme="primary"
                            class="btn-permission-disable"
                            @click="onServicePermissonCheck(['service_manage'], props.row)">
                            SLA
                        </bk-button>
                        <router-link v-else data-test-id="service_link_linkToSLA" class="bk-button-text bk-primary" :to="{ name: 'projectServiceSla', params: { id: props.row.id }, query: { project_id: $store.state.project.id } }">SLA</router-link>
                        <!-- 编辑 -->
                        <bk-button
                            v-if="!hasPermission(['service_manage'], [...props.row.auth_actions, ...$store.state.project.projectAuthActions])"
                            v-cursor
                            text
                            theme="primary"
                            class="btn-permission-disable"
                            @click="onServicePermissonCheck(['service_manage'], props.row)">
                            {{ $t('m.serviceConfig["编辑"]') }}
                        </bk-button>
                        <bk-button
                            v-else
                            data-test-id="service_button_editService"
                            theme="primary"
                            text
                            @click="changeEntry(props.row, 'edit')">
                            {{ $t('m.serviceConfig["编辑"]') }}
                        </bk-button>
                        <!-- 删除 -->
                        <bk-button
                            v-if="!hasPermission(['service_manage'], [...props.row.auth_actions, ...$store.state.project.projectAuthActions])"
                            v-cursor
                            text
                            theme="primary"
                            class="btn-permission-disable"
                            @click="onServicePermissonCheck(['service_manage'], props.row)">
                            {{ $t('m.serviceConfig["删除"]') }}
                        </bk-button>
                        <template v-else-if="!!props.row.bounded_catalogs[0]">
                            <bk-popover placement="top">
                                <bk-button
                                    theme="primary"
                                    text
                                    :disabled="!!props.row.bounded_catalogs[0]"
                                    @click="deleteOne(props.row)">
                                    {{ $t('m.serviceConfig["删除"]') }}
                                </bk-button>
                                <div slot="content" style="white-space: normal;">
                                    <span>{{ $t(`m.serviceConfig['服务已绑定关联目录，请先解绑后在进行删除操作']`) }}</span>
                                </div>
                            </bk-popover>
                        </template>
                        <template v-else>
                            <bk-button
                                data-test-id="service_button_deleteService"
                                theme="primary"
                                text
                                @click="deleteOne(props.row)">
                                {{ $t('m.serviceConfig["删除"]') }}
                            </bk-button>
                        </template>
                    </template>
                </bk-table-column>
            </bk-table>
        </div>
    </div>
</template>

<script>
    import axios from 'axios'
    import NavTitle from '@/components/common/layout/NavTitle'
    import searchInfo from '../commonComponent/searchInfo/searchInfo.vue'
    import permission from '@/mixins/permission.js'
    import { errorHandler } from '../../utils/errorHandler'

    export default {
        name: 'ServiceList',
        components: {
            NavTitle,
            searchInfo
        },
        mixins: [permission],
        data () {
            return {
                trueStatus: true,
                falseStatus: false,
                isDataLoading: false,
                // 服务类型数据
                serviceTypesMap: [],
                dataList: [],
                // 选择
                checkList: [],
                pagination: {
                    current: 1,
                    count: 10,
                    limit: 10
                },
                // 查询
                moreSearch: [
                    {
                        name: this.$t(`m.serviceConfig["服务名称"]`),
                        type: 'input',
                        typeKey: 'name__icontains',
                        value: '',
                        placeholder: this.$t(`m.serviceConfig["请输入服务名"]`)
                    },
                    {
                        name: this.$t(`m.serviceConfig["类型"]`),
                        type: 'select',
                        typeKey: 'key',
                        value: '',
                        list: []
                    },
                    {
                        name: this.$t(`m.serviceConfig["服务级别"]`),
                        type: 'select',
                        typeKey: 'sla',
                        value: '',
                        list: []
                    }
                ],
                addList: [],
                lineList: [],
                // 流程预览
                processInfo: {
                    isShow: false,
                    title: this.$t(`m.serviceConfig["流程预览"]`),
                    position: {
                        top: 150
                    },
                    draggable: true,
                    loading: true
                }
            }
        },
        mounted () {
            this.getServiceTypes()
            this.getList()
            this.getSlaList()
        },
        methods: {
            // 获取数据
            getList (page) {
                // 查询时复位页码
                if (page !== undefined) {
                    this.pagination.current = page
                }
                // 重新获取数据时清空选中的数据
                this.checkList = []
                const params = {
                    page: this.pagination.current,
                    page_size: this.pagination.limit,
                    project_key: this.$store.state.project.id,
                    ordering: '-update_at'
                }

                this.moreSearch.forEach(item => {
                    if (item.value !== '' && item.typeKey) {
                        params[item.typeKey] = Array.isArray(item.value) ? item.value.join(',') : item.value
                    }
                })

                this.isDataLoading = true
                this.$store.dispatch('serviceEntry/getList', params).then(res => {
                    this.dataList = res.data.items
                    this.dataList.forEach((item, index) => {
                        this.$set(item, 'checkStatus', false)
                    })
                    // 分页
                    this.pagination.current = res.data.page
                    this.pagination.count = res.data.count
                }).catch(res => {
                    errorHandler(res, this)
                }).finally(() => {
                    this.isDataLoading = false
                })
            },
            // 服务类型
            getServiceTypes () {
                this.$store.dispatch('getCustom').then((res) => {
                    this.serviceTypesMap = res.data
                    this.moreSearch[1].list = res.data
                }).catch(res => {
                    errorHandler(res, this)
                })
            },
            // 服务级别列表
            getSlaList () {
                const params = {
                    is_enabled: true,
                    project_key: this.$store.state.project.id
                }
                this.$store.dispatch('slaManagement/getProtocolsList', { params }).then(res => {
                    this.slaList = res.data
                    this.moreSearch[2].list = res.data
                    this.moreSearch[2].list.forEach(item => {
                        this.$set(item, 'key', item.id)
                    })
                }).catch(res => {
                    errorHandler(res, this)
                })
            },
            disabledFn (item, index) {
                return !item.bounded_catalogs[0]
            },
            // 创建服务权限点击时校验
            onServiceCreatePermissonCheck () {
                if (!this.hasPermission(['service_create'], this.$store.state.project.projectAuthActions)) {
                    const projectInfo = this.$store.state.project.projectInfo
                    const resourceData = {
                        project: [{
                            id: projectInfo.key,
                            name: projectInfo.name
                        }]
                    }
                    this.applyForPermission(['service_create'], this.$store.state.project.projectAuthActions, resourceData)
                } else {
                    this.$router.push({
                        name: 'projectServiceEdit',
                        params: {
                            type: 'new',
                            step: 'basic'
                        },
                        query: {
                            project_id: this.$store.state.project.id
                        }
                    })
                }
            },
            // 编辑
            changeEntry (item, type) {
                this.$router.push({
                    name: 'projectServiceEdit',
                    params: {
                        type: 'edit',
                        step: 'basic'
                    },
                    query: {
                        serviceId: item.id,
                        project_id: this.$store.state.project.id
                    }
                })
            },
            /**
             * 单个服务操作项点击时校验
             * @params {Array} required 需要的权限
             * @params {Object} row 数据对象
             */
            onServicePermissonCheck (required, row) {
                const projectInfo = this.$store.state.project.projectInfo
                const resourceData = {
                    service: [{
                        id: row.id,
                        name: row.name
                    }],
                    project: [{
                        id: projectInfo.key,
                        name: projectInfo.name
                    }]
                }
                this.applyForPermission(required, [...this.$store.state.project.projectAuthActions, ...row.auth_actions], resourceData)
            },
            deleteCheck () {
                this.$bkInfo({
                    type: 'warning',
                    title: this.$t(`m.serviceConfig["确认删除服务？"]`),
                    subTitle: this.$t(`m.serviceConfig["服务一旦删除，对应的服务将不可用。请谨慎操作。"]`),
                    confirmFn: () => {
                        const idArr = this.checkList.map(item => {
                            return item.id
                        })
                        const id = idArr.join(',')
                        if (this.secondClick) {
                            return
                        }
                        this.secondClick = true
                        this.$store.dispatch('serviceEntry/batchDeleteService', { id: id }).then((res) => {
                            this.$bkMessage({
                                message: this.$t(`m.serviceConfig["删除成功"]`),
                                theme: 'success'
                            })
                            this.getList(1)
                        }).catch((res) => {
                            errorHandler(res, this)
                        }).finally(() => {
                            this.secondClick = false
                        })
                    }
                })
            },
            // 删除
            deleteOne (item) {
                this.$bkInfo({
                    type: 'warning',
                    title: this.$t(`m.serviceConfig["确认删除服务？"]`),
                    subTitle: this.$t(`m.serviceConfig["服务一旦删除，对应的服务将不可用。请谨慎操作。"]`),
                    confirmFn: () => {
                        const id = item.id
                        if (this.secondClick) {
                            return
                        }
                        this.secondClick = true
                        this.$store.dispatch('serviceEntry/deleteService', id).then((res) => {
                            this.$bkMessage({
                                message: this.$t(`m.serviceConfig["删除成功"]`),
                                theme: 'success'
                            })
                            if (this.dataList.length === 1) {
                                this.pagination.current = this.pagination.current === 1 ? 1 : this.pagination.current - 1
                            }
                            this.getList()
                        }).catch((res) => {
                            errorHandler(res, this)
                        }).finally(() => {
                            this.secondClick = false
                        })
                    }
                })
            },
            // 简单查询
            searchContent () {
                this.getList(1)
            },
            // 清空搜索表单
            clearSearch () {
                this.moreSearch.forEach(item => {
                    item.value = ''
                })
                this.getList(1)
            },
            searchMore () {
                this.$refs.searchInfo.searchMore()
            },
            handlePageChange (page) {
                this.pagination.current = page
                this.getList()
            },
            // 分页过滤数据
            handlePageLimitChange () {
                this.pagination.limit = arguments[0]
                this.getList()
            },
            changeCheck (value) {
                // 改变中选态，与表头选择相呼应
                this.$refs.serviceTable.toggleRowSelection(value, value.checkStatus)
                if (value.checkStatus) {
                    if (!this.checkList.some(item => item.id === value.id)) {
                        this.checkList.push(value)
                    }
                } else {
                    this.checkList = this.checkList.filter(item => item.id !== value.id)
                }
            },
            // 全选 半选
            handleSelectAll (selection) {
                this.dataList.forEach(item => {
                    if (!item.bounded_catalogs[0] && this.hasPermission(['service_manage'], item.auth_actions)) {
                        item.checkStatus = !!selection.length
                    }
                })
                // 选中有权限数据
                this.checkList = selection.filter(item => this.hasPermission(['service_manage'], item.auth_actions))
            },
            handleSelect (selection, row) {
                this.checkList = selection
            },
            // 流程预览
            processShow (item) {
                const id = item.workflow
                this.processInfo.isShow = !this.processInfo.isShow
                this.processInfo.loading = true
                axios.all([
                    this.$store.dispatch('deployCommon/getNodeVersion', { id }),
                    this.$store.dispatch('deployCommon/getLineVersion', { id })
                ]).then(axios.spread((userResp, reposResp) => {
                    this.addList = userResp.data
                    for (let i = 0; i < this.addList.length; i++) {
                        this.addList[i].indexInfo = i
                    }
                    this.lineList = reposResp.data.items
                })).finally(() => {
                    this.processInfo.loading = false
                })
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '~@/scss/mixins/scroller.scss';
.page-content {
    padding: 20px;
    height: calc(100vh - 104px);
    overflow: auto;
    @include scroller;
}
.filter-btn /deep/ .icon-search-more {
    font-size: 14px;
}
.bk-form-checkbox {
    padding: 0;
    width: 16px;
    margin: 0 auto;
}
</style>
