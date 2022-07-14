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
  <div class="bk-deal-person">
    <!-- 一级处理人 -->
    <div class="bk-form-width">
      <bk-select v-model="formData.levelOne"
        :clearable="false"
        searchable
        @selected="getSecondLevelList">
        <bk-option v-for="option in firstLevelList"
          :key="option.typeName"
          :id="option.typeName"
          :name="option.name">
        </bk-option>
      </bk-select>
    </div>
    <!-- 二级处理人 -->
    <template v-if="formData.levelOne !== 'ORGANIZATION'">
      <div class="bk-form-width" v-if="formData.levelOne === 'VARIABLE'">
        <bk-select v-model="formData.levelSecond"
          :loading="isLoading"
          show-select-all
          multiple
          searchable>
          <bk-option v-for="option in frontMemberField"
            :key="option.id"
            :id="option.key"
            :name="option.name">
          </bk-option>
        </bk-select>
      </div>
      <div class="bk-form-width" v-else-if="formData.levelOne === 'PERSON'">
        <member-select v-model="formData.levelSecond">
        </member-select>
      </div>
      <div class="bk-form-width" v-else-if="formData.levelOne === 'CMDB'">
        <bk-select v-model="formData.levelSecond"
          :loading="isLoading"
          show-select-all
          searchable>
          <bk-option v-for="option in secondLevelList"
            :key="option.id"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
      </div>
      <div class="bk-form-width" v-else-if="formData.levelOne === 'GENERAL'">
        <bk-select v-model="formData.levelSecond"
          :loading="isLoading"
          searchable>
          <bk-option v-for="option in secondLevelList"
            :key="option.id"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
      </div>
    </template>
    <!-- 组织架构 -->
    <div class="bk-form-width" v-if="formData.levelOne === 'ORGANIZATION'">
      <select-tree
        v-model="formData.levelSecond"
        :list="organizationList">
      </select-tree>
    </div>
  </div>
</template>
<script>
  import memberSelect from '../../commonComponent/memberSelect';
  import SelectTree from '../../../components/form/selectTree/index.vue';
  import { errorHandler } from '../../../utils/util.js';

  export default {
    name: 'dealPerson',
    components: {
      SelectTree,
      memberSelect,
    },
    props: {
      firstLevelList: {
        type: Array,
        default() {
          return [];
        },
      },
      checkValue: {
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
      keyType: {
        type: String,
        default() {
          return '';
        },
      },
    },
    data() {
      return {
        isLoading: false,
        formData: {
          levelOne: 'ORGANIZATION',
          levelSecond: [],
        },
        secondLevelList: [],
        organizationList: [],
        frontMemberField: [],
      };
    },
    mounted() {
      this.initData();
      if (this.nodeInfo.id) {
        this.getFrontNodesList();
      }
    },
    methods: {
      initData() {
        this.formData.levelOne = this.checkValue.type;
        // 处理人（不是提单节点去掉OPEN的默认值）
        if (!this.nodeInfo.is_builtin && this.nodeInfo.processors_type === 'OPEN' && this.keyType === 'processors') {
          this.formData.levelOne = '';
        }
        // 初始化数据的时候区分
        if (this.formData.levelOne === 'ORGANIZATION') {
          this.formData.levelSecond = this.checkValue.value;
          this.getOrganization();
        } else {
          this.getSecondLevelList(this.formData.levelOne);
          if (this.formData.levelOne === 'GENERAL') {
            this.formData.levelSecond = this.checkValue.value || '';
          } else {
            this.formData.levelSecond = this.checkValue.value ? this.checkValue.value.split(',') : [];
          }
        }
      },
      getSecondLevelList(value) {
        // 清空二级数据
        this.formData.levelSecond = [];
        this.secondLevelList = [];
        if (value === 'ORGANIZATION') {
          this.formData.levelSecond = '';
          this.getOrganization();
        } else if (value === 'PERSON') {
          this.secondLevelList = [];
        } else if (value === 'GENERAL') {
          this.formData.levelSecond = '';
          this.secondListFn(value);
        } else {
          this.secondListFn(value);
        }
      },
      // 获取数据
      secondListFn(value) {
        if (!value) {
          return;
        }
        this.isLoading = true;
        this.$store.dispatch('deployCommon/getSecondUser', {
          role_type: value,
          scope: 'shortcut',
          project_key: this.$store.state.project.id,
        }).then((res) => {
          const valueList = res.data;
          const userList = [];
          if (value === 'GENERAL') {
            valueList.forEach((item) => {
              userList.push({
                id: String(item.id),
                name: `${item.name}(${item.count})`,
                disabled: (item.count === 0),
              });
            });
          } else {
            valueList.forEach((item) => {
              userList.push({
                id: String(item.id),
                name: item.name,
              });
            });
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
        this.$store.dispatch('cdeploy/getTreeInfo').then((res) => {
          // 操作角色组织架构
          this.organizationList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 获取前置节点的字段信息
      getFrontNodesList() {
        const params = {
          workflow: this.nodeInfo.workflow,
          state: this.nodeInfo.id,
          exclude_self: true,
        };
        this.$store.dispatch('apiRemote/get_related_fields', params).then((res) => {
          this.frontMemberField = res.data.filter(item => (item.type === 'MEMBERS' && item.validate_type === 'REQUIRE') || (item.type === 'MEMBER' && item.validate_type === 'REQUIRE'));
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../scss/mixins/clearfix.scss';

    .bk-form-width {
        float: left;
        width: 50%;
        padding-right: 10px;
    }
    .bk-deal-person {
        line-height: normal;
        @include clearfix;
    }
</style>
