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
  <div v-if="taskList.length" class="task-list">
    <!-- 任务列表 -->
    <p class="list-title">任务列表</p>
    <div class="list-content">
      <div v-for="item in taskList" :key="item.id" class="content-item">
        <span class="van-ellipsis">{{ item.name }}</span>
        <div class="item-right">
          <i class="itsm-mobile-icon icon-copy copy-icon" @click="copyCut(item.name)" />
          <span class="item-status" :class="[statusMap[item.status].cls]">
            <van-icon v-if="item.status === 'FAILED'" name="warning-o" />
            {{ statusMap[item.status].name }}
          </span>
        </div>
        <input ref="inputRef" type="text">
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, toRefs, Ref, ref } from 'vue'
import { useStore } from 'vuex'
import { Toast } from 'vant'

interface TaskInfo {
  id: number,
  name: string,
  status: string
}

export default defineComponent({
  name: 'TaskList',
  props: {
    id: {
      type: Number,
      default: 0
    }
  },
  setup(props) {
    const { id } = toRefs(props)
    const store = useStore()
    const taskList: Ref<TaskInfo[]> = ref([])
    const inputRef = ref(null) // 获取输入框dom

    // 状态列表
    const statusMap = {
      NEW: { name: '新' },
      QUEUE: { name: '待处理' },
      WAITING_FOR_OPERATE: { name: '待处理' },
      WAITING_FOR_BACKEND: { name: '后台处理中' },
      RUNNING: { name: '执行中' },
      WAITING_FOR_CONFIRM: { name: '待总结', cls: 'bk-status-summary' },
      FINISHED: { name: '已完成', cls: 'bk-status-over' },
      FAILED: { name: '失败', cls: 'bk-status-error' },
      DELETED: { name: '已删除', cls: 'bk-status-delete' },
      REVOKED: { name: '已撤销', cls: 'bk-status-revoke' },
      SUSPENDED: { name: '已暂停', cls: 'bk-status-suspend' }
    }

    // 获取任务列表
    const getTaskList = async () => {
      const resp = await store.dispatch('ticket/getTaskList', {
        ticket_id: id.value
      })
      taskList.value = resp.data
    }
    getTaskList()

    // 复制任务文本
    const copyCut = (name: string): void => {
      inputRef.value.value = name  // 修改文本框的内容
      inputRef.value.select() // 选中文本
      document.execCommand('copy') // 执行浏览器复制命令
      inputRef.value.blur() // 失去焦点
      Toast.success({
        message: '已复制',
        icon: 'passed',
        className: 'common-toast'
      })
    }

    return { getTaskList, taskList, statusMap, copyCut, inputRef }
  }
})
</script>

<style lang="postcss" scoped>
  .task-list {
    margin: 24px 0 40px;
    font-size: 24px;
    color: #979ba5;
    border: 1px solid #d8d8d8;
    .list-title {
      padding: 0 24px;
      font-size: 24px;
      line-height: 50px;
      color: #63656e;
      background: #f0f1f5;
    }
    .list-content {
      background: #ffffff;
      padding: 0 24px;
      .content-item {
        height: 96px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 26px;
        color: #262626;
        line-height: 48px;
        box-shadow: 0px -1px 0px 0px #e6e6e6 inset;
        .item-right {
          flex: 1;
          min-width: 200px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          .copy-icon {
            top: 5px;
            font-size: 30px;
            color: #c8cad0;
          }
          .item-status {
            line-height: 34px;
            color: #699df4;
            text-align: right;
            .van-icon {
              top: 5px;
              font-size: 30px;
            }
            &.bk-status-over {
              color: #DCDEE5;
            }
            &.bk-status-summary {
              color: #2DCB56;
            }
            &.bk-status-error {
              color: #FF5656;
            }
            &.bk-status-delete {
              color: #DCDEE5;
            }
            &.bk-status-revoke {
              color: #DCDEE5;
            }
            &.bk-status-suspend {
              color: #DCDEE5;
            }
          }
        }
        input {
          position: absolute;
          left: 9999px;
          transform: scale(0);
        }
        &:last-child {
          box-shadow: none;
        }
      }
    }
  }

</style>
