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
  <section class="common-card-block">
    <label class="common-card-label" :style="{ width: applyLabelWidth }">
      <slot name="label"></slot>
      {{ label }}
      <p class="common-card-desc">{{ desc }}</p>
    </label>
    <div class="common-card-body">
      <slot></slot>
    </div>
  </section>
</template>

<script>

  export default {
    name: 'SectionCard',
    props: {
      label: {
        type: String,
        default: '',
      },
      desc: {
        type: String,
        default: '',
      },
      labelWidth: {
        type: [String, Number],
        default: '',
      },
    },
    computed: {
      applyLabelWidth() {
        const w = this.labelWidth;
        if (typeof w === 'number') {
          return `${w}px`;
        }
        return w;
      },
    },
  };
</script>
<style lang='scss' scoped>
.common-card-block {
    padding: 20px;
    display: flex;
    background: #ffffff;
    border-radius: 2px;
    box-shadow: 0px 2px 6px 0px rgba(0,0,0,0.1);
    .common-card-label {
        width: 138px;
        font-size: 14px;
        font-weight: 700;
        text-align: left;
        color: #63656e;
        line-height: 19px;
        flex-shrink: 0;
        .common-card-desc {
            margin-top: 4px;
            width: 120px;
            font-size: 12px;
            color: #979ba5;
            line-height: 16px;
            word-break: break-all;
        }
    }
    .common-card-body {
        flex: 1;
    }
}
</style>
