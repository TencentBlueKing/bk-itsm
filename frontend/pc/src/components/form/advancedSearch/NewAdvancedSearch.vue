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
    <div class="bk-search-info">
        <div class="operate-wrapper-item">
            <div class="filter-content">
                <div class="slot-content">
                    <slot></slot>
                </div>
                <bk-input
                    data-test-id="search_input_enter"
                    :clearable="true"
                    :right-icon="'bk-icon icon-search'"
                    :placeholder="searchForms[0].desc"
                    v-model="searchForms[0].value"
                    @enter="onSearchClick"
                    @clear="onClearClick">
                </bk-input>
                <bk-button
                    data-test-id="search_button_conditions"
                    :title="$t(`m.deployPage['更多筛选条件']`)"
                    icon=" bk-itsm-icon icon-search-more"
                    class="ml10 filter-btn"
                    @click="onShowSearchMore">
                </bk-button>
                <i data-test-id="ticket_button_highlightSetting" style="margin:0 10px;cursor: pointer;color:#3A84FF" class="bk-icon icon-cog-shape" @click="isHighlightSetting = true"></i>
            </div>
        </div>
        <!-- 高级搜索 -->
        <collapse-transition>
            <div class="bk-filter" v-if="showMore">
                <bk-form
                    :label-width="200"
                    form-type="vertical"
                    ref="dynamicForm">
                    <template>
                        <div class="bk-filter-line"
                            v-for="(item, index) in searchForms"
                            :key="index">
                            <bk-form-item :label="item.name" v-if="item.type === 'input'">
                                <bk-input v-model="item.value"
                                    :placeholder="item.placeholder"
                                    @change="onFormChange($event, item)">
                                </bk-input>
                            </bk-form-item>
                            <bk-form-item :label="item.name" v-if="item.type === 'select'">
                                <bk-select
                                    searchable
                                    :placeholder="item.placeholder"
                                    :show-select-all="item.multiSelect"
                                    :multiple="item.multiSelect"
                                    v-model="item.value"
                                    @change="onFormChange($event, item)">
                                    <bk-option v-for="option in item.list"
                                        :key="option.key"
                                        :id="option.key"
                                        :name="option.name">
                                    </bk-option>
                                </bk-select>
                            </bk-form-item>
                            <bk-form-item :label="item.name" v-if="item.type === 'datetime'">
                                <bk-date-picker
                                    style="width: 100%;"
                                    v-model="item.value"
                                    :placeholder="item.placeholder"
                                    :type="'datetimerange'"
                                    @change="onFormChange($event, item)">
                                </bk-date-picker>
                            </bk-form-item>
                            <!-- 级联类型 -->
                            <bk-form-item :label="item.name" v-if="item.type === 'cascade'">
                                <common-cascade
                                    style="width: 100%;"
                                    v-model="item.value"
                                    :options="item.list"
                                    :iscollect_first="false"
                                    :iscollect_two="false"
                                    :isshow-number="false"
                                    :isactive="true"
                                    @change="onFormChange($event, item)">
                                </common-cascade>
                            </bk-form-item>
                            <!-- 人员 -->
                            <bk-form-item :label="item.name" v-if="item.type === 'member'">
                                <member-select
                                    v-model="item.value"
                                    :multiple="false"
                                    :placeholder="item.placeholder"
                                    @change="onFormChange($event, item)"></member-select>
                            </bk-form-item>
                        </div>
                    </template>
                </bk-form>
                <!-- 查询清空 -->
                <div class="bk-filter-btn">
                    <bk-button theme="primary"
                        data-test-id="highlight_button_search"
                        :title="$t(`m.deployPage['查询']`)"
                        @click="onSearchClick">
                        {{ $t('m.deployPage["查询"]') }}
                    </bk-button>
                    <bk-button theme="default"
                        data-test-id="highlight_button_clear"
                        :title="$t(`m.deployPage['清空']`)"
                        @click="onClearClick">
                        {{ $t('m.deployPage["清空"]') }}
                    </bk-button>
                </div>
            </div>
        </collapse-transition>
        <!-- 单据高亮设置 -->
        <bk-dialog
            v-model="isHighlightSetting"
            width="560"
            :draggable="false"
            @confirm="highlightSettingConfirm">
            <p slot="header" style="text-align: left;">
                {{$t(`m.slaContent["单据高亮设置"]`)}}
            </p>
            <div class="bk-highlight-setting">
                <div class="bk-itsm-version">
                    <i class="bk-icon icon-info-circle"></i>
                    <span>{{ $t('m.slaContent["对特殊单据，如预警单和超时单设置颜色高亮提醒。"]') }}</span>
                </div>
                <div class="bk-color-box">
                    <span>{{ $t('m.slaContent["预警单据背景颜色"]') }} :</span>
                    <bk-color-picker v-model="highlightObj.reply_timeout_color"></bk-color-picker>
                </div>
                <div class="bk-color-box">
                    <span>{{ $t('m.slaContent["超时单据背景颜色"]') }} :</span>
                    <bk-color-picker v-model="highlightObj.handle_timeout_color"></bk-color-picker>
                </div>
            </div>
        </bk-dialog>
    </div>
</template>

