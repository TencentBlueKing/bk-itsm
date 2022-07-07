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
  <div class="bk-basic-node">
    <basic-card :card-label="$t(`m.treeinfo['基本信息']`)">
      <bk-form :label-width="150" :model="formInfo" :rules="nodeInfoRule" ref="nodeInfoForm">
        <bk-form-item
          data-test-id="signNode-input-name"
          :label="$t(`m.treeinfo['节点名称：']`)"
          :required="true"
          :property="'name'"
          :ext-cls="'bk-form-width'">
          <bk-input v-model="formInfo.name"
            maxlength="120">
          </bk-input>
        </bk-form-item>
        <bk-form-item
          :label="$t(`m.treeinfo['处理方式：']`)"
          :required="true" :property="'nodeType'">
          <bk-radio-group v-model="formInfo.is_sequential">
            <bk-radio :value="false" :ext-cls="'mr50 pr40'">{{$t(`m.treeinfo['多人随机会签']`)}}
              <i class="bk-itsm-icon icon-icon-info tooltip-icon"
                v-bk-tooltips="$t(`m.treeinfo['要求所有处理人全部处理完成，多人处理没有先后顺序要求。']`)"></i></bk-radio>
            <bk-radio :value="true">{{$t(`m.treeinfo['多人依次会签']`)}}
              <i class="bk-itsm-icon icon-icon-info tooltip-icon"
                v-bk-tooltips="$t(`m.treeinfo['要求所有处理人按照名单顺序，依次全部处理完成。']`)"></i></bk-radio>
          </bk-radio-group>
        </bk-form-item>
        <bk-form-item
          data-test-id="signNode-radio-processors "
          :label="$t(`m.treeinfo['处理人：']`)"
          :required="true"
          :property="'processors'"
          :ext-cls="'bk-processor-width form-cus-height'">
          <member-select v-model="formInfo.processors">
          </member-select>
          <p v-if="formInfo.processors.length" class="bk-processor-length">{{$t(`m.treeinfo['共']`)}}<span>{{formInfo.processors.length}}</span>{{formInfo.is_sequential ? $t(`m.treeinfo['人']`) + $t(`m.treeinfo['，名单顺序将会影响会签顺序']`) : $t(`m.treeinfo['人']`)}}</p>
        </bk-form-item>
      </bk-form>
    </basic-card>
    
    <basic-card class="mt20" :card-label="$t(`m.treeinfo['字段配置']`)">
      <field-config
        ref="field"
        :flow-info="flowInfo"
        :configur="configur">
      </field-config>
    </basic-card>
        
    <basic-card
      class="mt20"
      v-bkloading="{ isLoading: getConditionFlag }"
      :card-label="$t(`m.treeinfo['会签提前结束配置']`)"
      :card-desc="$t(`m.treeinfo['默认结束条件：所有处理人处理完成，会签自动结束；若配置了会签提前结束条件，满足条件，将提前结束']`)">
      <div class="bk-condition-content">
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
              <bk-form-item data-test-id="signNode-input-conditionValue" :ext-cls="'bk-form-item-cus'" :property="'value'">
                <bk-input v-model="expression.value"
                  :ext-cls="'bk-form-width-long'"
                  v-bk-tooltips="expression.tooltipInfo"
                  :disabled="(!formInfo.processors.length && expression.meta.unit === 'INT') ||
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
        <p class="bk-add-group" @click="operateGroup"><i class="bk-itsm-icon icon-add-new mr5"></i>
          {{$t(`m.treeinfo['添加“或”条件组']`)}}</p>
      </div>
    </basic-card>

    <common-trigger-list :origin="'state'"
      :node-type="configur.type"
      :source-id="flowInfo.id"
      :sender="configur.id"
      :table="flowInfo.table">
    </common-trigger-list>
    <div class="bk-node-btn">
      <bk-button :theme="'primary'"
        data-test-id="signNode-button-submit"
        :title="$t(`m.treeinfo['确定']`)"
        :loading="secondClick"
        class="mr10"
        @click="submitNode">
        {{$t(`m.treeinfo['确定']`)}}
      </bk-button>
      <bk-button :theme="'default'"
        data-test-id="signNode-button-close"
        :title="$t(`m.treeinfo['取消']`)"
        class="mr10"
        @click="closeNode">
        {{$t(`m.treeinfo['取消']`)}}
      </bk-button>
    </div>
  </div>
