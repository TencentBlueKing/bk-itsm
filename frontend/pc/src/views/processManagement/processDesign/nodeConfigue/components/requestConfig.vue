<template>
    <div>
        <ul class="bk-config-tab">
            <li v-for="(item, index) in panels"
                :key="item.id"
                :class="{ 'bk-check-config': acticeTab === item.key }"
                @click="changeTab(item, index)">
                <span>{{ item.label }}</span>
                <span v-if="count[item.key]">{{ count[item.key] }}</span>
            </li>
        </ul>
        <template v-if="acticeTab === 'queryParams'">
            <div class="param-config">
                <i class="bk-itsm-icon icon-info-fail"></i>
                <span style="font-size: 12px;color: #63656e">参数说明</span>
                <params-table :list="config.queryParams"></params-table>
            </div>
        </template>
        <template v-if="acticeTab === 'auth'">
            <div class="param-config">
                <bk-radio-group v-model="config.authRadio">
                    <bk-radio :value="'None'">无需认证</bk-radio>
                    <bk-radio :value="'Token'">Bearer Token</bk-radio>
                    <bk-radio :value="'Auth'">Basic Auth</bk-radio>
                </bk-radio-group>
                <div class="bk-radio-config">
                    <div v-if="config.authRadio === 'None'">
                        <span>该请求不需要任何认证</span>
                    </div>
                    <div v-else-if="config.authRadio === 'Token'">
                        <div class="config-option" style="width: 80%">
                            <p class="mb5">TOKEN ：</p>
                            <bk-input behavior="simplicity" :clearable="true" v-model="config.auth_config.Token"></bk-input>
                        </div>
                    </div>
                    <div v-else style="display: flex">
                        <div class="config-option">
                            <p class="mb5">用户名 ：</p>
                            <bk-input behavior="simplicity" :clearable="true" v-model="config.auth_config.username"></bk-input>
                        </div>
                        <div class="config-option">
                            <p class="mb5">密码 ：</p>
                            <bk-input behavior="simplicity" type="password" :clearable="true" v-model="config.auth_config.password"></bk-input>
                        </div>
                    </div>
                </div>
            </div>
        </template>
        <template v-if="acticeTab === 'body'">
            <div class="param-config">
                <div style="display: flex; align-items: center; margin-bottom: 8px">
                    <bk-radio-group v-model="config.bodyRadio">
                        <bk-radio :value="'none'">默认</bk-radio>
                        <bk-radio :value="'form-data'">form-data</bk-radio>
                        <bk-radio :value="'x-www-form-urlencoded'">x-www-form-urlencoded</bk-radio>
                        <bk-radio :value="'raw'">raw</bk-radio>
                    </bk-radio-group>
                    <bk-select
                        v-if="config.bodyRadio === 'raw'"
                        ext-cls="select-custom"
                        :disabled="false"
                        v-model="config.rawType"
                        style="width: 100px;"
                        behavior="simplicity">
                        <bk-option v-for="(option, index) in rawList"
                            :key="index"
                            :id="option"
                            :name="option">
                        </bk-option>
                    </bk-select>
                </div>
                <template v-if="config.bodyRadio === 'form-data' || config.bodyRadio === 'x-www-form-urlencoded'">
                    <params-table :list="config.body"></params-table>
                </template>
                <template v-if="config.bodyRadio === 'raw'">
                    <textarea class="bk-form-textarea" style="resize: vertical" v-model="config.bodyValue" placeholder="请输入"></textarea>
                </template>
            </div>
        </template>
        <template v-if="acticeTab === 'headers'">
            <div class="param-config">
                <params-table :list="config.headers"></params-table>
            </div>
        </template>
        <template v-if="acticeTab === 'settings'">
            <div class="param-config">
                <div class="setting-option">
                    <p class="mb5">请求超时</p>
                    <div class="setting-content">
                        <bk-input behavior="simplicity" :clearable="true" v-model="config.settings.timeout"></bk-input>
                        <span style="margin-left: 5px">S</span>
                    </div>
                </div>
            </div>
        </template>
    </div>
</template>

