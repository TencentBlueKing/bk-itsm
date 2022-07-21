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
  <div v-if="item.showFeild" class="ci-template">
    <bk-form
      ref="devopsForm"
      :model="item.devopsContent"
      :rules="defaultRules"
      :label-width="200"
      form-type="vertical">
      <bk-form-item :label="$t(`m.tickets['项目']`)" :required="true" property="project_id" error-display-type="normal">
        <bk-select
          v-model="item.devopsContent.project_id"
          :loading="projectLoading"
          searchable
          :disabled="disabled"
          @selected="handleProjectChange">
          <bk-option v-for="option in projectList"
            :key="option.projectCode"
            :id="option.projectCode"
            :name="option.project_name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item :label="$t(`m.tickets['流水线']`)" :required="true" property="pipeline_id" error-display-type="normal">
        <bk-select
          v-model="item.devopsContent.pipeline_id"
          :loading="pipelineLoading"
          searchable
          :disabled="disabled"
          @selected="handlePipelineChange">
          <bk-option v-for="option in pipelineList"
            :key="option.pipelineId"
            :id="option.pipelineId"
            :name="option.pipelineName">
          </bk-option>
        </bk-select>
      </bk-form-item>
    </bk-form>
    <h3 class="setion-title">
      <span class="setion-title-icon" @click.stop="showPipelineVariable = !showPipelineVariable">
        <i v-if="showPipelineVariable" class="bk-icon icon-angle-down"></i>
        <i v-else class="bk-icon icon-angle-right"></i>
      </span>
      {{ $t(`m.tickets['流水线变量']`) }}
    </h3>
    <bk-form
      v-show="showPipelineVariable"
      v-bkloading="{ isLoading: pipelineStartLoading }"
      ref="devopsVariable"
      :model="item.devopsContent.variables"
      :label-width="200"
      form-type="vertical">
      <bk-form-item
        v-for="variable in pipelineVariableList"
        :key="variable.id"
        :label="variable.id"
        :required="true"
        :property="variable.id"
        :rules="rules[variable.id]"
        class="half-width-item"
        error-display-type="normal">
        <bk-input
          v-model="item.devopsContent.variables[variable.id]"
          :disabled="disabled"
          :clearable="true">
        </bk-input>
        <!-- TODO: 暂时只支持输入框输入变量 -->
        <!-- <bk-select
                    v-else
                    v-model="item.devopsContent.project_id"
                    :loading="projectLoading"
                    searchable
                    @change="handleProjectChange">
                    <bk-option v-for="option in projectList"
                        :key="option.project_id"
                        :id="option.project_id"
                        :name="option.project_name">
                    </bk-option>
                </bk-select> -->
      </bk-form-item>
    </bk-form>
    <h3 class="setion-title border-none">
      <span class="setion-title-icon" @click.stop="showPipelineStages = !showPipelineStages">
        <i v-if="showPipelineStages" class="bk-icon icon-angle-down"></i>
        <i v-else class="bk-icon icon-angle-right"></i>
      </span>
      {{ $t(`m.tickets['插件预览']`) }}
    </h3>
    <devops-preview
      v-show="showPipelineStages"
      :stages="pipelineStages"
      :loading="pipelineDetailLoading">
    </devops-preview>
  </div>
</template>

