<template>
    <div class="comment">
        <div class="comment-info">
            <!-- <el-avatar src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"></el-avatar> -->
            <img class="user-img" src="" alt="">
            <p><span class="user-name">windyhasda</span><span class="issue-time">发布于 2020-05-15</span><i v-if="curComment.remark === 'INSIDE'" class="tip">及内部可见</i></p>
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
                <div></div>
                <i class="bk-itsm-icon icon-itsm-icon-speak" @click="$emit('editComment', curComment , 'add')"></i>
                <i class="bk-itsm-icon icon-itsm-icon-smeil"></i>
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
            <span @click="deleteComment(curComment.id)">删除</span>
        </div>
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
                isEditComment: false
            }
        },
        mounted () {
        },
        methods: {
            deleteComment (id) {
                this.$store.dispatch('ticket/deleteTicketComment', id).then(res => {
                    console.log('删除成功')
                    this.$emit('refreshComment')
                })
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
        .user-img {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            margin-right: 10px;
        }
        .user-name {
            color: #3a3b41;
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
            i {
                float: right;
            }
        }
    }
    .comment-content {
        margin-left: 40px;
        min-height: 22px;
    }
    .comment-reply {
        line-height: 22px;
        margin-left: 40px;
        .comment-message {
            padding: 10px 24px 10px 16px;
            height: 74px;
            margin-bottom: 2px;
            background: #f5f7fa;
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
</style>
