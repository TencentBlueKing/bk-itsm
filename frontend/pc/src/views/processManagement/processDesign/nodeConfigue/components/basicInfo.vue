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
  <div class="bk-basic-info" v-bkloading="{ isLoading: isLoading }">
    <bk-form :label-width="150"
      :model="formInfo"
      :rules="rules"
      form-type="vertical"
      ref="basicForm">
      <bk-form-item :label="$t(`m.treeinfo['节点名称：']`)"
        data-test-id="basicInfo-input-nodeName"
        :ext-cls="'bk-item-width'"
        :required="true"
        :property="'name'">
        <bk-input :font-size="'medium'"
          v-model="formInfo.name"
          maxlength="120">
        </bk-input>
      </bk-form-item>
      <desc-info v-model="formInfo.desc"></desc-info>
      <!-- <bk-form-item :label="$t(`m.treeinfo['节点标签：']`)" :required="true">
        <bk-select :ext-cls="'bk-form-width'"
          v-model="formInfo.tag"
          :clearable="false"
          searchable
          :font-size="'medium'">
          <bk-option v-for="option in nodeTagList"
            :key="option.key"
            :id="option.key"
            :name="option.name">
          </bk-option>
        </bk-select>
      </bk-form-item> -->
      <bk-form-item data-test-id="basicInfo-select-ProcessingScenarios" :label="$t(`m.treeinfo['处理场景：']`)" :required="true">
        <bk-select :ext-cls="'bk-form-width'"
          v-model="formInfo.distribute_type"
          :clearable="false"
          searchable
          :disabled="nodeInfo.is_builtin"
          :font-size="'medium'"
          @selected="changeDistribute">
          <bk-option v-for="option in sceneList"
            :key="option.typeName"
            :id="option.typeName"
            :name="option.name">
          </bk-option>
        </bk-select>
        <p v-for="(item, index) in prompt"
          :key="index"
          v-if="item.id === formInfo.distribute_type"
          class="mt5 mb0 bk-revoke-span">
          <i class="bk-icon icon-exclamation-circle" style="padding-right: 5px"></i>
          <span>{{item.prompt}}</span>
        </p>
      </bk-form-item>
      <template v-if="assignorsTypeList.some(assignor => assignor === formInfo.distribute_type)">
        <bk-form-item data-test-id="basicInfo-select-assignors" :label="$t(`m.treeinfo['派单人：']`)" :required="true">
          <div @click="checkStatus.assignors = false">
            <deal-person
              ref="assignors"
              :value="assignorsInfo"
              :exclude-role-type-list="assignorExclude">
            </deal-person>
          </div>
        </bk-form-item>
      </template>
      <template v-if="processorsInfo.type">
        <bk-form-item data-test-id="basicInfo-component-processor" :label="$t(`m.treeinfo['处理人：']`)" :required="true">
          <div @click="checkStatus.processors = false">
            <deal-person
              ref="processors"
              :value="processorsInfo"
              :node-info="nodeInfo"
              :show-overbook="true"
              :exclude-role-type-list="excludeProcessor">
            </deal-person>
          </div>
        </bk-form-item>
      </template>
      <bk-form-item :label="$t(`m.treeinfo['设置单据状态：']`)" :required="true">
        <bk-select :ext-cls="'bk-form-width bk-form-display'"
          v-model="formInfo.ticket_type"
          :clearable="false"
          searchable
          :font-size="'medium'"
          @selected="handleTicket">
          <bk-option v-for="option in billStatusList"
            :key="option.type"
            :id="option.type"
            :name="option.name">
          </bk-option>
        </bk-select>
        <template v-if="formInfo.ticket_type === 'custom'">
          <bk-select :ext-cls="'bk-form-width bk-form-display'"
            v-model="formInfo.ticket_key"
            :loading="ticketKeyLoading"
            :clearable="false"
            searchable
            :font-size="'medium'">
            <bk-option v-for="option in secondLevelList"
              :key="option.key"
              :id="option.key"
              :name="option.name">
            </bk-option>
          </bk-select>
        </template>
      </bk-form-item>
      <template v-if="!nodeInfo.is_builtin">
        <bk-form-item data-test-id="basicInfo-radio-canDeliver" :label="$t(`m.treeinfo['是否可转单：']`)" :required="true">
          <bk-radio-group v-model="formInfo.can_deliver">
            <bk-radio :value="trueStatus" :ext-cls="'mr20'">{{ $t('m.treeinfo["是"]') }}</bk-radio>
            <bk-radio :value="falseStatus">{{ $t('m.treeinfo["否"]') }}</bk-radio>
          </bk-radio-group>
        </bk-form-item>
      </template>
      <template v-if="formInfo.can_deliver">
        <bk-form-item data-test-id="basicInfo-radio-delivers" :label="$t(`m.treeinfo['转单人：']`)" :required="true">
          <div @click="checkStatus.delivers = false">
            <deal-person
              ref="delivers"
              :value="deliversInfo"
              :exclude-role-type-list="deliversExclude">
            </deal-person>
          </div>
        </bk-form-item>
      </template>
    </bk-form>
  </div>
