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
  <div class="bk-customtable-data">
    <div class="bk-custom-line"
      :class="{ 'mb10': itemIndex !== customTableInfo.list.length - 1 }"
      v-for="(item, itemIndex) in customTableInfo.list"
      :key="itemIndex">
      <bk-input :ext-cls="'bk-custom-input'"
        :clearable="true"
        :placeholder="$t(`m.treeinfo['请输入名称']`)"
        v-model="item.name">
      </bk-input>
      <bk-checkbox style="float: left; margin-right: 10px; line-height: 32px;"
        :true-value="trueStatus"
        :false-value="falseStatus"
        v-model="item.required">
        {{ $t(`m.treeinfo['必填']`) }}
      </bk-checkbox>
      <bk-select :ext-cls="'bk-custom-small'"
        v-model="item.display"
        :clearable="false"
        searchable>
        <bk-option v-for="option in typeList"
          :key="option.id"
          :id="option.id"
          :name="option.name">
        </bk-option>
      </bk-select>
      <textarea style="width: 180px; min-height: 32px;"
        class="bk-form-textarea bk-textarea-tanble"
        :placeholder="$t(`m.treeinfo['请输入，Enter分隔']`)"
        :disabled="item.display !== 'select' && item.display !== 'multiselect'"
        v-model.trim="item.choice">
            </textarea>
      <div class="bk-custom-icon">
        <i class="bk-itsm-icon icon-flow-add" @click="addTableData(item, itemIndex)"></i>
        <i class="bk-itsm-icon icon-flow-reduce"
          :class="{ 'bk-no-delete': customTableInfo.list.length === 1 }"
          @click="reduceTableData(item, itemIndex)"></i>
      </div>
    </div>
  </div>
</template>
<script>
  export default {
    name: 'customTableData',
    props: {
      customTableInfo: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        typeList: [
          { id: 'input', name: this.$t('m.treeinfo["输入框"]') },
          { id: 'select', name: this.$t('m.treeinfo["单选框"]') },
          { id: 'multiselect', name: this.$t('m.treeinfo["多选框"]') },
          { id: 'datetime', name: this.$t('m.treeinfo["时间"]') },
          { id: 'date', name: this.$t('m.treeinfo["日期"]') },
        ],
        trueStatus: true,
        falseStatus: false,
      };
    },
    computed: {
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
    },
    mounted() {

    },
    methods: {
      addTableData(item, index) {
        const valueInfo = {
          name: '',
          display: 'input',
          choice: '',
          required: false,
        };
        this.customTableInfo.list.splice(index + 1, 0, valueInfo);
      },
      reduceTableData(item, index) {
        if (this.customTableInfo.list.length === 1) {
          return;
        }
        this.customTableInfo.list.splice(index, 1);
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../../../scss/mixins/clearfix.scss';
    @import '../../../../../scss/mixins/scroller';
    .bk-custom-line {
        display: flex;
        align-items: center;
        @include clearfix;
        .bk-custom-input {
            flex: 1;
        }
        .bk-form-checkbox {
            width: 50px;
            margin: 0 5px;
        }
        .bk-custom-small {
            flex: 1;
            margin-right: 5px;
        }
        .bk-custom-icon {
            margin: 0 5px;
            float: right;
            line-height: 32px;
            font-size: 18px;
            .bk-itsm-icon {
                color: #C4C6CC;
                margin-right: 9px;
                cursor: pointer;
                &:hover {
                    color: #979BA5;
                }
            }
            .bk-no-delete{
                color: #DCDEE5;
                cursor: not-allowed;
                &:hover {
                    color: #DCDEE5;
                }
            }
        }
        .bk-textarea-tanble {
            flex: 1;
            overflow-y: scroll;
            // position: absolute;
            height: 32px;
            min-height: 32px;
            padding: 3px 10px;
            float: left;
            width: 225px;
            line-height: 24px !important;
            @include scroller;
            &:focus {
                height: 90px!important;
                z-index: 10;
            }
        }
    }
</style>
