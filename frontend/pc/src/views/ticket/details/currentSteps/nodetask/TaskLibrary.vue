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
  <div class="task-library">
    <bk-form :label-width="200" form-type="vertical">
      <bk-form-item :label="$t(`m.task['任务库']`)" :required="true">
        <bk-select
          :loading="templateListLoading"
          v-model="formData.templateId"
          :placeholder="$t(`m.taskTemplate['请选择任务模板']`)"
          searchable
          @change="onTaskLibChange">
          <bk-option v-for="option in templateList"
            :key="option.id"
            :id="option.id"
            :name="option.name">
            <span>{{ option.name }}</span>
            <div class="del-lib-icon" @click.stop>
              <bk-popconfirm
                class="del-lib-icon"
                title="确定删除该任务库？"
                trigger="click"
                @confirm="handleDeleteTaskLib(option)">
                <i class="bk-icon icon-close"></i>
              </bk-popconfirm>
            </div>
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item :label="$t(`m.tickets['请勾选任务']`)" :required="true" v-if="formData.templateId">
        <bk-table
          v-bkloading="{ isLoading: taskListLoading }"
          :data="taskList"
          @selection-change="handleSelectedTaskChange">
          <bk-table-column type="selection" width="60"></bk-table-column>
          <bk-table-column :label="$t(`m.task['任务名称']`)" prop="name">
            <template slot-scope="props">
              <span class="task-name" @click="onTaskNameClick(props.row)">{{ props.row.name }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.task['处理人']`)" prop="processors">
            <template slot-scope="props">
              <span>{{ props.row.processors.replace(/^(,|，)+|(,|，)+$/g, '') }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.task['任务类型']`)">
            <template slot-scope="props">
              {{ getTaskZhName(props.row.component_type) }}
            </template>
          </bk-table-column>
        </bk-table>
      </bk-form-item>
    </bk-form>
    <div class="operation-btns mt20">
      <bk-button :theme="'primary'" type="submit" @click="handleSubmitClick" class="mr10" :loading="btnLoading">
        {{ $t(`m.systemConfig['确认']`) }}
      </bk-button>
      <bk-button class="mr10" @click="$emit('close')">
        {{ $t(`m['取消']`) }}
      </bk-button>
    </div>
    <bk-sideslider
      :is-show.sync="viewTaskInfo.show"
      :width="800"
      :quick-close="true"
      :title="$t(`m.task['查看任务']`)">
      <div slot="content" class="view-task-sideslider">
        <bk-form :ext-cls="'mb10'"
          :label-width="200"
          form-type="vertical">
          <!-- 处理人 -->
          <bk-form-item :label="$t(`m.task['处理人']`)"
            :required="true">
            <deal-person
              ref="personSelect"
              class="deal-person"
              :shortcut="true"
              :value="viewTaskInfo.dealPerson">
            </deal-person>
          </bk-form-item>
        </bk-form>
        <field-info
          v-if="viewTaskInfo.show"
          ref="fieldInfo"
          :fields="viewTaskInfo.item.fields"
          :basic-infomation="ticketInfo">
        </field-info>
        <div class="bk-task-disabled"></div>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import { errorHandler } from '../../../../../utils/errorHandler';
  import { TASK_TEMPLATE_TYPES } from '@/constants/task.js';
  import apiFieldsWatch from '@/views/commonMix/api_fields_watch.js';
  import fieldInfo from '@/views/managePage/billCom/fieldInfo.vue';
  import DealPerson from '@/views/processManagement/processDesign/nodeConfigue/components/dealPerson';

  export default {
    name: 'TaskLibrary',
    components: {
      fieldInfo,
      DealPerson,
    },
    mixins: [apiFieldsWatch],
    props: {
      ticketInfo: {
        type: Object,
        default: () => ({}),
      },
      nodeInfo: {
        type: Object,
        default: () => ({}),
      },
    },
    data() {
      return {
        btnLoading: false,
        taskListLoading: false,
        templateListLoading: false,
        formData: {
          templateId: '',
          selectedTask: '',
        },
        templateList: [],
        taskList: [],
        selectedTasks: [],
        viewTaskInfo: {
          show: false,
          item: null,
          dealPerson: {
            type: 'PERSON',
            value: '',
          },
        },
      };
    },
    mounted() {
      this.getLibraryList();
    },
    methods: {
      // 获取任务库列表
      getLibraryList() {
        this.templateListLoading = true;
        this.$store.dispatch('taskFlow/getLibraryList', {
          service_id: this.ticketInfo.service_id,
        }).then((res) => {
          this.templateList = res.data;
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.templateListLoading = false;
          });
      },
      // 获取任务库下的任务
      getLibraryTasks(id) {
        this.taskListLoading = true;
        const params = {
          task_lib_id: id,
        };
        this.$store.dispatch('taskFlow/getLibraryInfo', { params, id }).then((res) => {
          this.taskList = res.data;
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.taskListLoading = false;
          });
      },
      handleSubmitClick() {
        if (!this.selectedTasks.length) {
          return false;
        }
        const params = {
          batch_create: true,
          ticket_id: this.ticketInfo.id,
          tasks: [],
        };
        this.selectedTasks.forEach(task => {
          const taskParams = {
            processors: task.processors,
            processors_type: task.processors_type,
            fields: {},
            need_start: this.nodeInfo.can_execute_task, // 执行节点创建的任务需要立即启动
            state_id: this.nodeInfo.state_id,
            ticket_id: this.ticketInfo.id,
            task_schema_id: task.task_schema_id,
            source: 'template',
          };
          task.fields.forEach(field => {
            if (task.type === 'SOPS_TEMPLATE') {
              taskParams.fields[field.key] = {
                id: field.value.id,
                template_source: field.value.template_source,
                bk_biz_id: field.value.bk_biz_id,
                constants: field.value.constants,
              };
              taskParams.exclude_task_nodes_id = [];
            } else if (task.type === 'DEVOPS_TEMPLATE') {
              taskParams.fields.sub_task_params = field.value;
            } else {
              taskParams.fields[field.key] = field.value;
            }
          });
          params.tasks.push(taskParams);
        });
        this.btnLoading = true;
        this.$store.dispatch('taskFlow/createTask', { params }).then(() => {
          this.$bkMessage({
            message: this.$t('m.task[\'新建任务成功\']'),
            theme: 'success',
          });
          this.$emit('close', true);
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.btnLoading = false;
          });
      },
      onTaskLibChange(id) {
        this.getLibraryTasks(id);
      },
      getTaskZhName(key) {
        return TASK_TEMPLATE_TYPES.find(item => item.type === key).name;
      },
      handleSelectedTaskChange(selection) {
        this.selectedTasks = selection;
        console.log(selection, 'selection');
      },
      handleDeleteTaskLib(option) {
        const id = option.id;
        this.$store.dispatch('taskFlow/deleteLibrary', id).then(() => {
          this.$bkMessage({
            message: this.$t('m.serviceConfig["删除成功"]'),
            theme: 'success',
          });
          this.getLibraryList();
          // 删除了已选中任务库
          if (id === this.formData.templateId) {
            this.formData.templateId = '';
            this.taskList = [];
            this.selectedTasks = [];
          }
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      onTaskNameClick(row) {
        this.viewTaskInfo.show = true;
        this.viewTaskInfo.item = row;
        this.viewTaskInfo.dealPerson = {
          type: row.processors_type,
          value: row.processors,
        };
        const fields = row.fields.filter(item => item.type !== 'COMPLEX-MEMBERS');
        fields.forEach(item => {
          this.$set(item, 'showFeild', true);
          this.$set(item, 'val', item.value || '');
        });
        this.isNecessaryToWatch({ fields }, 'submit');
        this.viewTaskInfo.item.fields = fields;
      },
    },
  };
</script>
<style lang='scss' scoped>
.task-library {
    padding: 26px;
}
.del-lib-icon {
    font-size: 20px;
    position: absolute;
    right: 10px;
    top: 0px;
}
.task-name {
    color: #3a84ff;
    cursor: pointer;
}
.view-task-sideslider {
    padding: 26px;
    position: relative;
    .bk-task-disabled {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        cursor: not-allowed;
    }
}
</style>
