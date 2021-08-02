<template>
    <div class="test-page">
        <h3 class="page-title">RenderForm SDK 功能验证</h3>
        <hr />
        <div class="content-wrapper">
            <h3 class="section-title">创建任务</h3>
            <bk-form class="params-fill">
                <bk-form-item label="业务列表">
                    <bk-select :loading="bizLoading" v-model="business" @selected="onSelectBiz" @clear="onClearBiz" searchable>
                        <bk-option
                            v-for="item in bkBizList"
                            :key="item.key"
                            :name="item.name"
                            :id="item.key">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item label="流程模板">
                    <bk-select :loading="templateLoading" v-model="template" @selected="onSelectTpl" searchable>
                        <bk-option
                            v-for="item in templateList"
                            :key="item.id"
                            :name="item.name"
                            :id="item.id">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item label="模板参数">
                    <div class="form-wrapper" v-if="template !== '' && !formLoading" v-bkloading="{ isLoading: configLoading }">
                        <render-form
                            ref="renderForm"
                            :form-option="formOptions"
                            :constants="constants"
                            :context="context"
                            v-model="formData"
                            @configLoadingChange="configLoading = $event">
                        </render-form>
                    </div>
                </bk-form-item>
                <bk-form-item>
                    <bk-button
                        theme="primary"
                        :disabled="template === '' || formLoading || configLoading"
                        :loading="submitting"
                        @click="onCreateTask">
                        创建任务
                    </bk-button>
                    <bk-button
                        theme="default"
                        :loading="taskLoading"
                        @click="getTaskList">
                        刷新表格
                    </bk-button>
                </bk-form-item>
            </bk-form>
            <h3 class="section-title">任务记录</h3>
            <div class="table-wrapper" v-bkloading="{ isLoading: taskLoading }">
                <bk-table
                    :data="taskList"
                    :pagination="pagination"
                    @page-change="handlePageChange"
                    @page-limit-change="handlePageLimitChange">
                    <bk-table-column label="任务ID" property="task_id" :width="80"></bk-table-column>
                    <bk-table-column label="名称" property="name"></bk-table-column>
                    <bk-table-column label="开始时间" property="start_at" :width="190"></bk-table-column>
                    <bk-table-column label="结束时间" property="end_at" :width="190"></bk-table-column>
                    <bk-table-column label="创建时间" property="create_at" :width="190"></bk-table-column>
                    <bk-table-column label="创建人" property="creator" :width="120"></bk-table-column>
                    <bk-table-column label="状态" property="status" :width="120"></bk-table-column>
                    <bk-table-column label="操作" :width="120">
                        <template slot-scope="props">
                            <bk-button
                                v-if="props.row.status === 'NEW'"
                                theme="primary"
                                :text="true"
                                :disabled="taskOperating"
                                @click="onStartClick(props.row)">
                                启动
                            </bk-button>
                            <span v-else>
                                <a :href="props.row.task_url" target="blank">任务详情</a>
                            </span>
                        </template>
                    </bk-table-column>
                </bk-table>
            </div>
        </div>
    </div>
