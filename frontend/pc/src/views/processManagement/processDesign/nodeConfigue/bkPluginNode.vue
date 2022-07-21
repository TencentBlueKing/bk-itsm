<template>
  <div class="bk-basic-node" v-bkloading="{ isLoading: isLoading }">
    <basic-card>
      <bk-form ref="basicInfo" :model="basicInfo" :label-width="150" :rules="basicInfoRules" :ext-cls="'bk-form'" form-type="vertical">
        <bk-form-item
          data-test-id="devops-input-name"
          :label="$t(`m.treeinfo['节点名称：']`)"
          :required="true"
          error-display-type="normal"
          :ext-cls="'bk-form-width bk-form-display'"
          :property="'nodeName'">
          <bk-input :clearable="true" v-model="basicInfo.nodeName"></bk-input>
        </bk-form-item>
        <desc-info v-model="basicInfo.desc"></desc-info>
        <bk-form-item
          data-test-id="devops-select-project"
          :label="$t(`m['第三方插件']`)"
          :required="true"
          error-display-type="normal"
          :ext-cls="'bk-form-width bk-form-display'"
          :property="'plugin'">
          <bk-select
            v-model="basicInfo.plugin"
            searchable
            :disabled="false"
            @selected="onSelectplugin">
            <bk-option v-for="plugin in pluginList"
              :key="plugin.code"
              :id="plugin.code"
              :name="plugin.name">
            </bk-option>
          </bk-select>
          <div class="tip" v-if="pluginTip">
            <i class="bk-itsm-icon icon-itsm-icon-four-one"></i>
            <p v-text="pluginTip"></p>
          </div>
        </bk-form-item>
        <bk-form-item
          data-test-id="devops-select-pipeline"
          :label="$t(`m['版本']`)"
          :required="true"
          :property="'version'"
          error-display-type="normal"
          :ext-cls="'bk-form-width bk-form-display'">
          <bk-select
            searchable
            v-model="basicInfo.version"
            :loading="versionListLoading"
            :disabled="versionListDisabled"
            @selected="getFormInfo">
            <bk-option v-for="version in versionList"
              :key="version"
              :id="version"
              :name="version">
            </bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item
          data-test-id="devops-component-processor"
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
      <div class="bk-params-title">
        <p>{{ $t(`m.treeinfo['输入参数']`) }}:</p>
        <p>{{ $t(`m['执行蓝鲸插件需要填写的参数信息']`) }}</p>
      </div>
      <div v-bkloading="{ isLoading: isHasSchma }">
        <template v-if="Object.keys(schema || {}).length !== 0">
          <BkRenderForm
            class="bk-form-plugin"
            v-model="formData"
            ref="bkForm"
            :schema="schema"
            :layout="layout"
            :rules="rules"
            :form-type="formType"
            :context="{
              ...context,
              rules: {}
            }"
            :http-adapter="{
              responseParse: {
                labelKey: 'name',
                valueKey: 'id'
              }
            }"
            :key="formKey">
            <template #suffix="{ path, schema: schemaField }">
              <bk-checkbox
                ext-cls="select-check"
                v-model="hookVarList[path]"
                @change="onChangeChecked($event, path ,schemaField)">
              </bk-checkbox>
              <bk-select :disabled="!hookVarList[path]" style="width: 200px;"
                :value="( hookSelectList[path] || '' ).replace(/^\{\{/, '').replace(/\}\}/, '')"
                ext-cls="select-custom"
                searchable
                @selected="changeConstant($event, path ,schemaField)">
                <bk-option v-for="option in stateList"
                  :key="option.key"
                  :id="option.key"
                  :name="option.name">
                </bk-option>
              </bk-select>
            </template>
          </BkRenderForm>
          <p v-if="errorList.length !== 0" class="errorTip"><i class="bk-itsm-icon icon-itsm-icon-square-one"></i>{{ $t(`m['字段']`) + errorList.toString() + $t(`m['是必填项！']`) }}</p>
        </template>
        <no-data v-else></no-data>
      </div>
      <div class="bk-params-title">
        <p>{{ $t(`m['输出参数']`) }}:</p>
        <p>{{ $t(`m['蓝鲸插件执行之后的输出，可以通过勾选的方式作为引用变量在后面的节点使用']`) }}</p>
      </div>
      <div style="padding: 20px">
        <bk-table
          v-bkloading="{ isLoading: isHasSchma }"
          :data="outputsData">
          <bk-table-column :label="$t(`m['名称']`)" prop="title"></bk-table-column>
          <bk-table-column label="key" prop="key"></bk-table-column>
          <bk-table-column :label="$t(`m['设置为全局变量']`)">
            <template slot-scope="props">
              <bk-checkbox @change="onchangeOutputCheck($event, props)" v-model="outputsVarList[props.row.key]"></bk-checkbox>
            </template>
          </bk-table-column>
        </bk-table>
      </div>
      <common-trigger-list :origin="'state'"
        :node-type="configur.type"
        :source-id="flowInfo.id"
        :sender="configur.id"
        :table="flowInfo.table">
      </common-trigger-list>
      <div class="mt20" style="font-size: 0">
        <bk-button :theme="'primary'"
          data-test-id="devops-button-submit"
          :title="$t(`m.treeinfo['确定']`)"
          class="mr10"
          @click="submit">
          {{$t(`m.treeinfo['确定']`)}}
        </bk-button>
        <bk-button :theme="'default'"
          data-test-id="devops-button-close"
          :title="$t(`m.treeinfo['取消']`)"
          class="mr10"
          @click="closeNode">
          {{$t(`m.treeinfo['取消']`)}}
        </bk-button>
      </div>
    </basic-card>
  </div>
