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
  <div v-if="item.showFeild">
    <bk-form
      ref="taskForm"
      :model="item.sopsContent"
      :rules="rules"
      :label-width="200"
      form-type="vertical">
      <template v-if="!editTask">
        <bk-form-item :label="$t(`m.newCommon['创建方式']`)" :required="true">
          <bk-radio-group v-model="item.sopsContent.createWay" @change="handleCreateWayChange">
            <bk-radio :disabled="disabled" class="bk-form-radio" :value="'template'">{{ $t(`m.newCommon["手动创建"]`) }}</bk-radio>
            <bk-radio :disabled="disabled" class="bk-form-radio" :value="'task'">{{ $t(`m.newCommon["关联未执行的任务"]`) }}</bk-radio>
            <bk-radio :disabled="disabled" class="bk-form-radio" :value="'started_task'">{{ $t(`m.newCommon["关联已执行的任务"]`) }}</bk-radio>
          </bk-radio-group>
        </bk-form-item>
        <bk-form-item :label="item.name" v-if="item.sopsContent.createWay === 'template'"
          :required="item.validate_type === 'REQUIRE'"
          :desc="item.tips"
          :ext-cls="'bk-line-height'"
          :property="'id'"
          :error-display-type="'normal'">
          <!-- 模板选择 -->
          <bk-select
            v-model="item.sopsContent.id"
            searchable
            @selected="onSelectTpl"
            ext-cls="form-item-inline-width mr5"
            :loading="loading.templateList"
            :disabled="typeInfo === 'RETRY' || disabled"
            :clearable="false">
            <bk-option
              v-for="(option, index) in templateList"
              :key="index"
              :name="option.name"
              :id="option.id">
            </bk-option>
          </bk-select>
          <!-- 方案选择 -->
          <bk-select
            v-if="item.sopsContent.id"
            v-model="item.sopsContent.planId"
            :loading="loading.plan"
            :disabled="disabled"
            multiple
            ext-cls="form-item-inline-width mr0"
            :placeholder="$t(`m['选择执行方案，默认选择全部任务节点']`)"
            @selected="onplanSelect">
            <bk-option v-for="option in planList"
              :key="option.id"
              :id="option.id"
              :name="option.name"
              class="sops-plan-option">
              <span>{{option.name}}</span>
              <span class="preview-sops-plan" @click.stop="jumpToSopsSelectSchemePage">
                <i class="bk-icon icon-eye"></i>
                {{ $t(`m.flowManager["预览"]`) }}
              </span>
            </bk-option>
            <div slot="extension"
              class="add-sops-scheme"
              @click="jumpToSopsSelectSchemePage">
              <i class="bk-icon icon-plus"></i>
              {{ $t(`m.newCommon['创建执行方案']`) }}
            </div>
          </bk-select>
          <div v-if="item.sopsContent.id" class="reload-template-plan" @click="onReloadPlanBtnClick">
            <i class="bk-icon icon-refresh"></i>
            {{ $t(`m.newCommon["刷新"]`) }}
          </div>
        </bk-form-item>
        <!-- 未执行/已执行任务列表 -->
        <bk-form-item
          v-else
          label="标准运维的任务选择"
          :required="true"
          :property="'sopsTaskId'">
          <bk-select
            v-model="item.sopsContent.sopsTask.id"
            :loading="loading.sopsTaskList"
            :disabled="disabled"
            searchable
            @change="onSopsTaskChange">
            <bk-option v-for="option in sopsTaskList"
              :key="option.id"
              :id="option.id"
              :name="option.name">
            </bk-option>
          </bk-select>
          <div class="preview-sops-task" v-if="item.sopsContent.sopsTask.id" @click.stop="jumpToSops">
            <i class="bk-icon icon-eye"></i>
            {{ $t(`m.flowManager["预览"]`) }}
          </div>
        </bk-form-item>
      </template>
    </bk-form>
    <!-- 标准运维参数 -->
    <div class="form-wrapper" v-if="!formLoading" v-bkloading="{ isLoading: configLoading }">
      <h3 class="setion-title">{{ $t(`m.newCommon["参数配置"]`) }}</h3>
      <render-form
        v-if="showRenderForm"
        ref="renderForm"
        :form-option="formOptions"
        :constants="item.sopsContent.constants"
        :context="item.sopsContent.context"
        :hooked="hookedVarList"
        v-model="item.sopsContent.formData"
        @configLoadingChange="configLoading = $event">
        <template slot="tagHook" slot-scope="{ scheme }">
          <div class="hook-area">
            <bk-checkbox
              :disabled="disabled || disabledRenderForm"
              :value="!!hookedVarList[scheme.tag_code]"
              @change="onHookChange($event, scheme)">
              {{ $t(`m.tickets["引用变量"]`) }}
            </bk-checkbox>
            <div v-if="hookedVarList[scheme.tag_code]" class="var-select">
              <bk-select
                :disabled="disabled || disabledRenderForm"
                :class="{ 'quote-error': quoteErrors.includes(scheme.tag_code) }"
                :clearable="false"
                :value="item.sopsContent.formData[scheme.tag_code].replace(/^\$\{/, '').replace(/\}$/, '')"
                @selected="onSelectVar($event, scheme)">
                <bk-option
                  v-for="varItem in quoteVars"
                  :key="varItem.key"
                  :id="varItem.key"
                  :name="varItem.name">
                  {{ varItem.name }}
                </bk-option>
              </bk-select>
              <span v-if="quoteErrors.includes(scheme.tag_code)" class="quote-error-text">{{ $t(`m.tickets["请选择变量"]`) }}</span>
              <i
                v-if="!item.sopsContent.constants.find(item => item.key === scheme.tag_code).changed"
                class="bk-icon icon-info update-tips"
                v-bk-tooltips.top="$t(`m.tickets['配置有更新']`)">
              </i>
            </div>
          </div>
        </template>
      </render-form>
      <no-data v-else></no-data>
    </div>
    <template v-if="item.checkValue">
      <p class="bk-task-error" v-if="item.checkMessage">{{ item.checkMessage }}</p>
      <p class="bk-task-error" v-else>{{ item.name }}{{$t('m.newCommon["为必填项！"]')}}</p>
    </template>
  </div>
