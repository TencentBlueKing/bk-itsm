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
    <div class="bk-basic-info" v-if="!step">
      <div class="bk-service-name">
        <h1><span class="is-outline"></span>{{ $t('m.treeinfo["基本信息"]') }}</h1>
        <div class="task-info">
          <div class="info-item">
            <span>{{ $t('m.common["模板名称："]') }}</span>
            <div class="static" v-if="!firstStepInfo.changeName">
              <span>{{firstStepInfo.name}}</span>
              <span class="bk-itsm-icon icon-edit-bold isOn" @click="firstStepInfo.changeName = true"></span>
            </div>
            <div class="dynamic" v-else>
              <bk-form :model="firstStepInfo" :label-width="10" :rules="formRule" ref="taskInfoForm">
                <bk-form-item :label="''" :required="true" :property="'name'">
                  <bk-input v-model="firstStepInfo.name"
                    style="width: 450px"
                    maxlength="120">
                  </bk-input>
                  <div class="operate">
                    <bk-button :theme="'primary'" text :title="$t(`m.systemConfig['保存']`)" class="ml10" @click="stepChange('', false, 'changeName')">{{$t(`m.systemConfig['保存']`)}}</bk-button>
                    <span>|</span>
                    <bk-button :theme="'primary'" text :title="$t(`m.wiki['取消']`)" class="ml10" @click="cancelEdit('changeName')">{{$t(`m.wiki['取消']`)}}</bk-button>
                  </div>
                </bk-form-item>
              </bk-form>
            </div>
          </div>
          <div class="info-item">
            <span>{{$t(`m.user['负责人：']`)}}</span>
            <div class="static" v-if="!firstStepInfo.changeOwners">
              <span>{{changedTemplateInfo.owners || '--'}}</span>
              <span class="bk-itsm-icon icon-edit-bold isOn" @click="firstStepInfo.changeOwners = true"></span>
            </div>
            <div class="dynamic" v-else>
              <bk-form :model="firstStepInfo" :label-width="10" ref="taskInfoForm">
                <bk-form-item :label="''" :ext-cls="'flex-form-item'">
                  <div style="width: 450px;display: inline-flex">
                    <member-select v-model="firstStepInfo.ownersInputValue" style="width: 100%"></member-select>
                  </div>
                  <div class="operate">
                    <bk-button :theme="'primary'" text :title="$t(`m.systemConfig['保存']`)" class="ml10" @click="stepChange('', false, 'changeOwners')">{{$t(`m.systemConfig['保存']`)}}</bk-button>
                    <span>|</span>
                    <bk-button :theme="'primary'" text :title="$t(`m.wiki['取消']`)" class="ml10" @click="cancelEdit('changeOwners')">{{$t(`m.wiki['取消']`)}}</bk-button>
                  </div>
                </bk-form-item>
              </bk-form>
            </div>
          </div>
          <div class="info-item top-item">
            <span>{{ $t('m.common["模板说明："]') }}</span>
            <div class="static" v-if="!firstStepInfo.changeDesc">
              <span>{{firstStepInfo.desc || '--'}}</span>
              <span class="bk-itsm-icon icon-edit-bold isOn" @click="firstStepInfo.changeDesc = true"></span>
            </div>
            <div class="dynamic" v-else>
              <bk-form :model="firstStepInfo" :label-width="10" ref="taskInfoForm">
                <bk-form-item>
                  <bk-input style="width: 450px"
                    :placeholder="$t(`m.taskTemplate['请输入任务描述']`)"
                    :type="'textarea'"
                    :rows="3"
                    :maxlength="64"
                    v-model="firstStepInfo.desc">
                  </bk-input>
                  <div class="operate">
                    <bk-button :theme="'primary'" text :title="$t(`m.systemConfig['保存']`)" class="ml10" @click="stepChange('', false, 'changeDesc')">{{$t(`m.systemConfig['保存']`)}}</bk-button>
                    <span>|</span>
                    <bk-button :theme="'primary'" text :title="$t(`m.wiki['取消']`)" class="ml10" @click="cancelEdit('changeDesc')">{{$t(`m.wiki['取消']`)}}</bk-button>
                  </div>
                </bk-form-item>
              </bk-form>

            </div>
          </div>
        </div>
      </div>
    </div>
    <field-config
      ref="field"
      :template-info="changedTemplateInfo"
      :template-stage="stepList[step].stage">
    </field-config>
    <!-- 触发器组件 -->
    <common-trigger-list
      :source-id="changedTemplateInfo.id"
      :step-signal="stepList[step].signal"
      :template-stage="stepList[step].stage">
    </common-trigger-list>
    <!-- 步骤操作按钮 -->
    <div class="bk-common-step">
      <bk-button theme="default"
        data-test-id="taskTemplate-button-commonStep-nextStep"
        v-if="step"
        class="mr10"
        :loading="buttonLoading"
        :title="$t(`m.taskTemplate['上一步']`)"
        @click="stepChange('previous')">
        {{$t(`m.taskTemplate['上一步']`)}}
      </bk-button>
      <bk-button theme="primary"
        :data-test-id="step === 2 ? 'taskTemplate-button-commonStep-saveStep' : 'taskTemplate-button-commonStep-pervStep'"
        class="mr10"
        :loading="buttonLoading"
        :title="step === 2 ? $t(`m.taskTemplate['完成']`) : $t(`m.deployPage['下一步']`)"
        @click="stepChange">
        {{ step === 2 ? $t(`m.taskTemplate['完成']`) : $t(`m.deployPage['下一步']`) }}
      </bk-button>
      <bk-button theme="default"
        data-test-id="taskTemplate-button-commonStep-saveDrafts"
        class="mr10"
        :loading="buttonLoading"
        :title="$t(`m.trigger['保持草稿']`)"
        @click="stepChange('', true)">
        {{$t(`m.trigger['保持草稿']`)}}
      </bk-button>
      <bk-button theme="default"
        data-test-id="taskTemplate-button-commonStep-closeTask"
        class="mr10"
        :loading="buttonLoading"
        :title="$t(`m.taskTemplate['取消']`)"
        @click="cancelStep">
        {{$t(`m.taskTemplate['取消']`)}}
      </bk-button>
    </div>
  </div>
