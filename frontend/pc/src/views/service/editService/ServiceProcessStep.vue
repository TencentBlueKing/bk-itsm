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
  <div :class="[!isShowNodeConfig ? 'process-step' : 'process-step-node-conf']" v-bkloading="{ isLoading: flowDataLoading }">
    <template v-if="!flowDataLoading">
      <second-flow
        v-if="!isShowNodeConfig"
        ref="flowInfo"
        :add-list="nodeList"
        :line-list="lineList"
        :flow-info="flowInfo"
        @handleNodeClick="handleNodeClick">
      </second-flow>
      <div v-else>
        <div class="node-type">{{ nodeType }}
          <i class="bk-itsm-icon icon-itsm-icon-three-one close-node-conf" @click="closeConfigur"></i>
        </div>
        <basic-node
          v-if="configur.type === 'NORMAL'"
          :flow-info="flowInfo"
          :configur="configur"
          @closeConfigur="closeConfigur">
        </basic-node>
        <autoNode
          v-if="configur.type === 'TASK'"
          :flow-info="flowInfo"
          :configur="configur"
          @closeConfigur="closeConfigur">
        </autoNode>
        <sopsNode
          v-if="configur.type === 'TASK-SOPS'"
          :flow-info="flowInfo"
          :configur="configur"
          @closeConfigur="closeConfigur">
        </sopsNode>
        <devopsNode
          v-if="configur.type === 'TASK-DEVOPS'"
          :flow-info="flowInfo"
          :configur="configur"
          @closeConfigur="closeConfigur">
        </devopsNode>
        <signNode
          v-if="configur.type === 'SIGN'"
          :flow-info="flowInfo"
          :configur="configur"
          @closeConfigur="closeConfigur">
        </signNode>
        <approval-node
          v-if="configur.type === 'APPROVAL'"
          :flow-info="flowInfo"
          :configur="configur"
          @closeConfigur="closeConfigur">
        </approval-node>
        <bk-plugin-node
          v-if="configur.type === 'BK-PLUGIN'"
          :flow-info="flowInfo"
          :configur="configur"
          @closeConfigur="closeConfigur">
        </bk-plugin-node>
        <web-hook-node
          v-if="configur.type === 'WEBHOOK'"
          :flow-info="flowInfo"
          :configur="configur"
          @closeConfigur="closeConfigur">
        </web-hook-node>
      </div>
    </template>
  </div>
</template>

<script>
  import axios from 'axios';
  import { errorHandler } from '../../../utils/errorHandler';
  import secondFlow from './flowCanvas/secondFlow.vue';
  import basicNode from '@/views/processManagement/processDesign/nodeConfigue/basicNode.vue';
  import autoNode from '@/views/processManagement/processDesign/nodeConfigue/autoNode.vue';
  import sopsNode from '@/views/processManagement/processDesign/nodeConfigue/sopsNode.vue';
  import signNode from '@/views/processManagement/processDesign/nodeConfigue/signNode.vue';
  import devopsNode from '@/views/processManagement/processDesign/nodeConfigue/devopsNode.vue';
  import ApprovalNode from '@/views/processManagement/processDesign/nodeConfigue/ApprovalNode.vue';
  import webHookNode from '@/views/processManagement/processDesign/nodeConfigue/webHookNode.vue';
  import bkPluginNode from '@/views/processManagement/processDesign/nodeConfigue/bkPluginNode.vue';

  export default {
    name: 'ServiceProcessStep',
    components: {
      secondFlow,
      basicNode,
      autoNode,
      sopsNode,
      signNode,
      ApprovalNode,
      devopsNode,
      bkPluginNode,
      webHookNode,
    },
    props: {
      serviceInfo: {
        type: Object,
        default: () => ({}),
      },
      flowInfo: {
        type: Object,
        default: () => ({}),
      },
    },
    data() {
      return {
        flowDataLoading: false,
        isShowNodeConfig: false,
        nodeList: [],
        lineList: [],
        configur: {},
      };
    },
    computed: {
      processId() {
        return this.serviceInfo.workflow_id;
      },
      nodeType() {
        const nodoTypeList = {
          'TASK-DEVOPS': this.$t('m["蓝盾节点"]'),
          'TASK-SOPS': this.$t('m["标准运维节点"]'),
          NORMAL: this.$t('m["手动节点"]'),
          TASK: this.$t('m["任务节点"]'),
          APPROVAL: this.$t('m["审批节点"]'),
          SIGN: this.$t('m["会签节点"]'),
          WEBHOOK: this.$t('m["WEBHOOK节点"]'),
          'BK-PLUGIN': this.$t('m["蓝鲸插件节点"]'),
        };
        return nodoTypeList[this.configur.type];
      },
    },
    watch: {
      isShowNodeConfig(val) {
        this.$emit('setConfigStatus', val);
      },
    },
    created() {
      this.$emit('setConfigStatus', this.isShowNodeConfig);
    },
    mounted() {
      if (this.processId) {
        this.getFlowChart();
      }
    },
    methods: {
      // 获取流程图
      getFlowChart() {
        this.flowDataLoading = true;
        axios.all([
          this.$store.dispatch('deployCommon/getStates', { workflow: this.processId }),
          this.$store.dispatch('deployCommon/getChartLink', {
            workflow: this.processId,
            page_size: 1000,
          }),
        ]).then(axios.spread((userResp, reposResp) => {
          this.nodeList = userResp.data;
          this.lineList = reposResp.data.items;
        }))
          .finally(() => {
            this.flowDataLoading = false;
          });
      },
      handleNodeClick(data) {
        this.isShowNodeConfig = true;
        this.configur = data;
      },
      closeConfigur() {
        this.isShowNodeConfig = false;
        this.configur = {};
        this.$emit('updateFlowInfo');
      },
      // 保存节点位置
      submitFlow() {
        const lineInfoList = this.$refs.flowInfo.canvasData;
        const params = {
          workflow_id: this.processId,
          transitions: [],
        };
        lineInfoList.lines.forEach(item => {
          params.transitions.push({
            id: item.lineInfo.id,
            axis: {
              start: item.source.arrow,
              end: item.target.arrow,
            },
          });
        });
        this.$store.dispatch('deployCommon/updateFlowLine', { params }).catch(res => {
          errorHandler(res, this);
        });
      },
      saveProcess() {
        const id = this.processId;
        const params = [];
        return this.$store.dispatch('cdeploy/submitChart', { params, id }).then(() => {
          this.$bkMessage({
            message: this.$t('m.treeinfo["保存成功"]'),
            theme: 'success',
          });
        }, (res) => {
          if (res.data && res.data.data) {
            this.errorList = res.data.data.invalid_state_ids;
            this.$refs.flowInfo.errorNodes(this.errorList);
          }
          errorHandler(res, this);
          return { data: { result: false } };
        });
      },
      validate() {
        this.submitFlow();
        return this.saveProcess();
      },
    },
  };
</script>
<style lang='scss' scoped>
.process-step {
    height: 100%;
}
.process-step-node-conf {
    margin: 24px auto;
    width: 1000px;
    /deep/ .bk-basic-node {
        padding: 0;
    }
}
.node-type {
    background-color: #fafbfd;
    line-height: 48px;
    height: 48px;
    width: 100%;
    font-size: 14px;
    padding: 0 24px;
}
.close-node-conf {
    font-size: 20px;
    font-weight: 500;
    float: right;
    line-height: 48px;
    cursor: pointer;
    &:hover {
        color: red;
    }
}
</style>
