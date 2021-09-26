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
    <div class="log-list" v-bkloading="{ isLoading: loading }">
        <bk-timeline
            data-test-id="ticket_timeline_viewLog"
            ext-cls="log-time-line"
            :list="list"
            @select="handleSelect"></bk-timeline>
        <!-- 操作日志详情 sideslider -->
        <ticket-log-detail
            :log-info.sync="dispalyLogInfo"
            :show="!!dispalyLogInfo"
            @close="() => {
                dispalyLogInfo = null
            }">
        </ticket-log-detail>
    </div>
</template>

<script>
    import ticketLogDetail from './logInfo/ticketLogDetail'
    import { errorHandler } from '@/utils/errorHandler'
    import fieldMix from '@/views/commonMix/field.js'

    export default {
        name: 'LogTab',
        components: {
            ticketLogDetail
        },
        mixins: [fieldMix],
        data () {
            return {
                dispalyLogInfo: null,
                flowStartText: this.$t(`m.newCommon["流程开始"]`),
                loading: false,
                list: []
            }
        },
        created () {
            this.getOperationLogList()
        },
        // 方法集合
        methods: {
            // 获取流转日志-操作日志
            getOperationLogList () {
                const id = this.$route.query.id
                if (!id) {
                    return
                }
                this.loading = true
                const params = {}
                params['ticket'] = id
                if (this.$route.query.token) {
                    params['token'] = this.$route.query.token
                }
                this.$store.dispatch('change/getLog', params).then((res) => {
                    this.list = []
                    res.data.forEach(item => {
                        const line = {}
                        line.content = item.message
                        line.tag = item.operate_at
                        if (item.message !== this.flowStartText) {
                            // item.content = item.message
                            // item.tag = item.operate_at
                            item.content = item.operate_at
                            item.tag = item.message
                            item.type = 'primary'
                            item.showMore = false
                            this.list.push(JSON.parse(JSON.stringify(item)))
                        }
                    })
                }).catch((res) => {
                    errorHandler(res, this)
                }).finally(() => {
                    this.loading = false
                })
            },
            handleSelect (item) {
                const copyItem = JSON.parse(JSON.stringify(item))
                copyItem.form_data.forEach(form => {
                    form.val = form.value
                    this.conditionField(form, copyItem.form_data)
                })
                copyItem.form_data = copyItem.form_data.filter(form => form.showFeild)
                this.dispalyLogInfo = copyItem
            }
        }
    }
</script>

<style lang='scss' scoped>
.log-list {
    width: 100%;
    height: 100%;
}
.log-time-line {
    /deep/ {
        .bk-timeline-title,
        .bk-timeline-content {
            font-size: 12px;
        }
        .bk-timeline-title {
            &:hover {
                color: #3a84ff;
            }
        }
        .bk-timeline-dot {
            padding-bottom: 10px;
        }
    }
}
</style>
