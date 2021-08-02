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
  <div class="page-content">
    <router-view />
  </div>
</template>
<script lang="ts">
import { defineComponent } from 'vue'
import emitter from './utils/emitter'

export default defineComponent({
  name: 'App',
  created() {
    emitter.on('notify', (payload) => {
      const { type, message, duration } = payload
      this.$Notify({
        type,
        message,
        className: 'common-notify',
        duration: duration || 3000
      })
    })
    this.$store.dispatch('getServiceConfig')
  }
})
</script>
<style lang="postcss">
.app-container {
  height: 100%;
}
.page-content {
  height: 100%;
  .van-skeleton {
    padding-top: 50px;
    .van-skeleton__row {
      height: 30px;
    }
  }
}
.common-dialog.van-dialog {
  width: 686px;
  .van-dialog__header {
    font-size: 32px;
  }
  .van-dialog__message {
    padding: 80px 40px;
    font-size: 28px;
    line-height: initial;
    color: #000000;
  }
  .van-dialog__footer button {
    padding: 40px 0;
    font-size: 32px;
  }
}
.common-toast.van-toast {
  width: 240px;
  height: 240px;
  .van-icon {
    font-size: 62px;
    color: #3ecb55;
  }
  .van-toast__text {
    margin-top: 28px;
    font-size: 28px;
  }
}
.common-notify.van-notify {
  font-size: 24px;
  line-height: 32px;
}
</style>
