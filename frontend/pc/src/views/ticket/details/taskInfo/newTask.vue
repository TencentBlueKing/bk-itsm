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
  <div class="bk-new-task">
    <h3 class="setion-title">
      <span
        class="setion-title-icon"
        @click.stop="showTaskInfo = !showTaskInfo"
      >
        <i v-if="showTaskInfo" class="bk-icon icon-angle-down"></i>
        <i v-else class="bk-icon icon-angle-right"></i>
      </span>
      {{ $t(`m.task['任务信息']`) }}
    </h3>
    <bk-form
      v-show="showTaskInfo"
      :label-width="200"
      ref="addTask"
      form-type="vertical"
      class="task-info"
    >
      <template v-if="nodeInfo.task_schemas.length !== 0">
        <bk-form-item
          :label="$t(`m.task['任务模板']`)"
          :required="true"
          :property="'template'"
          class="half-width-item"
        >
          <bk-select
            searchable
            :clearable="falseStatus"
            v-model="formData.template"
            @selected="selectTemplate"
            :disabled="!!itemContent.id"
          >
            <bk-option
              v-for="option in nodeInfo.task_schemas"
              :key="option.id"
              :id="option.id"
              :name="option.name"
            ></bk-option>
          </bk-select>
          <p class="bk-task-error" v-if="checkInfo.template">
            {{ $t(`m.task['任务模板为必填项']`) }}
          </p>
        </bk-form-item>
      </template>
      <!-- 处理人 -->
      <template v-if="isComplexMembers">
        <bk-form-item
          :label="$t(`m.task['处理人']`)"
          :required="true"
          :property="'processor'"
        >
          <deal-person
            ref="personSelect"
            class="deal-person"
            :shortcut="true"
            :value="dealPersonData"
            :exclude-role-type-list="excludeTypeList"
          ></deal-person>
        </bk-form-item>
      </template>
    </bk-form>
    <h3 class="setion-title">
      <span
        class="setion-title-icon"
        @click.stop="showTemplateInfo = !showTemplateInfo"
      >
        <i v-if="showTemplateInfo" class="bk-icon icon-angle-down"></i>
        <i v-else class="bk-icon icon-angle-right"></i>
      </span>
      {{ $t(`m.tickets['模板信息']`) }}
    </h3>
    <!-- 自定义渲染拉取到的表单字段 -->
    <div
      class="bk-field-info"
      v-bkloading="{ isLoading: fieldLoading }"
      v-show="showTemplateInfo"
    >
      <field-info
        v-if="showField"
        ref="fieldInfo"
        :fields="fieldList"
        :basic-infomation="basicInfomation"
      ></field-info>
    </div>
    <div slot="footer" class="bk-submit-task">
      <bk-button
        :theme="'primary'"
        :title="$t(`m.task['确认']`)"
        :disabled="btnLoading || fieldLoading"
        class="mr10"
        @click="submitTask"
      >
        {{ $t(`m.task['确认']`) }}
      </bk-button>
      <bk-button
        :theme="'default'"
        :disabled="btnLoading"
        :title="$t(`m.task['取消']`)"
        @click="closeSlider"
      >
        {{ $t(`m.task['取消']`) }}
      </bk-button>
    </div>
  </div>
</template>

