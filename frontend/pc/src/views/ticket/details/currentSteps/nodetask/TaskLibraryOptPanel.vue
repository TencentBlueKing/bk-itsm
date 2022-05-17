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
  <div class="task-library-opt-panel">
    <div class="bk-button-group">
      <bk-button size="small"
        :class="[{ 'is-selected': type === 'new' }]"
        @click="onSwitchType('new')">
        {{ $t(`m.systemConfig['新增']`) }}</bk-button>
      <bk-button size="small"
        :class="[{ 'is-selected': type === 'update' }]"
        @click="onSwitchType('update')">
        {{ $t(`m.tickets['更新']`) }}</bk-button>
    </div>
    <bk-form ref="taskForm" :model="formData" :rules="rules" form-type="vertical" class="mt15">
      <bk-form-item
        :label="$t(`m.task['任务库名称']`)"
        :required="true"
        :property="'name'">
        <template v-if="type === 'new'">
          <bk-input
            v-model="formData.name"
            :placeholder="$t(`m.tickets['请输入任务库名称']`)"
            :max-length="120"></bk-input>
          <p class="desc">{{ $t(`m.tickets['存入任务库后，可用于快速创建任务']`) }}</p>
        </template>
        <bk-select v-else
          v-model="formData.name"
          searchable
          :loading="templateListLoading">
          <bk-option v-for="option in templateList"
            :key="option.id"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
      </bk-form-item>
    </bk-form>
    <div class="opt-btns">
      <span @click="onSbumit">{{ $t(`m.treeinfo['确定']`) }}</span>
      <span @click="$emit('close')">{{ $t('m.treeinfo["取消"]') }}</span>
    </div>
  </div>
</template>

<script>
  import { errorHandler } from '../../../../../utils/errorHandler';

  export default {
    name: 'TaskLibraryOptPanel',
    props: {
      taskList: {
        type: Array,
        default: () => ([]),
      },
      ticketInfo: {
        type: Object,
        default: () => ({}),
      },
    },
    data() {
      return {
        templateListLoading: false,
        type: 'new',
        formData: {
          name: '',
        },
        rules: { name: [
          {
            required: true,
            message: this.$t('m.task[\'任务库名称\']') + this.$t('m.newCommon["为必填项！"]'),
            trigger: 'blur',
          },
        ] },
        templateList: [],
      };
    },
    methods: {
      getLibraryList() {
        this.templateListLoading = true;
        this.$store.dispatch('taskFlow/getLibraryList', {
          service_id: this.ticketInfo.service_id,
        }).then((res) => {
          this.templateList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.templateListLoading = false;
          });
      },
      onSwitchType(type) {
        this.type = type;
        this.formData.name = '';
        if (type === 'update') {
          this.getLibraryList();
        }
      },
      async onSbumit() {
        const result = await this.$refs.taskForm.validate();
        if (!result) {
          return;
        }
        if (!this.taskList.length) {
          this.$bkMessage({
            message: this.$t('m.tickets[\'没有任务可以存入任务库\']'),
            theme: 'error',
          });
          return false;
        }
        if (this.type === 'new') {
          this.newTaskLibrary();
        } else {
          this.updataLibrary();
        }
      },
      newTaskLibrary() {
        const params = {
          name: this.formData.name,
          service_id: this.ticketInfo.service_id,
          tasks: this.taskList.map(item => item.id),
        };
        this.$store.dispatch('taskFlow/creatLibrary', params).then(() => {
          this.$bkMessage({
            message: this.$t('m.task[\'任务库创建成功\']'),
            theme: 'success',
          });
          this.$emit('close');
          this.resetForm();
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      updataLibrary() {
        const params = {
          tasks: this.taskList.map(item => item.id),
        };
        const id = this.formData.name;
        this.$store.dispatch('taskFlow/updataLibrary', { params, id }).then(() => {
          this.$bkMessage({
            message: this.$t('m.task[\'更新成功\']'),
            theme: 'success',
          });
          this.$emit('close');
          this.resetForm();
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      resetForm() {
        this.formData.name = '';
        this.type = 'new';
      },
    },
  };
</script>
<style lang='scss' scoped>
.task-library-opt-panel {
    padding: 10px;
    padding-top: 20px;
    min-height: 192px;
    .bk-button-group {
        width: 100%;
        text-align: center;
    }
    .desc {
        font-size: 12px;
        color: #979ba5;
    }
    .opt-btns {
        position: absolute;
        bottom: 4px;
        right: 4px;
        span {
            margin-left: 8px;
            color: #3a84ff;
            font-size: 12px;
            cursor: pointer;
        }
    }
}
</style>
