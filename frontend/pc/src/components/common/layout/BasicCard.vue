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
  <div class="basic-card-wrap">
    <div
      v-if="showFoldTitle"
      class="more-configuration mb20" @click="showMore = !showMore">
      <i v-if="!showMore" class="bk-icon icon-down-shape"></i>
      <i v-else class="bk-icon icon-up-shape"></i>
      <span>{{ foldTitle }}</span>
    </div>
    <collapse-transition>
      <div class="common-section-card-block" v-if="showMore">
        <label class="common-section-card-label">
          {{ cardLabel }}
          <p v-if="cardDesc" class="common-section-card-desc">{{ cardDesc }}</p>
        </label>
        <div class="common-section-card-body">
          <slot />
        </div>
      </div>
    </collapse-transition>
  </div>
</template>

<script>
  import collapseTransition from '@/utils/collapse-transition.js';
  export default {
    name: 'BasicCard',
    components: {
      collapseTransition,
    },
    props: {
      showFoldTitle: {
        type: Boolean,
        default: false,
      },
      foldTitle: {
        type: String,
        default: '',
      },
      firstUnfold: {
        type: Boolean,
        default: true,
      },
      cardLabel: {
        type: String,
        default: '',
      },
      cardDesc: {
        type: String,
        default: '',
      },
    },
    data() {
      return {
        showMore: true,
      };
    },
    watch: {
      isFold: {
        handler() {
          this.showMore = this.firstUnfold;
        },
        immediate: true,
      },
    },
  };
</script>
<style lang='scss' scoped>
@import '~@/scss/common-section-card.scss';
</style>
