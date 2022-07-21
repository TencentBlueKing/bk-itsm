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
      <bk-form data-test-id="service-form-autoNode" :label-width="150" :model="formInfo" form-type="vertical">
        <bk-form-item data-test-id="autoNode-input-nodeName" :label="$t(`m.treeinfo['节点名称：']`)" :required="true">
          <bk-input :ext-cls="'bk-form-width'"
            v-model="formInfo.name"
            maxlength="120">
          </bk-input>
        </bk-form-item>
        <desc-info v-model="formInfo.desc"></desc-info>
        <bk-form-item data-test-id="autoNode-select-apiInterface" :label="$t(`m.treeinfo['API接口']`)" :required="true">
          <bk-select :ext-cls="'bk-form-width bk-form-display'"
            v-model="formInfo.api_info.remote_system_id"
            :clearable="false"
            :placeholder="$t(`m.treeinfo['请选择接入系统']`)"
            searchable
            @selected="changeCode">
            <bk-option v-for="option in apiSysList"
              :key="option.id"
              :id="option.id"
              :name="option.name">
            </bk-option>
          </bk-select>
          <template v-if="formInfo.api_info.remote_system_id">
            <bk-select :ext-cls="'bk-form-width bk-form-display'"
              v-model="formInfo.api_info.remote_api_id"
              :loading="isLoading"
              :clearable="false"
              searchable
              @selected="changeMethod">
              <bk-option v-for="option in apiList"
                :key="option.id"
                :id="option.id"
                :name="option.name">
              </bk-option>
            </bk-select>
          </template>
        </bk-form-item>
        <bk-form-item data-test-id="autoNode-select-processor" :label="$t(`m.treeinfo['处理人：']`)" :required="true">
          <div @click="checkStatus.processors = false">
            <deal-person
              ref="processors"
              :value="processorsInfo"
              :show-overbook="true"
              :node-info="configur"
              :exclude-role-type-list="excludeRoleTypeList">
            </deal-person>
          </div>
        </bk-form-item>
      </bk-form>
    </basic-card>
    <template v-if="formInfo.api_info.remote_api_id">
      <basic-card
        v-bkloading="{ isLoading: isLoading }"
        :card-label="$t(`m.treeinfo['输入参数']`)"
        :card-desc="$t(`m.treeinfo['调用该API需要传递的参数信息']`)">
        <!-- get/query/参数 -->
        <div class="bk-param"
          v-if="apiDetail.req_params && apiDetail.req_params.length && apiDetail.req_params[0].name">
          <get-param
            ref="getParam"
            @addNewItem="addNewItem"
            :change-info="configur"
            :state-list="stateList"
            :api-detail="apiDetail">
          </get-param>
        </div>
        <!-- post/body/参数 -->
        <div class="bk-param"
          v-if="apiDetail.req_body && Object.keys(apiDetail.req_body).length && apiDetail.req_body.properties && Object.keys(apiDetail.req_body.properties).length ">
          <post-param
            @addNewItem="addNewItem"
            ref="postParam"
            :change-info="configur"
            :state-list="stateList"
            :api-detail="apiDetail">
          </post-param>
        </div>
      </basic-card>

      <basic-card

        v-bkloading="{ isLoading: isLoading }"
        :card-label="$t(`m.treeinfo['返回数据']`)"
        :card-desc="$t(`m.treeinfo['调用成功后API将会返回的参数信息']`)">
        <!-- 返回数据/选取全局变量 -->
        <div class="bk-param">
          <response-data-node
            ref="responseDataNode"
            v-if="apiDetail.rsp_data && Object.keys(apiDetail.rsp_data).length && apiDetail.rsp_data.properties && Object.keys(apiDetail.rsp_data.properties).length"
            :change-info="configur"
            :state-list="stateList"
            :api-detail="apiDetail">
          </response-data-node>
        </div>
      </basic-card>
            
      <basic-card
        v-bkloading="{ isLoading: isLoading }"
        :card-label="$t(`m.treeinfo['轮询配置']`)"
        :card-desc="$t(`m.treeinfo['当出现异常时，设置重试及结束的条件']`)">
        <nodeCondition
          :form-info="formInfo"
          :line-info="lineInfo">
        </nodeCondition>
      </basic-card>
    </template>
    <basic-card>
      <bk-sideslider
        :is-show.sync="sliderInfo.show"
        :title="sliderInfo.title"
        :width="sliderInfo.width">
        <div class="p20" slot="content" v-if="sliderInfo.show">
          <add-field
            @getRelatedFields="getRelatedFields"
            :change-info="changeInfo"
            :sosp-info="showTabData"
            :workflow="flowInfo.id"
            :state="configur.id"
            @closeShade="closeShade">
          </add-field>
        </div>
      </bk-sideslider>
      <common-trigger-list
        :origin="'state'"
        :node-type="configur.type"
        :source-id="flowInfo.id"
        :sender="configur.id"
        :table="flowInfo.table">
      </common-trigger-list>
      <div class="mt20" style="font-size: 0">
        <bk-button :theme="'primary'"
          data-test-id="autoNode-button-submit"
          :title="$t(`m.treeinfo['确定']`)"
          :loading="secondClick"
          :disabled="!formInfo.api_info.remote_api_id"
          class="mr10"
          @click="submitNode">
          {{$t(`m.treeinfo['确定']`)}}
        </bk-button>
        <bk-button :theme="'default'"
          data-test-id="autoNode-button-close"
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
  import getParam from './addField/getParam.vue';
  import postParam from './addField/postParam.vue';
  import responseDataNode from './autoComponents/responseDataNode.vue';
  import nodeCondition from './autoComponents/nodeCondition.vue';
  import addField from './addField/index.vue';
  import mixins from '../../../commonMix/mixins_api.js';
  import commonTriggerList from '../../taskTemplate/components/commonTriggerList';
  import dealPerson from './components/dealPerson.vue';
  import BasicCard from '@/components/common/layout/BasicCard.vue';
  import { errorHandler } from '../../../../utils/errorHandler';

  export default {
    name: 'autoNode',
    components: {
      getParam,
      postParam,
      responseDataNode,
      nodeCondition,
      addField,
      commonTriggerList,
      dealPerson,
      BasicCard,
      descInfo,
    },
    mixins: [mixins],
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
        isLoading: true,
        lineInfo: {
          // 关系模板
          template: '',
          // 流转条件
          condition_type: '',
          // 关系名称
          name: '',
          checkName: false,
          // 关系
          between: 'and',
          // 条件组
          expressions: [
            {
              type: 'and',
              expressions: [
                {
                  condition: '',
                  key: '',
                  name: '',
                  value: '',
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
            },
          ],
        },
        formInfo: {
          workflow: '',
          name: '',
          desc: '',
          type: 'TASK',
          api_info: {
            remote_system_id: '',
            remote_api_id: '',
            req_params: {},
            req_body: {},
            rsp_data: 'data.info,data.result',
            need_poll: false,
            succeed_conditions: {
              expressions: [],
              type: 'and',
            },
            end_conditions: {
              poll_interval: 1,
              poll_time: 3,
            },
          },
          variables: {
            inputs: [],
            outputs: [],
          },
          processors_type: '',
          processors: '',
        },
        processorsInfo: {
          type: '',
          value: '',
        },
        checkStatus: {
          processors: false,
        },
        organizaInfo: {
          processorsShow: false,
          assignorShow: false,
        },
        // 条件组数组
        fieldList: [],
        // 排除处理人类型
        excludeRoleTypeList: [],
        // API接口
        apiDetail: {},
        // 字段信息
        apiList: [],
        apiSysList: [],
        secondClick: false,
        stateList: [],
        sliderInfo: {
          title: this.$t('m.treeinfo["添加变量"]'),
          show: false,
          width: 700,
        },
        showTabData: {},
        changeInfo: {
          workflow: '',
          id: '',
          key: '',
          name: '',
          type: 'STRING',
          desc: '',
          layout: 'COL_12',
          validate_type: 'REQUIRE',
          choice: [],
          is_builtin: false,
          source_type: 'CUSTOM',
          source_uri: '',
          regex: 'EMPTY',
          custom_regex: '',
          is_tips: false,
          tips: '',
        },
      };
    },
    computed: {
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
    },
    mounted() {
      this.initData();
    },
    methods: {
      async initData() {
        await this.configur;
        await this.flowInfo;
        // 节点名称
        this.formInfo.name = this.configur.name;
        this.formInfo.desc = this.configur.desc;
        this.getRelatedFields();
        this.getExcludeRoleTypeList();
        // 处理人
        if (this.configur.processors_type) {
          this.formInfo.processors_type = this.configur.processors_type;
          this.formInfo.processors = this.formInfo.processors_type === 'PERSON' ? this.configur.processors.split(',') : this.configur.processors;
        }
        // 处理人
        this.processorsInfo = {
          type: this.configur.processors_type,
          value: this.configur.processors,
        };
        // API接口
        if (this.configur.api_info) {
          this.formInfo.api_info = JSON.parse(JSON.stringify(this.configur.api_info));
        }
        await this.getRemoteSystemData();
        await this.getApiTableList(this.formInfo.api_info.remote_system_id);
      },
      // 计算处理人类型需要排除的类型
      getExcludeRoleTypeList() {
        // 不显示的人员类型
        let excludeRoleTypeList = [];
        // 内置节点
        if (this.configur.is_builtin) {
          excludeRoleTypeList = ['BY_ASSIGNOR', 'STARTER', 'VARIABLE'];
        } else {
          excludeRoleTypeList = ['OPEN'];
        }
        // 是否使用权限中心角色
        // if (!this.flowInfo.is_iam_used) {
        //     excludeRoleTypeList.push('IAM')
        // }
        // 处理场景如果不是'DISTRIBUTE_THEN_PROCESS' || 'DISTRIBUTE_THEN_CLAIM'，则去掉派单人指定
        if (this.configur.distribute_type !== 'DISTRIBUTE_THEN_PROCESS' && this.configur.distribute_type !== 'DISTRIBUTE_THEN_CLAIM') {
          excludeRoleTypeList.push('BY_ASSIGNOR');
        }
        if (!this.flowInfo.is_biz_needed) {
          excludeRoleTypeList.push('CMDB');
        }
        this.excludeRoleTypeList = [...['EMPTY', 'API'], ...excludeRoleTypeList];
      },
      // 确认
      async submitNode() {
        // api参数校验
        const isre = await this.apiFz();
        if (!isre) {
          return;
        }
        if (!this.checkLineInfo()) {
          return;
        }
        this.formInfo.workflow = this.flowInfo.id;
        const params = JSON.parse(JSON.stringify(this.formInfo));
        params.is_draft = false;
        params.processors_type = '';
        params.processors = '';
        params.desc = this.formInfo.desc || undefined;
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
        }, (res) => {
          errorHandler(res, this);
        })
          .finally(() => {
            this.secondClick = false;
          });
      },
      // 获取以前的字段/引用变量
      async getRelatedFields() {
        const params = {
          workflow: this.flowInfo.id,
          state: this.configur.id,
          field: '',
        };
        await this.$store.dispatch('apiRemote/get_related_fields', params).then(res => {
          this.stateList = res.data;
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      // 取消
      closeNode() {
        this.$emit('closeConfigur', false);
      },
      closeShade() {
        this.sliderInfo.show = false;
      },
      // 获取Api系统列表
      async getRemoteSystemData() {
        const params = {
          project_key: this.$store.state.project.id,
        };
        await this.$store.dispatch('apiRemote/get_all_remote_system', params).then(res => {
          this.apiSysList = res.data.filter(item => item.is_activated);
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      // 获取Api接口列表数据
      async getApiTableList(id) {
        const params = {
          remote_system: id || '',
        };
        this.isLoading = true;
        await this.$store.dispatch('apiRemote/get_remote_api', params).then(res => {
          this.apiList = res.data.filter(ite => ite.is_activated);
          if (this.configur.api_info) {
            this.apiDetail = Object.assign({}, this.apiList.filter(ite => ite.id === this.configur.api_info.remote_api_id)[0]);
          }
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isLoading = false;
          });
      },
      // 选择api接口
      async changeMethod(valueId) {
        this.lineInfo = {
          // 关系模板
          template: '',
          // 流转条件
          condition_type: '',
          // 关系名称
          name: '',
          checkName: false,
          // 关系
          between: 'and',
          // 条件组
          expressions: [
            {
              type: 'and',
              expressions: [
                {
                  condition: '',
                  key: '',
                  name: '',
                  value: '',
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
            },
          ],
        };
        this.formInfo.variables = {
          inputs: [],
          outputs: [],
        };
        this.formInfo.api_info.need_poll = false;
        this.formInfo.api_info.succeed_conditions = {
          expressions: [],
          type: 'and',
        };
        this.formInfo.api_info.end_conditions = {
          poll_interval: 1,
          poll_time: 3,
        };
        if (this.configur.api_info && (this.configur.api_info.remote_api_id === valueId)) {
          this.formInfo.api_info = JSON.parse(JSON.stringify(this.configur.api_info));
        }
        const valueOption = this.apiList.filter(item => item.id === valueId)[0];
        this.apiDetail = await Object.assign({}, valueOption);
      },
      // 选择接口系统
      changeCode(value) {
        this.formInfo.api_info.remote_api_id = '';
        this.formInfo.api_info.req_params = {};
        this.formInfo.api_info.req_body = {};
        this.formInfo.api_info.rsp_data = '';
        this.getApiTableList(value);
      },
      // 检验轮询配置条件是否填充完整
      checkLineInfo() {
        if (!this.formInfo.api_info.need_poll) {
          return true;
        }
        this.lineInfo.expressions.forEach(item => {
          item.checkInfo = item.expressions.some(node => (!node.condition.toString() || !node.key.toString() || !node.value.toString()));
        });
        const checkStatus = this.lineInfo.expressions.some(item => item.checkInfo);
        if (checkStatus) {
          this.$bkMessage({
            message: this.$t('m.treeinfo["请完善轮询配置！"]'),
            theme: 'warning',
          });
          return false;
        }
        this.formInfo.api_info.succeed_conditions = {
          expressions: [],
          type: this.lineInfo.between,
        };
        this.formInfo.api_info.succeed_conditions.expressions = this.lineInfo.expressions.map(item => {
          const objz = {
            type: item.type,
            expressions: [],
          };
          objz.expressions = item.expressions.map(ite => {
            const obj = {
              key: ite.key.split(',').map(it => {
                it = it.replace(/^\d+\_/, '');
                return it;
              })
                .join('.'),
              condition: ite.condition,
              value: ite.type === 'number' ? Number(ite.value) : (ite.type === 'boolean' ? !!Number(ite.value) : ite.value),
              type: ite.type,
              source: 'global',
              choiceList: [],
            };
            return obj;
          });
          return objz;
        });
        if (!this.formInfo.api_info.end_conditions.poll_interval.toString()
          || !this.formInfo.api_info.end_conditions.poll_time.toString()) {
          this.$bkMessage({
            message: this.$t('m.treeinfo["请完善轮询间隔、次数！"]'),
            theme: 'warning',
          });
          return false;
        }
        this.formInfo.api_info.end_conditions.poll_interval = Number(this.formInfo.api_info.end_conditions.poll_interval);
        this.formInfo.api_info.end_conditions.poll_time = Number(this.formInfo.api_info.end_conditions.poll_time);
        return true;
      },
      // api参数校验
      async apiFz() {
        if (!this.formInfo.name) {
          this.$bkMessage({
            message: this.$t('m.treeinfo["请填写节点名称！"]'),
            theme: 'warning',
          });
          return false;
        }
        if (!this.formInfo.api_info.remote_system_id || !this.formInfo.api_info.remote_api_id) {
          this.$bkMessage({
            message: this.$t('m.treeinfo["请选取接口！"]'),
            theme: 'warning',
          });
          return false;
        }
        // 是否可 滚动
        // let isNow = false
        // 1.query参数检验
        if (this.$refs.getParam) {
          // 过滤
          const necessaryVariableQuery = this.$refs.getParam.paramTableData.filter(ite => ite.is_necessary);
          // 提示 标红
          necessaryVariableQuery.forEach(item => {
            item.isCheck = true;
            item.isSatisfied = item.source_type === 'CUSTOM' ? !!item.value : !!item.value_key;
          });
          // 校验
          const firstNotSatisfiedQuery = necessaryVariableQuery.filter(ite => !ite.isSatisfied)[0];
          if (firstNotSatisfiedQuery) {
            this.$bkMessage({
              message: this.$t('m.treeinfo["请输入GET参数！"]'),
              theme: 'warning',
            });
            // if (!isNow) {
            //     // 滚动
            //     firstNotSatisfiedQuery.el.scrollIntoView(true)
            //     isNow = true
            // }
            return false;
          }
        }
        // 2.body参数检验
        if (this.$refs.postParam) {
          // 过滤
          const necessaryVariableBody = this.$refs.postParam.bodyTableData.filter(ite => ite.is_necessary && (ite.type !== 'object' && ite.type !== 'array'));
          // 提示 标红 验证
          necessaryVariableBody.forEach(item => {
            item.isCheck = true;
            item.isSatisfied = item.source_type === 'CUSTOM' ? item.value.toString() : !!item.value_key;
          });
          const firstNotSatisfied = necessaryVariableBody.filter(ite => !ite.isSatisfied)[0];
          if (firstNotSatisfied) {
            // 展开参数
            this.$refs.postParam.bodyTableData.forEach(item => {
              item.showChildren = true;
              item.isShow = true;
            });
            this.$bkMessage({
              message: this.$t('m.treeinfo["请输入POST参数！"]'),
              theme: 'warning',
            });
            // 滚动 跳转
            // if (!isNow) {
            //     firstNotSatisfied.el.scrollIntoView(true)
            //     isNow = true
            // }
            return false;
          }
        }
        // 提交参数赋值
        this.formInfo.api_info.req_params = !this.$refs.getParam ? {} : await this.listTojson(this.$refs.getParam.paramTableData);
        this.formInfo.api_info.req_body = !this.$refs.postParam ? {} : await this.treeToJson(this.$refs.postParam.bodyTableData.filter(item => (!item.level)));
        // 3.返回参数校验
        const selectKeyList = this.$refs.responseDataNode
          ? this.$refs.responseDataNode.responseTableData.filter(item => (item.isSelectedKey))
          : [];
        // 未选全局变量
        if (!selectKeyList.length) {
          return true;
        }
        if (!selectKeyList.every(item => !!item.isSelectedValue)) {
          // 展开参数
          this.$refs.responseDataNode && this.$refs.responseDataNode.responseTableData.forEach(item => {
            item.showChildren = true;
            item.isShow = true;
          });
          this.$bkMessage({
            message: this.$t('m.treeinfo["勾选全局变量后，请提供变量名"]'),
            theme: 'warning',
          });
          // 标红
          selectKeyList.forEach(item => {
            item.isCheck = true;
            item.isSatisfied = item.isSelectedValue;
          });
          // const firstNotSatisfiedRes = selectKeyList.filter(
          //     ite => {
          //         return !ite['isSatisfied']
          //     }
          // )[0]
          // 滚动 跳转
          // firstNotSatisfiedRes.el.scrollIntoView(true)
          // isNow = true
          return false;
        }
        this.formInfo.variables.outputs = selectKeyList.map(item => {
          const objdata = {
            // "key": "",
            name: '',
            ref_path: '',
            type: item.type,
            source: 'global',
          };
          // objdata.key = JSON.parse(JSON.stringify(item.isSelectedValue))
          objdata.name = JSON.parse(JSON.stringify(item.isSelectedValue));
          objdata.ref_path = item.ancestorsList_str.split(',').map(ite => {
            ite = ite.replace(/^\d+\_/, '');
            return ite;
          })
            .join('.');
          return objdata;
        });
        this.formInfo.api_info.rsp_data = this.formInfo.variables.outputs.map(item => item.ref_path).join(',');
        return true;
      },
      // 多级列表数据转换为JSON数据
      listTojson(listdata) {
        const jsondata = {};
        if (listdata.length) {
          listdata.forEach(item => {
            jsondata[item.name] = item.source_type === 'CUSTOM' ? item.value
              : `\$\{params\_${item.value_key}\}`;
          });
        }
        return jsondata;
      },
      addNewItem(data) {
        this.showTabData = data;
        this.sliderInfo.show = true;
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
        /deep/ .common-section-card-block {
            display: flex;
            flex-direction: column;
        }
        /deep/ .common-section-card-label {
            width: 100%;
            padding: 0 24px;
            .common-section-card-desc {
                width: 100%;
            }
        }
        /deep/ .bk-polling {
            margin-top: -25px;
        }
        /deep/ .common-section-card-body {
            padding: 20px;
        }
        /deep/ .bk-form-width {
            width: 446px;
        }
        /deep/ .common-section-card-block {
            box-shadow: 0 0;
        }
        .api-params-title {
            font-size: 14px;
            margin-bottom: 8px;
            p:nth-child(1) {
                color: #63656e;
                margin-bottom: 4px;
            }
            p:nth-child(2) {
                font-size: 12px;
                color: #929397;
            }
        }
    }
    .bk-basic-info {
        padding-bottom: 20px;
        border-bottom: 1px solid #E9EDF1;
        margin-bottom: 20px;
    }
    .bk-form-width {
        width: 446px;
    }
    .bk-form-display {
        float: left;
        margin-right: 10px;
    }
    .bk-error-info {
        color: #ff5656;
        font-size: 12px;
        line-height: 30px;
    }
</style>
