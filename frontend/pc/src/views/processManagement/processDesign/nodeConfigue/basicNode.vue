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
    <!-- <basic-card :card-label="$t(`m.treeinfo['基本信息']`)">
        </basic-card> -->
    <basic-card>
      <basic-info
        ref="basic"
        :node-info="configur"
        :node-tag-list="nodeTagList"
        :is-loading="isLoading"
        :flow-info="flowInfo"
        @baseFormInfoChange="baseFormInfoChange">
      </basic-info>
      <field-config
        ref="field"
        :is-show-title="true"
        :flow-info="flowInfo"
        :configur="configur">
      </field-config>
      <common-trigger-list
        ref="commonTriggerList"
        :origin="'state'"
        :node-type="configur.type"
        :source-id="flowInfo.id"
        :sender="configur.id"
        :table="flowInfo.table">
      </common-trigger-list>
      <div class="bk-node-btn mt20">
        <bk-button :theme="'primary'"
          data-test-id="basicNode-button-submit"
          :title="$t(`m.treeinfo['确定']`)"
          :loading="secondClick"
          class="mr10"
          @click="submitNode">
          {{$t(`m.treeinfo['确定']`)}}
        </bk-button>
        <bk-button :theme="'default'"
          data-test-id="basicNode-button-close"
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
  import basicInfo from './components/basicInfo.vue';
  import fieldConfig from './components/fieldConfig.vue';
  import commonTriggerList from '../../taskTemplate/components/commonTriggerList';
  import BasicCard from '@/components/common/layout/BasicCard.vue';
  import { deepClone } from '@/utils/util.js';
  import { errorHandler } from '../../../../utils/errorHandler';

  export default {
    name: 'basicNode',
    components: {
      BasicCard,
      basicInfo,
      fieldConfig,
      commonTriggerList,
    },
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
    },
    data() {
      return {
        isLoading: false,
        secondClick: false,
        showMoreConfig: false,
        stringValueList: ['OPEN', 'STARTER'],
        // 节点标签数据
        nodeTagList: [],
        // 基础信息 form
        baseFormData: {},
      };
    },
    mounted() {
      this.initData();
    },
    methods: {
      initData() {
        // this.getNodeTagList();
      },
      // 获取节点标签数据
      getNodeTagList() {
        const params = {
          key: 'STATE_TAG_TYPE',
        };
        this.$store.dispatch('datadict/get_data_by_key', params).then((res) => {
          this.nodeTagList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {

          });
      },
      checkStringValue(value) {
        const temp = this.stringValueList.findIndex(item => item === value);
        return temp === -1;
      },
      // 确认
      async submitNode() {
        // 校验阻止
        const basicInfo = this.$refs.basic.backBasicInfo();
        const checkBasic = this.$refs.basic.checkStatus;
        if (checkBasic.name || checkBasic.assignors || checkBasic.delivers || checkBasic.processors) {
          return;
        }
        const params = {};
        // 固定值
        params.is_draft = false;
        params.workflow = this.flowInfo.id;
        params.type = this.configur.type;
        params.is_terminable = false;
        // 基本信息
        params.name = basicInfo.name;
        params.desc = basicInfo.desc || undefined;
        params.tag = basicInfo.tag;
        params.distribute_type = basicInfo.distribute_type;
        params.assignors_type = basicInfo.assignors_type;
        params.assignors = basicInfo.assignors;
        params.processors_type = basicInfo.processors_type;
        params.processors = basicInfo.processors;
        params.extras = {
          ticket_status: {
            name: basicInfo.ticket_key,
            type: basicInfo.ticket_type,
          },
        };
        params.can_deliver = basicInfo.can_deliver;
        params.delivers_type = basicInfo.delivers_type;
        params.delivers = basicInfo.delivers;
        // 字段配置
        const fieldInfo = this.$refs.field.showTabList;
        params.fields = fieldInfo.map(item => item.id);
        const { id } = this.configur;
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
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.secondClick = false;
          });
      },
      // 取消
      closeNode() {
        this.$emit('closeConfigur', false);
      },
      // 基础信息数据改变
      baseFormInfoChange(form) {
        const { distribute_type: distributeType, can_deliver: canDeliver } = form;
        if (distributeType === this.baseFormData.distribute_type && canDeliver === this.baseFormData.can_deliver) {
          return;
        }
        this.baseFormData = deepClone(form);
        // 根据处理场景不同，剔除不必要触发事件
        const filterMap = {
          // 直接处理
          PROCESS: [],
          // 先派单，后处理
          DISTRIBUTE_THEN_PROCESS: ['CLAIM_STATE', 'DELIVER_STATE'],
          // 先认领，后处理
          CLAIM_THEN_PROCESS: ['DISTRIBUTE_STATE', 'DELIVER_STATE'],
          // 先派单，后认领
          DISTRIBUTE_THEN_CLAIM: [],
        };
        let filterList = filterMap[distributeType] || [];
        // 是否可转单 选项存在时
        if (!this.configur.is_builtin) {
          if (canDeliver) {
            filterList = filterList.filter(key => key !== 'DELIVER_STATE');
          } else if (filterList.indexOf('DELIVER_STATE') === -1) {
            filterList.push('DELIVER_STATE');
          }
        }

        if (this.$refs.commonTriggerList) {
          this.$refs.commonTriggerList.setFilterSignal(filterList);
          this.$refs.commonTriggerList.getBoundTriggerList();
        }
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

        .bk-node-btn{
            font-size: 0;
        }
        /deep/ .common-section-card-label {
            display: none;
        }
        /deep/ .common-section-card-body {
            padding: 20px;
        }
    }
</style>
