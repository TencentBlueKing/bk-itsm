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
  <div class="bk-itsm-service">
    <div class="is-title" :class="{ 'bk-title-left': !sliderStatus }">
      <p class="bk-come-back">
        {{ $t('m["自定义角色组"]') }}
      </p>
    </div>
    <div class="itsm-page-content">
      <empty-tip
        v-if="!isDataLoading && tableList.length === 0 && searchToggle"
        :title="emptyTip.title"
        :sub-title="emptyTip.subTitle"
        :desc="emptyTip.desc"
        :links="emptyTip.links">
        <template slot="btns">
          <bk-button theme="primary"
            data-test-id="userGroup_button_create_permission"
            v-cursor="{ active: !hasPermission(['user_group_create'], $store.state.project.projectAuthActions) }"
            :class="{
              'btn-permission-disable': !hasPermission(['user_group_create'], $store.state.project.projectAuthActions)
            }"
            @click="showEditor({
              name: '',
              staffInputValue: [],
              ownersInputValue: []
            }, 'new')">
            {{ $t(`m['立即创建']`) }}
          </bk-button>
        </template>
      </empty-tip>
      <template v-else>
        <div class="bk-only-btn">
          <bk-button theme="primary"
            data-test-id="userGroup_button_create"
            v-cursor="{ active: !hasPermission(['user_group_create'], $store.state.project.projectAuthActions) }"
            icon="plus"
            :title="$t(`m.deployPage['新增']`)"
            :class="['mr10', 'plus-cus', {
              'btn-permission-disable': !hasPermission(['user_group_create'], $store.state.project.projectAuthActions)
            }]"
            @click="showEditor({
              name: '',
              staffInputValue: [],
              ownersInputValue: []
            }, 'new')">
            {{ $t(`m.deployPage['新增']`) }}
          </bk-button>
          <div class="bk-only-search">
            <bk-input
              data-test-id="userGroup_input_search"
              :placeholder="$t(`m.systemConfig['请输入角色名称']`)"
              :clearable="true"
              :right-icon="'bk-icon icon-search'"
              v-model="searchName"
              @enter="getList(1)"
              @clear="getList(1)">
            </bk-input>
          </div>
        </div>
        <bk-table
          v-bkloading="{ isLoading: isDataLoading }"
          :data="tableList"
          :size="'small'">
          <!--<bk-table-column type="index" label="NO." align="center" width="60"></bk-table-column>-->
          <bk-table-column :label="$t(`m.common['ID']`)" min-width="60">
            <template slot-scope="props">
              <span :title="props.row.id">{{ props.row.id || '--' }}</span>
            </template>
          </bk-table-column>

          <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m['角色组名']`)" width="200">
            <template slot-scope="props">
              <span :title="props.row.name">{{ props.row.name || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.user['人员']`)">
            <template slot-scope="props">
              <span :title="props.row.members">{{props.row.members}}</span>
            </template>
          </bk-table-column>
          <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.common['创建人']`)">
            <template slot-scope="props">
              <span :title="props.row.creator">{{props.row.creator || '--'}}</span>
            </template>
          </bk-table-column>
          <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.common['负责人']`)">
            <template slot-scope="props">
              <span :title="props.row.owners">{{props.row.owners || '--'}}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.user['操作']`)" width="150" fixed="right">
            <template slot-scope="props">
              <bk-button
                data-test-id="userGroup_button_edit"
                v-cursor="{ active: !hasPermission(['user_group_edit'], [...props.row.auth_actions, ...$store.state.project.projectAuthActions]) }"
                theme="primary"
                text
                :class="[{
                  'btn-permission-disable': !hasPermission(['user_group_edit'], [...props.row.auth_actions, ...$store.state.project.projectAuthActions])
                }]"
                @click="showEditor(props.row, 'edit')">
                {{ $t('m.user["编辑"]') }}
              </bk-button>
              <bk-button
                v-if="!props.row.is_builtin"
                data-test-id="userGroup_button_delete"
                v-cursor="{ active: !hasPermission(['user_group_delete'], [...props.row.auth_actions, ...$store.state.project.projectAuthActions]) }"
                theme="primary"
                text
                :class="[{
                  'btn-permission-disable': !hasPermission(['user_group_delete'], [...props.row.auth_actions, ...$store.state.project.projectAuthActions])
                }]"
                @click="deleteUser(props.row)">
                {{ $t('m.user["删除"]') }}
              </bk-button>
            </template>
          </bk-table-column>
          <div class="empty" slot="empty">
            <empty
              :is-error="listError"
              :is-search="!searchToggle"
              @onRefresh="getList()"
              @onClearSearch="getList(1)">
            </empty>
          </div>
        </bk-table>
      </template>
    </div>
    <!-- 编辑列表 -->
    <bk-dialog
      data-test-id="userGroup_dialog_editAndCreate"
      v-model="openDialog.isShow"
      :render-directive="'if'"
      :width="openDialog.width"
      :header-position="openDialog.headerPosition"
      :loading="secondClick"
      :auto-close="openDialog.autoClose"
      :mask-close="openDialog.autoClose"
      @confirm="submitUser">
      <p slot="header">{{ itemContent.id ? $t('m["修改自定义角色组"]') : $t('m["新增自定义角色组"]') }}</p>
      <div class="bk-add-project bk-add-module">
        <bk-form
          :label-width="200"
          form-type="vertical"
          :rules="rules"
          :model="formData"
          ref="dynamicForm">
          <bk-form-item
            data-test-id="role-input-roleName"
            :label="$t(`m['角色组名：']`)"
            :required="true"
            :property="'name'">
            <bk-input v-model.trim="formData.name" maxlength="120"></bk-input>
          </bk-form-item>
          <bk-form-item
            data-test-id="role-input-staffList"
            :label="$t(`m.user['人员名单：']`)"
            :required="true">
            <member-select v-model="formData.staffInputValue"></member-select>
          </bk-form-item>
          <bk-form-item :label="$t(`m.user['负责人：']`)">
            <member-select v-model="formData.ownersInputValue"></member-select>
          </bk-form-item>
        </bk-form>
      </div>
    </bk-dialog>
  </div>
</template>
<script>
  import memberSelect from '../commonComponent/memberSelect';
  import permission from '@/mixins/permission.js';
  import { errorHandler } from '../../utils/errorHandler';
  import EmptyTip from '../project/components/emptyTip.vue';
  import Empty from '../../components/common/Empty.vue';

  export default {
    components: {
      memberSelect,
      EmptyTip,
      Empty,
    },
    mixins: [permission],
    data() {
      return {
        // 二次点击
        secondClick: false,
        isDataLoading: false,
        tableList: [],
        // 编辑列表
        openDialog: {
          isShow: false,
          width: 700,
          headerPosition: 'left',
          autoClose: false,
        },
        // 校验规则
        rules: {
          name: [
            {
              required: true,
              message: this.$t('m.systemConfig["格式为长度小于120"]'),
              trigger: 'blur',
            },
            {
              max: 120,
              message: this.$t('m.systemConfig["格式为长度小于120"]'),
              trigger: 'blur',
            },
          ],
        },
        formData: {
          name: '',
          staffInputValue: [],
          ownersInputValue: [],
        },
        itemContent: {},
        searchName: '',
        searchToggle: false,
        listError: false,
        emptyTip: {
          title: this.$t('m[\'当前项目下还没有 <用户组>\']'),
          subTitle: this.$t('m[\'同一个职能团队可能会出现在多个不同的服务处理流程中，为了达到人员配置的一致性管理目的，你只需将对应的人员设置到同一个<用户组>中即可，这样便可以在不同的服务中配置引用它。\']'),
          desc: [
            {
              src: require('../../images/illustration/setting-group.svg'),
              title: this.$t('m[\'配置用户组的名称和成员\']'),
              content: this.$t('m[\'你只需要为其设计一个合理的名称（如：行政仓库管理员、IT技术人员、等等...），并将相应的成员加入到该用户组中即可。\']'),
            },
            {
              src: require('../../images/illustration/use-group.svg'),
              title: this.$t('m[\'在服务流程配置中使用它\']'),
              content: this.$t('m[\'服务的处理流程节点中，你可以在处理人、关注人等跟人员属性有关的字段中使用<用户组>；这种“引用”的逻辑，可以达到在一个地方编辑，所有引用方同时更新的效果，提升配置管理的效率。\']'),
            },
          ],
          links: [
            {
              text: this.$t('m[\'快速入门如何配置一个用户组\']'),
              btn: this.$t('m[\'产品白皮书\']'),
              href: 'https://bk.tencent.com/docs/document/6.0/145/6592',
            },
          ],
        },
      };
    },
    computed: {
      sliderStatus() {
        return this.$store.state.common.slideStatus;
      },
    },
    mounted() {
      this.getList();
    },
    methods: {
      getList(isSearch) {
        this.isDataLoading = true;
        const params = {
          role_type: 'GENERAL',
          name__icontains: this.searchName,
          project_key: this.$store.state.project.id,
        };
        if (isSearch) this.searchName = '';
        this.listError = false;
        this.$store.dispatch('user/getRoleList', params).then((res) => {
          this.tableList = res.data;
          this.searchToggle = res.data.length !== 0;
          this.tableList.forEach((item) => {
            this.$set(item, 'staffInputValue', item.members ? item.members.split(',') : []);
            this.$set(item, 'ownersInputValue', item.owners ? item.owners.split(',') : []);
          });
        })
          .catch((res) => {
            this.listError = true;
            errorHandler(res, this);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
      },
      // 保存修改，新增
      submitUser() {
        this.$refs.dynamicForm.validate().then(() => {
          if (this.formData.staffInputValue.length === 0) {
            this.$bkMessage({
              message: this.$t('m.user["人员不能为空！"]'),
              theme: 'warning',
            });
            return;
          }
          if (this.secondClick) {
            return;
          }
          this.secondClick = true;
          if (this.itemContent.id) {
            this.updateUser();
          } else {
            this.addUser();
          }
        });
      },
      // 新增
      addUser() {
        const params = {
          members: '',
          name: this.formData.name,
          role_type: 'GENERAL',
          project_key: this.$store.state.project.id,
        };
        params.members = this.formData.staffInputValue.join(',');
        params.owners = this.formData.ownersInputValue.join(',');
        this.$store.dispatch('user/submit', params).then(() => {
          this.$bkMessage({
            message: this.$t('m.user[\'新增成功\']'),
            theme: 'success',
          });
          this.openDialog.isShow = false;
          this.getList();
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.secondClick = false;
          });
      },
      // 更新
      updateUser() {
        const params = {
          id: this.itemContent.id,
          role_key: this.itemContent.role_key,
          members: '',
          name: this.formData.name,
          role_type: 'GENERAL',
          project_key: this.$store.state.project.id,
        };
        params.members = this.formData.staffInputValue.join(',');
        params.owners = this.formData.ownersInputValue.join(',');
        this.$store.dispatch('user/update', params).then(() => {
          this.$bkMessage({
            message: this.$t('m.user[\'保存成功\']'),
            theme: 'success',
          });
          this.openDialog.isShow = false;
          this.getList();
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.secondClick = false;
          });
      },
      // 编辑
      showEditor(item, type) {
        // 编辑权限校验
        const authAction = type === 'new' ? 'user_group_create' : 'user_group_edit';
        const curPermissions = type === 'new' ? this.$store.state.project.projectAuthActions : [...this.$store.state.project.projectAuthActions, ...item.auth_actions];
        if (!this.hasPermission([authAction], curPermissions || [])) {
          let resourceData = {};
          const { projectInfo } = this.$store.state.project;
          if (authAction === 'user_group_create') {
            resourceData = {
              project: [{
                id: projectInfo.key,
                name: projectInfo.name,
              }],
            };
          } else {
            resourceData = {
              project: [{
                id: projectInfo.key,
                name: projectInfo.name,
              }],
              user_group: [{
                id: item.id,
                name: item.name,
              }],
            };
          }
          this.applyForPermission([authAction], curPermissions, resourceData);
          return false;
        }
        this.openDialog.isShow = true;
        this.formData.name = item.name;
        this.formData.staffInputValue = item.staffInputValue;
        this.formData.ownersInputValue = item.ownersInputValue;
        this.itemContent = item;
      },
      // 删除
      deleteUser(item) {
        // 删除权限校验
        if (!this.hasPermission(['user_group_delete'], [...this.$store.state.project.projectAuthActions, ...item.auth_actions])) {
          const { projectInfo } = this.$store.state.project;
          const resourceData = {
            project: [{
              id: projectInfo.key,
              name: projectInfo.name,
            }],
            user_group: [{
              id: item.id,
              name: item.name,
            }],
          };
          this.applyForPermission(['user_group_delete'], [...this.$store.state.project.projectAuthActions, ...item.auth_actions], resourceData);
          return false;
        }
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.user["确认要删除此角色？"]'),
          confirmFn: () => {
            const { id } = item;
            if (this.secondClick) {
              return;
            }
            this.secondClick = true;
            this.$store.dispatch('user/delete', id).then(() => {
              this.$bkMessage({
                message: this.$t('m.user["删除成功"]'),
                theme: 'success',
              });
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.secondClick = false;
                this.getList();
              });
          },
        });
      },
      // 人员选择器赋值
      handleChange(name, value) {
        this.formData.staffInputValue = value;
      },
    },
  };
</script>
