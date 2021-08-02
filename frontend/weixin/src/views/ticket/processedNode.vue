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
  <div class="processed-node">
    <p class="node-name" @click="toggleExtend">
      {{ node.name }}
      <template v-if="node.fields.length > 0">
        <van-icon :name="isExtended ? 'arrow-up' : 'arrow-down'" />
      </template>
    </p>
    <!-- 普通节点处理人、处理时间信息 -->
    <div v-if="!isMultipleProcessNode" class="basic-info">
      <div class="node-processors">
        <van-icon name="user-circle-o" />
        {{ commonData.processors }}
      </div>
      <span class="node-time">{{ commonData.update_at }}</span>
    </div>
    <!-- 节点展开详情 -->
    <div v-if="isExtended" class="node-detail">
      <!-- 普通节点字段详情 -->
      <render-field
        v-if="!isMultipleProcessNode"
        :is-view-mode="true"
        :fields="commonData.fields"
        :class="['step-render-form', { 'has-field': node.fields.length }]" />
      <!-- 审批多人、顺序会签处理详情 -->
      <template v-else>
        <template
          v-for="(task, index) in node.tasks"
          :key="index">
          <div
            v-if="task.status === 'FINISHED'"
            class="multiple-process-item">
            <div class="basic-info">
              <div class="node-processors">
                <van-icon name="user-circle-o" />
                {{ task.processor }}
              </div>
              <span class="node-time">{{ task.create_at }}</span>
            </div>
            <render-field
              :is-view-mode="true"
              :fields="task.fields"
              :class="['step-render-form', { 'has-field': task.fields.length }]" />
          </div>
        </template>
      </template>
    </div>
  </div>
</template>
<script lang="ts">
import { defineComponent, ref, toRefs, computed } from 'vue'
import RenderField from '../../components/renderField/index.vue'

export default defineComponent({
  name: 'ProcessedNode',
  components: {
    RenderField
  },
  props: {
    node: { // 当前节点详情
      type: Object,
      default: () => ({})
    },
    isMultipleProcessNode: {
      type: Boolean,
      default: false
    },
    isSingleProcessNode: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const { node, isSingleProcessNode } = toRefs(props)
    const isExtended = ref(false)
    const commonData = computed(() => {
      let { processors, update_at, fields } = node.value
      if (isSingleProcessNode.value && node.value.status === 'FINISHED') {
        const processInfo = node.value.tasks.find(item => item.status === 'FINISHED')
        processors = processInfo.processor
        update_at = processInfo.create_at
        fields = processInfo.fields
      }

      return { processors, update_at, fields }
    })

    const toggleExtend = (): void => {
      if (node.value.fields.length > 0) {
        isExtended.value = !isExtended.value
      }
    }

    return { isExtended, commonData, toggleExtend }
  }
})
</script>
<style lang="postcss" scoped>
  .processed-node {
    .node-name {
      position: relative;
      margin-bottom: 18px;
      padding-right: 40px;
      font-size: 28px;
      color: #63656e;
      line-height: 44px;
      .van-icon {
        position: absolute;
        right: 0px;
        top: 8px;
        font-size: 32px;
        color: #979ba5;
      }
    }
    .basic-info {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
      line-height: 40px;
      font-size: 24px;
      color: #979ba5;
      .node-processors {
        position: relative;
        flex: 1;
        margin-right: 10px;
        padding-left: 36px;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
        .van-icon {
          position: absolute;
          left: 0;
          top: 6px;
          font-size: 28px;
          vertical-align: middle;
        }
      }
      .node-time {
        display: inline-block;
        width: 280px;
        text-align: right;
      }
    }
    .multiple-process-item {
      margin-bottom: 40px;
    }
    .render-field.is-view-mode {
      background: #fafafa;
    }
  }
</style>
