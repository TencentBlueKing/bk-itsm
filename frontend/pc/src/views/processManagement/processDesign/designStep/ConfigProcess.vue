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
  <div class="bk-design-second">
    <div class="bk-step" v-bkloading="{ isLoading: isDataLoading }">
      <second-flow
        v-if="!isDataLoading"
        ref="flowInfo"
        :add-list="addList"
        :line-list="lineList"
        :flow-info="flowInfo">
      </second-flow>
    </div>
    <div class="bk-second-btn">
      <bk-button theme="default"
        class="mr10"
        :title="$t(`m.treeinfo['上一步']`)"
        :disabled="secondClick"
        @click="previousStep">
        {{ $t('m.treeinfo["上一步"]') }}
      </bk-button>
      <bk-button theme="primary"
        :title="flowInfo.is_draft ? $t(`m.treeinfo['下一步']`) : $t(`m.treeinfo['保存']`)"
        :loading="secondClick"
        @click="submitChart">
        {{flowInfo.is_draft ? $t(`m.treeinfo['下一步']`) : $t(`m.treeinfo['保存']`)}}
      </bk-button>
    </div>
  </div>
</template>
<script>
  import axios from 'axios';
  import secondFlow from '../jsflowCanvas/secondFlow.vue';
  import { errorHandler } from '../../../../utils/errorHandler';

  export default {
    name: 'ConfigProcess',
    components: {
      secondFlow,
    },
    props: {
      flowInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      isNewFlow: {
        type: Boolean,
        default: false,
      },
      isSaveing: {
        type: Boolean,
        default: false,
      },
      processId: {
        type: [String, Number],
        required: true,
      },
    },
    data() {
      return {
        isDataLoading: true,
        // 二次点击
        secondClick: false,
        // 流程图数据
        addList: [],
        lineList: [],
        errorList: [],
        // 配置判断
        statusList: [],
      };
    },
    mounted() {
      this.getFlowChart();
    },
    methods: {
      // 清空数据
      clearInfo() {
        this.addList = [];
      },
      // 获取流程图
      getFlowChart() {
        this.isDataLoading = true;
        axios.all([
          this.$store.dispatch('deployCommon/getStates', { workflow: this.processId }),
          this.$store.dispatch('deployCommon/getChartLink', {
            workflow: this.processId,
            page_size: 1000,
          }),
        ]).then(axios.spread((userResp, reposResp) => {
          this.addList = userResp.data;
          for (let i = 0; i < this.addList.length; i++) {
            this.addList[i].indexInfo = i;
          }
          this.$store.commit('cdeploy/getChart', this.addList);

          this.lineList = reposResp.data.items;
        }))
          .finally(() => {
            this.isDataLoading = false;
          });
      },
      // 立即配置
      configurNode(item) {
        this.statusList = [];
        // 赋值配置信息
        this.$parent.changeConfigur(item);
      },
      showToops(item, index) {
        this.statusList = [];
        if (item.type === 'ROUTER') {
          for (let i = index; i < this.addList.length; i++) {
            if (!this.addList[i].is_draft && this.addList[i].type !== 'END') {
              this.statusList.push(this.addList[i]);
            }
          }
        }
      },
      // 下一步操作or保存流程
      submitChart() {
        this.submitFlow();
        if (this.secondClick) {
          return;
        }
        this.secondClick = true;

        const id = this.processId;
        const params = [];
        this.$store.dispatch('cdeploy/submitChart', { params, id }).then(() => {
          this.$bkMessage({
            message: this.$t('m.treeinfo["保存成功"]'),
            theme: 'success',
          });
          this.$router.push({
            name: 'ProcessEdit',
            params: {
              type: 'edit',
              step: 'processCreate',
            },
            query: {
              processId: this.processId,
            },
          });
        }, (res) => {
          if (res.data && res.data.data) {
            this.errorList = res.data.data.invalid_state_ids;
            this.$refs.flowInfo.errorNodes(this.errorList);
          }
          errorHandler(res, this);
        })
          .finally(() => {
            this.secondClick = false;
          });
      },
      // 保存节点位置
      submitFlow() {
        const lineInfoList = this.$refs.flowInfo.canvasData;
        const params = {
          workflow_id: this.processId,
          transitions: [],
        };
        lineInfoList.lines.forEach((item) => {
          params.transitions.push({
            id: item.lineInfo.id,
            axis: {
              start: item.source.arrow,
              end: item.target.arrow,
            },
          });
        });
        this.$store.dispatch('deployCommon/updateFlowLine', { params }).then(() => {
          // ...
        })
          .catch(() => {
            console.log('error');
          });
      },
      previousStep() {
        this.$router.push({
          name: 'ProcessEdit',
          params: {
            type: 'edit',
            step: 'processInfo',
          },
          query: {
            processId: this.processId,
          },
        });
      },
    },
  };
</script>

<style lang='scss' scoped>
    .bk-design-second {
        background: url(../../../../images/flowbg.png) repeat 0 0 transparent;
        position: relative;
        height: 100%;
    }
    .bk-step {
        height: 100%;
        width: 100%;
    }
    .bk-second-btn {
        position: absolute;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 500;
    }
</style>
