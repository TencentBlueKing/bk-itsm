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
  <div class="bk-hidden-conditions" @click="checkStatus = false" v-bkloading="{ isLoading: isLoading }">
    <div class="bk-form-content" style="margin-left: 0">
      <p class="bk-form-p">{{$t(`m.treeinfo['条件组间关系']`)}}</p>
      <bk-radio-group v-model="conditionType">
        <bk-radio :value="'and'" :ext-cls="'mr20'">{{$t(`m.treeinfo['且']`)}}</bk-radio>
        <bk-radio :value="'or'">{{$t(`m.treeinfo['或']`)}}</bk-radio>
      </bk-radio-group>
    </div>
    <p class="bk-error-msg" v-if="checkStatus">{{$t(`m.treeinfo['关系名称，关系表达式，关系值不能为空']`)}}</p>
    <i class="bk-icon icon-close"
      @click="clearCondition"></i>
    <div class="bk-between-form"
      :class="{ 'mt20': nodeIndex }"
      v-for="(node, nodeIndex) in listInfo"
      :key="nodeIndex">
      <bk-select style="width: 182px; float: left; margin-right: 10px;"
        v-model="node.key"
        searchable
        @selected="changeName(...arguments, node)">
        <bk-option v-for="option in fieldList"
          :key="option.key"
          :id="option.key"
          :name="option.name">
        </bk-option>
      </bk-select>
      <bk-select style="width: 120px; float: left; margin-right: 10px;"
        v-model="node.condition"
        searchable>
        <bk-option v-for="option in node.betweenList"
          :key="option.typeName"
          :id="option.typeName"
          :name="option.name">
        </bk-option>
      </bk-select>
      <!-- 判断父元素的类型 来觉得第三个框的样式 -->
      <template
        v-if="node.type === 'SELECT' || node.type === 'MULTISELECT' || node.type === 'RADIO' || node.type === 'CHECKBOX' || node.type === 'MEMBERS' || node.type === 'TREESELECT'">
        <template v-if="node.choiceList.length">
          <bk-select :ext-cls="'bk-form-style'"
            v-model="node.value"
            searchable
            :multiple="node.multiSelect">
            <bk-option v-for="option in node.choiceList"
              :key="option.key"
              :id="option.key"
              :name="option.name">
            </bk-option>
          </bk-select>
        </template>
        <template v-else>
          <bk-input :ext-cls="'bk-form-style'"
            :type="node.type === 'INT' ? 'number' : 'text'"
            :placeholder="$t(`m.treeinfo['请输入关系值']`)"
            v-model="node.value">
          </bk-input>
        </template>
      </template>
      <template v-else-if="node.type === 'DATE' || node.type === 'DATETIME'">
        <bk-date-picker
          :ext-cls="'bk-form-style'"
          :type="node.type === 'DATETIME' ? 'datetime' : 'date'"
          v-model="node.value">
        </bk-date-picker>
      </template>
      <template v-else>
        <bk-input :ext-cls="'bk-form-style'"
          :type="node.type === 'INT' ? 'number' : 'text'"
          :placeholder="$t(`m.treeinfo['请输入关系值']`)"
          v-model="node.value">
        </bk-input>
      </template>
      <div class="bk-between-operat">
        <i class="bk-itsm-icon icon-flow-add" @click="addNode(node, nodeIndex)"></i>
        <i class="bk-itsm-icon icon-flow-reduce"
          :class="{ 'bk-no-delete': listInfo.length === 1 }"
          @click="deleteNode(node, nodeIndex)"></i>
      </div>
    </div>
  </div>
