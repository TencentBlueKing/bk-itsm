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
  <div class="bk-trigger-info mt20" v-bkloading="{ isLoading: loading }">
    <div class="bk-service-name">
      <h1 style="padding-left: 10px">
        <span class="is-outline"></span>
        {{$t(`m.taskTemplate['任务配置']`)}}
        <i class="bk-itsm-icon icon-icon-info"
          v-bk-tooltips="$t(`m.taskTemplate['如果需要在流程中调用标准运维的业务流程进而创建任务，请在第一步的“填写流程信息”中，打开“是否关联业务”的开关。']`)"></i>
      </h1>
    </div>
    <div style="width: 100%">
      <div class="bk-trigger-add" @click="openCite">
        <i class="bk-itsm-icon icon-add-new"></i>
        <span>{{$t(`m.taskTemplate['添加流程任务']`)}}</span>
      </div>
      <!-- 模板列表 -->
      <div class="task-table">
        <ul class="bk-task-content">
          <li v-for="(item, index) in boundTaskList" :key="index" @click="editTemplate(item)">
            <span class="bk-task-icon">
              <i class="bk-itsm-icon" :class="item.component_type === 'NORMAL' ? 'icon-itsm-icon-task' : 'icon-task-node'"></i>
            </span>
            <span class="bk-task-name" :title="item.name">
              <span>{{ item.name || '--' }}</span>
              <span>{{ item.update_at || '--' }}</span>
            </span>
            <span class="bk-task-operate">
              <i class="bk-icon icon-delete"
                :class="{ 'icon-disable': item.builtIn }"
                v-bk-tooltips="$t(`m.taskTemplate['删除模板']`)"
                @click.stop="delTask(index)"></i>
              <i class="bk-itsm-icon icon-itsm-icon-three-seven"
                v-bk-tooltips="$t(`m.taskTemplate['跳转查看']`)"
                @click.stop="toTaskPage()"></i>
            </span>
          </li>
        </ul>
      </div>
      <!-- 模板配置 -->
      <div class="task-form" v-if="boundTaskList.length">
        <bk-form :label-width="170" :model="taskConfig" :rules="taskConfigRule" ref="taskForm">
          <bk-form-item :label="$t(`m.taskTemplate['条件配置：']`)" :required="true" :property="'createId'" class="config-form-item">
            <div class="config-content">
              <span>{{$t(`m.taskTemplate['创建任务的条件']`)}}</span>
              <div class="config-item">
                <span class="ml50 mr20">{{$t(`m.taskTemplate['处于']`)}}</span>
                <bk-select v-model="taskConfig.createId"
                  :placeholder="$t(`m.taskTemplate['请选择节点']`)"
                  :ext-cls="'bk-form-width'"
                  searchable
                  clearable
                  @change="getPostNodes">
                  <bk-option v-for="node in createList"
                    :key="node.id"
                    :id="node.id"
                    :name="node.name">
                  </bk-option>
                </bk-select>
                <span>{{$t(`m.taskTemplate['时']`)}}</span>
              </div>
            </div>
          </bk-form-item>
          <bk-form-item :property="'handleId'" class="config-form-item">
            <div class="config-content">
              <span>{{$t(`m.taskTemplate['处理任务的条件']`)}}</span>
              <div class="config-item">
                <span class="ml50 mr20">{{$t(`m.taskTemplate['处于']`)}}</span>
                <bk-select v-model="taskConfig.handleId"
                  :placeholder="$t(`m.taskTemplate['请选择节点']`)"
                  searchable
                  :ext-cls="'bk-form-width'"
                  clearable
                  :loading="handleListLoading">
                  <bk-option v-for="node in handleList"
                    :key="node.id"
                    :id="node.id"
                    :name="node.name">
                  </bk-option>
                </bk-select>
                <span class="mr40">{{$t(`m.taskTemplate['时']`)}}</span>
              </div>
            </div>
          </bk-form-item>
          <bk-form-item>
            <div class="config-content auto-height">
              <span>{{$t(`m.newCommon['应用设置']`)}}</span>
              <div class="config-item setting">
                <p>
                  <bk-checkbox class="ml50 mr20" :value="taskConfig.execute_can_create" @change="taskConfig.execute_can_create = !taskConfig.execute_can_create"></bk-checkbox>
                  <span>{{$t(`m.taskTemplate['处理任务的节点也可以创建任务']`)}}</span>
                </p>
                <p>
                  <bk-checkbox class="ml50 mr20" :value="taskConfig.waitTask" @change="taskConfig.waitTask = !taskConfig.waitTask"></bk-checkbox>
                  <span>{{$t(`m.taskTemplate['下一个节点流转是否必须等待任务处理完成']`)}}</span>
                </p>
              </div>
            </div>
          </bk-form-item>
        </bk-form>
      </div>
    </div>
    <template>
      <bk-dialog v-model="taskDialogInfo.isShow"
        theme="primary"
        width="660"
        :mask-close="false">
        <div slot="header" class="trigger-dialog-header">
          <span>{{$t(`m.taskTemplate['选择任务模板']`)}}</span>
          <div class="bk-search-key">
            <bk-input
              :clearable="true"
              :right-icon="'bk-icon icon-search'"
              v-model="taskDialogInfo.searchKey"
              @enter="searchInfo"
              @clear="clearSearch">
            </bk-input>
          </div>
        </div>
        <div class="trigger-dialog-box" v-bkloading="{ isLoading: taskDialogInfo.listLoading }">
          <p class="dialog-none-content" v-if="taskDialogInfo.list.length === 0">
            <i class="bk-icon icon-info-circle"></i>
            <span>{{$t(`m.taskTemplate['尚未创建任一任务模板，']`)}}</span>
            <span class="bk-primary" @click="toTaskPage">{{$t(`m.taskTemplate['跳转创建']`)}}</span>
          </p>
          <ul class="bk-task-dialog" v-else>
            <li v-for="(item, index) in taskDialogInfo.list"
              :key="index" @click="item.checked = !item.checked">
              <span class="bk-task-icon">
                <i class="bk-itsm-icon" :class="item.component_type === 'NORMAL' ? 'icon-itsm-icon-task' : 'icon-task-node'"></i>
              </span>
              <span class="bk-task-name" :title="item.name">
                <span>{{ item.name || '--' }}</span>
                <span>{{ item.update_at || '--' }}</span>
              </span>
              <span class="bk-task-operate">
                <bk-checkbox :value="item.checked"></bk-checkbox>
              </span>
            </li>
          </ul>
        </div>
        <div slot="footer" class="trigger-dialog-footer">
          <bk-checkbox :value="Boolean((taskDialogInfo.list.length === citeList.length) && taskDialogInfo.list.length)"
            :ext-cls="'checkbox'"
            :disabled="!taskDialogInfo.list.length"
            @change="selectAllFn">{{$t(`m.taskTemplate['全选']`)}}</bk-checkbox>
          <span>{{$t(`m.taskTemplate['已选']`)}}<span>{{citeList.length}}</span>个</span>
          <bk-button theme="primary"
            class="mr10"
            :title="$t(`m.taskTemplate['确定']`)"
            @click="citeTask">
            {{$t(`m.taskTemplate['确定']`)}}
          </bk-button>
          <bk-button theme="default"
            class="mr10"
            :title="$t(`m.taskTemplate['取消']`)"
            @click="initDialogInfo">
            {{$t(`m.taskTemplate['取消']`)}}
          </bk-button>
        </div>
      </bk-dialog>
    </template>
  </div>
