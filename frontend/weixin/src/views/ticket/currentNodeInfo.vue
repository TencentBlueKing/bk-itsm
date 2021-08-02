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
  <div class="current-node-info">
    <p class="node-name">{{ node.name }}</p>
    <div v-if="!isMultipleProcessNode" class="processor-wrap">
      <van-icon name="user-circle-o" />
      <div class="label">处理人</div>
      <div class="processors">{{ node.processors }}</div>
    </div>
    <div v-else class="multiple-processor-wrap">
      <div class="label">
        <van-icon name="user-circle-o" />
        处理人
      </div>
      <div class="processors">
        <span
          v-for="item in node.tasks"
          :key="item"
          class="processor-item">
          {{ item.processor }}
          <span v-if="item.status === 'FINISHED'" class="status-icon">
            <van-icon name="success" />
          </span>
        </span>
      </div>
      <!-- 等待其他人员操作时，展示操作记录 -->
      <template v-if="!canOperate">
        <template
          v-for="(task, index) in node.tasks"
          :key="index">
          <div
            v-if="task.status === 'FINISHED'"
            class="process-history">
            <div class="basic-info">
              <div class="node-processors">
                <van-icon name="user-circle-o" />
                {{ task.processor }}
              </div>
              <span class="node-time">{{ task.create_at }}</span>
            </div>
            <render-field
              :is-view-mode="true"
              :highlight-refuse="true"
              :fields="task.fields"
              :class="['step-render-form', { 'has-field': task.fields.length }]" />
          </div>
        </template>
      </template>
    </div>
  </div>
</template>
<script lang="ts">
import { defineComponent, toRefs, computed } from 'vue'
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
    canOperate: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const { node } = toRefs(props)
    const isMultipleProcessNode = computed(() => {
      const { type, is_sequential, is_multi } = node.value
      return (type === 'SIGN' && is_sequential) || (type === 'APPROVAL' && is_multi)
    })

    return { isMultipleProcessNode }
  }
})
</script>
<style lang="postcss" scoped>
  .node-name {
    margin-bottom: 16px;
    line-height: 44px;
    font-size: 28px;
    font-weight: 700;
    color: #222222;
  }
  .processor-wrap {
    display: flex;
    justify-content: flex-start;
    .van-icon {
      margin-top: 4px;
      margin-right: 10px;
      font-size: 28px;
      color: #3a84ff;
    }
    .label {
      margin-right: 12px;
      font-size: 24px;
      color: #222222;
      line-height: 40px;
      white-space: nowrap;
    }
    .processors {
      font-size: 24px;
      color: #63656e;
      line-height: 40px;
      word-break: break-all;
    }
  }
  .multiple-processor-wrap {
    .label {
      display: flex;
      justify-content: flex-start;
      margin-bottom: 16px;
      font-size: 24px;
      line-height: 40px;
      color: #979ba5;
      .van-icon {
        margin-top: 4px;
        margin-right: 10px;
        font-size: 28px;
        color: #3a84ff;
      }
    }
    .processors {
      margin-bottom: 50px;
    }
    .processor-item {
      display: inline-flex;
      align-items: center;
      margin-right: 18px;
      color: #63656e;
      line-height: 32px;
      font-size: 24px;
      .status-icon {
        display: inline-block;
        margin-left: 6px;
        height: 24px;
        width: 24px;
        background: #ffffff;
        border-radius: 50%;
        font-size: 12px;
        color: #10b613;
      }
    }
  }
  .process-history {
    margin-bottom: 40px;
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
</style>