</template>
<script>
  import fieldConfig from './components/fieldConfig.vue';
  import memberSelect from '../../../commonComponent/memberSelect';
  import commonTriggerList from '../../taskTemplate/components/commonTriggerList';
  import BasicCard from '@/components/common/layout/BasicCard.vue';
  import { errorHandler } from '../../../../utils/errorHandler';

  export default {
    name: 'signNode',
    components: {
      BasicCard,
      fieldConfig,
      memberSelect,
      commonTriggerList,
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
        secondClick: false,
        getConditionFlag: false,
        formInfo: {
          name: '',
          is_sequential: false,
          processors: [],
        },
        finishCondition: {
          expressions: [
            {
              expressions: [],
              type: 'and',
            },
          ],
          type: 'or',
        },
        allCondition: [],
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
      };
    },
    computed: {
      globalChoise() {
        return this.$store.state.cdeploy.configurInfo;
      },
      openFunction() {
        return this.$store.state.openFunction;
      },
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
        this.formInfo.name = this.configur.name;
        this.formInfo.is_sequential = this.configur.is_sequential;
        this.formInfo.processors = this.configur.processors ? this.configur.processors.split(',') : [];
        if (this.configur.finish_condition && this.configur.finish_condition.expressions) {
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
          this.passRateExpression.key = this.allCondition.find(one => one.meta.code === 'PROCESS_COUNT').key;
          this.finishCondition.expressions[0].expressions.push(JSON.parse(JSON.stringify(this.passRateExpression)));
          this.giveTooltip(this.passRateExpression);
        }
      },
      // 所有条件添加tootip
      setAllTooltip() {
        this.finishCondition.expressions.forEach(group => {
          group.expressions.forEach(expression => {
            this.giveTooltip(expression);
          });
        });
      },
      // 获取提前结束可选条件
      async getAllConditions() {
        const id = this.configur.id;
        this.getConditionFlag = true;
        await this.$store.dispatch('apiRemote/get_sign_conditions', id).then(res => {
          this.allCondition = res.data;
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.getConditionFlag = false;
          });
      },
      // 条件选择回调
      selectCondition(val, condition, eIndex, gIndex) {
        if (gIndex === 0 && eIndex === 0 && condition.meta.code === 'PROCESS_COUNT') {
          this.$bkInfo({
            type: 'warning',
            title: this.$t('m.treeinfo[\'确定更改“处理人数”？\']'),
            subTitle: this.$t('m.treeinfo[\'若更改该条件，则忽略处理人数，条件满足即结束\']'),
            cancelFn: () => {
              condition.key = this.allCondition.find(one => one.meta.code === 'PROCESS_COUNT').key;
            },
            confirmFn: () => {
              this.changeCondition(condition);
            },
          });
        } else {
          this.changeCondition(condition);
        }
      },
      changeCondition(condition) {
        condition.meta.code = this.allCondition.find(one => one.key === condition.key).meta.code;
        condition.meta.unit = this.allCondition.find(one => one.key === condition.key).meta.unit || 'INT';
        this.giveTooltip(condition);
      },
      // 设置条件tooltip
      giveTooltip(expression) {
        if (!expression.key) {
          expression.tooltipInfo.disabled = false;
          expression.tooltipInfo.content = this.$t('m.treeinfo[\'请先选择条件\']');
          return;
        }
        if (!(expression.meta.code === 'PASS_RATE' || expression.meta.code === 'REJECT_RATE') && !this.formInfo.processors.length) {
          expression.tooltipInfo.disabled = false;
          expression.tooltipInfo.content = this.$t('m.treeinfo[\'请先选择处理人\']');
          return;
        }
        expression.tooltipInfo.disabled = true;
        expression.tooltipInfo.content = '';
      },
      // 确认
      async submitNode() {
        let validates = [this.$refs.nodeInfoForm.validate()];
        if (this.$refs.finishConditionForms && this.$refs.finishConditionForms.length) {
          validates = validates.concat(this.$refs.finishConditionForms.map(form => form.validate()));
        }
        await Promise.all(validates).then(() => {
          const params = {
            is_draft: false,
            workflow: this.flowInfo.id,
            type: this.configur.type,
            is_terminable: false,
            processors_type: 'PERSON',
          };
          // 基本信息
          params.name = this.formInfo.name;
          params.is_sequential = this.formInfo.is_sequential;
          params.processors = this.formInfo.processors.join(',');
          // 字段配置
          const fieldInfo = this.$refs.field.showTabList;
          params.fields = fieldInfo.map(item => item.id);
          // 提前结束条件
          this.finishCondition.expressions.forEach(group => {
            group.expressions.forEach(expression => {
              delete expression.tooltipInfo;
            });
          });
          params.finish_condition = this.finishCondition;
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
      // 添加组条件
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
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../../scss/mixins/scroller.scss';
    .bk-basic-node {
        padding: 20px;
        height: 100%;
        background-color: #FAFBFD;
        overflow: auto;
        @include scroller;

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
        .bk-processor-length{
            color: #63656E;
            font-size: 12px;
            margin-top: 8px;
            & span{
                font-weight: bold;
                margin: 0 3px;
            }
        }

        .bk-form-width {
            width: 490px;
        }

        .form-cus-height{
            & div:first-child{
                height: auto!important;
            }
        }

        .bk-processor-width {
            width: 700px;
        }

        .bk-condition-content{
            height: auto;
            max-width: 750px;

            .bk-condition-group{
                width: 100%;
                &:not(:first-child) {
                    margin-top: 20px;
                }
                .bk-group-title{
                    color: #63656E;
                    font-weight: bold;
                    font-size: 14px;
                    margin-bottom: 6px;
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
