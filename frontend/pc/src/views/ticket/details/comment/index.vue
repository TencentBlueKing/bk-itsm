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
    <div class="wang-editor-template">
        <ul v-show="isShowSelect" class="select-pattern">
            <li v-for="(item, index) in selectPatternList" :key="index" @click="postComment(item.type)">
                <i :class="item.icon"></i>
                <span>{{ item.name}}</span>
                <p>{{ item.docs }}</p>
            </li>
        </ul>
        <editor v-if="isShowEditor" ref="editorAdd" :editor-id="'editor1'" @changebuttonStatus="changebuttonStatus"></editor>
        <bk-button v-show="isShowEditor" class="submit" :theme="'primary'" @click="submit">{{ isEditEditor ? $t('m["发布"]') : $t('m["返回"]') }}</bk-button>
        <bk-divider></bk-divider>
        <div>{{ $t('m["全部评论"]') }}</div>
        <ul v-bkloading="{ isLoading: commentLoading }">
            <li v-for="(item, index) in commentList" :key="index">
                <comment-item
                    :cur-comment="item"
                    @refreshComment="refreshComment"
                    @editComment="editComment">
                </comment-item>
            </li>
        </ul>
        <div v-if="commentList.length === 0" class="no-comment">暂无评论</div>
        <bk-dialog
            v-model="isEdit"
            :title="editType === 'edit' ? '编辑评论' : '回复评论'"
            width="800"
            theme="primary"
            :mask-close="false"
            @confirm="submitEdit">
            <editor ref="editorEdit" :editor-id="'editor2'"></editor>
        </bk-dialog>
    </div>
</template>
<script>
    import editor from './editor.vue'
    import commentItem from './commentItem.vue'
    export default {
        name: 'ticketComment',
        components: {
            commentItem,
            editor
        },
        props: {
            commentId: [Number, String],
            commentList: Array,
            ticketInfo: Object,
            ticketId: [Number, String],
            commentLoading: Boolean
        },
        data () {
            return {
                // commentId: '',
                curCommentId: '',
                commentType: '', // 评论类型
                isShowSelect: true,
                isShowEditor: false, // 打开富文本
                isEditEditor: false, // 是否编辑文本
                selectPatternList: [
                    {
                        type: 'INSIDE',
                        icon: 'bk-itsm-icon icon-itsm-icon-lock-two',
                        name: '内部评论',
                        docs: '发布的评论仅内部人员可用'
                    },
                    {
                        type: 'PUBLIC',
                        icon: 'bk-itsm-icon icon-itsm-icon-lock-two public-icon',
                        name: '外部评论',
                        docs: '发布的评论所有人可见'
                    }
                ],
                // commentList: [],
                editType: '',
                isEdit: false
            }
        },
        methods: {
            editComment (curComment, type) {
                const _this = this.$refs.editorEdit.editor
                _this.txt.clear()
                this.editType = type
                this.curCommentId = curComment.id
                if (type === 'edit') _this.txt.html(curComment.content)
                // 新增回复评论的类型取决于父级类型
                this.commentType = curComment.remark
                this.isEdit = true
            },
            changebuttonStatus (val) {
                this.isEditEditor = val
            },
            submitEdit () {
                const _this = this.$refs.editorEdit.editor
                const text = _this.txt.text()
                this.editorEditData = ''
                _this.txt.clear()
                let url = ''
                const params = {
                    content: text,
                    users: [],
                    remark_type: this.commentType
                }
                if (this.editType === 'edit') {
                    params.id = this.curCommentId
                    url = 'ticket/updateTicketComment'
                } else {
                    params.ticket_id = this.ticketId
                    params.parent__id = this.curCommentId
                    url = 'ticket/addTicketComment'
                }
                this.$store.dispatch(url, params).then(res => {
                    this.refreshComment()
                })
            },
            refreshComment () {
                this.isEditEditor = false
                this.$emit('refreshComment')
            },
            postComment (type) {
                if (!this.$route.query.project_id && type === 'INSIDE') {
                    this.$bkMessage({
                        message: this.$t('m["你当前无法发表内部评论"]'),
                        theme: 'warning '
                    })
                    return
                }
                this.commentType = type
                this.isShowSelect = false
                this.isShowEditor = true
            },
            submit () {
                // 评论内容
                this.isShowEditor = false
                if (this.$refs.editorAdd) {
                    const _this = this.$refs.editorAdd.editor
                    const text = _this.txt.text()
                    this.editorData = ''
                    this.isShowSelect = true
                    _this.txt.clear()
                    const params = {
                        content: text,
                        ticket_id: this.ticketId,
                        parent__id: this.commentId,
                        remark_type: this.commentType,
                        users: []
                    }
                    if (text) {
                        this.$store.dispatch('ticket/addTicketComment', params).then(res => {
                            this.refreshComment()
                        })
                    }
                }
            }
        }
    }
</script>
<style scoped lang="scss">
    .public-icon {
        color: #e2e3e5;
    }
    .wang-editor-template {
        padding: 20px;
        .select-pattern {
            cursor: pointer;
            text-align: center;
            display: flex;
            height: 160px;
            background-color: #fafbfd;
            border-radius: 2px;
            border: 1px solid #e0e1e8;
            li{
                display: flex;
                flex: 1;
                padding: 40px;
                flex-direction: column;
                &:hover {
                    background-color: #f0f1f5;
                }
                i{
                    font-size: 30px;
                }
                span {
                    font-weight: 400;
                    color: #3a84ff;
                    font-size: 14px;
                    line-height: 24px;
                }
                p {
                    color: #979ba5;
                    font-size: 12px;
                    line-height: 20px;
                }
            }
        }
        .submit {
            margin: 10px 0;
        }
        .no-comment {
            height: 50px;
            text-align: center;
            font-size: 14px;
            line-height: 50px;
            color: #979ba5;
        }
    }
</style>
