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
  <div class="bk-add-trigger">
    <div class="bk-service-name">
      <h1><span class="is-outline"></span>{{ $t('m.trigger["基础信息"]') }}</h1>
    </div>
    <div class="bk-trigger-basic">
      <bk-form :label-width="170"
        :model="formData"
        :ext-cls="'bk-basic-form'"
        form-type="vertical"
        :rules="rules"
        ref="triggerBasic">
        <bk-form-item :label="$t(`m.trigger['触发器名称']`)"
          data-test-id="trigger-input-name"
          :required="true"
          :property="'name'">
          <bk-input v-model="formData.name" :placeholder="$t(`m.trigger['请输入触发器名称']`)"></bk-input>
        </bk-form-item>
        <bk-form-item :label="$t(`m.trigger['是否启用']`)">
          <bk-switcher data-test-id="triggers_switcher_isUseTrigger" v-model="formData.is_enabled" size="small"></bk-switcher>
        </bk-form-item>
        <!-- <template v-if="!originInfoToTrigger.id">
          <bk-form-item :label="$t(`m.trigger['基础模型']`)">
            <bk-select v-model="formData.moduleType"
              searchable
              :loading="formData.variableLoading"
              :disabled="formData.moduleTypeDisabled"
              :font-size="'medium'"
              @selected="giveTableVariables">
              <bk-option v-for="option in moduleTypes"
                :key="option.id"
                :id="option.id"
                :name="option.name">
              </bk-option>
            </bk-select>
          </bk-form-item>
        </template> -->
        <bk-form-item :label="$t(`m.trigger['触发器描述']`)">
          <bk-input
            :placeholder="$t(`m.trigger['请输入触发器描述']`)"
            :type="'textarea'"
            :rows="3"
            :maxlength="100"
            v-model="formData.desc">
          </bk-input>
        </bk-form-item>
      </bk-form>
      <!-- <div class="bk-basic-type" v-bk-clickoutside="handleClickOutSide">
        <p class="bk-type-icon"><i class="bk-itsm-icon" :class="[iconInfo.key]"></i></p>
        <p class="bk-type-name">{{iconInfo.name}}</p>
        <div class="bk-type-change"
          :class="{ 'bk-show': iconInfo.status }"
          data-test-id="trigger_div_changeType"
          @click="handleClick">
          <span>{{$t(`m.trigger['点击更换']`)}}</span>
        </div>
        <ul class="bk-icon-list" v-if="iconInfo.status">
          <li v-for="(item, index) in iconList"
            :key="index"
            v-bk-tooltips="item.name"
            @click="changeIcon(item)">
            <i class="bk-itsm-icon" :class="[item.key]" style="font-size: 24px"></i>
          </li>
        </ul>
      </div> -->
    </div>
    <div class="bk-service-name">
      <h1><span class="is-outline"></span>{{$t(`m.trigger['触发机制']`)}}</h1>
    </div>
    <div class="bk-trigger-made">
      <bk-form :label-width="170"
        :model="formData"
        form-type="vertical"
        :rules="rules"
        ref="triggerMade">
        <bk-form-item :label="$t(`m.trigger['触发事件']`)"
          data-test-id="trigger-select-triggerEvent"
          :required="true"
          :property="'signal'"
          style="width: 300px;">
          <bk-select data-test-id="triggers_select_choiceEvent" v-model="formData.signal" :placeholder="$t(`m.trigger['请选择触发事件']`)">
            <bk-option-group
              v-for="(group, index) in triggerEventList"
              :name="group.name"
              :key="index">
              <bk-option v-for="option in group.children"
                :key="option.key"
                :id="option.key"
                :name="option.name">
              </bk-option>
            </bk-option-group>
          </bk-select>
        </bk-form-item>
        <bk-form-item
          data-test-id="trigger-div-triggerRules"
          :label="$t(`m.trigger['触发规则']`)"
          :required="true">
          <div v-bkloading="{ isLoading: contentLoading }" style="min-height: 300px;">
            <div class="bk-trigger-rule mb10" v-for="(item, index) in rulesList" :key="index">
              <div class="bk-rule-title">
                <div style="float: left; margin-right: 10px;">
                  <i class="bk-icon icon-down-shape icon-cus" v-if="item.showContent" @click="showContent(item)"></i>
                  <i class="bk-icon icon-right-shape icon-cus" v-else @click="showContent(item)"></i>
                </div>
                <!-- 可以修改触发规则名称 -->
                <div class="bk-name-input"
                  v-if="item.nameChange">
                  <bk-input style="width: 260px; display: inline-block;"
                    :clearable="true"
                    v-model="item.name">
                  </bk-input>
                  <span class="bk-input-submit" @click.stop="handleClickName(item, 'submit')">{{$t(`m.trigger['确认']`)}}</span>
                  <span class="bk-input-submit" @click.stop="handleClickName(item, 'close')">{{$t(`m.trigger['取消']`)}}</span>
                </div>
                <span v-else
                  class="bk-title-name"
                  @click.stop="changeName(item)">
                  {{ item.name || ($t(`m.trigger['规则']`) + '-' + (index + 1)) }}
                </span>
                <!-- 删除 -->
                <template v-if="rulesList.length !== 1">
                  <i class="bk-icon icon-close icon-nodelete"
                    @click.stop="deleteRule(index)"></i>
                </template>
                <template v-else>
                  <i class="bk-icon icon-close icon-nodelete"
                    data-test-id="trigger_i_closeTriggerRule"
                    v-bk-tooltips.top-start="$t(`m.trigger['规则不能为空']`)"></i>
                </template>
                <!-- 条件触发开关 -->
                <div class="bk-condition-switch">
                  <span class="mr5">{{$t(`m.trigger['条件触发']`)}}</span>
                  <bk-switcher data-test-id="triggers_switcher_conditionTriggered" v-model="item.triggerStatus" size="small"></bk-switcher>
                </div>
              </div>
              <div v-show="item.showContent">
                <!-- 触发条件 -->
                <trigger-condition v-if="item.triggerStatus"
                  :trigger-rules="item.triggerRules">
                </trigger-condition>
                <!-- 响应条件 -->
                <response-condition
                  :signal="formData.signal"
                  :response-way-list="responseWayList"
                  :response-list="item.responseList">
                </response-condition>
              </div>
            </div>
            <p class="bk-add-rules" @click="addRule">
              <i class="bk-icon icon-plus-circle"></i><span data-test-id="trigger_span_addTriggerRules">{{$t(`m.trigger['添加规则']`)}}</span>
            </p>
          </div>
        </bk-form-item>
      </bk-form>
    </div>
    <div class="bk-submit-trigger">
      <bk-button :theme="'primary'"
        data-test-id="trigger_button_submitTrigger"
        :title="$t(`m.trigger['确认']`)"
        :disabled="btnLoading"
        class="mr10"
        @click="submitTrigger(false)">
        {{$t(`m.trigger['确认']`)}}
      </bk-button>
      <bk-button :theme="'default'"
        data-test-id="trigger_button_submitTrigger"
        :title="$t(`m.trigger['保持草稿']`)"
        :disabled="btnLoading"
        class="mr10"
        @click="submitTrigger(true)">
        {{$t(`m.trigger['保持草稿']`)}}
      </bk-button>
      <bk-button :theme="'default'"
        data-test-id="trigger_button_KeepDraft"
        :disabled="btnLoading"
        :title="$t(`m.trigger['取消']`)"
        @click="closeTrigger">
        {{$t(`m.trigger['取消']`)}}
      </bk-button>
    </div>
  </div>
