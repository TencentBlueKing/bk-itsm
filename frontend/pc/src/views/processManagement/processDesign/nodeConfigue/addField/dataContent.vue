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
  <div class="bk-data-content" @click="closeError">
    <template v-if="formInfo.source_type === 'CUSTOM'">
      <div class="bk-custom-line"
        :class="{ 'mb20': itemIndex !== fieldInfo.list.length - 1 }"
        v-for="(item, itemIndex) in fieldInfo.list"
        :key="itemIndex">
        <div class="bk-costom-form">
          <bk-input :maxlength="120"
            :ext-cls="'bk-custom-input'"
            :clearable="true"
            :disabled="(changeInfo.is_builtin || changeInfo.source === 'TABLE') && formInfo.key !== 'bk_biz_id'"
            v-model="item.name"
            :placeholder="$t(`m.treeinfo['请输入选项名']`)"
            @blur="putChar(item, itemIndex)">
          </bk-input>
          <template v-if="formInfo.type === 'TABLE'">
            <bk-checkbox style="float: left; margin-right: 10px; line-height: 32px;"
              :true-value="trueStatus"
              :false-value="falseStatus"
              v-model="item.required">
              {{ $t(`m.treeinfo['必填']`) }}
            </bk-checkbox>
          </template>
          <bk-input :ext-cls="'bk-custom-input'"
            :disabled="(changeInfo.is_builtin || changeInfo.source === 'TABLE' || (changeInfo.meta && changeInfo.meta.code === 'APPROVE_RESULT')) && formInfo.key !== 'bk_biz_id'"
            v-model="item.key"
            :placeholder="$t(`m.treeinfo['请输入选项ID']`)">
          </bk-input>
          <div class="bk-custom-icon">
            <i class="bk-itsm-icon icon-flow-add" :class="{ 'bk-no-delete': (changeInfo.meta && changeInfo.meta.code === 'APPROVE_RESULT') }" @click="addDataLine(item, itemIndex)"></i>
            <i class="bk-itsm-icon icon-flow-reduce"
              :class="{ 'bk-no-delete': fieldInfo.list.length === 1 || (changeInfo.meta && changeInfo.meta.code === 'APPROVE_RESULT') }"
              @click="deleteDataLine(item, itemIndex)"></i>
          </div>

        </div>
        <div class="bk-field-error-tip">
          <p class="bk-field-error" v-if="item.nameCheck">{{ $t('m.deployPage["名称不能为空且不能重复"]') }}</p>
          <template v-else>
            <p class="bk-field-error" v-if="item.keyCheck">{{ $t('m.deployPage["名称ID为英文数字及下划线且不能重复"]') }}</p>
          </template>
        </div>
      </div>
    </template>
    <template v-if="formInfo.source_type === 'API'">
      <div class="bk-api-param" v-if="apiInfo.remote_system_id && apiInfo.remote_api_id">
        <!-- get/query/参数 -->
        <div class="bk-param"
          v-if="apiDetail.req_params && apiDetail.req_params.length && apiDetail.req_params[0].name">
          <get-param
            ref="getParam"
            :entry="'addField'"
            :form-info="formInfo"
            :change-info="changeInfo"
            :state-list="stateList"
            :api-detail="apiDetail">
          </get-param>
        </div>
        <!-- post/body/参数 -->
        <div class="bk-param"
          v-if="apiDetail.req_body && Object.keys(apiDetail.req_body).length && apiDetail.req_body.properties && Object.keys(apiDetail.req_body.properties).length ">
          <post-param
            ref="postParam"
            :entry="'addField'"
            :form-info="formInfo"
            :change-info="changeInfo"
            :state-list="stateList"
            :api-detail="apiDetail">
          </post-param>
        </div>
        <!-- 返回数据/可选数组Tree -->
        <div class="bk-param"
          v-if="apiDetail.rsp_data && Object.keys(apiDetail.rsp_data).length && apiDetail.rsp_data.properties && Object.keys(apiDetail.rsp_data.properties).length">
          <response-data
            ref="responseData"
            :remote-api-iid="apiInfo.remote_api_id"
            :change-info="changeInfo"
            :form-info="formInfo"
            :state-list="stateList"
            :api-detail="apiDetail">
          </response-data>
        </div>
      </div>
    </template>
    <template v-if="formInfo.source_type === 'RPC'">
      <div class="bk-api-param" v-if="prcTable.length">
        <div class="bk-param">
          <get-rpc-param
            ref="getRpcParam"
            :form-info="formInfo"
            :change-info="changeInfo"
            :state-list="stateList"
            :prc-table="prcTable">
          </get-rpc-param>
        </div>
      </div>
    </template>
  </div>
