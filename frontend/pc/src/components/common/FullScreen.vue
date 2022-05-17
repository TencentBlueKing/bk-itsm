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
  <div :class="{ 'full-screen-wrap': isFull }">
    <div v-if="isFull" class="full-screen-header">
      <span class="full-screen-title">{{ title }}</span>
      <div class="full-exit-btn" @click.stop="onClose">
        <i class="bk-itsm-icon icon-order-close"></i>
        <span class="exit-text">{{$t(`m.common['退出全屏']`)}}</span>
      </div>
    </div>
    <div class="full-screen-content">
      <slot></slot>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'FullScreen',
    props: {
      isFull: {
        type: Boolean,
        default: false,
      },
      title: {
        type: String,
        default: '',
      },
    },
    watch: {
      isFull(val) {
        if (val) {
          this.$bkMessage({
            message: this.$t('m.common["按 ESC 键退出全屏"]'),
          });
          document.addEventListener('keydown', this.handlerKeyDown);
        }
      },
    },
    methods: {
      onClose() {
        this.$emit('onClose');
      },
      handlerKeyDown(event) {
        if (event.keyCode === 27) {
          this.onClose();
          document.removeEventListener('keydown', this.handlerKeyDown);
        }
      },
    },
  };
</script>

<style lang='scss' scoped>
    .full-screen-wrap {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: #fff;
        z-index: 2100;
        .full-screen-header {
            height: 50px;
            line-height: 50px;
            font-size: 16px;
            color: #333948;
            .full-screen-title {
                margin-left: 15px;
                padding-left: 12px;
                position: relative;
                display: inline-block;
                &::before {
                    margin-top: -7px;
                    position: absolute;
                    left: 0;
                    top: 50%;
                    content: '';
                    width: 4px;
                    height: 14px;
                    background: #3c96ff;
                }
            }
            .full-exit-btn {
                float: right;
                padding: 0px 10px 0px 18px;
                color:#63656e;
                height: 50px;
                line-height: 50px;
                color: #979BA5;
                cursor: pointer;
                &:hover {
                    background-color: #dcdee5;
                }
                .icon-order-close {
                    font-size: 16px;
                }
                .exit-text {
                    font-size: 12px;
                }
            }
        }
        .full-screen-content {
            height: 100%;
        }
    }
</style>
