<template>
  <div class="comment">
    <div class="comment-info">
      <i class="author bk-itsm-icon icon-itsm-icon-my"></i>
      <!-- <div class="author" :style="{ background: randomHex() }">{{ avatar(curComment.creator) }}</div> -->
      <p>
        <span class="user-name">{{ curComment.creator}}  </span>
        <span class="issue-time">{{ $t('m["发布于"]') }} {{ createTime }}</span>
        <i v-if="curComment.remark_type === 'INSIDE'" class="tip bk-itsm-icon icon-icon-no-permissions"> {{ $t('m["仅内部可见"]') }}</i></p>
      <div
        v-if="curComment.update_log.length"
        v-bk-tooltips="{
          placement: 'top-start',
          content: curComment.update_log
        }"
        class="edited">
        <span>{{ $t('m["已被编辑"]') }}</span>
      </div>
      <div class="reply-praise">
        <i class="bk-itsm-icon icon-xiaoxi" title="回复" @click="$emit('replyComment', curComment)"></i>
        <!-- <i class="bk-itsm-icon icon-itsm-icon-smeil" title="暂不支持" @click="endorse"></i> -->
      </div>
    </div>
    <div class="comment-content">
      <div v-html="curComment.content"></div>
      <div
        v-if="curComment.hasOwnProperty('parent_creator')"
        class="comment-reply"
        @click="jumpTargetComment(curComment)">
        <div class="comment-message">
          <span><i class="bk-itsm-icon icon-yinyong"></i>{{ $t('m["回复"]') }} {{ curComment.parent_creator }} {{ $t('m["的评论"]') }} :</span>
          <div v-html="curComment.parent_content"></div>
        </div>
      </div>
    </div>
    <div class="operation">
      <span @click="$emit('editComment', curComment, 'edit')">{{ $t('m["编辑"]') }}</span>
      <i class="line"></i>
      <span @click="handleDeleteDialogShow(true)">{{ $t('m["删除"]') }}</span>
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
        <bk-button @click="handleDeleteDialogShow(false)">{{ $t('m["取消"]') }}</bk-button>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
  import dayjs from 'dayjs';
  import relativeTime from 'dayjs/plugin/relativeTime';
  export default {
    name: 'commentItem',
    props: {
      curComment: Object,
      commentList: Array,
    },
    data() {
      return {
        isEditComment: false,
        deleteCommentDialog: false,
        isAgree: false,
        timeFormat: {
          'seconds ago': this.$t('m[\'秒钟前\']'),
          'minutes ago': this.$t('m[\'分钟前\']'),
          'minute ago': this.$t('m[\'分钟前\']'),
          'hours ago': this.$t('m[\'小时前\']'),
          'hour ago': this.$t('m[\'小时前\']'),
          'days ago': this.$t('m[\'天前\']'),
          'day ago': this.$t('m[\'天前\']'),
          'months ago': this.$t('m[\'月前\']'),
          'month ago': this.$t('m[\'月前\']'),
          'years ago': this.$t('m[\'年前\']'),
          'year ago': this.$t('m[\'年前\']'),
        },
      };
    },
    computed: {
      // parentComment () {
      //     const parentComment = this.commentList.find(item => item.id === this.curComment.parent)
      //     if (parentComment && parentComment.remark_type === 'ROOT') {
      //         return null
      //     }
      //     return parentComment
      // },
      createTime() {
        dayjs.extend(relativeTime);
        const timestamp = dayjs(this.curComment.create_at).unix() * 1000;
        const time = dayjs(timestamp).fromNow();
        // 0 to 44 seconds
        const timeStr = time.split(' ')[1];
        const timeType = time.split(' ').slice(1, 3)
          .join(' ');
        if (timeStr === 'few') {
          return this.$t('m[\'刚刚\']');
        }
        if (time.split(' ')[0] === 'an' || time.split(' '[0] === 'a')) {
          return `${1} ${this.timeFormat[timeType]}`;
        }
        return `${time.split(' ')[0]} ${this.timeFormat[timeType]}`;
      },
    },
    methods: {
      randomHex() {
        let authorbgc;
        do {
          authorbgc = `#${Math.floor(Math.random() * 0xffffff).toString(16)
            .padEnd(6, '0')}`;
        }
        while (authorbgc === '#ffffff');
        return authorbgc;
      },
      avatar(str) {
        return str.substr(0, 1).toLocaleUpperCase();
      },
      deleteComment(id) {
        this.$store.dispatch('ticket/deleteTicketComment', id).then(() => {
          this.$emit('refreshComment');
          this.deleteCommentDialog = false;
        });
      },
      endorse() {
        this.isAgree = !this.isAgree;
        console.log('agree', '暂不支持');
      },
      handleDeleteDialogShow(val) {
        this.deleteCommentDialog = val;
      },
      jumpTargetComment(curComment) {
        this.$emit('jumpTargetComment', curComment);
      },
    },
  };
</script>

<style scoped lang="scss">
.icon-itsm-icon-one-five {
    display: inline-block;
    width: 1px;
    margin: 0 12px;
}
.icon-itsm-icon-my {
    display: inline-block;
    height: 30px;
    width: 30px;
    font-size: 30px;
    color: #c4c6cc;
}
.comment {
    width: 100%;
    color: #6d6f77;
    font-size: 12px;
    .comment-info {
        display: flex;
        line-height: 22px;
        .author {
            width: 30px;
            height: 30px;
            // border: 1px solid #dcdee5;
            border-radius: 50%;
            margin-right: 10px;
            line-height: 30px;
            font-size: 30px;
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
            margin-left: 20px;
            height: 22px;
            width: 68px;
            text-align: center;
            line-height: 22px;
            background-color: #f0f1f5;
            border-radius: 2px;
            &:hover {
                background-color: #dcdee5;
            }
        }
        .issue-time {
            color: #989ca6;
        }
        .reply-praise {
            flex: 1;
            display: flex;
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
                line-height: 24px;
                margin: 0 10px;
            }
        }
    }
    .comment-content {
        margin-left: 40px;
        min-height: 22px;
    }
    .comment-reply {
        line-height: 28px;
        cursor: pointer;
        margin: 8px 0;
        .comment-message {
            padding: 10px 24px 10px 16px;
            min-height: 74px;
            margin-bottom: 2px;
            background: #f5f7fa;
            white-space: pre-wrap;
            word-break: break-all;
            margin-bottom: 5px;
            .reply-right {
                display: none;
                cursor: pointer;
                float: right;
            }
            &:hover{
                background: #eaebf0;
                .reply-right {
                    display: inline-block;
                }
        }
        }
        p {
            margin-left: 24px;
        }
    }
    .operation {
        margin: 8px 0px 8px 40px;
        line-height: 20px;
        span {
            display: inline-block;
            height: 20px;
            width: 24px;
            color: #979ba5;
            cursor: pointer;
            &:hover {
                color: #3a84ff;
            }
        }
        .line {
            display: inline-block;
            width: 1px;
            height: 12px;
            margin: -2px 12px;
            background-color: #dcdee5;
        }
    }
}
.icon-yinyong {
    position: relative;
    top: -4px;
    left: 0px;
    font-size: 16px;
    margin-right: 10px;
    width: 12px;
    height: 10px;
    opacity: 1;
    color: #c4c6cc;
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
