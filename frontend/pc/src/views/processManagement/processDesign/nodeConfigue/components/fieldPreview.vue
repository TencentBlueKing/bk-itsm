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
  <div class="bk-field-preview" id="bkPreview">
    <bk-form :label-width="200" form-type="vertical" :ext-cls="'bk-ext-form'">
      <template v-for="(item, index) in fields">
        <div :class="{ 'bk-field-line': item.layout === 'COL_12', 'bk-field-half': item.layout === 'COL_6' }" v-if="item.showFeild" :key="index">
          <component
            :is="'CW-' + item.type"
            :item="item"
            :fields="fields"
            :is-preview="isPreview"
            :is-file-preview="isFilePreview">
          </component>
        </div>
      </template>
    </bk-form>
  </div>
</template>
<script>
  import string from '../../../../commonComponent/fieldComponent/string.vue';
  import link from '../../../../commonComponent/fieldComponent/link';
  import int from '../../../../commonComponent/fieldComponent/int.vue';
  import text from '../../../../commonComponent/fieldComponent/text.vue';
  import checkbox from '../../../../commonComponent/fieldComponent/checkbox.vue';
  import radio from '../../../../commonComponent/fieldComponent/radio.vue';
  import select from '../../../../commonComponent/fieldComponent/select.vue';
  import inputSelect from '../../../../commonComponent/fieldComponent/inputSelect';
  import multiselect from '../../../../commonComponent/fieldComponent/multiselect.vue';
  import date from '../../../../commonComponent/fieldComponent/date.vue';
  import datetime from '../../../../commonComponent/fieldComponent/datetime.vue';
  import member from '../../../../commonComponent/fieldComponent/member.vue';
  import members from '../../../../commonComponent/fieldComponent/members.vue';
  import table from '../../../../commonComponent/fieldComponent/table.vue';
  import customtable from '../../../../commonComponent/fieldComponent/customtable.vue';
  import editor from '../../../../commonComponent/fieldComponent/editor.vue';
  import tree from '../../../../commonComponent/fieldComponent/tree.vue';
  import file from '../../../../commonComponent/fieldComponent/file.vue';
  import cascade from '../../../../commonComponent/fieldComponent/cascade.vue';
  import sopsTemplate from '../../../../commonComponent/fieldComponent/sopsTemplate.vue';
  import complexMembers from '../../../../commonComponent/fieldComponent/complexMembers.vue';
  import customForm from '../../../../commonComponent/fieldComponent/customForm.vue';

  export default {
    name: 'preview',
    components: {
      'CW-STRING': string,
      'CW-LINK': link,
      'CW-INT': int,
      'CW-TEXT': text,
      'CW-CHECKBOX': checkbox,
      'CW-RADIO': radio,
      'CW-SELECT': select,
      'CW-INPUTSELECT': inputSelect,
      'CW-MULTISELECT': multiselect,
      'CW-DATE': date,
      'CW-DATETIME': datetime,
      'CW-MEMBER': member,
      'CW-MEMBERS': members,
      'CW-TABLE': table,
      'CW-CUSTOMTABLE': customtable,
      'CW-RICHTEXT': editor,
      'CW-TREESELECT': tree,
      'CW-FILE': file,
      'CW-CASCADE': cascade,
      'CW-SOPS_TEMPLATE': sopsTemplate,
      'CW-COMPLEX-MEMBERS': complexMembers,
      'CW-CUSTOM-FORM': customForm,
    },
    props: {
      fields: {
        type: Array,
        required: true,
        default: () => [],
      },
      isPreview: {
        type: Boolean,
        default: false,
      },
      isFilePreview: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {

      };
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../../../scss/mixins/clearfix.scss';
    @import '../../../../../scss/mixins/scroller.scss';

    .bk-ext-form {
        width: 100%;
        @include clearfix;
        .bk-field-line {
            width: 100%;
            float: left;
            padding: 0 10px 10px 0px;
        }
        .bk-field-half {
            display: inline-block;
            vertical-align: top;
            width: 50%;
            padding: 0 10px 10px 0px;
        }
    }
</style>
