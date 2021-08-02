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
  <div :class="['create-ticket-info', 'van-hairline--bottom', {'unfold': unfold }]">
    <div class="content-wrap">
      <div class="scroll-content">
        <p class="detail-title van-hairline--bottom">提单详情</p>
        <div class="field-info">
          <RenderField :is-view-mode="true" :fields="fields" :all-fields="allFields" />
        </div>
      </div>
    </div>
    <p v-if="showUnfoldIcon" class="unfold" @click="unfold = !unfold">
      <van-icon v-if="!unfold" name="arrow-down" />
      <van-icon v-else name="arrow-up" />
    </p>
  </div>
</template>
<script lang="ts">
import { defineComponent, onMounted, ref, toRefs, watch } from 'vue'
import RenderField from '@/components/renderField'

export default defineComponent({
  name: 'CreateTicketInfo',
  components: {
    RenderField
  },
  props: {
    fields: {
      type: Array,
      default: () => ([])
    },
    allFields: {
      type: Array,
      default: () => ([])
    },
    ticketDetail: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props) {
    const { fields }  = toRefs<{ fields: any  }>(props)
    const unfold = ref<boolean>(false)
    const showUnfoldIcon = ref<boolean>(false)
    watch(fields, () => {
      getContentHeight()
    })
    const getContentHeight = () => {
      setTimeout(() => {
        const createTicketInfoEl = document.querySelector('.create-ticket-info .scroll-content')
        if (createTicketInfoEl) {
          const { height } = createTicketInfoEl.getBoundingClientRect()
          const maxHeight = document.body.clientWidth * 0.5826667
          showUnfoldIcon.value = height > maxHeight
        }
      })
    }
    onMounted(() => {
      getContentHeight()
    })

    return {
      unfold,
      showUnfoldIcon
    }
  }
})
</script>
<style lang="postcss" scoped>
.create-ticket-info {
  position: relative;
  background: #ffffff;
  padding-bottom: 50px;
  &:after {
    border-color: #e6e6e6;
  }
  .content-wrap {
    padding: 0px 32px;
    max-height: 58.26667vw;
    overflow: hidden;
  }
  .unfold {
    position: absolute;
    left: 0;
    bottom: 0;
    width: 100%;
    height: 60px;
    line-height: 100px;
    text-align: center;
    color: #979BA5;
    background: #ffffff;
  }
  &.unfold {
    .content-wrap {
      max-height: initial;
    }
  }
  /deep/ .render-field {
    padding: 16px 0;
    background: #ffffff;
    .common-view-field {
      padding-left: 0;
      padding-right: 0;
      background: #ffffff;
    }
    .view-label {
      color: #979ba5;
    }
    .view-value {
      color: #000000;
    }
  }
}
.detail-title {
  &:after {
    color: #dcdee5;
  }
  padding: 24px 0;
  font-size: 28px;
  font-weight: 400;
  color: #000000;
}
</style>
