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
        {{ title }}
      </p>
    </div>
    <div class="itsm-page-content">
      <div class="bk-api-configure">
        <div class="bk-directory-tree">
          <api-tree
            ref="apiTree"
            :project-id="projectId"
            :code-list="codeList"
            :all-code-list="allCodeList"
            :tree-list-ori="treeList">
          </api-tree>
        </div>
        <div class="bk-directory-table">
          <api-table v-if="!Object.keys(displayInfo['level_1']).length"
            ref="apiTable"
            :remote-system="remoteSystem"
            :project-id="projectId"
            :first-level-info="firstLevelInfo"
            :custom-paging="customPaging"
            :tree-list="treeList"
            :path-list="pathList"
            :get-list-error="listError"
            :list-info-ori="listInfo">
          </api-table>
          <api-content v-else
            :remote-system="remoteSystem"
            :second-level-info="secondLevelInfo"
            :api-detail-info="apiDetailInfo"
            :tree-list="treeList"
            :path-list="pathList"
            :is-builtin-id-list="isBuiltinIdList">
          </api-content>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import mixins from '../../commonMix/mixins_api.js';
  import apiTree from './apiTree.vue';
  import apiTable from './apiTable.vue';
  import apiContent from './apiContent.vue';
  import { errorHandler } from '../../../utils/errorHandler.js';

  export default {
    components: {
      apiTree,
      apiTable,
      apiContent,
    },
    mixins: [mixins],
    props: {
      projectId: String,
      title: {
        type: String,
        default: 'API',
      },
    },
    data() {
      return {
        // 目前展示信息
        displayInfo: {
          level_0: {},
          level_1: {},
        },
        // 系统id
        remoteSystem: '',
        // API 详情
        apiDetailInfo: {},
        // API列表
        listInfo: [],
        // 系统分类列表
        treeList: [
          {
            id: 0,
            name: this.$t('m.systemConfig["全部系统"]'),
            code: '',
            check: false,
          },
        ],
        // code列表
        codeList: [],
        allCodeList: [],
        pathList: [],
        isBuiltinIdList: [],
        isSelectedApiList: [],
        showContent: false,
        customPaging: {
          total_page: 1,
          page: 1,
          count: 0,
          page_size: 10,
          list: [
            { num: 5 },
            { num: 10 },
            { num: 15 },
            { num: 20 },
          ],
        },
        listError: false,
      };
    },
    computed: {
      sliderStatus() {
        return this.$store.state.common.slideStatus;
      },
      firstLevelInfo() {
        return this.displayInfo.level_0;
      },
      secondLevelInfo() {
        return this.displayInfo.level_1;
      },
    },
    mounted() {
      this.getRemoteSystemData();
    },
    methods: {
      // 获取系统
      getRemoteSystemData() {
        const params = {
          project_key: this.projectId || 'public',
        };
        this.$refs.apiTree.isTreeLoading = true;
        this.$store.dispatch('apiRemote/get_remote_system', params).then((res) => {
          this.isBuiltinIdList = res.data.map(item => item.system_id);
          res.data.forEach((item) => {
            item.moreShow = false;
            item.check = item.id === this.displayInfo.level_0.id;
          });
          this.treeList = [this.treeList[0], ...res.data];
          this.getSystems();
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.$refs.apiTree.isTreeLoading = false;
          });
      },
      // 获取codeList
      async getSystems() {
        const params = {};
        await this.$store.dispatch('apiRemote/get_systems', params).then((res) => {
          this.allCodeList = res.data;
          this.codeList = res.data.filter(item => this.isBuiltinIdList.indexOf(item.system_id) === -1);
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
          });
      },
      // 获取API详情
      async getRemoteApiDetail(id) {
        const params = {
          id,
        };
        await this.$store.dispatch('apiRemote/get_remote_api_detail', params).then((res) => {
          this.apiDetailInfo = res.data;
          this.apiDetailInfo.ownersInputValue = this.apiDetailInfo.owners ? this.apiDetailInfo.owners.split(',') : [];
          if (!this.apiDetailInfo.req_headers.length) {
            this.apiDetailInfo.req_headers = [];
          }
          if (!this.apiDetailInfo.req_params.length) {
            this.apiDetailInfo.req_params = [];
          } else {
            this.apiDetailInfo.req_params = [...this.apiDetailInfo.req_params.map((item) => {
              item.value = '';
              return item;
            })];
          }
          if (!Object.keys(this.apiDetailInfo.req_body).length || !Object.keys(this.apiDetailInfo.req_body.properties).length) {
            this.apiDetailInfo.treeDataList = [{
              has_children: false,
              showChildren: true,
              checkInfo: false,
              key: 'root',
              is_necessary: true,
              type: 'object',
              desc: this.$t('m.systemConfig["初始化数据"]'),
              parentInfo: '',
              children: [],
            }];
            this.apiDetailInfo.bodyJsonData = {
              root: {},
            };
            this.apiDetailInfo.bodyTableData = [];
          } else {
            this.apiDetailInfo.treeDataList = this.jsonschemaToList({
              root: JSON.parse(JSON.stringify(this.apiDetailInfo.req_body)), // root初始 Jsonschema数据结构
            });
            this.apiDetailInfo.bodyJsonData = this.jsonschemaToJson({
              root: JSON.parse(JSON.stringify(this.apiDetailInfo.req_body)), // root初始 Jsonschema数据结构
            });
            this.apiDetailInfo.bodyTableData = this.treeToTableList(JSON.parse(JSON.stringify(this.apiDetailInfo.treeDataList[0].children)));
          }
          if (!Object.keys(this.apiDetailInfo.rsp_data).length || !Object.keys(this.apiDetailInfo.rsp_data.properties).length) {
            this.apiDetailInfo.responseTreeDataList = [{
              has_children: false,
              showChildren: true,
              checkInfo: false,
              key: 'root',
              is_necessary: true,
              type: 'object',
              desc: this.$t('m.systemConfig["初始化数据"]'),
              parentInfo: '',
              children: [],
            }];
            this.apiDetailInfo.responseJsonData = {
              root: {},
            };
            this.apiDetailInfo.responseTableData = [];
          } else {
            this.apiDetailInfo.responseTreeDataList = this.jsonschemaToList({
              root: this.apiDetailInfo.rsp_data, // root初始 Jsonschema数据结构
            });
            this.apiDetailInfo.responseJsonData = this.jsonschemaToJson({
              root: this.apiDetailInfo.rsp_data, // root初始 Jsonschema数据结构
            });
            this.apiDetailInfo.responseTableData = this.treeToTableList(JSON.parse(JSON.stringify(this.apiDetailInfo.responseTreeDataList[0].children)));
          }
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 获取已接入api接口列表数据
      async getTableList(id, customPaging, searchInfo) {
        await this.displayInfo.level_1;
        await this.$refs.apiTable;
        this.remoteSystem = id;
        const params = {
          remote_system: id || '',
          page_size: customPaging ? customPaging.page_size : 10,
          is_draft: 0,
          page: customPaging ? customPaging.page : 1,
          // 关键字
          key: searchInfo ? searchInfo.key : '',
          project_key: this.projectId || 'public',
        };
        this.$refs.apiTable.isTableLoading = true;
        this.listError = false;
        await this.$store.dispatch('apiRemote/get_remote_api', params).then((res) => {
          this.isSelectedApiList = res.data.items.filter(ite => !ite.is_builtin).map(item => item.path);
          this.listInfo = res.data.items.map((item) => {
            item.check = false;
            return item;
          });
          // 分页
          this.$refs.apiTable.pagination.current = res.data.page;
          this.$refs.apiTable.pagination.count = res.data.count;
        })
          .catch((res) => {
            this.listError = true;
            errorHandler(res, this);
          })
          .finally(() => {
            this.$refs.apiTable.isTableLoading = false;
          });
      },
      // 根据系统code --> 获取pathList 未接入api接口
      async getChannelPathList(code) {
        const params = {
          system_code: code,
        };
        await this.$store.dispatch('apiRemote/get_components', params).then((res) => {
          this.pathList = res.data.map((item) => {
            item.func_name = item.name;
            item.name = item.label;
            return item;
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
          });
      },
    },
  };
</script>

<style lang="scss" scoped>
    @import '../../../scss/mixins/clearfix.scss';
    @import '../../../scss/mixins/scroller.scss';
    .bk-api-configure {
        background-color: #fff;
        border: 1px solid #DDE4EB;
        height: 100%;
        @include clearfix;
    }
    .bk-directory-tree {
        height: 100%;
        width: 300px;
        float: left;
        border-right: 1px solid #dde4eb;
        position: relative;
        overflow: auto;
        @include scroller;
    }
    .bk-directory-table {
        height: 100%;
        width: calc(100% - 300px);
        float: left;
        position: relative;
        overflow: auto;
        @include scroller;
    }
</style>
<style lang="scss">
    .ace_editor {
        font: 12px/normal 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;

        div {
            font: inherit !important;
        }

        .ace_line_group .ace_line {
            font: inherit !important;

            span {
                font: inherit !important;
            }
        }
    }
</style>
