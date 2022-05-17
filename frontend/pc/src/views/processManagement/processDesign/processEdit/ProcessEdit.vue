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
  <div class="process-edit" v-bkloading="{ isLoading: isloading }">
    <!-- title -->
    <div class="is-title" :class="{ 'bk-title-left': !sliderStatus }">
      <p
        v-if="!isShowNodeConfig"
        class="bk-come-back"
        @click="onBackProcessHome">
        <arrows-left-icon></arrows-left-icon>
        <template v-if="isNewFlow"> {{ $t('m.deployPage["新增设计流程"]') }} </template>
        <template v-else> {{ flowInfo.name }} </template>
      </p>
      <p v-else class="bk-come-back" @click="closeConfigur">
        <arrows-left-icon></arrows-left-icon>
        <span>{{ $t('m.deployPage["配置节点"]') }}</span>
      </p>
    </div>
    <!-- 流程步骤 -->
    <div class="bk-itsm-tree">
      <div class="bk-tree-content">
        <div class="bk-tree-first" v-for="(item, index) in lineList" :key="item.id">
          <div class="bk-tree-shadow" @click="onChangeStep(item, index)">
            <span
              class="bk-tree-step"
              :class="{
                'bk-tree-primary': item.type === 'primary',
                'bk-tree-success': item.type === 'success',
                'bk-tree-error': item.type === 'error' }">
              <i
                v-if="item.type === 'success'"
                class="bk-icon icon-check-1">
              </i>
              <i
                v-if="item.type === 'error'"
                class="bk-icon icon-close"
                style="font-size: 18px;">
              </i>
              <span
                v-if="item.type !== 'success' && item.type !== 'error'">
                {{item.id}}
              </span>
            </span>
            <span
              class="bk-tree-normal bk-tree-cursor"
              :class="{ 'bk-tree-info': item.type !== 'normal' }">{{item.name}}</span>
          </div>
          <span class="bk-tree-line" v-if="item.id !== lineList.length"></span>
        </div>
      </div>
    </div>
    <div v-if="!isShowNodeConfig" class="bk-design-step">
      <create-process
        v-if="step === 'processInfo'"
        :is-saveing="isSaveing"
        :is-new-flow="isNewFlow"
        :process-id="processId"
        :flow-info="flowInfo"
        @saveFlowInfo="saveFlowInfo"
        @onBusinessChange="onBusinessChange">
      </create-process>
      <config-process
        v-if="step === 'pipelineDesign'"
        :flow-info="flowInfo"
        :process-id="processId"
        :is-new-flow="isNewFlow">
      </config-process>
      <activation-process
        v-if="step === 'processCreate'"
        :flow-info="flowInfo"
        :process-id="processId"
        :is-new-flow="isNewFlow"
        :business="business">
      </activation-process>
    </div>
    <!-- 流程节点配置 -->
    <div v-else class="node-config-wrap">
      <basic-node
        v-if="configur.id && configur.type === 'NORMAL'"
        :flow-info="flowInfo"
        :configur="configur"
        @closeConfigur="closeConfigur">
      </basic-node>
      <autoNode
        v-if="configur.id && configur.type === 'TASK'"
        :flow-info="flowInfo"
        :configur="configur"
        @closeConfigur="closeConfigur">
      </autoNode>
      <sopsNode
        v-if="configur.id && configur.type === 'TASK-SOPS'"
        :flow-info="flowInfo"
        :configur="configur"
        @closeConfigur="closeConfigur">
      </sopsNode>
      <signNode
        v-if="configur.id && configur.type === 'SIGN'"
        :flow-info="flowInfo"
        :configur="configur"
        @closeConfigur="closeConfigur">
      </signNode>
      <approval-node
        v-if="configur.id && configur.type === 'APPROVAL'"
        :flow-info="flowInfo"
        :configur="configur"
        @closeConfigur="closeConfigur">
      </approval-node>
    </div>
  </div>
</template>