</template>
<script>
  import descInfo from './components/descInfo.vue';
  import createForm from '@blueking/bkui-form/dist/bkui-form-umd';
  import dealPerson from './components/dealPerson.vue';
  import commonTriggerList from '../../taskTemplate/components/commonTriggerList';
  import BasicCard from '@/components/common/layout/BasicCard.vue';
  import NoData from '@/components/common/NoData.vue';
  import i18n from '@/i18n/index.js';
  function newRequiredRule() {
    return {
      required: true,
      message: i18n.t('m.treeinfo["字段必填"]'),
      trigger: 'blur',
    };
  }
  const BkRenderForm = createForm();
  export default {
    name: 'devops',
    components: {
      BasicCard,
      commonTriggerList,
      NoData,
      dealPerson,
      BkRenderForm,
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
        isLoading: false,
        basicInfo: {
          nodeName: '',
          desc: '',
          plugin: '',
          version: '',
          processors: [],
        },
        pluginList: [],
        versionList: [],
        hookVarList: {},
        hookSelectList: {},
        versionListLoading: false,
        versionListDisabled: true,
        formLoading: false,
        basicInfoRules: {
          nodeName: [newRequiredRule()],
          plugin: [newRequiredRule()],
          version: [newRequiredRule()],

        },
        checkStatus: {
          delivers: false,
          processors: false,
        },
        excludeProcessor: ['EMPTY', 'OPEN'],
        processorsInfo: {
          type: '',
          value: '',
        },
        formKey: '',
        hookedVarList: {},
        initForm: {},
        stateList: [
        ], // 引用变量
        // 这是个测试的schema
        schema: {},
        layout: [],
        outputsData: [],
        outputsVarList: {},
        primarySchema: {},
        formData: {},
        formType: 'vertical',
        rules: {
          maxLength20: { validator: '{{ $self.value.length < 20}}', message: this.$t('m[\'长度必须大于 20\']') },
          number: { validator: '/!^[0-9]*$/', message: this.$t('m[\'必须是数字\']') },
          required: { message: this.$t('m[\'值不能为空\']'), validator: '{{ $self.value !== ""}}' },
          reservedWord: { validator: '{{ !$self.value.includes("bk") }}', message: this.$t('m[\'不能使用保留字符\']') },
        },
        context: {
          bizId: 1,
          site_url: '/o/bk_sops/',
          projectId: this.$route.query.project_id,
          baseURL: '',
          pod_name: 'test_pod_name',
        },
        pluginTip: '',
        errorList: [],
      };
    },
    computed: {
      isHasSchma() {
        return Object.keys(this.schema).length === 0 && this.formLoading;
      },
    },
    watch: {
      basicInfo: {
        handler(val) {
          if (val.plugin === '') {
            val.version = '';
            this.pluginTip = '';
            this.versionList = [];
            this.schema = {};
            this.outputsData = [];
            this.formLoading = false;
            this.versionListDisabled = true;
          } else {
            this.versionListDisabled = false;
          }
          if (val.version === '') {
            this.schema = {};
            this.outputsData = [];
            this.formLoading = false;
          } else {
            this.formLoading = true;
          }
        },
        deep: true,
      },
    },
    mounted() {
      this.initData();
      this.getRelatedFields();
      // 初始变量下拉选择的状态
      // Object.keys(this.schema.properties).map(item => {
      //     this.$set(this.hookedVarList, item, false)
      // })
    },
    methods: {
      async initData() {
        this.isLoading = true;
        this.basicInfo.nodeName = this.configur.name;
        this.basicInfo.desc = this.configur.desc;
        this.processorsInfo = {
          type: this.configur.processors_type,
          value: this.configur.processors,
        };
        this.$store.dispatch('bkPlugin/getPluginList').then(res => {
          this.pluginList = res.data.plugins;
          this.getExcludeRoleTypeList();
        });
        if (Object.keys(this.configur.extras).length !== 0) {
          this.basicInfo.plugin = this.configur.extras.bk_plugin_info.plugin_code;
          this.onSelectplugin(this.basicInfo.plugin);
          this.basicInfo.version = this.configur.extras.bk_plugin_info.version;
          this.initForm = true;
          this.getFormInfo(this.basicInfo.version);
          this.formData = this.configur.extras.bk_plugin_info.inputs;
          this.primarySchema = this.configur.extras.bk_plugin_info.inputs;
          this.schema = this.primarySchema;
          const outputs_var_list = this.configur.extras.outputs_var_list || {};
          const input_var_list = this.configur.extras.input_var_list || {};
          Object.keys(outputs_var_list).map(item => {
            this.$set(this.outputsVarList, item, outputs_var_list[item]);
          });
          Object.keys(input_var_list).map(item => {
            this.$set(this.hookVarList, item, input_var_list[item]);
            if (input_var_list[item]) {
              this.hookSelectList[item] = this.formData[item];
            }
          });
        }
        this.isLoading = false;
      },
      async getRelatedFields() {
        const params = {
          workflow: this.flowInfo.id,
          state: this.configur.id,
          field: '',
        };
        this.$store.dispatch('apiRemote/get_related_fields', params).then(res => {
          this.stateList = res.data;
        });
      },
      onChangeChecked(value, path, schema) {
        const data = Object.assign({}, this.formData);
        if (value) {
          if (schema.type === 'integer') {
            schema.type = 'string';
          }
          Object.assign(schema, { 'ui:component': { name: 'bk-input', props: { disabled: true, value: data[path] } } });
        } else {
          Object.assign(schema, { 'ui:component': { name: 'bk-input', props: { disabled: false, value: data[path] } } });
        }
        if (!value) {
          this.hookSelectList[path] = '';
        }
        this.formKey = new Date().getTime();
      },
      changeConstant(value, path, schema) {
        if (schema.type === 'integer') {
          schema.type = 'string';
        }
        this.hookSelectList[path] = `{{${value}}}`;
        this.formData[path] = this.hookSelectList[path];
        Object.assign(schema, { 'ui:component': { name: 'bk-input', props: { disabled: true, value: this.hookSelectList[path] } } });
        this.formKey = new Date().getTime();
      },
      onchangeOutputCheck(value, props) {
        this.outputsVarList[props.row.key] = value;
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
        if (this.configur.distribute_type !== 'DISTRIBUTE_THEN_PROCESS' && this.configur.distribute_type !== 'DISTRIBUTE_THEN_CLAIM') {
          excludeProcessor.push('BY_ASSIGNOR');
        }
        if (!this.flowInfo.is_biz_needed) {
          excludeProcessor.push('CMDB');
        }
        this.excludeProcessor = [...['EMPTY', 'API'], ...excludeProcessor];
      },
      handleVarClick(item, path) {
        this.formData[path] = `{{${item.key}}}`;
        this.$set(this.hookedVarList, path, false);
        this.formKey = new Date().getTime();
      },
      onSelectplugin(value) {
        this.pluginTip = '';
        this.schema = {};
        this.formData = {};
        this.versionListLoading = true;
        this.basicInfo.version = '';
        this.formLoading = false;
        try {
          const params = { plugin_code: value };
          this.$store.dispatch('bkPlugin/getPluginMeta', params).then(res => {
            this.pluginTip = res.data.description;
            this.versionList = res.data.versions;
          });
        } catch (e) {
          console.log(e);
        } finally {
          this.versionListLoading = false;
        }
      },
      getFormInfo(value) {
        this.schema = {};
        this.formData = {};
        try {
          const params = { plugin_code: this.basicInfo.plugin, plugin_version: value };
          this.$store.dispatch('bkPlugin/getPluginDetail', params).then(res => {
            this.schema = res.data.inputs || {};
            Object.keys(this.schema.properties).map(item => {
              if (this.schema.properties[item].type === 'integer') {
                this.schema.properties[item].type = 'string';
              }
            });
            if (Object.keys(res.data.outputs.properties).length !== 0) {
              this.outputsData = Object.keys(res.data.outputs.properties).map(item => {
                const items = {
                  key: item,
                  title: res.data.outputs.properties[item].title,
                };
                return items;
              });
            } else {
              this.outputsData = [];
            }
            if (!this.initForm) {
              this.outputsVarList = {};
              this.hookSelectList = {};
              this.hookVarList = {};
            }
            this.initForm = false;
          });
        } catch (e) {
          console.log(e);
        }
      },
      closeNode() {
        this.$parent.closeConfigur();
      },
      submit() {
        this.$refs.basicInfo.validate().then(() => {
          this.errorList = [];
          const isRequired = this.schema.required || [];
          const state = Object.keys(this.$refs.bkForm.value).map(item => {
            if (isRequired.includes(item)) {
              if (this.$refs.bkForm.value[item] === '' || this.$refs.bkForm.value[item].length === 0) {
                if (!this.errorList.includes(item)) this.errorList.push(item);
                return false;
              }
              return true;
            }
            return true;
          });
          if (!state.every(item => item)) {
            return;
          }
          const { value: processors, type: processors_type } = this.$refs.processors.getValue();
          const bk_plugin_info = { plugin_code: this.basicInfo.plugin, version: this.basicInfo.version, inputs: this.formData, context: {} };
          const outputs = [];
          this.outputsData.forEach(item => {
            if (!this.outputsVarList[item.key]) {
              return;
            }
            if (this.outputsVarList[item.key]) {
              outputs.push({
                name: item.title,
                ref_path: `resp.outputs.${item.key}`,
                source: 'global',
                type: 'STRING',
              });
            }
          });
          if (this.$refs.processors && !this.$refs.processors.verifyValue()) {
            this.checkStatus.processors = true;
            return;
          }
          if (this.$refs.bkForm) {
            const valid = this.$refs.bkForm.validateForm();
            if (!valid) {
              return;
            }
          }
          const params = {
            name: this.basicInfo.nodeName,
            desc: this.basicInfo.desc || undefined,
            processors: processors || '',
            processors_type: processors_type || '',
            type: 'BK-PLUGIN',
            is_draft: false,
            extras: {
              bk_plugin_info,
              outputs_var_list: this.outputsVarList,
              input_var_list: this.hookVarList,
            },
            variables: { outputs },
            workflow: this.configur.workflow,
          };
          const stateId = this.configur.id;
          this.$store.dispatch('cdeploy/putWebHook', { params, stateId }).then(() => {
            this.$bkMessage({
              message: this.$t('m[\'保存成功\']'),
              theme: 'success',
            });
            this.$parent.closeConfigur();
          }, e => {
            console.log(e);
          })
            .finally(() => {
              this.secondClick = false;
            });
        });
      },
    },
  };
