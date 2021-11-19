<template>
    <div class="comment">
        <div class="comment-info">
            <div class="author" :style="{ background: randomHex() }">{{ avatar(curComment.creator) }}</div>
            <p><span class="user-name">{{ curComment.creator}}  </span><span class="issue-time">{{ $t('m["发布于"]') }} {{ curComment.create_at }}</span><i v-if="curComment.remark === 'INSIDE'" class="tip bk-itsm-icon icon-icon-no-permissions"> {{ $t('m["仅内部可见"]') }}</i></p>
            <div
                v-if="curComment.update_log.length"
                v-bk-tooltips.top-start="{
                    placement: 'top-start',
                    content: curComment.update_log
                }"
                class="edited">
                <span>{{ $t('m["已被编辑"]') }}</span>
            </div>
            <div class="reply-praise">
                <i class="bk-itsm-icon icon-itsm-icon-speak" title="回复" @click="$emit('editComment', curComment , 'add')"></i>
                <i class="bk-itsm-icon icon-itsm-icon-smeil" title="暂不支持" @click="endorse"></i>
                <!-- <ul v-if="isAgree" class="expression">
                    <li>😘</li>
                    <li>😭</li>
                    <li>😊</li>
                    <li>😁</li>
                    <li>👍</li>
                </ul> -->
            </div>
        </div>
        <div class="comment-content">
            <p>{{ curComment.content }}</p>
        </div>
        <div class="comment-reply">
            <div class="comment-message" v-for="(item, index) in curComment.children" :key="index">
                <span>“ {{ $t('m["回复"]') }} {{ item.creator }} {{ $t('m["的评论"]') }} :</span>
                <p>{{ item.content }}</p>
            </div>
        </div>
        <div class="operation">
            <span @click="$emit('editComment', curComment, 'edit')">{{ $t('m["编辑"]') }}</span>|
            <span @click="isShowDeleteDialog(1)">{{ $t('m["删除"]') }}</span>
        </div>
        <bk-dialog
            ext-cls="delete-dialog"
            width="400"
            :show-footer="false"
            v-model="deleteCommentDialog">
            <i class="bk-itsm-icon icon-info-fail"></i>
            <div class="delete-tip">{{ $t('m["确认删除该条评论？"]') }}</div>
            <div class="delete-option">
                <bk-button :theme="'primary'" @click="deleteComment(curComment.id)">{{ $t('m["确定"]') }}</bk-button>
                <bk-button @click="isShowDeleteDialog(0)">{{ $t('m["取消"]') }}</bk-button>
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
                deleteCommentDialog: false,
                isAgree: false
            }
        },
        methods: {
            randomHex () {
                return `#${Math.floor(Math.random() * 0xffffff).toString(16).padEnd(6, '0')}`
            },
            avatar (str) {
                return str.substr(0, 1).toLocaleUpperCase()
            },
            deleteComment (id) {
                this.$store.dispatch('ticket/deleteTicketComment', id).then(res => {
                    this.$emit('refreshComment')
                    this.deleteCommentDialog = false
                })
            },
            endorse () {
                this.isAgree = !this.isAgree
                console.log('agree', '暂不支持')
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
        .author {
            width: 30px;
            height: 30px;
            border: 1px solid #dcdee5;
            border-radius: 50%;
            margin-right: 10px;
            line-height: 28px;
            font-size: 20px;
            text-align: center;
            opacity: 0.8;
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
