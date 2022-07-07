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
  <div class="failed-wrap">
    <div v-if="operationType === '' && reason && nodeInfo.status === 'FAILED'" class="fail-reason">
      <span class="reason-title">{{ $t('m.common["失败原因："]') }}</span>
      <input type="checkbox" :name="`toggle-${nodeInfo.state_id}`" :id="`toggle-${nodeInfo.state_id}`" style="display: none;">
      <p :class="`describe-${nodeInfo.state_id}`">
        {{reason}}
      </p>
      <label class="show-more" :for="`toggle-${nodeInfo.state_id}`">...<span class="show-more-text">{{ $t('m.common["展示更多"]') }}</span></label>
    </div>
    <p v-else class="operation-tips">{{ operationTips }}</p>
    <template v-if="(operationType === '' || operationType === 'retry') && !reloadParams">
      <div class="bk-param"
        v-if="nodeInfo.api_info.remote_api_info.req_params && nodeInfo.api_info.remote_api_info.req_params.length">
        <h3 class="params-title">{{ $t('m.newCommon["输入参数"]') }}</h3>
        <get-param
          ref="getParam"
          :query-value="nodeInfo.api_info.req_params"
          :is-static="!operationType"
          :is-custom="true"
          :api-detail="nodeInfo.api_info.remote_api_info">
        </get-param>
      </div>
      <div class="bk-param"
        v-if="nodeInfo.api_info.remote_api_info.req_body
          && Object.keys(nodeInfo.api_info.remote_api_info.req_body).length
          && nodeInfo.api_info.remote_api_info.req_body.properties
          && Object.keys(nodeInfo.api_info.remote_api_info.req_body.properties).length ">
        <h3 class="params-title">{{ $t('m.newCommon["输入参数"]') }}</h3>
        <post-param
          ref="postParam"
          :body-value="nodeInfo.api_info.req_body"
          :is-static="!operationType"
          :is-custom="true"
          :api-detail="nodeInfo.api_info.remote_api_info">
        </post-param>
      </div>
    </template>
    <!-- 返回数据/可选数组Tree -->
    <div class="bk-param"
      v-if=" (operationType === '' || operationType === 'ignore' || operationType === 'hand')
        && apiDetail.rsp_data
        && Object.keys(apiDetail.rsp_data).length
        && apiDetail.rsp_data.properties
        && Object.keys(apiDetail.rsp_data.properties).length
        && !reloadParams">
      <h3 class="params-title">{{ $t('m.systemConfig["返回数据"]') }}</h3>
      <response-data-node
        ref="responseDataNode"
        :change-info="{}"
        :api-detail="apiDetail"
        :is-static="!operationType"
        :is-custom="true">
      </response-data-node>
    </div>
    <div class="operation-button-group">
      <template v-if="!operationType">
        <bk-button
          class="mr10"
          v-for="buttom in buttons"
          :key="buttom.key"
          :theme="buttom.theme"
          :title="buttom.name"
          :disabled="!nodeInfo.is_schedule_ready || nodeInfo.status !== 'FAILED' || !nodeInfo.can_operate"
          @click="clickBtn(buttom.key)">
          <template v-if="!nodeInfo.is_schedule_ready">
            <span v-bk-tooltips.top="readyTips">{{ buttom.name }}</span>
          </template>
          <template v-else>
            {{ buttom.name }}
          </template>
        </bk-button>
      </template>
      <template v-if="operationType && nodeInfo.status === 'FAILED'">
        <bk-button
          class="mr10"
          :theme="'primary'"
          @click="onSubmit">
          {{ $t('m.common["提交"]') }}
        </bk-button>
        <bk-button
          class="mr10"
          @click="onCancel">
          {{ $t('m["取消"]') }}
        </bk-button>
      </template>
      <slot name="button-extend">
      </slot>
    </div>
  </div>
</template>

