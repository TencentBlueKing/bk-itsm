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
  <div class="bk-add-entry">
    <bk-form
      :label-width="200"
      form-type="vertical"
      :model="directory.formInfo"
      :rules="rules"
      ref="dynamicForm">
      <bk-form-item
        :label="$t(`m.serviceConfig['服务名称']`)"
        :required="true"
        :property="'name'">
        <bk-input v-model.trim="directory.formInfo.name"
          maxlength="120"
          :placeholder="$t(`m.serviceConfig['请输入服务名称']`)">
        </bk-input>
      </bk-form-item>
      <bk-form-item
        :label="$t(`m.serviceConfig['关联流程版本']`)"
        :required="true"
        :property="'workflow'">
        <bk-select v-model="directory.formInfo.workflow"
          :placeholder="directory.place.workflow"
          :clearable="false"
          searchable
          :font-size="'medium'">
          <bk-option v-for="option in flowList"
            :key="option.id"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item
        :label="$t(`m.serviceConfig['服务类型']`)"
        :required="true"
        :property="'key'">
        <bk-select v-model="directory.formInfo.key"
          :placeholder="directory.place.key"
          :clearable="false"
          searchable
          :font-size="'medium'">
          <bk-option v-for="option in codeList"
            :key="option.key"
            :id="option.key"
            :name="option.name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item v-if="openFunction.SLA_SWITCH"
        :label="$t(`m.serviceConfig['服务协议']`)">
        <bk-select v-model="directory.formInfo.sla"
          :placeholder="directory.place.sla"
          searchable
          :font-size="'medium'">
          <bk-option v-for="option in slaList"
            :key="option.id"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item
        :label="$t(`m.serviceConfig['可见范围']`)"
        :required="true">
        <deal-person
          class="display-range"
          ref="displayRange"
          :value="dealPersonValue"
          :show-role-type-list="displayRangeTypes">
        </deal-person>
      </bk-form-item>
      <bk-form-item
        :label="$t(`m.serviceConfig['代提单']`)">
        <bk-switcher v-model="directory.formInfo.can_ticket_agency" size="small"></bk-switcher>
      </bk-form-item>
      <bk-form-item
        :label="$t(`m.serviceConfig['服务描述']`)">
        <bk-input
          :placeholder="$t(`m.serviceConfig['请输入服务描述']`)"
          :type="'textarea'"
          :rows="3"
          :maxlength="100"
          v-model="directory.formInfo.desc">
        </bk-input>
      </bk-form-item>
      <bk-form-item
        :label="$t(`m.serviceConfig['服务负责人']`)"
        :required="true"
        :property="'admin'">
        <member-select v-model="directory.formInfo.admin"></member-select>
      </bk-form-item>
      <bk-form-item
        :label="$t(`m.serviceConfig['启用服务']`)">
        <bk-switcher v-model="directory.formInfo.is_valid" size="small"></bk-switcher>
      </bk-form-item>
      <template v-if="directory.formInfo.is_valid">
        <bk-form-item
          :label="$t(`m.serviceConfig['关联目录']`)">
          <select-tree
            v-model="directory.formInfo.catalog_id"
            :list="dirList"
            ext-cls="bk-form-width">
          </select-tree>
        </bk-form-item>
      </template>
    </bk-form>
    <div class="bk-add-btn">
      <bk-button :theme="'primary'" :title="$t(`m.serviceConfig['确认']`)" class="mr10" @click="submitAdd">
        {{$t(`m.serviceConfig['确认']`)}}
      </bk-button>
      <bk-button :theme="'default'" :title="$t(`m.serviceConfig['取消']`)" class="mr10" @click="closeAdd">
        {{$t(`m.serviceConfig['取消']`)}}
      </bk-button>
    </div>
  </div>
</template>

