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
  <div class="bk-deal-person" :class="{
    'person-vertical': formType === 'vertical',
    'inline-auto-width': formType === 'inline-auto-width',
    'no-second': noSecondTypeList.includes(formData.levelOne)
  }">
    <div class="first-level">
      <!-- 一级处理人 -->
      <bk-select :ext-cls="'bk-form-width mr10'"
        data-test-id="dealPerson-select-firstHandler"
        v-model="formData.levelOne"
        :loading="initLoaing"
        :clearable="false"
        searchable
        :font-size="'medium'"
        @selected="onFirstLevelChange">
        <bk-option v-for="option in firstLevelList"
          :data-test-id="`dealPerson-select-first-${option.id}`"
          :key="option.id"
          :id="option.id"
          :name="option.name">
        </bk-option>
      </bk-select>
    </div>
    <!-- 二级处理人 -->
    <div class="second-level" v-if="['PERSON', 'GENERAL', 'CMDB', 'IAM', 'API', 'ASSIGN_LEADER', 'VARIABLE', 'ORGANIZATION'].includes(formData.levelOne)">
      <!-- 个人 -->
      <template v-if="formData.levelOne === 'PERSON' && Array.isArray(formData.levelSecond)">
        <member-select data-test-id="dealPerson-select-personSecondHandler" :ext-cls="'bk-form-width'"
          v-model="formData.levelSecond" :specify-id-list="targetSpecifyIdList">
        </member-select>
      </template>
      <!-- 通用角色表|CMDB|权限中心|第三方系统|指定节点处理人上级|引用变量 -->
      <template v-else-if="['GENERAL', 'CMDB', 'IAM', 'API', 'ASSIGN_LEADER', 'VARIABLE'].includes(formData.levelOne)">
        <bk-select :ext-cls="'bk-form-width'"
          data-test-id="dealPerson-select-secondHandler"
          v-model="formData.levelSecond"
          :loading="isLoading"
          show-select-all
          :multiple="!['ASSIGN_LEADER'].includes(formData.levelOne)"
          searchable
          :font-size="'medium'">
          <bk-option v-for="option in secondLevelList"
            :data-test-id="`dealPerson-select-second-${option.id}`"
            :key="option.id"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
      </template>
      <!-- 组织架构 -->
      <template v-else-if="formData.levelOne === 'ORGANIZATION'">
        <bkTree
          v-model="formData.levelSecond"
          :list="organizationList"
          :organization-loading="organizationLoading"
          ext-cls="bk-form-width"
          @toggle="toggleInfo">
        </bkTree>
      </template>
    </div>
    <p class="bk-error-info" v-if="showError">{{ requiredMsg || $t(`m.treeinfo['处理人不能为空']`) }}</p>
    <bk-dialog v-model="organizationTip.show"
      theme="primary"
      footer-position="center"
      :mask-close="false"
      @cancel="cancelSelect">
      <i class="bk-itsm-icon icon-itsm-icon-mark-eight organization-tip"></i>
      <p>
        <span>{{$t('m["当前组织架构下共有员工"]')}}</span>
        <span style="color:red">{{organizationTip.count}}</span>
        <span>{{$t('m["人，如果开启了消息通知，会导致"]')}}</span>
        <span style="color:red">{{organizationTip.count}}</span>
        <span>{{$t('m["人都会收到单据代办通知，是否继续？如有疑问请咨询ITSM系统管理员。"]')}}</span>
      </p>
    </bk-dialog>
  </div>
