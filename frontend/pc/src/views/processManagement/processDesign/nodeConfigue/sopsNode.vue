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
  <div class="bk-basic-node" v-bkloading="{ isLoading: isLoading }">
    <basic-card :card-label="$t(`m.treeinfo['基本信息']`)">
      <bk-form data-test-id="service-form-sopsNode" :label-width="150" :model="basicsFormData" ref="basicsForm" :rules="rules" :ext-cls="'bk-form'" form-type="vertical">
        <bk-form-item
          data-test-id="sopsNode-select-nodeName"
          :label="$t(`m.treeinfo['节点名称：']`)"
          error-display-type="normal"
          :required="true"
          :property="'name'">
          <bk-input
            :ext-cls="'bk-form-width'"
            v-model="basicsFormData.name"
            maxlength="120">
          </bk-input>
        </bk-form-item>
        <desc-info v-model="basicsFormData.desc"></desc-info>
        <bk-form-item
          data-test-id="sopsNode-select-processType"
          error-display-type="normal"
          :label="$t(`m['流程类型：']`)"
          :required="true"
          :property="'processType'">
          <bk-select
            :ext-cls="'bk-form-width bk-form-display'"
            v-model="basicsFormData.processType"
            :placeholder="$t(`m['请选择流程类型']`)"
            searchable
            @selected="getTemplateList">
            <bk-option
              v-for="process in processOptions"
              :key="process.id"
              :id="process.id"
              :name="process.name">
            </bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item data-test-id="sopsNode-select-business" error-display-type="normal" :label="$t(`m['关联业务：']`)" :required="true" :property="'projectId'">
          <bk-select
            :ext-cls="'bk-form-width bk-form-display'"
            v-model="basicsFormData.projectId"
            :placeholder="$t(`m['请选择关联业务']`)"
            searchable
            :disabled="processDisable"
            @clear="onClearProcess"
            @selected="getProjectTemplateList">
            <bk-option
              v-for="project in projectList"
              :key="project.bk_biz_id"
              :id="project.bk_biz_id"
              :name="project.name">
              {{ project.name }}<span style="font-size: 12px; color: #ded6d7">&nbsp;&nbsp;{{ '(' + project.bk_biz_id + ')' }}</span>
            </bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item data-test-id="sopsNode-select-processTemplate" :label="$t(`m['流程模板：']`)" error-display-type="normal" :required="true" :property="'templateId'">
          <bk-select
            :ext-cls="'bk-form-width bk-form-display'"
            v-model="basicsFormData.templateId"
            :placeholder="$t(`m['请选择流程模板']`)"
            searchable
            :disabled="templateDisable"
            :loading="processesLoading"
            @clear="onClearTemplate"
            @selected="getTemplateDetail">
            <bk-option
              v-for="template in templateList"
              :key="template.id"
              :id="template.id"
              :name="template.name">
            </bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item :label="$t(`m['执行方案：']`)">
          <bk-select
            :ext-cls="'bk-form-width bk-form-display'"
            :disabled="planDisable"
            :placeholder="$t(`m['选择执行方案，默认选择全部任务节点']`)"
            v-model="basicsFormData.planId"
            multiple
            :clearable="true"
            :loading="planLoading"
            @selected="onplanSelect">
            <bk-option
              v-for="options in planList"
              :key="options.id"
              :id="options.id"
              :name="options.name">
            </bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item
          data-test-id="sopsnode-component-processor"
          :label="$t(`m.treeinfo['处理人：']`)"
          :required="true">
          <div @click="checkStatus.processors = false">
            <deal-person
              ref="processors"
              :show-overbook="true"
              :value="processorsInfo"
              :node-info="configur"
              :exclude-role-type-list="excludeProcessor">
            </deal-person>
          </div>
        </bk-form-item>
      </bk-form>
      <div class="sops-params-title">
        <p>{{ $t(`m.treeinfo['输入参数']`) }}:</p>
        <p>{{ $t(`m.treeinfo['调用该API需要传递的参数信息']`) }}</p>
      </div>
      <div class="bk-param" v-bkloading="{ isLoading: sopsFormLoading }">
        <sops-get-param
          v-if="constants.length !== 0"
          ref="getParam"
          :configur="configur"
          :param-table-data="paramTableData"
          :state-list="stateList"
          :fields="fieldList"
          :context="context"
          :init-form-date="initFormDate"
          :constants="constants"
          :hooked-var-list="hookedVarList"
          :constant-default-value="constantDefaultValue"
          :quote-vars="quoteVars"
          :flow-info="flowInfo"
          @onChangeHook="onChangeHook">
        </sops-get-param>
        <no-data v-else></no-data>
        <common-trigger-list :origin="'state'"
          :node-type="configur.type"
          :source-id="flowInfo.id"
          :sender="configur.id"
          :table="flowInfo.table">
        </common-trigger-list>
        <div class="mt20" style="font-size: 0">
          <bk-button :theme="'primary'"
            data-test-id="sopsNode-button-submit"
            :title="$t(`m.treeinfo['确定']`)"
            :loading="secondClick"
            class="mr10"
            @click="submit">
            {{$t(`m.treeinfo['确定']`)}}
          </bk-button>
          <bk-button :theme="'default'"
            data-test-id="sopsNode-button-close"
            :title="$t(`m.treeinfo['取消']`)"
            class="mr10"
            @click="closeNode">
            {{$t(`m.treeinfo['取消']`)}}
          </bk-button>
        </div>
      </div>
    </basic-card>
    <!-- <basic-card>
        </basic-card> -->
  </div>
