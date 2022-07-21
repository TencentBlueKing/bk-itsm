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
  <div class="bk-design-first">
    <SectionCard :label="$t(`m.trigger['基础信息']`)" :desc="$t(`m.tickets['流程基础信息']`)" :label-width="210">
      <div class="base-info">
        <bk-form
          :label-width="400"
          :model="formInfo"
          :rules="rules"
          form-type="vertical"
          ref="stepOneForm">
          <bk-form-item
            :label="$t(`m.deployPage['流程名称']`)"
            :required="true"
            :property="'name'">
            <bk-input v-model.trim="formInfo.name"
              maxlength="120"
              :placeholder="$t(`m.deployPage['请输入流程名称']`)">
            </bk-input>
          </bk-form-item>
          <bk-form-item
            :label="$t(`m.deployPage['基础模型']`)"
            :required="true"
            :desc="$t(`m.deployPage['可直接引用模板中的字段']`)"
            :property="'flowModuleType'">
            <bk-select v-model="formInfo.flowModuleType"
              :disabled="formInfo.flowModuleTypeDisabled"
              :clearable="false"
              searchable
              :font-size="'medium'">
              <bk-option v-for="option in flowModuleTypes"
                :key="option.id"
                :id="option.id"
                :name="option.name">
              </bk-option>
            </bk-select>
          </bk-form-item>
          <bk-form-item
            :label="$t(`m.deployPage['是否关联业务']`)"
            :required="true">
            <bk-switcher v-model="formInfo.business" size="small"></bk-switcher>
          </bk-form-item>
          <bk-form-item
            :label="$t(`m.newCommon['是否使用权限中心角色']`)"
            :required="true">
            <bk-switcher v-model="formInfo.useIam" size="small"></bk-switcher>
          </bk-form-item>
          <bk-form-item :label="$t(`m.user['负责人：']`)">
            <member-select v-model="formInfo.owners"></member-select>
          </bk-form-item>
          <bk-form-item :label="$t(`m.deployPage['流程说明']`)">
            <bk-input type="textarea"
              style="background-color: white"
              v-model="formInfo.desc"
              :rows="3"
              :maxlength="100"
              :placeholder="$t(`m.deployPage['请输入流程说明，最多能输入100个字']`)"></bk-input>
          </bk-form-item>
        </bk-form>
        <div class="bk-design-btn">
          <bk-button theme="default"
            class="mr10"
            :title="$t(`m.deployPage['返回']`)"
            :disabled="isSaveing"
            @click="previousStep">
            {{ $t('m.deployPage["返回"]') }}
          </bk-button>
          <bk-button theme="primary"
            :title="!isNewFlow ? $t(`m.deployPage['保存']`) : $t(`m.deployPage['下一步']`)"
            :loading="isSaveing"
            @click="changeText">
            {{!isNewFlow ? $t(`m.deployPage['保存']`) : $t(`m.deployPage['下一步']`)}}
          </bk-button>
        </div>
      </div>
    </SectionCard>
  </div>
</template>
<script>
  import commonMix from '../../../commonMix/common.js';
  import memberSelect from '../../../commonComponent/memberSelect';
  import { errorHandler } from '../../../../utils/errorHandler.js';
  import SectionCard from '@/components/common/layout/SectionCard';

  export default {
    name: 'CreateProcess',
    components: { memberSelect, SectionCard },
    mixins: [commonMix],
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
        // 基础模型类型
        flowModuleTypes: [],
        // 新增or修改
        addStatus: false,
        // 表单数据
        formInfo: {
          // 流程名称
          name: '',
          // 流程说明
          desc: '',
          // 流程类型
          flowType: '',
          // 基础模型类型
          flowModuleType: '',
          // 关联业务
          business: false,
          // 流程配置中使用权限中心角色
          useIam: false,
          flowModuleTypeDisabled: false,
          owners: [],
        },
        // 校验
        rules: {},
        // 向父组件传值
        parentInfo: {
          status: 'success',
          index: 0,
          firstStep: {},
        },
      };
    },
    watch: {
      flowInfo() {
        this.initInfo();
      },
    },
    mounted() {
      this.getFlowModuleTypes();
      // 判断是编辑数据还是新增数据
      if (!this.isNewFlow) {
        this.initInfo();
      }
      // 校验
      this.rules.name = this.checkCommonRules('name').name;
      this.rules.flowModuleType = this.checkCommonRules('select').select;
    },
    methods: {
      // 基础模型类型
      getFlowModuleTypes() {
        const params = {
          all: true,
        };
        this.$store.dispatch('basicModule/get_tables', params).then((res) => {
          this.flowModuleTypes = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 通过ID获取数据
      initInfo() {
        this.formInfo.name = this.flowInfo.name;
        this.formInfo.owners = this.flowInfo.owners ? this.flowInfo.owners.split(',') : [];
        this.formInfo.desc = this.flowInfo.desc;
        this.formInfo.flowType = this.flowInfo.flow_type;
        this.formInfo.flowModuleType = this.flowInfo.table || '';
        this.formInfo.flowModuleTypeDisabled = !!this.flowInfo.table;
        this.formInfo.business = this.flowInfo.is_biz_needed;
        this.formInfo.useIam = this.flowInfo.is_iam_used;
      },
      // 数据校验
      changeText() {
        this.$refs.stepOneForm.validate().then(() => {
          this.stepNext();
        });
      },
      // 下一步操作
      stepNext() {
        if (this.isSaveing) {
          return;
        }
        // 基础参数
        const params = {
          name: this.formInfo.name,
          owners: this.formInfo.owners.join(','),
          flow_type: this.formInfo.flowType || 'other',
          table: this.formInfo.flowModuleType,
          desc: this.formInfo.desc,
          is_biz_needed: this.formInfo.business,
          is_iam_used: this.formInfo.useIam,
        };
        // 保存
        this.$emit('saveFlowInfo', params, this.isNewFlow);
        this.$emit('onBusinessChange', this.formInfo.business);
      },
      previousStep() {
        this.$router.push({
          name: 'ProcessHome',
        });
      },
    },
  };
</script>

<style lang='scss' scoped>
    .bk-design-first {
        padding: 20px;
        .base-info {
            width: 600px;
        }
    }
    .bk-design-btn {
        margin-top: 20px;
    }
</style>
