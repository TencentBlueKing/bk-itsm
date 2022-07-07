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
  <div class="bk-trigger-condition">
    <div class="bk-condition-name"><span>{{$t(`m.trigger['触发条件']`)}}</span></div>
    <div class="bk-condition-content" @click="triggerRules.checkStatus = false">
      <ul class="bk-content-step">
        <li class="bk-content-li" v-for="(item, index) in triggerRules.list" :key="index">
          <ul class="bk-content-item" :class="{ 'bk-more-margin': item.itemList.length !== 1 }">
            <li class="bk-content-item-li"
              :class="{ 'bk-none-margin': item.itemList.length - 1 === nodeIndex }"
              v-for="(node, nodeIndex) in item.itemList"
              :key="nodeIndex">
              <template v-if="item.itemList.length !== 1">
                <div class="bk-content-type"
                  v-if="nodeIndex !== item.itemList.length - 1"
                  @click="changeBetween(item)">
                  <span>{{ item.type === 'all' ? $t(`m.trigger['且']`) : $t(`m.trigger['或']`) }}</span>
                  <i class="bk-icon icon-down-shape"></i>
                </div>
                <!-- 线条 -->
                <div class="bk-item-line"></div>
                <div class="bk-item-line-none bk-item-none" v-if="nodeIndex === 0"></div>
                <div class="bk-item-line-none bk-item-none-bottom" v-if="nodeIndex === item.itemList.length - 1"></div>
              </template>
              <!-- 内容 -->
              <bk-select style="width: 190px;"
                :ext-cls="'bk-item-float'"
                v-model="node.key"
                :clearable="false"
                searchable
                @change="changeContent(node)">
                <bk-option v-for="option in keyList"
                  :key="option.key"
                  :id="option.key"
                  :name="option.name">
                </bk-option>
              </bk-select>
              <bk-select style="width: 140px;"
                :ext-cls="'bk-item-float'"
                v-model="node.condition"
                :clearable="false"
                searchable
                @selected="changeCondition(node)">
                <bk-option v-for="option in node.conditionList"
                  :key="option.name"
                  :id="option.name"
                  :name="option.label">
                </bk-option>
              </bk-select>
              <template v-if="node.conditionType !== 'none'">
                <trigger-field style="width: 170px; float: left; margin-right: 8px;"
                  :item="node">
                </trigger-field>
              </template>
              <!-- 新增和删除 -->
              <div class="bk-between-operat">
                <i class="bk-itsm-icon icon-flow-add" @click="addLine(item, node, nodeIndex)"></i>
                <i class="bk-itsm-icon icon-flow-reduce"
                  :class="{ 'bk-no-delete': item.itemList.length === 1 }"
                  @click="deleteLine(item, node, nodeIndex)"></i>
              </div>
            </li>
          </ul>
          <!-- 删除 -->
          <i class="bk-icon icon-close-circle-shape"
            :class="{ 'bk-no-delete': triggerRules.list.length === 1 }"
            @click="deleteGroup(item, index)"></i>
          <!-- 且或关系 -->
          <div class="bk-content-type" @click="handleBetween">
            <span>{{ triggerRules.type === 'all' ? $t(`m.trigger['且']`) : $t(`m.trigger['或']`) }}</span>
            <i class="bk-icon icon-down-shape"></i>
          </div>
          <!-- 最外层线条 -->
          <div class="bk-item-line"></div>
          <div class="bk-item-line-none bk-item-none" v-if="index === 0"></div>
          <!-- 内层线条 -->
          <div class="bk-content-line" v-if="item.itemList.length !== 1"></div>
        </li>
        <li class="bk-content-add">
          <span @click="addGroup">
            <i class="bk-icon icon-plus-circle mr5"></i><span>{{$t(`m.trigger['添加']`)}}</span>
          </span>
          <div class="bk-item-line"></div>
          <div class="bk-item-line-none" :class="{ 'bk-item-over-line': triggerRules.checkStatus }"></div>
        </li>
      </ul>
      <div class="bk-content-line"></div>
      <p class="bk-error-info" v-if="triggerRules.checkStatus">{{$t(`m.trigger['请填写完整的触发条件']`)}}</p>
    </div>
  </div>
