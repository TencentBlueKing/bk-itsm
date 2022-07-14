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
  <!-- 终止,挂起,转单 -->
  <bk-dialog
    v-model="openFormInfo.isShow"
    :render-directive="'if'"
    :title="openFormInfo.title"
    :width="openFormInfo.width"
    :header-position="openFormInfo.headerPosition"
    :loading="submitting"
    :auto-close="openFormInfo.autoClose"
    :mask-close="openFormInfo.autoClose"
    @confirm="submitForm"
    @cancel="cancelForm">
    <!-- 终止/暂停 -->
    <template v-if="openFormInfo.btnInfo.key === 'TERMINATE' || openFormInfo.btnInfo.key === 'SUSPEND'">
      <bk-form :label-width="200" form-type="vertical" :model="formData" :rules="rules" ref="dialogForm">
        <template v-if="openFormInfo.btnInfo.key === 'TERMINATE'">
          <bk-form-item :label="$t(`m.newCommon['终止原因']`)" :required="true" :property="'terminate_message'">
            <bk-input
              :placeholder="$t(`m.newCommon['请输入终止原因']`)"
              :type="'textarea'"
              :rows="3"
              v-model="formData.terminate_message">
            </bk-input>
          </bk-form-item>
        </template>
        <template v-if="openFormInfo.btnInfo.key === 'SUSPEND'">
          <bk-form-item :label="$t(`m.newCommon['挂起原因']`)" :required="true" :property="'suspend_message'">
            <bk-input
              :placeholder="$t(`m.newCommon['请输入挂起原因']`)"
              :type="'textarea'"
              :rows="3"
              v-model="formData.suspend_message">
            </bk-input>
          </bk-form-item>
        </template>
      </bk-form>
    </template>
    <!-- 分派 -->
    <template v-if="openFormInfo.btnInfo.key === 'DISTRIBUTE'">
      <bk-form :label-width="200" :rules="rules" form-type="vertical" ref="dialogForm">
        <bk-form-item :label="$t(`m.newCommon['指定处理人']`)" :required="true">
          <deal-person
            ref="personSelect"
            class="deal-person"
            form-type="vertical"
            :shortcut="true"
            :value="{
              type: distribution.type,
              value: distribution.value
            }"
            :specify-id-list="distribution.specifyIdList"
            :exclude-role-type-list="distribution.excludeTypeList"
            :show-role-type-list="distribution.includeTypeList"
            :required-msg="$t(`m.treeinfo['派单人不能为空']`)">
          </deal-person>
        </bk-form-item>
      </bk-form>
    </template>
    <!-- 转单 -->
    <template v-if="openFormInfo.btnInfo.key === 'DELIVER' || openFormInfo.btnInfo.key === 'EXCEPTION_DISTRIBUTE'">
      <bk-form :model="formData" :rules="rules" :label-width="200" form-type="vertical" ref="dialogForm">
        <bk-form-item :label="$t(`m.newCommon['${type}至：']`)" :required="true">
          <deal-person
            ref="personSelect"
            class="deal-person"
            form-type="vertical"
            :shortcut="true"
            :value="{
              type: deliverInfo.type,
              value: deliverInfo.value
            }"
            :specify-id-list="deliverInfo.specifyIdList"
            :exclude-role-type-list="type === '转单' ? deliverInfo.excludeTypeList : excludeAssignList"
            :show-role-type-list="deliverInfo.includeTypeList"
            :required-msg="$t(`m.newCommon['${type}人不能为空']`)">
          </deal-person>
        </bk-form-item>
        <bk-form-item :label="$t(`m.newCommon['${type}原因']`)" :required="true" :property="'deliverReason'">
          <bk-input
            :placeholder="$t(`m.newCommon['请输入${type}原因']`)"
            :type="'textarea'"
            :rows="3"
            v-model="formData.deliverReason">
          </bk-input>
        </bk-form-item>
      </bk-form>
    </template>
  </bk-dialog>
</template>