</template>
<script>
    export default {
        name: 'test',
        data () {
            return {
                formData: {},
                formOptions: {
                    showRequired: true,
                    showGroup: true,
                    showLabel: true,
                    showHook: false,
                    showDesc: true
                },
                templateLoading: false,
                bizLoading: false,
                formLoading: false,
                configLoading: false,
                submitting: false,
                template: '',
                business: '',
                context: {
                    project: {
                        id: 2,
                        bk_biz_id: 2,
                        name: '蓝鲸',
                        from_cmdb: true
                    },
                    bk_biz_id: 2,
                    site_url: window.SITE_URL_SOPS + window.PREFIX_SOPS
                },
                templateList: [],
                bkBizList: [],
                taskList: [],
                taskLoading: false,
                constants: [],
                taskOperating: false,
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 10
                }
            }
        },
        mounted () {
            this.getBizList()
            this.getTemplateList()
            this.getTaskList()
        },
        methods: {
            async getTemplateList () {
                try {
                    this.template = ''
                    this.constants = []
                    this.formData = {}
                    this.formOptions = {
                        showRequired: true,
                        showGroup: true,
                        showLabel: true,
                        showHook: false,
                        showDesc: true
                    }
                    this.templateLoading = true
                    const params = {
                        bk_biz_id: this.business
                    }
                    const resp = await this.$store.dispatch('getTemplateList', params)
                    this.templateList = resp.data
                } catch (error) {
                    this.$bkMessage({
                        message: error.data.msg,
                        theme: 'error'
                    })
                } finally {
                    this.templateLoading = false
                }
            },
            async getBizList () {
                try {
                    this.bizLoading = true
                    const resp = await this.$store.dispatch('getBkBizList')
                    this.bkBizList = resp.data
                } catch (error) {
                    this.$bkMessage({
                        message: error.data.msg,
                        theme: 'error'
                    })
                } finally {
                    this.bizLoading = false
                }
            },
            // 获取模板详情，即参数列表
            async getTemplateDetail (id) {
                try {
                    this.formLoading = true
                    const params = {
                        template_id: this.template,
                        bk_biz_id: this.business
                    }
                    const resp = await this.$store.dispatch('getTemplateDetail', params)
                    this.constants = resp.data.constants
                } catch (error) {
                    this.$bkMessage({
                        message: error.data.msg,
                        theme: 'error'
                    })
                } finally {
                    this.formLoading = false
                }
            },
            // 获取任务列表
            async getTaskList () {
                try {
                    this.taskLoading = true
                    const params = {
                        page_size: this.pagination.limit,
                        page: this.pagination.current
                    }
                    const resp = await this.$store.dispatch('getTaskList', params)
                    this.taskList = resp.data.items
                    this.pagination.count = resp.data.count
                } catch (error) {
                    this.$bkMessage({
                        message: error.data.msg,
                        theme: 'error'
                    })
                } finally {
                    this.taskLoading = false
                }
            },
            onSelectBiz (id) {
                this.business = id
                this.context.bk_biz_id = this.business
                if (this.template === '') {
                    this.getTemplateList()
                }
            },
            onClearBiz (oldId) {
                this.onSelectBiz('')
            },
            onSelectTpl (id) {
                this.template = id
                const templateInfo = this.templateList.find(item => item.id === this.template)
                if (templateInfo.bk_biz_id !== undefined) {
                    this.context.project.bk_biz_id = templateInfo.bk_biz_id
                    this.context.project.id = this.template
                }
                this.getTemplateDetail(id)
            },
            // 创建任务
            async onCreateTask () {
                const isValid = this.$refs.renderForm.validate()
                if (isValid) {
                    try {
                        this.submitting = true
                        this.constants.forEach(item => {
                            this.$set(item, 'value', this.formData[item.key])
                        })

                        let templateSource = 'common'
                        const templateInfo = this.templateList.find(item => item.id === this.template)
                        if (templateInfo.bk_biz_id !== undefined) {
                            templateSource = 'business'
                        }
                        const params = {
                            id: this.template,
                            template_source: templateSource,
                            bk_biz_id: this.business,
                            constants: this.constants
                        }
                        if (params) {
                            return
                        }
                        await this.$store.dispatch('createTask', params)
                        this.template = ''
                        this.constants = []
                        this.pagination.current = 1
                        this.getTaskList()
                    } catch (error) {
                        this.$bkMessage({
                            message: error.data.msg,
                            theme: 'error'
                        })
                    } finally {
                        this.submitting = false
                    }
                }
            },
            // 启动任务
            async onStartClick (data) {
                if (this.taskOperating) {
                    return
                }
                try {
                    this.taskOperating = true
                    const params = {
                        bk_biz_id: this.business, // 测试环境写死一个业务id
                        task_id: data.id,
                        action: 'start'
                    }
                    await this.$store.dispatch('startTask', params)
                    this.getTaskList()
                } catch (error) {
                    this.$bkMessage({
                        message: error.data.msg,
                        theme: 'error'
                    })
                } finally {
                    this.taskOperating = false
                }
            },
            handlePageChange (page) {
                this.pagination.current = page
                this.getTaskList()
            },
            handlePageLimitChange (limit) {
                this.pagination.limit = limit
                this.pagination.current = 1
                this.getTaskList()
            }
        }
    }
</script>
<style lang="scss" scoped>
    .test-page {
        padding-top: 20px;
        height: 100%;
    }
    .page-title {
        padding: 0 20px;
        font-size: 14px;
    }
    .content-wrapper {
        padding: 20px;
        height: calc(100% - 68px);
        overflow-y: auto;
    }
    .section-title {
        padding-top: 20px;
        font-size: 14px;
    }
    .params-fill {
        width: 800px;
    }
    .form-wrapper {
        min-height: 30px;
    }
</style>
