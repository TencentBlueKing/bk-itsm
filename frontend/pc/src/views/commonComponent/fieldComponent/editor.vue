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
    <bk-form-item :label="item.name" :required="item.validate_type === 'REQUIRE'" :desc="item.tips" style="font-size: 0" desc-type="icon">
      <rich-text-editor
        v-model="item.val"
        :full-title="item.name"
        :id="item.key"
        :is-preview="disabled">
      </rich-text-editor>
      <template v-if="item.checkValue">
        <p class="bk-task-error" v-if="item.checkMessage">{{ item.checkMessage }}</p>
        <p class="bk-task-error" v-else>{{ item.name }}{{$t('m.newCommon["为必填项！"]')}}</p>
      </template>
    </bk-form-item>
  </div>
</template>

<script>
  import RichTextEditor from '../../../components/form/richTextEditor/richTextEditor.vue';
  export default {
    name: 'RICHTEXT',
    components: {
      RichTextEditor,
    },
    props: {
      item: {
        type: Object,
        required: true,
        default: () => {},
      },
      isCurrent: {
        type: Boolean,
        default: false,
      },
      disabled: {
        type: Boolean,
        default: false,
      },
    },
    mounted() {
      if (this.item.value && !this.item.val) {
        this.item.val = this.item.value;
      }
    },
  };
</script>

<style lang='scss' scoped>
    .cus-change-mode{
        font-size: 12px;
        display: inline-block;
        height: 24px;
        width: 100%;
        line-height: 24px;
        background-color: #f9f9f9;
        border: 1px solid #e5e5e5;
        border-top: none;
        text-align: right;
        span{
            display: inline-block;
            height: 100%;
            width: 120px;
            cursor: pointer;
            text-align: center;
            background-color: #e5e5e5;
            padding: 0 10px;
            color: #a0aabf;
            border-left: 1px solid #e5e5e5;
        }
        .checked {
            background-color: #fff;
            color: #000;
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