<script>
  import commonMix from '../commonMix/common.js';
  import memberSelect from '../commonComponent/memberSelect';
  import SelectTree from '../../components/form/selectTree';
  import DealPerson from '../processManagement/processDesign/nodeConfigue/components/dealPerson';
  import { errorHandler } from '../../utils/errorHandler.js';
  import { isEmpty } from '../../utils/util.js';

  export default {
    name: 'changeServiceEntry',
    components: {
      memberSelect,
      SelectTree,
      DealPerson,
    },
    mixins: [commonMix],
    props: {
      // 弹窗内容
      addDirectory: {
        type: Object,
        default() {
          return {};
        },
      },
      // 关联流程
      flowList: {
        type: Array,
        default() {
          return [];
        },
      },
      // 服务级别
      slaList: {
        type: Array,
        default() {
          return [];
        },
      },
      // 服务类型
      codeList: {
        type: Array,
        default() {
          return [];
        },
      },
    },
    data() {
      return {
        clickSecond: false,
        // 服务目录列表
        dirList: [],
        displayRangeTypes: ['OPEN', 'ORGANIZATION', 'GENERAL', 'API'],
        dealPersonValue: {
          type: '',
          value: '',
        },
        directory: {
          place: {
            workflow: this.$t('m.serviceConfig["请选择关联流程版本"]'),
            sla: this.$t('m.serviceConfig["请选择服务级别"]'),
            key: this.$t('m.serviceConfig["请选择服务类型"]'),
          },
          formInfo: {
            type: '',
            value: [],
          },
        },
        checkInfo: {
          // 服务名称
          name: false,
          // 关联流程
          workflow: false,
          // 服务级别
          sla: false,
          // 服务类型
          key: false,
          admin: false,
          displayRange: false,
        },
        // 校验规则
        rules: {},
      };
    },
    computed: {
      openFunction() {
        return this.$store.state.openFunction;
      },
    },
    created() {
      this.initData();
    },
    mounted() {
      // 关联服务
      this.getTreeInfo();
      // 校验规则
      this.rules.name = this.checkCommonRules('name').name;
      this.rules.workflow = this.checkCommonRules('select').select;
      this.rules.key = this.checkCommonRules('select').select;
      this.rules.admin = this.checkCommonRules('select').select;
    },
    methods: {
      // 切换可见范围人员类型
      changeProcessor(type) {
        if (type === 'GENERAL') {
          this.getGeneral();
        } else if (type === 'ORGANIZATION') {
          this.getOrganization();
        }
        this.directory.formInfo.display_role = [];
      },
      // 初始化数据
      initData() {
        const {
          name,
          workflow,
          sla,
          key,
          can_ticket_agency: canTicketAgency,
          desc,
          is_valid: isValid,
          display_type: displayType,
          display_role: displayRole,
          owners,
          catalog_id: catalogId,
        } = this.addDirectory.formInfo;
        this.directory.formInfo = {
          // 服务名称
          name: name || '',
          // 关联流程
          workflow: Number(workflow) || '',
          // 服务级别
          sla: sla || '',
          // 服务类型
          key: key || '',
          // 代提单
          can_ticket_agency: canTicketAgency || false,
          // 服务描述
          desc: desc || '',
          // 启用服务
          is_valid: !!isValid,
          // 角色类型
          display_type: displayType || 'OPEN',
          display_role: displayRole || '',
          // 负责人
          admin: owners ? owners.split(',') : [],
          owners: owners || '',
          // 服务目录
          catalog_id: isEmpty(catalogId) ? 0 : catalogId,
        };
        this.dealPersonValue = {
          type: displayType || 'OPEN',
          value: displayRole || '',
        };
      },
      // 校验数据
      checkForm() {
        this.checkInfo.name = this.directory.formInfo.name.length === 0 || this.directory.formInfo.name.length > 120;
        this.checkInfo.workflow = !this.directory.formInfo.workflow;
        this.checkInfo.key = !this.directory.formInfo.key;
        this.checkInfo.admin = this.directory.formInfo.admin.length === 0;
        if (this.$refs.displayRange && !this.$refs.displayRange.verifyValue()) {
          this.checkInfo.displayRange = true;
        }
        // 是否全部为 false
        const checkList = Object.keys(this.checkInfo).map(key => this.checkInfo[key]);
        return checkList.every(bool => bool === false);
      },
      // 保存
      submitAdd() {
        // 校验
        this.$refs.dynamicForm.validate().then(() => {

        }, () => {

        });
        if (!this.checkForm()) {
          return;
        }

        this.directory.formInfo.owners = this.directory.formInfo.admin.join(',');
        if (this.$refs.displayRange) {
          const data = this.$refs.displayRange.getValue();
          this.directory.formInfo.display_type = data.type;
          this.directory.formInfo.display_role = data.value;
        }
        if (['OPEN'].includes(this.directory.formInfo.display_type)) {
          delete this.directory.formInfo.display_role;
        }
        if (this.addDirectory.type === 'new') {
          this.addNewEntry();
        } else {
          this.changeEntry();
        }
      },
      // 关闭
      closeAdd() {
        this.$parent.$parent.toggleDialog();
      },
      // 添加服务
      addNewEntry() {
        // 关联服务
        const formInfo = JSON.parse(JSON.stringify(this.directory.formInfo));
        delete formInfo.admin;
        if (this.clickSecond) {
          return;
        }
        this.clickSecond = true;
        this.$store.dispatch('serviceEntry/createService', formInfo).then(() => {
          this.$bkMessage({
            message: this.$t('m.serviceConfig["添加成功"]'),
            theme: 'success',
          });
          this.$parent.$parent.toggleDialog();
          this.$parent.$parent.getList(1);
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.clickSecond = false;
          });
      },
      // 修改服务
      changeEntry() {
        this.directory.formInfo.id = this.addDirectory.id;
        if (this.clickSecond) {
          return;
        }
        this.clickSecond = true;
        const params = JSON.parse(JSON.stringify(this.directory.formInfo));
        this.$store.dispatch('serviceEntry/updateService', params).then(() => {
          this.$bkMessage({
            message: this.$t('m.serviceConfig["修改成功"]'),
            theme: 'success',
          });
          this.$parent.$parent.toggleDialog();
          this.$parent.$parent.getList();
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.clickSecond = false;
          });
      },
      // 关联目录树组件
      async getTreeInfo() {
        await this.$store.dispatch('serviceCatalog/getTreeData', {
          show_deleted: true, project_key: this.$store.state.project.id,
        }).then((res) => {
          this.dirList = (res.data[0] && res.data[0].children) ? res.data[0].children : res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
    },
  };
</script>
<style lang="scss" scoped>
.display-range {
    /deep/ .bk-form-width {
        width: 303px;
    }
}
.bk-error-info {
    color: #ff5656;
    font-size: 12px;
    line-height: 30px;
}
</style>
