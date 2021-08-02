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
    <bk-dialog
        :value="isShow"
        render-directive="if"
        :title="title"
        :width="600"
        :auto-close="false"
        :mask-close="false"
        :loading="editProjectPending"
        @confirm="onEditProjectConfirm"
        @cancel="$emit('cancel')">
        <div class="project-form">
            <bk-form
                ref="projectForm"
                form-type="vertical"
                :model="projectForm"
                :rules="projectRules">
                <bk-form-item property="name" :label="$t(`m['项目名称']`)" :required="true">
                    <bk-input
                        v-model="projectForm.name"
                        :placeholder="$t(`m['请输入50个字符以内的项目名称']`)">
                    </bk-input>
                </bk-form-item>
                <bk-form-item property="key" :label="$t(`m['项目代号']`)" :required="true">
                    <bk-input
                        v-model="projectForm.key"
                        :disabled="!!project.key"
                        :placeholder="$t(`m['请输入50个英文字符以内的项目代号']`)">
                    </bk-input>
                </bk-form-item>
                <bk-form-item property="desc" :label="$t(`m['项目说明']`)">
                    <bk-input
                        v-model="projectForm.desc"
                        type="textarea"
                        :maxlength="100"
                        :label="$t(`m['请输入项目说明']`)"
                        :placeholder="$t(`m['请输入项目说明']`)">
                    </bk-input>
                </bk-form-item>
            </bk-form>
        </div>
    </bk-dialog>
</template>
<script>
    import { deepClone } from '@/utils/util'
    import { errorHandler } from '@/utils/errorHandler.js'

    export default {
        name: 'EditProjectDialog',
        props: {
            isShow: {
                type: Boolean,
                default: false
            },
            title: String,
            project: {
                type: Object,
                default () {
                    return {
                        name: '',
                        key: '',
                        desc: '',
                        color: ''
                    }
                }
            }
        },
        data () {
            return {
                projectForm: deepClone(this.project),
                editProjectPending: false,
                projectRules: {
                    name: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'blur'
                        },
                        {
                            max: 50,
                            message: '不能多于50个字符',
                            trigger: 'blur'
                        }
                    ],
                    key: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'blur'
                        },
                        {
                            max: 50,
                            message: '不能多于50个字符',
                            trigger: 'blur'
                        },
                        {
                            regex: /^[a-zA-Z]*$/,
                            message: '只能包含英文字符',
                            trigger: 'blur'
                        }
                    ],
                    desc: [
                        {
                            max: 100,
                            message: '不能多于100个字符',
                            trigger: 'blur'
                        }
                    ]
                }
            }
        },
        watch: {
            isShow (val) {
                if (val) {
                    this.projectForm = deepClone(this.project)
                }
            }
        },
        methods: {
            onEditProjectConfirm () {
                this.$refs.projectForm.validate().then(async (result) => {
                    if (result) {
                        this.editProjectPending = true
                        const url = this.project.key ? 'project/updateProject' : 'project/createProject'
                        try {
                            await this.$store.dispatch(url, this.projectForm)
                            this.$emit('confirm', this.projectForm.key)
                        } catch (e) {
                            errorHandler(e, this)
                        } finally {
                            this.editProjectPending = false
                        }
                    }
                })
            }
        }
    }
</script>