</template>
<script>
  import { errorHandler } from '../../../../../utils/errorHandler';
  export default {
    name: 'workflowTaskList',
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
        loading: false,
        boundTaskList: [],
        taskDialogInfo: {
          isShow: false,
          searchKey: '',
          list: [],
          listLoading: false,
        },
        taskConfig: {
          createId: '',
          handleId: '',
          waitTask: true,
          execute_can_create: true,
        },
        taskConfigRule: {
          createId: [
            {
              required: true,
              message: this.$t('m.taskTemplate[\'请选择节点\']'),
              trigger: 'blur',
            },
          ],
          handleId: [
            {
              required: true,
              message: this.$t('m.taskTemplate[\'请选择节点\']'),
              trigger: 'blur',
            },
          ],
        },
        createList: [],
        handleList: [],
        handleListLoading: false,
      };
    },
    computed: {
      citeList() {
        return this.taskDialogInfo.list.filter(trigger => trigger.checked);
      },
    },
    async mounted() {
      await this.initData();
    },
    methods: {
      async initData() {
        this.loading = true;
        await this.getPublicTaskList();
        await this.getNodeList();
        if (this.workflowInfo.extras && this.workflowInfo.extras.task_settings) {
          const temp = this.workflowInfo.extras.task_settings;
          temp.task_schema_ids.forEach((task) => {
            const flag = this.taskDialogInfo.list.find(module => task === module.id);
            if (flag) {
              this.boundTaskList.push(flag);
            }
          });
          this.taskConfig.createId = temp.create_task_state;
          await this.getPostNodes();
          this.taskConfig.handleId = temp.execute_task_state;
          this.taskConfig.waitTask = temp.need_task_finished;
        }
      },
      // 获取流程节点
      async getNodeList() {
        await this.$store.dispatch('deployCommon/getStates', { workflow: this.workflowInfo.id }).then((res) => {
          this.createList = res.data.filter(node => !node.is_builtin && node.type !== 'ROUTER-P' && node.type !== 'COVERAGE');
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.loading = false;
          });
      },
      // 选择创建节点的回调
      async getPostNodes() {
        if (!this.taskConfig.createId) {
          this.taskConfig.handleId = '';
          this.handleList = JSON.parse(JSON.stringify(this.createList));
          return;
        }
        this.handleListLoading = true;
        this.taskConfig.handleId = '';
        await this.$store.dispatch('deployCommon/getOrderedStates', { id: this.taskConfig.createId }).then((res) => {
          this.handleList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.handleListLoading = false;
          });
      },
      // 全选函数
      selectAllFn() {
        const flag = this.taskDialogInfo.list.length !== this.citeList.length;
        this.taskDialogInfo.list.forEach((trigger) => {
          trigger.checked = flag;
        });
      },
      openCite() {
        this.boundTaskList.forEach((task) => {
          const temp = this.taskDialogInfo.list.find(pubTask => pubTask.id === task.id);
          if (temp) {
            temp.checked = true;
          }
        });
        this.taskDialogInfo.isShow = true;
      },
      citeTask() {
        this.boundTaskList = JSON.parse(JSON.stringify(this.citeList));
        this.taskDialogInfo.isShow = false;
      },
      // 删除模板
      delTask(index) {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.taskTemplate[\'确认删除该任务？\']'),
          subTitle: this.$t('m.taskTemplate[\'一旦删除，与任务相关的触发动作将会一并删除。\']'),
          confirmFn: () => {
            this.boundTaskList.splice(index, 1);
          },
        });
      },
      async getPublicTaskList() {
        const params = {
          name__icontains: this.taskDialogInfo.searchKey,
          // component_type: 'NORMAL',
          is_draft: false,
        };
        this.taskDialogInfo.listLoading = true;
        await this.$store.dispatch('taskTemplate/getTemplateList', params).then((res) => {
          this.taskDialogInfo.list = res.data.map(pubTask => ({
            ...pubTask,
            checked: false,
          }));
          // 流程未关联业务，则不显示标准运维模板
          if (!this.workflowInfo.is_biz_needed) {
            this.taskDialogInfo.list = this.taskDialogInfo.list.filter(template => template.component_type !== 'SOPS');
          }
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.taskDialogInfo.listLoading = false;
          });
      },
      toTaskPage() {
        this.$router.push({ name: 'TaskTemplate' });
      },
      initDialogInfo() {
        this.taskDialogInfo.isShow = false;
        this.taskDialogInfo.searchKey = '';
      },
      searchInfo() {
        this.getPublicTaskList();
      },
      clearSearch() {
        this.taskDialogInfo.searchKey = '';
        this.getPublicTaskList();
      },
      async checkData() {
        let valid = true;
        if (this.$refs.taskForm) {
          await this.$refs.taskForm.validate().then(() => {}, () => {
            valid = false;
          });
        }
        return valid;
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../publicTrigger/triggerCss/index';
    @import '../../../taskTemplate/taskCss/commonTrigger';
    @import '../../../taskTemplate/taskCss/index';
    .bk-task-dialog {
        margin-top: 13px;
        @include clearfix;
        li {
            width: calc(50% - 22px);
            display: inline-flex;
            align-items: center;
            margin-right: 22px;
            margin-bottom: 20px;
            border: 1px solid #DCDEE5;
            border-radius: 2px;
            height: 80px;
            background-color: #fff;
            cursor: pointer;
            @include clearfix;
        }
        .bk-task-icon {
            width: 60px;
            height: 80px;
            display: inline-flex;
            justify-content: flex-end;
            align-items: center;
            font-size: 18px;
            color: #979BA5;
            i{
                border-radius: 50%;
                background: #F0F1F5;
                line-height: 50px;
                text-align: center;
                width: 50px;
                height: 50px;
            }
        }
        .bk-task-name {
            width: calc(100% - 100px);
            padding-left: 10px;
            span{
                display: inline-block;
                height: 20px;
                line-height: 20px;
                font-size: 14px;
                color: #C4C6CC;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
            }
            span:first-child{
                max-width: calc(100% - 50px);
                color: #63656E;
                font-size: 14px;
                font-weight: bold;
            }
            span:last-child{
                display: block;
                font-size: 12px;
            }
        }
        .bk-task-operate {
            display: inline-flex;
            cursor: pointer;
            font-size: 18px;
            color: #3A84FF;
            .bk-icon, .bk-itsm-icon {
                margin-right: 20px;
            }
            .icon-disable{
                color: #C4C6CC;
                cursor: not-allowed;
            }
        }
    }
    .bk-form-width {
        width: 240px;
        display: inline-block;
        margin-right: 5px;
    }
    .config-form-item {
        /deep/ .icon-exclamation-circle-shape.tooltips-icon {
            left: 463px;
            right: inherit !important;
            top: 21px;
        }
    }
    .config-content{
        display: flex;
        min-width: 850px;
        align-items: center;
        height: 60px;
        font-size: 12px;
        border: 1px solid rgba(220,222,229,1);
        background: rgba(255,255,255,1);
        color: #63656E;
        &.auto-height {
            height: auto;
            display: table;
            &>span {
                display: table-cell;
                vertical-align: middle;
            }
            &>.config-item {
                display: table-cell;
            }
        }
        &>span{
            display: inline-block;
            width: 150px;
            font-weight: bold;
            height: 58px;
            line-height: 60px;
            text-align: center;
            background: #FAFBFD;
            border-right: 1px solid rgba(220,222,229,1);
        }

        .config-item{
            width: calc(100% - 150px);
            height: 100%;
            display: inline-flex;
            align-items: center;
            &.setting {
                display: block;
                padding: 14px 0;
            }
        }

    }
</style>
