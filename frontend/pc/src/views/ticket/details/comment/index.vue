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
    <!-- 回复评论 -->
    <div v-if="isReplyComment" class="reply-comment">
      <div class="reply-title">
        <i class="bk-itsm-icon icon-yinyong"></i>
        <span class="quote-creator">{{ $t('m["回复"]') }} {{ replyContent.creator }} {{ $t('m["的评论"]') }} :</span>
        <span class="repeal-reply" @click="repealReply">{{ $t('m["取消回复"]') }}</span>
      </div>
      <div class="reply-content">
        <div v-html="replyContent.content"></div>
      </div>
    </div>
    <editor
      v-if="isShowEditor"
      ref="editorAdd"
      :editor-id="'editor1'"
      :comment-type="commentType"
      @postComment="postComment"
      @changebuttonStatus="changebuttonStatus">
    </editor>
    <bk-button v-show="isShowEditor" class="submit" :theme="'primary'" @click="submit">{{ isEditEditor ? $t('m["发布"]') : $t('m["返回"]') }}</bk-button>
    <bk-divider></bk-divider>
    <div>{{ $t('m["全部评论"]') }}</div>
    <ul v-bkloading="{ isLoading: commentLoading }" v-show="commentList.length !== 0" class="comment-list">
      <li v-for="(item, index) in commentList" :key="index" :class="[{ 'twinkling': flash[item.id] }]">
        <comment-item
          :comment-list="commentList"
          :cur-comment="item"
          @replyComment="replyComment"
          @refreshComment="refreshComment"
          @jumpTargetComment="jumpTargetComment"
          @editComment="editComment">
        </comment-item>
      </li>
      <li class="page-over">
        <div v-bkloading="{ isLoading: moreLoading }"></div>
        <span v-if="isPageOver">{{ $t('m["评论已经加载完了"]') }}</span>
      </li>
    </ul>
    <div v-if="commentList.length === 0" class="no-comment">
      <img :src="imgUrl">
      <p>{{ $t('m["当前暂无评论，快去评论吧！"]') }}</p>
    </div>
    <bk-dialog
      v-model="isEdit"
      :title="editType === 'edit' ? $t(`m['编辑评论']`) : $t(`m['回复评论']`)"
      width="800"
      theme="primary"
      :mask-close="false"
      @confirm="submitEdit">
      <editor ref="editorEdit"
        :editor-id="'editor2'"
        :comment-type-reply="commentType">
      </editor>
    </bk-dialog>
  </div>
