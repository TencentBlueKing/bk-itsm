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
  <div class="project-list-page">
    <i class="bk-icon icon-close-line-2 back-icon" @click="handleGoBack"></i>
    <div class="action-wrap">
      <bk-button
        v-cursor="{ active: !hasPermission(['project_create']) }"
        :class="[{
          'btn-permission-disable': !hasPermission(['project_create'])
        }]"
        theme="primary"
        @click="onCreateProject">
        {{ $t('m["新建"]') }}
      </bk-button>
      <bk-input
        right-icon="bk-icon icon-search"
        style="width: 530px;"
        :placeholder="$t(`m['请输入项目名称']`)"
        v-model="keyword"
        @enter="onSearchProject"
        @clear="onSearchProject">
      </bk-input>
    </div>
    <div class="project-table">
      <bk-table
        v-bkloading="{ isLoading: listLoading }"
        :data="list"
        :pagination="pagination"
        @sort-change="handleSortChange"
        @page-change="handlePageChange"
        @page-limit-change="handlePageLimitChange">
        <bk-table-column prop="name" :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m['项目名称']`)">
          <template slot-scope="props">
            <div class="name-wrap">
              <span
                class="prefix-icon"
                :style="{ background: props.row.color || '#90a1ff' }">
                {{ props.row.name[0].toUpperCase() }}
              </span>
              <span class="text">{{ props.row.name }}</span>
            </div>
          </template>
        </bk-table-column>
        <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" prop="key" :label="$t(`m['项目代号']`)"></bk-table-column>
        <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" prop="desc" :label="$t(`m['项目说明']`)">
          <template slot-scope="props">
            {{ props.row.desc || '--' }}
          </template>
        </bk-table-column>
        <bk-table-column :show-overflow-tooltip="true" prop="creator" :label="$t(`m['创建人']`)"></bk-table-column>
        <bk-table-column :show-overflow-tooltip="true" :sortable="true" prop="create_at" :label="$t(`m['创建时间']`)"></bk-table-column>
        <bk-table-column :label="$t(`m['操作']`)" fixed="right">
          <template slot-scope="props">
            <bk-button
              v-cursor="{ active: !hasPermission(['project_edit'], props.row.auth_actions) }"
              text
              theme="primary"
              :class="{
                'btn-permission-disable': !hasPermission(['project_edit'], props.row.auth_actions) }"
              @click="onEditProject(props)">
              {{ $t(`m['编辑']`) }}
            </bk-button>
            <div
              :style="{ display: 'inline-block' }"
              v-bk-tooltips.right="$t(`m['该项目不允许删除']`)">
              <!-- 删除按钮暂时禁用 -->
              <bk-button
                v-cursor="{ active: !hasPermission(['project_edit'], props.row.auth_actions) }"
                text
                theme="primary"
                :disabled="true"
                :class="{
                  'btn-permission-disable': !hasPermission(['project_edit'], props.row.auth_actions)
                }"
                @click="onDeleteProject(props.row)">
                {{ $t(`m['删除']`) }}
              </bk-button>
            </div>
          </template>
        </bk-table-column>
        <div class="empty" slot="empty">
          <empty
            :is-error="listError"
            :is-search="searchToggle"
            @onRefresh="getProjectList()"
            @onClearSearch="onClearSearch()">
          </empty>
        </div>
      </bk-table>
    </div>
    <edit-project-dialog
      :title="editDialogTitle"
      :is-show="isEditDialogShow"
      :project="projectForm"
      @confirm="onProjectDialogConfirm"
      @cancel="onProjectDialogCancel">
    </edit-project-dialog>
    <bk-dialog
      v-model="isDeleteDialogShow"
      header-position="center"
      render-directive="if"
      :title="$t(`m['确认删除项目？']`)"
      :width="400"
      :auto-close="false"
      :mask-close="false"
      :loading="deleteProjectPending"
      @confirm="onDeleteProjectConfirm"
      @cancel="editingProject = null">
      <div v-if="editingProject" class="delete-tips">
        {{$t(`m['确认删除']`)}}{{$t(`m['“']`)}}{{editingProject.name}}{{$t(`m['”']`)}}{{$t(`m['，']`)}}{{$t(`m['一旦删除将不可回复，请谨慎操作。']`)}}
      </div>
    </bk-dialog>
  </div>
</template>
<script>
  import i18n from '@/i18n/index.js';
  import { errorHandler } from '@/utils/errorHandler.js';
  import permission from '@/mixins/permission.js';
  import EditProjectDialog from './editProjectDialog.vue';
  import Empty from '../../components/common/Empty.vue';

  export default {
    name: 'ProjectList',
    components: {
      EditProjectDialog,
      Empty,
    },
    mixins: [permission],
    data() {
      return {
        keyword: '',
        list: [],
        listLoading: false,
        ordering: undefined,
        editingProject: null,
        isEditDialogShow: false,
        isDeleteDialogShow: false,
        editProjectPending: false,
        deleteProjectPending: false,
        projectForm: {
          name: '',
          key: '',
          desc: '',
          color: '',
        },
        pagination: {
          current: 1,
          count: 0,
          limit: 10,
        },
        listError: false,
        searchToggle: false,
      };
    },
    computed: {
      editDialogTitle() {
        return this.editingProject ? i18n.t('m["编辑项目"]') : i18n.t('m["新建项目"]');
      },
    },
    created() {
      this.getProjectList();
    },
    beforeRouteEnter(to, from, next) {
      if (from.name) {
        window.previousRouter = from.fullPath;
      }
      next();
    },
    beforeRouteLeave(to, from, next) {
      window.previousRouter = null;
      next();
    },
    methods: {
      async getProjectList() {
        this.listLoading = true;
        this.listError = false;
        try {
          const { current, limit } = this.pagination;
          const params = {
            page_size: limit,
            page: current,
            ordering: this.ordering,
          };
          if (this.keyword !== '') {
            params.name__icontains = this.keyword;
            this.searchToggle = true;
          } else {
            this.searchToggle = false;
          }
          const res = await this.$store.dispatch('project/getProjectList', params);
          this.pagination.count = res.data.count;
          this.list = res.data.items;
        } catch (e) {
          this.listError = true;
          errorHandler(e, this);
        } finally {
          this.listLoading = false;
        }
      },
      getNameColor(index) {
        return ['#90a1ff', '#bb90ff', '#ffd990'][index];
      },
      onSearchProject() {
        this.pagination.current = 1;
        this.getProjectList();
      },
      onClearSearch() {
        this.keyword = '';
        this.searchToggle = false;
        this.getProjectList();
      },
      onCreateProject() {
        if (!this.hasPermission(['project_create'])) {
          this.applyForPermission(['project_create'], [], {});
          return;
        }
        this.isEditDialogShow = true;
        this.projectForm = {
          name: '',
          key: '',
          desc: '',
          color: this.getNameColor(this.pagination.count % 3),
        };
        this.editingProject = null;
      },
      onEditProject(props) {
        this.editingProject = props.row;
        if (!this.hasPermission(['project_edit'], this.editingProject.auth_actions)) {
          const resourceData = {
            project: [{
              id: this.editingProject.key,
              name: this.editingProject.name,
            }],
          };
          this.applyForPermission(['project_edit'], this.editingProject.auth_actions, resourceData);
          return false;
        }
        this.projectForm = Object.assign({}, props.row);
        if (!this.projectForm.color) {
          this.projectForm.color = this.getNameColor(props.$index % 3);
        }
        this.isEditDialogShow = true;
      },
      onProjectDialogConfirm() {
        this.isEditDialogShow = false;
        this.getProjectList();
      },
      onProjectDialogCancel() {
        this.isEditDialogShow = false;
      },
      // onEditProjectConfirm () {
      //     this.$refs.projectForm.validate().then(async (result) => {
      //         if (result) {
      //             this.editProjectPending = true
      //             const url = this.editingProject ? 'project/updateProject' : 'project/createProject'
      //             try {
      //                 await this.$store.dispatch(url, this.projectForm)
      //                 this.editingProject = null
      //                 this.isEditDialogShow = false
      //                 this.getProjectList()
      //             } catch (e) {
      //                 errorHandler(e, this)
      //             } finally {
      //                 this.editProjectPending = false
      //             }
      //         }
      //     })
      // },
      onDeleteProject(project) {
        if (!this.hasPermission(['project_edit'], project.auth_actions)) {
          const resourceData = {
            project: [{
              id: project.key,
              name: project.name,
            }],
          };
          this.applyForPermission(['project_edit'], project.auth_actions, resourceData);
          return false;
        }
        this.editingProject = project;
        this.isDeleteDialogShow = true;
      },
      async onDeleteProjectConfirm() {
        this.deleteProjectPending = true;
        try {
          await this.$store.dispatch('project/deleteProject', this.editingProject.key);
          this.editingProject = null;
          this.isDeleteDialogShow = false;
          if (this.list.length === 1) {
            this.pagination.current = this.pagination.current === 1 ? 1 : this.pagination.current - 1;
          }
          this.getProjectList();
        } catch (e) {
          errorHandler(e, this);
        } finally {
          this.deleteProjectPending = false;
        }
      },
      handleSortChange(data) {
        if (data.order === 'ascending') {
          this.ordering = data.prop;
        } else if (data.order === 'descending') {
          this.ordering = data.prop;
        } else {
          this.ordering = undefined;
        }
        this.getProjectList();
      },
      handlePageChange(page) {
        this.pagination.current = page;
        this.getProjectList();
      },
      handlePageLimitChange(limit) {
        this.pagination.limit = limit;
        this.pagination.current = 1;
        this.getProjectList();
      },
      handleGoBack() {
        if (window.previousRouter) {
          this.$router.push(window.previousRouter);
        } else {
          this.$router.push({ name: 'Home' });
        }
      },
    },
  };
</script>
<style lang="scss" scoped>
    .project-list-page {
        position: relative;
        padding: 60px 0 30px;
        width: 1256px;
        margin: 0 auto;
        .back-icon {
            position: absolute;
            top: 20px;
            right: 0;
            font-size: 24px;
            color: #979ba5;
            cursor: pointer;
            &:hover {
                color: #3a84ff;
            }
        }
        .action-wrap {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
        }
        .project-table {
            /deep/.bk-link .bk-link-text {
                font-size: 12px;
                line-height: 1;
            }
        }
        .name-wrap {
            display: flex;
            align-items: center;
            .prefix-icon {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                margin-right: 8px;
                width: 20px;
                height: 20px;
                border-radius: 50%;
                color: #ffffff;
                font-size: 12px;
            }
        }
    }
</style>
