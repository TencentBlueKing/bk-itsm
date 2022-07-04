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
  <bk-sideslider
    :is-show.sync="isShow"
    :quick-close="true"
    :title="title"
    :width="width"
    ext-cls="ui-sideslider">
    <div slot="content">
      <render-view
        :form-data="formData"
        :context="context">
      </render-view>
    </div>
  </bk-sideslider>
</template>

<script>
  export default {
    name: 'Sideslider',
    components: {
      RenderView: () => import('../RenderView'),
    },
    props: {
      title: {
        type: String,
        default: '',
      },
      formData: {
        type: Array,
        default: () => ([]),
      },
      context: {
        type: Object,
        default: () => ({
          schemes: {},
        }),
      },
      width: {
        type: [String, Number],
        default: 800,
      },
    },
    data() {
      return {
        isShow: true,
      };
    },
  };
</script>

<style lang="scss">
.ui-sideslider {
    .bk-sideslider-content {
        padding: 20px;
    }
}
</style>