<script>
  import CreateProcess from '../designStep/CreateProcess.vue';
  import ConfigProcess from '../designStep/ConfigProcess.vue';
  import ActivationProcess from '../designStep/ActivationProcess.vue';
  import basicNode from '../nodeConfigue/basicNode.vue';
  import autoNode from '../nodeConfigue/autoNode.vue';
  import sopsNode from '../nodeConfigue/sopsNode.vue';
  import signNode from '../nodeConfigue/signNode.vue';
  import ApprovalNode from '../nodeConfigue/ApprovalNode.vue';
  import { errorHandler } from '../../../../utils/errorHandler';

  export default {
    name: 'ProcessEdit',
    components: {
      CreateProcess,
      ConfigProcess,
      ActivationProcess,
      basicNode,
      autoNode,
      sopsNode,
      signNode,
      ApprovalNode,
    },
    props: {
      /**
       * 当前步骤
       * processInfo
       * pipelineDesign
       * processCreate
       */
      step: {
        type: String,
        required: true,
      },
      // 流程 id
      processId: {
        type: [String, Number],
        default: '',
      },
      /**
       * 类型 new | edit
       */
      type: {
        type: String,
        required: true,
      },
    },
    data() {
      return {
        isloading: false,
        business: false,
        // 保存中
        isSaveing: false,
        // 显示配置页面
        isShowNodeConfig: false,
        // 流程详情信息
        flowInfo: {},
        // 配置节点
        configur: {},
      };
    },
    computed: {
      sliderStatus() {
        return this.$store.state.common.slideStatus;
      },
      isNewFlow() {
        return this.type === 'new';
      },
      /**
       * 是否为草稿，只有第三步提交成功后才不是草稿
       */
      isDraft() {
        return this.flowInfo.is_draft === true;
      },
      lineList() {
        /**
         * type
         * normal 没填写
         * primary 当前，填写中
         * success 已填写过
         * error 错误
         */
        const self = this;
        return [
          {
            id: 1,
            name: this.$t('m.deployPage["填写流程信息"]'),
            step: 'processInfo',
            type: (() => {
              if (self.step !== 'processInfo') {
                return 'success';
              }
              return 'primary';
            })(),
          },
          {
            id: 2,
            name: this.$t('m.deployPage["定义与配置流程"]'),
            step: 'pipelineDesign',
            type: (() => {
              if (self.step === 'pipelineDesign') {
                return 'primary';
              }
              if (self.step !== 'pipelineDesign' && self.processId) {
                return 'success';
              }
              return 'normal';
            })(),
          },
          {
            id: 3,
            name: this.$t('m.deployPage["流程启用设置"]'),
            step: 'processCreate',
            type: (() => {
              if (self.step === 'processCreate') {
                return 'primary';
              }
              if (self.step !== 'processCreate' && self.flowInfo.is_draft === false) {
                return 'success';
              }
              return 'normal';
            })(),
          },
        ];
      },
    },
    mounted() {
      if (!this.isNewFlow) {
        this.getFlowDetailInfo();
      }
      this.getArrangeInfo();
    },
    methods: {
      // 获取流程详情
      getFlowDetailInfo() {
        this.isloading = true;
        this.$store.dispatch('design/getFlowDetail', { params: this.processId }).then((res) => {
          const { data } = res;
          this.flowInfo = data;
          this.business = data.is_biz_needed;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isloading = false;
          });
      },
      // 全局常量信息，此处获取节点排列信息
      getArrangeInfo() {
        this.$store.dispatch('cdeploy/getConfigurInfo').then((res) => {
          const value = res.data;
          const globalInfo = {};
          for (const key in value) {
            const listInfo = [];
            for (let i = 0; i < value[key].length; i++) {
              listInfo.push({
                id: i + 1,
                name: value[key][i][1] ? value[key][i][1] : this.$t('m.deployPage["无"]'),
                typeName: value[key][i][0],
              });
            }
            globalInfo[key] = listInfo;
          }
          this.$store.commit('cdeploy/changeConfigur', globalInfo);
        }, (res) => {
          errorHandler(res, this);
        });
      },
      // 改变步骤
      onChangeStep(item) {
        if (item.step === this.step || item.type !== 'success') {
          return false;
        }
        this.closeConfigur();
        this.$router.push({
          name: 'ProcessEdit',
          params: {
            type: 'edit',
            step: item.step,
          },
          query: {
            processId: this.processId,
          },
        });
      },
      // 显示配置信息
      changeConfigur(item) {
        this.configur = item;
        this.isShowNodeConfig = true;
      },
      // 关闭配置
      closeConfigur() {
        this.isShowNodeConfig = false;
      },
      /**
       * 新建/保存流程信息
       * @param { Object } params 保存参数
       * @param { Boolean } new 是否新建
       */
      saveFlowInfo(params, isNew) {
        const api = isNew ? 'cdeploy/createFlow' : 'cdeploy/changeDesign';
        this.isSaveing = true;
        const id = this.processId;
        this.$store.dispatch(api, { params, id }).then((res) => {
          this.$bkMessage({
            message: this.$t('m.deployPage["保存成功"]'),
            theme: 'success',
          });
          if (this.isNewFlow) {
            this.$router.push({
              name: 'ProcessEdit',
              params: {
                type: 'edit',
                step: 'pipelineDesign',
              },
              query: {
                processId: res.data.id,
              },
            });
            // 获取信息
            this.$nextTick(() => {
              this.getFlowDetailInfo();
            });
            return;
          }
          const { data } = res;
          this.flowInfo = data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isSaveing = false;
          });
      },
      onBusinessChange(value) {
        this.business = value;
      },
      // 跳转到 process 列表
      onBackProcessHome() {
        this.$router.push({
          name: 'ProcessHome',
        });
      },
    },
  };
</script>

<style lang="scss" scoped>
    @import '../../../../scss/mixins/scroller.scss';
    .process-edit {
        padding-top: 53px;
        height: 100%;
        .node-config-wrap {
            height: calc(100% - 112px);
            overflow: scroll;
            @include scroller;
        }
    }
</style>