</template>
<script>
  import descInfo from './components/descInfo.vue';
  import dealPerson from './components/dealPerson.vue';
  import NoData from '../../../../components/common/NoData.vue';
  import sopsGetParam from './components/sopsGetParam.vue';
  import commonTriggerList from '../../taskTemplate/components/commonTriggerList';
  import BasicCard from '@/components/common/layout/BasicCard.vue';
  import { errorHandler } from '../../../../utils/errorHandler';
  import { deepClone } from '@/utils/util.js';

  export default {
    name: 'sopsDevopsTask',
    components: {
      BasicCard,
      sopsGetParam,
      commonTriggerList,
      NoData,
      dealPerson,
      descInfo,
    },
    props: {
      // 流程信息
      flowInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      // 节点信息
      configur: {
        type: Object,
        default() {
          return {};
        },
      },
      state: {
        type: [String, Number],
        default() {
          return '';
        },
      },
    },
    data() {
      return {
        secondClick: false,
        quoteVars: [],
        hookedVarList: {},
        constantDefaultValue: {},
        basicsFormData: {
          name: '',
          desc: '',
          templateId: '',
          projectId: '',
          planId: [],
          processType: '',
          processors: [],
        },
        processOptions: [
          {
            id: 'business',
            name: '项目流程',
          },
          {
            id: 'common',
            name: '公共流程',
          },
        ],
        isLoading: false,
        excludeTaskNodesId: [],
        projectList: [],
        templateList: [],
        paramTableData: [],
        stateList: [],
        fieldList: [],
        constants: [],
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
        sopsFormLoading: false,
        processesLoading: false,
        planLoading: false,
        planList: [],
        optionalNodeIdList: [],
        templateDisable: false,
        planDisable: false,
        processDisable: false,
        renderFormValidate: false,
        biz: [
          {
            name: this.$t('m.treeinfo["业务"]'),
            custom_type: '',
            source_type: 'custom',
            value: '--',
            key: 1,
          },
        ],
        rules: {
          name: [
            {
              required: true,
              message: '必填项',
              trigger: 'blur',
            },
            {
              max: 50,
              message: '不能多于50个字符',
              trigger: 'blur',
            },
          ],
          processType: [
            {
              required: true,
              message: '必填项',
              trigger: 'blur',
            },
          ],
          projectId: [
            {
              required: true,
              message: '必填项',
              trigger: 'blur',
            },
          ],
          templateId: [
            {
              required: true,
              message: '必填项',
              trigger: 'blur',
            },
          ],
        },
        checkStatus: {
          delivers: false,
          processors: false,
        },
        excludeProcessor: [],
        processorsInfo: {
          type: '',
          value: '',
        },
        initFormDate: {},
      };
    },
    computed: {
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
    },
    created() {

    },
    mounted() {
      this.initData();
    },
    methods: {
      async initData() {
        this.isLoading = true;
        this.getRelatedFields();
        const userProjectList = await this.$store.dispatch('apiRemote/get_user_project_list');
        if (userProjectList) this.projectList = userProjectList.data;
        if (Object.keys(this.configur.extras).length !== 0) {
          this.basicsFormData.name = this.configur.name;
          this.basicsFormData.desc = this.configur.desc;
          // 流程类型
          this.basicsFormData.processType = this.configur.extras.sops_info.template_source;
          // 跳过执行任务ID
          this.excludeTaskNodesId = this.configur.extras.sops_info.exclude_task_nodes_id || [];
          // 项目ID
          this.basicsFormData.projectId = this.configur.extras.sops_info.bk_biz_id.value;
          if (this.basicsFormData.processType === 'common') {
            await this.getTemplateList(this.basicsFormData.processType);
          } else {
            await this.getProjectTemplateList(this.basicsFormData.projectId);
          }
          await this.getTemplateDetail(this.configur.extras.sops_info.template_id);
          this.basicsFormData.templateId = this.configur.extras.sops_info.template_id;
          this.processorsInfo = {
            type: this.configur.processors_type,
            value: this.configur.processors,
          };
        }
        this.getExcludeRoleTypeList();
        this.isLoading = false;
      },
      // 获取common流程类型
      async getTemplateList(key) {
        const isCommonProcess = key === 'common';
        const params = isCommonProcess ? {} : { bk_biz_id: this.basicsFormData.projectId };
        if (!isCommonProcess) this.basicsFormData.projectId = '';
        this.basicsFormData.templateId = '';
        this.basicsFormData.planId = [];
        this.templateDisable = !isCommonProcess;
        this.planDisable = !isCommonProcess;
        if (isCommonProcess) {
          this.processesLoading = true;
          // 获取流程模板
          await this.$store.dispatch('getTemplateList', params).then((res) => {
            this.templateList = res.data;
          })
            .catch(res => {
              errorHandler(res, this);
            })
            .finally(() => {
              this.processesLoading = false;
            });
        }
      },
      // 获取项目模板列表
      async getProjectTemplateList(id) {
        const params = {
          bk_biz_id: id,
        };
        if (this.basicsFormData.processType !== 'common') {
          this.processesLoading = true;
          this.basicsFormData.templateId = '';
          const res = await this.$store.dispatch('getTemplateList', params);
          if (res.result) {
            this.templateList = res.data;
            this.templateDisable = false;
            this.planDisable = false;
            this.processesLoading = false;
          }
        }
      },
      // 获取标准运维模板
      async getTemplateDetail(id) {
        const params = {
          bk_biz_id: this.basicsFormData.processType === 'common' ? '' : this.basicsFormData.projectId,
          template_id: id,
        };
        const templateInfo = this.templateList.find(item => item.id === id);
        if (templateInfo !== undefined) {
          this.context.project.bk_biz_id = templateInfo.bk_biz_id;
          this.context.project.id = this.template;
        }
        this.constants = [];
        this.hookedVarList = {};
        this.sopsFormLoading = true;
        this.basicsFormData.planId = [];
        await this.$store.dispatch('getTemplateDetail', params).then(res => {
          this.processingVariables(res.data.constants);
          this.optionalNodeIdList = res.data.all_ids || [];
          this.getTempaltePlanList(id);
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.sopsFormLoading = false;
          });
      },
      // 获取模板任务列表
      getTempaltePlanList(id) {
        const template = this.templateList.find(template => template.id === id);
        this.planList = [];
        const params = {
          bk_biz_id: template.bk_biz_id,
          template_id: template.id,
        };
        this.planLoading = true;
        this.$store.dispatch('getTemplatePlanList', params).then(res => {
          this.planList = res.data;
          if (this.excludeTaskNodesId.length !== 0) {
            res.data.forEach(item => {
              if (item.data) {
                const ids = this.optionalNodeIdList.filter(nodeId => !JSON.parse(item.data).includes(nodeId));
                const result = ids.filter(ite => !this.excludeTaskNodesId.includes(ite));
                if (result.length === 0 && this.excludeTaskNodesId.length === ids.length) {
                  this.basicsFormData.planId.push(item.id);
                }
              }
            });
          }
          this.onplanSelect(this.basicsFormData.planId);
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.planLoading = false;
          });
      },
      async onplanSelect(ids) {
        const planList = [];
        if (ids.length > 0) {
          ids.forEach(item => {
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
          this.excludeTaskNodesId = this.optionalNodeIdList.filter(nodeId => !planList.includes(nodeId));
        } else {
          this.excludeTaskNodesId = [];
        }
        const template = this.templateList.find(item => item.id === this.basicsFormData.templateId);
        try {
          this.sopsFormLoading = true;
          const isCommon = this.basicsFormData.processType === 'common';
          const constants = [];
          if (!isCommon) {
            const res = await this.$store.dispatch('taskFlow/getSopsPreview', {
              bk_biz_id: template.bk_biz_id,
              template_id: template.id,
              exclude_task_nodes_id: this.excludeTaskNodesId,
            });
            this.initFormDate = deepClone(res.data.pipeline_tree.constants);
            for (const key in res.data.pipeline_tree.constants) {
              if (res.data.pipeline_tree.constants[key].show_type === 'show') {
                constants.push(res.data.pipeline_tree.constants[key]);
              }
            }
          } else {
            constants.push([]);
          }
          this.processingVariables(constants);
        } catch (e) {
          console.error(e);
        } finally {
          this.sopsFormLoading = false;
        }
      },
      onChangeHook(key, value) {
        this.hookedVarList[key] = value;
        const cur = this.constants.find(item => item.key === key);
        const init = this.initFormDate[key];
        this.$set(cur, 'value', init.value);
      },
      processingVariables(vars) {
        const constants = vars;
        constants.sort((a, b) => a.index - b.index);
        // 设置每个变量的hook
        constants.map(item => {
          this.$set(this.hookedVarList, item.key, false);
        });
        if (Object.prototype.hasOwnProperty.call(this.configur.extras, 'sops_info')) {
          constants.forEach(item => {
            const curConstant = this.configur.extras.sops_info.constants.find(ite => ite.key === item.key);
            if (!curConstant) return;
            this.constantDefaultValue[item.key] = deepClone(curConstant.value);
            if (curConstant.is_quoted) {
              this.$set(this.hookedVarList, item.key, true);
              item.value = `\${${curConstant.value}}`;
            } else {
              item.value = curConstant.value;
            }
          });
        }
        this.constants = constants;
      },
      async getRelatedFields() {
        const params = {
          workflow: this.flowInfo.id,
          state: this.configur.id,
          field: '',
        };
        await this.$store.dispatch('apiRemote/get_related_fields', params).then(res => {
          this.stateList = res.data;
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
          });
      },
      // 计算处理人类型需要排除的类型
      getExcludeRoleTypeList() {
        // 不显示的人员类型
        let excludeProcessor = [];
        // 内置节点
        if (this.configur.is_builtin) {
          excludeProcessor = ['BY_ASSIGNOR', 'STARTER', 'VARIABLE'];
        } else {
          excludeProcessor = ['OPEN'];
        }
        // 是否使用权限中心角色
        if (!this.flowInfo.is_iam_used) {
          // excludeProcessor.push('IAM')
        }
        // 处理场景如果不是'DISTRIBUTE_THEN_PROCESS' || 'DISTRIBUTE_THEN_CLAIM'，则去掉派单人指定
        if (this.configur.distribute_type !== 'DISTRIBUTE_THEN_PROCESS' && this.configur.distribute_type !== 'DISTRIBUTE_THEN_CLAIM') {
          excludeProcessor.push('BY_ASSIGNOR');
        }
        if (!this.flowInfo.is_biz_needed) {
          excludeProcessor.push('CMDB');
        }
        this.excludeProcessor = [...['EMPTY', 'API'], ...excludeProcessor];
      },
      onClearProcess() {
        if (this.basicsFormData.processType !== 'common') {
          this.templateDisable = true;
          this.planDisable = true;
          this.constants = [];
        }
        this.templateList = [];
        this.basicsFormData.templateId = '';
        this.planList = [];
      },
      onClearTemplate() {
        this.basicsFormData.planId = [];
        this.basicsFormData.templateId = '';
        this.constants = [];
        this.planList = [];
      },
      closeNode() {
        this.$parent.closeConfigur();
      },
      submit() {
        // 处理人为空校验
        if (this.$refs.processors && !this.$refs.processors.verifyValue()) {
          this.checkStatus.processors = true;
        }
        if (this.$refs.getParam) {
          this.renderFormValidate = this.$refs.getParam.getRenderFormValidate();
        } else {
          this.renderFormValidate = true;
        }
        if (this.secondClick) {
          return;
        }
        this.$refs.basicsForm.validate().then(() => {
          if (this.renderFormValidate && this.$refs.processors.verifyValue()) {
            this.secondClick = true;
            const formData = [];
            const curbiz = this.projectList.find(item => item.bk_biz_id === this.basicsFormData.projectId);
            const biz = {
              name: curbiz ? curbiz.name : this.$t('m.treeinfo["业务"]'),
              value: curbiz ? curbiz.bk_biz_id : this.basicsFormData.projectId,
              key: 1,
              value_type: 'custom',
            };
            this.constants.map(item => {
              // renderForm的formData与constant匹配的key
              const formKey = Object.keys(this.$refs.getParam.formData).filter(key => key === item.key);
              const { name, key } = item;
              const vt = this.hookedVarList[formKey] ? 'variable' : 'custom';
              if (item.show_type === 'show') {
                const formTeamlate = {
                  value: this.hookedVarList[formKey] ? this.$refs.getParam.formData[formKey].slice(2, this.$refs.getParam.formData[formKey].length - 1) : this.$refs.getParam.formData[formKey],
                  name,
                  key: key || 1,
                  value_type: vt,
                  type: item.custom_type,
                  is_quoted: this.hookedVarList[formKey],
                };
                formData.push(formTeamlate);
              }
            });
            const { value: processors, type: processors_type } = this.$refs.processors.getValue();
            const params = {
              extras: {
                sops_info: {
                  bk_biz_id: biz,
                  template_id: this.basicsFormData.templateId,
                  constants: formData,
                  exclude_task_nodes_id: this.excludeTaskNodesId,
                  template_source: this.basicsFormData.processType,
                },
              },
              processors: processors || '',
              processors_type,
              is_draft: false,
              is_terminable: false,
              name: this.basicsFormData.name,
              desc: this.basicsFormData.desc || undefined,
              type: 'TASK-SOPS',
              workflow: this.configur.workflow,
            };
            const stateId = this.configur.id;
            this.$store.dispatch('cdeploy/putSopsInfo', { params, stateId }).then(() => {
              this.$bkMessage({
                message: this.$t('m.treeinfo["保存成功"]'),
                theme: 'success',
              });
              this.$parent.closeConfigur();
            }, (res) => {
              errorHandler(res, this);
            })
              .finally(() => {
                this.secondClick = false;
              });
          }
        });
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../../scss/mixins/scroller.scss';
    .bk-basic-node {
        padding: 30px 40px;
        height: 100%;
        background-color: #FAFBFD;
        overflow: auto;
        @include scroller;
        /deep/ .common-section-card-label {
            display: none;
        }
        /deep/ .common-section-card-body {
            width: 100%;
            padding: 20px;
        }
        /deep/ .bk-form-width {
            width: 448px;
        }
        .sops-params-title {
            margin-top: 20px;
            font-size: 14px;
            p:nth-child(1) {
                color: #63656e;
                margin-bottom: 4px;
            }
            p:nth-child(2) {
                font-size: 12px;
                color: #929397;
            }
        }
    }
    .bk-basic-info {
        padding-bottom: 20px;
        border-bottom: 1px solid #E9EDF1;
        margin-bottom: 20px;
    }
    .bk-form-width {
        width: 448px;
    }
    .bk-form-display {
        margin-right: 10px;
    }
</style>
