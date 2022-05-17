<template>
    <div>
        <!-- SOPS -->
        <sops-get-param
            v-if="nodeInfo.type === 'TASK-SOPS'"
            class="sops-form"
            ref="sopsGetParam"
            :key="new Date().getTime()"
            :hooked-var-list="hookedVarList"
            :constants="constants"
            :context="context"
            :is-hook="isHook"
            :is-edit="isEdit"
            :state-list="stateList"
            :is-static="isStatic"
            :constant-default-value="constantDefaultValue"
            @onChangeHook="onChangeHook"
        ></sops-get-param>
        <!-- DEVOPS -->
        <bk-form
            v-if="nodeInfo.type === 'TASK-DEVOPS'"
            ref="devopsVariable"
            ext-cls="pipelineForm"
            form-type="vertical"
            :model="pipelineData"
            :rules="pipelineRules"
            :label-width="200"
        >
            <bk-form-item
                v-for="pipeline in pipelineList"
                :key="pipeline.id"
                :label="pipeline.id"
                :property="pipeline.id"
                :rules="pipelineRules[pipeline.id]"
                :required="pipeline.required"
            >
                <bk-input
                    :disabled="!changeBtn"
                    v-model="pipelineData[pipeline.id]"
                    :clearable="true"
                ></bk-input>
            </bk-form-item>
        </bk-form>
        <devops-preview
            v-if="nodeInfo.type === 'TASK-DEVOPS'"
            :stages="pipelineStages"
        ></devops-preview>
        <div class="submit-btn">
            <bk-button v-if="changeBtn" :theme="'primary'" @click="submit">
                {{ $t(`m["提交"]`) }}
            </bk-button>
            <bk-button :theme="'primary'" @click="reSetSopTask">
                {{ changeBtn ? $t(`m["返回"]`) : $t(`m["重做"]`) }}
            </bk-button>
            <bk-button @click="ignore">{{ $t(`m["忽略"]`) }}</bk-button>
        </div>
    </div>
</template>

<script>
    import DevopsPreview from '@/components/task/DevopsPreview.vue';
    import sopsGetParam from '../../../../processManagement/processDesign/nodeConfigue/components/sopsGetParam.vue';
    export default {
        name: 'sopsTask',
        components: {
            sopsGetParam,
            DevopsPreview,
        },
        props: {
            ticketInfo: Object,
            nodeInfo: Object,
            constants: Array,
            hookedVarList: Object,
            constantDefaultValue: Object,
            pipelineList: {
                type: Array,
                default: () => [],
            },
            pipelineRules: Object,
            workflow: [Number, String],
            pipelineStages: Array,
            pipelineConstants: Array,
        },
        data() {
            return {
                isStatic: false,
                changeBtn: false,
                context: {
                    project: {
                        id: '',
                        bk_biz_id: '',
                        name: '',
                        from_cmdb: true,
                    },
                    bk_biz_id: '',
                    site_url: window.SITE_URL_SOPS + window.PREFIX_SOPS,
                },
                isHook: false,
                isEdit: false,
                stateList: [],
                pipelineFormList: [],
                pipelineData: {}, // 流水线参数
            };
        },
        watch: {
            pipelineConstants(val) {
                val.map((item) => {
                    this.$set(this.pipelineData, item.key, item.value);
                });
            },
        },
        mounted() {
            this.getRelatedFields();
        },
        methods: {
            async getRelatedFields() {
                const params = {
                    workflow: this.workflow,
                    state: this.nodeInfo.state_id,
                    field: '',
                };
                await this.$store
                    .dispatch('apiRemote/get_related_fields', params)
                    .then((res) => {
                        this.stateList = res.data;
                    })
                    .catch((res) => {
                        console.log(res);
                    })
                    .finally(() => {});
            },
            reSetSopTask() {
                this.changeBtn = !this.changeBtn;
                this.isHook = this.changeBtn;
                this.isEdit = !this.isEdit;
                if (this.$refs.sopsGetParam) {
                    this.$refs.sopsGetParam.changeTicketformDisable(this.changeBtn);
                }
            },
            onChangeHook(key, value) {
                this.$emit('onChangeHook', key, value);
            },
            ignore() {
                const params = {
                    inputs: {},
                    is_direct: true,
                    state_id: this.nodeInfo.state_id,
                };
                this.$store
                    .dispatch('deployOrder/ignoreNode', {
                        params,
                        ticketId: this.nodeInfo.ticket_id,
                    })
                    .then(() => {
                        this.$bkMessage({
                            message: this.$t('m["忽略完成"]'),
                            theme: 'success',
                        });
                        this.$emit('reloadTicket');
                    });
            },
            retry(params) {
                this.$store
                    .dispatch('deployOrder/retryNode', {
                        params,
                        ticketId: this.nodeInfo.ticket_id,
                    })
                    .then(() => {
                        this.$bkMessage({
                            message: this.$t('m.newCommon["提交成功"]'),
                            theme: 'success',
                        });
                        this.changeBtn = false;
                        this.$emit('reloadTicket');
                    });
            },
            submit() {
                const params = {
                    inputs: {},
                    state_id: this.nodeInfo.state_id,
                };
                if (this.nodeInfo.type === 'TASK-SOPS') {
                    if (!this.$refs.sopsGetParam.getRenderFormValidate()) return;
                    const biz = {
                        name: this.$t('m.treeinfo["业务"]'),
                        value: this.nodeInfo.projectId || 2,
                        key: 1,
                        value_type: 'custom',
                    };
                    const { exclude_task_nodes_id, template_id, template_source } =                    this.nodeInfo.contexts.task_params;
                    const formData = this.constants.map((item) => {
                        const formKey = Object.keys(this.$refs.sopsGetParam.formData).filter(key => key === item.key);
                        const vt = this.hookedVarList[formKey]
                            ? 'variable'
                            : 'custom';
                        return {
                            name: item.name,
                            key: item.key,
                            value: this.hookedVarList[formKey]
                                ? this.$refs.sopsGetParam.formData[formKey].slice(
                                    2,
                                    this.$refs.sopsGetParam.formData[formKey]
                                        .length - 1
                                )
                                : this.$refs.sopsGetParam.formData[formKey],
                            value_type: vt,
                            is_quoted: this.hookedVarList[formKey],
                        };
                    });
                    params.inputs = {
                        bk_biz_id: biz,
                        template_id,
                        constants: formData,
                        exclude_task_nodes_id,
                        template_source,
                    };
                    this.retry(params);
                } else {
                    this.$refs.devopsVariable.validate().then(() => {
                        const constants = Object.keys(this.$refs.devopsVariable.model).map(item => ({
                            value: this.$refs.devopsVariable.model[item],
                            name: item,
                            key: item,
                        }));
                        const projectId = this.nodeInfo.api_info.devops_info.find(item => item.key === 'project_id');
                        const pipelineId = this.nodeInfo.api_info.devops_info.find(item => item.key === 'pipeline_id');
                        params.inputs = {
                            username: window.username,
                            project_id: projectId,
                            pipeline_id: pipelineId,
                            constants,
                        };
                        this.retry(params);
                    });
                }
            },
        },
    };
</script>

<style lang="scss" scoped>
.sops-form {
    width: 100%;
    min-height: 100px;
}
.submit-btn {
    margin-top: 60px;
}
</style>
