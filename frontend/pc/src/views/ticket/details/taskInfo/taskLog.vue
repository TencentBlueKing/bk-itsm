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
  <div class="bk-task">
    <ul v-if="showTask || showHistory || showArticle" class="bk-flow-head">
      <li :class="{ 'bk-flow-check': checkInfo === 'task' }"
        v-if="showTask"
        @click="checkInfo = 'task'">
        <span>{{$t(`m.task['任务列表']`)}}</span>
      </li>
      <li :class="{ 'bk-flow-check': checkInfo === 'taskHistory' }"
        v-if="showHistory"
        @click="checkInfo = 'taskHistory'">
        <span>{{$t(`m.task['触发器记录']`)}}</span>
      </li>
      <li :class="{ 'bk-flow-check': checkInfo === 'slaRecord' }"
        @click="checkInfo = 'slaRecord'">
        <span>{{$t(`m.task['SLA记录']`)}}</span>
      </li>
      <li :class="{ 'bk-flow-check': checkInfo === 'article' }"
        v-if="showArticle"
        @click="checkInfo = 'article'">
        <span>{{$t(`m.task['关联文章']`)}}</span>
      </li>
    </ul>
    <div class="bk-task-content">
      <div v-if="checkInfo === 'task'">
        <task :basic-infomation="basicInfomation"
          :node-list="nodeList"
          @updateCurrentStep="updateCurrentStep">
        </task>
      </div>
      <div v-if="checkInfo === 'taskHistory'">
        <task-history :basic-infomation="basicInfomation" :node-list="nodeList"></task-history>
      </div>
      <div v-if="checkInfo === 'slaRecord'">
        <sla-record :basic-infomation="basicInfomation" :node-list="nodeList"></sla-record>
      </div>
      <div v-if="checkInfo === 'article'"></div>
    </div>
  </div>
</template>

<script>
  import task from './task';
  import taskHistory from './taskHistory';
  import slaRecord from './slaRecord';
  export default {
    name: 'taskLog',
    components: {
      task,
      taskHistory,
      slaRecord,
    },
    props: {
      basicInfomation: {
        type: Object,
        default() {
          return {};
        },
      },
      nodeList: {
        type: Array,
        default() {
          return [];
        },
      },
      openFunction: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        checkInfo: '',
        showArticle: '',
        showTask: '',
        showHistory: '',
      };
    },
    mounted() {
      this.showTask = this.openFunction.TASK_SWITCH && this.basicInfomation.task_schemas.length;
      this.showArticle = window.is_article_tag_show;
      this.showHistory = window.is_itsm_admin;
      this.checkInfo = 'slaRecord';
      if (this.showTask) {
        this.checkInfo = 'task';
      } else if (this.showArticle) {
        this.checkInfo = 'article';
      } else if (this.showHistory) {
        this.checkInfo = 'taskHistory';
      }
    },
    methods: {
      updateCurrentStep() {
        this.$emit('updateCurrentStep');
      },
    },
  };
</script>

<style scoped lang='scss'>
    @import './taskLog';
</style>
