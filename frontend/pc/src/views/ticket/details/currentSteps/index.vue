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
  <div class="bk-current-node">
    <div class="bk-current-info" :class="{ 'bk-current-padding': openStatus }" v-bkloading="{ isLoading: loading }">
      <template v-if="!basicInfomation.is_over">
        <template v-if="currentStepList.length !== 0">
          <current-step-item
            v-for="(item, index) in currentStepList"
            :key="index"
            :index="index"
            :node-info="item"
            :node-list="nodeList"
            :is-show-assgin="isShowAssgin"
            :ticket-info="basicInfomation"
            :all-groups="allGroups"
            :read-only="readOnly"
            :is-last-node="index === currentStepList.length - 1"
            :node-trigger-list="nodeTriggerList"
            :all-field-list="allFieldList"
            @successFn="successFn">
          </current-step-item>
        </template>
        <template v-else>
          <!-- 暂无内容 -->
          <bk-exception
            class="ui-empty"
            type="empty"
            scene="part">
            {{$t('m.newCommon["您暂无任务需要处理"]')}}
          </bk-exception>
        </template>
      </template>
      <template v-else>
        <!-- 暂无内容 -->
        <div class="bk-no-content bk-no-status">
          <template v-if="basicInfomation.current_status === 'TERMINATED'">
            <img src="../../../../images/orderStop.png">
            <p>{{ $t('m.newCommon["该单据已被终止"]') }}</p>
          </template>
          <template v-else>
            <img src="../../../../images/orderFinished.png">
            <p>{{ $t('m.newCommon["该单据已结束"]') }}</p>
          </template>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
  import { errorHandler } from '@/utils/errorHandler.js';
  import mixins from '@/views/commonMix/field.js';
  import apiFieldsWatch from '@/views/commonMix/api_fields_watch.js';
  import CurrentStepItem from './CurrentStepItem.vue';

  export default {
    name: 'CurrentSteps',
    components: {
      CurrentStepItem,
    },
    mixins: [mixins, apiFieldsWatch],
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
      nodeList: {
        type: Array,
        default() {
          return [];
        },
      },
      openStatus: {
        type: Boolean,
        default: false,
      },
      nodeTriggerList: {
        type: Array,
        default() {
          return [];
        },
      },
      loading: {
        type: Boolean,
        default: false,
      },
      isShowBasicInfo: Boolean,
      readOnly: Boolean,
      isShowAssgin: Boolean,
    },
    data() {
      return {
        allGroups: [],
        allFieldList: [],
        // 组织架构
        organizationList: [],
        updateDate: +new Date(),
        tooltipConfig: {
          allowHtml: true,
          trigger: 'click',
          theme: 'light',
          content: '#tooltipHtml',
          placement: 'top',
          extCls: 'bk-processor-wrapper',
        },
        // 手动触发器下拉框状态
        isDropdownShow: false,
        basicInDomHeight: 54, // 基本信息初始高度
      };
    },
    watch: {
      isShowBasicInfo() {
        this.getBasicHeight();
      },
    },
    mounted() {
      this.getBasicHeight();
    },
    methods: {
      loadData() {
        this.getAllGroups();
      },
      getAllGroups() {
        const params = 'is_processor=true';
        this.$store.dispatch('deployCommon/getUser', { params }).then((res) => {
          const disabledList = ['VARIABLE', 'STARTER_LEADER', 'IAM'];
          this.allGroups = res.data.filter(item => !disabledList.includes(item.type));
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      getBasicHeight() {
        const basicDom = document.querySelector('.base-info-content');
        this.basicInDomHeight = basicDom.clientHeight;
      },
      // 成功后的回调事件
      successFn() {
        this.$emit('handlerSubmitSuccess');
      },
    },
  };
</script>

<style scoped lang='scss'>
    @import '../../../../scss/mixins/scroller.scss';
    .bk-current-info {
        // overflow: auto;
        position: relative;
        padding: 10px;
        @include scroller;
    }

    .bk-current-padding {
        padding: 0;
    }

    .bk-no-status {
        padding: 67px 0;
        text-align: center;
        padding: 80px 0;
        img {
            width: 110px;
        }
        p {
            font-size: 16px;
            color: #63656E;
            margin-top: 10px;
        }
    }
    .ui-empty {
        margin: 50px auto;
    }
</style>
