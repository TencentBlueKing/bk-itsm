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
  <div :class="['bk-number', { 'focus': isFocus, 'disabled': disabled, 'is-error': isError }]" :style="exStyle">
    <div class="bk-number-content " :class="[{ 'bk-number-larger': size === 'large','bk-number-small': size === 'small' }]">
      <input
        type="text"
        :disabled="disabled"
        :placeholder="placeholder"
        class="bk-number-input"
        autocomplete="off"
        @keydown.up.prevent="add"
        @keydown.down.prevent="minus"
        @focus="focus"
        @blur="blur"
        @input="debounceHandleInput"
        :value="currentValue">
      <div class="bk-number-icon-content" v-if="!hideOperation">
        <!-- <div :class="['bk-number-icon-top', {'btn-disabled': isMax}]" @click="add">
                    <i class="bk-icon icon-angle-up"></i>
                </div>
                <div :class="['bk-number-icon-lower', {'btn-disabled': isMin}]" @click="minus">
                    <i class="bk-icon icon-angle-down"></i>
                </div>-->
      </div>
    </div>
  </div>
</template>
<script>
  import debounce from 'throttle-debounce/debounce';
  export default {
    name: 'bk-number-input',
    props: {
      value: {
        type: [Number, String],
        default: 0,
      },
      hideOperation: {
        type: Boolean,
        default: false,
      },
      type: {
        type: String,
        default: 'int',
      },
      exStyle: {
        type: Object,
        default() {
          return {};
        },
      },
      placeholder: {
        type: String,
        default: '',
      },
      disabled: {
        type: [String, Boolean],
        default: false,
      },
      min: {
        type: Number,
        default: Number.NEGATIVE_INFINITY,
      },
      max: {
        type: Number,
        default: Number.POSITIVE_INFINITY,
      },
      steps: {
        type: Number,
        default: 1,
      },
      size: {
        type: String,
        default: 'large',
        validator(value) {
          return [
            'large',
            'small',
          ].indexOf(value) > -1;
        },
      },
      debounceTimer: {
        type: Number,
        default: 100,
      },
    },
    data() {
      return {
        isMax: false,
        isMin: false,
        currentValue: '',
        isFocus: false,
        maxNumber: this.max,
        minNumber: this.min,
        isError: false,
        inputDom: null,
      };
    },
    watch: {
      min() {
        this.minNumber = this.min;
      },
      max() {
        this.maxNumber = this.max;
      },
      value: {
        immediate: true,
        handler(value) {
          value = `${value}`;
          if (value === '') {
            this.currentValue = value;
            return;
          }

          // let newVal = parseInt(value);

          // if (this.type === 'decimals') {
          //     newVal = Number(value);
          // }

          this.currentValue = value;
        },
      },
    },
    created() {
      this.debounceHandleInput = debounce(this.debounceTimer, (event) => {
        const { value } = event.target;
        this.inputHandler(value, event.target);
      });
    },
    methods: {
      focus(event) {
        this.isFocus = true;
        this.$emit('focus', event);
      },
      blur() {
        this.isFocus = false;
        this.$emit('blur', event);
      },
      getPower(val) {
        const valueString = val.toString();
        const dotPosition = valueString.indexOf('.');

        let power = 0;
        if (dotPosition > -1) {
          power = valueString.length - dotPosition - 1;
        }
        return Math.pow(10, power);
      },
      checkMinMax(val) {
        if (val <= this.minNumber) {
          val = this.minNumber;
          this.isMin = true;
        } else {
          this.isMin = false;
        }
        if (val >= this.maxNumber) {
          val = this.maxNumber;
          this.isMax = true;
        } else {
          this.isMax = false;
        }
        return val;
      },
      inputHandler(value, target) {
        if (value === '') {
          this.$emit('update:value', value);
          this.$emit('change', value);
          this.currentValue = value;
          target && (target.value = value);
          return;
        }
        if (value !== '' && value.indexOf('.') === (value.length - 1)) {
          return;
        }

        if (value !== '' && value.indexOf('.') > -1 && Number(value) === 0) {
          return;
        }
        // if (value !== '' && value.indexOf('-') === (value.length - 1)) {
        //     return
        // }

        let newVal = Number(value);

        if (this.type === 'decimals') {
          newVal = Number(value);
        }

        if (!isNaN(newVal)) {
          this.setCurrentValue(newVal, target);
        } else {
          target.value = this.currentValue;
        }
      },
      setCurrentValue(val, target) {
        // const oldVal = this.currentValue.toFixed(2)
        val = this.checkMinMax(val);
        this.$emit('update:value', val);
        this.$emit('change', val);
        this.currentValue = val;
        target && (target.value = val);
      },
      add() {
        if (this.disabled) return;
        const value = this.value || 0;
        if (typeof value !== 'number') return this.currentValue;
        const power = this.getPower(value);
        const newVal = (power * value + power * this.steps) / power;
        if (newVal > this.max) return;
        this.setCurrentValue(newVal);
      },
      minus() {
        if (this.disabled) return;
        const value = this.value || 0;
        if (typeof value !== 'number') return this.currentValue;
        const power = this.getPower(value);
        const newVal = Number(power * value - power * this.steps) / power;
        if (newVal < this.min) return;
        this.setCurrentValue(newVal);
      },
    },
  };
</script>
<style lang="scss" scoped>
    .bk-number{
        display: inline-block;
        .bk-number-content{
            color: #666;
            background-color: #fff;
            border-radius: 2px;
            box-sizing: border-box;
            border: 1px solid #c3cdd7;
            padding:0  10px;
            font-size: 14px;
            text-align: left;
            vertical-align: middle;
            &.disabled{
                background:#fafafa;
                .bk-number-input{
                    color:#ccc;
                }
                .bk-number-icon-content{
                    cursor:not-allowed;
                }
            }
            &.bk-number-larger{
                height:36px;
                line-height:36px;
                .bk-number-icon-content{
                    margin-top:3px !important;
                }
            }
            &.bk-number-small{
                height:32px;
                line-height:32px;
                .bk-number-icon-content{
                    margin-top:1px !important;
                }
            }
            .bk-number-input{
                width: 94%;
                -moz-appearance: textfield;
                border: none;
                outline: none;
                background: none;
                height:100%;
            }
            input::-webkit-outer-spin-button,
            input::-webkit-inner-spin-button{
                -webkit-appearance: none !important;
                margin: 0;
            }
            .bk-number-icon-content{
                line-height:1;
                cursor:pointer;
                i{
                    font-size:12px;
                    font-weight:bold;
                    color:#c3cdd7;
                }
            }
        }
    }
    .bk-number {
        &.is-error {
            border-color: red;
        }
    }
    .bk-number.disabled .bk-number-input {
        color: #ccc;
    }

</style>