</template>

<script>
  import fieldConfig from '../../processDesign/nodeConfigue/components/fieldConfig';
  import commonTriggerList from './commonTriggerList';
  import memberSelect from '../../../commonComponent/memberSelect';
  import { errorHandler } from '../../../../utils/errorHandler';

  export default {
    name: 'commonStep',
    components: {
      fieldConfig,
      commonTriggerList,
      memberSelect,
    },
    props: {
      templateInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      step: {
        type: Number,
        default: '',
      },
      stepList: {
        type: Array,
        default() {
          return [];
        },
      },
    },
    data() {
      return {
        firstStepInfo: {
          name: '',
          ownersInputValue: '',
          desc: '',
          changeName: '',
          changeOwners: '',
          changeDesc: '',
        },
        formRule: {
          name: [
            {
              required: true,
              message: this.$t('m.taskTemplate[\'请输入任务名称\']'),
              trigger: 'blur',
            },
          ],
        },
        buttonLoading: false,
        // 模板信息会在编辑时保存，这里单独保存
        changedTemplateInfo: {},
      };
    },
    watch: {
      step() {
        this.initData();
      },
    },
    async mounted() {
      await this.initData();
    },
    methods: {
      async initData() {
        this.changedTemplateInfo = JSON.parse(JSON.stringify(this.templateInfo.itemInfo));
        this.firstStepInfo.name = this.changedTemplateInfo.name;
        this.firstStepInfo.ownersInputValue = this.changedTemplateInfo.owners ? this.changedTemplateInfo.owners.split(',') : [];
        this.firstStepInfo.desc = this.changedTemplateInfo.desc;
      },
      cancelStep() {
        this.$parent.backTab();
      },
      // 下一步操作
      async stepChange(type = 'next', isDraft = false, isTemplate = '') {
        if (isTemplate === 'changeName') {
          let valid = false;
          await this.$refs.taskInfoForm.validate().then(() => {
            valid = true;
          }, () => {});
          if (!valid) {
            return;
          }
        }
        const patch = {
          params: {
            name: this.firstStepInfo.name,
            component_type: this.changedTemplateInfo.component_type,
            is_draft: isDraft ? true : (this.step === 2 ? false : this.changedTemplateInfo.is_draft),
            is_builtin: false,
            owners: this.firstStepInfo.ownersInputValue.join(','),
            desc: this.firstStepInfo.desc,
          },
          id: this.changedTemplateInfo.id,
        };
        if (!isTemplate) {
          patch.params.task_fields = {
            stage: this.stepList[this.step].stage,
            task_field_ids: this.$refs.field.showTabList.map(field => field.id),
          };
        }
        this.buttonLoading = true;
        this.$store.dispatch('taskTemplate/updateTemplate', patch).then((res) => {
          this.$bkMessage({
            message: this.$t('m.taskTemplate[\'保存成功\']'),
            theme: 'success',
          });
          this.changedTemplateInfo = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.$parent.changeTemplateInfo(this.changedTemplateInfo);
            this.initData();
            this.buttonLoading = false;
            if (isTemplate) {
              this.cancelEdit(isTemplate);
              return;
            }
            if (isDraft) {
              return;
            }
            if (this.step === 2) {
              this.$parent.backTab();
              return;
            }
            const stepIndex = type === 'previous' ? this.step - 1 : this.step + 1;
            const temp = {
              id: stepIndex + 1,
              name: this.stepList[stepIndex].name,
              type: 'primary',
              is_draft: this.changedTemplateInfo.is_draft,
              show: false,
            };
            this.$parent.changeTree(temp, stepIndex);
          });
      },
      cancelEdit(type) {
        this.firstStepInfo[type] = '';
        if (type === 'changeName') {
          this.firstStepInfo.name = this.changedTemplateInfo.name;
        } else if (type === 'changeOwners') {
          this.firstStepInfo.ownersInputValue = this.changedTemplateInfo.owners ? this.changedTemplateInfo.owners.split(',') : [];
        } else {
          this.firstStepInfo.desc = this.changedTemplateInfo.desc;
        }
      },
    },
  };
</script>

<style scoped lang="scss">
    @import '../taskCss/commonStep';
    .flex-form-item{
        /deep/ .bk-form-content{
            display: inline-flex;
        }
    }
</style>