</script>

<style lang='scss' scoped>
@import '../../../../scss/mixins/scroller.scss';
    .bk-form {
        display: flex;
        flex-direction: column;
    }
    .bk-basic-node {
        padding: 30px 40px;
        height: 100%;
        background-color: #FAFBFD;
        overflow: unset;
        @include scroller;
        /deep/ .common-section-card-label {
            display: none;
        }
        /deep/ .common-section-card-body {
            padding: 20px;
        }
        /deep/ .bk-form-width {
            width: 448px;
        }
        .bk-params-title {
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
        .bk-form-plugin {
            padding: 20px;
            /deep/ .bk-schema-form-group {
                overflow: unset !important;
            }
            /deep/ .bk-form-content {
                display: flex;
                align-items: center;
                .bk-form-control {
                    width: 70%;
                }
                .select-check {
                    margin: 0 auto;
                }
                .select-custom {
                    width: 150px;
                }
            }
            .var-select {
                width: 200px;
                height: 230px;
                position: absolute;
                border-radius: 4px;
                background: #fff;
                font-size: 14px;
                border: 1px solid #c4c6cc;
                top: 35px;
                left: 71px;
                z-index: 2000;
                overflow-y: auto;
                @include scroller;
                ul {
                    padding: 5px;
                    li {
                        height: 30px;
                        cursor: pointer;
                        color: #75777f;
                        &:hover {
                            background-color: #e1ecff;
                            color: #3a84ff;
                        }
                    }
                }
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
        .tip {
            display: flex;
            height: 20px;
            align-items: center;
            font-size: 10px;
            color: #929397;
            p {
                margin-left: 5px;
            }
        }
    }
    .bk-form-display {
        float: left;
        margin-right: 10px;
    }
    .errorTip {
        color: red;
        font-size: 12px;
    }
</style>
