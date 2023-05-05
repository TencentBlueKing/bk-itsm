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
  <div class="bk-itsm-box">
    <div class="is-title" :class="{ 'bk-title-left': !sliderStatus }">
      <template v-if="!addStatus">
        <p class="bk-come-back">
          {{$t(`m['任务模板']`)}}
        </p>
      </template>
      <template v-else>
        <p class="bk-come-back" @click="backTab">
          <arrows-left-icon></arrows-left-icon>
          <template>{{templateInfo.itemInfo.name}}</template>
        </p>
      </template>
    </div>
    <div class="itsm-page-content">
      <div v-if="!addStatus" class="add-status">
        <div class="bk-itsm-service" v-bkloading="{ isLoading: listLoading }">
          <div class="bk-itsm-version" v-if="infoStatus">
            <i class="bk-icon icon-info-circle"></i>
            <span>{{$t(`m.taskTemplate['任务模版：管理使用不同任务场景下的任务模板。当流程中开启任务模块时，可以设置适用的任务模板。任务处理人只需要按照任务模板进行任务处理即可。']`)}}
            </span>
            <i class="bk-icon icon-close" @click="infoStatus = false"></i>
          </div>
          <div class="bk-normal-search">
            <bk-button
              data-test-id="taskTemplate-button-create"
              v-cursor="{ active: !hasPermission(['task_template_create']) }"
              :theme="'primary'"
              :title="$t(`m.systemConfig['新增']`)"
              icon="plus"
              :class="['mr10', 'plus-cus', {
                'btn-permission-disable': !hasPermission(['task_template_create'])
              }]"
              @click="addTemplate">
              {{$t(`m.systemConfig['新增']`)}}
            </bk-button>
            <div class="bk-search-key">
              <bk-input
                data-test-id="taskTemplate-input-search"
                :clearable="true"
                :right-icon="'bk-icon icon-search'"
                v-model="searchKey"
                @enter="getTemplateList"
                @clear="clearSearch">
              </bk-input>
            </div>
          </div>
          <div class="bk-task-content">
            <p class="bk-none-content" v-if="templateList.length === 0">
              <Empty :is-search="Boolean(searchKey)" :is-error="listError" @onClearSearch="clearSearch">
                <template v-if="!searchKey" slot="create">
                  <i class="bk-icon icon-info-circle"></i>
                  <span>{{$t(`m.taskTemplate['尚未创建任一任务模板，']`)}}</span>
                  <span
                    v-cursor="{ active: !hasPermission(['task_template_create']) }"
                    :class="['bk-primary', {
                      'text-permission-disable': !hasPermission(['task_template_create'])
                    }]"
                    @click="addTemplate">
                    {{$t(`m.taskTemplate['立即创建']`)}}
                  </span>
                </template>
              </Empty>
            </p>
            <ul v-else>
              <li v-for="(item, index) in templateList" :key="index" @click="editTemplate(item)">
                <span class="bk-task-icon">
                  <i class="bk-itsm-icon" :class="item.component_type === 'NORMAL' ? 'icon-itsm-icon-task' : 'icon-task-node'"></i>
                </span>
                <span class="bk-task-name" :title="item.name">
                  <span :style="{ maxWidth: item.is_draft ? 'calc(100% - 50px)' : '100%' }">{{ item.name || '--' }}</span>
                  <span v-show="item.is_draft">{{$t(`m.taskTemplate['(草稿)']`)}}</span>
                  <span>{{ item.update_at || '--' }}</span>
                </span>
                <span class="bk-task-operate">
                  <i class="bk-itsm-icon icon-itsm-icon-copy"
                    :data-test-id="`taskTemplate-i-cloneTemplate${index}`"
                    :class="{ 'icon-disable': item.component_type === 'SOPS' }"
                    v-bk-tooltips="item.component_type === 'SOPS' ? $t(`m.taskTemplate['标准运维模板不可克隆']`) : $t(`m.taskTemplate['克隆模板']`)"
                    @click.stop="cloneTemplate(item)"></i>
                  <i class="bk-icon icon-delete"
                    :data-test-id="`taskTemplate-i-deleteTemplate${index}`"
                    :class="{ 'icon-disable': item.is_builtin }"
                    v-bk-tooltips="item.is_builtin ? $t(`m.taskTemplate['内置模板不可删除']`) : $t(`m.taskTemplate['删除模板']`)"
                    @click.stop="deleteTemplate(item)"></i>
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>
      <div v-else class="step-wrap-content">
        <!-- 流程步骤 -->
        <div class="bk-itsm-tree">
          <div class="bk-tree-content">
            <div class="bk-tree-first" v-for="(item, index) in stepList" :key="item.id">
              <div class="bk-tree-shadow" @click="changeTree(item, index, 'tree')">
                <span
                  class="bk-tree-step"
                  :class="{ 'bk-tree-primary': item.type === 'primary', 'bk-tree-success': item.type === 'success', 'bk-tree-error': item.type === 'error' }">
                  <i class="bk-icon icon-check-1" v-if="item.type === 'success'"></i>
                  <i class="bk-icon icon-close" v-if="item.type === 'error'" style="font-size: 18px;"></i>
                  <span v-if="item.type !== 'success' && item.type !== 'error'">{{item.id}}</span>
                </span>
                <span
                  class="bk-tree-normal bk-tree-cursor"
                  :class="{ 'bk-tree-info': (item.show || item.type !== 'normal') }">{{item.name}}</span>
              </div>
              <span class="bk-tree-line" v-if="item.id !== stepList.length"></span>
            </div>
          </div>
        </div>
        <div class="bk-design-step">
          <common-step :template-info="templateInfo"
            :step="stepList.findIndex(step => step.show)"
            :step-list="stepList"></common-step>
        </div>
      </div>
    </div>
    <!-- 新增弹窗 -->
    <bk-dialog v-model="addDialogInfo.isShow"
      data-test-id="taskTemplate-dialog-taskCreate"
      :title="addDialogInfo.title"
      :auto-close="false"
      :mask-close="false"
      :render-directive="'if'"
      :header-position="'left'"
      :width="addDialogInfo.width"
      :ok-text="$t(`m.taskTemplate['进入配置']`)"
      @confirm="saveTemplate">
      <bk-form :label-width="150" :model="firstStepInfo" :rules="formRule" ref="taskInfoForm" :form-type="'vertical'">
        <bk-form-item
          data-test-id="taskTemplate-dialog-taskTemplateName"
          :label="$t(`m.taskTemplate['任务模板名称']`)"
          :required="true"
          :property="'name'"
          :ext-cls="'bk-form-width'">
          <bk-input v-model="firstStepInfo.name"
            maxlength="120">
          </bk-input>
        </bk-form-item>
        <bk-form-item :label="$t(`m.user['负责人：']`)">
          <member-select v-model="firstStepInfo.ownersInputValue"></member-select>
        </bk-form-item>
        <bk-form-item
          :label="$t(`m.taskTemplate['任务描述']`)"
          :ext-cls="'bk-form-width'">
          <bk-input
            :placeholder="$t(`m.taskTemplate['请输入任务描述']`)"
            :type="'textarea'"
            :rows="3"
            :maxlength="100"
            v-model="firstStepInfo.desc">
          </bk-input>
        </bk-form-item>
      </bk-form>
    </bk-dialog>
  </div>
