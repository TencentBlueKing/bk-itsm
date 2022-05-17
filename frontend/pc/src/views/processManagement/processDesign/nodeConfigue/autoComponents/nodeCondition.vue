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
  <div class="bk-polling" v-if="formInfo.api_info && lineInfo.expressions">
    <div class="bk-service-name mt20">
      <div class="mt20">
        <bk-switcher v-model="formInfo.api_info.need_poll" size="small"></bk-switcher>
      </div>
    </div>
    <div class="bk-line-form">
      <template v-if="formInfo.api_info.need_poll">
        <div class="bk-service-name">
          <h1 style="padding-left: 10px">
            <span>{{ $t('m.treeinfo["条件组间关系"]') }}</span>
            <span v-bk-tooltips.top="$t(`m.treeinfo['当所有条件组都满足且/或的条件组时，轮询才会结束']`)" class="top-middle">
              <i class="bk-itsm-icon icon-icon-info"></i>
            </span>
          </h1>
        </div>
        <div class="bk-hidden-conditions">
          <div class="bk-form-content" style="margin-left: 0">
            <bk-radio-group v-model="lineInfo.between">
              <bk-radio :value="'and'" :ext-cls="'mr20'">{{$t(`m.treeinfo['且']`)}}</bk-radio>
              <bk-radio :value="'or'">{{$t(`m.treeinfo['或']`)}}</bk-radio>
            </bk-radio-group>
          </div>
        </div>
      </template>
      <template v-if="formInfo.api_info.need_poll && lineInfo.expressions && lineInfo.expressions.length">
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
              <!-- 组织架构 -->
              <div style="width: 210px; float: left; margin-right: 10px; background: white;">
                <div class="bk-search-tree bk-form-width"
                  v-click-outside="closeOther">
                  <div class="bk-search-tree-wrapper" @click.stop="showTree(node)">
                    <span :class="{ 'bk-color-tree': node.organization && node.organization.assignorTree.name }">
                      {{(node.organization && node.organization.assignorTree.name) ? node.organization.assignorTree.name : $t(`m.treeinfo["请选择"]`)}}
                    </span>
                    <i class="bk-select-angle bk-icon icon-framework"></i>
                  </div>
                  <transition name="common-fade">
                    <div class="bk-search-tree-content" v-if="node.organizaInfo && node.organizaInfo.assignorShow">
                      <export-tree
                        :tree-data-list="node.organization.assignorPerson"
                        @toggle="assignorToggle(...arguments, node)"
                        @toggleChildren="toggleChildren(...arguments, node)">
                      </export-tree>
                    </div>
                  </transition>
                </div>
              </div>
              <bk-select style="width: 100px; float: left; margin-right: 10px;"
                v-model="node.condition"
                searchable
                :font-size="'medium'">
                <bk-option v-for="option in globalChoiseFilter(globalChoise.methods, node.type)"
                  :key="option.typeName"
                  :id="option.typeName"
                  :name="option.name">
                </bk-option>
              </bk-select>
              <div style="width: 195px; float: left; margin-right: 10px;">
                <template v-if="node.type === 'boolean'">
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
              </div>
              <div class="bk-between-operat">
                <span class="bk-itsm-icon icon-flow-add" @click="addNode(item, nodeIndex)"></span>
                <i class="bk-itsm-icon icon-flow-reduce"
                  :class="{ 'bk-no-delete': item.expressions.length === 1 }"
                  @click="deleteNode(item, nodeIndex)"></i>
              </div>
            </div>
            <i class="bk-icon icon-close"
              v-if="lineInfo.expressions.length !== 1"
              @click="delteCondition(item, index)"></i>
          </div>
        </div>
        <div :class="{ 'bk-line-padding': scrollTopStatus }">
          <p class="bk-add-between">
            <span @click="addCondition">
              <i class="bk-icon icon-plus-circle"></i>{{ $t('m.treeinfo["添加条件组"]') }}
            </span>
          </p>
        </div>
      </template>
    </div>
    <div class="bk-polling-configu" style="width: 650px" v-if="formInfo.api_info.need_poll">
      <bk-form
        :label-width="200"
        form-type="vertical"
        :model="formInfo">
        <bk-form-item
          :label="$t(`m.treeinfo['轮询间隔']`)"
          :ext-cls="'bk-polling-item'">
          <bk-input :clearable="true"
            type="number"
            :min="1"
            v-model="formInfo.api_info.end_conditions.poll_interval"
            :placeholder="$t(`m.treeinfo['请输入间隔时间']`)">
            <template slot="append">
              <div class="group-text">{{ $t('m.treeinfo["秒"]') }}</div>
            </template>
          </bk-input>
        </bk-form-item>
        <bk-form-item
          :label="$t(`m.treeinfo['轮询次数']`)"
          :ext-cls="'bk-polling-item bk-polling-right'">
          <bk-input :clearable="true"
            type="number"
            :min="1"
            v-model="formInfo.api_info.end_conditions.poll_time"
            :placeholder="$t(`m.treeinfo['请输入轮询次数']`)">
          </bk-input>
        </bk-form-item>
      </bk-form>
    </div>
  </div>
</template>

