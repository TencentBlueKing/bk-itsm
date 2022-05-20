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
    <div class="trigger-dialog-box">
        <bk-dialog v-model="isTrigger"
            width="800"
            theme="primary"
            :mask-close="false"
            :auto-close="false"
            header-position="left"
            :title="trigger.component_name"
            @confirm="confirmTrigger">
            <p style="margin-bottom: 10px"> 触发器名称：{{ trigger.display_name }}</p>
            <bk-form :form-type="'horizontal'"
                :label-width="100"
                ref="conductorForm">
                <template v-if="item.key === 'api'">
                    <api-call :item="item">
                    </api-call>
                </template>
                <template v-else-if="item.key === 'modify_field'">
                    <modify-field :field-schema="item.field_schema"></modify-field>
                </template>
                <template v-else>
                    <template v-for="(itemInfo, index) in item.field_schema">
                        <!-- 对于多层嵌套和单层嵌套的区别 -->
                        <template v-if="itemInfo.type === 'SUBCOMPONENT'">
                            <send-message :key="index"
                                :item-info="itemInfo">
                            </send-message>
                        </template>
                        <template v-else>
                            <bk-form-item :ext-cls="itemInfo.required ? 'bk-field-schema mb20' : 'bk-field-schema no-require-item mb20'"
                                :label="itemInfo.name"
                                :required="itemInfo.required"
                                :key="index"
                                :desc="itemInfo.tips">
                                <change-conductor
                                    :item-info="itemInfo">
                                </change-conductor>
                            </bk-form-item>
                        </template>
                    </template>
                </template>
            </bk-form>
        </bk-dialog>
    </div>
</template>
<script>
    import { errorHandler } from '../../utils/errorHandler'
    import sendMessage from '../../views/processManagement/publicTrigger/components/sendMessage.vue'
    import apiCall from '../../views/processManagement/publicTrigger/components/apiCall.vue'
    import changeConductor from '../../views/processManagement/publicTrigger/components/changeConductor.vue'
    export default {
        name: 'TicketTriggerDialog',
        components: {
            sendMessage,
            apiCall,
            changeConductor
        },
        props: {
            item: Object
        },
        data () {
            return {
                isTrigger: false,
                trigger: ''
            }
        },
        methods: {
            openDialog (trigger) {
                this.isTrigger = true
                this.trigger = trigger
            },
            executeTrigger (trigger) {
                const params = {}
                const paramsItem = {}
                paramsItem.name = this.item.name
                
                // paramsItem.display_name = response.performData.displayName
                // paramsItem.operate_type = response.performData.runMode
                // paramsItem.can_repeat = response.performData.repeat === 'more'
                // 内容
                // paramsItem.component_type = response.wayInfo.key
                paramsItem.params = []
                this.$store.dispatch('trigger/executeTrigger', { params, id: this.trigger.id }).then(() => {
                    this.$bkMessage({
                        message: '执行成功',
                        theme: 'success'
                    })
                    this.$store.commit('taskHistoryRefreshFunc')
                    if (trigger.need_refresh || !trigger.can_repeat) {
                        this.$emit('init-info')
                    }
                }).catch((res) => {
                    errorHandler(res, this)
                })
            },
            confirmTrigger () {
                this.executeTrigger()
                this.trigger = false
            }
        }
    }
</script>
<style lang='scss' scoped>

</style>
