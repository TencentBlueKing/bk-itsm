<template>
  <div class="wang-editor">
    <div class="change-comment" @click="handleChangeType" :title="commentType ? '点击切换评论类型' : '回复当前类型评论'">
      <i :class="['bk-itsm-icon', isInsideComment ? 'icon-suoding' : 'icon-jiesuo']"></i>
      <span>{{ isInsideComment ? $t('m["内部评论"]') : $t('m["外部评论"]') }}</span>
      <i class="bk-itsm-icon icon-jiantou_zuoyouqiehuan change-type"></i>
    </div>
    <div :id="editorId">
    </div>
    <ul class="bullet-box" :style="{ left: left + 'px', top: top + 'px', display: showFlag }">
      <li v-for="item in list" :key="item.key" @click="selectLine(item)">
        {{item.name}}
      </li>
    </ul>
  </div>
</template>

<script>
  import E from 'wangeditor';
  import { position, offset } from 'caret-pos';
  export default {
    name: 'commentEditor',
    props: {
      editorId: String,
      commentType: String,
      commentTypeReply: String,
    },
    data() {
      return {
        editor: null,
        editorData: '',
        left: '0px',
        top: '0px',
        showFlag: 'none',
        list: [
          { key: 1, name: '1' },
          { key: 5, name: '2' },
          { key: 2, name: '3' },
        ],
        isInsideComment: false,
      };
    },
    watch: {
      editorData() {
        const text = this.editor.txt.html();
        this.$emit('changebuttonStatus', !!text);
        if (text.charAt(text.length - 1) === '@') {
          this.showFlag = 'block';
          const textDom = this.editor.$textElem.elems[0];
          const pos = position(textDom); // { left: 15, top: 30, height: 20, pos: 15 }
          const off = offset(textDom);
          console.log(pos, off);
          const wangED = document.querySelector(`#${this.editorId}`);
          // 菜单的高度
          const menuH = wangED.offsetHeight - textDom.offsetHeight;
          this.left = pos.left;
          this.top = menuH + pos.height + pos.top;
          const childEle = document.getElementsByClassName('bullet-box')[0];
          console.log(childEle);
        } else {
          this.showFlag = 'none';
        }
      },
      commentType(val) {
        this.isInsideComment = val === 'INSIDE' || false;
      },
      // 回复类型根据当前评论类型
      commentTypeReply(val) {
        if (val) {
          this.isInsideComment = val === 'INSIDE' || false;
        }
      },
    },
    mounted() {
      const editor = new E(`#${this.editorId}`);
      editor.config.onchange = (newHtml) => {
        this.editorData = newHtml;
        this.$emit('editorContent', newHtml);
      };
      editor.config.height = 150;
      editor.config.zIndex = 400;
      editor.config.excludeMenus = [
        'emoticon',
        'video',
        'table',
        'strikeThrough',
        'indent',
        'image',
        'lineHeight',
        'foreColor',
        'backColor',
        'link',
        'list',
        'quote',
      ];
      editor.create();
      this.editor = editor;
      if (this.commentType === 'INSIDE' || this.commentTypeReply) {
        this.isInsideComment = true;
      }
    },
    methods: {
      selectLine(item) {
        const text = this.editor.txt.html();
        this.editor.txt.html(`${text}<span class="at-person">${item.name}<span>` + '  ');
      },
      handleChangeType() {
        if (this.commentTypeReply) {
          return;
        }
        if (this.ticketInfo && this.ticketInfo.is_over) {
          return;
        }
        if (!this.$store.state.ticket.hasTicketNodeOptAuth) {
          this.$bkMessage({
            message: this.$t('m["你当前无法发表内部评论"]'),
            theme: 'warning ',
          });
          return;
        }
        this.isInsideComment = !this.isInsideComment;
        const type = this.isInsideComment ? 'INSIDE' : 'PUBLIC';
        this.$emit('postComment', type);
      },
    },
  };
</script>

<style lang="scss" scoped>
.at-person {
    color: #3a84ff;
}
.change-type {
    font-size: 16px;
    color: #3a84ff;
}
.wang-editor {
    position: relative;
    .bullet-box {
        width: 100px;
        min-height: 50px;
        background-color: darkgray;
        z-index: 501;
        position: absolute;
    }
    .change-comment {
        font-size: 12px;
        line-height: 42px;
        z-index: 402;
        position: absolute;
        right: 0;
        top: 0;
        padding: 0 10px;
        height: 42px;
        color: #979ba5;
        cursor: pointer;
    }
}
</style>
