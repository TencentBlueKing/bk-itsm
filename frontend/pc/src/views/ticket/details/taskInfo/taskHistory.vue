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
    <div class="bk-task-history" v-bkloading="{ isLoading: loading }">
        <div class="history-table">
            <bk-table
                :data="historyList"
                :size="'small'"
                @sort-change="orderingClick">
                <bk-table-column :label="$t(`m.task['执行时间']`)" :sortable="'custom'">
                    <template slot-scope="props">
                        <span :title="props.row.end_time">
                            {{props.row.end_time || '--'}}
                        </span>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.task['响应动作']`)">
                    <template slot-scope="props">
                        <span
                            :title="props.row.display_name"
                            style="color: #3A84FF;cursor: pointer"
                            @click="openDetail(props.row)">
                            {{props.row.component_name || '--'}}
                        </span>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.task['执行状态']`)" :sortable="'custom'">
                    <template slot-scope="props">
                        <span class="bk-status-success"
                            :class="{ 'bk-status-failed': props.row.status === 'FAILED' }"
                            :title="props.row.status_name">
                            {{props.row.status_name || '--'}}
                        </span>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.task['操作人']`)">
                    <template slot-scope="props">
                        <span :title="props.row.operator_username">
                            {{props.row.operator_username || '--'}}
                        </span>
                    </template>
                </bk-table-column>
            </bk-table>
        </div>
        <!-- 任务记录详情 -->
        <bk-sideslider
            :is-show.sync="historyDetail.isShow"
            :title="historyDetail.title"
            :width="historyDetail.width"
            :quick-close="true">
            <div slot="content">
                <history-detail v-if="historyDetail.isShow"
                    :history-id="historyDetail.id"
                    :basic-infomation="basicInfomation"
                    :node-list="nodeList">
                </history-detail>
            </div>
        </bk-sideslider>
    </div>
</template>

<script>
    import historyDetail from './taskHistoryDetail.vue'
    import { errorHandler } from '@/utils/errorHandler'

    export default {
        name: 'taskHistory',
        components: {
            historyDetail
        },
        props: {
            basicInfomation: {
                type: Object,
                default () {
                    return {}
                }
            },
            nodeList: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                loading: false,
                historyList: [],
                historyDetail: {
                    isShow: false,
                    title: this.$t(`m.task['记录详情']`),
                    loading: false,
                    width: 660,
                    id: ''
                }
            }
        },
        computed: {
            taskHistoryRefresh () {
                return this.$store.state.taskHistoryRefresh
            }
        },
        watch: {
            taskHistoryRefresh: function () {
                this.getHistoryList()
            }
        },
        mounted () {
            this.getHistoryList()
        },
        methods: {
            getHistoryList () {
                // 获取单据手动触发器
                const params = {
                    operate_type: 'all'
                }
                this.loading = true
                const id = this.basicInfomation.id
                this.$store.dispatch('trigger/getTicketHandleTriggers', { id, params }).then(res => {
                    this.historyList = res.data.filter(item => item.status === 'FAILED' || item.status === 'SUCCEED')
                }).catch((res) => {
                    errorHandler(res, this)
                }).finally(() => {
                    this.loading = false
                })
            },
            openDetail (task) {
                this.historyDetail.isShow = true
                this.historyDetail.id = task.id
            },
            orderingClick (value) {
                this.historyList.sort(this.sortCompare('status', value.order))
            },
            sortCompare (prop, type) {
                return (obj1, obj2) => {
                    let val1 = obj1[prop]
                    let val2 = obj2[prop]
                    if (!isNaN(Number(val1)) && !isNaN(Number(val2))) {
                        val1 = Number(val1)
                        val2 = Number(val2)
                    }
                    if (val1 < val2) {
                        return (type === 'ascending' ? -1 : 1)
                    } else if (val1 > val2) {
                        return (type === 'ascending' ? 1 : -1)
                    } else {
                        return 0
                    }
                }
            }
        }
    }
</script>

<style scoped lang='scss'>
    .bk-task-history{
        .history-table{
        }
    }
    .bk-status-success{
        color: #2DCB56;
    }
    .bk-status-failed{
        color: #FF5656;
    }
</style>