</template>

<script>
  import NoData from '../../../components/common/NoData.vue';
  import { errorHandler } from '../../../utils/errorHandler';
  import { deepClone } from '../../../utils/util.js';
  import mixins from '../../commonMix/field.js';
  import commonMix from '../../commonMix/common.js';
  export default {
    name: 'SOPS_TEMPLATE',
    components: {
      NoData,
    },
    mixins: [mixins, commonMix],
    props: {
      item: {
        type: Object,
        required: true,
        default: () => {},
      },
      fields: {
        type: Array,
        default() {
          return [];
        },
      },
      isCurrent: {
        type: Boolean,
        default: false,
      },
      basicInfomation: {
        type: Object,
        default() {
          return {};
        },
      },
      typeInfo: {
        type: String,
        default() {
          return '';
        },
      },
      disabled: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        disabledRenderForm: false, // 单独禁用 renderform
        editTask: true,
        constantDefaultValue: {}, // 模板变量原始值
        templateList: [],
        planList: [],
        sopsTaskList: [],
        optionalNodeIdList: [], // 可选节点 id 列表
        hookedVarList: {}, // 被勾选为引用的变量
        quoteVars: [], // 可被引用列表
        quoteVarsLoading: false,
        quoteErrors: [], // 变量引用校验不同通过列表
        configLoading: false,
        formLoading: false,
        loading: {
          templateList: false,
          sopsTaskList: false,
          plan: false,
        },
        lastEditTaskName: '',
        rules: {},
        previewSopsTaskUrl: '',
      };
    },
    computed: {
      bkBizId() {
        return this.basicInfomation ? (this.basicInfomation.bk_biz_id !== -1 ? this.basicInfomation.bk_biz_id : '') : '';
      },
      showRenderForm() {
        return this.item.sopsContent.constants.filter(item => item.show_type === 'show').length > 0;
      },
      formOptions() {
        return {
          showRequired: true,
          showGroup: true,
          showLabel: true,
          showHook: true,
          showDesc: true,
          formEdit: !this.disabled && !this.disabledRenderForm,
        };
      },
    },
    created() {
      if (!this.item.sopsContent) {
        this.$set(this.item, 'sopsContent', {
          id: '',
          sopsTask: {
            id: '',
            template_id: '',
          },
          planId: '',
          createWay: 'template',
          exclude_task_nodes_id: [],
          formData: {},
          context: {
            project: {
              id: '',
              bk_biz_id: '',
              name: '',
              from_cmdb: true,
            },
            bk_biz_id: '',
            site_url: window.SITE_URL_SOPS + window.PREFIX_SOPS,
          },
          constants: [],
        });
      }
      this.rules.id = this.checkCommonRules('select').select;
      this.rules.sopsTaskId = this.checkCommonRules('select').select;
    },
    async mounted() {
      // 如果存在value信息，则需要解析信息进行渲染
      if (this.item.value) {
        this.item.sopsContent.id = this.item.value.id;
        const templateInfo = this.templateList.find(item => item.id === this.item.sopsContent.id);
        if (templateInfo && templateInfo.bk_biz_id !== undefined) {
          this.item.sopsContent.context.project.bk_biz_id = templateInfo.bk_biz_id;
          this.item.sopsContent.context.project.id = this.item.sopsContent.id;
          this.item.sopsContent.context.project.name = this.item.name;
        }
        this.item.sopsContent.constants = this.item.value.constants;
        this.item.value.constants.forEach((constant) => {
          if (constant.value) {
            this.item.sopsContent.formData[constant.key] = deepClone(constant.value);
          }
          if (constant.is_quoted) {
            this.hookedVarList[constant.key] = true;
          }
        });
      }
      this.editTask = !!this.item.value;
      if (this.editTask && this.item.value.id) { // 编辑任务时，需要加载模板详情
        this.getTemplateDetail(this.item.value.bk_biz_id, this.item.value.id);
      }
      if (this.basicInfomation.id) {
        this.getTicketOutput();
      }
      this.getTemplateList();
    },
    methods: {
      async getTicketOutput() {
        try {
          this.quoteVarsLoading = true;
          const res = await this.$store.dispatch('ticket/getTicketOutput', this.basicInfomation.id);
          this.quoteVars = res.data;
        } catch (e) {
          console.error(e);
        } finally {
          this.quoteVarsLoading = false;
        }
      },
      onSelectTpl(id) {
        this.item.sopsContent.id = id;
        const templateInfo = this.templateList.find(item => item.id === this.item.sopsContent.id);
        if (templateInfo && templateInfo.bk_biz_id !== undefined) {
          this.item.sopsContent.context.project.bk_biz_id = templateInfo.bk_biz_id;
          this.item.sopsContent.context.project.id = templateInfo.project_id;
          this.item.sopsContent.context.project.name = templateInfo.project_name;
        }
        this.hookedVarList = {};
        this.quoteErrors = [];
        this.getTempaltePlanList();
        this.getTemplateDetail(templateInfo.bk_biz_id, this.item.sopsContent.id);
      },
      // 选择标准运维任务
      onSopsTaskChange(sopsTaskId) {
        if (!sopsTaskId) {
          return false;
        }
        this.hookedVarList = {};
        this.quoteErrors = [];
        this.setTaskNameAndDisable(sopsTaskId);
        this.getSopsTaskDetail(sopsTaskId);
      },
      // 选择关联任务后，任务名称需要变成标准运维任务名称，且不能修改
      setTaskNameAndDisable(taskId) {
        const taskField = this.fields.find(m => m.key === 'task_name');
        const targetTask = this.sopsTaskList.find(task => task.id === taskId);
        if (taskField) {
          this.lastEditTaskName = taskField.val || taskField.value;
          taskField.val = targetTask.name;
          taskField.value = targetTask.name;
          taskField.is_readonly = true;
        }
        // 关联已执行的任务不能再修改参数
        this.disabledRenderForm = this.item.sopsContent.createWay === 'started_task';
      },
      clearTaskNameAndDisable() {
        if (!this.item.sopsContent.sopsTask.id) {
          return;
        }
        const taskField = this.fields.find(m => m.key === 'task_name');
        if (taskField) {
          taskField.val = this.lastEditTaskName;
          taskField.value = this.lastEditTaskName;
          taskField.is_readonly = false;
        }
      },
      // 获取标准运维任务详情
      async getSopsTaskDetail(sopsTaskId) {
        this.configLoading = true;
        const params = {
          bk_biz_id: this.bkBizId,
          task_id: sopsTaskId,
        };
        await this.$store.dispatch('taskFlow/getSopsTaskDetail', params).then((res) => {
          this.previewSopsTaskUrl = res.data.task_url;
          const constants = [];
          for (const key in res.data.constants) {
            if (res.data.constants[key].show_type === 'show') {
              constants.push(res.data.constants[key]);
            }
          }
          constants.sort((a, b) => a - b);
          this.item.sopsContent.constants = constants;
          this.item.sopsContent.sopsTask.template_id = res.data.template_id;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.configLoading = false;
          });
      },
      getTemplateDetail(bizId, tplId) {
        this.formLoading = true;
        const params = {
          template_id: tplId,
          bk_biz_id: bizId || '',
        };
        this.$store.dispatch('getTemplateDetail', params).then((res) => {
          const constants = [];
          res.data.constants.forEach((item) => {
            const constantItem = this.item.sopsContent.constants.find(cons => cons.key === item.key);
            if (!this.editTask || constantItem) {
              if (constantItem) {
                item = Object.assign(constantItem, item);
              }
              if (item.is_meta) {
                item.meta = deepClone(item);
              }
              if (this.item.value) {
                item.value = deepClone(this.item.sopsContent.formData[item.key]);
              }
              this.constantDefaultValue[item.key] = deepClone(item.value);
              if (item.show_type === 'show') {
                constants.push(item);
              }
            }
          });
          this.item.sopsContent.constants = constants;
          this.optionalNodeIdList = res.data.optional_ids;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.formLoading = false;
          });
      },
      // 获取templateList的数据
      async getTemplateList() {
        this.loading.templateList = true;
        const params = {
          bk_biz_id: this.bkBizId,
          with_common: true,
        };
        await this.$store.dispatch('getTemplateList', params).then((res) => {
          this.templateList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.loading.templateList = false;
          });
      },
      // 获取标准运维任务列表
      async getSopsTaskList() {
        this.loading.sopsTaskList = true;
        const params = {
          bk_biz_id: this.bkBizId,
          is_started: this.item.sopsContent.createWay === 'started_task',
        };
        await this.$store.dispatch('taskFlow/getSopsTask', params).then((res) => {
          this.sopsTaskList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.loading.sopsTaskList = false;
          });
      },
      // 获取模板方案列表
      async getTempaltePlanList() {
        const { id } = this.item.sopsContent;
        const template = this.templateList.find(template => template.id === id);

        this.planList = [];
        this.loading.plan = true;
        const params = {
          bk_biz_id: template.bk_biz_id,
          template_id: template.id,
        };
        await this.$store.dispatch('getTemplatePlanList', params).then((res) => {
          this.planList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.loading.plan = false;
          });
      },
      async onplanSelect(ids) {
        const planList = [];
        if (ids.length > 0) {
          ids.forEach((item) => {
            const plan = this.planList.find(plan => plan.id === item);
            if (plan.data) {
              const twPlanList = JSON.parse(plan.data);
              for (let index = 0; index < twPlanList.length; index++) {
                if (planList.indexOf(twPlanList[index]) === -1) {
                  planList.push(twPlanList[index]);
                }
              }
            }
          });
          this.item.sopsContent.exclude_task_nodes_id = this.optionalNodeIdList.filter(nodeId => !planList.includes(nodeId));
        } else {
          this.item.sopsContent.exclude_task_nodes_id = [];
        }
        const template = this.templateList.find(item => item.id === this.item.sopsContent.id);
        try {
          this.formLoading = true;
          const res = await this.$store.dispatch('taskFlow/getSopsPreview', {
            bk_biz_id: template.bk_biz_id,
            template_id: template.id,
            exclude_task_nodes_id: this.item.sopsContent.exclude_task_nodes_id,
          });
          const constants = [];
          for (const key in res.data.pipeline_tree.constants) {
            if (res.data.pipeline_tree.constants[key].show_type === 'show') {
              constants.push(res.data.pipeline_tree.constants[key]);
            }
          }
          constants.sort((a, b) => a.index - b.index);
          this.item.sopsContent.constants = constants;
        } catch (e) {
          console.error(e);
        } finally {
          this.formLoading = false;
        }
      },
      jumpToSops() {
        window.open(this.previewSopsTaskUrl);
      },
      handleCreateWayChange(value) {
        this.clearTaskNameAndDisable();
        this.item.sopsContent.id = '';
        this.item.sopsContent.planId = '';
        this.item.sopsContent.constants = [];
        this.item.sopsContent.sopsTask.id = '';
        if (value === 'task' || value === 'started_task') {
          this.getSopsTaskList();
        } else {
          this.getTemplateList();
        }
      },
      onReloadPlanBtnClick() {
        if (this.item.sopsContent.id) {
          this.getTempaltePlanList();
        }
      },
      validate() {
        this.$refs.taskForm.validate();
        let renderFormStatus = true;
        if (this.disabled || this.disabledRenderForm) {
          renderFormStatus = true;
        } else if (this.$refs.renderForm) {
          renderFormStatus = this.$refs.renderForm.validate();
        }
        const formDataStatus = this.item.sopsContent.createWay === 'template'
          ? !!this.item.sopsContent.id
          : !!this.item.sopsContent.sopsTask.id;
        const quoteFormStatus = Object.keys(this.hookedVarList).every((key) => {
          if (this.hookedVarList[key] && this.item.sopsContent.formData[key] === '') {
            this.quoteErrors.push(key);
            return false;
          }
          return true;
        });
        return renderFormStatus && formDataStatus && quoteFormStatus;
      },
      jumpToSopsSelectSchemePage() {
        const templateId = this.item.sopsContent.id;
        const templateInfo = this.templateList.find(item => item.id === templateId);
        const projectId = templateInfo.project_id;
        const selectSchemeUrl = `taskflow/newtask/${projectId}/selectnode/?template_id=${templateId}&entrance=templateEdit`;
        window.open(window.SOPS_URL + selectSchemeUrl, '__blank');
      },
      // 引用/取消引用变量
      onHookChange(val, scheme) {
        this.$set(this.hookedVarList, scheme.tag_code, val);
        const constantItem = this.item.sopsContent.constants.find(item => item.key === scheme.tag_code);
        constantItem.is_quoted = val;
        if (val) {
          this.item.sopsContent.formData[scheme.tag_code] = '';
        } else {
          this.item.sopsContent.formData[scheme.tag_code] = constantItem ? deepClone(this.constantDefaultValue[scheme.tag_code]) : '';
          const index = this.quoteErrors.findIndex(item => item === scheme.tag_code);
          if (index > -1) {
            this.quoteErrors.splice(index, 1);
          }
        }
      },
      onSelectVar(id, scheme) {
        this.item.sopsContent.formData[scheme.tag_code] = `\${${id}}`;
        const index = this.quoteErrors.findIndex(item => item === scheme.tag_code);
        if (index > -1) {
          this.quoteErrors.splice(index, 1);
        }
      },
    },
  };
