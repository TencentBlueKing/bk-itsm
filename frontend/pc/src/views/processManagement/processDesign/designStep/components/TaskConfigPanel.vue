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
  <div class="task-form">
    <div class="use-task-config">
      <span class="mr5">{{ $t(`m.trigger['是否启用']`) }}</span>
      <bk-switcher v-model="useTask" @change="handleUseTaskChange"></bk-switcher>
    </div>
    <template v-if="useTask">
      <bk-form v-for="(oneCondition, index) in taskConditionList"
        :key="index" :model="oneCondition"
        :rules="taskConfigRule"
        class="mt10"
        form-type="vertical"
        ref="taskForms">
        <div class="task-condition clearfix">
          <div class="condition-item">
            <bk-form-item :label="$t(`m.taskTemplate['任务模板']`)" :required="true" :property="'taskId'">
              <bk-select v-model="oneCondition.taskId"
                :placeholder="$t(`m.basicModule['请选择']`) + $t(`m.taskTemplate['任务模板']`)"
                :ext-cls="'bk-form-width'"
                searchable
                clearable>
                <bk-option v-for="node in taskTemplateList"
                  :key="node.id"
                  :id="node.id"
                  :name="node.name">
                </bk-option>
              </bk-select>
            </bk-form-item>
          </div>
          <div class="condition-item">
            <bk-form-item :label="$t(`m.tickets['可创建任务节点']`)" :required="true" :property="'createNodeId'">
              <bk-select v-model="oneCondition.createNodeId"
                :placeholder="$t(`m.tickets['请选择可创建任务节点']`)"
                :ext-cls="'bk-form-width'"
                :loading="nodeListLoading"
                searchable
                clearable
                @change="getCanDealNodeList($event, oneCondition)">
                <bk-option v-for="node in normalNodeList"
                  :key="node.id"
                  :id="node.id"
                  :name="node.name"
                  :disabled="node.disabled">
                </bk-option>
              </bk-select>
            </bk-form-item>
          </div>
          <div class="condition-item">
            <bk-form-item :label="$t(`m.tickets['可处理任务的节点']`)" :required="true" :property="'dealNodeId'">
              <bk-select v-model="oneCondition.dealNodeId"
                :placeholder="$t(`m.tickets['请选择可处理任务的节点']`)"
                :ext-cls="'bk-form-width'"
                :loading="oneCondition.dealLoading"
                searchable
                clearable
                @change="handleDealNodeChange">
                <bk-option v-for="node in oneCondition.dealList"
                  :key="node.id"
                  :id="node.id"
                  :name="node.name">
                </bk-option>
              </bk-select>
            </bk-form-item>
          </div>
          <div class="condition-checkbox">
            <bk-checkbox-group v-model="oneCondition.others">
              <p><bk-checkbox :value="1">{{ $t(`m.taskTemplate['处理任务的节点也可以创建任务']`) }}</bk-checkbox></p>
              <p class="mt10"><bk-checkbox :value="2">{{ $t(`m.taskTemplate['下一个节点流转是否必须等待任务处理完成']`) }}</bk-checkbox></p>
            </bk-checkbox-group>
          </div>
          <div class="row-operating">
            <span @click="onAddCondition">+</span>
            <span @click="onDelCondition(index)">-</span>
          </div>
        </div>
      </bk-form>
    </template>
  </div>
</template>