<script>
  import commonMix from '@/views/commonMix/common.js';
  import DealPerson from '@/views/processManagement/processDesign/nodeConfigue/components/dealPerson';

  export default {
    name: 'NodeDealDialog',
    components: {
      DealPerson,
    },
    mixins: [commonMix],
    props: {
      openFormInfo: {
        type: Object,
        default: () => ({}),
      },
      nodeInfo: {
        type: Object,
        default: () => ({}),
      },
      submitting: {
        type: Boolean,
        default: false,
      },
      allGroups: {
        type: Array,
        default: () => [],
      },
      ticketInfo: {
        type: Object,
        default: () => ({}),
      },
    },
    data() {
      return {
        falseStatus: false,
        formData: {
          terminate_message: '', // 终止原因
          suspend_message: '', // 挂起原因
          deliverReason: '', // 转单原因
        },
        // 校验
        rules: {},
        // 派单人
        distribution: {
          excludeTypeList: [],
          includeTypeList: [],
          specifyIdList: [],
          type: '',
          value: '',
        },
        // 转单人
        deliverInfo: {
          excludeTypeList: [], // 排除类型
          includeTypeList: [], // 包含类型
          specifyIdList: [], // 包含人员 id 列表
          type: '',
          value: '',
        },
        excludeAssignList: [
          'CMDB',
          'VARIABLE',
          'EMPTY',
          'STARTER_LEADER',
          'OPEN',
          'STARTER',
          'BY_ASSIGNOR',
          'ASSIGN_LEADER',
          'IAM',
          'API',
          'ORGANIZATION',
          'SYSTEM',
        ],
      };
    },
    computed: {
      //  转单 or 异常分派
      type() {
        return this.openFormInfo.btnInfo.key === 'DELIVER' ? '转单' : '分派';
      },
    },
    watch: {
      'openFormInfo.isShow'() {
        this.clearFormData();
        this.initData();
      },
    },
    methods: {
      initData() {
        // 校验
        this.rules.terminate_message = this.checkCommonRules('select').select;
        this.rules.suspend_message = this.checkCommonRules('select').select;
        this.rules.deliverReason = this.checkCommonRules('select').select;

        // 初始化 分派/转单 类型
        const isDelive = this.openFormInfo.btnInfo.key === 'DELIVER';
        const specialType = ['OPEN', 'BY_ASSIGNOR'];
        const {
          assignors, // 分派人（username + display_name）
          assignors_type: assignorsType, // 分派类型
          origin_assignors: originAssignors, // 原始分派人(id)
          delivers,
          delivers_type: deliversType,
          origin_delivers: originDelivers,
        } = this.nodeInfo;

        const handler = isDelive ? delivers : assignors;
        const originHandler = isDelive ? originDelivers : originAssignors;
        const handlerType = isDelive ? deliversType : assignorsType;

        let includeTypeList = [];
        let specifyIdList = [];
        if (specialType.includes(handlerType)) {
          // 特殊类型, 不限制选择
          includeTypeList = ['PERSON', 'GENERAL', 'ORGANIZATION'];
          specifyIdList = [];
          if (!isDelive) {
            // 分派时
            includeTypeList.push('STARTER');
          }
          if (this.ticketInfo.is_biz_need) {
            // 有关联业务才能显示
            includeTypeList.push('CMDB');
          }
        } else if (handlerType === 'PERSON') {
          // 类型为个人, 只能在 originHandler 中选
          includeTypeList = ['PERSON'];
          specifyIdList = [{ type: 'PERSON', list: originHandler.split(',').filter((id) => !!id) }];
        } else {
          // 其他默认类型（通用角色、组织架构、cmdb 角色...）, PERSON 只能在 handler 中选，`handlerType` 只能在 originHandler 中选
          includeTypeList = ['PERSON', handlerType];
          const includePerson = handler.split(',').map((fullName) => fullName.replace(/\(.+\)/g, ''));
          specifyIdList = [
            { type: 'PERSON', list: includePerson },
            { type: handlerType, list: originHandler.split(',') },
          ];
        }

        if (isDelive) {
          this.deliverInfo.includeTypeList = includeTypeList;
          this.deliverInfo.specifyIdList = specifyIdList;
          if (includeTypeList.length === 1) {
            this.deliverInfo.type = includeTypeList[0];
          }
        } else {
          this.distribution.includeTypeList = includeTypeList;
          this.distribution.specifyIdList = specifyIdList;
          if (includeTypeList.length === 1) {
            this.distribution.type = includeTypeList[0];
          }
        }
      },
      clearFormData() {
        this.deliverInfo = {
          excludeTypeList: [],
          includeTypeList: [],
          specifyIdList: [],
          type: '',
          value: '',
        };
        this.distribution = {
          excludeTypeList: [],
          includeTypeList: [],
          specifyIdList: [],
          type: '',
          value: '',
        };
        this.formData = {
          terminate_message: '',
          suspend_message: '',
          deliverReason: '',
        };
      },
      // 确认事件
      submitForm() {
        this.$refs.dialogForm.validate().then(
          () => {
            let person = {};
            if (this.$refs.personSelect) {
              const res = this.$refs.personSelect.verifyValue();
              if (!res) {
                return false;
              }
              person = this.$refs.personSelect.getValue();
            }

            this.$emit('submitFormAjax', Object.assign(this.formData, { person }));
          },
          (validator) => {
            console.warn(validator);
          }
        );
      },
      // 取消事件
      cancelForm() {
        this.openFormInfo.isShow = false;
      },
    },
  };
</script>

<style lang="scss" scoped>
.deal-person {
  /deep/ .bk-form-width {
    width: 100%;
  }
}
.bk-error-info {
  line-height: 32px;
  color: #ff5656;
  font-size: 12px;
}
</style>
