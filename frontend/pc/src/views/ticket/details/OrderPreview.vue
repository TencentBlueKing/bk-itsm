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
  <div class="bk-order-preview">
    <!-- 工单进度预览 -->
    <div class="bk-basic-head bk-change">
      <span class="bk-head-icon" v-if="false"></span>
      <!-- <i class="bk-icon icon-order-progress"></i> -->
      <span v-if="false">{{ $t('m.newCommon["工单进度预览"]') }}</span>
      <span data-test-id="ticket_button_progressFullscreen" class="bk-font-icon" @click="openFull" title="全屏">
        <i class="bk-itsm-icon icon-order-open cus-order-open"></i>
      </span>
    </div>
    <!-- 流程预览图 -->
    <div class="bk-order-flow" v-bkloading="{ isLoading: isDataLoading }">
      <template v-if="!isDataLoading && !fullStatus">
        <preview
          ref="preview"
          :add-list="addList"
          :line-list="lineList"
          :preview-info="previewInfo">
        </preview>
      </template>
    </div>
    <!-- 底部隔层 -->
    <div class="bk-current-bottom"></div>
    <!-- 查看全图 -->
    <div class="bk-preview-full" v-if="fullStatus">
      <div class="bk-basic-head">
        <span class="bk-head-icon"></span>
        <!-- <i class="bk-icon icon-order-progress"></i> -->
        <span>{{ $t('m.newCommon["工单进度预览"]') }}</span>
        <span class="bk-font-icon" @click="closeFull" title="小屏">
          <i class="bk-itsm-icon icon-order-close cus-order-open" style="margin-right: 0;"></i>
        </span>
      </div>
      <div class="bk-full-div">
        <preview
          ref="preview"
          :add-list="addList"
          :line-list="lineList"
          :preview-info="previewInfo"
          :full-status="fullStatus">
        </preview>
      </div>
    </div>
    <!-- 单个节点的详情信息 -->
    <div class="bk-node-content">
      <bk-sideslider
        :show-mask="false"
        :is-show.sync="nodeContent.isShow"
        :title="nodeContent.title"
        :width="nodeContent.width"
        :quick-close="nodeContent.quick">
        <div slot="content" v-if="nodeContent.isShow">
          <node-info
            @initInfo="initInfo"
            :node-list="nodeInfo"
            :read-only="nodeContent.isShow"
            :current-step-list="currentStepList"
            :basic-infomation="basicInfomation"
            :open-node-info="openNodeInfo"
            :is-loading="isNodeLoading"
            @closeSlider="closeNodeContent">
          </node-info>
        </div>
      </bk-sideslider>
    </div>
  </div>
</template>