<script>
  import { errorHandler } from '@/utils/errorHandler';
  function newTaskCondition() {
    return {
      taskId: '',
      createNodeId: '',
      dealNodeId: '',
      others: [1, 2],
    };
  }
  export default {
    name: 'TaskConfigPanel',
    components: {},
    props: {
      workflowInfo: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        taskConfigRule: {
          taskId: [
            {
              required: true,
              message: this.$t('m.taskTemplate[\'请选择任务模板\']'),
              trigger: 'blur',
            },
          ],
          createNodeId: [
            {
              required: true,
              message: this.$t('m[\'请选择可创建任务节点\']'),
              trigger: 'blur',
            },
          ],
          dealNodeId: [
            {
              required: true,
              message: this.$t('m[\'请选择可处理任务的节点\']'),
              trigger: 'blur',
            },
          ],
        },
        taskTemplateList: [],
        normalNodeList: [],
        taskConditionList: [],
        selectedDealNodeIds: [],
        useTask: false,
        nodeListLoading: false,
      };
    },
    computed: {
      taskSettings() {
        if (this.workflowInfo.extras && this.workflowInfo.extras.task_settings) {
          const taskSettings = this.workflowInfo.extras.task_settings;
          if (Array.isArray(taskSettings)) {
            return this.workflowInfo.extras.task_settings;
          }
        }
        return [];
      },
    },
    async created() {
      this.initTaskCondition();
      this.getTaskTemplateList();
      await this.getNodeList();
      this.handleDealNodeChange();
    },
    methods: {
      initTaskCondition() {
        if (this.workflowInfo.extras && this.workflowInfo.extras.task_settings) {
          const taskSettings = this.workflowInfo.extras.task_settings;
          if (Array.isArray(taskSettings)) {
            this.taskConditionList = taskSettings.map((setting) => {
              const con = {
                taskId: setting.task_schema_id,
                createNodeId: setting.create_task_state,
                dealNodeId: setting.execute_task_state,
                others: [],
                dealLoading: false,
                dealList: [],
              };
              if (setting.execute_can_create) {
                con.others.push(1);
              }
              if (setting.need_task_finished) {
                con.others.push(2);
              }
              return con;
            });
            this.taskConditionList.forEach((condition) => {
              this.getCanDealNodeList(condition.createNodeId, condition);
            });
            this.useTask = !!taskSettings.length;
          } else {
            errorHandler('taskSettings not Array', this);
          }
        }
      },
      getTaskTemplateList() {
        const params = {
          // name__icontains: '',
          is_draft: false,
        };
        return this.$store.dispatch('taskTemplate/getTemplateList', params).then((res) => {
          this.taskTemplateList = res.data.filter((task) => {
            // 流程未关联业务，则不显示标准运维模板
            if (!this.workflowInfo.is_biz_needed && task.component_type === 'SOPS') {
              return false;
            }
            return true;
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 获取流程节点
      async getNodeList() {
        this.nodeListLoading = true;
        return this.$store.dispatch('deployCommon/getStates', { workflow: this.workflowInfo.id }).then((res) => {
          this.normalNodeList = res.data.filter(node => !node.is_builtin && node.type !== 'ROUTER-P' && node.type !== 'COVERAGE');
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.nodeListLoading = false;
          });
      },
      // 选择创建节点的回调
      getCanDealNodeList(createNodeId, item) {
        if (!createNodeId) {
          return;
        }
        this.$set(item, 'dealLoading', true);
        return this.$store.dispatch('deployCommon/getOrderedStates', { id: createNodeId }).then((res) => {
          item.dealList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.$set(item, 'dealLoading', false);
          });
      },
      getAllDealNodeIds() {
        this.selectedDealNodeIds = this.taskConditionList.map(condition => condition.dealNodeId).filter(id => !!id);
      },
      handleDealNodeChange() {
        this.getAllDealNodeIds();
        this.normalNodeList.forEach((node) => {
          node.disabled = false;
          if (this.selectedDealNodeIds.includes(node.id)) {
            node.disabled = true;
          }
        });
      },
      onAddCondition() {
        this.taskConditionList.push(newTaskCondition());
      },
      onDelCondition(index) {
        this.taskConditionList.splice(index, 1);
        if (this.taskConditionList.length === 0) {
          this.useTask = false;
        }
      },
      async validate() {
        if (!this.useTask) {
          return true;
        }
        const checks = this.$refs.taskForms.map((form) => {
          const check = form.validate();
          return check;
        });
        return Promise.all(checks);
        // return checks.every(check => !!check)
      },
      getPostParams() {
        if (!this.useTask) {
          return [];
        }
        return this.taskConditionList.map(condition => ({
          create_task_state: condition.createNodeId,
          task_schema_id: condition.taskId,
          execute_task_state: condition.dealNodeId,
          need_task_finished: condition.others.indexOf(2) !== -1,
          execute_can_create: condition.others.indexOf(1) !== -1,
        }));
      },
      handleUseTaskChange(val) {
        if (val && !this.taskConditionList.length) {
          this.onAddCondition();
        }
      },
    },
  };
</script>
<style lang='scss' scoped>
@import '../../../../../scss/mixins/form.scss';
.bk-form-width {
    width: 240px;
    display: inline-block;
    margin-right: 5px;
}
.use-task-config {
    font-size: 14px;
    color: #63656e;
}
.task-form {
    .task-condition {
        width: calc(100% - 88px);
        position: relative;
        padding: 10px 100px 10px 24px;
        padding: 10px 24px;
        background: #fafbfd;
        border: 1px solid #dcdee5;
        .condition-item {
            display: inline-block;
            margin-right: 10px;
            margin-bottom: 10px;
            font-size: 12px;
            color: #63656e;
            /deep/ .bk-label .bk-label-text {
                font-size: 12px;
            }
        }
        .condition-checkbox {
            display: inline-block;
            vertical-align: text-bottom;
        }
        .row-operating {
            position: absolute;
            right: -67px;
            top: 50%;
            transform: translateY(-50%);
            height: 20px;
            span {
                display: inline-block;
                width: 20px;
                height: 20px;
                line-height: 16px;
                color: #fff;
                text-align: center;
                background: #c4c6cc;
                border-radius: 50%;
                cursor: pointer;
                &:hover {
                    background: #979ba5;
                }
                &:not(:first-child) {
                    margin-left: 10px;
                }
            }
        }
    }
}
</style>
