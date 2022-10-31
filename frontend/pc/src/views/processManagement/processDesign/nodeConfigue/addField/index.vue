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
  <div class="bk-add-field" v-bkloading="{ isLoading: isDataLoading }">
    <bk-form
      class="bk-add-field bk-form-vertical"
      :label-width="200"
      :form-type="formAlign"
      :model="formInfo"
      :rules="rules"
      ref="fieldForm">
      <template v-if="Object.keys(sospInfo).length">
        <bk-form-item
          :style="{ marginTop: formAlign === 'vertical' ? 0 : '20px' }"
          :label="$t(`m.treeinfo['前置节点']`)"
          :required="true"
          :property="'prevId'"
          :error-display-type="'normal'"
          :ext-cls="'bk-mt0-item'">
          <bk-select v-model="formInfo.prevId"
            searchable>
            <bk-option v-for="option in prevNodeList"
              :key="option.id"
              :id="option.id"
              :name="option.name">
            </bk-option>
          </bk-select>
        </bk-form-item>
      </template>
      <bk-form-item
        data-test-id="field-input-fieldName"
        :style="{ marginTop: formAlign === 'vertical' ? 0 : '20px' }"
        :label="$t(`m.treeinfo['字段名']`)"
        :required="true"
        :property="'name'"
        :error-display-type="'normal'"
        :ext-cls="'bk-halfline-item bk-halfline-margin'">
        <bk-input maxlength="120"
          v-model="formInfo.name"
          @change="fieldNameChange"
          :disabled="changeInfo.source === 'TABLE' && formInfo.key !== 'bk_biz_id'"
          :placeholder="$t(`m.treeinfo['请输入字段显示名']`)"
          @input="putKey">
        </bk-input>
      </bk-form-item>
      <bk-form-item
        :style="{ marginTop: formAlign === 'vertical' ? 0 : '20px' }"
        :label="$t(`m.treeinfo['唯一标识']`)"
        :required="true"
        :property="'key'"
        :error-display-type="'normal'"
        :ext-cls="'bk-halfline-item'">
        <bk-input
          v-model="formInfo.key"
          :placeholder="$t(`m.treeinfo['请输入唯一标识']`)"
          :disabled="typeof changeInfo.id === 'number' || changeInfo.is_builtin || changeInfo.source === 'TABLE'">
        </bk-input>
      </bk-form-item>
      <bk-form-item
        data-test-id="field-select-fieldType"
        :label="$t(`m.treeinfo['字段类型']`)"
        :required="true"
        :property="'type'"
        :error-display-type="'normal'"
        :ext-cls="'bk-halfline-item bk-halfline-margin bk-mt20-item'">
        <bk-select v-model="formInfo.type"
          :clearable="false"
          :disabled="(changeInfo.is_builtin || changeInfo.source === 'TABLE' || (changeInfo.meta && changeInfo.meta.code === 'APPROVE_RESULT')) && formInfo.key !== 'bk_biz_id'"
          searchable
          @selected="changeType">
          <bk-option v-for="option in fieldTypeList"
            :key="option.typeName"
            :id="option.typeName"
            :name="option.name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item
        :label="$t(`m.treeinfo['校验方式']`)"
        :required="true"
        :error-display-type="'normal'"
        :ext-cls="'bk-halfline-item bk-mt20-item'">
        <bk-select v-model="formInfo.regex"
          :clearable="false"
          :disabled="(changeInfo.is_builtin || changeInfo.source === 'TABLE' || (changeInfo.meta && changeInfo.meta.code === 'APPROVE_RESULT')) && formInfo.key !== 'bk_biz_id'"
          searchable
          @selected="changeRegex">
          <bk-option v-for="option in regexList"
            :key="option.typeName"
            :id="option.typeName"
            :name="option.name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <div class="bk-form-item bk-relate-conditions" style="width: 100%"
        v-if="formInfo.regex === 'ASSOCIATED_FIELD_VALIDATION' && !isEditPublic">
        <div class="bk-form-content" style="margin-left: 0">
          <p class="bk-form-p">{{$t(`m.newCommon["字段间关系"]`)}}</p>
          <bk-radio-group v-model="formInfo.regex_config.rule.type">
            <bk-radio :value="'and'" :ext-cls="'mr20'">{{$t(`m.treeinfo['且']`)}}</bk-radio>
            <bk-radio :value="'or'">{{$t(`m.treeinfo['或']`)}}</bk-radio>
          </bk-radio-group>
        </div>
        <div class="bk-between-form"
          v-for="(expression, index) in formInfo.regex_config.rule.expressions"
          :key="index">
          <p class="current-field">{{$t(`m.newCommon["当前字段"]`)}}</p>
          <bk-select style="width: 120px"
            :ext-cls="'field-valid-select'"
            v-model="expression.condition"
            :clearable="false">
            <bk-option v-for="option in betweenList"
              :key="option.id"
              :id="option.typeName"
              :name="option.name">
            </bk-option>
          </bk-select>
          <bk-select style="width: 210px"
            :ext-cls="'field-valid-select'"
            v-model="expression.key"
            :clearable="false"
            @change="onRegexFieldChange($event, expression)">
            <bk-option v-for="option in regexFieldList"
              :key="option.id"
              :id="option.key"
              :name="option.name">
            </bk-option>
          </bk-select>
          <div class="bk-between-operate">
            <i class="bk-itsm-icon icon-flow-add" @click="addExpression()"></i>
            <i class="bk-itsm-icon icon-flow-reduce"
              :class="{ 'bk-no-delete': formInfo.regex_config.rule.expressions.length === 1 }"
              @click="deleteExpression(index)"></i>
          </div>
        </div>
      </div>
      <template v-if="formInfo.regex === 'CUSTOM'">
        <bk-form-item
          :label="$t(`m.treeinfo['正则规则']`)"
          :required="true"
          :property="'key'"
          :error-display-type="'normal'"
          :ext-cls="'bk-halfline-item bk-halfline-margin bk-mt20-item'">
          <bk-input
            v-model="formInfo.customRegex"
            :disabled="(changeInfo.is_builtin || changeInfo.source === 'TABLE') && formInfo.key !== 'bk_biz_id'"
            :placeholder="$t(`m.treeinfo['请输入正则规则']`)">
          </bk-input>
        </bk-form-item>
      </template>
    </bk-form>
    <bk-form
      :label-width="200"
      class="bk-form-vertical"
      :form-type="formAlign"
      :model="formInfo"
      ref="dataForm">
      <template v-if="showType.sourceList.some(type => type === formInfo.type)">
        <bk-form-item
          :label="$t(`m.treeinfo['数据源']`)"
          :required="true"
          :ext-cls="'bk-mt20-item'">
          <data-source ref="dataSource"
            :form-info="formInfo"
            :prc-data="prcData"
            :change-info="assignValue"
            :api-info="apiInfo.api_info"
            :dictionary-data="dictionaryData"
            @changeApiInfo="changeApiInfo"
            @getRpcData="getRpcData">
          </data-source>
        </bk-form-item>
        <template v-if="(formInfo.source_type !== 'DATADICT' && formInfo.source_type !== 'RPC') || (formInfo.source_type === 'RPC' && prcTable.length)">
          <template v-for="(node, nodeIndex) in globalChoise.source_type">
            <bk-form-item
              v-if="node.typeName === formInfo.source_type"
              :key="nodeIndex"
              :label="node.name"
              :desc="node.desc"
              :required="true"
              :ext-cls="'bk-mt20-item'">
              <bk-button v-if="isShowDataSourcebtn" :disabled="isDisabled" class="configuration-data-source" theme="primary" :title="$t(`m['配置数据源']`)" :outline="true" @click="openDataSource">{{ $t(`m['配置数据源']`)}}</bk-button>
              <bk-dialog
                v-model="isShowDataSource"
                width="960"
                :title="formInfo.source_type === 'API' ? $t(`m['配置接口数据']`) : $t(`m['配置自定义数据']`)"
                theme="primary"
                :auto-close="false"
                :mask-close="false"
                @confirm="validateContent">
                <data-content ref="dataContent"
                  :form-info="formInfo"
                  :workflow="workflow"
                  :state="state"
                  :change-info="assignValue"
                  :api-detail="apiDetail"
                  :api-info="apiInfo.api_info"
                  :kv-relation="apiInfo.kv_relation"
                  :prc-table="prcTable"
                  :field-info="fieldInfo">
                </data-content>
              </bk-dialog>
            </bk-form-item>
          </template>
        </template>
      </template>
      <template v-if="formInfo.type === 'CUSTOMTABLE'">
        <bk-form-item
          data-test-id="field_form_custom"
          :label="$t(`m.treeinfo['自定义数据']`)"
          :required="true"
          :ext-cls="'bk-mt20-item'">
          <div @click="checkStatus.customTableStatus = false">
            <custom-table-data :custom-table-info="customTableInfo"></custom-table-data>
            <p class="bk-field-error" v-if="checkStatus.customTableStatus">{{ $t('m.treeinfo["请填写正确格式的自定义数据"]') }}</p>
          </div>
          <div class="bk-form-disabled" v-if="(changeInfo.is_builtin || changeInfo.source === 'TABLE' || (changeInfo.meta && changeInfo.meta.code === 'APPROVE_RESULT')) && formInfo.key !== 'bk_biz_id'"></div>
        </bk-form-item>
      </template>
      <template v-if="formInfo.type === 'FILE'">
        <bk-form-item :ext-cls="'bk-input-position bk-mt20-item'"
          :label="$t(`m.treeinfo['上传附件模板']`)">
          <bk-button :theme="'default'" :title="$t(`m.treeinfo['点击上传']`)">
            {{$t(`m.treeinfo['点击上传']`)}}
          </bk-button>
          <input type="file" :value="fileVal" class="bk-input-file" @change="handleFile">
          <ul class="bk-file-list">
            <li v-for="(item, index) in fileList" :key="index">
              <span class="bk-file-success">
                <i class="bk-icon icon-check-1"></i>
              </span>
              <span>{{item.name}}</span>
              <span class="bk-file-delete" @click="deleteFile(item, index)">×</span>
            </li>
          </ul>
          <div class="bk-form-disabled" v-if="(changeInfo.is_builtin || changeInfo.source === 'TABLE') && formInfo.key !== 'bk_biz_id'"></div>
        </bk-form-item>
      </template>
      <template v-if="showType.belongDefaultList.some(belong => formInfo.type === belong)">
        <bk-form-item
          :label="$t(`m.treeinfo['默认值']`)"
          :ext-cls="'bk-mt20-item'">
          <default-value
            :form-info="formInfo"
            :field-info="fieldInfo"
            :dictionary-data="dictionaryData"
            :change-info="changeInfo"
            :api-info="apiInfo"
            :check-status="checkStatus"
            :label="$t(`m.treeinfo['默认值']`)">
          </default-value>
        </bk-form-item>
      </template>
      <!-- 公共字段不需要填写布局和填写规则 -->
      <template v-if="!(addOrigin.isOther && addOrigin.addOriginInfo.type === 'publicField')">
        <bk-form-item :ext-cls="'bk-halfline-item bk-halfline-margin bk-mt20-item'"
          :label="$t(`m.treeinfo['布局要求']`)"
          :required="true">
          <bk-radio-group v-model="formInfo.layout">
            <template v-for="(layout, layoutIndex) in globalChoise.layout_type">
              <bk-radio :ext-cls="'mr20'"
                :key="layoutIndex"
                :value="layout.typeName"
                :disabled="showType.layoutList.some(node => node === formInfo.type)">
                {{layout.name}}
              </bk-radio>
            </template>
          </bk-radio-group>
        </bk-form-item>
        <bk-form-item :ext-cls="'bk-halfline-item bk-mt20-item'"
          :label="$t(`m.treeinfo['字段必填']`)"
          :required="true">
          <bk-radio-group v-model="formInfo.validate">
            <template v-for="(validate, validateIndex) in globalChoise.validate_type">
              <bk-radio :ext-cls="'mr20'"
                :key="validateIndex"
                :value="validate.typeName"
                :disabled="changeInfo.key === 'title' || changeInfo.is_builtin || formInfo.key === 'bk_biz_id'">
                {{validate.name}}
              </bk-radio>
            </template>
          </bk-radio-group>
        </bk-form-item>
      </template>
      <bk-form-item :ext-cls="'bk-tanble-height bk-mt20-item'"
        :label="$t(`m.treeinfo['填写说明']`)">
        <!-- 禁用：formInfo.isModule && formInfo.key!== 'bk_biz_id' -->
        <textarea
          class="bk-form-textarea bk-textarea-tanble bk-halfline-item bk-halfline-margin field-input-tips"
          :placeholder="$t(`m.treeinfo['请输入字段填写说明']`)"
          v-model.trim="formInfo.desc">
                </textarea>
        <p class="field-tips-checkbox" style="margin-left: 335px;">
          <bk-checkbox
            :true-value="trueStatus"
            :false-value="falseStatus"
            v-model="formInfo.is_tips">
            {{ $t('m.treeinfo["添加额外提示说明"]') }}
          </bk-checkbox>
        </p>
      </bk-form-item>
      <template v-if="formInfo.is_tips">
        <bk-form-item
          :label="$t(`m.treeinfo['字段释疑']`)"
          :required="true"
          :ext-cls="'bk-mt20-item'">
          <!-- 禁用：formInfo.isModule && formInfo.key!== 'bk_biz_id' -->
          <textarea
            class="bk-form-textarea bk-textarea-tanble bk-halfline-item bk-halfline-margin"
            :placeholder="$t(`m.treeinfo['请输入，用于鼠标经过提示']`)"
            v-model.trim="formInfo.tips">
                    </textarea>
          <p class="bk-label-tips">
            <span v-bk-tooltips.top="(formInfo.tips || $t(`m.treeinfo['字段释疑填填看哦']`))">
              {{ $t('m.treeinfo["效果预览"]') }}
            </span>
          </p>
          <!-- <div class="bk-form-disabled" v-if="changeInfo.source === 'TABLE' || changeInfo.is_builtin"></div> -->
        </bk-form-item>
      </template>
      <!-- 公共字段不需要填写条件隐藏' -->
      <template v-if="!(addOrigin.isOther && addOrigin.addOriginInfo.type === 'publicField') && (changeInfo.meta && changeInfo.meta.code !== 'APPROVE_RESULT')">
        <bk-form-item
          :label="$t(`m.treeinfo['是否设置字段隐藏条件']`)"
          :ext-cls="'bk-mt20-item'">
          <bk-switcher v-model="formInfo.show_type"
            size="small"
            :disabled="changeInfo.key === 'title'">
          </bk-switcher>
        </bk-form-item>
        <template v-if="formInfo.show_type">
          <bk-form-item
            :label="$t(`m.treeinfo['隐藏条件']`)"
            :desc="$t(`m.treeinfo['字段默认为显示。当满足以下配置条件时，该字段将会被隐藏。']`)"
            :ext-cls="'bk-mt20-item'">
            <hidden-conditions
              ref="hiddenConditions"
              :template-info="templateInfo"
              :template-stage="templateStage"
              :add-origin="addOrigin"
              :workflow="workflow"
              :state="state"
              :form-info="formInfo">
            </hidden-conditions>
          </bk-form-item>
        </template>
      </template>
    </bk-form>
    <div class="operate-btns mt20">
      <bk-button :theme="'primary'"
        data-test-id="field_button_submit"
        :title="$t(`m.treeinfo['提交']`)"
        :loading="secondClick"
        class="mr10"
        @click="checkInfo">
        {{$t(`m.treeinfo['提交']`)}}
      </bk-button>
      <bk-button :theme="'default'"
        data-test-id="field_button_cancel"
        :title="$t(`m.treeinfo['取消']`)"
        :disabled="secondClick"
        class="mr10"
        @click="onCancelClick">
        {{$t(`m.treeinfo['取消']`)}}
      </bk-button>
    </div>
  </div>