<script>
  import postParam from '@/views/processManagement/processDesign/nodeConfigue/addField/postParam.vue';
  import getParam from '@/views/processManagement/processDesign/nodeConfigue/addField/getParam.vue';
  import responseDataNode from '@/views/processManagement/processDesign/nodeConfigue/autoComponents/responseDataNode.vue';
  import { isEmpty } from '@/utils/util.js';
  import { errorHandler } from '@/utils/errorHandler.js';

  export default {
    name: 'apiNodeHandleBody',
    components: {
      getParam,
      postParam,
      responseDataNode,
    },
    props: {
      nodeInfo: {
        type: Object,
        default: () => ({}),
      },
      basicInfomation: {
        type: Object,
        default: () => ({}),
      },
    },
    data() {
      return {
        isShowSubmitBtns: false,
        reloadParams: false,
        operationType: '',
        reason: '',
        readyTips: this.$t('m.task["请将任务列表中的任务全部处理完成之后再进行处理提交"]'),
        buttons: [
          {
            name: this.$t('m.task["重试"]'),
            theme: 'primary',
            key: 'retry',
            notice: this.$t('m.task["将会以当前的填写的参数进行重试"]'),
          },
          {
            name: this.$t('m.task["手动修改"]'),
            theme: 'default',
            key: 'hand',
            notice: this.$t('m.task["系统将以修改后的结果为节点的最终完成结果"]'),
          },
          {
            name: this.$t('m.task["忽略"]'),
            theme: 'default',
            key: 'ignore',
            notice: this.$t('m.task["执行忽略，将会以当前输出的信息为完成结果，继续后续流程"]'),
          },
        ],
      };
    },
    computed: {
      inputs() {
        if (this.nodeInfo.query_params) {
          return this.nodeInfo.query_params;
        }
        const apiInfo = this.nodeInfo.api_info;
        const reqData = apiInfo.method === 'POST' ? apiInfo.req_body : apiInfo.req_params;
        return reqData.data || [];
      },
      apiDetail() {
        return this.nodeInfo.api_info.remote_api_info;
      },
      operationTips() {
        const tipsMap = {
          retry: this.$t('m.newCommon["请重新修改以下参数后再重试："]'),
          hand: this.$t('m.newCommon["执行手动修改，需要根据接口要求填写相应参数信息（若无参数要求，可留空或忽略）："]'),
        };
        return tipsMap[this.operationType] || '';
      },
    },
    watch: {
      reason() {
        this.$nextTick(() => {
          this.addTruncatedAttr();
        });
      },
    },
    mounted() {
      this.getNodeLog();
    },
    beforeDestroy() {
      // this.clearFloatBtn()
    },
    methods: {
      getNodeLog() {
        const params = {
          ticket: this.basicInfomation.id,
          from_state_id: this.nodeInfo.state_id,
        };
        this.$store.dispatch('deployOrder/getNodeLog', { params }).then(res => {
          const lastLog = res.data.pop();
          this.reason = lastLog ? lastLog.message : '';
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      /**
       * 文字溢出时添加 truncated 属性
       */
      addTruncatedAttr() {
        const ps = document.querySelector(`.fail-reason .describe-${this.nodeInfo.state_id}`);
        const observer = new ResizeObserver(entries => {
          for (const entry of entries) {
            entry.target.classList[entry.target.scrollHeight > entry.contentRect.height ? 'add' : 'remove']('truncated');
          }
        });
        ps && observer.observe(ps);
      },
      clickBtn(action) {
        if (action === 'ignore') {
          this.showConfirmDialog('ignore');
          return;
        }
        this.operationType = action;
        this.reloadParamsComponents();

        this.$nextTick(() => {
          // 当前操作节点自动定位到页面上方
          const currStepOffsetTop = document.querySelector('.current-step-content').offsetTop;
          const currContentOffsetTop = document.querySelector(`.bk-content-node.state_id_${this.nodeInfo.state_id}`).offsetTop;
          document.body.querySelector('.ticket-container-left').scrollTo({ top: currStepOffsetTop + currContentOffsetTop - 70 });
        });
                
        // 进入处理界面，添加滚动监听，按钮悬浮在内容上
        // this.handleContentScroll = debounce(this.contentScroll, 30)
        // document.querySelector('.ticket-container-left').addEventListener('scroll', this.handleContentScroll, false)
      },
      contentScroll() {
        const currStepEl = document.querySelector(`.bk-content-node.state_id_${this.nodeInfo.state_id}`);
        const cuurStepInfo = currStepEl.getBoundingClientRect();
        const winHeight = document.body.clientHeight;
        if (cuurStepInfo.y + cuurStepInfo.height > winHeight && cuurStepInfo.y + 60 < winHeight) {
          this.$el.classList.add('float-btn');
        } else {
          this.$el.classList.remove('float-btn');
        }
      },
      // clearFloatBtn () {
      //     const leftContentEl = document.querySelector('.bk-common-left')
      //     leftContentEl && leftContentEl.removeEventListener('scroll', this.handleContentScroll, false)
      //     this.$el.classList.remove('float-btn')
      // },
      // 重新加载参数显示组件
      reloadParamsComponents() {
        this.reloadParams = true;
        this.$nextTick(() => {
          this.reloadParams = false;
        });
      },
      onSubmit() {
        if (!this.checkSubmitParams()) return;
        this.showConfirmDialog(this.operationType);
      },
      onCancel() {
        this.operationType = '';
        this.reloadParamsComponents();
        // this.clearFloatBtn()
      },
      // 参数校验
      checkSubmitParams() {
        if (this.$refs.postParam) {
          const body = this.$refs.postParam.tableList;
          const verifiFailedItem = body.find(item => item.is_necessary && isEmpty(item.customValue) && !item.children.length);
          if (verifiFailedItem) {
            this.$bkMessage({
              message: verifiFailedItem.key + this.$t('m.newCommon["为必填项！"]'),
              theme: 'warning',
            });
            return false;
          }
        }
        if (this.$refs.getParam) {
          const body = this.$refs.getParam.paramTableData;
          const verifiFailedItem = body.find(item => item.is_necessary && isEmpty(item.customValue) && !item.children.length);
          if (verifiFailedItem) {
            this.$bkMessage({
              message: verifiFailedItem.key + this.$t('m.newCommon["为必填项！"]'),
              theme: 'warning',
            });
            return false;
          }
        }
        if (this.$refs.responseDataNode) {
          const body = this.$refs.responseDataNode.tableList;
          const verifiFailedItem = body.find(item => item.is_necessary && isEmpty(item.customValue) && !item.children.length);
          if (verifiFailedItem) {
            this.$bkMessage({
              message: verifiFailedItem.key + this.$t('m.newCommon["为必填项！"]'),
              theme: 'warning',
            });
            return false;
          }
        }
        return true;
      },
      // 显示确认弹窗
      showConfirmDialog(type) {
        const currentModel = this.buttons.find(m => m.key === type);
        this.$bkInfo({
          type: 'warning',
          title: `${this.$t('m.task["确认"]')}${currentModel.name}？`,
          subTitle: currentModel.notice,
          confirmFn: () => {
            // this.clearFloatBtn()
            if (type === 'retry') {
              this.onRetryNode();
            }
            if (type === 'hand' || type === 'ignore') {
              this.onIgnoreNode(this.operationType === 'hand');
            }
          },
        });
      },
      // 节点重试
      onRetryNode() {
        let data = [];
        if (this.nodeInfo.api_info.method === 'POST' && this.$refs.postParam) {
          data = this.$refs.postParam.tableList;
        } else if (this.$refs.getParam) {
          data = this.$refs.getParam.paramTableData;
        }
        const inputs = this.getInputsParams(data);
        const params = {
          inputs,
          state_id: this.nodeInfo.state_id,
        };
        this.$store.dispatch('deployOrder/retryNode', { params, ticketId: this.basicInfomation.id }).then(() => {
          this.$bkMessage({
            message: this.$t('m.newCommon["提交成功"]'),
            theme: 'success',
          });
          this.$emit('updateOrderStatus');
          this.onCancel();
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      // 忽略节点（手动修改输出参数/自动成功）
      onIgnoreNode(fillParam = false) {
        let inputs = {};
        if (fillParam) {
          const data = (this.$refs.responseDataNode && this.$refs.responseDataNode.tableList) || [];
          inputs = this.getInputsParams(data);
        }
        const params = {
          inputs,
          state_id: this.nodeInfo.state_id,
          is_direct: !fillParam,
        };
        this.$store.dispatch('deployOrder/ignoreNode', { params, ticketId: this.basicInfomation.id }).then(() => {
          this.$bkMessage({
            message: this.$t('m.newCommon["提交成功"]'),
            theme: 'success',
          });
          this.$emit('updateOrderStatus');
          this.onCancel();
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      // 获取输入参数对象
      getInputsParams(data) {
        const reqParams = {};
        data.forEach((reqItem, index) => {
          const parentKeyPath = this.getParentKeyPath(data, reqItem, index);
          let key = reqItem.name;
          let fieldData = data;
          const paramsValue = parentKeyPath.reduce((acc, crt) => {
            const field = fieldData.find(field => field.primaryKey === crt);
            fieldData = field.children;
            if (Array.isArray(acc)) {
              const arrIndex = acc.length > 0 ? acc.length - 1 : 0;
              return acc[arrIndex];
            }
            return acc[field.name];
          }, reqParams);
          if (parentKeyPath.length > 0 && Array.isArray(paramsValue)) {
            key = paramsValue.length;
          }
          if (reqItem.type === 'array') {
            paramsValue[key] = [];
          } else if (reqItem.type === 'object') {
            paramsValue[key] = {};
          } else {
            paramsValue[key] = reqItem.customValue;
          }
        });
        return reqParams;
      },
      // 获取当前字段的父级路径集合
      getParentKeyPath(list, field, index) {
        const parentKeyPath = [];
        if (field.parentPrimaryKey) {
          let parentField; let parentFieldIndex;
          parentKeyPath.push(field.parentPrimaryKey);
          list.slice(0, index).forEach((item, i) => {
            if (item.primaryKey === field.parentPrimaryKey) {
              parentField = item;
              parentFieldIndex = i;
            }
          });
          if (parentField.parentPrimaryKey) {
            return this.getParentKeyPath(list, parentField, parentFieldIndex).concat(parentKeyPath);
          }
        }
        return parentKeyPath;
      },
    },
  };
</script>

<style lang="scss" scoped>
    .fail-reason {
        position: relative;
        font-size: 12px;
        .reason-title {
            float: left;
            color: #ea3636;
        }
        input[name^="toggle-"]:checked {
            & + [class^="describe-"] {
                -webkit-line-clamp: unset;
            }
        }
        [class^="describe-"] {
            display: inline-block;
            line-height: 16px;
            color: #63656e;
            word-break: break-all;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            &.truncated {
                & + .show-more {
                    display: block;
                }
            }
        }
        .show-more {
            display: none;
            padding-left: 0.3em;
            position: absolute;
            right: 0;
            bottom: 0;
            background: #fff;
            cursor: pointer;
            .show-more-text {
                color: #3A84FF;
            }
        }
    }
    .operation-tips {
       color: #63656e;
    }
    .params-title {
        font-size: 12px;
        color: #63656e;
        font-weight: bold;
    }
    .operation-button-group {
        margin-top: 10px;
    }
    .float-btn {
        .operation-button-group {
            position: fixed;
            bottom: 24px;
            width: 100%;
            height: auto;
            z-index: 1;
        }
    }
</style>
