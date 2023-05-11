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
  <div v-if="item.showFeild">
    <bk-form-item :label="item.name" :required="item.validate_type === 'REQUIRE'" :desc="item.tips" desc-type="icon">
      <p style="color: #c4c6cc;" class="mt5 mb0 f12" slot="tip" v-if="item.type === 'CUSTOM-FORM'">{{$t('m["当前字段为自定义表单"]')}}</p>
      <render-view
        :form-data="formData"
        :context="context">
      </render-view>
    </bk-form-item>
    <template v-if="item.checkValue">
      <p class="bk-task-error" v-if="item.checkMessage">{{ item.checkMessage }}</p>
      <p class="bk-task-error" v-else>{{ item.name }}{{$t('m.newCommon["为必填项！"]')}}</p>
    </template>
  </div>
</template>

<script>
  import mixins from '../../commonMix/field.js';
  import RenderView from '../../../components/renderview/RenderView';

  export default {
    name: 'CUSTOM-FORM',
    components: {
      RenderView,
    },
    mixins: [mixins],
    props: {
      item: {
        type: Object,
        default: () => {
        },
      },
      fields: {
        type: Array,
        default() {
          return [];
        },
      },
    },
    data() {
      return {
        formData: [],
        context: {},
        errMessage: '',
      };
    },
    watch: {
      'item.val': {
        handler() {
          this.conditionField(this.item, this.fields);
          this.initRenderView();
        },
        immediate: true,

      },
    },
    mounted() {
      if (this.item.value && !this.item.val) {
        this.item.val = this.item.value;
      }
    },
    methods: {
      initRenderView() {
        this.errMessage = '';
        try {
          const data = typeof this.item.val === 'string' ? JSON.parse(this.item.val) : this.item.val;
          const { form_data: formData, schemes, config } = data;
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