</template>
<script>
  import pinyin from 'pinyin';
  import getParam from './getParam.vue';
  import postParam from './postParam.vue';
  import responseData from './responseData.vue';
  import getRpcParam from './getRpcParam.vue';
  import mixins from '../../../../commonMix/mixins_api.js';
  import { errorHandler } from '../../../../../utils/errorHandler';

  export default {
    name: 'dataContent',
    components: {
      getParam,
      postParam,
      responseData,
      getRpcParam,
    },
    mixins: [mixins],
    props: {
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
      apiInfo: {
        type: Object,
        default() {
          return {
            remote_system_id: '',
            remote_api_id: '',
            req_params: {},
            req_body: {},
            rsp_data: '',
          };
        },
      },
      fieldInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      kvRelation: {
        type: Object,
        default() {
          return {};
        },
      },
      prcTable: {
        type: Array,
        default() {
          return [];
        },
      },
    },
    data() {
      return {
        stateList: [],
        trueStatus: true,
        falseStatus: false,
      };
    },
    computed: {
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
    },
    mounted() {
      this.getRelatedFields();
    },
    methods: {
      // 自定义类型
      addDataLine(item, index) {
        if (this.changeInfo.meta && this.changeInfo.meta.code === 'APPROVE_RESULT') {
          return;
        }
        const valueInfo = {
          name: '',
          key: '',
          required: false,
          nameCheck: false,
          keyCheck: false,
        };
        this.fieldInfo.list.splice(index + 1, 0, valueInfo);
      },
      deleteDataLine(item, index) {
        if (this.fieldInfo.list.length === 1 || (this.changeInfo.meta && this.changeInfo.meta.code === 'APPROVE_RESULT')) {
          return;
        }
        this.fieldInfo.list.splice(index, 1);
      },
      closeError() {
        this.fieldInfo.list.forEach((item) => {
          item.nameCheck = false;
          item.keyCheck = false;
        });
      },
      // API
      // 获取节点以前的字段--引用字段/变量
      getRelatedFields() {
        if (!this.state) {
          return;
        }
        const params = {
          workflow: this.workflow,
          state: this.state,
          field: '',
        };
        this.$store.dispatch('apiRemote/get_related_fields', params).then((res) => {
          this.stateList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
          });
      },
      // 计算祖先元素type是列表array的有几个
      countArrayAncestors(data) {
        const ids = [];
        const countArrayAncestorsStep = function (item) {
          if (item.parentInfo.type === 'array') {
            ids.push(item);
            countArrayAncestorsStep(item.parentInfo);
          }
          if (item.parentInfo.type === 'object') {
            countArrayAncestorsStep(item.parentInfo);
          }
        };
        countArrayAncestorsStep(data);
        return ids;
      },
      // 多级列表数据转换为JSON数据
      listTojson(listdata) {
        const jsondata = {};
        if (listdata.length) {
          listdata.forEach((item) => {
            /* eslint-disable */
                        jsondata[item.name] = item.source_type === 'CUSTOM' ? item.value
                            : `\$\{params\_${item.value_key}\}`;
                        /* eslint-disable */
                    });
                }
                return jsondata;
            },
            // api参数检验
            async apiFz() {
                this.apiInfo.req_params = !this.$refs.getParam ? {} : await this.listTojson(this.$refs.getParam.paramTableData);
                this.apiInfo.req_body = !this.$refs.postParam ? {} : await this.treeToJson(this.$refs.postParam.bodyTableData.filter(item => (!item.level)));
                let isNow = false;
                // 1.query参数检验
                if (this.$refs.getParam) {
                    // 过滤
                    const necessaryVariableQuery = this.$refs.getParam.paramTableData.filter(ite => ite.is_necessary);
                    // 提示 标红
                    necessaryVariableQuery.forEach((item) => {
                        item.isCheck = true;
                        item.isSatisfied = item.source_type === 'CUSTOM' ? !!item.value : !!item.value_key;
                    });
                    // 校验
                    const firstNotSatisfiedQuery = necessaryVariableQuery.filter(ite => !ite.isSatisfied)[0];
                    if (firstNotSatisfiedQuery) {
                        this.$bkMessage({
                            message: this.$t('m.treeinfo["请输入GET参数！"]'),
                            theme: 'error',
                        });
                        if (!isNow) {
                            // 滚动
                            firstNotSatisfiedQuery.el.scrollIntoView(true);
                            isNow = true;
                        }
                        return false;
                    }
                }
                // 2.body参数检验
                if (this.$refs.postParam) {
                    // 过滤
                    const necessaryVariableBody = this.$refs.postParam.bodyTableData.filter(ite => ite.is_necessary && (ite.type !== 'object' && ite.type !== 'array'));
                    // 提示 标红 验证
                    necessaryVariableBody.forEach((item) => {
                        item.isCheck = true;
                        item.isSatisfied = item.source_type === 'CUSTOM' ? item.value.toString() : !!item.value_key;
                    });
                    const firstNotSatisfied = necessaryVariableBody.filter(ite => !ite.isSatisfied)[0];
                    if (firstNotSatisfied) {
                        // 展开参数
                        this.$refs.postParam.bodyTableData.forEach((item) => {
                            item.showChildren = true;
                            item.isShow = true;
                        });
                        this.$bkMessage({
                            message: this.$t('m.treeinfo["请输入POST参数！"]'),
                            theme: 'error',
                        });
                        // 滚动 跳转
                        if (!isNow) {
                            firstNotSatisfied.el.scrollIntoView(true);
                            isNow = true;
                        }
                        return false;
                    }
                }
                // 3.返回参数检验
                if (!this.$refs.responseData) {
                    this.$bkMessage({
                        message: this.$t('m.treeinfo["数据为空，请联系管理员"]'),
                        theme: 'error',
                    });
                    return false;
                }
                const selectKey = this.$refs.responseData.responseTableData.filter(item => (item.isSelectedKey))[0];
                const selectValue = this.$refs.responseData.responseTableData.filter(item => (item.isSelectedValue))[0];
                if (!selectKey || !selectValue) {
                    this.$bkMessage({
                        message: this.$t('m.treeinfo["请选择返回数据"]'),
                        theme: 'error',
                    });
                    this.$refs.responseData.isCheck = true;
                    return false;
                }
                const selectKeyList = [...JSON.parse(JSON.stringify(selectKey.ancestorsList)), selectKey.primaryKey];
                const selectValueList = [...JSON.parse(JSON.stringify(selectValue.ancestorsList)), selectValue.primaryKey];
                const selectArrayKey = await this.countArrayAncestors(selectKey);
                const selectArrayValue = await this.countArrayAncestors(selectValue);
                const selectArrayKeyNum = selectKeyList.indexOf(selectArrayKey[0].primaryKey);
                const selectArrayValueNum = selectValueList.indexOf(selectArrayValue[0].primaryKey);
                if (selectArrayKey.length !== 1 || selectArrayValue.length !== 1) {
                    return false;
                }
                // 参数拼接成后台所需的格式
                this.apiInfo.rsp_data = selectKeyList.slice(0, selectArrayKeyNum).map((item) => {
                    // eslint-disable-next-line
                    item = item.replace(/^\d+\_/, '');
                    return item;
                })
                    .join('.');
                this.kvRelation.key = selectKeyList.slice(selectArrayKeyNum + 1).map((item) => {
                    // eslint-disable-next-line
                    item = item.replace(/^\d+\_/, '');
                    return item;
                })
                    .join('.');
                this.kvRelation.name = selectValueList.slice(selectArrayValueNum + 1).map((item) => {
                    // eslint-disable-next-line
                    item = item.replace(/^\d+\_/, '');
                    return item;
                })
                    .join('.');
                return true;
            },
            putChar(node, index) {
                if (node.key) {
                    return;
                }
                this.fieldInfo.list[index].key = '';
                const transfer = pinyin(this.fieldInfo.list[index].name, {
                    style: pinyin.STYLE_NORMAL,
                    heteronym: false,
                });
                transfer.forEach((item) => {
                    this.fieldInfo.list[index].key = `${this.fieldInfo.list[index].key}${item}`;
                });
                this.fieldInfo.list[index].key = this.fieldInfo.list[index].key.toUpperCase();
                this.fieldInfo.list[index].key = this.fieldInfo.list[index].key.replace(/\ /g, '_');
                if (this.fieldInfo.list[index].key.length >= 32) {
                    this.fieldInfo.list[index].key = this.fieldInfo.list[index].key.substr(0, 32);
                }
            },
        },
    };
</script>

<style lang='scss' scoped>
    @import '../../../../../scss/mixins/clearfix.scss';
    .bk-custom-line {
        @include clearfix;
        display: flex;
        align-items: center;
        flex-direction: column;
        .bk-costom-form {
            width: 100%;
        }
        .bk-field-error-tip {
            width: 100%;
            .bk-field-error {
                float: left;
                color: #ff5656;
                font-size: 12px;
            }
        }
        .bk-custom-input {
            width: 36%;
            margin-right: 10px;
        }

        .bk-custom-icon {
            display: inline-block;
            line-height: 32px;
            font-size: 18px;
            margin-left: 4px;

            .bk-itsm-icon {
                color: #C4C6CC;
                margin-right: 9px;
                cursor: pointer;
                &:hover {
                    color: #979BA5;
                }
            }
            .bk-no-delete{
                color: #DCDEE5;
                cursor: not-allowed;
                &:hover {
                    color: #DCDEE5;
                }
            }
        }
    }
</style>