</template>
<script>
  import commonMix from '../../commonMix/common.js';
  import triggerCondition from './components/triggerCondition.vue';
  import responseCondition from './components/responseCondition.vue';
  import { errorHandler } from '../../../utils/errorHandler.js';

  export default {
    name: 'addTrigger',
    components: {
      triggerCondition,
      responseCondition,
    },
    mixins: [commonMix],
    props: {
      projectId: String,
      triggerInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      originInfoToTrigger: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        contentLoading: false,
        formData: {
          name: '',
          is_enabled: true,
          desc: '',
          signal: '',
          // moduleType: '',
          moduleTypeDisabled: false,
          variableLoading: false,
        },
        triggerEventList: [],
        // icon数据
        iconList: [
          { key: 'icon-icon-notice-new', name: '', typeName: 'message' },
          { key: 'icon-icon-user-new', name: '', typeName: 'user' },
          { key: 'icon-icon-status-new', name: '', typeName: 'status' },
          { key: 'icon-icon-api-new', name: '', typeName: 'api' },
        ],
        iconInfo: {
          status: false,
          key: 'icon-icon-notice-new',
          name: '',
          typeName: '',
        },
        // 响应事件list
        responseWayList: [],
        rulesList: [],
        ruleItem: {
          name: '',
          historyName: '',
          nameChange: false,
          triggerStatus: false,
          showContent: true,
          triggerRules: {
            type: 'all',
            list: [
              {
                type: 'all',
                itemList: [
                  {
                    key: '',
                    condition: '',
                    value: '',
                    conditionList: [],
                    type: 'STRING',
                  },
                ],
              },
            ],
          },
          responseList: [{
            way: '',
            wayInfo: {},
            performData: {
              runMode: 'BACKEND',
              displayName: '',
              repeat: 'one',
            },
            isLoading: false,
          }],
        },
        // 保存返回的数据
        backInfo: {
          responseList: [],
          triggerInfo: {},
        },
        btnLoading: false,
        triggerAllRules: [],
        // 校验规则
        rules: {},
        // 公共触发器可关联基础模型
        moduleTypes: [],
      };
    },
    computed: {
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
    },
    mounted() {
      this.initData();
      this.rules.name = this.checkCommonRules('name').name;
      this.rules.signal = this.checkCommonRules('select').select;
    },
    methods: {
      async initData() {
        // 初始化默认存在一个rulesList数据
        const valueItem = JSON.parse(JSON.stringify(this.ruleItem));
        this.rulesList.push(valueItem);
        // icon数据
        this.iconList.forEach(item => {
          switch (item.key) {
            case 'icon-icon-notice-new':
              item.name = this.globalChoise.trigger_icon.find(triggerItem => triggerItem.typeName === 'message').name;
              break;
            case 'icon-icon-user-new':
              item.name = this.globalChoise.trigger_icon.find(triggerItem => triggerItem.typeName === 'user').name;
              break;
            case 'icon-icon-status-new':
              item.name = this.globalChoise.trigger_icon.find(triggerItem => triggerItem.typeName === 'status').name;
              break;
            case 'icon-icon-api-new':
              item.name = this.globalChoise.trigger_icon.find(triggerItem => triggerItem.typeName === 'api').name;
              break;
          }
        });
        this.iconInfo.key = this.iconList[0].key;
        this.iconInfo.name = this.iconList[0].name;
        this.iconInfo.typeName = this.iconList[0].typeName;
        // 触发事件数据
        this.triggerEventList = [];
        for (const key in this.globalChoise.trigger_signals) {
          const valueObj = {
            key,
            name: this.globalChoise.trigger_categories[key],
            children: [],
          };
          for (const itemKey in this.globalChoise.trigger_signals[key]) {
            valueObj.children.push({
              key: itemKey,
              name: this.globalChoise.trigger_signals[key][itemKey],
            });
          }
          this.triggerEventList.push(valueObj);
        }
        // 统一管理新增触发器来源
        if (this.originInfoToTrigger.id) {
          // 保留整个触发器内使用的流程信息
          const id = this.originInfoToTrigger.sender;
          const type = this.originInfoToTrigger.type;
          const params = {
            workflow: this.originInfoToTrigger.id,
          };
          if (type === 'task_schemas') {
            params.stage = this.originInfoToTrigger.stage;
            delete params.workflow;
          }
          if (type === 'states') {
            params.state = this.originInfoToTrigger.sender;
          }
          // 获取对应来源的变量
          await this.$store.dispatch('trigger/getTriggerVariables', { id, type, params }).then(res => {
            this.$store.commit('trigger/changeTriggerVariables', res.data);
          });
          // 只保留对应来源的父选项
          this.triggerEventList = this.triggerEventList.filter(item => item.key === this.originInfoToTrigger.filter);
          // if (this.originInfoToTrigger.filter === 'TASK') {
          // 任务来源时区分三种状态
          this.triggerEventList[0].children = this.triggerEventList[0].children.filter(child => this.originInfoToTrigger.signal.indexOf(child.key) !== -1);
          // }
          if (this.triggerEventList.length === 1 && this.triggerEventList[0].children.length === 1) {
            this.formData.signal = this.triggerEventList[0].children[0].key;
          }
        } else {
          this.$store.commit('trigger/changeTriggerVariables', this.globalChoise.ticket_variables);
        }
        // 获取数据
        this.getModuleTypes();
        await this.getResponseList();
        // 修改数据时渲染数据
        if (this.triggerInfo.id) {
          this.contentLoading = true;
          this.getData();
        }
      },
      // 基础模型类型
      getModuleTypes() {
        const params = {
          all: true,
        };
        this.$store.dispatch('basicModule/get_tables', params).then(res => {
          this.moduleTypes = res.data;
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      // 获取数据，初始化渲染
      async getData() {
        // icon 渲染
        const iconItem = this.iconList.find(triggerItem => triggerItem.typeName === this.triggerInfo.icon);
        this.iconInfo.key = iconItem.key;
        this.iconInfo.name = iconItem.name;
        this.iconInfo.typeName = iconItem.typeName;
        // 基本信息
        this.formData.name = this.triggerInfo.name;
        this.formData.is_enabled = this.triggerInfo.is_enabled;
        this.formData.desc = this.triggerInfo.desc;
        this.formData.signal = this.triggerInfo.signal;
        if (this.triggerInfo.source_table_id) {
          // this.formData.moduleType = this.triggerInfo.source_table_id;
          this.formData.moduleTypeDisabled = true;
          this.giveTableVariables(this.triggerInfo.source_table_id);
        }
        await this.getTriggerRules();
        const triggerRuleList = this.triggerAllRules.filter(item => item.trigger_id === this.triggerInfo.id);
        // push多个ruleItem的数据
        this.rulesList = [];
        for (let i = 0; i < triggerRuleList.length; i++) {
          const valueItem = JSON.parse(JSON.stringify(this.ruleItem));
          // 触发条件
          valueItem.triggerStatus = triggerRuleList[i].by_condition || !!triggerRuleList[i].condition;
          if (valueItem.triggerStatus) {
            valueItem.triggerRules = this.conditionValue(triggerRuleList[i].condition);
          }
          valueItem.triggerRules.id = triggerRuleList[i].id;
          // 响应事件
          await this.responseValue(triggerRuleList[i].action_schemas, valueItem);
        }
        // 触发条件
        this.contentLoading = false;
      },
      // 触发条件的显示
      conditionValue(itemInfo) {
        const triggerRule = {
          type: '',
          list: [],
        };
        for (const key in itemInfo) {
          triggerRule.type = key;
          itemInfo[key].forEach(rule => {
            const ruleItem = {};
            for (const ruleKey in rule) {
              ruleItem.type = ruleKey;
              ruleItem.itemList = [];
              rule[ruleKey].forEach(ruleKeyItem => {
                const multiKey = ['CHECKBOX', 'MULTISELECT', 'MEMBERS', 'MULTI_MEMBERS', 'MEMBER'];
                const ruleKeyInfo = {
                  key: ruleKeyItem.key,
                  condition: ruleKeyItem.operator,
                  meta: ruleKeyItem.meta,
                  value: multiKey.some(multi => multi === ruleKeyItem.field_type) ? ruleKeyItem.value.split(',') : ruleKeyItem.value,
                  conditionList: [],
                  type: ruleKeyItem.field_type,
                };
                ruleKeyInfo.conditionList = this.globalChoise.trigger_methods[ruleKeyItem.field_type.toLowerCase()];
                ruleItem.itemList.push(ruleKeyInfo);
              });
            }
            triggerRule.list.push(ruleItem);
          });
        }
        return triggerRule;
      },
      async responseValue(itemInfo, valueItem) {
        // 通过action_schemas的值去获取响应事件的内容
        const params = {
          id__in: itemInfo.join(','),
        };
        await this.$store.dispatch('trigger/getResponseListById', params).then((res) => {
          const resBack = res.data;
          // 规则名称
          valueItem.responseList = [];
          valueItem.name = resBack[0].name;
          resBack.forEach(async item => {
            const responseItem = {
              id: item.id,
              way: '',
              wayInfo: {},
              performData: {
                runMode: 'BACKEND',
                displayName: '',
                repeat: 'one',
              },
              isLoading: false,
            };
            // 响应事件内容
            responseItem.way = item.component_type;
            responseItem.wayInfo = JSON.parse(JSON.stringify(this.responseWayList.find(response => response.key === item.component_type)));
            // 赋值wayInfo的内容(区分普通节点和api节点)
            if (responseItem.way === 'api') {
              responseItem.wayInfo.field_schema.forEach(field => {
                item.params.forEach(itemFiled => {
                  if (field.key === itemFiled.key) {
                    this.$set(field, 'value', itemFiled.value);
                  }
                });
              });
            } else {
              responseItem.wayInfo.field_schema.forEach(field => {
                // 区分嵌套关系数据
                if (field.type === 'SUBCOMPONENT') {
                  item.params.forEach(itemFiled => {
                    if (itemFiled.key === field.key) {
                      field.sub_components.forEach(subField => {
                        itemFiled.sub_components.forEach(subItemField => {
                          if (subItemField.key === subField.key) {
                            subField.checked = true;
                            // 字段赋值
                            subField.field_schema.forEach(subFieldField => {
                              subItemField.params.forEach(subItemFieldParams => {
                                if (subFieldField.key === subItemFieldParams.key) {
                                  subFieldField.referenceType = subItemFieldParams.ref_type;
                                  subFieldField.value = subItemFieldParams.value;
                                }
                              });
                            });
                          }
                        });
                      });
                    }
                  });
                } else {
                  item.params.forEach(itemFiled => {
                    if (field.key === itemFiled.key) {
                      this.$set(field, 'value', itemFiled.value);
                      this.$set(field, 'ref_type', itemFiled.ref_type);
                    }
                  });
                }
              });
            }
            // 执行方式内容
            responseItem.performData.runMode = item.operate_type;
            responseItem.performData.displayName = item.display_name;
            responseItem.performData.repeat = item.can_repeat ? 'more' : 'one';
            valueItem.responseList.push(responseItem);
          });
          this.rulesList.push(valueItem);
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      // 初始化时，获取modify_field的choice
      async getResponseFields(fieldKey) {
        const params = {
          source_uri: fieldKey.source_uri,
          trigger_source_id: this.originInfoToTrigger.id,
          trigger_source_type: 'workflow',
        };
        await this.$store.dispatch('apiRemote/getRpcData', params).then(res => {
          fieldKey.choice = res.data.map(field => ({
            ...field,
            showFeild: true,
            value: '',
          }));
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      // 更换icon
      handleClick() {
        this.iconInfo.status = true;
      },
      handleClickOutSide() {
        this.iconInfo.status = false;
      },
      changeIcon(item) {
        this.iconInfo.key = item.key;
        this.iconInfo.name = item.name;
        this.iconInfo.typeName = item.typeName;
        this.iconInfo.status = false;
      },
      // 新增响应条件
      addRule() {
        const valueItem = JSON.parse(JSON.stringify(this.ruleItem));
        this.rulesList.push(valueItem);
      },
      deleteRule(index) {
        if (this.rulesList.length === 1) {
          return;
        }
        this.rulesList.splice(index, 1);
      },
      // 修改name
      changeName(item) {
        item.historyName = item.name;
        item.nameChange = true;
      },
      handleClickName(item, type) {
        item.nameChange = false;
        if (type === 'close') {
          item.name = item.historyName;
        }
      },
      showContent(item) {
        item.showContent = !item.showContent;
      },
      // 保存、取消、草稿
      submitTrigger(type) {
        this.$refs.triggerBasic.validate().then(() => {
          this.$refs.triggerMade.validate().then(() => {
            if (this.checkInfo()) {
              return;
            }
            // 内部校验
            const params = {
              name: this.formData.name,
              source_type: 'basic',
              source_id: 0,
              signal: this.formData.signal,
              // source_table_id: this.formData.moduleType,
              sender: 0,
              is_draft: type,
              is_enabled: this.formData.is_enabled,
              icon: this.iconInfo.typeName,
              desc: this.formData.desc,
              project_key: this.$store.state.project.id,
            };
            if (this.originInfoToTrigger.id) {
              params.source_type = this.originInfoToTrigger.source;
              params.sender = this.originInfoToTrigger.id;
              params.source_id = this.originInfoToTrigger.id;
              params.sender = this.originInfoToTrigger.sender;
            }
            if (this.projectId) {
              params.project_key = this.projectId;
            }
            if (this.triggerInfo.id) {
              this.putTrigger(params);
            } else {
              this.creatTrigger(params);
            }
          });
        });
      },
      checkInfo() {
        let backStatus = false;
        this.rulesList.forEach(item => {
          // 当触发条件开关开时检查条件必填
          if (item.triggerStatus) {
            item.triggerRules.list.forEach(firstItem => {
              firstItem.itemList.forEach(secondItem => {
                if (secondItem.condition === 'non_empty') {
                  item.triggerRules.checkStatus = secondItem.key === '' || secondItem.value === '';
                } else {
                  item.triggerRules.checkStatus = secondItem.key === '' || secondItem.condition === '' || secondItem.value === '';
                }
              });
            });
          }
          // 响应事件
          item.responseList.forEach(responseItem => {
            // 动作名称
            this.$set(responseItem, 'wayStatus', !responseItem.way);
            // 内容
            if (responseItem.wayInfo.field_schema) {
              // 这里区分三种
              if (responseItem.wayInfo.key === 'api') {
                responseItem.wayInfo.field_schema.forEach(schema => {
                  if (schema.key === 'api_source') {
                    responseItem.contentStatus = responseItem.contentStatus ? responseItem.contentStatus : !schema.apiId;
                  } else {
                    schema.apiContent.bodyTableData.forEach(apiValue => {
                      // 是否必填 is_necessary
                      if (apiValue.type !== 'array' && apiValue.type !== 'object' && apiValue.is_necessary) {
                        responseItem.contentStatus = responseItem.contentStatus ? responseItem.contentStatus : (apiValue.source_type === 'CUSTOM' ? apiValue.value === '' : apiValue.value_key === '');
                      }
                    });
                  }
                });
              } else {
                responseItem.wayInfo.field_schema.forEach(schema => {
                  if (schema.type === 'SUBCOMPONENT' && schema.sub_components && schema.sub_components.length) {
                    // 至少勾选一个项
                    responseItem.contentStatus = !schema.sub_components.some(subSchema => subSchema.checked);
                    // 勾选的项内部字段做必填校验
                    if (!responseItem.contentStatus) {
                      schema.sub_components.forEach(subItemSchema => {
                        if (subItemSchema.checked) {
                          subItemSchema.field_schema.forEach(fieldSchema => {
                            if (fieldSchema.required) {
                              if (fieldSchema.type === 'MEMBERS' || fieldSchema.type === 'MULTI_MEMBERS') {
                                responseItem.contentStatus = responseItem.contentStatus ? responseItem.contentStatus : fieldSchema.value.some(schemaMem => (Array.isArray(schemaMem.value) ? !schemaMem.value.length : !schemaMem.value));
                              } else {
                                responseItem.contentStatus = responseItem.contentStatus ? responseItem.contentStatus : !fieldSchema.value;
                              }
                            }
                          });
                        }
                      });
                    }
                  } else {
                    // 区分人员选择
                    if (schema.required) {
                      if (schema.type === 'MEMBERS' || schema.type === 'MULTI_MEMBERS') {
                        responseItem.contentStatus = responseItem.contentStatus ? responseItem.contentStatus : schema.value.some(schemaMem => (Array.isArray(schemaMem.value) ? !schemaMem.value.length : !schemaMem.value));
                      } else {
                        responseItem.contentStatus = responseItem.contentStatus ? responseItem.contentStatus : (schema.key === 'field_value' ? !(schema.itemInfo[0].value || schema.itemInfo[0].val) : !schema.value);
                      }
                    }
                  }
                });
              }
              // 执行方式的校验也由contentStatus来控制
              if (responseItem.performData.runMode === 'MANUAL' && !responseItem.contentStatus) {
                responseItem.contentStatus = !responseItem.performData.displayName;
              }
            }
          });
          backStatus = item.triggerRules.checkStatus || item.responseList.some(responseItem => (responseItem.contentStatus || responseItem.wayStatus));
        });
        return backStatus;
      },
      closeTrigger() {
        this.$emit('closeTrigger');
      },
      // 创建一个触发器
      creatTrigger(params) {
        this.btnLoading = true;
        this.$store.dispatch('trigger/createTriggerRule', params).then((res) => {
          this.backInfo.triggerInfo = res.data;
          // 响应条件
          const value = this.responseParams();
          this.createRespond(value);
        })
          .catch(res => {
            errorHandler(res, this);
            this.btnLoading = false;
          })
          .finally(() => {

          });
      },
      // 修改一个触发器
      putTrigger(params) {
        this.btnLoading = true;
        const id = this.triggerInfo.id;
        this.$store.dispatch('trigger/putTriggerRule', { params, id }).then((res) => {
          this.backInfo.triggerInfo = res.data;
          // 响应条件
          const value = this.responseParams();
          this.createRespond(value);
        })
          .catch(res => {
            errorHandler(res, this);
            this.btnLoading = false;
          })
          .finally(() => {

          });
      },
      // 创建多个触发器规则（响应条件）
      createRespond(value) {
        const params = value;
        const id = this.originInfoToTrigger.id;
        this.$store.dispatch('trigger/createRespond', { id, params }).then((res) => {
          this.backInfo.responseList = res.data;
          // 触发条件
          this.createTriggerCondition();
        })
          .catch(res => {
            errorHandler(res, this);
            this.btnLoading = false;
          })
          .finally(() => {

          });
      },
      responseParams() {
        const params = [];
        this.rulesList.forEach(item => {
          item.responseList.forEach(response => {
            const paramsItem = {};
            // 如果存在ID则将ID带上（请求由此变成更新数据）
            if (response.id) {
              paramsItem.id = response.id;
            }
            // 执行方式
            paramsItem.name = item.name;
            paramsItem.display_name = response.performData.displayName;
            paramsItem.operate_type = response.performData.runMode;
            paramsItem.can_repeat = response.performData.repeat === 'more';
            // 内容
            paramsItem.component_type = response.wayInfo.key;
            paramsItem.params = [];
            // 区分API传值和普通传值的
            if (response.wayInfo.key === 'api') {
              paramsItem.params = this.responseApiInfo(response);
            } else {
              response.wayInfo.field_schema.forEach(field => {
                // 区分嵌套关系数据
                if (field.type === 'SUBCOMPONENT') {
                  const subContent = {
                    key: field.key,
                    sub_components: [],
                  };
                  field.sub_components.forEach(subItem => {
                    if (subItem.checked) {
                      const subInfo = {
                        key: subItem.key,
                        params: [],
                      };
                      subItem.field_schema.forEach(subField => {
                        const paramsContent = {
                          key: subField.key,
                          value: this.formattingValue(subField),
                          ref_type: subField.referenceType,
                        };
                        subInfo.params.push(paramsContent);
                      });
                      subContent.sub_components.push(subInfo);
                    }
                  });
                  paramsItem.params.push(subContent);
                } else {
                  const paramsContent = {
                    key: field.key,
                    value: this.formattingValue(field),
                    ref_type: field.referenceType,
                  };
                  paramsItem.params.push(paramsContent);
                }
              });
            }
            // 将数据push到params里面
            params.push(paramsItem);
          });
        });
        return params;
      },
      responseApiInfo(response) {
        const valueList = [];
        response.wayInfo.field_schema.forEach(field => {
          if (field.key === 'api_source') {
            valueList.push({
              key: field.key,
              value: field.apiId,
            });
          } else {
            const valueInfo = {
              key: field.key,
              value: {},
            };
            valueInfo.value = this.treeToJson(field.apiContent.bodyTableData.filter(item => (!item.level)));
            // 使用递归来取值
            // const checkInfo = (arr, parentKey) => {
            //     arr.forEach(itemArr => {
            //         field.apiContent.bodyTableData.forEach(apiField => {
            //             if (itemArr.key === apiField.key) {
            //                 const value = {
            //                     is_leaf: ((apiField.type !== 'object') && (apiField.type !== 'array')),
            //                     ref_type: apiField.source_type === 'CUSTOM' ? 'custom' : 'reference',
            //                     value: apiField.source_type === 'CUSTOM' ? apiField.value : apiField.value_key
            //                 }
            //                 if (!parentKey) {
            //                     parentKey = {}
            //                 }
            //                 parentKey[apiField.key] = value
            //             }
            //         })
            //         if (itemArr.children && itemArr.children.length) {
            //             checkInfo(itemArr.children, parentKey[itemArr.key])
            //         }
            //     })
            // }
            // checkInfo(field.apiContent.treeDataList[0].children, valueInfo.value)
            valueList.push(valueInfo);
          }
        });
        return valueList;
      },
      treeToJson(listData) {
        const jsonDataDict = {};
        const treeToJsonStep = function (jsonDataDict, item, level, lastType) {
          if (!item.key) {
            return;
          }
          if (item.type === 'array') {
            const baseItem = [];
            if (lastType === 'array') {
              jsonDataDict.push(baseItem);
              for (const j in item.children) {
                treeToJsonStep(jsonDataDict[jsonDataDict.length - 1], item.children[j], 1, 'array');
              }
            }
            if (lastType === 'object') {
              const baseItem = {};
              baseItem[item.key] = [];
              Object.assign(jsonDataDict, baseItem);
              for (const j in item.children) {
                treeToJsonStep(jsonDataDict[item.key], item.children[j], 1, 'array');
              }
            }
          } else if (item.type === 'object') {
            const baseItem = {};
            if (lastType === 'array') {
              jsonDataDict.push(baseItem);
              for (const j in item.children) {
                treeToJsonStep(jsonDataDict[jsonDataDict.length - 1], item.children[j], 1, 'object');
              }
            }
            if (lastType === 'object') {
              baseItem[item.key] = {};
              Object.assign(jsonDataDict, baseItem);
              for (const j in item.children) {
                treeToJsonStep(jsonDataDict[item.key], item.children[j], 1, 'object');
              }
            }
          } else {
            if (item.type === 'number') {
              item.value = Number(item.value);
            }
            if (lastType === 'array') {
              const baseItem = {
                is_leaf: ((item.type !== 'object') && (item.type !== 'array')),
                ref_type: item.source_type === 'CUSTOM' ? 'custom' : 'reference',
                value: item.source_type === 'CUSTOM' ? item.value : item.value_key,
              };
              // item.source_type === 'CUSTOM' ? item.value
              //     : `\$\{params\_${item.value_key}\}`
              jsonDataDict.push(baseItem);
            }
            if (lastType === 'object') {
              const baseItem = {};
              baseItem[item.key] = {
                is_leaf: ((item.type !== 'object') && (item.type !== 'array')),
                ref_type: item.source_type === 'CUSTOM' ? 'custom' : 'reference',
                value: item.source_type === 'CUSTOM' ? item.value : item.value_key,
              };
              // item.source_type === 'CUSTOM' ? item.value
              //     : `\$\{params\_${item.value_key}\}`
              Object.assign(jsonDataDict, baseItem);
            }
          }
        };
        for (const i in listData) {
          treeToJsonStep(jsonDataDict, listData[i], 0, 'object');
        }
        return jsonDataDict;
      },
      formattingValue(item) {
        let backValue = '';
        if (item.key === 'receivers' || item.type === 'MEMBERS' || item.type === 'MEMBER') {
          // 收件人做特殊格式化处理
          backValue = [];
          item.value.forEach(receiver => {
            const valueInfo = {
              ref_type: receiver.key === 'VARIABLE' ? 'reference' : 'custom',
              value: {
                member_type: receiver.key,
                members: Array.isArray(receiver.value) ? receiver.value.join(',') : receiver.value,
              },
            };
            backValue.push(valueInfo);
          });
        } else {
          // 对于引用变量的数据
          if (item.value === 'VARIABLE') {
            backValue = Array.isArray(item.insertValue) ? item.insertValue.join(',') : item.insertValue;
          } else if (item.itemInfo && item.itemInfo[0].id) {
            backValue = item.itemInfo[0].value || item.itemInfo[0].val;
          } else {
            backValue = item.value;
          }
        }
        return backValue;
      },
      // 创建触发条件
      createTriggerCondition() {
        const params = this.conditionParams();
        const id = this.backInfo.triggerInfo.id;
        this.$store.dispatch('trigger/batchTriggerCondition', { params, id }).then(() => {
          this.$bkMessage({
            message: this.triggerInfo.id ? this.$t('m.common[\'保存成功\']') : this.$t('m.trigger[\'创建成功\']'),
            theme: 'success',
          });
          this.closeTrigger();
          this.$emit('getList');
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.btnLoading = false;
          });
      },
      conditionParams() {
        const params = [];
        let sum = 0;
        this.rulesList.forEach(item => {
          const itemParam = {
            condition: {},
            name: item.name,
            by_condition: item.triggerStatus,
            action_schemas: [],
          };
          // 把id带上则视为更新触发条件
          if (item.triggerRules.id) {
            itemParam.id = item.triggerRules.id;
          }
          // 条件关系
          if (item.triggerStatus) {
            itemParam.condition[item.triggerRules.type] = [];
            item.triggerRules.list.forEach(rule => {
              const ruleInfo = {};
              ruleInfo[rule.type] = [];
              rule.itemList.forEach(ruleItem => {
                const ruleItemInfo = {
                  key: ruleItem.key,
                  value: Array.isArray(ruleItem.value) ? ruleItem.value.join(',') : ruleItem.value,
                  field_type: ruleItem.type,
                  operator: ruleItem.condition,
                  type: 'custom',
                };
                ruleInfo[rule.type].push(ruleItemInfo);
              });
              itemParam.condition[item.triggerRules.type].push(ruleInfo);
            });
          } else {
            itemParam.condition = '';
          }
          // 需要引用前面保存的字段信息
          // itemParam.trigger_id = this.backInfo.triggerInfo.id
          item.responseList.forEach((id, idIndex) => {
            itemParam.action_schemas.push(this.backInfo.responseList[sum + idIndex]);
          });
          sum += item.responseList.length;
          params.push(itemParam);
        });
        return params;
      },
      // 获取触发条件
      async getTriggerRules() {
        const params = {
          trigger_id: this.triggerInfo.id,
        };
        await this.$store.dispatch('trigger/getTriggerRules', params).then((res) => {
          this.triggerAllRules = res.data;
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {

          });
      },
      // 获取响应事件列表
      async getResponseList() {
        await this.$store.dispatch('trigger/getResponseList').then(async (res) => {
          this.responseWayList = res.data;
          // todo:任务模板和公共触发器中不允许修改字段值
          if (!this.originInfoToTrigger.id || this.originInfoToTrigger.source === 'task') {
            this.responseWayList = this.responseWayList.filter(way => way.key !== 'modify_field' && way.key !== 'modify_specified_state_processor');
          } else {
            this.responseWayList.forEach(way => {
              way.field_schema.forEach(async schema => {
                if (schema.source_type === 'RPC') {
                  await this.getResponseFields(schema);
                }
              });
            });
          }
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      // 选择基础模型后，添加触发器变量
      giveTableVariables(id) {
        this.formData.variableLoading = true;
        this.$store.dispatch('basicModule/get_trigger_tables', id).then((res) => {
          const tempVariables = res.data.fields;
          tempVariables.forEach(field => {
            field.name += this.$t('m.trigger[\'（基础模型）\']');
          });
          this.$store.commit('trigger/changeTriggerVariables', this.globalChoise.ticket_variables.concat(tempVariables));
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.formData.variableLoading = false;
          });
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import './triggerCss/addTrigger.scss';
</style>