</template>
<script>
  import commonMix from '../../../../commonMix/common.js';
  import dataSource from './dataSource.vue';
  import dataContent from './dataContent.vue';
  import customTableData from './customTableData.vue';
  import defaultValue from './defaultValue.vue';
  import hiddenConditions from './hiddenConditions.vue';
  import pinyin from 'pinyin';
  import { CUSTOM_FORM_DEFAULT_VALUE } from '../../../../../constants/field';
  import { errorHandler } from '../../../../../utils/errorHandler.js';
    
  export default {
    name: 'addField',
    components: {
      dataSource,
      dataContent,
      customTableData,
      defaultValue,
      hiddenConditions,
    },
    mixins: [commonMix],
    props: {
      formAlign: {
        type: String,
        default: 'vertical',
      },
      changeInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      workflow: {
        type: [String, Number],
        default() {
          return '';
        },
      },
      state: {
        type: [String, Number],
        default() {
          return '';
        },
      },
      // 标准运维变量
      sospInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      // 公共字段
      addOrigin: {
        type: Object,
        default() {
          return {
            isOther: false,
            addOriginInfo: {},
          };
        },
      },
      isEditPublic: {
        type: Boolean,
        default: false,
      },
      templateStage: {
        type: String,
        default: '',
      },
      templateInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      // 挂载后是否触发 changeType
      autoSelectedType: {
        type: Boolean,
        default: true,
      },
      nodesList: Array,
    },
    data() {
      return {
        isShowDataSource: false,
        isDataLoading: false,
        trueStatus: true,
        falseStatus: false,
        secondClick: false,
        // 公共字段保留默认值，隐藏条件，布局的设置，其他都进行隐藏
        isPublicField: false,
        formInfo: {
          prevId: '',
          name: '',
          key: '',
          type: '',
          regex: '',
          regex_config: {
            rule: {
              expressions: [],
              type: 'and',
            },
          },
          customRegex: '',
          source_type: '',
          source_uri: '',
          default_value: '',
          layout: '',
          validate: '',
          desc: '',
          is_tips: false,
          tips: '',
          show_type: false,
          show_conditions: {},
        },
        regexFieldList: [],
        allBetweenList: [
          {
            id: 1,
            available: 'INT',
            name: this.$t('m.common[\'大于\']'),
            typeName: '>',
          },
          {
            id: 2,
            available: 'INT',
            name: this.$t('m.common[\'小于\']'),
            typeName: '<',
          },
          {
            id: 3,
            available: 'INT',
            name: this.$t('m.common[\'不大于\']'),
            typeName: '<=',
          },
          {
            id: 4,
            available: 'INT',
            name: this.$t('m.common[\'不小于\']'),
            typeName: '>=',
          },
          {
            id: 5,
            available: 'DATE',
            name: this.$t('m.common[\'早于\']'),
            typeName: '<',
          },
          {
            id: 6,
            available: 'DATE',
            name: this.$t('m.common[\'晚于\']'),
            typeName: '>',
          },
          {
            id: 7,
            available: 'DATE',
            name: this.$t('m.common[\'不早于\']'),
            typeName: '>=',
          },
          {
            id: 8,
            available: 'DATE',
            name: this.$t('m.common[\'不晚于\']'),
            typeName: '<=',
          },
        ],
        betweenList: [],
        // 自定义复杂表格
        customTableInfo: {
          list: [
            { name: '', display: 'input', choice: '', required: false, nameCheck: false, check: false },
          ],
        },
        // 前置节点
        prevNodeList: [],
        // 前置所有节点的字段
        frontNodesList: [],
        // 校验方式
        regexList: [],
        // 显示数据类型
        showType: {
          sourceList: ['SELECT', 'MULTISELECT', 'CHECKBOX', 'RADIO', 'TABLE', 'TREESELECT', 'INPUTSELECT'],
          belongDefaultList: ['STRING', 'TEXT', 'INT', 'DATE', 'DATETIME', 'DATETIMERANGE', 'SELECT', 'MULTISELECT', 'CHECKBOX', 'RADIO', 'MEMBER', 'MEMBERS', 'INPUTSELECT', 'RICHTEXT', 'CUSTOM-FORM'],
          multipleList: ['MULTISELECT', 'CHECKBOX', 'MEMBERS', 'MEMBER'],
          layoutList: ['TABLE', 'CUSTOMTABLE', 'RICHTEXT', 'CUSTOM-FORM'],
        },
        // 校验规则
        rules: {},
        // api需要用到的字段
        assignValue: {},
        // 自定义类型数据
        fieldInfo: {
          list: [
            { name: '', key: '', required: false },
          ],
        },
        // api接口配置信息
        apiDetail: {},
        apiInfo: {
          api_info: {
            remote_system_id: '',
            remote_api_id: '',
            req_params: {},
            req_body: {},
            rsp_data: '',
          },
          kv_relation: {
            key: '',
            name: '',
          },
        },
        // 数据字典数据
        dictionaryData: {
          list: [],
          check: '',
        },
        // prc数据
        prcData: {
          list: [],
          check: '',
        },
        prcTable: [],
        // 上传文件
        fileList: [],
        fileVal: '',
        // 字段校验
        checkStatus: {
          customStatus: false,
          customTableStatus: false,
          customFormStatus: false,
        },
        // 任务内置字段特殊处理
        fieldTypeList: [],
        hiddenConditionStatus: true,
      };
    },
    computed: {
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
      isShowDataSourcebtn() {
        return (this.formInfo.source_type === 'API' || this.formInfo.source_type === 'CUSTOM') && (Object.keys(this.apiDetail).length !== 0 || this.fieldInfo.list.length !== 0);
      },
      isDisabled() {
        return this.formInfo.source_type === 'API' && !this.apiInfo.api_info.remote_api_id;
      },
    },
    watch: {
      formInfo: {
        handler(val) {
          this.$emit('getAddFieldStatus', val.name !== '');
        },
        deep: true,
      },
    },
    async mounted() {
      this.isDataLoading = true;
      await this.initData();
      this.rules.name = this.checkCommonRules('name').name;
      this.rules.key = this.checkCommonRules('key').key;
      this.rules.type = this.checkCommonRules('select').select;
      this.rules.tips = this.checkCommonRules('select').select;
      this.rules.prevId = this.checkCommonRules('select').select;
      this.isDataLoading = false;
      if (this.changeInfo.id === 'add' && this.autoSelectedType) {
        this.changeType();
      }
    },
    methods: {
      validateContent() {
        const result = this.checkField();
        if (result) {
          this.openDataSource();
        } else {
          this.isShowDataSource = false;
        }
      },
      openDataSource() {
        this.isShowDataSource = true;
      },
      fieldNameChange() {
        const keyElement = this.$refs.fieldForm.$data.formItems.find(item => item.property === 'key');
        if (keyElement.fieldValue) {
          keyElement.validator.content = '';
          keyElement.validator.state = '';
        }
      },
      // 初始化赋值数据
      initData() {
        // 去掉时间间隔的选项
        this.fieldTypeList = this.globalChoise.field_type.filter(item => item.typeName !== 'DATETIMERANGE');
        if ((this.changeInfo.type === 'COMPLEX-MEMBERS' || this.changeInfo.type === 'SOPS_TEMPLATE') && this.addOrigin.addOriginInfo.type === 'templateField') {
          this.fieldTypeList = this.fieldTypeList.concat([
            {
              name: this.$t('m.common[\'复杂人员选择\']'),
              typeName: 'COMPLEX-MEMBERS',
            },
            {
              name: this.$t('m.common[\'标准运维模板\']'),
              typeName: 'SOPS_TEMPLATE',
            },
          ]);
        }
        // 在不同的数据源里面添加不同的desc
        this.globalChoise.source_type.forEach(item => {
          const descInfo = item.typeName === 'CUSTOM' ? this.$t('m.treeinfo[\'自定义数据每行的name和key都不能相同。\']') : this.$t('m.treeinfo[\'接口中的数据详情\']');
          this.$set(item, 'desc', descInfo);
        });
        if (!this.nodesList) {
          this.getFrontNodesList();
        } else {
          this.frontNodesList = this.nodesList;
        }
        this.changeRegex('ASSOCIATED_FIELD_VALIDATION');
        this.assignmentData();
        // 获取字段校验方式
        this.getRegexList();
        // 获取PRC数据
        this.getRpcList();
        this.getSysDictList();
        this.getPreStates();
      },
      assignmentData(publicValue) {
        const assignValue = publicValue || this.changeInfo;
        this.formInfo.name = assignValue.name;
        this.formInfo.key = assignValue.key;
        this.formInfo.type = assignValue.type;
        this.formInfo.regex = assignValue.regex;
        if (assignValue.regex_config && assignValue.regex_config.rule) {
          this.changeRegex('ASSOCIATED_FIELD_VALIDATION');
          this.formInfo.regex_config.rule.type = assignValue.regex_config.rule.type;
          
          this.formInfo.regex_config = assignValue.regex_config;
        }
        if (this.formInfo.regex === 'CUSTOM') {
          this.formInfo.customRegex = assignValue.custom_regex || '';
        }
        this.formInfo.layout = assignValue.layout;
        this.formInfo.validate = assignValue.validate_type;
        this.formInfo.desc = assignValue.desc;
        this.formInfo.is_tips = assignValue.is_tips;
        this.formInfo.tips = assignValue.tips;
        this.formInfo.default_value = (this.showType.multipleList.some(item => item === assignValue.type) && assignValue.default !== '') ? assignValue.default.split(',') : (assignValue.default || '');
        // 数据源
        this.formInfo.source_type = assignValue.source_type;
        if (assignValue.source_type === 'CUSTOM') {
          if (assignValue.type === 'FILE') {
            for (const key in assignValue.choice) {
              this.fileList.push(assignValue.choice[key]);
            }
          } else if (assignValue.choice.length !== 0) {
            this.fieldInfo.list = [];
            assignValue.choice.forEach(item => {
              this.fieldInfo.list.push({
                name: item.name,
                key: item.key,
                required: !!item.required,
                nameCheck: false,
                keyCheck: false,
              });
            });
          }
        } else if (this.formInfo.source_type === 'API') {
          this.apiInfo.api_info = assignValue.api_info;
        } else if (this.formInfo.source_type === 'DATADICT') {
          this.formInfo.source_uri = assignValue.source_uri;
          this.dictionaryData.check = this.formInfo.source_uri;
        } else if (this.formInfo.source_type === 'RPC') {
          this.formInfo.source_uri = assignValue.source_uri;
          this.prcData.check = assignValue.source_uri;
        }
        // 隐藏条件
        this.formInfo.show_type = (assignValue.show_type === 0);
        this.formInfo.show_conditions = assignValue.show_conditions || {};
        if (this.formInfo.type === 'CUSTOMTABLE') {
          this.customTableInfo.list = [];
          if (Object.prototype.hasOwnProperty.call(assignValue.meta, 'columns')) {
            assignValue.meta.columns.forEach(node => {
              const valChoice = [];
              node.choice.forEach(vaule => {
                valChoice.push(vaule.name);
              });
              this.customTableInfo.list.push({
                name: node.name,
                display: node.display,
                choice: valChoice.join('\n'),
                required: node.required,
                nameCheck: false,
                check: false,
              });
            });
          } else {
            this.customTableInfo.list.push({ name: '', display: 'input', choice: '', required: false, nameCheck: false, check: false });
          }
        }
        // 标准运维变量
        if (Object.keys(this.sospInfo).length) {
          this.formInfo.name = this.sospInfo.name || '';
          this.formInfo.validate = 'REQUIRE';
        }

        this.assignValue = JSON.parse(JSON.stringify(assignValue));
      },
      // 获取前置节点的字段信息
      async getFrontNodesList() {
        if (!this.state && !this.templateInfo.id) {
          return;
        }
        let url = '';
        const params = {};
        if (this.state) {
          url = 'apiRemote/get_related_fields';
          params.workflow = this.workflow;
          params.state = this.state;
        }
        if (this.templateInfo.id) {
          url = 'taskTemplate/getFrontFieldsList';
          params.id = this.templateInfo.id;
          params.stage = this.templateStage;
        }
        await this.$store.dispatch(url, params).then(res => {
          this.frontNodesList = res.data;
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      // 操作字段关联条件
      addExpression() {
        this.formInfo.regex_config.rule.expressions.push({
          condition: '',
          key: '',
          source: 'field',
          type: this.formInfo.type,
          value: '',
        });
      },
      deleteExpression(index) {
        if (this.formInfo.regex_config.rule.expressions.length === 1) {
          return;
        }
        this.formInfo.regex_config.rule.expressions.splice(index, 1);
      },
      // 改变字段类型，需要进行操作
      async changeType() {
        // 改变字段类型，清空正则规则表达式
        this.formInfo.regex = 'EMPTY';
        this.formInfo.customRegex = '';
        // 表格，自定义表格，富文本，自定义表单（整行显示）
        if (this.showType.layoutList.includes(this.formInfo.type)) {
          this.formInfo.layout = 'COL_12';
        }
        // 改变字段类型，清空自定义数据，数据字典数据
        this.formInfo.field = '';
        this.dictionaryData.check = '';
        // 改变字段类型，改变数据源类型
        if (this.formInfo.type === 'TREESELECT') {
          this.formInfo.source_type = 'DATADICT';
        } else {
          this.formInfo.source_type = 'CUSTOM';
        }
        if (!this.fieldInfo.list.length) {
          this.fieldInfo.list = [
            { name: '', key: '', required: false, nameCheck: false, keyCheck: false },
          ];
        }
        if (this.formInfo.type === 'CUSTOM-FORM') {
          this.formInfo.default_value = CUSTOM_FORM_DEFAULT_VALUE;
        }
        await this.getRegexList();
        this.formInfo.regex_config.rule.expressions = [];
      },
      // 改变正则表达式，清空自定义规则
      changeRegex(data) {
        this.formInfo.customRegex = '';
        if (data === 'ASSOCIATED_FIELD_VALIDATION') {
          this.regexFieldList = this.frontNodesList.filter(item => this.formInfo.type === 'INT' ? item.type === this.formInfo.type : item.type === 'DATE' || item.type === 'DATETIME').filter(item => item.id !== this.changeInfo.id);
          if (['DATE', 'DATETIME'].includes(this.formInfo.type)) {
            this.regexFieldList.push({
              name: '系统时间',
              id: 'system_time',
              key: 'system_time',
              source: 'system',
            });
          }
          this.betweenList = this.allBetweenList.filter(item => this.formInfo.type === 'INT' ? item.available === 'INT' : item.available === 'DATE');
          this.betweenList.push({
            name: '等于',
            typeName: '==',
          });
          if (!this.formInfo.regex_config.rule.expressions.length) {
            this.addExpression();
          }
        }
      },
      getRegexList() {
        const params = this.formInfo.type;
        this.$store.dispatch('cdeploy/regexList', params).then((res) => {
          this.regexList = res.data.regex_choice.map(item => ({
            name: item[1] ? item[1] : this.$t('m.treeinfo["无"]'),
            typeName: item[0],
          }));
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      onRegexFieldChange(key, expression) {
        // system 表示系统内置条件，field 表示来源节点
        const systemCondition = ['system_time'];
        expression.source = systemCondition.includes(key) ? 'system' : 'field';
      },
      // 选择字段关系字段后填充接口所需内容
      relateSelected(...value) {
        value[2].type = value[1].type;
        value[2].source = value[1].source;
      },
      // 自动填充key值
      putKey() {
        if (typeof this.changeInfo.id !== 'number') {
          this.formInfo.key = '';
          const transfer = pinyin(this.formInfo.name, {
            style: pinyin.STYLE_NORMAL,
            heteronym: false,
          });
          transfer.forEach(item => {
            this.formInfo.key = `${this.formInfo.key}${item}`;
          });
          this.formInfo.key = this.formInfo.key.toUpperCase();
          this.formInfo.key = this.formInfo.key.replace(/\ /g, '_');
          if (this.formInfo.key.length >= 32) {
            this.formInfo.key = this.formInfo.key.substr(0, 32);
          }
        }
      },
      changeApiInfo(val) {
        this.apiDetail = val;
      },
      // rpc数据
      getRpcData(val) {
        this.prcTable = val;
      },
      // 上传文件模板
      handleFile(e) {
        const fileInfo = e.target.files[0];
        const maxSize = 100000;
        const fileSize = fileInfo.size / 1024;
        const fileName = fileInfo.name;
        for (let i = 0; i < this.fileList.length; i++) {
          if (fileName === this.fileList[i].name) {
            this.$bkMessage({
              message: this.$t('m.treeinfo["此文件已经上传"]'),
              theme: 'error',
            });
            return;
          }
        }

        if (fileSize <= maxSize) {
          const data = new FormData();
          data.append('field_file', fileInfo);
          this.$store.dispatch('cdeploy/fileUpload', { data }).then((res) => {
            for (const key in res.data.succeed_files) {
              this.fileList.push({ ...res.data.succeed_files[key], key });
            }
            this.fileVal = '';
            this.$bkMessage({
              message: this.$t('m.treeinfo["上传成功"]'),
              theme: 'success',
            });
          })
            .catch(res => {
              errorHandler(res, this);
            });
        } else {
          this.fileVal = '';
          this.$bkMessage({
            message: this.$t('m.treeinfo["该文件大小超过100MB！"]'),
            theme: 'error',
          });
        }
      },
      // 删除文件
      deleteFile(item, index) {
        this.fileList.splice(index, 1);
      },
      // 保存，取消
      async addField() {
        const params = await this.getDataContent();
        if (!params) {
          return;
        }
        if (this.secondClick) {
          return;
        }
        this.secondClick = true;
        if (typeof this.changeInfo.id === 'number') {
          const id = this.changeInfo.id;
          let url = this.changeInfo.source === 'TABLE' ? 'cdeploy/changeNewModuleField' : 'cdeploy/changeNewField';
          // 公共字段
          if (this.addOrigin.isOther && this.addOrigin.addOriginInfo.updateUrl) {
            url = this.addOrigin.addOriginInfo.updateUrl;
            if (this.addOrigin.addOriginInfo.type === 'templateField') {
              params.task_schema_id = this.templateInfo.id;
              params.stage = this.templateStage;
              if (params.type === 'COMPLEX-MEMBERS' || params.type === 'SOPS_TEMPLATE') {
                delete params.type;
              }
            }
          }
          // 项目下编辑字段
          if (this.changeInfo.project_key) {
            params.project_key = this.changeInfo.project_key;
          }
          this.$store.dispatch(url, { params, id }).then(() => {
            this.$bkMessage({
              message: this.$t('m.treeinfo["修改成功"]'),
              theme: 'success',
            });
            this.$emit('closeShade');

            // 公共字段 / 添加前置节点字段(重新拉取数据)
            if (this.addOrigin.isOther && this.addOrigin.addOriginInfo.updateUrl && this.addOrigin.addOriginInfo.type !== 'templateField' && this.$parent.$parent.getList) {
              this.$parent.$parent.getList();
            } else if (this.$parent.$parent.getTableList) {
              this.$parent.$parent.getTableList();
            } else {
              this.$emit('getRelatedFields');
            }
            this.$emit('onConfirm', Object.assign({}, this.changeInfo, params));
          })
            .catch(res => {
              errorHandler(res, this);
            })
            .finally(() => {
              this.secondClick = false;
            });
        } else {
          params.state = this.state;
          if (Object.keys(this.sospInfo).length) {
            params.state = this.formInfo.prevId;
          }
          let url = 'cdeploy/addNewField';
          // 公共字段
          if (this.addOrigin.isOther && this.addOrigin.addOriginInfo.addUrl) {
            url = this.addOrigin.addOriginInfo.addUrl;
            if (this.addOrigin.addOriginInfo.type === 'templateField') {
              params.task_schema_id = this.templateInfo.id;
              params.stage = this.templateStage;
            }
          }
          // 项目下新增字段
          if (this.changeInfo.project_key) {
            params.project_key = this.changeInfo.project_key;
          }

          this.$store.dispatch(url, { params }).then((res) => {
            this.addNew = res.data;
            this.$bkMessage({
              message: this.$t('m.treeinfo["新增成功"]'),
              theme: 'success',
            });
            this.$emit('closeShade');

            // 公共字段 / 添加前置节点字段(重新拉取数据)
            if (this.addOrigin.isOther && this.addOrigin.addOriginInfo.addUrl) {
              if (this.addOrigin.addOriginInfo.type === 'templateField' && this.$parent.$parent.getTableList) {
                this.$parent.$parent.getTableList();
              } else if (this.$parent.$parent.getList) {
                this.$parent.$parent.getList();
              }
            } else if (this.$parent.$parent.getTableList) {
              this.$parent.$parent.getTableList();
            } else {
              this.$emit('getRelatedFields');
              if (this.$parent.$parent.showNew) {
                this.$parent.$parent.showNew(this.sospInfo, res);
              }
            }
            this.$emit('onConfirm', res.data);
          })
            .catch(res => {
              errorHandler(res, this);
            })
            .finally(() => {
              this.secondClick = false;
            });
        }
      },
      onCancelClick() {
        this.$emit('closeShade');
        this.$emit('onCancel');
      },
      // 字段校验
      checkInfo() {
        this.$refs.fieldForm.validate().then(() => {
          // 数据源校验
          if (this.$refs.dataSource && this.$refs.dataSource.checkSouce()) {
            return;
          }
          // 自定义数据校验
          if (this.checkField()) {
            return;
          }
          // 字段释疑
          if (this.formInfo.is_tips && !this.formInfo.tips) {
            this.$bkMessage({
              theme: 'warning',
              message: this.$t('m.treeinfo["字段释疑为必填项"]'),
            });
            return;
          }
          this.addField();
        }, validator => {
          console.error(validator);
        });
      },
      async getDataContent() {
        // 区分模型字段，内置字段，基础字段
        const params = {};
        // 公用字段信息
        params.layout = this.formInfo.layout;
        params.validate_type = this.formInfo.validate;
        params.regex = this.formInfo.regex;
        params.regex_config = this.formInfo.regex_config;
        params.desc = this.formInfo.desc;
        params.is_tips = this.formInfo.is_tips;
        params.tips = this.formInfo.tips;
        // 字段默认值
        params.default = '';
        if (this.showType.belongDefaultList.some(defaultType => defaultType === this.formInfo.type)) {
          const defaultList = ['MULTISELECT', 'CHECKBOX', 'MEMBERS', 'MEMBER'];
          let formDefault = [];
          if (defaultList.some(defaultItem => defaultItem === this.formInfo.type) && this.formInfo.default_value) {
            formDefault = this.formInfo.default_value.filter(defaultItem => defaultItem !== '');
          }
          params.default = defaultList.some(defaultItem => defaultItem === this.formInfo.type) ? formDefault.join(',') : this.formInfo.default_value;
        }
        // 隐藏字段值
        if (this.$refs.hiddenConditions) {
          if (this.$refs.hiddenConditions.checkList()) {
            this.hiddenConditionStatus = false;
            return false;
          }
          const hiddenList = this.$refs.hiddenConditions.listInfo;
          params.show_conditions = {
            type: this.$refs.hiddenConditions.conditionType,
            expressions: [],
          };
          hiddenList.forEach(item => {
            params.show_conditions.expressions.push({
              key: item.key,
              condition: item.condition,
              value: Array.isArray(item.value) ? item.value.join(',') : item.value,
              type: item.type,
            });
          });
          params.show_type = 0;
        } else {
          params.show_type = 1;
          params.show_conditions = {};
        }
        // 只有基础字段才需要的值
        if (this.changeInfo.source !== 'TABLE') {
          params.workflow = this.workflow;
          params.name = this.formInfo.name;
          params.key = this.formInfo.key;
          params.type = this.formInfo.type;
          params.desc = this.formInfo.desc;
          params.source_type = this.formInfo.source_type || 'CUSTOM';
          params.custom_regex = this.formInfo.customRegex;
          params.is_tips = this.formInfo.is_tips;
          params.tips = this.formInfo.tips;
          // 文件字段特殊处理
          if (this.formInfo.type === 'FILE') {
            params.choice = {};
            this.fileList.forEach(file => {
              this.$set(params.choice, file.key, file);
            });
          } else {
            // 不同的数据源传递的数据不同
            if (this.formInfo.source_type === 'CUSTOM') {
              params.choice = [];
              // 常规数据需要传choice的字段类型（表格，单选下拉，多选下拉，复选框，单选框）
              if (this.formInfo.type === 'SELECT' || this.formInfo.type === 'MULTISELECT' || this.formInfo.type === 'CHECKBOX' || this.formInfo.type === 'RADIO' || this.formInfo.type === 'INPUTSELECT') {
                this.fieldInfo.list.forEach(item => {
                  params.choice.push({
                    key: item.key,
                    name: item.name,
                  });
                });
              } else if (this.formInfo.type === 'TABLE') {
                this.fieldInfo.list.forEach(item => {
                  params.choice.push({
                    key: item.key,
                    name: item.name,
                    required: item.required,
                  });
                });
              }
            } else if (this.formInfo.source_type === 'API') {
              if (this.formInfo.source_type === 'API') {
                // api参数校验
                const isre = await this.$refs.dataContent[0].apiFz();
                if (!isre) {
                  return false;
                }
              }
              params.api_info = this.apiInfo.api_info;
              params.kv_relation = this.apiInfo.kv_relation;
            } else if (this.formInfo.source_type === 'DATADICT') {
              params.choice = [];
              params.source_uri = this.dictionaryData.check;
            }
          }
          // 复杂表格数据
          if (this.formInfo.type === 'CUSTOMTABLE') {
            this.customTableInfo.list.forEach(item => {
              let choiceList = [];
              if (item.choice && (item.display === 'select' || item.display === 'multiselect')) {
                choiceList = item.choice.split('\n').filter(node => node.length > 0);
              }
              item.nameCheck = item.name.length === 0 || item.name.length > 120;
              item.check = (!choiceList.length && (item.display === 'select' || item.display === 'multiselect'));
            });
            const checkNameStatus = this.customTableInfo.list.some(item => item.nameCheck);
            const checkValueStatus = this.customTableInfo.list.some(item => item.check);
            if (checkNameStatus || checkValueStatus) {
              this.$bkMessage({
                theme: 'warning',
                message: this.$t('m.treeinfo["请填写正确格式的自定义数据"]'),
              });
              return false;
            }
            params.meta = {};
            params.meta.columns = [];
            this.customTableInfo.list.forEach(item => {
              let choiceList = item.choice.split('\n').filter(node => node.length > 0);
              choiceList = Array.from(new Set(choiceList));
              params.meta.columns.push({
                name: item.name,
                display: item.display,
                choice: item.choice.length ? choiceList : [],
                required: item.required,
              });
            });
          }
          // RPC数据
          if (this.formInfo.source_type === 'RPC') {
            params.source_uri = this.prcData.check;
            params.meta = {};
            this.prcTable.forEach(prcInfo => {
              const prcValue = prcInfo.source_type === 'CUSTOM' ? prcInfo.value : (`\${params_${prcInfo.value_key}}`);
              params.meta[prcInfo.name] = prcValue;
            });
          }
        }
        return this.timeConversion(params);
      },
      // 将时间转换一下
      timeConversion(params) {
        // 默认值
        if (params.default !== '') {
          if (params.type === 'DATE' || params.type === 'DATETIME') {
            params.default = params.type === 'DATE' ? this.standardDayTime(params.default) : this.standardTime(params.default);
          }
        }
        // 隐藏条件
        if (params.show_conditions && params.show_conditions.expressions && params.show_conditions.expressions.length) {
          params.show_conditions.expressions.forEach(item => {
            if (item.type === 'DATE' || item.type === 'DATETIME') {
              item.value = item.type === 'DATE' ? this.standardDayTime(item.value) : this.standardTime(item.value);
            }
          });
        }
        return params;
      },
      // 字段校验
      checkField() {
        this.checkStatus.customStatus = false;
        this.checkStatus.customTableStatus = false;
        this.checkStatus.customFormStatus = false;
        // 自定义数据
        const customTypeList = ['SELECT', 'MULTISELECT', 'CHECKBOX', 'RADIO', 'TABLE'];
        if (customTypeList.some(item => this.formInfo.type === item) && this.formInfo.source_type === 'CUSTOM') {
          // 判断key，name的值
          this.fieldInfo.list.forEach(item => {
            item.nameCheck = item.name.length > 120 || item.name.length === 0;
            item.keyCheck = !(/[a-zA-Z0-9]+$/.test(item.key));
          });
          // 判断重复的key和name
          this.fieldInfo.list.forEach((item, index) => {
            this.fieldInfo.list.forEach((node, nodeIndex) => {
              if (index !== nodeIndex) {
                if (node.key === item.key) {
                  item.keyCheck = true;
                }
                if (node.name === item.name) {
                  item.nameCheck = true;
                }
              }
            });
          });
          this.checkStatus.customStatus = this.fieldInfo.list.some(item => (item.nameCheck || item.keyCheck));
        }

        if (this.formInfo.type === 'CUSTOMTABLE') {
          const repeatName = [];
          this.customTableInfo.list.forEach(item => {
            let choiceList = [];
            if (item.choice && (item.display === 'select' || item.display === 'multiselect')) {
              choiceList = item.choice.split('\n').filter(node => node.length > 0);
            }
            item.nameCheck = item.name.length === 0 || item.name.length > 120;
            item.check = (!choiceList.length && (item.display === 'select' || item.display === 'multiselect'));
            if (!repeatName.includes(item.name)) {
              repeatName.push(item.name);
            } else {
              item.nameCheck = true;
            }
          });
          this.checkStatus.customTableStatus = this.customTableInfo.list.some(item => (item.nameCheck || item.check));
        }
        if (this.formInfo.type === 'CUSTOM-FORM') {
          try {
            const customFormDefaultValue = JSON.parse(this.formInfo.default_value);
            if (customFormDefaultValue) {
              // 至少含义 schemes 和 form_data 字段
              this.checkStatus.customFormStatus = !customFormDefaultValue.schemes || !customFormDefaultValue.form_data;
            }
          } catch (error) {
            this.checkStatus.customFormStatus = true;
          }
        }
        return this.checkStatus.customStatus || this.checkStatus.customTableStatus || this.checkStatus.customFormStatus;
      },
      // 获取RPC数据
      getRpcList() {
        this.$store.dispatch('datadict/getPrcData').then((res) => {
          const skip_keys = ['table_fields', 'flow_states'];
          this.prcData.list = res.data.filter(item => skip_keys.indexOf(item.key) === -1);
          if (this.prcData.list.filter(prcInfo => prcInfo.key === this.prcData.check).length) {
            this.prcTable = this.prcData.list.filter(prcInfo => prcInfo.key === this.prcData.check)[0].req_params;
          }
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 获取字典列表
      getSysDictList() {
        this.$store.dispatch('datadict/list', {}).then((res) => {
          this.dictionaryData.list = res.data.filter(item => item.is_enabled);
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 获取前置节点
      getPreStates() {
        if (!this.state) {
          return;
        }
        this.$store.dispatch('deployCommon/getPreStates', { id: this.state }).then((res) => {
          this.prevNodeList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../../../scss/mixins/clearfix.scss';
    @import "../../../../../scss/mixins/scroller";
    .configuration-data-source {
        // width: 102px;
        height: 32px;
        border: 1px solid #3a84ff;
        border-radius: 4px;
        color: #3a84ff;
        font-size: 14px;
        line-height: 30px;
        text-align: center;
    }
    .data-source-tip {
        color: red;
        font-size: 14px;
        line-height: 32px;
    }
    .bk-tanble-height {
        .bk-textarea-tanble {
            overflow-y: scroll;
            position: absolute;
            min-height: 32px;
            padding: 3px 10px;
            float: left;
            line-height: 24px !important;
            @include scroller;
        }
    }
    .bk-halfline-item {
        display: inline-block;
        width: 49%;
    }
    .bk-halfline-margin {
        margin-right: 1%;
    }
    .bk-mt0-item{
        margin-top: 0!important;
    }
    .bk-mt20-item{
        margin-top: 20px!important;
    }
    .bk-input-position {
        position: relative;
        .bk-input-file {
            position: absolute;
            top: 0;
            left: 0;
            width: 96px;
            height: 36px;
            overflow: hidden;
            opacity: 0;
            cursor: pointer;
        }
        .bk-file-list {
            margin-top: 10px;
            line-height: 25px;
            font-size: 14px;
            color: #424950;
            li {
                &:hover {
                    background-color: #dfeeff;
                }
            }
            .bk-file-success {
                color: #30d878;
                font-size: 12px;
            }
            .bk-file-delete {
                float: right;
                font-size: 20px;
                color: #7a7f85;
                cursor: pointer;
            }
        }
    }
    .bk-label-tips {
        position: absolute;
        top: -30px;
        left: 267px;
        font-size: 14px;
        color: #3a84ff;
    }
    .bk-form-disabled {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        cursor: not-allowed;
        z-index: 10;
    }

    .bk-relate-conditions {
        font-size: 12px;
        color: #737987;
        padding: 16px 22px;
        border: 1px solid #DCDEE5;
        background-color: #F0F1F5;
        position: relative;
        .bk-between-form {
            @include clearfix;
            display: flex;
            align-items: center;
            padding: 10px 0;
        }
        .current-field {
            height: 32px;
            line-height: 32px;
            border: 1px solid #c3cdd7;
            width: 210px;
            background: white;
            margin-right: 10px;
            padding-left: 10px;
        }
        .field-valid-select{
            height: 32px;
            margin-right: 10px;
        }
        .bk-error-msg {
            color: #ff5656;
            font-size: 12px;
            line-height: 19px;
            text-align: left;
        }
        .bk-between-operate {
            float: right;
            line-height: 36px;
            font-size: 18px;
            width: 64px;
            margin-left: 4px;
            .bk-itsm-icon {
                color: #C4C6CC;
                margin-right: 9px;
                cursor: pointer;
                &:hover {
                    color: #979BA5;
                }
            }
            .bk-no-delete {
                cursor: not-allowed;
                &::before{
                    color: #DCDEE5;
                }
                &:hover {
                    &::before{
                        color: #DCDEE5;
                    }
                }
            }
        }
        .bk-form-p {
            color: #737987;
            font-size: 14px;
            margin-bottom: 10px;
            .bk-span-prompt {
                font-size: 12px;
                color: #C4C6CC;
            }
            .icon-question-circle {
                position: relative;
                font-size: 12px;
                color: #979BA5;

                &:hover {
                    .entry-title {
                        display: block;
                    }
                }
            }
        }
        .icon-close {
            position: absolute;
            top: 6px;
            right: 6px;
            font-size: 18px;
            cursor: pointer;
            text-align: center;
            color: #c4c6cc;
            &:hover {
                background-color: #dcdee5;
                color: #fff;
                border-radius: 50%;
            }
        }
        .bk-form-style {
            width: 185px;
            float: left;
            margin-right: 10px;
        }
    }
    .bk-field-error {
        line-height: 32px;
        color: #ff5656;
        font-size: 12px;
    }
</style>
