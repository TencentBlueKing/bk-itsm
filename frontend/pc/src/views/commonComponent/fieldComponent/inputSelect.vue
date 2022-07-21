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
      <bk-select :class="{ 'bk-border-error': item.checkValue }"
        searchable
        v-model="item.val"
        :search-with-pinyin="true"
        :disabled="(item.is_readonly && !isCurrent) || disabled"
        :placeholder="item.desc"
        :font-size="'medium'"
        @selected="selected"
        @toggle="item.checkValue = false">
        <bk-option v-for="option in options"
          class="custom-option"
          :key="option.key"
          :id="option.key"
          :name="option.name">
          <span>{{option.name}}</span>
          <i class="bk-icon icon-close" v-if="option.can_delete" @click.stop="handleDeleteOption(option.key)"></i>
        </bk-option>
        <div slot="extension">
          <div class="plus-content" @click="addStatus = !addStatus">
            <i class="bk-icon icon-plus-circle"></i>新增
          </div>
          <div class="add-status" v-if="addStatus">
            <bk-form-item label="name">
              <bk-input v-model="tempChoice.name"
                @blur="giveDefaultKey">
              </bk-input>
            </bk-form-item>
            <bk-form-item label="key">
              <bk-input v-model="tempChoice.key">
              </bk-input>
            </bk-form-item>
            <p class="operations">
              <span @click="confirmAdd" :class="{ 'disabled': !tempChoice.name }">{{$t(`m.task['确认']`)}}</span>
              <span @click="cancelAdd">{{$t(`m.task['取消']`)}}</span>
            </p>
          </div>
        </div>
      </bk-select>
      <template v-if="item.checkValue">
        <p class="bk-task-error" v-if="item.checkMessage">{{ item.checkMessage }}</p>
        <p class="bk-task-error" v-else>{{ item.name }}{{$t('m.newCommon["为必填项！"]')}}</p>
      </template>
    </bk-form-item>
  </div>
</template>

<script>
  import mixins from '../../commonMix/field.js';
  import pinyin from 'pinyin';

  export default {
    name: 'INPUTSELECT',
    mixins: [mixins],
    props: {
      item: {
        type: Object,
        default() {
          return {};
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
        options: [],
        addStatus: false,
        tempChoice: {
          name: '',
          key: '',
        },
      };
    },
    watch: {
      'item.val'() {
        this.conditionField(this.item, this.fields);
      },
      'item.choice'(newVal, oldVal) {
        if ((this.item.source_type === 'API' || this.item.source_type === 'DATADICT' || this.item.source_type === 'RPC') && (oldVal.length !== newVal.length)) {
          this.getOption();
        }
      },
    },
    async mounted() {
      if (!this.item.val && this.item.value) {
        this.item.val = this.item.value;
      }
      await this.getOption();
      const valueStatus = this.judgeValue(this.item.val, this.item.choice);
      this.item.val = valueStatus ? this.item.val : '';
      this.conditionField(this.item, this.fields);
    },
    methods: {
      async getOption() {
        this.item.choice = await this.getFieldOptions(this.item);
        this.options = this.item.choice;
      },
      selected() {
        if (this.item.related_fields && this.item.related_fields.be_relied) {
          this.item.related_fields.be_relied.forEach((ite) => {
            this.fields.forEach((it) => {
              if (ite === it.key) {
                it.value = '';
                it.val = it.value;
              }
            });
          });
        }
      },
      giveDefaultKey() {
        if (!this.tempChoice.name || this.tempChoice.key) {
          return;
        }
        this.tempChoice.key = '';
        const transfer = pinyin(this.tempChoice.name, {
          style: pinyin.STYLE_NORMAL,
          heteronym: false,
        });
        transfer.forEach((item) => {
          this.tempChoice.key += `${item}`;
        });
        // eslint-disable-next-line
                this.tempChoice.key = this.tempChoice.key.toUpperCase().replace(/\ /g, '_');
        if (this.tempChoice.key.length >= 32) {
          this.tempChoice.key = this.tempChoice.key.substr(0, 32);
        }
      },
      confirmAdd() {
        if (!this.tempChoice.name) {
          return;
        }
        this.addStatus = false;
        this.options.push({ ...this.tempChoice, can_delete: true });
        this.item.val = this.tempChoice.key;
        this.tempChoice.key = '';
        this.tempChoice.name = this.tempChoice.key;
      },
      cancelAdd() {
        this.addStatus = false;
        this.tempChoice.key = '';
        this.tempChoice.name = this.tempChoice.key;
      },
      handleDeleteOption(deleteOption) {
        if (deleteOption === this.item.val) {
          this.item.val = '';
        }
        this.options = this.options.filter(option => option.key !== deleteOption);
      },
    },
  };
</script>

<style lang='scss' scoped>
    .add-status{
        display: flex;
        align-items: center;
        flex-wrap: nowrap;
        /deep/ .bk-form-item{
            display: inline-flex;
            align-items: center;
            width: 30%;
            margin: 10px 0!important;
            .bk-label{
                width: 50px!important;
            }
            .bk-form-content{
                margin-right: 10px;
                margin-left: 0!important;
                display: inline-flex;
                width: calc(100% - 50px);
            }
        }
        .operations{
            display: inline-block;
            font-size: 12px;
            width: 30%;
            & span{
                cursor: pointer;
                color: #3a84ff;
            }
            & span:first-child{
                margin-right: 5px;
                margin-left: 5px;
            }
            .disabled{
                cursor: not-allowed;
                color: #979ba5;
            }
        }
    }
    .plus-content{
        cursor: pointer;
        i{
            margin-right: 5px;
        }
    }
    .custom-option .icon-close {
        display: none;
        position: absolute;
        right: 0;
        top: 3px;
        font-size: 26px;
        width: 26px;
        height: 26px;
        line-height: 26px;
        text-align: center;
    }
    .custom-option:hover .icon-close {
        display: block;
    }
</style>
