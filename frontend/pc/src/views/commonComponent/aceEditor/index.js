/*
 * Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 * BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
 *
 * License for BK-ITSM 蓝鲸流程服务:
 * --------------------------------------------------------------------
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
 * LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
 * NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
 */

module.exports = {
  template: '<div :style="{height: calcSize(height), width: calcSize(width)}"></div>',
  props: {
    value: {
      type: String,
      default: '',
    },
    width: {
      type: [Number, String],
      default: 500,
    },
    height: {
      type: [Number, String],
      default: 300,
    },
    lang: {
      type: String,
      default: 'text',
    },
    theme: {
      type: String,
      default: 'monokai',
    },
    readOnly: {
      type: Boolean,
      default: false,
    },
    fullScreen: {
      type: Boolean,
      default: false,
    },
    hasError: {
      type: Boolean,
      default: false,
    },
    fontSize: {
      type: Number,
      default: 14,
    },
  },
  data() {
    return {
      $editor: null,
    };
  },
  watch: {
    value(newVal) {
      if (this.$editor && this.$editor.setValue) {
        this.$editor.setValue(newVal, 1);
      }
    },
    // lang (newVal) {
    //     if (newVal) {
    //         require(`brace/mode/${newVal}`)
    //         this.$editor.getSession().setMode(`ace/mode/${newVal}`)
    //     }
    // },
    fullScreen() {
      this.$el.classList.toggle('ace-full-screen');
      this.$editor.resize();
    },
  },
  methods: {
    calcSize(size) {
      const newSize = size.toString();
      if (newSize.match(/^\d*$/)) return `${size}px`;
      if (newSize.match(/^[0-9]?%$/)) return newSize;
      return '100%';
    },
  },
  mounted() {
    this.$editor = this.$ace.edit(this.$el);
    const {
      $editor,
      lang = 'javascript',
      theme = 'monokai',
      readOnly,
      fontSize,
    } = this;
    const session = $editor.getSession();
    this.$editor.setFontSize(fontSize);

    this.$emit('init', $editor);
    session.setMode(`ace/mode/${lang}`); // 配置语言
    $editor.setTheme(`ace/theme/${theme}`); // 配置主题
    $editor.setTheme('ace/theme/textmate'); // 配置主题
    session.setUseWrapMode(true); // 自动换行
    $editor.setValue(this.value, 1); // 设置默认内容
    $editor.setReadOnly(readOnly); // 设置是否为只读模式
    $editor.setShowPrintMargin(false); // 不显示打印边距
    // 绑定输入事件回调
    $editor.on('change', ($editorPoint, $fn) => {
      const content = $editor.getValue();
      this.$emit('update:hasError', !content);
      this.$emit('input', content, $editorPoint, $fn);
    });

    $editor.on('blur', ($editorPoint, $fn) => {
      const content = $editor.getValue();
      this.$emit('update:hasError', !content);
      this.$emit('blur', content, $editorPoint, $fn);
    });

    session.on('changeAnnotation', (args, instance) => {
      const annotations = instance.$annotations;
      if (annotations && annotations.length) {
        this.$emit('change-annotation', annotations);
      }
    });
  },
};
