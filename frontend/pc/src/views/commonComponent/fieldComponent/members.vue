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
    <bk-form-item :label="item.name" :required="item.validate_type === 'REQUIRE'" :ext-cls="'bk-ext-item'" :desc="item.tips" desc-type="icon">
      <div @click="item.checkValue = false" class="member-form-item">
        <member-select :class="{ 'bk-border-error': item.checkValue }"
          v-model="selectedItems"
          :disabled="(item.is_readonly && !isCurrent) || item.evaluDisable || disabled"
          :placeholder="item.desc"
          @change="onMemberSelectChange">
        </member-select>
        <business-card
          :item="item">
        </business-card>
      </div>
      <template v-if="item.checkValue">
        <p class="bk-task-error" v-if="item.checkMessage">{{ item.checkMessage }}</p>
        <p class="bk-task-error" v-else>{{ item.name }}{{$t('m.newCommon["为必填项！"]')}}</p>
      </template>
    </bk-form-item>
  </div>
</template>

<script>
  import mixins from '../../commonMix/field.js';
  import memberSelect from '../memberSelect';
  import businessCard from '@/components/common/BusinessCard.vue';

  export default {
    name: 'MEMBERS',
    components: {
      memberSelect,
      businessCard,
    },
    mixins: [mixins],
    props: {
      item: {
        type: Object,
        required: true,
        default: () => {
        },
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
        selectedItems: [],
      };
    },
    watch: {
      'item.val'(val) {
        this.selectedItems = val ? val.split(',') : [];
      },
    },
    async mounted() {
      this.selectedItems = this.item.val ? this.item.val.split(',') : [];
      this.conditionField(this.item, this.fields);
    },
    methods: {
      onMemberSelectChange(data) {
        this.item.val = data.join(',');
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../scss/mixins/scroller.scss';
    .member-form-item {
        position: relative;
        /deep/ .business-popover {
            position: absolute;
            right: 10px;
            top: 0px;
            z-index: 1;
        }
    }
    .bk-ext-item {
        position: relative;
    }
</style>