<script>
  import axios from 'axios';
  import preview from '../../commonComponent/preview';
  import NodeInfo from './nodeInfo/index.vue';
  import { errorHandler } from '@/utils/errorHandler';

  export default {
    name: 'OrderPreview',
    components: {
      preview,
      NodeInfo,
    },
    props: {
      // 单据信息
      basicInfomation: {
        type: Object,
        default() {
          return {};
        },
      },
      currentStepList: {
        type: Array,
        default() {
          return [];
        },
      },
      loadingInfo: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        clickSecond: false,
        addList: [],
        lineList: [],
        nodeList: [],
        isDataLoading: true,
        fullStatus: false,
        previewInfo: {
          canClick: true,
          narrowSize: 0.7,
        },
        // 右侧弹窗内容
        nodeContent: {
          isShow: false,
          title: '',
          width: 600,
          quick: false,
        },
        // 打开节点信息
        openNodeInfo: {},
        nodeInfo: [],
        isNodeLoading: true,
      };
    },
    computed: {},
    watch: {
      'basicInfomation.id'() {
        this.getFlowInfo();
      },
    },
    mounted() {
      this.getFlowInfo();
      // 轮询单据详情的数据
      this.getStateStatus();
      clearInterval(this.$store.state.deployOrder.intervalInfo.lines);
      this.$store.state.deployOrder.intervalInfo.lines = setInterval(() => {
        this.intervalLines();
      }, 2000);
    },
    methods: {
      initInfo() {
        this.$emit('reloadTicket');
      },
      // 获取流程图数据
      getFlowInfo() {
        this.isDataLoading = true;
        const id = this.basicInfomation.flow_id;
        axios.all([
          this.$store.dispatch('deployCommon/getNodeVersion', { id }),
          this.$store.dispatch('deployCommon/getLineVersion', { id }),
        ]).then(axios.spread((userResp, reposResp) => {
          this.addList = userResp.data;
          this.addList.forEach((item, index) => {
            this.$set(item, 'indexInfo', index);
            this.$set(item, 'statusInfo', 'WAIT');
            this.nodeList.forEach(node => {
              if (item.id === node.state_id) {
                item.statusInfo = node.status;
              }
            });
          });
          this.lineList = reposResp.data.items;
          this.setLineStatus();
        }))
          .catch((res) => {
            console.log(res);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
      },
      // 获取流程节点状态信息
      getStateStatus() {
        const ticketId = this.basicInfomation.id;
        this.$store.dispatch('deployOrder/getOnlyStateStatus', { params: {}, id: ticketId }).then((res) => {
          this.nodeList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      /**
       * 设置线状态
       * 开始节点出来的线常亮
       * 中间的线通过节点上的 from_transition_id 判断
       * 最后连接结束节点的线通过 last_transition_id 判断
       */
      setLineStatus() {
        const startNodeId = this.addList.find(node => node.type === 'START').id;
        this.lineList.forEach(line => {
          if (this.nodeList.find(node => Number(node.from_transition_id) === line.id)) {
            line.lineStatus = 'SUCCESS';
          }
          if (line.id === Number(this.basicInfomation.last_transition_id)) {
            line.lineStatus = 'SUCCESS';
          }
          if (line.from_state === startNodeId) {
            line.lineStatus = 'SUCCESS';
          }
        });
      },
      // 轮询线条颜色数据
      intervalLines() {
        this.addList.forEach((item, index) => {
          this.$set(item, 'indexInfo', index);
          this.$set(item, 'statusInfo', 'WAIT');
          this.nodeList.forEach(node => {
            if (item.id === node.state_id) {
              item.statusInfo = node.status;
            }
          });
        });
        if (this.$refs.preview) {
          this.$refs.preview.changeDataStatus();
        }
      },
      // 显示和关闭预览图全屏
      openFull() {
        this.previewInfo.narrowSize = 1.1;
        this.fullStatus = true;
      },
      closeFull() {
        this.previewInfo.narrowSize = 0.7;
        this.fullStatus = false;
      },
      // 右侧弹窗动作
      openNodeContent(node) {
        // 未执行的节点禁止查看
        if (node.nodeInfo.statusInfo === 'WAIT') {
          return;
        }
        this.isNodeLoading = true;
        this.openNodeInfo = node.nodeInfo;
        this.nodeContent.isShow = true;
        this.nodeContent.title = node.nodeInfo.name;
        this.getTicketNodeInfo(node);
      },
      closeNodeContent() {
        this.nodeContent.isShow = false;
      },
      getTicketNodeInfo(node) {
        const id = this.basicInfomation.id;
        const params = {
          state_id: node.nodeInfo.id,
        };
        if (this.$route.query.token) {
          params.token = this.$route.query.token;
        }
        this.clickSecond = false;
        this.$store.dispatch('deployOrder/getTicketNodeInfo', { params, id }).then((res) => {
          this.nodeInfo = [res.data];
          this.nodeContent.quick = (res.data.status === 'FINISHED' || !res.data.can_operate);
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isNodeLoading = false;
            this.clickSecond = false;
          });
      },
    },
  };
</script>

<style scoped lang='scss'>
    @import '../../../scss/mixins/clearfix.scss';

    .bk-order-preview {
        width: 100%;
        height: 600px;
        position: relative;
    }

    .bk-basic-head {

        height: 42px;
        padding: 10px 15px;
        font-size: 16px;
        color: #333948;
        border-bottom: 1px solid #dde4eb;

        .bk-head-icon {
            float: left;
            width: 4px;
            height: 14px;
            background-color: #3c96ff;
            margin-right: 8px;
            margin-top: 4px;
        }

        .bk-itsm-icon {
            float: left;
            margin: 4px 10px 0 0;
        }

        .bk-font-icon {
            float: right;
            color: #979BA5;
            cursor: pointer;
            position: relative;
            margin-right: 0;
            top: -1px;

            .cus-order-open{
                &:before{
                    color: #979BA5;
                }
                &:hover{
                    &:before{
                        color: #63656E;
                    }
                }
            }
            .icon-icon-full-srceen,
            .icon-icon-back-full {
                position: absolute;
                top: 1px;
                left: -18px;
                font-size: 13px;
            }
        }
    }

    .bk-basic-head.bk-change {
        position: absolute;
        top: 0;
        right: 0;
        z-index: 1;
        border-bottom: 0px solid #dde4eb;
    }

    .bk-order-flow {
        height: calc(100% - 5px);
    }

    .bk-preview-full {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: #fff;
        z-index: 500;

        .bk-full-div {
            height: calc(100% - 42px);
        }
    }

    .bk-current-bottom {
        position: absolute;
        bottom: 0;
        left: 0;
        // height: 10px;
        background-color: #f5f7fa;
        width: 100%;
        // border-top: 1px solid #dde4eb;
        // border-bottom: 1px solid #dde4eb;
    }
</style>