</template>
<script>
  import triggerField from '../common/triggerField.vue';
  import { mapState } from 'vuex';
  import { errorHandler } from '../../../../utils/errorHandler';

  export default {
    name: 'triggerCondition',
    components: {
      triggerField,
    },
    props: {
      triggerRules: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        // 下拉选框
        keyList: [],
      };
    },
    computed: {
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
      ...mapState('trigger', {
        triggerVariables: state => state.triggerVariables,
      }),
    },
    mounted() {
      this.keyList = this.triggerVariables;
      // 初始化内置触发条件检查参数
      this.$set(this.triggerRules, 'checkStatus', false);
    },
    methods: {
      // 新增和删除行
      addLine(item, node, nodeIndex) {
        item.itemList.splice(nodeIndex + 1, 0, {
          condition: '',
          key: '',
          value: '',
          conditionList: [],
          type: 'STRING',
        });
      },
      deleteLine(item, node, nodeIndex) {
        if (item.itemList.length === 1) {
          return;
        }
        item.itemList.splice(nodeIndex, 1);
      },
      // 切换关系
      changeBetween(item) {
        item.type = item.type === 'all' ? 'any' : 'all';
      },
      handleBetween() {
        this.triggerRules.type = this.triggerRules.type === 'all' ? 'any' : 'all';
      },
      // 添加和删除触发条件组
      addGroup() {
        this.triggerRules.list.push({
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
        });
      },
      deleteGroup(item, index) {
        if (this.triggerRules.list.length === 1) {
          return;
        }
        this.triggerRules.list.splice(index, 1);
      },
      // 切换选项内容，匹配不同的表达式
      changeContent(node) {
        // 获取选中的项
        const checkItem = this.keyList.filter(item => item.key === node.key)[0];
        // 字母小写
        const lowerType = checkItem.type.toLowerCase();
        node.conditionList = this.globalChoise.trigger_methods[lowerType];
        this.getConditionList(checkItem, node);
        node.condition = '';
        this.$set(node, 'conditionType', '');
        node.type = checkItem.type;
        const multiType = ['MEMBERS', 'MEMBER', 'MULTI_MEMBERS', 'MULTISELECT', 'CHECKBOX'];
        node.value = multiType.some(item => item === node.type) ? [] : '';
      },
      changeCondition(node) {
        // 获取选中的项
        const checkItem = node.conditionList.filter(item => item.name === node.condition)[0];
        this.$set(node, 'conditionType', checkItem.input_type);
      },
      // 根据条件的不同，填充不同的conditionList数据
      getConditionList(checkItem, node) {
        const typeList = ['SELECT', 'RADIO', 'MULTISELECT', 'CHECKBOX'];
        if (typeList.some(item => item === checkItem.type)) {
          // 数据字典
          this.$set(node, 'loading', true);
          this.$set(node, 'options', []);
          if (checkItem.source_type === 'DATADICT') {
            this.$store.dispatch('datadict/get_data_by_key', {
              key: checkItem.source_uri,
              field_key: checkItem.key,
            }).then((res) => {
              node.options = res.data.map((ite) => {
                const temp = {
                  key: ite.key,
                  name: ite.name,
                };
                return temp;
              });
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                node.loading = false;
              });
          } else if (checkItem.source_type === 'API') {
            this.$store.dispatch('apiRemote/get_data_workflow', {
              kv_relation: checkItem.kv_relation,
              api_instance_id: checkItem.api_instance_id,
            }).then((res) => {
              node.options = res.data.map((ite) => {
                const temp = {
                  key: ite.key,
                  name: ite.name,
                };
                return temp;
              });
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                node.loading = false;
              });
          } else if (checkItem.source_type === 'RPC') {
            this.$store.dispatch('apiRemote/getRpcData', {
              meta: checkItem.meta,
              source_uri: checkItem.source_uri,
            }).then((res) => {
              node.options = res.data.map((ite) => {
                const temp = {
                  key: ite.key,
                  name: ite.name,
                };
                return temp;
              });
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                node.loading = false;
              });
          } else {
            node.options = checkItem.choice.map((ite) => {
              const temp = {
                key: ite.key,
                name: ite.name,
              };
              return temp;
            });
            node.loading = false;
          }
        }
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../../scss/mixins/clearfix.scss';

    .bk-trigger-condition {
        position: relative;
        border: 1px solid #DCDEE5;
        border-top: none;
        background-color: #FAFBFD;
        @include clearfix;
    }
    .bk-condition-name {
        color: #63656E;
        font-size: 12px;
        width: 100px;
        span {
            position: absolute;
            top: 50%;
            left: 50px;
            transform: translate(-50%, -50%);
        }
    }
    .bk-condition-content {
        float: right;
        width: calc(100% - 100px);
        padding: 10px 20px 4px 63px;
        border-left: 1px solid #DCDEE5;
        background-color: #ffffff;
        .bk-content-line {
            position: absolute;
            top: 0;
            left: 130px;
            height: 100%;
            border-left: 1px dashed #DCDEE5;
        }
    }
    .bk-content-step {
        .bk-content-li {
            border: 1px solid #DCDEE5;
            background-color: #FAFBFD;
            padding: 6px;
            margin-bottom: 6px;
            position: relative;
            &:hover {
                .icon-close-circle-shape {
                    display: block;
                }
            }
            .bk-item-none {
                height: calc(50% + 10px);
                top: -10px;
            }
            .bk-content-line {
                left: 20px;
            }
            .icon-close-circle-shape {
                display: none;
                position: absolute;
                top: 6px;
                right: 6px;
                font-size: 16px;
                color: #c4c6cc;
                cursor: pointer;
                &:hover {
                    color: #979ba5;
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
        .bk-content-add {
            font-size: 12px;
            color: #3A84FF;
            position: relative;
            padding-left: 15px;
            span {
                cursor: pointer;
            }
        }
        .bk-content-type {
            position: absolute;
            bottom: -10px;
            left: -50px;
            width: 45px;
            text-align: center;
            background-color: #C4C6CC;
            border-radius: 2px;
            font-size: 12px;
            color: #fff;
            line-height: 18px;
            z-index: 2;
            cursor: pointer;
        }
        .bk-item-line {
            position: absolute;
            top: 50%;
            left: -32px;
            width: 30px;
            border-top: 1px dashed #DCDEE5;
            cursor: default;
        }
        .bk-item-line-none {
            position: absolute;
            top: 50%;
            left: -36px;
            height: calc(50% + 4px);
            width: 5px;
            background: #fff;
            z-index: 2;
            cursor: default;
        }
        .bk-item-over-line {
            height: calc(50% + 34px);
        }
    }
    .bk-content-item {
        .bk-content-item-li {
            @include clearfix;
            margin-bottom: 10px;
            position: relative;
            .bk-content-type {
                left: -65px;
                bottom: -14px;
            }
            .bk-item-line {
                left: -47px;
                width: 45px;
            }
            .bk-item-none {
                height: calc(50% + 11px);
                top: -11px;
                left: -50px;
                background: #FAFBFD;
            }
            .bk-item-none-bottom {
                height: calc(50% + 4px);
                top: 18px;
                left: -50px;
                background: #FAFBFD;
            }
            .bk-between-operat {
                float: left;
                line-height: 32px;
                font-size: 18px;
                .bk-itsm-icon {
                    color: #C4C6CC;
                    margin-right: 9px;
                    cursor: pointer;
                    &:hover {
                        color: #979BA5;
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
        }
        .bk-none-margin {
            margin-bottom: 0px;
        }
        .bk-item-float {
            float: left;
            margin-right: 8px;
        }
    }
    .bk-more-margin {
        padding: 5px 10px 0px 63px;
    }
    .bk-error-info {
        color: #ff5656;
        font-size: 12px;
        line-height: 30px;
    }
</style>
