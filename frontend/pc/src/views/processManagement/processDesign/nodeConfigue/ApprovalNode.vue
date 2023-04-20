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
      <bk-form
        form-type="vertical"
        style="margin-bottom: 40px"
        :label-width="150"
        :model="formInfo"
        :rules="nodeInfoRule" ref="nodeInfoForm">
        <bk-form-item
          data-test-id="approveNode-input-nodeName"
          :label="$t(`m.treeinfo['节点名称：']`)"
          :required="true"
          :property="'name'"
          :ext-cls="'bk-form-width'">
          <bk-input v-model="formInfo.name"
            maxlength="120">
          </bk-input>
        </bk-form-item>
        <desc-info v-model="formInfo.desc"></desc-info>
        <!-- <bk-form-item
          data-test-id="approveNode-input-nodeLabel"
          :label="$t(`m.treeinfo['节点标签：']`)"
          :required="true"
          :ext-cls="'bk-form-width'">
          <bk-select
            v-model="formInfo.tag"
            :clearable="false"
            searchable
            :font-size="'medium'">
            <bk-option v-for="option in nodeTagList"
              :key="option.key"
              :id="option.key"
              :name="option.name">
            </bk-option>
          </bk-select>
        </bk-form-item> -->
        <bk-form-item
          data-test-id="approveNode-radio-approveMode"
          :label="$t(`m.treeinfo['审批方式：']`)"
          :required="true"
          :property="'nodeType'">
          <bk-radio-group v-model="processType" @change="handleChangeDispose">
            <bk-radio :value="'multi'" :ext-cls="'mr20'">{{$t(`m.treeinfo['或签']`)}}
              <i class="bk-itsm-icon icon-icon-info tooltip-icon"
                v-bk-tooltips="$t(`m.treeinfo['多个审批人当有一个审批人审批即可，该审批节点的审批结果为该审批人的审批结果']`)"></i>
            </bk-radio>
            <bk-radio :value="'sequential'" :ext-cls="'mr20'">{{$t(`m.treeinfo['顺序会签']`)}}
              <i class="bk-itsm-icon icon-icon-info tooltip-icon"
                v-bk-tooltips="$t(`m.treeinfo['所有审批人必须按照审批人列表的顺序依次审批，直到满足条件才会结束，当不设置提前结束条件时，需要所有的审批人按照顺序依次审批完该节点才会结束']`)"></i>
            </bk-radio>
            <bk-radio :value="'random'">{{$t(`m.treeinfo['随机会签']`)}}
              <i class="bk-itsm-icon icon-icon-info tooltip-icon"
                v-bk-tooltips="$t(`m.treeinfo['所有审批人都可以审批，没有顺序要求，直到满足条件才会结束，当不设置提前结束条件时，需要所有的审批人都审批完该节点才会结束']`)"></i>
            </bk-radio>
          </bk-radio-group>
          <template v-if="isShowSignSwitch">
            <span class="bk-condtion-switch">{{ $t(`m.treeinfo['提前结束条件']`) }}</span>
            <bk-switcher data-test-id="approve-switcher-condtion" v-model="isShowSignOptions" theme="primary"></bk-switcher>
            <i class="bk-itsm-icon icon-icon-info tooltip-icon" v-bk-tooltips="$t(`m.treeinfo['若配置了会签提前结束条件，满足条件，将提前结束']`)"></i>
            <div class="bk-condition-content" v-if="isShowSignOptions">
              <div class="bk-condition-group" v-for="(group, gIndex) in finishCondition.expressions" :key="gIndex">
                <p class="bk-group-title">{{$t(`m.treeinfo['或-条件组']`)}}{{gIndex + 1}}</p>
                <div :class="{ 'bk-group-content': true, 'bk-group-contents': group.expressions.length > 1 }">
                  <bk-form :label-width="0"
                    :rules="finishConditionRule"
                    ref="finishConditionForms"
                    v-for="(expression, eIndex) in group.expressions" :key="eIndex"
                    :model="expression"
                    form-type="inline"
                    :ext-cls="'bk-condition'">
                    <bk-form-item :ext-cls="'bk-form-item-cus'" :property="'key'">
                      <div class="bk-left-block" v-if="group.expressions.length > 1">
                        <span :class="{ 'left-top-default': true, 'no-left-border': eIndex === 0 }"></span>
                        <span :class="{ 'left-bottom-default': true, 'no-left-border': eIndex === group.expressions.length - 1 }"></span>
                        <span class="bk-left-letter" v-if="eIndex !== group.expressions.length - 1">{{$t(`m.common['且']`)}}</span>
                      </div>
                      <bk-select
                        v-model="expression.key"
                        data-test-id="approve-select-condtionType"
                        :font-size="'medium'"
                        :clearable="false"
                        :ext-cls="'bk-form-width-long'"
                        @selected="selectCondition($event, expression, eIndex, gIndex)">
                        <bk-option v-for="option in allCondition"
                          :key="option.id"
                          :id="option.key"
                          :name="option.name">
                        </bk-option>
                      </bk-select>
                    </bk-form-item>
                    <bk-form-item :ext-cls="'bk-form-item-cus'">
                      <bk-select v-model="expression.condition"
                        data-test-id="approve-select-condtion"
                        :font-size="'medium'"
                        :clearable="false"
                        :ext-cls="'bk-form-width-short'">
                        <bk-option v-for="option in betweenList"
                          :key="option.key"
                          :id="option.key"
                          :name="option.name">
                        </bk-option>
                      </bk-select>
                    </bk-form-item>
                    <bk-form-item :ext-cls="'bk-form-item-cus'" :property="'value'">
                      <bk-input v-model="expression.value"
                        data-test-id="approve-condtion-value"
                        :ext-cls="'bk-form-width-long'"
                        v-bk-tooltips="expression.tooltipInfo"
                        :disabled="(!$refs.processors.getValue().value && expression.meta.unit === 'INT') ||
                          !expression.key"
                        :clearable="false"
                        type="number"
                        :max="expression.meta.unit === 'INT' ? formInfo.processors.length : 100"
                        :min="0"
                        :precision="0"
                        @change="giveTooltip(expression)"></bk-input>
                      <span v-if="expression.meta.unit === 'PERCENT'"
                        class="buttonIcon">%</span>
                    </bk-form-item>
                    <bk-form-item :ext-cls="'bk-form-item-cus'">
                      <div class="bk-operate-expression">
                        <i class="bk-itsm-icon icon-flow-add mr10" @click="operateExpression(group)"></i>
                        <i class="bk-itsm-icon icon-flow-reduce mr10" :class="{ 'bk-itsm-icon-disable':
                          group.expressions.length === 1 }"
                          @click="operateExpression(group, 'del', eIndex, gIndex, expression)"></i>
                      </div>
                    </bk-form-item>
                    <i class="bk-icon icon-close bk-delete-group"
                      @click="operateGroup('del', gIndex)"></i>
                  </bk-form>
                </div>
              </div>
              <p class="bk-add-group" data-test-id="approve-condtion-addGroup" @click="operateGroup"><i class="bk-itsm-icon icon-add-new mr5"></i>
                {{$t(`m.treeinfo['添加“或”条件组']`)}}</p>
            </div>
          </template>
        </bk-form-item>
        <bk-form-item
          data-test-id="approveNode-component-processor"
          :label="$t(`m.treeinfo['处理人：']`)"
          :required="true">
          <div @click="checkStatus.processors = false">
            <deal-person
              ref="processors"
              :value="processorsInfo"
              :show-overbook="true"
              :node-info="configur"
              :exclude-role-type-list="excludeProcessor">
            </deal-person>
          </div>
        </bk-form-item>
        <bk-form-item
          data-test-id="approveNode-input-ticketStatus"
          :label="$t(`m.treeinfo['设置单据状态：']`)"
          :required="true"
          :ext-cls="'bk-form-width'">
          <bk-select :ext-cls="'inline-form-width'"
            v-model="formInfo.ticket_type"
            :clearable="false"
            searchable
            :font-size="'medium'"
            @selected="handleTicket">
            <bk-option v-for="option in billStatusList"
              :key="option.type"
              :id="option.type"
              :name="option.name">
            </bk-option>
          </bk-select>
          <template v-if="formInfo.ticket_type === 'custom'">
            <bk-select :ext-cls="'inline-form-width mt10'"
              v-model="formInfo.ticket_key"
              :loading="ticketKeyLoading"
              :clearable="false"
              searchable
              :font-size="'medium'">
              <bk-option v-for="option in secondLevelList"
                :key="option.key"
                :id="option.key"
                :name="option.name">
              </bk-option>
            </bk-select>
          </template>
        </bk-form-item>
        <template v-if="!configur.is_builtin">
          <bk-form-item
            data-test-id="approveNode-radio-canDeliver"
            :label="$t(`m.treeinfo['是否可转单：']`)"
            :required="true">
            <bk-radio-group v-model="formInfo.can_deliver">
              <bk-radio :value="true" :ext-cls="'mr20'">{{ $t('m.treeinfo["是"]') }}</bk-radio>
              <bk-radio :value="false">{{ $t('m.treeinfo["否"]') }}</bk-radio>
            </bk-radio-group>
          </bk-form-item>
        </template>
        <template v-if="formInfo.can_deliver">
          <bk-form-item
            data-test-id="approveNode-component-deliver"
            :label="$t(`m.treeinfo['转单人：']`)"
            :required="true">
            <div @click="checkStatus.delivers = false">
              <deal-person
                ref="delivers"
                :value="deliversInfo"
                :exclude-role-type-list="deliversExclude">
              </deal-person>
            </div>
          </bk-form-item>
        </template>
        <bk-form-item :label="$t(`m.treeinfo['自动处理']`)" :required="true">
          <bk-checkbox
            :true-value="true"
            :false-value="false"
            v-model="formInfo.is_allow_skip">
            {{$t(`m['节点处理人为空时，直接跳过且不视为异常']`) }}
          </bk-checkbox>
        </bk-form-item>
      </bk-form>
      <field-config
        ref="field"
        :is-show-title="true"
        :flow-info="flowInfo"
        :configur="configur">
      </field-config>
      <common-trigger-list :origin="'state'"
        :node-type="configur.type"
        :source-id="flowInfo.id"
        :sender="configur.id"
        :table="flowInfo.table">
      </common-trigger-list>
      <div class="bk-node-btn">
        <bk-button :theme="'primary'"
          data-test-id="approve-button-submit"
          :title="$t(`m.treeinfo['确定']`)"
          :loading="secondClick"
          class="mr10"
          @click="submitNode">
          {{$t(`m.treeinfo['确定']`)}}
        </bk-button>
        <bk-button :theme="'default'"
          data-test-id="approve-button-close"
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
  import dealPerson from './components/dealPerson.vue';
  import fieldConfig from './components/fieldConfig.vue';
  import commonTriggerList from '../../taskTemplate/components/commonTriggerList';
  import BasicCard from '@/components/common/layout/BasicCard.vue';
  import { errorHandler } from '../../../../utils/errorHandler';
  export default {
    name: 'ApprovalNode',
    components: {
      BasicCard,
      dealPerson,
      fieldConfig,
      commonTriggerList,
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
    },
    data() {
      return {
        betweenList: [
          {
            id: 1,
            name: '>=',
            key: '>=',
          },
          {
            id: 2,
            name: '>',
            key: '>',
          },
          {
            id: 3,
            name: '=',
            key: '==',
          },
          {
            id: 4,
            name: '<=',
            key: '<=',
          },
          {
            id: 5,
            name: '<',
            key: '<',
          },
        ],
        finishCondition: {
          expressions: [
            {
              expressions: [],
              type: 'and',
            },
          ],
          type: 'or',
        },
        finishConditionRule: {
          key: [
            {
              required: true,
              message: this.$t('m.systemConfig[\'请输入\']'),
              trigger: 'blur',
            },
          ],
          value: [
            {
              required: true,
              message: this.$t('m.systemConfig[\'请输入\']'),
              trigger: 'blur',
            },
          ],
        },
        passRateExpression: {
          key: '',
          condition: '>=',
          value: '',
          source: 'global',
          type: 'INT',
          meta: {
            code: 'PROCESS_COUNT',
            unit: 'INT',
          },
          tooltipInfo: {
            disabled: true,
            content: '',
            placements: ['top'],
          },
        },
        emptyExpression: {
          key: '',
          condition: '>=',
          value: '',
          source: 'global',
          type: 'INT',
          meta: {
            code: '',
            unit: 'INT',
          },
          tooltipInfo: {
            disabled: false,
            content: this.$t('m.treeinfo[\'请先选择条件\']'),
            placements: ['top'],
          },
        },
        isShowSignSwitch: false,
        isShowSignOptions: false,
        processType: '',
        isLoading: false,
        secondClick: false,
        getConditionFlag: false,
        ticketKeyLoading: false,
        formInfo: {
          name: '',
          desc: '',
          tag: '',
          ticket_type: '',
          ticket_key: '',
          is_sequential: false,
          is_multi: true,
          processors: [],
          is_allow_skip: false,
        },
        nodeTagList: [],
        allCondition: [],
        secondLevelList: [],
        excludeProcessor: [], // 处理人排除类型
        deliversExclude: ['BY_ASSIGNOR', 'EMPTY', 'STARTER', 'VARIABLE', 'API', 'ASSIGN_LEADER', 'STARTER_LEADER'], // 转单人排除类型
        // 单据状态
        billStatusList: [
          { type: 'keep', name: this.$t('m.treeinfo["延续上个节点"]') },
          { type: 'custom', name: this.$t('m.treeinfo["自定义"]') },
        ],
        processorsInfo: {
          type: '',
          value: '',
        },
        deliversInfo: {
          type: '',
          value: '',
        },
        checkStatus: {
          delivers: false,
          processors: false,
        },
        nodeInfoRule: {
          name: [
            {
              required: true,
              message: this.$t('m.newCommon[\'请输入节点名称\']'),
              trigger: 'blur',
            },
          ],
          processors: [
            {
              validator(val) {
                return val.length;
              },
              message: this.$t('m.newCommon[\'请选择处理人\']'),
              trigger: 'blur',
            },
          ],
        },
      };
    },
    watch: {
      'formInfo.processors'() {
        this.setAllTooltip();
      },
    },
    mounted() {
      this.initData();
    },
    methods: {
      async initData() {
        await this.getAllConditions();
        this.isLoading = true;
        let getSecondLevelList;
        this.processType = 'multi';
        // name
        this.formInfo.name = this.configur.name;
        this.formInfo.desc = this.configur.desc;
        // 节点标签
        this.formInfo.tag = this.configur.tag || '';
        this.formInfo.is_multi = this.configur.is_multi === true;
        // this.formInfo.can_deliver = this.configur.can_deliver === true
        if (this.configur.is_multi) {
          this.isShowSignSwitch = true;
          if (this.configur.is_sequential) {
            this.processType = 'sequential';
          } else {
            this.processType = 'random';
          }
        } else {
          this.processType = 'multi';
        }
        this.formInfo.is_sequential = this.configur.is_sequential;
        this.formInfo.is_allow_skip = this.configur.is_allow_skip;
        this.formInfo.processors = this.configur.processors ? this.configur.processors.split(',') : [];
        this.formInfo.ticket_type = this.configur.extras.ticket_status ? this.configur.extras.ticket_status.type : 'keep';
        this.formInfo.ticket_key = this.configur.extras.ticket_status ? this.configur.extras.ticket_status.name : '';
        if (this.configur.finish_condition && this.configur.finish_condition.expressions) {
          if (this.configur.finish_condition.expressions.length) {
            this.isShowSignOptions = true;
          }
          this.finishCondition = JSON.parse(JSON.stringify(this.configur.finish_condition));
          this.finishCondition.expressions.forEach(group => {
            group.expressions = group.expressions.map(expression => {
              const tooltipInfo = {
                disabled: true,
                content: '',
                placements: ['top'],
              };
              return { ...expression, tooltipInfo };
            });
          });
        } else {
          const passRateExpressionKey = this.allCondition.find(one => one.meta.code === 'PROCESS_COUNT');
          if (passRateExpressionKey) {
            this.passRateExpression.key = passRateExpressionKey.key;
          }
          this.finishCondition.expressions[0].expressions.push(JSON.parse(JSON.stringify(this.passRateExpression)));
          this.giveTooltip(this.passRateExpression);
        }
        this.$set(this.formInfo, 'can_deliver', this.configur.can_deliver === true);
        if (this.formInfo.ticket_type === 'custom') {
          getSecondLevelList = this.getSecondLevelList();
        }
        if (this.formInfo.can_deliver) {
          this.deliversInfo = {
            type: this.configur.delivers_type,
            value: this.configur.delivers,
          };
        }
        // 处理人
        this.processorsInfo = {
          type: this.configur.processors_type,
          value: this.configur.processors,
        };
        const getNodeTagList = this.getNodeTagList();
        this.getExcludeRoleTypeList();
        Promise.all([getSecondLevelList, getNodeTagList]).then(() => {
          this.isLoading = false;
        });
      },
      // 获取节点标签数据
      getNodeTagList() {
        const params = {
          key: 'STATE_TAG_TYPE',
        };
        return this.$store.dispatch('datadict/get_data_by_key', params).then((res) => {
          this.nodeTagList = res.data;
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {

          });
      },
      // 获取等级
      getSecondLevelList() {
        this.ticketKeyLoading = true;
        return this.$store.dispatch('ticketStatus/getOverallTicketStatuses').then(res => {
          this.secondLevelList = res.data;
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.ticketKeyLoading = false;
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
        // if (!this.flowInfo.is_iam_used) {
        //     excludeProcessor.push('IAM')
        //     this.deliversExclude.push('IAM')
        // }
        // 处理场景如果不是'DISTRIBUTE_THEN_PROCESS' || 'DISTRIBUTE_THEN_CLAIM'，则去掉派单人指定
        if (this.configur.distribute_type !== 'DISTRIBUTE_THEN_PROCESS' && this.configur.distribute_type !== 'DISTRIBUTE_THEN_CLAIM') {
          excludeProcessor.push('BY_ASSIGNOR');
        }
        if (!this.flowInfo.is_biz_needed) {
          excludeProcessor.push('CMDB');
          this.deliversExclude.push('CMDB');
        }
        this.excludeProcessor = [...['EMPTY', 'API'], ...excludeProcessor];
      },
      // 确认
      async submitNode() {
        const validates = [this.$refs.nodeInfoForm.validate()];
        await Promise.all(validates).then(() => {
          const params = {
            is_draft: false,
            workflow: this.flowInfo.id,
            type: this.configur.type,
            is_terminable: false,
            processors_type: 'PERSON',
            finish_condition: this.finishCondition,
            is_multi: false,
            is_allow_skip: false,
          };
          // 基本信息
          params.name = this.formInfo.name;
          params.desc = this.formInfo.desc || undefined;
          params.is_sequential = this.formInfo.is_sequential;
          params.processors_type = '';
          params.processors = '';
          // 提前条件结束为false
          if (!this.isShowSignOptions) {
            params.finish_condition = {
              expressions: [],
              type: 'or',
            };
          }
          // 处理人为空校验
          if (this.$refs.processors && !this.$refs.processors.verifyValue()) {
            this.checkStatus.processors = true;
            return;
          }
          if (this.$refs.processors) {
            const data = this.$refs.processors.getValue();
            params.processors_type = data.type;
            params.processors = data.value;
          }
          // 转单人为空校验
          if (this.$refs.delivers && !this.$refs.delivers.verifyValue()) {
            this.checkStatus.delivers = true;
            return;
          }
          // 处理人异常时
          params.is_allow_skip = this.formInfo.is_allow_skip;
          if (this.$refs.delivers) {
            const data = this.$refs.delivers.getValue();
            params.delivers_type = data.type;
            params.delivers = data.value;
          }
          if (this.processType !== 'multi') {
            params.is_multi = true;
          }
          params.tag = this.formInfo.tag;
          params.can_deliver = this.formInfo.can_deliver;
          params.ticket_type = this.formInfo.ticket_type;
          params.extras = {
            ticket_status: {
              name: this.formInfo.ticket_key,
              type: this.formInfo.ticket_type,
            },
          };
          // 字段配置
          const fieldInfo = this.$refs.field.showTabList;
          params.fields = fieldInfo.map(item => item.id);
          const id = this.configur.id;
          if (this.secondClick) {
            return;
          }
          this.secondClick = true;
          this.$store.dispatch('deployCommon/updateNode', { params, id }).then(() => {
            this.$bkMessage({
              message: this.$t('m.treeinfo["保存成功"]'),
              theme: 'success',
            });
            this.$emit('closeConfigur', true);
          })
            .catch(res => {
              errorHandler(res, this);
            })
            .finally(() => {
              this.secondClick = false;
            });
        })
          .catch((validator) => {
            // 防止出现Uncaught
            console.log(validator);
          });
      },
      // 取消
      closeNode() {
        this.$emit('closeConfigur', false);
      },
      handleChangeDispose(val) {
        this.isShowSignSwitch = false;
        this.formInfo.is_sequential = false;
        if (val !== 'multi') {
          this.isShowSignSwitch = true;
        }
        if (val === 'sequential') {
          this.formInfo.is_sequential = true;
        }
      },
      // 获取二级状态数据
      handleTicket(value) {
        this.formInfo.ticket_key = '';
        if (value === 'custom') {
          if (!this.secondLevelList.length) {
            this.getSecondLevelList();
          }
        }
      },
      operateGroup(type = 'add', index) {
        if (type === 'del') {
          if (this.finishCondition.expressions.length === 1) {
            this.$bkInfo({
              type: 'warning',
              title: this.$t('m.treeinfo[\'确定删除唯一的条件组？\']'),
              subTitle: this.$t('m.treeinfo[\'若删除，则必须所有人处理完成才结束\']'),
              confirmFn: () => {
                this.finishCondition.expressions.splice(index, 1);
              },
            });
          } else {
            this.finishCondition.expressions.splice(index, 1);
          }
        } else {
          this.finishCondition.expressions.push({
            expressions: [JSON.parse(JSON.stringify(this.emptyExpression))],
            type: 'and',
          });
        }
      },
      // 添加删除条件
      operateExpression(expressionGroup, type = 'add', eIndex, gIndex, expression) {
        if (type === 'del') {
          if (expressionGroup.expressions.length === 1) {
            return;
          }
          if (gIndex === 0 && eIndex === 0 && expression.meta.code === 'PROCESS_COUNT') {
            this.$bkInfo({
              type: 'warning',
              title: this.$t('m.treeinfo[\'确定删除“处理人数”？\']'),
              subTitle: this.$t('m.treeinfo[\'若删除该条件，则忽略处理人数，条件满足即结束\']'),
              confirmFn: () => {
                expressionGroup.expressions.splice(eIndex, 1);
              },
            });
          } else {
            expressionGroup.expressions.splice(eIndex, 1);
          }
        } else {
          expressionGroup.expressions.push(JSON.parse(JSON.stringify(this.emptyExpression)));
        }
      },
      // 获取提前结束可选条件
      async getAllConditions() {
        const id = this.configur.id;
        this.getConditionFlag = true;
        await this.$store.dispatch('apiRemote/get_sign_conditions', id).then(res => {
          // 会签不需要审批结果
          const result = res.data.filter(item => item.meta.code !== 'NODE_APPROVE_RESULT');
          this.allCondition = result;
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.getConditionFlag = false;
          });
      },
      // 设置条件tooltip
      giveTooltip(expression) {
        if (!expression.key) {
          expression.tooltipInfo.disabled = false;
          expression.tooltipInfo.content = this.$t('m.treeinfo[\'请先选择条件\']');
          return;
        }
        if (!(expression.meta.code === 'PASS_RATE' || expression.meta.code === 'REJECT_RATE') && !this.$refs.processors.getValue().value) {
          expression.tooltipInfo.disabled = false;
          expression.tooltipInfo.content = this.$t('m.treeinfo[\'请先选择处理人\']');
          return;
        }
        expression.tooltipInfo.disabled = true;
        expression.tooltipInfo.content = '';
      },
      // 所有条件添加tootip
      setAllTooltip() {
        this.finishCondition.expressions.forEach(group => {
          group.expressions.forEach(expression => {
            this.giveTooltip(expression);
          });
        });
      },
      // 条件选择回调
      selectCondition(condition) {
        this.changeCondition(condition);
        // 不需要二次确认
        // if (gIndex === 0 && eIndex === 0 && condition.meta.code === 'PROCESS_COUNT') {
        //     this.$bkInfo({
        //         type: 'warning',
        //         title: this.$t(`m.treeinfo['确定更改“处理人数”？']`),
        //         subTitle: this.$t(`m.treeinfo['若更改该条件，则忽略处理人数，条件满足即结束']`),
        //         cancelFn: () => {
        //             condition.key = this.allCondition.find(one => one.meta.code === 'PROCESS_COUNT').key
        //         },
        //         confirmFn: () => {
        //             this.changeCondition(condition)
        //         }
        //     })
        // } else {
        //     this.changeCondition(condition)
        // }
      },
      changeCondition(condition) {
        condition.meta.code = this.allCondition.find(one => one.key === condition.key).meta.code;
        condition.meta.unit = this.allCondition.find(one => one.key === condition.key).meta.unit || 'INT';
        this.giveTooltip(condition);
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../../scss/mixins/scroller.scss';
    .bk-error-info {
        color: #ff5656;
        font-size: 12px;
        line-height: 30px;
    }
    .bk-basic-node {
        padding: 20px;
        padding-bottom: 20px;
        margin-bottom: 20px;
        height: 100%;
        background-color: #FAFBFD;
        overflow: auto;
        @include scroller;
        /deep/ .common-section-card-label {
            display: none;
        }
        /deep/ .common-section-card-body {
            padding: 20px;
        }

        .bk-node-btn{
            font-size: 0;
        }

        .bk-service-name{
            h1{
                padding-left: 10px;
            }
        }

        .tooltip-icon{
            font-size: 15px;
            vertical-align: inherit;
            &:before{
                color: #979BA5;
            }
        }

        /deep/ .bk-form-width {
            width: 448px;
        }
        .inline-form-width {
            float: left;
            width: 448px;
            margin-right: 10px;
        }
        .form-cus-height{
            & div:first-child{
                height: auto!important;
            }
        }

        .bk-processor-width {
            width: 760px;
        }

        .bk-sign-info{

            .bk-service-title{
                display: flex;
                align-items: center;
                margin-top: 40px;
            }
        }
        .bk-condtion-switch {
            font-size: 14px;
            color: #979BA5;
        }
        .bk-condition-content{
                height: auto;
                max-width: 750px;

                .bk-condition-group{
                    width: 100%;

                    .bk-group-title{
                        color: #63656E;
                        font-weight: bold;
                        font-size: 14px;
                        margin-bottom: 6px;
                        // margin-top: 30px;
                    }

                    .bk-group-content{
                        display: flex;
                        width: fit-content;
                        align-items: center;
                        flex-wrap: wrap;
                        padding: 0 20px 20px 20px;
                        border: 1px solid #DCDEE5;
                        position: relative;
                        background-color: #fff;

                        .bk-condition{
                            display: flex;
                            align-items: center;
                            padding-top: 20px;
                            width: 100%;

                            .bk-form-item-cus{
                                margin-top: 8px;
                                /deep/ .bk-form-content{
                                    display: inline-flex;
                                    align-items: center;
                                }

                                /deep/ .bk-select-dropdown{
                                    width: 100%;
                                }

                                .bk-form-width-long{
                                    display: inline-flex;
                                    width: 250px;
                                }

                                .buttonIcon{
                                    position: absolute;
                                    display: inline-flex;
                                    justify-content: center;
                                    align-items: center;
                                    height: 30px;
                                    width: 30px;
                                    right: 1px;
                                    color: #63656e;
                                    font-size: 12px;
                                    border-left: 1px solid #c4c6cc;
                                    background: #f2f4f8;
                                }

                                .bk-form-width-short{
                                    width: 100px
                                }

                                .bk-operate-expression{
                                    width: 50px;
                                    display: inline-flex;
                                    align-items: center;

                                    .bk-icon-disable{
                                        cursor: no-drop;
                                        &:before{
                                            color: #DCDEE5;
                                        }
                                    }
                                }
                            }
                        }

                        .bk-delete-group {
                            position: absolute;
                            top: 6px;
                            right: 6px;
                            text-align: center;
                            cursor: pointer;
                            font-weight: 700;
                            color: #979ba5;
                            border-radius: 50%;
                            font-size: 18px;
                            display: none;
                        }

                        &:hover {
                            .bk-delete-group {
                                display: block;
                            }
                        }
                    }

                    .bk-group-contents{
                        padding: 14px 34px 34px 22px;

                        .bk-left-block{
                            position: relative;
                            display: inline-flex;
                            height: 32px;
                            width: 20px;
                            flex-wrap: wrap;

                            .left-top-default, .left-bottom-default{
                                height: 50%;
                                width: 100%;
                                border: 1px dashed #DCDEE5;
                                border-right: none;
                            }

                            .left-top-default{
                                border-top: none;
                            }

                            .left-bottom-default{
                                border-bottom: none;
                                border-top: none;
                            }

                            .bk-left-letter{
                                position: absolute;
                                height: 18px;
                                width: 28px;
                                line-height: 18px;
                                font-size: 12px;
                                color: #FFFFFF;
                                background: #C4C6CC;
                                text-align: center;
                                top: 100%;
                                left: -13px;
                                border-radius: 2px;
                            }

                            .no-left-border{
                                border-left: none;
                            }
                        }
                    }
                }

                .bk-add-group{
                    display: flex;
                    align-items: center;
                    color: #3A84FF;
                    margin-top: 15px;
                    cursor: pointer;
                    height: 20px;
                    line-height: 20px;
                    font-size: 14px;
                    width: fit-content;

                    .icon-add-new:before{
                        color: #3A84FF;
                    }
                }
            }
    }
</style>
