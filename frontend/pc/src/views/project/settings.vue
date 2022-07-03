<template>
    <div class="bk-itsm-service">
        <div class="is-title">
            <p class="bk-come-back">
                {{ $t('m["设置"]') }}
            </p>
        </div>
        <div class="itsm-page-content">
            <div class="bk-itsm-version" v-if="versionStatus">
                <i class="bk-icon icon-info-circle"></i>
                <span>{{ $t('m.home["“功能开关”可以自定义启停以下ITSM功能模块，关闭后，该模块对应的所有的功能将被隐藏。"]') }}</span>
                <i class="bk-icon icon-close" @click="closeVersion"></i>
            </div>
            <div class="project-setting">
                <p class="bk-setting-title">{{ $t('m.home["功能开关"]') }}</p>
                <div class="bk-setting-content">
                    <div class="bk-setting-btn" v-for="(item,key) in moduleInfo" v-if="item.isAvailable" :key="key">
                        <span class="bk-clear-info">
                            {{ item.title }}
                        </span>
                        <bk-switcher
                            v-model="item.open"
                            size="small"
                            :on-text="$t(`m.home['打开']`)"
                            :off-text="$t(`m.home['关闭']`)"
                            @change="allSwitchChange($event,key)"></bk-switcher>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        name: 'Settings',
        data () {
            return {
                versionStatus: true,
                // 开关功能对照表
                switchKeyMap: {
                    SYS_FILE_PATH: 'systemPath',
                    FLOW_PREVIEW: 'preview',
                    WIKI_SWITCH: 'wiki',
                    CHILD_TICKET_SWITCH: 'inherit',
                    SLA_SWITCH: 'sla',
                    TRIGGER_SWITCH: 'trigger',
                    TASK_SWITCH: 'task',
                    FIRST_STATE_SWITCH: 'basic',
                    TABLE_FIELDS_SWITCH: 'module',
                    SMS_COMMENT_SWITCH: 'smsComment'
                },
                moduleInfo: {
                    basic: {
                        id: '',
                        title: this.$t('m.home["提单信息展示开关："]'),
                        open: false,
                        isAvailable: true
                    },
                    module: {
                        id: '',
                        title: this.$t('m.home["基础信息展示开关："]'),
                        open: false,
                        isAvailable: true
                    },
                    inherit: {
                        id: '',
                        title: this.$t('m.home["母子单功能开关："]'),
                        open: false,
                        isAvailable: true
                    },
                    preview: {
                        id: '',
                        title: this.$t('m.home["流程预览功能开关："]'),
                        open: false,
                        isAvailable: true
                    },
                    sla: {
                        id: '',
                        title: this.$t('m.home["SLA功能开关："]'),
                        open: false,
                        isAvailable: true
                    },
                    trigger: {
                        id: '',
                        title: this.$t('m.home["触发器功能开关："]'),
                        open: false,
                        isAvailable: true
                    },
                    smsComment: {
                        id: '',
                        title: this.$t('m.home["短信评论开关："]'),
                        open: false,
                        isAvailable: true
                    }
                }
            }
        },
        mounted () {
            this.init()
        },
        methods: {
            init () {
                this.getSettingsDate()
            },
            async getSettingsDate () {
                const res = await this.$store.dispatch('project/getProjectSettings', { project_key: this.$route.query.project_id })
                const tempObj = {}
                const skipList = ['IS_ORGANIZATION', 'WIKI_SWITCH', 'TASK_SWITCH']
                const result = res.data.filter(item => !skipList.includes(item.key))
                result.forEach(item => {
                    if (item.key !== 'SERVICE_SWITCH' && this.switchKeyMap[item.key]) {
                        this.moduleInfo[this.switchKeyMap[item.key]].open = tempObj[item.key] = item.value === 'on'
                        this.moduleInfo[this.switchKeyMap[item.key]].id = item.id || ''
                    }
                })
                this.$store.commit('project/setprojectSwitch', tempObj)
            },
            allSwitchChange (status, type) {
                const id = this.moduleInfo[type].id
                const params = {
                    id,
                    project: this.$route.query.project_id,
                    project_key: this.$route.query.project_id,
                    type: 'FUNCTION',
                    key: Object.keys(this.switchKeyMap)[Object.values(this.switchKeyMap).indexOf(type)],
                    value: status ? 'on' : 'off'
                }
                this.$store.dispatch('project/updateProjectSettings', params).then(res => {
                    this.$bkMessage({
                        message: this.$t(`m.home["更新成功"]`),
                        theme: 'success'
                    })
                }).finally(() => {
                    this.getSettingsDate()
                })
            },
            closeVersion () {
                this.versionStatus = false
            }
        }
    }
</script>

<style lang='scss' scoped>
.project-setting {
    border: 1px solid #dde4eb;;
    padding: 0 20px;
    background-color: #ffffff;
    .bk-setting-title {
        line-height: 40px;
        padding-left: 20px;
        border-bottom: 1px solid #dfe0e5;
        font-size: 16px;
        color: #424950;
    }
    .bk-setting-content {
        padding: 16px 20px;
        .bk-setting-btn {
            margin-top: 15px;
            font-size: 14px;
            .bk-clear-info {
                color: #656770;
            }
        }
    }
}
</style>
