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
  <div v-if="!isViewMode" class="not-support required">
    <span class="van-ellipsis">{{ item.name }}
      <van-icon name="info-o" color="#ffb213" @click="handelNotSupportPrompt" />
    </span>
    <div class="content-right text-status">
      请选择
    </div>
  </div>
  <p v-else class="common-view-field">
    <label class="view-label">{{ item.name }}</label>
    <span class="view-value" style="color: #e5e6e9;">暂不支持显示</span>
  </p>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { Toast } from 'vant'

export default defineComponent({
  name: 'NotSupport',
  props: {
    item: {
      type: Object,
      default: () => ({})
    },
    isViewMode: {
      type: Boolean,
      default: false
    }
  },
  setup() {
    const handelNotSupportPrompt = () => {
      Toast({
        message: '暂不支持操作，请至PC端处理',
        className: 'not-support-toast'
      })
    }
    return { handelNotSupportPrompt }
  }
})

</script>

<style lang="postcss">
  .not-support {
    position: relative;
    width: 100%;
    height: 90px;
    display: flex;
    background: #fff;
    align-items: center;
    justify-content: space-between;
    font-size: 26px;
    color: #63656e;
    line-height: 48px;
    border-bottom: 1px solid rgba(0,0,0,.12);
    &.required::before {
      position: absolute;
      left: -12px;
      color: #ee0a24;
      font-size: 1em;
      content: "*";
      color: #ee0a24;
    }
    .van-icon {
      margin-left: 5px;
      display: inline-block;
      vertical-align: middle;
      font-size: 28px;
    }
    .content-right {
      color: #e5e6e9;
    }
  }
  .not-support-toast {
    width: 640px;
    height: 100px;
    line-height: 100px;
    .van-toast__text {
      font-size: 28px;
    }
  }
</style>
