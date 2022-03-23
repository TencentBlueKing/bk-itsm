<template>
    <div class="bk-itsm-service">
        <div class="is-title" :class="{ 'bk-title-left': !sliderStatus }">
            <p class="bk-come-back">
                {{ $t('m["通知配置"]') }}
            </p>
        </div>
        <div class="itsm-page-content">
            <ul class="bk-notice-tab">
                <li v-for="(item, index) in remindWayList"
                    :key="item.id"
                    :class="{ 'bk-check-notice': acticeTab === item.id }"
                    @click="changeNotice(item, index)">
                    <span>{{ item.name }}</span>
                </li>
            </ul>
            <div class="bk-only-btn">
                <bk-button theme="primary"
                    data-test-id="notice_button_create"
                    @click="addNotice">
                    <i class="bk-itsm-icon icon-itsm-icon-one-five"></i>
                    {{ $t(`m.deployPage['新增']`) }}
                </bk-button>
                <div class="bk-only-search">
                    <bk-input
                        data-test-id="notice_input_search"
                        :placeholder="$t(`m.systemConfig['请输入角色名称']`)"
                        :clearable="true"
                        :right-icon="'bk-icon icon-search'"
                        v-model="searchNotice"
                        @enter="getList(1)"
                        @clear="getList(1)">
                    </bk-input>
                </div>
            </div>
            <bk-table
                v-bkloading="{ isLoading: isDataLoading }"
                :data="noticeList"
                :size="'small'">
                <bk-table-column type="index" label="No." align="center" width="60"></bk-table-column>
                <bk-table-column :label="$t(`m.deployPage['通知类型']`)">
                    <template slot-scope="props">
                        <template v-if="hasPermission(['notification_manage'], $store.state.project.projectAuthActions)">
                            <span class="bk-lable-primary" @click="editorInfo(props.row)">{{props.row.action_name}}</span>
                        </template>
                        <span
                            v-else
                            class="bk-table-permission"
                            v-cursor="{ active: !hasPermission(['notification_manage'], $store.state.project.projectAuthActions) }"
                            @click="editNotice(props.row)">
                            {{props.row.action_name}}
                        </span>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.slaContent['更新时间']`)" prop="update_at"></bk-table-column>
                <bk-table-column :label="$t(`m.deployPage['更新人']`)" prop="updated_by"></bk-table-column>
                <bk-table-column :label="$t(`m.deployPage['操作']`)" width="150">
                    <template slot-scope="props">
                        <bk-button
                            theme="primary"
                            v-cursor="{ active: !hasPermission(['notification_manage'], $store.state.project.projectAuthActions) }"
                            :disabled="!hasPermission(['notification_manage'], $store.state.project.projectAuthActions)"
                            text
                            @click="editNotice(props.row)">
                            {{ $t('m.deployPage["编辑"]') }}
                        </bk-button>
                        <bk-button>删除</bk-button>
                    </template>
                </bk-table-column>
            </bk-table>
            <bk-dialog v-model="isShowEdit"
                width="700"
                theme="primary"
                :mask-close="false"
                :header-position="'left'"
                :title="isEdit ? '编辑' : '新建'">
                <bk-form ref="basicFrom" :model="formData" width="700" form-type="vertical" :rules="rules">
                    <bk-form-item label="通知方式" :required="true" :property="'noticeType'">
                        <bk-select :disabled="false" v-model="formData.noticeType" searchable>
                            <bk-option v-for="option in noticeTypeLIST"
                                :key="option.id"
                                :id="option.id"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                    </bk-form-item>
                    <bk-form-item label="通知类型" :required="true" :property="'noticeAction'">
                        <bk-select :disabled="false" v-model="formData.noticeAction" searchable>
                            <bk-option v-for="option in actionList"
                                :key="option.id"
                                :id="option.id"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                    </bk-form-item>
                    <bk-form-item label="通知触发" :required="true" :property="'noticeUserBy'">
                        <bk-select :disabled="false" v-model="formData.noticeUserBy" searchable>
                            <bk-option v-for="option in userByList"
                                :key="option.id"
                                :id="option.id"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                    </bk-form-item>
                </bk-form>
                <editor-notice
                    ref="editorNotice"
                    :check-id="acticeTab"
                    :is-show-footer="false"
                    :notice-info="formInfo"
                    @closeEditor="closeEditor">
                </editor-notice>
            </bk-dialog>
        </div>
    </div>
</template>

<script>
    import editorNotice from '../processManagement/notice/editorNotice.vue'
    export default {
        name: 'Notice',
        components: {
            editorNotice
        },
        data () {
            return {
                acticeTab: 'WEIXIN',
                isShowEdit: false,
                isEdit: false,
                remindWayList: [
                    { id: 'WEIXIN', name: '企业微信' },
                    { id: 'EMAIL', name: '邮件' },
                    { id: 'SMS', name: '手机短信' }
                ],
                noticeList: [],
                // 先写死，后续添加自定义
                noticeTypeLIST: [
                    { id: 'WEIXIN', name: '企业微信' },
                    { id: 'EMAIL', name: '邮件' },
                    { id: 'SMS', name: '手机短信' }
                ],
                userByList: [
                    { id: 'TICKET', name: '单据' },
                    { id: 'SLA', name: 'SLA' },
                    { id: 'TASK', name: '任务' }
                ],
                rules: {
                    noticeType: [
                        {
                            required: true,
                            message: '必选项',
                            trigger: 'blur'
                        }
                    ],
                    noticeAction: [
                        {
                            required: true,
                            message: '必选项',
                            trigger: 'blur'
                        }
                    ],
                    noticeUserBy: [
                        {
                            required: true,
                            message: '必选项',
                            trigger: 'blur'
                        }
                    ]
                },
                actionList: [],
                typeList: [],
                formData: {
                    noticeType: '',
                    noticeAction: '',
                    noticeUserBy: ''
                },
                formInfo: {},
                isDataLoading: false,
                searchNotice: ''
            }
        },
        computed: {
            sliderStatus () {
                return this.$store.state.common.slideStatus
            }
        },
        mounted () {
            this.getNoticeList()
            this.getAction()
        },
        methods: {
            changeNotice (item, index) {
                this.acticeTab = item.id
                this.getNoticeList()
            },
            getAction () {
                this.$store.dispatch('project/getAction').then(res => {
                    const list = res.data
                    console.log(res.data)
                    for (const item in list) {
                        this.actionList.push({
                            id: item,
                            name: list[item]
                        })
                    }
                })
            },
            getNoticeList () {
                this.isDataLoading = true
                const params = {
                    project_key: this.$route.query.project_id,
                    notify_type: this.acticeTab
                }
                this.$store.dispatch('noticeConfigure/getNoticeList', { params }).then((res) => {
                    this.noticeList = res.data
                }).catch((res) => {
                    console.log(res)
                }).finally(() => {
                    this.isDataLoading = false
                })
            },
            // 新增配置
            addNotice () {
                this.isEdit = false
                this.isShowEdit = true
            },
            editNotice () {
                this.isEdit = true
                this.isShowEdit = true
            },
            closeEditor () {
                this.isShowEdit = false
            }
        }
    }

</script>

<style lang='scss' scoped>
    @import '../../scss/mixins/clearfix.scss';
    .bk-notice-tab {
        @include clearfix;
        border-bottom: 1px solid #dde4eb;
        margin: -20px -20px 20px;
        padding: 0 20px;
        background-color: #ffffff;
        li {
            float: left;
            padding: 0 10px;
            line-height: 46px;
            text-align: center;
            color: #63656e;
            cursor: pointer;
            font-size: 14px;

            &:hover {
                color: #3a84ff;
            }
        }

        .bk-check-notice {
            border-bottom: 2px solid #3a84ff;
            color: #3a84ff;
        }
    }
</style>
