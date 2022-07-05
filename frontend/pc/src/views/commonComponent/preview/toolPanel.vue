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
  <div class="tools-wrapper" v-if="fullStatus">
    <div class="tool-item" data-test-id="tools-warpper-ZoomIn" @click="onZoomIn" :title="$t(`m.treeinfo['放大']`)">
      <i class="bk-itsm-icon icon-order-add icon-cus"></i>
    </div>
    <div class="tool-item" data-test-id="tools-warpper-ZoomOut" @click="onZoomOut" :title="$t(`m.treeinfo['缩小']`)">
      <i class="bk-itsm-icon icon-order-reduce icon-cus"></i>
    </div>
    <!-- <div class="tool-item" @click="onResetPosition">
            <i class="bk-itsm-icon icon-flow-restore"></i>
        </div> -->
  </div>
</template>
<script>
  export default {
    name: 'toolPanel',
    props: {
      fullStatus: {
        type: Boolean,
        default() {
          return false;
        },
      },
    },
    data() {
      return {};
    },
    methods: {
      onZoomIn() {
        this.$emit('onZoomIn');
      },
      onZoomOut() {
        this.$emit('onZoomOut');
      },
      onResetPosition() {
        this.$emit('onResetPosition');
      },
    },
  };
</script>
<style lang="scss" scoped>
    .tools-wrapper {
        .tool-item {
            display: inline-block;
            font-size: 20px;
            cursor: pointer;
            line-height: 38px;
            &:hover {
                background-color: #fff!important;
            }
            .icon-cus{
                position: relative;
                top: -3px;
                &:before{
                    color: #979BA5;
                }
                &:hover{
                    &:before{
                        color: #63656E;
                    }
                }
            }
        }
    }
</style>
