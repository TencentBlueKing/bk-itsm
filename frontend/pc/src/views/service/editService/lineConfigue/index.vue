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
  <div class="bk-configu-line" ref="lienHeight">
    <div class="bk-line-graph">
      <div class="bk-line-div"
        :class="{ 'bk-line-small': widthStatus === 2, 'bk-line-big': widthStatus === 1 }">
        <template-node
          :node="customLine.nodeInfo.from_state"></template-node>
        <div class="bk-line-style">
          <span class="bk-line-line">
            <span class="bk-line-info"></span>
          </span>
          <!-- 显示改变后的数据 -->
          <span class="bk-line-word"> {{lineInfo.name || '--'}} </span>
          <span class="bk-line-squrea"></span>
        </div>
        <template-node
          :node="customLine.nodeInfo.to_state"></template-node>
      </div>
    </div>
    <bk-form
      :label-width="200"
      :model="lineInfo"
      form-type="vertical"
      :rules="rules"
      ref="lineForm">
      <template v-if="!customLine.isOnly">
        <bk-form-item
          :label="$t(`m.treeinfo['关系模板']`)"
          :desc="$t(`m.treeinfo['（使用模版可以快速填写）']`)">
          <bk-select v-model="lineInfo.template"
            :clearable="false"
            searchable
            :font-size="'medium'"
            @selected="changeTemplate">
            <bk-option v-for="option in templateList"
              :key="option.id"
              :id="option.id"
              :name="option.name">
            </bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item
          data-test-id="lineConfig-select-condition"
          :label="$t(`m.treeinfo['流转条件']`)"
          :required="true">
          <bk-select v-model="lineInfo.condition_type"
            :clearable="false"
            searchable
            :font-size="'medium'"
            @selected="changeCondition">
            <bk-option v-for="option in globalChoise.condition_type"
              :key="option.typeName"
              :id="option.typeName"
              :name="option.name">
            </bk-option>
          </bk-select>
        </bk-form-item>
      </template>
      <bk-form-item
        data-test-id="lineConfig-select-relation"
        :label="$t(`m.treeinfo['关系名称']`)"
        :property="'name'"
        :required="true">
        <bk-input v-model.trim="lineInfo.name"
          maxlength="120"
          :placeholder="$t(`m.treeinfo['请输入关系名称']`)">
        </bk-input>
      </bk-form-item>
    </bk-form>
    <!-- 字段判断 -->
    <template v-if="lineInfo.condition_type !== 'default'">
      <div v-bkloading="{ isLoading: isDataLoading }">
        <bk-form
          :label-width="200"
          :model="lineInfo"
          :ext-cls="'bk-line-form'"
          form-type="vertical"
          ref="conditionForm">
          <bk-form-item
            :label="$t(`m.treeinfo['条件组间关系']`)"
            :desc="$t(`m.treeinfo['当所有条件组都满足且/或的条件时，节点才会流转']`)"
            :ext-cls="'mb10 mt10'">
            <bk-radio-group v-model="lineInfo.between">
              <bk-radio :value="'and'" class="mr10">{{ $t('m.treeinfo["且"]') }}</bk-radio>
              <bk-radio :value="'or'">{{ $t('m.treeinfo["或"]') }}</bk-radio>
            </bk-radio-group>
          </bk-form-item>
          <div class="bk-form-content"
            v-for="(item, index) in lineInfo.expressions"
            :key="index">
            <p class="bk-between-title">{{lineInfo.between === 'and' ? $t(`m.treeinfo['且']`) :
              $t(`m.treeinfo["或"]`)}}{{ $t('m.treeinfo["-条件组"]') }}{{index + 1}}</p>
            <div class="bk-between-info">
              <p>
                <span class="bk-between-span">{{ $t('m.treeinfo["字段间关系"]') }}</span>
                <bk-radio-group v-model="item.type" style="width: auto;">
                  <bk-radio :value="'and'" class="mr10">{{ $t('m.treeinfo["且"]') }}</bk-radio>
                  <bk-radio :value="'or'">{{ $t('m.treeinfo["或"]') }}</bk-radio>
                </bk-radio-group>
              </p>
              <div class="bk-between-form"
                v-for="(node, nodeIndex) in item.expressions"
                :key="nodeIndex" @click="item.checkInfo = false">
                <bk-form-item
                  data-test-id="lineConfig-select-fieldList"
                  :ext-cls="'bk-width210 no-label'">
                  <bk-select
                    v-model="node.key"
                    :clearable="false"
                    searchable
                    :font-size="'medium'"
                    @selected="changeName(...arguments, node)">
                    <bk-option v-for="option in fieldList"
                      :key="option.key"
                      :id="option.key"
                      :name="option.name">
                    </bk-option>
                  </bk-select>
                </bk-form-item>
                <template v-if="node.betweenList">
                  <bk-form-item
                    data-test-id="lineConfig-select-betweenList"
                    :ext-cls="'bk-width100 no-label'">
                    <bk-select
                      v-model="node.condition"
                      :clearable="false"
                      searchable
                      :font-size="'medium'">
                      <bk-option v-for="option in node.betweenList"
                        :key="option.typeName"
                        :id="option.typeName"
                        :name="option.name">
                      </bk-option>
                    </bk-select>
                  </bk-form-item>
                </template>
                <bk-form-item
                  data-test-id="lineConfig-select-choiceList"
                  :label="''"
                  :ext-cls="'bk-width195 no-label'">
                  <template v-if="node.source !== 'global'">
                    <template v-if="globalTypeList.some(global => node.type === global)">
                      <bk-select
                        v-if="node.choiceList.length"
                        v-model="node.value"
                        :multiple="node.multiSelect"
                        searchable
                        :font-size="'medium'">
                        <bk-option v-for="option in node.choiceList"
                          :key="option.id"
                          :id="option.id"
                          :name="option.name">
                        </bk-option>
                      </bk-select>
                      <bk-input
                        v-else
                        :clearable="true"
                        :type="node.type === 'INT' ? 'number' : 'text'"
                        v-model="node.value"
                        :placeholder="$t(`m.treeinfo['请输入条件值']`)">
                      </bk-input>
                    </template>
                    <template v-else-if="node.type === 'DATE' || node.type === 'DATETIME'">
                      <bk-date-picker
                        v-model="node.value"
                        :placeholder="'选择日期时间'"
                        :type="node.type === 'DATETIME' ? 'datetime' : 'date'">
                      </bk-date-picker>
                    </template>
                    <template v-else>
                      <bk-input
                        :clearable="true"
                        :type="node.type === 'INT' ? 'number' : 'text'"
                        v-model="node.value"
                        :placeholder="$t(`m.treeinfo['请输入条件值']`)">
                      </bk-input>
                      <span v-if="node.meta && node.meta.unit" class="buttonIcon">%</span>
                    </template>
                  </template>
                  <template v-if="node.source === 'global'">
                    <template v-if="node.type === 'BOOLEAN'">
                      <bk-select
                        v-model="node.value"
                        searchable
                        :font-size="'medium'">
                        <bk-option v-for="option in booleanList"
                          :key="option.id"
                          :id="option.id"
                          :name="option.name">
                        </bk-option>
                      </bk-select>
                    </template>
                    <template v-else>
                      <bk-input
                        :clearable="true"
                        :type="node.type === 'INT' ? 'number' : 'text'"
                        v-model="node.value"
                        :placeholder="$t(`m.treeinfo['请输入比较值']`)">
                      </bk-input>
                    </template>
                  </template>
                </bk-form-item>
                <div class="bk-between-operat">
                  <span data-test-id="lineConfig-span-addNode" class="bk-itsm-icon icon-flow-add" @click="addNode(item, nodeIndex)"></span>
                  <i class="bk-itsm-icon icon-flow-reduce"
                    data-test-id="lineConfig-i-deleteNode"
                    :class="{ 'bk-no-delete': item.expressions.length === 1 }"
                    @click="deleteNode(item, nodeIndex)"></i>
                </div>
              </div>
              <i class="bk-icon icon-close"
                v-if="lineInfo.expressions.length !== 1"
                @click="delteCondition(item, index)"></i>
            </div>
            <p class="bk-error-msg" v-if="item.checkInfo">{{ $t('m.treeinfo["关系组内的数据不能为空"]') }}</p>
          </div>
        </bk-form>
      </div>
      <p class="bk-add-between">
        <span data-test-id="lineConfig-span-addCondition" @click="addCondition">
          <i class="bk-icon icon-plus-circle"></i>{{ $t('m.treeinfo["添加条件组"]') }}
        </span>
      </p>
    </template>
    <div :class="{ 'bk-line-padding': scrollTopStatus }" v-if="openFunction.TRIGGER_SWITCH">
      <common-trigger-list :origin="'transition'"
        :source-id="customLine.lineValue.workflow"
        :sender="customLine.lineValue.id"
        :table="flowInfo.table">
      </common-trigger-list>
    </div>
    <div class="mt20" :class="{ 'bk-line-btn': scrollTopStatus }">
      <bk-button theme="primary"
        data-test-id="lineConfig-button-submit"
        class="mr10"
        :title="$t(`m.treeinfo['确认']`)"
        :loading="secondClick"
        @click="submitLine">
        {{ $t('m.treeinfo["确认"]') }}
      </bk-button>
      <bk-button theme="default"
        class="mr10"
        :title="$t(`m.treeinfo['取消']`)"
        :disabled="secondClick"
        @click="closeLine">
        {{ $t('m.treeinfo["取消"]') }}
      </bk-button>
      <bk-button theme="default"
        class="mr10"
        :title="$t(`m.treeinfo['删除']`)"
        :disabled="secondClick"
        @click="deleteLine">
        {{ $t('m.treeinfo["删除"]') }}
      </bk-button>
      <bk-button theme="default"
        v-if="lineInfo.condition_type === 'by_field'"
        style="float: right;"
        :title="lineInfo.template ? $t(`m.treeinfo['更新模板']`) : $t(`m.treeinfo['存为模版']`)"
        :disabled="secondClick"
        @click="submitTemplate">
        {{lineInfo.template ? $t(`m.treeinfo['更新模板']`) : $t(`m.treeinfo['存为模版']`)}}
      </bk-button>
    </div>
  </div>