<script>
    import paramsTable from './paramsTable.vue'
    export default {
        key: 'requestConfig',
        components: {
            paramsTable
        },
        props: {
            type: {
                type: String,
                default: () => 'GET'
            },
            configur: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        data () {
            return {
                acticeTab: 'queryParams',
                
                panels: [
                    { key: 'queryParams', label: '参数', count: 0 },
                    { key: 'auth', label: '认证', count: 0 },
                    { key: 'headers', label: '头信息', count: 0 },
                    { key: 'body', label: '主体', count: 0 },
                    { key: 'settings', label: '设置', count: 0 }
                ],
                list: [
                    {
                        check: false,
                        key: '',
                        value: '',
                        desc: '',
                        select: false
                    }
                ],
                rawList: ['JSON', 'HTML', 'XML', 'Text'],
                config: {
                    auth_config: {
                        Token: '',
                        username: '',
                        password: ''
                    },
                    authRadio: 'None',
                    queryParams: [
                        {
                            check: false,
                            key: '',
                            value: '',
                            desc: '',
                            select: false
                        }
                    ],
                    headers: [
                        {
                            check: false,
                            key: '',
                            value: '',
                            desc: '',
                            select: false
                        }
                    ],
                    body: [
                        {
                            check: false,
                            key: '',
                            value: '',
                            desc: '',
                            select: false
                        }
                    ],
                    bodyRadio: 'none',
                    bodyValue: '',
                    rawType: 'Text',
                    settings: {
                        timeout: 10
                    }
                }
            }
        },
        computed: {
            count () {
                const queryParams = this.config.queryParams.filter(item => item.select).length
                return { queryParams }
            }
        },
        mounted () {
            if (Object.keys(this.configur.extras).length !== 0) {
                this.config.queryParams = [...this.configur.extras.query_params, ...this.config.queryParams]
                this.config.settings.timeout = this.configur.extras.settings.timeout

                this.config.bodyRadio = this.configur.extras.body.type || 'none'
                if (this.configur.extras.body.type === 'form-data' || this.configur.extras.body.type === 'x-www-form-urlencoded') {
                    this.config.body = [...this.configur.extras.body.value, ...this.config.body]
                } else if (this.configur.extras.body.type === 'raw') {
                    this.config.rawType = this.configur.extras.body.row_type
                    this.config.bodyValue = this.configur.extras.body.value
                }
            }
        },
        methods: {
            changeTab (item, index) {
                this.acticeTab = item.key
            },
            handleDelete (row) {
                const index = this.list.indexOf(row)
                if (index !== -1) {
                    this.list.splice(index, 1)
                }
            },
            changeInput (val) {
                if (!val.check) {
                    val.check = true
                    val.select = true
                    this.list.push({
                        check: false,
                        key: '',
                        value: '',
                        desc: '',
                        select: false
                    })
                } else {
                    const { key, value, desc } = val
                    const checkList = [key, value, desc]
                    if (checkList.every(item => item === '')) {
                        this.list.pop()
                        val.check = false
                        val.select = false
                    }
                }
            }
        }
    }
</script>

<style lang='scss' scoped>
.bk-config-tab {
    border-bottom: 1px solid #dde4eb;
    height: 40px;
    margin: 0 10px;
    // background-color: #ffffff;
    li {
        float: left;
        padding: 0 10px;
        line-height: 38px;
        text-align: center;
        color: #63656e;
        cursor: pointer;
        font-size: 12px;

        &:hover {
            color: #3a84ff;
        }
    }
    .bk-check-config {
        border-bottom: 2px solid #3a84ff;
        color: #3a84ff;
    }
}
.param-config {
    // margin-top: 10px;
    padding: 10px;
    position: relative;
    .bk-radio-config {
        font-size: 12px;
        color: #63656e;
        .config-option {
            width: 40%;
            margin-right: 20px;
        }
    }
    .select-custom {
        margin-left: -380px;
    }
    .setting-option {
        font-size: 14px;
        width: 25%;
        .setting-content {
            display: flex;
        }
    }
}
.icon-info-fail {
    font-size: 16px;
    color: #63656e;
}
.bk-form-radio {
    margin-right: 30px;
}
</style>