<script>
  import fieldInfo from '@/views/managePage/billCom/fieldInfo.vue';
  import DealPerson from '@/views/processManagement/processDesign/nodeConfigue/components/dealPerson';
  import commonMix from '@/views/commonMix/common.js';
  import apiFieldsWatch from '@/views/commonMix/api_fields_watch.js';
  import { errorHandler } from '@/utils/errorHandler';
  import { deepClone } from '@/utils/util';

  export default {
    name: 'newTask',
    components: {
      fieldInfo,
      DealPerson,
    },
    mixins: [apiFieldsWatch, commonMix],
    props: {
      basicInfomation: {
        type: Object,
        default() {
          return {};
        },
      },
      itemContent: {
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
    },
    data() {
      return {
        fieldLoading: false,
        showField: false,
        btnLoading: false,
        falseStatus: false,
        showTaskInfo: true,
        showTemplateInfo: true,
        dealPersonData: {
          value: '',
          type: 'PERSON',
        },
        excludeTypeList: [
          'OPEN',
          'STARTER',
          'BY_ASSIGNOR',
          'EMPTY',
          'VARIABLE',
          'CMDB',
          'ORGANIZATION',
          'IAM',
          'STARTER_LEADER',
          'API',
        ],
        formData: {
          template: '',
        },
        fieldList: [],
        isComplexMembers: false,
        memberContent: {},
        // 校验
        checkInfo: {
          template: false,
          fields: false,
        },
        validatePopInfo: {
          content: '',
        },
      };
    },
    created() {
      if (this.itemContent.id) {
        this.initData();
      } else {
        this.formData.template = this.nodeInfo.task_schemas[0].id;
        this.getFieldList(this.formData.template);
      }
    },
    methods: {
      initData() {
        // 渲染任务模板信息
        this.formData.template = this.itemContent.task_schema_id;
        // 处理人渲染
        this.dealPersonData.value = this.itemContent.processors;
        this.dealPersonData.type = this.itemContent.processors_type;
        // 通过模板渲染信息
        this.fieldLoading = true;
        this.showField = false;
        const { id } = this.itemContent;
        this.$store
          .dispatch('taskFlow/getTaskInfo', id)
          .then((res) => {
            this.fieldList = res.data.fields.create_fields.filter(item => item.type !== 'COMPLEX-MEMBERS');
            this.isComplexMembers = res.data.fields.create_fields.some(item => item.type === 'COMPLEX-MEMBERS');
            this.fieldList.forEach((item) => {
              if (item.type === 'CASCADE') {
                item.type = 'SELECT';
              }
              this.$set(item, 'showFeild', true);
              this.$set(item, 'val', item.value || '');
            });
            this.isNecessaryToWatch(
              { fields: this.fieldList },
              'submit'
            );
            this.showField = true;
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.fieldLoading = false;
          });
      },
      // 选择任务模板
      selectTemplate(value) {
        this.getFieldList(value);
      },
      // 获取字段列表
      getFieldList(id) {
        const params = {
          task_schema_id: id,
          stage: 'CREATE',
        };
        this.fieldLoading = true;
        this.showField = false;
        this.$store
          .dispatch('taskFlow/getTaskField', params)
          .then((res) => {
            this.fieldList = res.data.filter(item => item.type !== 'COMPLEX-MEMBERS');
            this.isComplexMembers = res.data.some(item => item.type === 'COMPLEX-MEMBERS');
            this.fieldList.forEach((item) => {
              if (item.type === 'CASCADE') {
                item.type = 'SELECT';
              }
              this.$set(item, 'showFeild', true);
              this.$set(item, 'val', item.value || '');
            });
            this.isNecessaryToWatch(
              { fields: this.fieldList },
              'submit'
            );
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.fieldLoading = false;
            this.showField = true;
          });
      },
      closeSlider() {
        this.$emit('closeSlider');
      },
      submitTask() {
        const params = {
          processors: '',
          processors_type: '',
          fields: {},
          need_start: this.nodeInfo.can_execute_task, // 执行节点创建的任务需要立即启动
          state_id: this.nodeInfo.state_id,
        };
        // 新建参数
        if (!this.itemContent.id) {
          params.ticket_id = this.basicInfomation.id;
          params.task_schema_id = this.formData.template;
        }
        if (this.$refs.personSelect) {
          const data = this.$refs.personSelect.getValue();
          params.processors_type = data.type;
          params.processors = data.value;
        }
        if (this.fieldList.length) {
          // 将字段信息value值进行转换
          this.fieldFormatting(this.fieldList);
          this.fieldList.forEach((item) => {
            if (item.type === 'SOPS_TEMPLATE') {
              const sopsContent = deepClone(item.sopsContent);
              sopsContent.constants.forEach((contentItem) => {
                this.$set(
                  contentItem,
                  'value',
                  sopsContent.formData[contentItem.key]
                );
              });
              params.fields[item.key] = {
                id: sopsContent.id,
                template_source: sopsContent.context.project
                  .bk_biz_id
                  ? 'business'
                  : 'common',
                bk_biz_id:
                  this.basicInfomation.bk_biz_id !== -1
                    ? this.basicInfomation.bk_biz_id
                    : '',
                constants: sopsContent.constants,
              };
              if (
                sopsContent.createWay === 'task'
                || sopsContent.createWay === 'started_task'
              ) {
                params.fields[item.key].task_id =                                sopsContent.sopsTask.id;
                params.fields[item.key].id =                                sopsContent.sopsTask.template_id;
              }
              // 标准运维排除执行节点
              if (
                sopsContent.planId
                && sopsContent.planId.length > 0
              ) {
                params.exclude_task_nodes_id =                                sopsContent.exclude_task_nodes_id;
              } else {
                params.exclude_task_nodes_id = [];
              }
              // 标准运维任务参数
              params.source = sopsContent.createWay;
            } else if (item.type === 'DEVOPS_TEMPLATE') {
              params.fields.sub_task_params =                            item.devopsContent.variables;
              params.fields.sub_task_params.project_id =                            item.devopsContent.project_id;
              params.fields.sub_task_params.pipeline_id =                            item.devopsContent.pipeline_id;
            } else {
              params.fields[item.key] = item.value;
            }
          });
          if (!params.source) {
            params.source = 'template';
          }
        }
        // 数据校验
        if (this.checkValue()) {
          return;
        }
        const relateValid = this.relatedRegex(
          this.fieldList,
          this.fieldList
        );
        if (!relateValid.result) {
          relateValid.validList.forEach((item) => {
            if (!item.result) {
              item.validList.forEach((it) => {
                this.validatePopInfo.content += `${it.tips}、`;
              });
              this.validatePopInfo.content = `${this.validatePopInfo.content.substr(
                0,
                this.validatePopInfo.content.length - 1
              )}！`;
            }
          });
          this.$bkInfo({
            type: 'warning',
            title: '',
            subTitle: this.validatePopInfo.content,
          });
          this.validatePopInfo.content = '';
          return;
        }
        this.btnLoading = true;
        if (this.itemContent.id) {
          const { id } = this.itemContent;
          this.$store
            .dispatch('taskFlow/editorTask', { params, id })
            .then(() => {
              this.$bkMessage({
                message: this.$t('m.task[\'编辑任务成功\']'),
                theme: 'success',
              });
              this.closeSlider();
              // 刷新数据
              this.$emit('getTaskList');
            })
            .catch((res) => {
              errorHandler(res, this);
            })
            .finally(() => {
              this.btnLoading = false;
            });
        } else {
          this.$store
            .dispatch('taskFlow/createTask', { params })
            .then(() => {
              this.$bkMessage({
                message: this.$t('m.task[\'新建任务成功\']'),
                theme: 'success',
              });
              this.closeSlider();
              // 刷新数据
              this.$emit('getTaskList');
            })
            .catch((res) => {
              errorHandler(res, this);
            })
            .finally(() => {
              this.btnLoading = false;
            });
        }
      },
      checkValue() {
        this.checkInfo.template = !this.formData.template;
        // 处理人
        const personStatus = this.isComplexMembers
          ? !this.$refs.personSelect.verifyValue()
          : false;
        // 字段
        const fieldStatus = !this.$refs.fieldInfo.checkValue();
        return personStatus || this.checkInfo.template || fieldStatus;
      },
    },
  };
</script>

<style scoped lang="scss">
@import "../../../../scss/mixins/clearfix";
@import "../../../../scss/mixins/scroller";

.bk-new-task {
    margin-bottom: 70px;
    padding: 10px 65px 0px 30px;
}
.bk-task-error {
    font-size: 12px;
    color: #ea3636;
    line-height: 18px;
    margin: 2px 0 0;
}
.pr10 {
    padding-right: 10px;
}
.task-info {
    padding: 0 20px;
}
.bk-field-info {
    margin-top: 8px;
    padding: 0 20px;
    @include clearfix;
}
.bk-half-big {
    float: left;
    width: 100%;
    padding-right: 10px;
    margin-top: 8px;
}
.bk-half-small {
    float: left;
    width: 50%;
    padding-right: 10px;
}
.bk-submit-task {
    position: absolute;
    bottom: 0;
    left: 0;
    padding: 8px 32px;
    width: 100%;
    background: #fafbfd;
    z-index: 1;
}
.deal-person {
    /deep/ .first-level,
    /deep/ .second-level {
        width: calc(50% - 8px);
        margin-right: 8px;
        .bk-form-width {
            width: 100%;
        }
    }
}
.setion-title {
    margin-top: 30px;
    margin-bottom: 0;
    padding-bottom: 10px;
    color: #63656e;
    font-size: 14px;
    line-height: 20px;
    border-bottom: 1px solid #cacedb;
    font-weight: 700;
    .setion-title-icon {
        display: inline-block;
        vertical-align: middle;
        font-size: 24px;
        cursor: pointer;
    }
}
.half-width-item {
    width: calc(50% - 8px);
    display: inline-block;
    &:first-child {
        margin-right: 4px;
    }
}
</style>