</script>

<style lang='scss' scoped>
.bk-form-radio {
    margin-right: 30px;
}
.form-wrapper {
    margin: 20px 0;
}
.setion-title {
    padding-bottom: 13px;
    color: #313238;
    font-size: 14px;
    line-height: 20px;
    border-bottom: 1px solid #cacedb;
}
.preview-sops-task {
    position: absolute;
    right: -48px;
    top: 0px;
    color: #3a84ff;
    font-size: 12px;
    cursor: pointer;
}
.form-item-inline-width {
    margin: 0;
    display: inline-block;
    width: calc(50% - 5px);
}
.reload-template-plan, .preview-sops-task {
    position: absolute;
    right: -48px;
    top: 0px;
    color: #3a84ff;
    font-size: 12px;
    cursor: pointer;
}
.add-sops-scheme {
    color: #3a84ff;
    text-align: center;
    cursor: pointer;
}
.sops-plan-option /deep/ .bk-option-content{
    display: flex;
    justify-content: space-between;
    .preview-sops-plan {
        display: none;
    }
    &:hover .preview-sops-plan{
        display: inline-block;
    }
}
.hook-area {
    display: flex;
    height: 32px;
    flex-wrap: nowrap;
    align-items: center;
    .var-select {
        position: relative;
        margin-left: 14px;
        width: 200px;
        .quote-error {
            border-color: #ff5757;
        }
    }
    .quote-error-text {
        position: absolute;
        bottom: -20px;
        left: 0;
        color: #ff5757;
    }
    .update-tips {
        position: absolute;
        right: -20px;
        top: 10px;
        font-size: 14px;
        color: #ff9c01;
        cursor: pointer;
    }
}
/deep/ .rf-form-item{
    .rf-tag-hook {
        top: 40px;
    }
    &.rf-has-hook > .rf-tag-form {
        margin-right: 96px;
    }
    &.rf-has-hook.rf-hooked > .rf-tag-form {
        margin-right: 316px;
    }
}
/deep/ .rf-form-group {
    .rf-tag-hook {
        top: 40px;
    }
    &.rf-has-hook .rf-tag-form {
        margin-right: 96px;
    }
    &.rf-has-hook.rf-hooked .rf-tag-form {
        margin-right: 316px;
    }
}
</style>
