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
  <section class="code-editor"></section>
</template>
<script>
  import * as monaco from 'monaco-editor';
  const DEFAULT_OPTIONS = {
    language: 'javascript',
    theme: 'vs-dark',
    automaticLayout: true,
    minimap: {
      enabled: false,
    },
    wordWrap: 'on',
    wrappingIndent: 'same',
  };
  export default {
    name: 'CodeEditor',
    props: {
      value: {
        type: String,
        default: '',
      },
      options: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      const editorOptions = Object.assign({}, DEFAULT_OPTIONS, this.options, { value: this.value });
      return {
        editorOptions,
        monacoInstance: null,
      };
    },
    watch: {
      value(val) {
        const valInEditor = this.monacoInstance.getValue();
        if (val !== valInEditor) {
          this.monacoInstance.setValue(val);
        }
      },
      options: {
        deep: true,
        handler(val) {
          this.editorOptions = Object.assign({}, DEFAULT_OPTIONS, val, { value: this.value });
          this.updateOptions();
        },
      },
    },
    mounted() {
      this.initIntance();
    },
    beforeDestroy() {
      if (this.monacoInstance) {
        this.monacoInstance.dispose();
      }
    },
    methods: {
      initIntance() {
        this.monacoInstance = monaco.editor.create(this.$el, this.editorOptions);
        const model = this.monacoInstance.getModel();
        model.setEOL(0); // 设置编辑器在各系统平台下 EOL 统一为 \n
        if (this.value.indexOf('\r\n') > -1) { // 转换已保存的旧数据
          const textareaEl = document.createElement('textarea');
          textareaEl.value = this.value;
          this.$emit('input', textareaEl.value);
        }
        model.onDidChangeContent(() => {
          const value = this.monacoInstance.getValue();
          this.$emit('input', value);
        });
        this.monacoInstance.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KEY_S, () => {
          const value = this.monacoInstance.getValue();
          this.$emit('saveContent', value);
        });
      },
      updateOptions() {
        this.monacoInstance.updateOptions(this.editorOptions);
      },
    },
  };
</script>
<style lang="scss" scoped>
    .code-editor {
        height: 100%;
    }
</style>
