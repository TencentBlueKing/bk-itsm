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
  <div class="bk-api-table">
    <div class="bk-api-button mb20">
      <p class="bk-api-title">{{ $t(`m.systemConfig["API列表"]`) }}</p>
      <div class="bk-api-button">
        <bk-dropdown-menu class="mr10 access-btn" @show="dropdownShow" @hide="dropdownHide" ref="apiDropdown" :disabled="disableImport">
          <div class="dropdown-trigger-btn" style="padding-left: 12px;" slot="dropdown-trigger">
            <span style="font-size: 14px;">{{ $t(`m.systemConfig['Api接入']`)}}</span>
            <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShow }]"></i>
          </div>
          <ul class="bk-dropdown-list" slot="dropdown-content">
            <li>
              <a href="javascript:;"
                v-cursor="{ active: !projectId && !hasPermission(['public_api_create']) }"
                :class="{ 'text-permission-disable': !projectId && !hasPermission(['public_api_create']) }"
                :title="$t(`m.systemConfig['接入']`)"
                data-test-id="api_a_apiTableAccessApi"
                @click="openShade('JOIN')">
                {{ $t(`m.systemConfig['接入']`) }}
              </a>
            </li>
            <li>
              <a href="javascript:;"
                data-test-id="api_a_apiTableCreateApi"
                v-cursor="{ active: !projectId && !hasPermission(['public_api_create']) }"
                :class="{ 'text-permission-disable': !projectId && !hasPermission(['public_api_create']) }"
                :title="$t(`m.systemConfig['新增']`)"
                @click="openShade('ADD')">
                {{$t(`m.systemConfig['新增']`)}}
              </a>
            </li>
          </ul>
        </bk-dropdown-menu>
        <bk-button :theme="'default'"
          data-test-id="api_button_apiTableuploadApi"
          :disabled="disableImport"
          v-cursor="{ active: !projectId && !hasPermission(['public_api_create']) }"
          :class="{ 'btn-permission-disable': !projectId && !hasPermission(['public_api_create']) }"
          :title="$t(`m.systemConfig['点击上传']`)"
          class="mr10 bk-btn-file">
          <input :disabled="disableImport" :type="!projectId && !hasPermission(['public_api_create']) ? 'button' : 'file'" :value="fileVal" class="bk-input-file" @change="handleFile" @click="hasImportPermission">
          {{$t(`m.systemConfig['导入']`)}}
        </bk-button>
        <bk-button :theme="'default'"
          data-test-id="api_button_apiTableBatchDeleteApi"
          class="mr10 batch-remove-btn"
          :title="$t(`m.systemConfig['批量移除']`)"
          :disabled="!checkList.length"
          @click="deleteCheck">
          {{$t(`m.systemConfig['批量移除']`)}}
        </bk-button>
        <bk-input class="bk-api-input"
          data-test-id="api_input_apiTableKeyword"
          v-model="searchInfo.key"
          :placeholder="$t(`m.systemConfig['请输入关键字']`)"
          :right-icon="'bk-icon icon-search'"
          :clearable="true"
          @clear="clearInfo"
          @enter="serchEntry">
        </bk-input>
      </div>
    </div>
    <bk-table
      v-bkloading="{ isLoading: isTableLoading }"
      :data="listInfo"
      :size="'small'"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handlePageLimitChange"
      @select-all="handleSelectAll"
      @select="handleSelect">
      <bk-table-column type="selection"
        width="60"
        align="center"
        :selectable="disabledFn">
      </bk-table-column>
      <!--<bk-table-column type="index" label="No." align="center" width="60"></bk-table-column>-->
      <bk-table-column :label="$t(`m.common['ID']`)" min-width="60">
        <template slot-scope="props">
          <span :title="props.row.id">{{ props.row.id || '--' }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.systemConfig['接口名称']`)" min-width="150">
        <template slot-scope="props">
          <!-- :disabled="props.row.is_builtin || !!props.row.count" -->
          <span class="bk-lable-primary"
            data-test-id="api_span_apiTableViewDetail"
            v-cursor="{ active: !projectId && !hasPermission(['public_api_manage'], props.row.auth_actions) }"
            :class="{ 'text-permission-disable': !projectId && !hasPermission(['public_api_manage'], props.row.auth_actions) }"
            :title="props.row.name"
            @click="entryOne(props.row)">
            {{props.row.name || '--'}}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.systemConfig['接口路径']`)" min-width="250">
        <template slot-scope="props">
          <span class="bk-table-type">{{props.row.method}}</span>
          <span :title="props.row.path">{{props.row.path || '--'}}</span>
        </template>
      </bk-table-column>
      <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.systemConfig['接口分类']`)" min-width="100">
        <template slot-scope="props">
          <span :title="systemName(props.row.remote_system)">
            {{systemName(props.row.remote_system) || '--'}}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.systemConfig['状态']`)" min-width="60">
        <template slot-scope="props">
          <span :title="props.row.is_activated ? $t(`m.systemConfig['启用']`) : $t(`m.systemConfig['关闭']`)">
            {{props.row.is_activated ? $t(`m.systemConfig['启用']`) : $t(`m.systemConfig['关闭']`)}}
          </span>
        </template>
      </bk-table-column>

      <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.common['负责人']`)">
        <template slot-scope="props">
          <span :title="props.row.owners">{{props.row.owners || '--'}}</span>
        </template>
      </bk-table-column>
      <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.common['创建人']`)">
        <template slot-scope="props">
          <span :title="props.row.creator">{{props.row.creator || '--'}}</span>
        </template>
      </bk-table-column>

      <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.systemConfig['接入数']`)" prop="count" width="80"></bk-table-column>
      <bk-table-column :show-overflow-tooltip="true" :label="$t(`m.systemConfig['操作']`)" width="150" fixed="right">
        <template slot-scope="props">
          <bk-button theme="primary" text
            data-test-id="api_button_apiTableExportApi"
            :title="$t(`m.systemConfig['导出']`)"
            :disabled="props.row.is_builtin"
            @click="exportFlow(props.row)">
            {{ $t('m.systemConfig["导出"]') }}
          </bk-button>
          <bk-button theme="primary" text
            data-test-id="api_button_apiTableEditApi"
            v-cursor="{ active: !projectId
              && !hasPermission(['public_api_manage'], props.row.auth_actions) }"
            :class="{ 'text-permission-disable': !projectId
              && !hasPermission(['public_api_manage'], props.row.auth_actions) }"
            :title="$t(`m.systemConfig['编辑']`)"
            :disabled="(projectId || hasPermission(['public_api_manage'], props.row.auth_actions))
              && (props.row.is_builtin || !!props.row.count)"
            @click="entryOne(props.row)">
            {{ $t('m.systemConfig["编辑"]') }}
          </bk-button>
          <bk-button theme="primary" text
            data-test-id="api_button_apiTableDeleteApi"
            v-cursor="{ active: !projectId
              && !hasPermission(['public_api_manage'], props.row.auth_actions) }"
            :class="{ 'text-permission-disable': !projectId
              && !hasPermission(['public_api_manage'], props.row.auth_actions) }"
            :title="$t(`m.systemConfig['移除']`)"
            :disabled="props.row.is_builtin"
            @click="openDelete(props.row)">
            {{ $t('m.systemConfig["移除"]') }}
          </bk-button>
        </template>
      </bk-table-column>
      <div class="empty" slot="empty">
        <empty
          status="500"
          :is-error="listError"
          :is-search="searchtoggle"
          @onRefresh="serchEntry()"
          @onClearSearch="clearInfo()">
        </empty>
      </div>
    </bk-table>
    <bk-sideslider
      :is-show.sync="entryInfo.show"
      :title="entryInfo.title"
      :width="entryInfo.width">
      <div slot="content" style="padding: 20px" v-if="entryInfo.show">
        <add-api-info
          :first-level-info="firstLevelInfo"
          :path-list="pathList"
          :tree-list="treeList"
          :type-info="typeInfo">
        </add-api-info>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import { errorHandler } from '../../../utils/errorHandler';
  import addApiInfo from './addApiInfo.vue';
  import permission from '@/mixins/permission.js';
  import Empty from '../../../components/common/Empty.vue';

  export default {
    components: {
      addApiInfo,
      Empty,
    },
    mixins: [permission],
    props: {
      treeList: {
        type: Array,
        default() {
          return [];
        },
      },
      listInfoOri: {
        type: Array,
        default() {
          return [];
        },
      },
      pathList: {
        type: Array,
        default() {
          return [];
        },
      },
      projectId: String,
      remoteSystem: [String, Number],
      firstLevelInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      customPaging: {
        type: Object,
        default() {
          return {};
        },
      },
      listError: Boolean,
    },
    data() {
      return {
        secondClick: false,
        isDropdownShow: false,
        // tag
        titleList: [
          { name: this.$t('m.systemConfig["API列表"]') },
          // { name: '编辑分类' }
        ],
        checkIndex: 0,
        isTableLoading: false,
        nameInfo: '',
        // 选中
        checkList: [],
        allCheck: false,
        // 查询
        searchInfo: {
          key: '',
        },
        // 分页
        pagination: {
          current: 1,
          count: 10,
          limit: 10,
        },
        // 新增服务
        entryInfo: {
          show: false,
          title: '',
          width: 700,
        },
        fileVal: '',
        typeInfo: '',
        searchtoggle: false,
      };
    },
    computed: {
      listInfo: {
        // getter
        get() {
          return this.listInfoOri;
        },
        // setter
        set(newVal) {
          this.$parent.listInfo = newVal;
        },
      },
      disableImport() {
        return Number(this.remoteSystem) === 0;
      },
    },
    watch: {
    },
    mounted() {

    },
    methods: {
      async entryOne(item) {
        // 公共api
        if (!this.projectId && !this.hasPermission(['public_api_manage'], item.auth_actions)) {
          const resourceData = {
            public_api: [{
              id: item.id,
              name: item.name,
            }],
          };
          this.applyForPermission(['public_api_manage'], item.auth_actions, resourceData);
          return;
        }
        this.$parent.displayInfo.level_1 = item;
        // 展示 单个api
        await this.$parent.getRemoteApiDetail(item.id);
      },
      getRemoteSystemData() {
        debugger;
        this.$parent.getRemoteSystemData();
        const customPaging = {
          page: this.pagination.current,
          page_size: this.pagination.limit,
        };
        this.$parent.getTableList(this.$parent.displayInfo.level_0.id || '', customPaging, this.searchInfo);
      },
      systemName(id) {
        const system = this.treeList.filter(item => item.id === id);
        if (system.length) {
          return system[0].name;
        }
        return '--';
      },
      changTitle(item, index) {
        this.checkIndex = index;
      },
      // 新增
      openShade(type) {
        if (!this.projectId) {
          if (!this.hasPermission(['public_api_create'])) {
            this.applyForPermission(['public_api_create'], [], {});
            return;
          }
        }
        this.typeInfo = type;
        this.entryInfo.title = type === 'ADD'
          ? this.$t('m.systemConfig["新增接口"]') : this.$t('m.systemConfig["接入接口"]');
        this.$refs.apiDropdown.hide();
        this.entryInfo.show = !this.entryInfo.show;
      },
      dropdownShow() {
        this.isDropdownShow = true;
      },
      dropdownHide() {
        this.isDropdownShow = false;
      },
      // 查询
      serchEntry() {
        const customPaging = {
          page: this.pagination.current,
          page_size: this.pagination.limit,
        };
        this.searchtoggle = true;
        this.$parent.getTableList(this.$parent.displayInfo.level_0.id || '', customPaging, this.searchInfo);
      },
      clearInfo() {
        this.searchInfo.key = '';
        this.serchEntry();
        this.searchtoggle = false;
      },
      // 分页过滤数据
      handlePageLimitChange() {
        this.pagination.limit = arguments[0];
        const customPaging = {
          page: this.pagination.current,
          page_size: this.pagination.limit,
        };
        this.$parent.getTableList(this.$parent.displayInfo.level_0.id || '', customPaging, this.searchInfo);
      },
      handlePageChange(page) {
        this.pagination.current = page;
        const customPaging = {
          page: this.pagination.current,
          page_size: this.pagination.limit,
        };
        this.$parent.getTableList(this.$parent.displayInfo.level_0.id || '', customPaging, this.searchInfo);
      },
      // 全选 半选
      handleSelectAll(selection) {
        this.checkList = selection;
      },
      handleSelect(selection) {
        this.checkList = selection;
      },
      disabledFn(item) {
        if (!this.projectId) {
          return this.hasPermission(['public_api_manage'], item.auth_actions) && !item.is_builtin;
        }
        return !item.is_builtin;
      },
      // 二次弹窗确认
      openDelete(item) {
        if (!this.projectId) {
          if (!this.hasPermission(['public_api_manage'], item.auth_actions)) {
            const resourceData = {
              public_api: [{
                id: item.id,
                name: item.name,
              }],
            };
            this.applyForPermission(['public_api_manage'], item.auth_actions, resourceData);
            return;
          }
        }
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.systemConfig["确认移除服务？"]'),
          subTitle: this.$t('m.systemConfig["移除后，将无法使用该接口，请谨慎操作"]'),
          confirmFn: () => {
            const { id } = item;
            if (this.secondClick) {
              return;
            }
            this.secondClick = true;
            this.$store.dispatch('apiRemote/delete_api', id).then(() => {
              this.$bkMessage({
                message: this.$t('m.systemConfig["删除成功"]'),
                theme: 'success',
              });
              this.getRemoteSystemData();
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.secondClick = false;
              });
          },
        });
      },
      deleteCheck() {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.systemConfig["确认移除服务？"]'),
          subTitle: this.$t('m.systemConfig["移除后，将无法使用该接口，请谨慎操作"]'),
          confirmFn: () => {
            const id = this.checkList.map(item => item.id).join(',');
            if (this.secondClick) {
              return;
            }
            this.secondClick = true;
            this.$store.dispatch('apiRemote/batch_delete_apis', { id }).then(() => {
              this.$bkMessage({
                message: this.$t('m.systemConfig["批量删除成功"]'),
                theme: 'success',
              });
              this.getRemoteSystemData();
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.secondClick = false;
              });
          },
        });
      },
      //
      hasImportPermission() {
        if (!this.projectId) {
          if (!this.hasPermission(['public_api_create'])) {
            this.applyForPermission(['public_api_create'], [], {});
          }
        }
      },
      // 上传文件模板
      handleFile(e) {
        const fileInfo = e.target.files[0];
        if (fileInfo.size <= 10 * 1024 * 1024) {
          const data = new FormData();
          data.append('file', fileInfo);
          data.append('project_key', this.projectId);
          data.append('remote_system', this.remoteSystem);
          const fileType = 'json';
          this.$store.dispatch('apiRemote/get_api_import', { fileType, data }).then((res) => {
            this.$bkMessage({
              message: `${this.$t('m.systemConfig["成功导入"]')}
                                ${res.data.success}
                                ${this.$t('m.systemConfig["个API接口，"]')}
                                ${this.$t('m.systemConfig["失败"]')}
                                ${res.data.failed}
                                ${this.$t('m.systemConfig["个"]')}`,
              theme: 'success',
            });
            this.getRemoteSystemData();
          }, (res) => {
            errorHandler(res, this);
          })
            .finally(() => {
              this.fileVal = '';
            });
        } else {
          this.fileVal = '';
          this.$bkMessage({
            message: this.$t('m.systemConfig["文件大小不能超过10MB！"]'),
            theme: 'error',
          });
        }
      },
      exportFlow(item) {
        window.open(`${window.SITE_URL}api/postman/remote_api/${item.id}/exports/`);
      },
    },
  };
</script>

<style lang="scss" scoped>
    @import '../../../scss/mixins/clearfix.scss';
    @import '../../../scss/mixins/scroller.scss';
    .bk-api-table {
        padding: 20px 10px;
    }
    .bk-api-button {
        @include clearfix;
        line-height: 32px;
        .bk-api-title {
            float: left;
            font-size: 14px;
            color: #424951;
        }
        .bk-api-button {
            float: right;
            .access-btn {
                float: left;
                vertical-align: middle;
            }
        }
        .bk-api-input {
            float: left;
            display: block;
            width: 200px;
        }
        .bk-btn-file {
            float: left;
            line-height: 30px;
            position: relative;
            cursor: pointer;

            .bk-input-file {
                position: absolute;
                top: 0;
                left: 0;
                width: 68px;
                height: 32px;
                overflow: hidden;
                opacity: 0;
                cursor: pointer;
            }
        }
        .batch-remove-btn {
            float: left;
        }
    }
    .bk-table-type {
        padding: 2px 4px;
        background-color: #e1ecff;
        color: #4b8fff;
    }
    .dropdown-trigger-btn {
        padding: 0 15px;
        height: 32px;
        line-height: 32px;
        color: #63656e;
        font-size: 12px;
        border: 1px solid #c4c6cc;
        border-radius: 2px;
        .bk-icon {
            vertical-align: text-top;
        }
    }
</style>