<script>
  import { errorHandler } from '@/utils/errorHandler';
  import i18n from '@/i18n/index.js';
  import DevopsPreview from '@/components/task/DevopsPreview.vue';
  function newRequiredRule() {
    return {
      required: true,
      message: i18n.t('m.treeinfo["字段必填"]'),
      trigger: 'blur',
    };
  }
  const defaultRules = {
    project_id: [newRequiredRule()],
    pipeline_id: [newRequiredRule()],
  };
  export default {
    name: 'DEVOPS_TEMPLATE',
    components: {
      DevopsPreview,
    },
    props: {
      item: {
        type: Object,
        required: true,
        default: () => {},
      },
      basicInfomation: {
        type: Object,
        default() {
          return {};
        },
      },
      disabled: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        projectLoading: false,
        pipelineLoading: false,
        pipelineStartLoading: false,
        pipelineDetailLoading: false,
        showPipelineVariable: true,
        showPipelineStages: true,
        defaultRules: {
          project_id: [{
            required: true,
            message: i18n.t('m.treeinfo["字段必填"]'),
            trigger: 'blur',
          }],
          pipeline_id: [{
            required: true,
            message: i18n.t('m.treeinfo["字段必填"]'),
            trigger: 'blur',
          }],
        },
        rules: {
          project_id: [newRequiredRule()],
          pipeline_id: [newRequiredRule()],
        },
        projectList: [], // 项目列表
        pipelineList: [], // 流水线列表
        pipelineStartInfo: {}, // 流水线启动信息
        pipelineVariableList: [], // 流水线变量
        pipelineStages: [], // 流水线阶段列表
      };
    },
    created() {
      if (!this.item.devopsContent) {
        this.$set(this.item, 'devopsContent', {
          project_id: '',
          pipeline_id: '',
          variables: {},
        });
      }
    },
    mounted() {
      this.getDevopsUserProjectList();
      if (this.item.value) {
        const { pipeline_id, project_id } = this.item.value;
        this.item.devopsContent = {
          project_id,
          pipeline_id,
          variables: JSON.parse(JSON.stringify({
            ...this.item.value,
            project_id: undefined,
            pipeline_id: undefined,
          })),
        };
        this.getDevopsPipelineList(project_id);
        this.getDevopsPipelineStartInfo();
        this.getDevopsPipelineDetail();
      }
    },
    methods: {
      // 项目列表
      getDevopsUserProjectList() {
        this.projectLoading = true;
        this.$store.dispatch('ticket/getDevopsUserProjectList', { ticket_id: this.basicInfomation.id }).then((res) => {
          this.projectList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.projectLoading = false;
          });
      },
      // 流水线列表
      getDevopsPipelineList(projectId) {
        this.pipelineLoading = true;
        this.$store.dispatch('ticket/getDevopsPipelineList', { project_id: projectId }).then((res) => {
          this.pipelineList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.pipelineLoading = false;
          });
      },
      // 流水线启动信息
      getDevopsPipelineStartInfo() {
        this.pipelineStartLoading = true;
        const { project_id, pipeline_id } = this.item.devopsContent;
        this.$store.dispatch('ticket/getDevopsPipelineStartInfo', {
          project_id,
          pipeline_id,
        }).then((res) => {
          this.pipelineStartInfo = res.data;
          this.pipelineVariableList = res.data.properties;
          const { variables } = this.item.devopsContent;
          res.data.properties.forEach((item) => {
            if (!Object.prototype.hasOwnProperty.call(variables, item.id)) {
              this.$set(variables, item.id, item.defaultValue || '');
            }
          });
          this.resetFormRules();
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.pipelineStartLoading = false;
          });
      },
      // 流水线详情
      getDevopsPipelineDetail() {
        this.pipelineDetailLoading = true;
        const { project_id, pipeline_id } = this.item.devopsContent;
        this.$store.dispatch('ticket/getDevopsPipelineDetail', {
          project_id,
          pipeline_id,
        }).then((res) => {
          this.pipelineStages = res.data.stages || [];
        })
          .finally(() => {
            this.pipelineDetailLoading = false;
          });
      },
      // 项目 change
      handleProjectChange(id) {
        this.pipelineList = [];
        this.pipelineStartInfo = {};
        this.pipelineVariableList = [];
        this.item.devopsContent.pipeline_id = '';
        this.item.devopsContent.variables = {};
        this.resetFormRules();
        this.getDevopsPipelineList(id);
      },
      // 流水线 change
      handlePipelineChange() {
        this.pipelineStartInfo = {};
        this.pipelineVariableList = [];
        this.item.devopsContent.variables = {};
        this.resetFormRules();
        this.getDevopsPipelineStartInfo();
        this.getDevopsPipelineDetail();
      },
      resetFormRules() {
        const requiredKeys = {};
        Object.keys(this.item.devopsContent.variables).forEach((key) => {
          const originVariable = this.pipelineVariableList.find(origin => origin.id === key);
          if (originVariable.required) {
            requiredKeys[key] = [newRequiredRule()];
          }
        });
        this.rules = {
          ...defaultRules,
          ...requiredKeys,
        };
      },
      validate() {
        this.$refs.devopsForm.validate();
        this.$refs.devopsVariable.validate();
        const { project_id: projectId, pipeline_id: pipelineId, variables } = this.item.devopsContent;
        const checkVariable = Object.keys(variables).every(key => !!variables[key]);
        if (!checkVariable) {
          this.showPipelineVariable = true;
        }
        return !!projectId && !!pipelineId && checkVariable;
      },
    },
  };
</script>
<style lang='scss' scoped>
.half-width-item {
    width: calc(50% - 4px);
    display: inline-block;
    &:nth-child(2n){
        margin-right: 8px;
    }
    /deep/ .bk-form-content .form-error-tip {
        position: absolute;
    }
}
.setion-title {
    margin-top: 30px;
    margin-bottom: 0;
    padding-bottom: 10px;
    color: #63656e;
    font-size: 14px;
    line-height: 20px;
    border-bottom: 1px solid #cacedb;
    font-weight: 700;
    &.border-none {
        border-bottom: none;
    }
    .setion-title-icon {
        display: inline-block;
        vertical-align: middle;
        font-size: 24px;
        cursor: pointer;
    }
}
</style>
