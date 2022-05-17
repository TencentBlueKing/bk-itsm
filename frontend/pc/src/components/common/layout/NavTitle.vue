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
  <div class="nav">
    <div class="nav-title">
      <arrows-left-icon v-if="showIcon" @click="goBack"></arrows-left-icon>
      <span class="title-name">{{ titleName }}</span>
      <div class="step">
        <slot name="step"></slot>
      </div>
    </div>
    <div class="nav-tab">
      <slot name="tab"></slot>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'navTitle',
    props: {
      showIcon: {
        type: Boolean,
        default: false,
      },
      titleName: {
        type: String,
        default: '--',
      },
    },
    methods: {
      goBack() {
        this.$emit('goBack');
      },
    },
  };
</script>

<style lang="scss" scoped>
    .nav {
        position: relative;
        z-index: 101;
        box-shadow: 0px 2px 2px 0px rgba(0,0,0,0.1);
        .nav-title {
            height: 52px;
            display: flex;
            align-items: center;
            font-size: 16px;
            padding-left: 14px;
            position: relative;
            background-color: #fff;
            .title-name {
                font-size: 16px;
                margin-left: 11px;
            }
            .step {
                width: 600px;
                margin: 0 auto;
            }
        }
        /deep/ .nav-tab {
            background: #fff;
            .bk-tab-label-wrapper {
                padding-left: 10px;
            }
        }
        /deep/ .nav-step {
            top: 0;
            left: 0;
            position: absolute;
            margin: 0 auto;
        }
    }

</style>
