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
  <div class="bk-node-content" v-bkloading="{ isLoading: !nodeListCurren[0] }">
    <template
      v-if="nodeListCurren[0] && (nodeListCurren[0].can_operate || nodeListCurren[0].can_view) && nodeListCurren[0].type !== 'TASK-SOPS'">
      <div class="bk-logs-basic" v-if="nodeListCurren[0] && nodeListCurren[0].action_type === 'TRANSITION'">
        <h3 class="bk-basic-h3">{{ $t('m.newCommon["基本信息"]') }}</h3>
        <ul>
          <li v-for="(item, index) in basicList" :key="index">
            <span class="bk-basic-label">{{item.name}}：</span>
            <span class="bk-basic-value" :title="item.value">{{item.value || '--'}}</span>
          </li>
        </ul>
      </div>
    </template>
    <div class="bk-logs-basic">
      <template
        v-if="nodeListCurren[0] && (nodeListCurren[0].can_operate || nodeListCurren[0].can_view) &&
          (nodeListCurren[0].type === 'NORMAL' || nodeListCurren[0].type === 'SIGN')">
        <h3 class="bk-basic-h3">
          {{nodeListCurren[0].type === 'SIGN' ? $t(`m.newCommon['会签进度']`) : $t('m.newCommon["节点信息"]')}}</h3>
      </template>
      <div v-for="(item, index) in nodeListCurren" :key="index" style="position: relative;">
        <!-- 有操作权限/有查看权限 -->
        <template v-if="(item.can_operate || item.can_view)">
          <div class="bk-node-form-disabled" v-if="!item.can_operate"></div>
          <!-- 节点未处理 -->
          <template
            v-if="(item.status === 'RUNNING' || item.status === 'QUEUEING') && (item.type === 'NORMAL' || item.type === 'APPROVAL')">
            <template v-if="basicInfomation.is_over">
              <!-- 暂无内容 -->
              <div class="bk-no-content bk-no-status">
                <img src="../../../../images/orderFinished.png"
                  v-if="basicInfomation.current_status === 'FINISHED'">
                <img src="../../../../images/orderStop.png"
                  v-if="basicInfomation.current_status === 'TERMINATED'">
                <p>
                  <span
                    v-if="basicInfomation.current_status === 'FINISHED'">{{ $t('m.newCommon["该单据已结束"]') }}</span>
                  <span
                    v-if="basicInfomation.current_status === 'TERMINATED'">{{ $t('m.newCommon["该单据已被终止"]') }}</span>
                </p>
              </div>
            </template>
            <current-steps
              v-else
              :read-only="readOnly"
              :basic-infomation="basicInfomation"
              :current-step-list="currentStepList"
              :node-list="nodeListCurren"
              :open-status="openStatus"
              @closeSlider="closeSlider">
            </current-steps>
            <div class="bk-option-see" v-if="item.status === 'QUEUEING'">
              <span>{{ $t('m.newCommon["信息已经提交成功，系统正在处理中，请稍后查看！"]') }}</span>
            </div>
          </template>
          <!-- 节点已处理 -->
          <field-preview
            v-else-if="(item.status !== 'RUNNING' && item.status !== 'QUEUEING') && item.type === 'NORMAL'"
            :comment-id="'fields-view'"
            :fields="item.fields"
            :ticket-id="basicInfomation.id"
            :stated-id="item.ticket_id">
          </field-preview>
          <!-- 自动节点未处理/已处理 -->
          <autoNodeInfo
            v-else-if="item.type === 'TASK'"
            :api-info="item.api_info"
            :node-info="item"
            :ticket-id="basicInfomation.id"
            :stated-id="item.ticket_id">
          </autoNodeInfo>
          <signNodeInfo
            v-else-if="item.type === 'SIGN'"
            :node-info="item">
          </signNodeInfo>
          <approvalNodeInfo
            v-else-if="item.type === 'APPROVAL'"
            :api-info="item.api_info"
            :node-info="item">
          </approvalNodeInfo>
          <devopsNodeInfo
            v-else-if="item.type === 'TASK-DEVOPS'"
            :api-info="item.api_info"
            :node-info="item">
          </devopsNodeInfo>
          <web-hook-info
            v-else-if="item.type === 'WEBHOOK'"
            :api-info="item.api_info"
            :node-info="item">
          </web-hook-info>
          <bk-plugin-info
            v-else-if="item.type === 'BK-PLUGIN'"
            :api-info="item.api_info"
            :node-info="item">
          </bk-plugin-info>
          <sopsNodeInfo
            v-else
            :api-info="item.api_info"
            :node-info="item"
            :ticket-id="basicInfomation.id"
            :stated-id="item.ticket_id">
          </sopsNodeInfo>
        </template>
        <!-- 暂无权限 -->
        <template v-else>
          <div class="bk-without-permission" :key="index">
            <p class="bk-without-prompt">
              <i class="bk-itsm-icon icon-icon-no-permissions"></i>
              <span v-if="!item.can_operate">{{ $t('m.newCommon["抱歉你暂无该节点的处理权限"]') }}</span>
              <span v-else>{{ $t('m.newCommon["抱歉你暂无该节点的查看权限"]') }}</span>
            </p>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
  import CurrentSteps from '../currentSteps/index.vue';
  import fieldPreview from '@/views/commonComponent/fieldPreview';
  import autoNodeInfo from './autoNodeInfo.vue';
  import sopsNodeInfo from './sopsNodeInfo.vue';
  import devopsNodeInfo from './devopsNodeInfo.vue';
  import signNodeInfo from './signNodeInfo';
  import approvalNodeInfo from './approvalNodeInfo';
  import webHookInfo from './webHookInfo.vue';
  import bkPluginInfo from './bkPluginInfo.vue';
  import { errorHandler } from '@/utils/errorHandler';

  export default {
    name: 'nodeContent',
    components: {
      CurrentSteps,
      fieldPreview,
      autoNodeInfo,
      sopsNodeInfo,
      signNodeInfo,
      approvalNodeInfo,
      devopsNodeInfo,
      webHookInfo,
      bkPluginInfo,
    },
    props: {
      readOnly: Boolean,
      // 单据信息
      basicInfomation: {
        type: Object,
        default() {
          return {};
        },
      },
      // 打开节点
      openNodeInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      // 说有节点信息
      nodeList: {
        type: Array,
        default() {
          return [];
        },
      },
      currentStepList: {
        type: Array,
        default() {
          return [];
        },
      },
    },
    data() {
      return {
        basicList: [
          { name: this.$t('m.newCommon["节点名称"]'), value: '', key: 'name' },
          { name: this.$t('m.newCommon["处理人"]'), value: '', key: 'processors' },
          { name: this.$t('m.newCommon["处理时间"]'), value: '', key: 'update_at' },
        ],
        openStatus: true,
      };
    },
    computed: {
      nodeListCurren() {
        const nodeListCurren = this.nodeList.filter(item => item.state_id === this.openNodeInfo.id);
        if (nodeListCurren[0]) {
          for (let i = 0; i < this.basicList.length; i++) {
            const property = this.basicList[i];
            property.value = JSON.parse(JSON.stringify((nodeListCurren[0][property.key] || '')));
          }
        }
        return nodeListCurren;
      },
    },
    mounted() {
      setTimeout(() => {
        if (this.nodeList[0] && this.nodeList[0].status !== 'FINISHED'
          && this && !this._isDestroyed) {
          this.getTicketNodeInfo(this.openNodeInfo);
        }
      }, 10000);
    },
    methods: {
      initInfo() {
        this.$emit('initInfo');
      },
      getTicketNodeInfo(openNodeInfo) {
        const id = this.basicInfomation.id;
        const params = {
          state_id: openNodeInfo.id,
        };
        this.$store.dispatch('deployOrder/getTicketNodeInfo', { params, id }).then((res) => {
          if (res.data.status !== 'FINISHED' && this && !this._isDestroyed && !this.basicInfomation.is_over) {
            // 判断数据 和上次请求是否相同
            if (this.nodeList[0].toString() !== res.data.toString()) {
              this.nodeInfo[0] = res.data;
            }
            // 轮询
            const setTimeoutFunc = setTimeout(() => {
              this.getTicketNodeInfo(this.openNodeInfo);
            }, 10000);
            this.$once('hook:beforeDestroy', () => {
              clearInterval(setTimeoutFunc);
            });
          }
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
          });
      },
      closeSlider() {
        this.$emit('closeSlider');
      },
    },
  };