</template>
<script>
  import templateNode from './templateNode.vue';
  import apiFieldsWatch from '@/views/commonMix/api_fields_watch.js';
  import commonMix from '@/views/commonMix/common.js';
  import commonTriggerList from '@/views/processManagement/taskTemplate/components/commonTriggerList';
  import { errorHandler } from '@/utils/errorHandler';

  export default {
    components: {
      templateNode,
      commonTriggerList,
    },
    mixins: [apiFieldsWatch, commonMix],
    props: {
      customLine: {
        type: Object,
        default() {
          return {};
        },
      },
      flowInfo: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        isDataLoading: false,
        secondClick: false,
        booleanList: [
          {
            id: '1',
            name: 'true',
          },
          {
            id: '0',
            name: 'false',
          },
        ],
        widthStatus: 0,
        scrollTopStatus: 0,
        lineInfo: {
          // 关系模板
          template: '',
          // 流转条件
          condition_type: '',
          // 关系名称
          name: '',
          checkName: false,
          // 关系
          between: true,
          // 条件组
          expressions: [
            {
              type: 'and',
              expressions: [
                { condition: '', key: '', value: '', choiceList: '', type: 'STRING', betweenList: [] },
              ],
            },
          ],
        },
        // 显示隐藏条件组关系
        templateList: [],
        // 条件组数组
        fieldList: [],
        // 剔除type的数组数据
        globalTypeList: ['SELECT', 'MULTISELECT', 'RADIO', 'CHECKBOX', 'MEMBERS', 'TREESELECT'],
        // 校验
        rules: {},
      };
    },
    computed: {
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
      openFunction() {
        return this.$store.state.openFunction;
      },
    },
    watch: {
      fieldList: {
        handler() {
          this.dealList();
        },
        deep: true,
      },
    },
    mounted() {
      this.initData();
      // 校验
      this.rules.name = this.checkCommonRules('name').name;
      this.rules.value = this.checkCommonRules('select').select;
      this.rules.key = this.rules.value;
      this.rules.condition = this.rules.value;
      // 判断标签的滚动长度
      this.$store.state.common.slideTimeout = setInterval(() => {
        if (!this.$refs.lienHeight) {
          clearInterval(this.$store.state.common.slideTimeout);
          return;
        }
        this.scrollTopStatus = this.$refs.lienHeight.offsetHeight + 60 > document.body.offsetHeight;
      }, 100);
    },
    methods: {
      initData() {
        // 判断线条弹窗的长度
        this.widthStatus = 0;
        const valueList = ['START', 'END', 'ROUTER-P', 'COVERAGE'];
        const fromValue = valueList.some(item => this.customLine.nodeInfo.from_state.type === item);
        if (fromValue) {
          this.widthStatus += 1;
        }
        const toValue = valueList.some(item => this.customLine.nodeInfo.to_state.type === item);
        if (toValue) {
          this.widthStatus += 1;
        }
        // 初始化赋值
        this.lineInfo.name = this.customLine.lineValue.name === this.$t('m.treeinfo[\'默认\']') ? '' : this.customLine.lineValue.name;
        this.lineInfo.condition_type = this.customLine.lineValue.condition_type;
        this.lineInfo.between = this.customLine.lineValue.condition.type;
        this.lineInfo.expressions = JSON.parse(JSON.stringify(this.customLine.lineValue.condition.expressions));
        this.lineInfo.expressions.forEach((item) => {
          item.expressions.forEach((ite) => {
            if (ite.type === 'BOOLEAN') {
              ite.value = ite.value ? '1' : '0';
            }
          });
        });
        // 获取字段值
        this.getFieldList();
        // 获取关系模板
        this.getBetweenTemplate();
      },
      checkBetweenList(typeValue) {
        const listOne = ['MULTISELECT', 'CHECKBOX', 'MEMBERS', 'TREESELECT'];
        const listTwo = ['DATE', 'DATETIME', 'DATETIMERANGE', 'INT'];
        const listThree = ['TEXT', 'STRING'];
        let betweenList = [];
        if (listOne.some(type => type === typeValue)) {
          betweenList = this.globalChoise.methods.filter(methods => (methods.typeName === 'issuperset' || methods.typeName === 'notissuperset'));
        } else if (listTwo.some(type => type === typeValue)) {
          betweenList = this.globalChoise.methods.filter(methods => (methods.typeName !== 'issuperset' && methods.typeName !== 'notissuperset'));
        } else if (listThree.some(type => type === typeValue)) {
          const filterList = ['==', '!=', 'in', 'notin'];
          betweenList = this.globalChoise.methods.filter(methods => filterList.includes(methods.typeName));
        } else {
          const filterList = ['==', '!='];
          betweenList = this.globalChoise.methods.filter(methods => filterList.includes(methods.typeName));
        }
        return betweenList;
      },
      // 获取关系模板
      getBetweenTemplate() {
        const params = {
          workflow: this.customLine.lineValue.workflow,
        };
        this.$store.dispatch('deployCommon/getLineTemplate', params).then((res) => {
          this.templateList = res.data.items;
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      async getRpcData(item) {
        await this.$store.dispatch('apiRemote/getRpcData', item).then((res) => {
          item.choice = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 获取字段值选项
      getFieldList() {
        const { id } = this.customLine.lineValue;
        this.isDataLoading = true;
        this.$store.dispatch('deployCommon/getLineField', { id }).then((res) => {
          this.fieldList = res.data;
          this.fieldList.forEach((item) => {
            if (item.source_type === 'RPC') {
              this.getRpcData(item);
            }
          });
          this.isNecessaryToWatch({ fields: this.fieldList }, 'workflow');
          this.dealList();
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
      },
      dealList() {
        this.lineInfo.expressions.forEach((item) => {
          this.$set(item, 'checkInfo', false);
          item.expressions.forEach((node) => {
            node.type = node.type || 'STRING';
            node.choiceList = '';
            this.$set(node, 'betweenList', []);
            node.betweenList = this.checkBetweenList(node.type);
            if (node.type === 'SELECT' || node.type === 'MULTISELECT' || node.type === 'RADIO' || node.type === 'CHECKBOX' || node.type === 'MEMBERS' || node.type === 'TREESELECT' || node.type === 'INT') {
              this.fieldList.forEach((info) => {
                if (info.key === node.key) {
                  node.choiceList = [];
                  info.choice.forEach((infoChoice) => {
                    node.choiceList.push({
                      id: infoChoice.key,
                      name: infoChoice.name,
                    });
                  });
                  if (node.type === 'MULTISELECT' || node.type === 'CHECKBOX' || node.type === 'MEMBERS' || node.type === 'TREESELECT') {
                    node.value = Array.isArray(node.value) ? node.value : node.value.split(',');
                  }
                  this.$set(node, 'multiSelect', !(node.type === 'SELECT' || node.type === 'RADIO'));
                }
              });
            }
          });
        });
      },
      // 选择关系模板
      changeTemplate(value, option) {
        // 获取选中的项
        const checkData = this.templateList.filter(item => item.id === option.id)[0];
        // 选择关系模板改变流转条件
        this.lineInfo.condition_type = 'by_field';
        this.lineInfo.between = checkData.data.type;
        this.lineInfo.expressions = checkData.data.expressions;
        // 将关系模板名称填充到关系名称里面
        this.lineInfo.name = checkData.name;
      },
      // 流转条件
      changeCondition() {
        // 改变流转条件，清空关系模板
        this.lineInfo.template = '';
        // 改变流转条件 清空条件组数据
        this.lineInfo.expressions = [
          {
            type: 'and',
            checkInfo: false,
            expressions: [
              { condition: '', key: '', value: '', choiceList: '', type: 'STRING', betweenList: this.checkBetweenList('STRING') },
            ],
          },
        ];
      },
      // 字段间关系
      changeName() {
        // 过滤获取当前选中的项
        const checkItem = this.fieldList.filter(item => arguments[0] === item.key)[0];
        arguments[2].meta = checkItem.meta;
        // 获取当前要操作的项
        const nodeItem = arguments[2];
        // 重新赋值当前操作项的值(source, type, choiceList, value, betweenList, condition)
        nodeItem.source = nodeItem.source || 'field';
        nodeItem.type = checkItem.type;
        if (this.globalTypeList.some(item => item === nodeItem.type)) {
          nodeItem.choiceList = checkItem.choice.map(choice => ({
            id: choice.key,
            name: choice.name,
          }));
          this.$set(nodeItem, 'multiSelect', !(nodeItem.type === 'SELECT' || nodeItem.type === 'RADIO'));
        } else {
          nodeItem.choiceList = '';
          this.$set(nodeItem, 'multiSelect', false);
        }
        nodeItem.value = nodeItem.multiSelect ? [] : '';
        const betweenList = this.checkBetweenList(nodeItem.type);
        this.$set(arguments[2], 'betweenList', betweenList);
        nodeItem.condition = '';
      },
      // 新增关系组
      addCondition() {
        const value = {
          type: 'and',
          checkInfo: false,
          expressions: [
            { condition: '', key: '', value: '', choiceList: '', type: 'STRING', betweenList: this.checkBetweenList('STRING') },
          ],
        };
        this.lineInfo.expressions.push(value);
      },
      delteCondition(item, index) {
        if (this.lineInfo.expressions.length === 1) {
          return;
        }
        this.lineInfo.expressions.splice(index, 1);
      },
      // 新增字段条件组
      addNode(item, index) {
        const value = {
          condition: '', key: '', value: '', choiceList: '', type: 'STRING', betweenList: this.checkBetweenList('STRING'),
        };
        item.expressions.splice(index + 1, 0, value);
      },
      deleteNode(item, index) {
        if (item.expressions.length === 1) {
          return;
        }
        item.expressions.splice(index, 1);
      },
      // 数据校验
      submitLine() {
        if (this.lineInfo.condition_type === 'by_field') {
          this.lineInfo.expressions.forEach((item) => {
            item.checkInfo = item.expressions.some(node => (!node.condition || !node.key || (Array.isArray(node.value) ? !node.value.length : !node.value)));
          });
          const checkStatus = this.lineInfo.expressions.some(item => item.checkInfo);
          if (checkStatus) {
            return;
          }
        }

        this.$refs.lineForm.validate().then(() => {
          this.submitFn();
        }, (validator) => {
          console.warn(validator);
        });
      },
      // 按钮事件
      submitFn() {
        if (this.secondClick) {
          return;
        }
        this.secondClick = true;
        const lineParams = {
          name: this.lineInfo.name,
          condition_type: this.lineInfo.condition_type,
          condition: {
            expressions: [],
            type: this.lineInfo.between,
          },
          from_state: this.customLine.lineValue.from_state,
          to_state: this.customLine.lineValue.to_state,
          workflow: this.customLine.lineValue.workflow,
        };
        // 将choiceList的数据清空
        this.lineInfo.expressions.forEach((item) => {
          lineParams.condition.expressions.push({
            checkInfo: item.checkInfo,
            expressions: [],
            type: item.type,
          });
        });
        this.lineInfo.expressions.forEach((item, index) => {
          item.expressions.forEach((node) => {
            lineParams.condition.expressions[index].expressions.push({
              choiceList: [],
              condition: node.condition,
              key: node.key,
              source: node.source,
              type: node.type,
              value: this.formattingData(node),
              meta: node.meta,
            });
          });
        });
        const { id } = this.customLine.lineValue;
        this.$store.dispatch('deployCommon/updateLine', { lineParams, id }).then((res) => {
          this.$bkMessage({
            message: this.$t('m.treeinfo["配置成功！"]'),
            theme: 'success',
          });
          this.$emit('submitLine', res.data);
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.secondClick = false;
          });
      },
      closeLine() {
        this.$emit('closeLine');
      },
      deleteLine() {
        this.$emit('deleteLine');
      },
      // 存为模板
      submitTemplate() {
        this.lineInfo.expressions.forEach((item) => {
          item.expressions.forEach((node) => {
            node.value = this.formattingData(node);
          });
        });
        const params = {
          workflow: this.customLine.lineValue.workflow,
          name: this.lineInfo.name,
          data: {
            expressions: this.lineInfo.expressions,
            type: this.lineInfo.between,
          },
        };
        if (this.lineInfo.template) {
          params.id = this.lineInfo.template;
        }
        if (!this.lineInfo.name) {
          return;
        }
        if (this.secondClick) {
          return;
        }
        this.secondClick = true;
        const templateUrl = this.lineInfo.template ? 'deployCommon/updateLineTemplate' : 'deployCommon/submitLineTemplate';
        this.$store.dispatch(templateUrl, { params }).then(() => {
          this.$bkMessage({
            message: this.$t('m.treeinfo["保存成功！"]'),
            theme: 'success',
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.secondClick = false;
          });
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import './lineConfigu.scss';

    .bk-form-border {
        border-color: #ff5555;
    }
    .no-label{
        /deep/.bk-label{
            display: none;
        }
    }
</style>
