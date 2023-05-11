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
  <div v-if="item.showFeild && !loading">
    <bk-form-item :label="item.name"
      :required="item.validate_type === 'REQUIRE'"
      :desc="item.tips"
      :ext-cls="'bk-line-height'"
      desc-type="icon">
      <bk-checkbox-group :ref="item.key" :value="selects" @change="selected">
        <bk-checkbox
          v-for="checkbox in item.choice"
          :value="checkbox.key"
          :key="checkbox.key"
          :disabled="disabled"
          :ext-cls="'mr20'">{{ checkbox.name }}
        </bk-checkbox>
      </bk-checkbox-group>
      <template v-if="item.checkValue">
        <p class="bk-task-error" v-if="item.checkMessage">{{ item.checkMessage }}</p>
        <p class="bk-task-error" v-else>{{ item.name }}{{$t('m.newCommon["为必填项！"]')}}</p>
      </template>
    </bk-form-item>
  </div>
</template>

<script>
  import mixins from '../../commonMix/field.js';
  export default {
    name: 'CHECKBOX',
    mixins: [mixins],
    props: {
      item: {
        type: Object,
        required: true,
        default: () => {},
      },
      fields: {
        type: Array,
        default() {
          return [];
        },
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
    data() {
      return {
        loading: false,
        selects: [],
      };
    },
    watch: {
      'item.val'(val) {
        this.selects = val === '' ? [] : val.split(',');
        this.conditionField(this.item, this.fields);
      },
      'item.choice': {
        handler() {
          this.resetCheckboxGroupData();
        },
        deep: true,
      },
    },
    async created() {
      this.item.choice = await this.getFieldOptions(this.item, this.isPreview);
      const valueStatus = this.judgeValue(this.item.val, this.item.choice);
      this.item.val = valueStatus ? this.item.val : '';
      this.selects = this.item.val === '' ? [] : this.item.val.split(',');
      this.conditionField(this.item, this.fields);
      if (this.item.value && !this.item.val) {
        this.item.val = this.item.value;
      }
    },
    methods: {
      selected(val) {
        this.item.val = val.join(',');
        this.item.checkValue = false;
      },
      /**
       * bk-checkbox-group 组件临时兼容处理，待 magicbox 解决后更新
       * checkbox 子组件动态重新渲染后，父组件的 checkboxItems 未更新，导致实际渲染的组件和 checkboxItems 记录的不一致
       */
      resetCheckboxGroupData() {
        const { key } = this.item;
        if (this.$refs[key]) {
          this.$refs[key].checkboxItems = [];
          this.loading = true;
          this.$nextTick(() => {
            this.loading = false;
          });
        }
      },
    },
  };
</script>