</template>
<script>
  import commonStep from './components/commonStep';
  import memberSelect from '../../commonComponent/memberSelect';
  import permission from '@/mixins/permission.js';
  import { errorHandler } from '../../../utils/errorHandler';
  import Empty from '../../../components/common/Empty.vue';

  export default {
    name: 'taskTemplate',
    components: {
      commonStep,
      memberSelect,
      Empty,
    },
    mixins: [permission],
    data() {
      return {
        infoStatus: true,
        listError: false,
        // 新增流程页面切换
        addStatus: false,
        searchKey: '',
        // 流程树
        stepList: [
          {
            id: 1,
            name: this.$t('m.taskTemplate[\'创建任务配置\']'),
            type: 'primary',
            show: true,
            is_draft: false,
            stage: 'CREATE',
            signal: '',
          },
          {
            id: 2,
            name: this.$t('m.taskTemplate[\'处理任务配置\']'),
            type: 'normal',
            show: false,
            is_draft: false,
            stage: 'OPERATE',
            signal: '',
          },
          {
            id: 3,
            name: this.$t('m.taskTemplate[\'总结任务配置\']'),
            type: 'normal',
            show: false,
            is_draft: false,
            stage: 'CONFIRM',
            signal: '',
          },
        ],
        // 步骤组件值
        templateInfo: {
          itemInfo: {},
          newNode: false,
        },
        templateList: [],
        listLoading: false,
        addDialogInfo: {
          isShow: false,
          title: this.$t('m.taskTemplate[\'新增任务模板\']'),
          width: 500,
        },
        firstStepInfo: {
          name: '',
          ownersInputValue: [],
          desc: '',
        },
        formRule: {
          name: [
            {
              required: true,
              message: this.$t('m.taskTemplate[\'请输入任务名称\']'),
              trigger: 'blur',
            },
          ],
        },
      };
    },
    computed: {
      sliderStatus() {
        return this.$store.state.common.slideStatus;
      },
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
    },
    async mounted() {
      await this.initData();
    },
    methods: {
      async initData() {
        this.stepList[0].signal = 'CREATE_TASK,DELETE_TASK';
        this.stepList[1].signal = 'BEFORE_START_TASK,AFTER_FINISH_TASK';
        this.stepList[2].signal = 'AFTER_CONFIRM_TASK';
        await this.getTemplateList();
      },
      async getTemplateList() {
        const params = {
          name__icontains: this.searchKey,
        };
        this.listLoading = true;
        this.listError = false;
        await this.$store.dispatch('taskTemplate/getTemplateList', params).then((res) => {
          this.templateList = res.data;
        })
          .catch((res) => {
            this.listError = true;
            errorHandler(res, this);
          })
          .finally(() => {
            this.listLoading = false;
          });
      },
      cloneTemplate(item) {
        if (!this.hasPermission(['task_template_manage'], item.auth_actions)) {
          const resourceData = {
            task_template: [{
              id: item.id,
              name: item.name,
            }],
          };
          this.applyForPermission(['task_template_manage'], item.auth_actions, resourceData);
          return;
        }
        if (item.component_type === 'SOPS') {
          return;
        }
        this.$bkInfo({
          title: this.$t('m.taskTemplate["确定克隆该模板？"]'),
          confirmFn: () => {
            this.$store.dispatch('taskTemplate/cloneTemplate', item.id).then(() => {
              this.$bkMessage({
                message: this.$t('m.taskTemplate[\'克隆成功\']'),
                theme: 'success',
              });
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.getTemplateList();
              });
          },
        });
      },
      deleteTemplate(item) {
        if (!this.hasPermission(['task_template_manage'], item.auth_actions)) {
          const resourceData = {
            task_template: [{
              id: item.id,
              name: item.name,
            }],
          };
          this.applyForPermission(['task_template_manage'], item.auth_actions, resourceData);
          return;
        }
        if (item.is_builtin) {
          return;
        }
        this.$bkInfo({
          type: 'warning',
          title: '确认删除数据？',
          subTitle: '数据如果被删除，此数据在流程中不可用。',
          confirmFn: () => {
            this.$store.dispatch('taskTemplate/deleteTemplate', item.id).then(() => {
              this.$bkMessage({
                message: this.$t('m.systemConfig[\'删除成功\']'),
                theme: 'success',
              });
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.getTemplateList();
              });
          },
        });
      },
      // 编辑列表数据
      editTemplate(item) {
        if (!this.hasPermission(['task_template_view'], item.auth_actions)) {
          const resourceData = {
            task_template: [{
              id: item.id,
              name: item.name,
            }],
          };
          this.applyForPermission(['task_template_view'], item.auth_actions, resourceData);
          return;
        }
        this.changeStep(item);
      },
      // 新增模板
      addTemplate() {
        if (!this.hasPermission(['task_template_create'])) {
          this.applyForPermission(['task_template_create'], [], {});
          return;
        }
        this.firstStepInfo.desc = '';
        this.firstStepInfo.name = this.firstStepInfo.desc;
        this.firstStepInfo.ownersInputValue = [];
        this.addDialogInfo.isShow = true;
      },
      clearSearch() {
        this.searchKey = '';
        this.getTemplateList();
      },
      changeStep(item) {
        this.templateInfo.itemInfo = item.id ? item : {};
        this.addStatus = !this.addStatus;

        for (let i = 0; i < this.stepList.length; i++) {
          this.stepList[i].show = false;
          this.stepList[i].is_draft = item.is_draft;
          this.stepList[i].type = item.is_draft ? 'normal' : 'success';
        }
        this.stepList[0].show = true;
        this.stepList[0].type = 'primary';
        this.changeTree(this.stepList[0], 0);
      },
      // 切换树状态
      changeTree(item, index, source = 'step') {
        if (item.type === 'normal' || (item.type === 'primary' && !this.templateInfo.itemInfo.id)) {
          return;
        }
        const finishedStep = source === 'step' ? index : this.stepList.length - 1;
        for (let i = 0; i <= finishedStep; i++) {
          this.stepList[i].show = false;
          this.stepList[i].is_draft = item.is_draft;
          this.stepList[i].type = 'success';
        }
        this.stepList[index].show = true;
        this.stepList[index].type = 'primary';
      },
      changeTemplateInfo(item) {
        this.templateInfo.itemInfo = item;
      },
      // 返回列表数据
      backTab() {
        const item = {
          id: '',
          is_draft: true,
        };
        this.changeStep(item);
        this.getTemplateList();
      },
      async saveTemplate() {
        let valid = false;
        await this.$refs.taskInfoForm.validate().then(() => {
          valid = true;
        }, () => {});
        if (!valid) {
          return;
        }
        const params = {
          name: this.firstStepInfo.name,
          component_type: 'NORMAL',
          owners: this.firstStepInfo.ownersInputValue.join(','),
          is_draft: true,
          desc: this.firstStepInfo.desc,
        };
        await this.$store.dispatch('taskTemplate/createNewTemplate', params).then((res) => {
          this.$bkMessage({
            message: this.$t('m.taskTemplate[\'保存成功\']'),
            theme: 'success',
          });
          this.changeTemplateInfo(res.data);
          this.changeStep(this.templateInfo.itemInfo);
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.addDialogInfo.isShow = false;
          });
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import './taskCss/index';
    .itsm-page-content {
        padding: 0;
        .add-status {
            padding: 20px;
        }
    }
    .step-wrap-content {
        padding-top: 53px;
    }
</style>
