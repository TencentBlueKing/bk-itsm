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
  <div style="width: 100%">
    <full-screen
      :is-full="isFull"
      :title="fullTitle"
      @onClose="closeFullSreen">
      <viewer v-if="isPreview" :initial-value="value" :height="height + 'px'">
      </viewer>
      <editor
        v-else
        ref="toastuiEditor"
        :height="height + 'px'"
        initial-edit-type="wysiwyg"
        preview-style="vertical"
        :initial-value="value"
        :options="editorOptions"
        @load="onEditorLoad"
        @blur="onEditorBlur" />
      <i
        v-if="!isFull"
        class="bk-itsm-icon icon-order-open"
        @click.stop="openFullScreen"></i>
    </full-screen>
  </div>
</template>

<script>
  import FullScreen from '../../common/FullScreen.vue';
  import { appendTargetAttrToHtml } from '../../../utils/util';
  import { errorHandler } from '../../../utils/errorHandler';
  // 基础样式
  import 'codemirror/lib/codemirror.css';
  import '@toast-ui/editor/dist/toastui-editor.css';
  import '@toast-ui/editor/dist/toastui-editor-viewer.css';
  // 代码高亮
  import 'highlight.js/styles/github.css';
  import codeSyntaxHighlight from '@toast-ui/editor-plugin-code-syntax-highlight';
  import hljs from 'highlight.js';
  import { Editor, Viewer } from '@toast-ui/vue-editor';
  // 国际化
  import '@toast-ui/editor/dist/i18n/zh-cn.js';
  // 需要代码高亮的语言
  const codelanguage = ['javascript', 'java', 'python', 'shell', 'powershell', 'markdown'];
  codelanguage.forEach((item) => {
    hljs.registerLanguage(item, require(`highlight.js/lib/languages/${item}`));
  });
  export default {
    name: 'RichTextEditor',
    components: {
      FullScreen,
      Editor,
      viewer: Viewer,
    },
    model: {
      prop: 'value',
      event: 'change',
    },
    props: {
      value: {
        type: String,
        default: '',
      },
      options: {
        type: Object,
        default: () => {},
      },
      id: {
        type: [String, Number],
        required: true,
      },
      fullTitle: {
        type: String,
        default: '',
      },
      // 预览模式
      isPreview: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        isFull: false,
        height: 250,
        editorOptions: {
          viewer: true,
          hideModeSwitch: false,
          usageStatistics: false,
          language: 'zh-CN',
          plugins: [[codeSyntaxHighlight, { hljs }]],
        },
      };
    },
    watch: {
      'value'(val) {
        const editor = this.$refs.toastuiEditor && this.$refs.toastuiEditor.editor;
        editor && editor.setHtml(val, true);
      },
    },
    mounted() {
      window.addEventListener('resize', this.handleScreenChange);
    },
    beforeDestroy() {
      window.removeEventListener('resize', this.handleScreenChange);
    },
    methods: {
      getHtml() {
        return this.$refs.toastuiEditor.invoke('getHtml');
      },
      /**
       * 修改 toastui-editor 模式栏默认样式
       */
      onEditorLoad() {
        try {
          const rootEl = this.$refs.toastuiEditor.getRootElement();
          const modeBarEl = rootEl.querySelector('.te-mode-switch-section');
          modeBarEl.classList.add('cus-change-mode');
          modeBarEl.querySelector('.te-switch-button.markdown').innerText = this.$t('m.common["Markdown模式"]');
          modeBarEl.querySelector('.te-switch-button.wysiwyg').innerText = this.$t('m.common["富文本模式"]');
        } catch (err) {
          errorHandler(err);
        }
      },
      onEditorBlur() {
        const value = this.getHtml();
        // 匹配 html 字符串中 a 标签是否有 target 属性，没有则加上 target="_blank"
        const replaceValue = appendTargetAttrToHtml(value);
        this.$emit('change', replaceValue);
      },
      setHeight(height) {
        this.height = height;
      },
      getFullScreenContentHeight() {
        return document.body.clientHeight - 50;
      },
      handleScreenChange() {
        if (this.isFull) {
          const height = this.getFullScreenContentHeight();
          this.setHeight(height);
        }
      },
      openFullScreen() {
        this.isFull = true;
        this.handleScreenChange();
      },
      closeFullSreen() {
        this.isFull = false;
        this.setHeight(250);
      },
    },
  };
</script>

<style lang='scss' scoped>
    /deep/ .cus-change-mode {
        font-size: 12px;
        text-align: right;
        background-color: #f9f9f9;
        border-color: #e5e5e5;
        .te-switch-button {
            width: 120px;
            color: #a0aabf;
            background-color: #e5e5e5;
            &.active {
                color: #000;
                background-color: #fff;
            }
        }
    }
    .icon-order-open {
        position: absolute;
        right: 10px;
        top: 8px;
        font-size: 16px;
        color: #979BA5;
        z-index: 2;
        cursor: pointer;
        &:hover {
            color: #63656E;
        }
    }
</style>