</script>

<style scoped lang='scss'>
    @import '../../../../scss/mixins/clearfix.scss';

    .bk-node-content {
        padding: 10px 20px;
        min-height: 100px;

        .bk-node-form-disabled {
            cursor: not-allowed;
        }
    }

    .bk-logs-basic {
        margin-bottom: 25px;

        ul {
            @include clearfix;
        }

        li {
            float: left;
            width: 50%;
            font-size: 12px;
            line-height: 27px;
            color: #63656E;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
            .bk-basic-label {
                display: inline-block;
                min-width: 70px;
                font-weight: bold;
            }
        }

        li:first-child {
            width: 100%;
        }
    }

    .bk-option-see {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        text-align: center;
        color: #ffffff;
        font-size: 16px;
        z-index: 10;

        span {
            position: absolute;
            top: 50%;
            left: 0;
            width: 100%;
            text-align: center;
            transform: translateY(-50%);
        }
    }

    .bk-basic-h3 {
        margin: 0;
        padding: 0;
        font-size: 14px;
        font-weight: bold;
        color: #63656E;
        line-height: 19px;
        margin-bottom: 10px;
    }

    /* 暂无权限 */
    .bk-without-permission {
        .bk-without-prompt {
            text-align: center;
            color: #63656E;
            font-size: 16px;
            padding: 35px 0;

            .bk-itsm-icon {
                margin-right: 5px;
                font-size: 20px;
                color: #979BA5;
            }
        }
    }

    .bk-content-form {
        position: relative;

        .bk-node-disabled {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            cursor: not-allowed;
            z-index: 5;
        }
    }

    .bk-no-content {
        text-align: center;
        padding: 80px 0;

        p {
            font-size: 16px;
            color: #63656E;
            margin-top: 10px;
        }
    }

    .bk-no-status {
        padding: 67px 0;

        img {
            width: 110px;
        }
    }
</style>
