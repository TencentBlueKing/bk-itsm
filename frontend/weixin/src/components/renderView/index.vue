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
  <div class="render-view">
    <template v-for="(item, index) in forms" :key="index">
      <RenderItem :type="getComponentType(item)" :form="item" />
    </template>
  </div>
  <van-popup v-model:show="isShowChildViewPopup" position="bottom" :style="{ height: '80%' }">
    <div v-if="isShowChildViewPopup" class="inner-render-view">
      <header class="inner-view-title">
        <span @click="toPrevInderForm">返回</span>
        <span>{{ currDisplayChildView.title }}</span>
        <span @click="clearInnerForms">关闭</span>
      </header>
      <div class="inner-render-view-content">
        <RenderItem
          v-for="(item) in currDisplayChildView.formData"
          :key="item"
          :type="getComponentType(item)"
          :form="item" />
      </div>
    </div>
  </van-popup>
</template>

<script lang="ts">
import RenderItem from './RenderItem.vue'
import { toRefs, defineComponent, provide, ref, computed } from 'vue'
import { IFormItem, IInnerForms } from './types'


export default defineComponent({
  name: 'RenderView',
  components: {
    RenderItem
  },
  props: {
    formData: {
      type: Array,
      default: () => ([])
    },
    context: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props) {
    const { formData, context }  = toRefs(props)
    provide('context', context.value)

    const getComponentType = (item: IFormItem): string => {
      const { schemes } = context.value
      return schemes[item.scheme].type
    }
    // 嵌套表单
    const innerForms = ref<IInnerForms []>([])
    const currDisplayChildView = computed(() => innerForms.value[innerForms.value.length - 1])
    const isShowChildViewPopup = computed({
      get() {
        return !!innerForms.value.length
      },
      set(val) {
        if (!val) {
          innerForms.value = []
        }
      }
    })
    const pushToInnerForms = (form: IInnerForms): void => {
      innerForms.value.push(form)
    }
    const clearInnerForms = (): void => {
      innerForms.value = []
    }
    const toPrevInderForm = (): void => {
      innerForms.value.pop()
    }
    const innerFormInstance = {
      pushToInnerForms,
      toPrevInderForm,
      clearInnerForms
    }
    provide('innerFormInstance', innerFormInstance)

    return {
      forms: formData,
      contexts: context,
      getComponentType,
      isShowChildViewPopup,
      currDisplayChildView,
      toPrevInderForm,
      clearInnerForms,
      innerForms
    }
  }
})
</script>

<style lang="postcss" scoped>
.render-view {
  padding: 0 20px;
}
.inner-render-view {
  &-content {
    padding: 20px;
  }
  .inner-view-title {
    padding: 0 20px;
    display: flex;
    justify-content: space-between;
    color: #63656e;
    font-size: 28px;
    line-height: 80px;
    border-bottom: 1px solid #e6e6e6;
  }
}
/* 字段通用样式 */
/deep/ .common-view-field {
  padding: 12px 18px;
  display: flex;
  width: 100%;
  font-size: 24px;
  text-align: left;
  color: #63656e;
  line-height: 34px;
  background: #fafafa;
  .view-label {
    flex-shrink: 0;
    width: 160px;
    word-break: break-all;
  }
  .view-value {
    margin-left: 10px;
    word-break: break-all;
  }
}
/deep/ .header-title {
  color: #63656e;
  font-size: 24px;
  font-weight: normal;
  line-height: 64px;
}
</style>