</template>
<script>
  import memberSelect from '../../../../commonComponent/memberSelect';
  import bkTree from '../../../../../components/form/bkTree/index.vue';
  import { errorHandler } from '../../../../../utils/errorHandler.js';
  import { isEmpty } from '../../../../../utils/util';

  export default {
    name: 'dealPerson',
    components: {
      bkTree,
      memberSelect,
    },
    props: {
      value: {
        type: Object,
        default: () => ({
          type: '',
          value: [],
        }),
      },
      // 指定人员 id 范围
      specifyIdList: {
        type: Array,
        default: () => ([]),
      },
      excludeRoleTypeList: {
        type: Array,
        default: () => ([]),
      },
      showRoleTypeList: {
        type: Array,
        default: () => ([]),
      },
      nodeInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      formType: {
        type: String,
        default: '',
      },
      shortcut: {
        type: Boolean,
        default: false,
      },
      requiredMsg: {
        type: String,
        default: '',
      },
      // 展示组织架构超过100人提示dialog
      showOverbook: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        showError: false,
        initLoaing: false,
        isLoading: false,
        organizationLoading: false,
        formData: {
          levelOne: '',
          levelSecond: [],
        },
        allUserlist: [],
        firstLevelList: [],
        secondLevelList: [],
        organizationList: [],
        frontMemberField: [],
        secondLevelRange: {},
        noSecondTypeList: ['EMPTY', 'OPEN', 'STARTER', 'BY_ASSIGNOR', 'STARTER_LEADER'],
        organizationTip: {
          show: false,
          count: '',
        },
      };
    },
    computed: {
      targetSpecifyIdList() {
        const target = this.specifyIdList.find(rule => rule.type === this.formData.levelOne);
        return target ? target.list : [];
      },
    },
    watch: {
      value: {
        handler(newVal, oldVal) {
          if (JSON.stringify(newVal) !== JSON.stringify(oldVal)) {
            this.initData();
          }
        },
        deep: true,
      },
      showRoleTypeList: {
        handler() {
          this.initData();
        },
        deep: true,
      },
      excludeRoleTypeList: {
        handler() {
          this.initData();
        },
        deep: true,
      },
    },
    created() {
      // 初始化默认值
      this.setDeaultSecondLeve(this.value.type);
    },
    async mounted() {
      this.initData();
    },
    methods: {
      toggleInfo(item) {
        if (!this.nodeInfo.is_builtin && this.showOverbook) this.getOrganizationNumber(item.id);
      },
      async initData() {
        this.initLoaing = true;
        await this.getRoleGroup();

        // 传入的 type 在过滤后的列表中，才赋值
        const roleType = this.value.type;
        if (this.firstLevelList.find(m => m.id === roleType)) {
          const defaultSecondValue = roleType === 'ORGANIZATION' || roleType === 'ASSIGN_LEADER'
            ? (this.value.value)
            : (this.value.value ? this.value.value.split(',').filter(val => val !== '') : []);
          this.formData = {
            levelOne: roleType,
            levelSecond: defaultSecondValue,
          };
        }
        if (roleType) {
          this.getSecondLevelList(roleType);
        }
        this.initLoaing = false;
      },
      // 获取人员分组列表
      getRoleGroup() {
        if (this.allUserlist.length) {
          this.getFirstLevelList(this.allUserlist);
          return;
        }
        return this.$store.dispatch('deployCommon/getUser', {
          is_processor: true,
          project_key: this.$store.state.project.id,
        }).then((res) => {
          this.allUserlist = res.data;
          this.getFirstLevelList(res.data);
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      getFirstLevelList(data) {
        this.firstLevelList = data.filter((item) => {
          if (this.excludeRoleTypeList.length) {
            return !this.excludeRoleTypeList.includes(item.type);
          } if (this.showRoleTypeList.length) {
            return this.showRoleTypeList.includes(item.type);
          }
          return true;
        }).map(item => ({
          id: item.type,
          name: item.name,
        }));
      },
      setDeaultSecondLeve(type) {
        switch (type) {
          case 'ORGANIZATION':
          case 'ASSIGN_LEADER':
            this.formData.levelSecond = '';
            break;
          default:
            this.formData.levelSecond = [];
        }
        this.secondLevelList = [];
      },
      getSecondLevelList(type) {
        if (this.noSecondTypeList.includes(type)) {
          return;
        }
        if (type === 'ORGANIZATION') {
          this.getOrganization();
        } else if (type === 'ASSIGN_LEADER') {
          this.getPreStates();
        } else if (type === 'VARIABLE') {
          this.getFrontNodesList();
        } else {
          this.secondListFn(type);
        }
      },
      async getOrganizationNumber(id) {
        if (this.showOverbook) {
          const res = await this.$store.dispatch('common/getOrganizationNumber', id);
          // 单个组织超过100人时提醒
          if (res.data.count > 100) {
            this.organizationTip.count = res.data.count;
            this.organizationTip.show = true;
          }
        }
      },
      cancelSelect() {
        this.formData.levelOne = 'PERSON';
        this.formData.levelSecond = [];
      },
      async onFirstLevelChange(type) {
        // 清空二级数据
        this.$set(this.formData, 'levelSecond', []);
        this.setDeaultSecondLeve(type);
        this.getSecondLevelList(type);
      },
      // 获取数据
      secondListFn(type) {
        if (!type) {
          return;
        }
        const params = {
          role_type: type,
          project_key: this.$store.state.project.id || this.$route.query.project.id,
        };
        // 非后台管理页面需要加 shortcut 参数
        if (this.shortcut) {
          params.scope = 'shortcut';
        }
        this.isLoading = true;
        this.$store.dispatch('deployCommon/getSecondUser', params).then((res) => {
          let userList = [];
          userList = res.data.map((item) => {
            if (type === 'GENERAL') {
              // shortcut 下没有 count 参数
              const count = this.shortcut ? '' : `(${item.count})`;
              return {
                id: String(item.id),
                name: item.name + count,
                disabled: (item.count === 0),
              };
            } if (type === 'API') {
              return {
                id: item.role_key,
                name: item.name,
              };
            }
            return {
              id: String(item.id),
              name: item.name,
            };
          });
          // 显示指定选项
          if (this.targetSpecifyIdList.length && type !== 'GENERAL') {
            userList = userList.filter(m => this.targetSpecifyIdList.some(id => String(id) === m.id));
          }
          this.secondLevelList = userList;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isLoading = false;
          });
      },
      // 组织架构
      getOrganization() {
        this.organizationLoading = true;
        this.$store.dispatch('cdeploy/getTreeInfo').then((res) => {
          // 操作角色组织架构
          this.organizationList = res.data;
          this.organizationList.forEach(item => {
            this.$set(item, 'route', []);
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.organizationLoading = false;
          });
      },
      // 获取变量列表
      getFrontNodesList() {
        this.isLoading = true;
        const params = {
          workflow: this.nodeInfo.workflow,
          state: this.nodeInfo.id,
          exclude_self: true,
        };
        // 从前置节点信息中筛选 MEMBER 信息
        return this.$store.dispatch('apiRemote/get_related_fields', params).then((res) => {
          this.secondLevelList = res.data.filter(item => (item.type === 'MEMBERS' && item.validate_type === 'REQUIRE')
            || (item.type === 'MEMBER' && item.validate_type === 'REQUIRE')).map(item => ({ id: item.key, name: item.name }));
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isLoading = false;
          });
      },
      // 获取前置节点列表
      getPreStates() {
        this.isLoading = true;
        this.$store.dispatch('deployCommon/getPreStates', { id: this.nodeInfo.id }).then((res) => {
          // 排除分支节点和汇聚节点
          this.secondLevelList = res.data.filter(node => !['ROUTER-P', 'COVERAGE'].includes(node.type)).map(node => ({
            id: node.id,
            name: node.name,
          }));
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isLoading = false;
          });
      },
      // 校验 value
      verifyValue() {
        let error = false;
        if (this.formData.levelOne && !this.noSecondTypeList.includes(this.formData.levelOne)) {
          error = isEmpty(this.formData.levelOne) || isEmpty(this.formData.levelSecond);
        } else {
          error = isEmpty(this.formData.levelOne);
        }
        this.showError = error;
        return !error;
      },
      // 获取 value
      getValue() {
        let value = this.formData.levelSecond;
        // 保存数据时，数组需要变成字符串
        if (Array.isArray(this.formData.levelSecond)) {
          value = value.join(',');
        }
        return {
          value: value || '',
          type: this.formData.levelOne,
        };
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../../../scss/mixins/clearfix.scss';
    .organization-tip {
      width: 40px;
      height: 40px;
      background-color: #ff9c01;
      display: block;
      margin: 0px auto 10px;
      border-radius: 50%;
      line-height: 40px;
      &::before {
        font-size: 40px;
        color: #ffe8c3;
      }
    }
    .bk-form-width {
        float: left;
        width: 330px;
    }
    .bk-error-info {
        clear: both;
        color: #ff5656;
        font-size: 12px;
        line-height: 30px;
    }
    .bk-deal-person {
        line-height: normal;
        @include clearfix;
    }
    .first-level, .second-level {
        float: left;
        height: 32px;
        margin-top: 10px;

    }
    .person-vertical {
        .first-level, .second-level {
            display: block;
            float: none;
            height: 32px;
        }
        .second-level {
            margin-top: 20px;
        }
    }
    .inline-auto-width {
        display: flex;
        &.no-second  /deep/ {
            .second-level {
                display: none;
            }
            .margin-right {
                margin-right: 0;
            }
        }
        .first-level {
            margin-right: 8px;

        }
        .first-level, .second-level {
            flex: 1;
            .bk-form-width {
                width: 100%;
                margin-right: 24px;
            }
        }
    }
</style>
