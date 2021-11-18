<template>
    <div class="comment">
        <div class="comment-info">
            <!-- <el-avatar src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"></el-avatar> -->
            <img class="user-img" src="" alt="">
            <p><span class="user-name">windyhasda  </span><span class="issue-time">发布于 2020-05-15</span><i v-if="curComment.remark === 'INSIDE'" class="tip bk-itsm-icon icon-icon-no-permissions"> 仅内部可见</i></p>
            <div
                v-if="curComment.update_log.length"
                v-bk-tooltips.top-start="{
                    placement: 'top-start',
                    content: '鼠标移入显示移出消失，浮层不承载复杂文本和操作。'
                }"
                class="edited">
                <span>已被编辑</span>
            </div>
            <div class="reply-praise">
                <i class="bk-itsm-icon icon-itsm-icon-speak" @click="$emit('editComment', curComment , 'add')"></i>
                <i class="bk-itsm-icon icon-itsm-icon-smeil" @click="endorse"></i>
                <ul class="expression">
                    <li>😘</li>
                    <li>😭</li>
                    <li>😊</li>
                    <li>😁</li>
                    <li>👍</li>
                </ul>
            </div>
        </div>
        <div class="comment-content">
            <p>{{ curComment.content }}</p>
        </div>
        <div class="comment-reply">
            <div class="comment-message" v-for="(item, index) in curComment.children" :key="index">
                <span>“ 回复 miffyyang 的评论：</span>
                <p>{{ item.content }}</p>
            </div>
        </div>
        <div class="operation">
            <span @click="$emit('editComment', curComment, 'edit')">编辑</span>|
            <span @click="isShowDeleteDialog(1)">删除</span>
        </div>
        <bk-dialog
            ext-cls="delete-dialog"
            width="400"
            :show-footer="false"
            v-model="deleteCommentDialog">
            <i class="bk-itsm-icon icon-info-fail"></i>
            <div class="delete-tip">确认删除该条评论？</div>
            <div class="delete-option">
                <bk-button :theme="'primary'" @click="deleteComment(curComment.id)">确定</bk-button>
                <bk-button @click="isShowDeleteDialog(0)">取消</bk-button>
            </div>
        </bk-dialog>
    </div>
</template>

<script>
    export default {
        name: 'commentItem',
        props: {
            curComment: Object
        },
        data () {
            return {
                isEditComment: false,
                deleteCommentDialog: false
            }
        },
        mounted () {
        },
        methods: {
            deleteComment (id) {
                this.$store.dispatch('ticket/deleteTicketComment', id).then(res => {
                    this.$emit('refreshComment')
                    this.deleteCommentDialog = false
                })
            },
            endorse () {
                console.log('agree')
            },
            isShowDeleteDialog (val) {
                this.deleteCommentDialog = !!val
            }
        }
    }
</script>

<style scoped lang="scss">
.comment {
    width: 100%;
    margin: 20px 0;
    color: #6d6f77;
    font-size: 12px;
    .comment-info {
        display: flex;
        line-height: 22px;
        .user-img {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            margin-right: 10px;
        }
        .user-name {
            color: #3a3b41;
        }
        .tip {
            margin-left: 20px;
        }
        .edited {
            margin: 0 20px;
            height: 22px;
            width: 68px;
            text-align: center;
            line-height: 22px;
            background-color: #dcdee5;
        }
        .issue-time {
            color: #989ca6;
        }
        .reply-praise {
            flex: 1;
            display: flex;
            flex-direction: row-reverse;
            font-size: 18px;
            line-height: 28px;
            .expression {
                font-size: 16px;
                border: 1px solid #dcdee5;
                border-radius: 14px;
                width: 151px;
                height: 28px;
                text-align: center;
                display: inline-block;
                li {
                    cursor: pointer;
                    width: 20%;
                    float: left;
                }
            }
            i {
                cursor: pointer;
                display: inline-block;
                height: 28px;
                line-height: 28px;
                margin: 0 5px;
            }
        }
    }
    .comment-content {
        margin-left: 40px;
        min-height: 22px;
    }
    .comment-reply {
        line-height: 28px;
        margin-left: 40px;
        .comment-message {
            padding: 10px 24px 10px 16px;
            min-height: 74px;
            margin-bottom: 2px;
            background: #f5f7fa;
            white-space: pre-wrap;
            word-break: break-all;
            margin-bottom: 5px;
            &:hover{
                background: #EAEBF0;
        }
        }
        p {
            margin-left: 24px;
        }
    }
    .operation {
        margin: 8px 0px 8px 40px;
        span {
            cursor: pointer;
            margin: 0 2px;
        }
    }
}
/deep/ .bk-dialog-body {
        text-align: center;
    }
    .icon-info-fail {
        font-size: 42px;
        color: #ffe8c3;
    }
    .delete-tip {
        margin: 10px 0;
        font-size: 20px;
        line-height: 30px;
    }
</style>