<script>
    import collapseTransition from '../../../utils/collapse-transition'
    import commonCascade from '../../../views/commonComponent/commonCascade'
    import memberSelect from '../../../views/commonComponent/memberSelect'
    import commonMix from '../../../views/commonMix/common.js'
    import { isEmpty } from '@/utils/util.js'

    export default {
        name: 'searchInfo',
        components: {
            collapseTransition,
            commonCascade,
            memberSelect
        },
        mixins: [commonMix],
        props: {
            forms: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                isHighlightSetting: false,
                highlightObj: {
                    reply_timeout_color: '#FFF5E3',
                    handle_timeout_color: '#FFECEC'
                },
                showMore: false,
                searchWord: '',
                searchForms: []
            }
        },
        watch: {
            forms: {
                handler (val) {
                    this.searchForms = val.filter(item => item.display)
                },
                deep: true,
                immediate: true
            }
        },
        created () {
            this.getTicketHighlight()
        },
        methods: {
            // 过滤参数
            getParams () {
                const params = {}
                // 过滤条件
                for (const item of this.searchForms) {
                    if (isEmpty(item.value)) {
                        continue
                    }
                    if (item.type === 'cascade') { // 服务目录
                        params[item.key] = item.value[item.value.length - 1].id
                    } else if (item.type === 'datetime') { // 时间
                        if (item.value[0] && item.value[1]) {
                            const gteTime = this.standardTime(item.value[0])
                            const lteTime = this.standardTime(item.value[1])
                            params['create_at__gte'] = gteTime
                            params['create_at__lte'] = lteTime
                        }
                    } else if (Array.isArray(item.value)) { // 数组
                        params[item.key] = item.value.join(',')
                    } else {
                        params[item.key] = item.value
                    }
                }
                return params
            },
            onSearchClick () {
                this.$emit('search', this.getParams())
            },
            onClearClick () {
                this.searchForms.forEach(item => {
                    item.value = item.multiSelect ? [] : ''
                })
                this.$emit('search', {})
                this.$emit('clear')
            },
            // 展开高级搜索
            onShowSearchMore () {
                this.showMore = !this.showMore
            },
            // change 事件，执行 form 中的回调函数
            onFormChange (val, form) {
                this.$emit('formChange', form.key, val, this.searchForms)
            },
            getTicketHighlight () {
                this.$store.dispatch('sla/getTicketHighlight').then(({ data }) => {
                    this.highlightObj = data.items[0]
                }).catch(res => {
                    this.$bkMessage({
                        message: res.data.msg,
                        theme: 'error'
                    })
                })
            },
            highlightSettingConfirm () {
                this.isHighlightSetting = false
                this.$store.dispatch('sla/updateTicketHighlight', this.highlightObj).then(({ result, data }) => {
                    if (result) {
                        this.$bkMessage({
                            message: data.msg || this.$t(`m.slaContent['成功更新单据高亮颜色']`),
                            theme: 'success'
                        })
                        this.$emit('onChangeHighlight')
                    } else {
                        this.getTicketHighlight()
                    }
                }).catch(res => {
                    this.$bkMessage({
                        message: res.data.msg,
                        theme: 'error'
                    })
                })
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import '../../../scss/mixins/clearfix.scss';
    @import '../../../scss/mixins/scroller.scss';

    .bk-search-info {
        position: relative;
        width: 100%;
    }
    .filter-content {
        display: flex;
        align-items: center;
        .slot-content {
            flex: 1;
        }
        /deep/ .bk-form-control {
            width: 400px;
            margin-left: 5px;
            .bk-form-input {
                width: 400px;
            }
        }
        /deep/ .filter-btn {
            height: 32px;
            width: 32px;
            display: flex;
            justify-content: center;
            line-height: 26px;
            .bk-icon {
                color: #979ba5;
                font-size: 12px;
            }
        }
    }
    .bk-filter {
        position: relative;
        box-sizing: content-box;
        color: #737987;
        background-color: #ffffff;
        margin-top: 12px;
        padding: 10px;
        padding-right: 0px;
        transition: .3s height ease-in-out, .3s padding-top ease-in-out, .3s padding-bottom ease-in-out;
        @include clearfix;
        .bk-filter-line {
            float: left;
            width: 50%;
            padding-right: 10px;
            height: 63px;
        }
        .bk-filter-btn {
            margin-top: 10px;
        }
    }
    @media screen and (min-width: 960px) and (max-width: 1380px) {
        .bk-filter {
            .bk-filter-line {
                width: 50%;
            }
        }
    }
    @media screen and (min-width: 1380px) and (max-width: 1680px) {
        .bk-filter {
            .bk-filter-line {
                width: 33.33%;
            }
        }
    }
    @media screen and (min-width: 1680px) {
        .bk-filter {
            .bk-filter-line {
                width: 25%;
            }
        }
    }
    .bk-highlight-setting {
        position: relative;
        padding-top: 14px;
        .bk-itsm-version {
            position: absolute;
            left: 0;
            top: -26px;
            width: 100%;
        }
        .bk-color-box {
            padding-left: 20px;
            color: #63656E;
            margin-top: 30px;
            span {
                margin-right: 8px;
            }
        }
    }
</style>
