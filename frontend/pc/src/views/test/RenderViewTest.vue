<template>
  <div class="test-page">
    <div class="display-view">
      <render-view
        v-if="!errMessage"
        :form-data="formData"
        :context="context">
      </render-view>
      <div v-else class="error-tips">
        {{ errMessage }}
      </div>
    </div>
    <div class="editor">
      <code-editor v-model="jsonConfigStr" :options="editorConfig">
      </code-editor>
    </div>
  </div>
</template>

<script>
  import CodeEditor from '../../components/CodeEditor';
  import RenderView from '../../components/renderview/RenderView';
  import { CUSTOM_FORM_TEMPLATE } from '../../constants/customFormTemplate';

  export default {
    name: 'RenderViewTest',
    components: {
      RenderView,
      CodeEditor,
    },
    data() {
      return {
        errMessage: null,
        jsonConfigStr: JSON.stringify(CUSTOM_FORM_TEMPLATE, null, 4),
        formData: [],
        context: {},
        editorConfig: {
          language: 'json',
        },
      };
    },
    watch: {
      jsonConfigStr: {
        handler() {
          this.initRenderView();
        },
        immediate: true,
      },
    },
    methods: {
      /**
       * 初始化
       */
      initRenderView() {
        this.errMessage = '';
        try {
          const { form_data: formData, schemes, config } = JSON.parse(this.jsonConfigStr);
          // 渲染表单
          this.formData = formData;
          this.context = {
            schemes,
            config,
          };
        } catch (err) {
          this.errMessage = err;
          this.formData = [];
        }
      },
    },
  };
</script>

<style lang="scss" scoped>
.test-page {
    width: 100%;
    height: 100%;
    padding: 40px;
    .display-view, .editor {
        width: 50%;
        float: left;
    }
    .display-view {
        padding-right: 20px;
    }
    .editor {
        height: 100%;
        /deep/ .code-editor {
            height: 100%;
        }
    }
}
</style>