<script>
  import exportTree from '../../../../commonComponent/treeInfo/exportTree.vue';
  import mixins from '../../../../commonMix/mixins_api.js';

  export default {
    name: 'nodeCondition',
    components: {
      exportTree,
    },
    mixins: [mixins],
    props: {
      lineInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      formInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      changeInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      apiDetail: {
        type: Object,
        default: () => {
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
      stateList: {
        type: Array,
        default() {
          return [];
        },
      },
    },
    data() {
      return {
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
        // 校验
        checkInfo: {
          assignors_type: false,
          assignors: false,
          processors_type: false,
          processors: false,
        },
        scrollTopStatus: 0,
      };
    },
    computed: {
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
    },
    watch: {
      apiDetail() {
        this.initData();
      },
    },
    mounted() {
      this.initData();
    },
    methods: {
      async initData() {
      },
      globalChoiseFilter(choiseMethods, type) {
        return choiseMethods.filter((item) => {
          const stringList = ['==', '!=', 'startswith', 'endswith', 'not contains', 'contains'];
          const numberList = ['==', '!=', '>', '>=', '<', '<='];
          const booleanList = ['==', '!='];
          switch (type) {
            case 'string':
              return stringList.indexOf(item.typeName) !== -1;
            case 'number':
              return numberList.indexOf(item.typeName) !== -1;
            case 'boolean':
              return booleanList.indexOf(item.typeName) !== -1;
            default:
              return true;
          }
        });
      },
      // 新增关系组
      addCondition() {
        const value = {
          type: 'and',
          checkInfo: false,
          expressions: [
            {
              condition: '',
              key: '',
              value: '',
              name: '',
              choiceList: '',
              type: 'string',
              // 组织架构
              organization: {
                assignorPerson: [],
                assignorTree: {},
              },
              organizaInfo: {
                assignorShow: false,
              },
            },
          ],
        };
        value.expressions.forEach((item) => {
          item.organization.assignorPerson = JSON.parse(JSON.stringify(this.lineInfo.expressions[0].expressions[0].organization.assignorPerson));
        });
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
          condition: '',
          key: '',
          value: '',
          name: '',
          choiceList: '',
          type: 'string',
          // 组织架构
          organization: {
            assignorPerson: [],
            assignorTree: {},
          },
          organizaInfo: {
            assignorShow: false,
          },
        };
        value.organization.assignorPerson = JSON.parse(JSON.stringify(this.lineInfo.expressions[0].expressions[0].organization.assignorPerson));
        item.expressions.splice(index + 1, 0, value);
      },
      deleteNode(item, index) {
        if (item.expressions.length === 1) {
          return;
        }
        item.expressions.splice(index, 1);
      },
      showTree(item) {
        const assignorShow = !item.organizaInfo.assignorShow;
        this.closeOther();
        item.organizaInfo.assignorShow = assignorShow;
      },
      closeOther() {
        this.lineInfo.expressions.forEach((item) => {
          item.expressions.forEach((ite) => {
            ite.organizaInfo.assignorShow = false;
          });
        });
      },
      recordCheckFn(tree) {
        tree.checkInfo = false;
        if (tree.children === null || (tree.children && !tree.children.length)) {
          return;
        }
        tree.children.forEach((item) => {
          this.recordCheckFn(item);
        });
      },
      assignorToggle() {
        arguments[1].type = arguments[0].type;
        arguments[1].name = arguments[0].name;
        arguments[1].key = arguments[0].ancestorsList_str;
        arguments[1].organization.assignorPerson.forEach((tree) => {
          this.recordCheckFn(tree);
        });
        arguments[0].checkInfo = true;

        // 选中的数据
        arguments[1].organization.assignorTree = arguments[0];

        this.checkInfo.assignors = false;

        // 关闭窗口
        this.closeTree(arguments[1]);
      },
      closeTree(item) {
        item.organizaInfo.assignorShow = false;
      },
      toggleChildren() {
        arguments[0].showChildren = !arguments[0].showChildren;
        arguments[1].organization.assignorPerson = JSON.parse(JSON.stringify(arguments[1].organization.assignorPerson));
      },
    },
  };
</script>

<style lang="scss" scoped>
    @import '../../../../../scss/mixins/clearfix.scss';

    .bk-line-form {
        .bk-form-content {
            margin-bottom: 10px;
            margin-left: 0px;
        }

        .bk-between-title {
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
        }

        .bk-between-info {
            padding: 16px 22px;
            border: 1px solid #DCDEE5;
            background-color: #fafbfd;
            position: relative;
            width: 650px;

            .bk-between-span {
                color: #666;
                font-size: 14px;
                margin-right: 10px;
            }

            .bk-between-form {
                @include clearfix;
                margin-top: 10px;
                .bk-width100,
                .bk-width210,
                .bk-width195 {
                    width: 100px;
                    float: left;
                    margin-right: 10px;
                    margin-top: 0;
                }
                .bk-width210 {
                    width: 210px;
                }
                .bk-width195 {
                    width: 195px;
                }
            }

            .bk-between-operat {
                float: right;
                line-height: 36px;
                font-size: 18px;
                .bk-itsm-icon {
                    color: #C4C6CC;
                    margin-right: 9px;
                    &:hover {
                        color: #979BA5;
                    }
                    &.bk-no-delete{
                        color: #DCDEE5;
                        cursor: not-allowed;
                        &:hover {
                            color: #DCDEE5;
                        }
                    }
                    cursor: pointer;
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
        }
    }
    .bk-line-padding {
        padding-bottom: 60px;
    }
    .bk-add-between {
        color: #3A84FF;
        cursor: pointer;
        line-height: 20px;
        position: relative;
        padding-left: 20px;
        font-size: 14px;
        .bk-icon {
            position: absolute;
            top: 3px;
            left: 0;
        }
    }
    .bk-polling-item {
        float: left;
        width: 250px;
        margin-top: 8px;
    }
    .bk-polling-right {
        float: right;
    }
    .bk-time {
        width: 30px;
        height: 30px;
        line-height: 30px;
        text-align: center;
    }
</style>