</template>
<script>
  import descInfo from './descInfo.vue';
  import dealPerson from './dealPerson.vue';
  import commonMix from '../../../../commonMix/common.js';
  import { errorHandler } from '../../../../../utils/errorHandler';

  export default {
    name: 'basicInfo',
    components: {
      dealPerson,
      descInfo,
    },
    mixins: [commonMix],
    props: {
      flowInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      nodeInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      nodeTagList: {
        type: Array,
        default() {
          return [];
        },
      },
      isLoading: {
        type: Boolean,
        default() {
          return false;
        },
      },
    },
    data() {
      return {
        // 数据变量
        formInfo: {
          name: '',
          desc: '',
          tag: '',
          distribute_type: '',
          ticket_key: '',
          ticket_type: '',
          can_deliver: false,
        },
        trueStatus: true,
        falseStatus: false,
        assignorsInfo: {
          type: '',
          value: '',
        },
        excludeProcessor: [], // 处理人排除类型
        assignorExclude: ['BY_ASSIGNOR', 'EMPTY', 'OPEN', 'VARIABLE', 'API'], // 派单人排除类型
        deliversExclude: ['BY_ASSIGNOR', 'EMPTY', 'STARTER', 'VARIABLE', 'API', 'ASSIGN_LEADER', 'STARTER_LEADER'], // 转单人排除类型
        assignorsTypeList: ['DISTRIBUTE_THEN_PROCESS', 'DISTRIBUTE_THEN_CLAIM'],
        processorsInfo: {
          type: '',
          value: '',
        },
        deliversInfo: {
          type: '',
          value: '',
        },
        // 单据状态
        billStatusList: [
          { type: 'keep', name: this.$t('m.treeinfo["延续上个节点"]') },
          { type: 'custom', name: this.$t('m.treeinfo["自定义"]') },
        ],
        secondLevelList: [],
        ticketKeyLoading: false,
        // 处理场景
        sceneList: [],
        prompt: [
          {
            id: 'DISTRIBUTE_THEN_PROCESS',
            prompt: this.$t('m.treeinfo["指该节点动作需要通过派单人分派到指定处理人或者处理角色，被分派到的处理人再进行处理。"]'),
          },
          {
            id: 'PROCESS',
            prompt: this.$t('m.treeinfo["单据直接流入到配置好的处理人/角色处理。当有多个处理人时，任何一位处理完成即可流入下个环节。"]'),
          },
          {
            id: 'CLAIM_THEN_PROCESS',
            prompt: this.$t('m.treeinfo["指配置好的处理人/角色人员需要主动认领任务。当处理人只有1位时，会自动认领。处理人有2人及以上时，需要主动认领至自己的待办任务中。"]'),
          },
          {
            id: 'DISTRIBUTE_THEN_CLAIM',
            prompt: this.$t('m.treeinfo["单据需要派单人进行指派到组或者多人，然后被指派对象进行主动认领。认领完成后才会到自己的待办任务列表中。"]'),
          },
        ],
        rules: {},
        checkStatus: {
          name: false,
          assignors: false,
          processors: false,
          delivers: false,
        },
      };
    },
    computed: {
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
    },
    watch: {
      formInfo: {
        deep: true,
        handler(val) {
          this.$emit('baseFormInfoChange', val);
        },
      },
    },
    mounted() {
      this.initData();
      this.getExcludeRoleTypeList();
      this.rules.name = this.commonRules.name;
    },
    methods: {
      // 初始化数据
      initData() {
        // 处理场景
        this.sceneList = [];
        this.globalChoise.distribute_type.forEach((item) => {
          // 提单节点只存在直接处理场景
          if (this.nodeInfo.is_builtin) {
            this.sceneList = [{
              typeName: 'PROCESS',
              name: this.$t('m.treeinfo["直接处理"]'),
            }];
          } else {
            this.sceneList.push({
              typeName: item.typeName,
              name: item.name,
            });
          }
        });
        // 节点名称
        this.formInfo.name = this.nodeInfo.name;
        // 节点描述
        this.formInfo.desc = this.nodeInfo.desc;
        // 节点标签
        this.formInfo.tag = this.nodeInfo.tag || '';
        // 处理场景
        this.formInfo.distribute_type = this.nodeInfo.distribute_type;
        // 派单人
        if (this.assignorsTypeList.some(assignor => assignor === this.formInfo.distribute_type)) {
          this.assignorsInfo = {
            type: this.nodeInfo.assignors_type,
            value: this.nodeInfo.assignors,
          };
        }
        // 处理人
        this.processorsInfo = {
          type: this.nodeInfo.processors_type,
          value: this.nodeInfo.processors,
        };
        // 单据状态
        this.formInfo.ticket_type = this.nodeInfo.extras.ticket_status ? this.nodeInfo.extras.ticket_status.type : 'keep';
        this.formInfo.ticket_key = this.nodeInfo.extras.ticket_status ? this.nodeInfo.extras.ticket_status.name : '';
        if (this.formInfo.ticket_type === 'custom') {
          this.getSecondLevelList();
        }
        // 转单
        this.formInfo.can_deliver = this.nodeInfo.can_deliver;
        if (this.formInfo.can_deliver) {
          this.deliversInfo = {
            type: this.nodeInfo.delivers_type,
            value: this.nodeInfo.delivers,
          };
        }
      },
      // 计算处理人类型需要排除的类型
      getExcludeRoleTypeList() {
        // 处理人
        let excludeProcessor = [];
        const isFirstNode = this.nodeInfo.is_first_state; // 提单节点

        // 内置节点
        if (this.nodeInfo.is_builtin) {
          excludeProcessor = ['BY_ASSIGNOR', 'STARTER', 'VARIABLE'];
        } else {
          excludeProcessor = ['OPEN'];
        }
        if (isFirstNode) {
          excludeProcessor.push('STARTER_LEADER');
        }
        // 是否使用权限中心角色
        // if (!this.flowInfo.is_iam_used) {
        //     excludeProcessor.push('IAM')
        //     this.assignorExclude.push('IAM')
        //     this.deliversExclude.push('IAM')
        // }
        // 处理场景如果不是'DISTRIBUTE_THEN_PROCESS' || 'DISTRIBUTE_THEN_CLAIM'，则去掉派单人指定
        if (this.nodeInfo.distribute_type !== 'DISTRIBUTE_THEN_PROCESS' && this.nodeInfo.distribute_type !== 'DISTRIBUTE_THEN_CLAIM') {
          excludeProcessor.push('BY_ASSIGNOR');
        }
        if (!this.flowInfo.is_biz_needed) {
          excludeProcessor.push('CMDB');
          this.deliversExclude.push('CMDB');
        }
        this.excludeProcessor = [...['EMPTY', 'API'], ...excludeProcessor];
      },
      // 处理场景
      changeDistribute(value) {
        this.getExcludeRoleTypeList();
        this.excludeProcessor = Array.from(new Set([...this.excludeProcessor, ...['BY_ASSIGNOR', 'VARIABLE']]));
        if (value === 'DISTRIBUTE_THEN_PROCESS' || value === 'DISTRIBUTE_THEN_CLAIM') {
          // 显示派单人指定
          this.excludeProcessor = this.excludeProcessor.filter(m => m !== 'BY_ASSIGNOR');
        }
        if (value === 'PROCESS') {
          // 显示引用变量
          this.excludeProcessor = this.excludeProcessor.filter(m => m !== 'VARIABLE');
        }
        // 选择不同的场景，需要清空派单人数据
        this.assignorsInfo = {
          type: '',
          value: '',
        };
      },
      // 获取二级状态数据
      handleTicket(value) {
        this.formInfo.ticket_key = '';
        if (value === 'custom') {
          if (!this.secondLevelList.length) {
            this.getSecondLevelList();
          }
        }
      },
      getSecondLevelList() {
        this.ticketKeyLoading = true;
        this.$store.dispatch('ticketStatus/getOverallTicketStatuses').then((res) => {
          this.secondLevelList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.ticketKeyLoading = false;
          });
      },
      backBasicInfo() {
        this.checkBasic();
        const basicForm = {};
        basicForm.name = this.formInfo.name;
        basicForm.desc = this.formInfo.desc || undefined;
        this.checkStatus.name = !this.formInfo.name;
        basicForm.tag = this.formInfo.tag;
        basicForm.distribute_type = this.formInfo.distribute_type;
        // 派单人
        basicForm.assignors_type = 'EMPTY';
        basicForm.assignors = '';
        if (this.$refs.assignors) {
          const data = this.$refs.assignors.getValue();
          basicForm.assignors_type = data.type;
          basicForm.assignors = data.value;
          this.checkStatus.assignors = !this.$refs.assignors.verifyValue();
        }
        // 处理人
        basicForm.processors_type = '';
        basicForm.processors = '';
        if (this.$refs.processors) {
          const data = this.$refs.processors.getValue();
          basicForm.processors_type = data.type;
          basicForm.processors = data.value;
          this.checkStatus.processors = !this.$refs.processors.verifyValue();
        }
        // 单据状态
        basicForm.ticket_type = this.formInfo.ticket_type;
        basicForm.ticket_key = this.formInfo.ticket_type === 'custom' ? this.formInfo.ticket_key : '';
        // 转单人
        basicForm.can_deliver = this.formInfo.can_deliver;
        basicForm.delivers_type = 'EMPTY';
        basicForm.delivers = '';
        if (this.$refs.delivers) {
          const data = this.$refs.delivers.getValue();
          basicForm.delivers_type = data.type;
          basicForm.delivers = data.value;
          this.checkStatus.delivers = !this.$refs.delivers.verifyValue();
        }
        return basicForm;
      },
      checkBasic() {
        this.$refs.basicForm.validate().then(() => {

        }, (validator) => {
          console.error(validator);
        });
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../../../scss/mixins/clearfix.scss';
    @import '../../../../../scss/mixins/scroller.scss';

    .bk-basic-info {
        padding-bottom: 20px;
        margin-bottom: 20px;
    }

    .bk-item-width {
        width: 448px;
    }
    .bk-form-width {
        width: 448px;
    }
    .bk-form-display {
        float: left;
        margin-right: 10px;
    }
    .bk-error-info {
        line-height: 32px;
        color: #ff5656;
        font-size: 12px;
    }
    /deep/ .bk-form-width {
        width: 448px;
    }
</style>