</template>
<script>
  import editor from './editor.vue';
  import commentItem from './commentItem.vue';
  export default {
    name: 'ticketComment',
    components: {
      commentItem,
      editor,
    },
    props: {
      commentId: [Number, String],
      commentList: Array,
      ticketInfo: Object,
      ticketId: [Number, String],
      commentLoading: Boolean,
      moreLoading: Boolean,
      isPageOver: Boolean,
      hasNodeOptAuth: Boolean,
      isShowBasicInfo: Boolean,
      stepActiveTab: String,
    },
    data() {
      return {
        curCommentId: '',
        commentListDom: '',
        commentType: '', // 评论类型
        isShowSelect: true,
        isShowEditor: false, // 打开富文本
        isEditEditor: false, // 是否编辑文本
        selectPatternList: [
          {
            type: 'INSIDE',
            icon: 'bk-itsm-icon icon-suoding common-color',
            name: this.$t('m[\'内部评论\']'),
            docs: this.$t('m[\'仅单据相关人员可发布的评论\']'),
          },
          {
            type: 'PUBLIC',
            icon: 'bk-itsm-icon icon-jiesuo common-color',
            name: this.$t('m[\'外部评论\']'),
            docs: this.$t('m[\'发布的评论所有人可见\']'),
          },
        ],
        // commentList: [],
        editType: '',
        isEdit: false,
        flash: {},
        imgUrl: require('@/images/box.png'),
        isReplyComment: false,
        replyCommnetId: '',
        replyContent: {
          creator: '',
          content: '',
        },
        commentDomHeight: '',
        isShowCommentScroll: false,
        basicInDomHeight: 54, // 基本信息初始高度
      };
    },
    watch: {
      stepActiveTab(val) {
        if (val === 'allComments') {
          this.getCommentHeight();
        }
      },
    },
    mounted() {
      this.commentListDom = document.querySelector('.comment-list');
      this.getBasicHeight();
    },
    methods: {
      getCommentHeight() {
        const commentDom = document.querySelector('.wang-editor-template');
        this.commentDomHeight = commentDom.clientHeight;
        this.isShowCommentScroll = commentDom.clientHeight > 500;
      },
      getBasicHeight() {
        const basicDom = document.querySelector('.base-info-content');
        this.basicInDomHeight = basicDom.clientHeight;
      },
      editComment(curComment, type) {
        const _this = this.$refs.editorEdit.editor;
        _this.txt.clear();
        this.editType = type;
        this.curCommentId = curComment.id;
        if (type === 'edit') _this.txt.html(curComment.content);
        // 新增回复评论的类型取决于父级类型
        this.commentType = curComment.remark_type;
        this.isEdit = true;
      },
      replyComment(curComment) {
        this.replyCommnetId = curComment.id;
        this.isReplyComment = true;
        this.commentType = curComment.remark_type;
        this.postComment(curComment.remark_type);
        this.replyContent.creator = curComment.creator;
        this.replyContent.content = curComment.content;
        this.commentListDom.scrollTop = 0;
      },
      repealReply() {
        this.replyCommnetId = '';
        this.isReplyComment = false;
        this.isShowSelect = true;
        this.isShowEditor = false;
      },
      changebuttonStatus(val) {
        this.isEditEditor = val;
      },
      submitEdit() {
        const _this = this.$refs.editorEdit.editor;
        const text = _this.txt.html();
        this.editorEditData = '';
        _this.txt.clear();
        let url = '';
        const params = {
          content: text,
          users: [],
          remark_type: this.commentType,
        };
        if (this.editType === 'edit') {
          params.id = this.curCommentId;
          url = 'ticket/updateTicketComment';
        } else {
          params.ticket_id = this.ticketId;
          params.parent__id = this.curCommentId;
          url = 'ticket/addTicketComment';
        }
        this.$store.dispatch(url, params).then(() => {
          this.refreshComment();
          this.commentListDom.scrollTop = 0;
        });
      },
      refreshComment() {
        this.isEditEditor = false;
        this.$emit('refreshComment');
      },
      postComment(type) {
        const is_history_processor = this.ticketInfo.updated_by.split(',').includes(window.username);
        const current_processors = [];
        this.ticketInfo.current_processors.split(',').forEach((item) => {
          current_processors.push(item.split('(')[0]);
        });
        const is_current_processor = current_processors.includes(window.username);
        // 内部评论的条件为，拥有单据处理权限，并且是历史处理人或者是当前处理人
        if (!(this.hasNodeOptAuth && (is_history_processor || is_current_processor)) && type === 'INSIDE') {
          this.$bkMessage({
            message: this.$t('m["你当前无法发表内部评论"]'),
            theme: 'warning ',
          });
          return;
        }
        this.commentType = type;
        this.isShowSelect = false;
        this.isShowEditor = true;
      },
      jumpTargetComment(curComment) {
        // 获取parent的评论下标
        const curCommentIndex = this.commentList.indexOf(this.commentList.filter(item => item.id === curComment.parent)[0]);
        if (curCommentIndex !== -1) {
          const commentListDom = document.querySelector('.ticket-container-left');
          const baseInfoDom = document.querySelector('.base-info-content');
          const heights = Array.from(commentListDom.childNodes).slice(0, curCommentIndex)
            .map(item => item.clientHeight);
          const sumHeight = heights.reduce((pre, cur) => pre + cur);
          this.$set(this.flash, curComment.parent__id, true);
          const timer = setTimeout(() => {
            this.$set(this.flash, curComment.parent__id, false);
            clearTimeout(timer);
          }, 2000);
          commentListDom.scrollTop = sumHeight + 340 + baseInfoDom.offsetHeight;
        } else {
          this.$emit('addTargetComment', curComment);
        }
      },
      submit() {
        // 评论内容
        if (!this.isEditEditor) {
          this.repealReply();
          return;
        }
        this.isShowEditor = false;
        this.isReplyComment = false;
        if (this.$refs.editorAdd) {
          const _this = this.$refs.editorAdd.editor;
          const text = _this.txt.html();
          this.editorData = '';
          this.isShowSelect = true;
          _this.txt.clear();
          const params = {
            content: text,
            ticket_id: this.ticketId,
            parent__id: this.replyCommnetId || this.commentId,
            remark_type: this.commentType,
            users: [],
          };
          if (text) {
            try {
              this.$store.dispatch('ticket/addTicketComment', params).then(() => {
                this.replyCommnetId = '';
                this.refreshComment();
                this.commentListDom.scrollTop = 0;
              });
            } catch (e) {
              console.log(e);
            } finally {
              this.isReplyComment = false;
            }
          }
        }
      },
    },
  };
</script>
<style scoped lang="scss">
    @import '../../../../scss/mixins/scroller.scss';
    @keyframes flash{
        0% {
            opacity: 0.1;
        }
        50% {
            opacity: 0.5;
        }
        100% {
            opacity: 1;
        }
    }
    .twinkling{
        background: rgb(240, 238, 238);
        animation: flash 1s linear infinite;
    }
    .common-color {
        color: #c4c6cc;
    }
    .wang-editor-template {
        // overflow: auto;
        @include scroller;
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
        .comment-list {
            @include scroller;
            li {
                padding-top: 20px;
            }
        }
        .submit {
            margin: 10px 0;
        }
        .no-comment {
            text-align: center;
            font-size: 14px;
            line-height: 50px;
            color: #979ba5;
            p {
                font-size: 12px;
                color: #63656E;
                margin-top: -14px;
            }
        }
        .page-over {
            height: 20px;
            color: #6d6f77;
            font-size: 12px;
            text-align: center;
            line-height: 20px;
        }
    }
    .reply-comment {
        font-size: 12px;
        padding: 12px 16px;
        min-height: 74px;
        background: #f5f7fa;
        border-radius: 2px;
        margin-bottom: 10px;
        position: relative;
        color: #c4c6cc;
        .reply-title {
            line-height: 20px;
            i {
                font-size: 16px;
                position: relative;
                top: -4px;
                left: 0;
                color: #c4c6cc;
            }
            .quote-creator {
                margin-left: 5px;
                color: #313238;
            }
            .repeal-reply {
                float: right;
                color: #3a84ff;
                cursor: pointer;
            }
        }
        .reply-content {
            color: #63656E;
            padding: 10px 0px 10px 25px;
            p {
                white-space: pre-wrap;
                word-break: break-all;
            }
        }
    }
</style>