</template>
<script>
  import { errorHandler } from '../../../../../utils/errorHandler.js';
  import apiFieldsWatch from '../../../../commonMix/api_fields_watch.js';

  export default {
    name: 'hiddenConditions',
    mixins: [apiFieldsWatch],
    props: {
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
      formInfo: {
        type: Object,
        default() {
          return {};
        },
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
      addOrigin: {
        type: Object,
        default() {
          return {
            isOther: false,
            addOriginInfo: {},
          };
        },
      },
    },
    data() {
      return {
        isLoading: false,
        listInfo: [],
        conditionType: 'and',
        fieldList: [],
        checkStatus: false,
      };
    },
    computed: {
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
    },
    mounted() {
      this.getFrontNodesList();
    },
    methods: {
      getFrontNodesList() {
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
        this.isLoading = true;
        this.$store.dispatch(url, params).then((res) => {
          this.frontNodesList = res.data;
          this.initData();
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isLoading = false;
          });
      },
      initData() {
        // 初始化listInfo的数据
        this.listInfo = [];
        if (this.formInfo.show_conditions.expressions && this.formInfo.show_conditions.expressions.length) {
          this.formInfo.show_conditions.expressions.forEach((item) => {
            this.frontNodesList.forEach((node) => {
              if (node.key === item.key) {
                const nodeStatus = (node.type === 'MULTISELECT' || node.type === 'CHECKBOX' || node.type === 'MEMBERS' || node.type === 'TREESELECT');
                const betweenList = this.checkBetweenList(node.type);
                this.listInfo.push({
                  condition: item.condition,
                  key: item.key,
                  value: nodeStatus ? item.value.split(',') : item.value,
                  choiceList: node.choice,
                  type: item.type,
                  multiSelect: nodeStatus,
                  betweenList,
                });
              }
            });
          });
          this.conditionType = this.formInfo.show_conditions.type;
        } else {
          this.listInfo = [
            {
              condition: '',
              key: '',
              value: '',
              choiceList: '',
              type: 'STRING',
              multiSelect: false,
              betweenList: this.checkBetweenList('STRING'),
            },
          ];
          this.conditionType = 'and';
        }
        // 初始化fieldList数据
        this.fieldList = [];
        this.frontNodesList.forEach((item) => {
          // 去除掉当前的字段，字段类型为CUSTOMTABLE，FILE，RICHTEXT，TABLE，DATETIMERANGE，MEMBERS
          const exceptList = ['CUSTOMTABLE', 'FILE', 'RICHTEXT', 'TABLE', 'DATETIMERANGE', 'MEMBERS'];
          if (item.key !== this.formInfo.key && !exceptList.some(node => node === item.type)) {
            this.fieldList.push(item);
          }
        });
        this.fieldList.forEach((item) => {
          if (item.source_type === 'RPC') {
            this.getRpcData(item);
          }
        });
        this.isNecessaryToWatch({ fields: this.fieldList }, 'workflow');
      },
      getRpcData(item) {
        this.$store.dispatch('apiRemote/getRpcData', item).then((res) => {
          item.choice = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      checkBetweenList(typeValue) {
        const listOne = ['MULTISELECT', 'CHECKBOX', 'MEMBERS', 'TREESELECT'];
        const listTwo = ['DATE', 'DATETIME', 'DATETIMERANGE', 'INT'];
        let betweenList = [];
        if (listOne.some(type => type === typeValue)) {
          betweenList = this.globalChoise.methods.filter(methods => (methods.typeName === 'issuperset' || methods.typeName === 'notissuperset'));
        } else if (listTwo.some(type => type === typeValue)) {
          betweenList = this.globalChoise.methods.filter(methods => (methods.typeName !== 'issuperset' && methods.typeName !== 'notissuperset'));
        } else {
          betweenList = this.globalChoise.methods.filter(methods => (methods.typeName === '==' || methods.typeName === '!='));
        }
        return betweenList;
      },
      clearCondition() {
        this.listInfo = [
          {
            condition: '',
            key: '',
            value: '',
            choiceList: '',
            type: 'STRING',
            multiSelect: false,
            betweenList: this.checkBetweenList('STRING'),
          },
        ];
      },
      changeName(...value) {
        const checkItem = this.fieldList.filter(item => item.key === value[0])[0];
        const nodeStatus = (checkItem.type === 'MULTISELECT' || checkItem.type === 'CHECKBOX' || checkItem.type === 'MEMBERS' || checkItem.type === 'TREESELECT');
        const betweenList = this.checkBetweenList(checkItem.type);
        value[2].type = checkItem.type;
        value[2].value = nodeStatus ? [] : '';
        value[2].betweenList = betweenList;
        value[2].condition = '';
        if (checkItem.type === 'SELECT' || checkItem.type === 'MULTISELECT' || checkItem.type === 'RADIO' || checkItem.type === 'CHECKBOX' || checkItem.type === 'MEMBERS' || checkItem.type === 'TREESELECT') {
          value[2].choiceList = [];
          checkItem.choice.forEach((node) => {
            value[2].choiceList.push({
              key: node.key,
              name: node.name,
            });
          });
          value[2].multiSelect = nodeStatus;
        } else {
          value[2].choiceList = '';
        }
      },
      // 新增字段条件组
      addNode(node, index) {
        const value = {
          condition: '',
          key: '',
          value: '',
          choiceList: '',
          type: 'STRING',
          multiSelect: false,
          betweenList: this.checkBetweenList('STRING'),
        };
        this.listInfo.splice(index + 1, 0, value);
      },
      deleteNode(node, index) {
        if (this.listInfo.length === 1) {
          return;
        }
        this.listInfo.splice(index, 1);
      },
      checkList() {
        this.checkStatus = this.listInfo.some(item => (!item.key || !item.condition || (Array.isArray(item.value) ? !item.value.length : !item.value)));
        return this.checkStatus;
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../../../scss/mixins/clearfix.scss';

    .bk-hidden-conditions {
        padding: 16px 22px;
        border: 1px solid #DCDEE5;
        background-color: #FAFBFD;
        position: relative;
    }

    .bk-between-form {
        @include clearfix;
        margin-top: 10px;
        display: flex;
        align-items: center;
    }

    .bk-error-msg {
        color: #ff5656;
        font-size: 12px;
        line-height: 19px;
        text-align: left;
    }

    .bk-between-operat {
        margin-left: 16px;
        line-height: 32px;
        font-size: 18px;

        .bk-itsm-icon {
            color: #C4C6CC;
            margin-right: 6px;
            cursor: pointer;

            &:hover {
                color: #979BA5;
            }
            &:last-child {
                margin-right: 0;
            }
        }

        .bk-no-delete {
            color: #DCDEE5;
            cursor: not-allowed;

            &:hover {
                color: #DCDEE5;
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
</style>
