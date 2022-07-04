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
        {{ $t('m.flowManager["流程版本"]') }}
      </p>
    </div>
    <div class="itsm-page-content">
      <!-- 提示信息 -->
      <div class="bk-itsm-version" v-if="versionStatus">
        <i class="bk-icon icon-info-circle"></i>
        <span>{{ $t('m.flowManager["流程版本：由流程模板部署后即可生成"]') }}</span>
        <i class="bk-icon icon-close" @click="closeVersion"></i>
      </div>
      <div class="bk-only-btn">
        <div class="bk-more-search">
          <bk-button
            :theme="'primary'"
            :title="$t(`m.flowManager['批量删除']`)"
            :disabled="!checkList.length"
            class="mr10"
            @click="openConfirmDialog({}, 'batchDelete')">
            {{ $t(`m.flowManager['批量删除']`) }}
          </bk-button>
          <div class="bk-search-name">
            <div class="bk-search-content">
              <bk-input
                :clearable="true"
                :right-icon="'bk-icon icon-search'"
                v-model="moreSearch[0].value"
                @enter="searchContent"
                @clear="clearSearch">
              </bk-input>
            </div>
            <bk-button :title="$t(`m.deployPage['更多筛选条件']`)"
              icon=" bk-itsm-icon icon-search-more"
              class="ml10 filter-btn"
              @click="searchMore">
            </bk-button>
          </div>
        </div>
        <search-info
          ref="searchInfo"
          :more-search="moreSearch">
        </search-info>
      </div>
      <bk-table ref="versionTable"
        v-bkloading="{ isLoading: isDataLoading }"
        :data="dataList"
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
          <template slot-scope="props">
            <template v-if="!hasPermission(['flow_version_manage'], props.row.auth_actions)">
              <div style="height: 100%; display: flex; justify-content: center; align-items: center;">
                <span
                  v-cursor
                  class="checkbox-permission-disable"
                  @click="checkfowManagePermisson(props.row)">
                </span>
              </div>
            </template>
            <template v-else>
              <bk-checkbox
                v-bk-tooltips.top="{
                  content: $t(`m.flowManager['流程已绑定服务，不能进行删除操作']`),
                  disabled: !props.row.service_cnt
                }"
                :true-value="trueStatus"
                :false-value="falseStatus"
                :disabled="!!props.row.service_cnt"
                v-model="props.row.checkStatus"
                @change="changeCheck(props.row)">
              </bk-checkbox>
            </template>
          </template>
        </bk-table-column>
        <!--<bk-table-column type="index" label="NO." align="center" width="60"></bk-table-column>-->
        <bk-table-column :label="$t(`m.common['ID']`)" min-width="60">
          <template slot-scope="props">
            <span :title="props.row.id">{{ props.row.id || '--' }}</span>
          </template>
        </bk-table-column>

        <bk-table-column :label="$t(`m.flowManager['流程名']`)" width="200">
          <template slot-scope="props">
            <span :title="props.row.name">{{ props.row.name || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.flowManager['版本号']`)" min-width="150">
          <template slot-scope="props">
            <span :title="props.row.version_number">{{ props.row.version_number || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.flowManager['发布人']`)">
          <template slot-scope="props">
            <span :title="props.row.updated_by">{{ props.row.updated_by || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.flowManager['发布时间']`)" min-width="150">
          <template slot-scope="props">
            <span :title="props.row.update_at">{{ props.row.update_at || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.flowManager['关联服务数']`)" width="90">
          <template slot-scope="props">
            <span :title="props.row.service_cnt">{{ props.row.service_cnt || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.flowManager['操作']`)" width="150">
          <template slot-scope="props">
            <bk-button
              v-cursor="{ active: !hasPermission(['flow_version_manage'], props.row.auth_actions) }"
              text
              theme="primary"
              :title="$t(`m.flowManager['预览']`)"
              :class="[{
                'btn-permission-disable':
                  !hasPermission(['flow_version_manage'], props.row.auth_actions)
              }]"
              @click="onFlowPreview(props.row)">
              {{ $t('m.flowManager["预览"]') }}
            </bk-button>
            <bk-button
              v-cursor="{ active: !hasPermission(['flow_version_restore'], props.row.auth_actions) }"
              text
              theme="primary"
              :title="$t(`m.flowManager['还原']`)"
              :class="[{
                'btn-permission-disable':
                  !hasPermission(['flow_version_restore'], props.row.auth_actions)
              }]"
              @click="openConfirmDialog(props.row, 'restore')">
              {{ $t('m.flowManager["还原"]') }}
            </bk-button>
            <bk-button
              v-cursor="{ active: !hasPermission(['flow_version_manage'], props.row.auth_actions) }"
              text
              theme="primary"
              :title="$t(`m.flowManager['删除']`)"
              :disabled="hasPermission(['flow_version_manage'], props.row.auth_actions)
                && !!props.row.service_cnt"
              :class="[{
                'btn-permission-disable':
                  !hasPermission(['flow_version_manage'], props.row.auth_actions)
              }]"
              @click="openConfirmDialog(props.row, 'delete')">
              {{ $t('m.flowManager["删除"]') }}
            </bk-button>
          </template>
        </bk-table-column>
      </bk-table>
    </div>
    <!-- 预览 -->
    <bk-dialog v-model="processInfo.isShow"
      width="760"
      :position="processInfo.position"
      :draggable="processInfo.draggable"
      :title="processInfo.title">
      <div style="width: 100%; height: 347px;" v-bkloading="{ isLoading: processInfo.loading }">
        <preview
          v-if="!processInfo.loading"
          :add-list="addList"
          :line-list="lineList"
          :preview-info="previewInfo"
          :normal-color="normalColor">
        </preview>
      </div>
      <div slot="footer">
        <bk-button
          theme="default"
          @click="processInfo.isShow = false">
          {{ $t('m.deployPage["关闭"]') }}
        </bk-button>
      </div>
    </bk-dialog>
  </div>
</template>
<script>
  import axios from 'axios';
  import searchInfo from '../../commonComponent/searchInfo/searchInfo.vue';
  import preview from '../../commonComponent/preview';
  import permission from '@/mixins/permission.js';
  import { errorHandler } from '../../../utils/errorHandler';

  export default {
    name: 'FlowVersion',
    components: {
      searchInfo,
      preview,
    },
    mixins: [permission],
    data() {
      return {
        secondClick: false,
        versionStatus: true,
        isDataLoading: false,
        normalColor: true,
        trueStatus: true,
        falseStatus: false,
        dataList: [],
        pagination: {
          current: 1,
          count: 10,
          limit: 10,
        },
        // 勾选
        checkList: [],
        // 查询
        moreSearch: [
          {
            name: this.$t('m.flowManager["流程名"]'),
            type: 'input',
            typeKey: 'name__contains',
            value: '',
            list: [],
          },
          {
            name: this.$t('m.flowManager["版本号"]'),
            type: 'input',
            typeKey: 'version_number__contains',
            value: '',
            list: [],
          },
          {
            name: this.$t('m.flowManager["发布人"]'),
            type: 'member',
            typeKey: 'updated_by__contains',
            multiSelect: true,
            value: [],
            list: [],
          },
        ],
        // 删除，还原
        deleteInfo: {
          type: '',
          info: {},
        },
        // 流程预览
        processInfo: {
          isShow: false,
          title: this.$t('m.flowManager["流程预览"]'),
          position: {
            top: 150,
          },
          draggable: true,
          loading: true,
          version: 'version',
          addList: [],
        },
        previewInfo: {
          canClick: false,
          narrowSize: 0.8,
        },
        addList: [],
        lineList: [],
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
      getList(page) {
        // 查询时复位页码
        if (page !== undefined) {
          this.pagination.current = page;
        }
        // 重新获取数据时清空选中的数据
        this.checkList = [];
        const params = {
          page: this.pagination.current,
          page_size: this.pagination.limit,
        };
        this.moreSearch.forEach((item) => {
          if (Array.isArray(item.value) ? !!item.value.length : !!item.value) {
            params[item.typeKey] = Array.isArray(item.value) ? item.value.join(',') : item.value;
          }
        });
        this.isDataLoading = true;
        this.$store.dispatch('workflowVersion/list', params).then((res) => {
          this.dataList = res.data.items;
          this.dataList.forEach((item) => {
            this.$set(item, 'checkStatus', false);
          });
          // 分页
          this.pagination.current = res.data.page;
          this.pagination.count = res.data.count;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
      },
      // 分页过滤数据
      handlePageLimitChange() {
        this.pagination.limit = arguments[0];
        this.getList();
      },
      handlePageChange(page) {
        this.pagination.current = page;
        this.getList();
      },
      // 全选 半选
      handleSelectAll(selection) {
        this.dataList.forEach((item) => {
          // 关联了当前这个流程版本的服务的数量不为 0 且有管理权限
          if (!item.service_cnt && this.hasPermission(['flow_version_manage'], item.auth_actions)) {
            item.checkStatus = !!selection.length;
          }
        });
        // 选中有权限数据
        this.checkList = selection.filter(item => this.hasPermission(['flow_version_manage'], item.auth_actions));
      },
      handleSelect(selection) {
        this.checkList = selection;
      },
      disabledFn(item) {
        return !item.service_cnt;
      },
      changeCheck(value) {
        // 改变中选态，与表头选择相呼应
        this.$refs.versionTable.toggleRowSelection(value, value.checkStatus);
        if (value.checkStatus) {
          if (!this.checkList.some(item => item.id === value.id)) {
            this.checkList.push(value);
          }
        } else {
          this.checkList = this.checkList.filter(item => item.id !== value.id);
        }
      },
      // 简单查询
      searchContent() {
        this.getList(1);
      },
      searchMore() {
        this.$refs.searchInfo.searchMore();
      },
      // 清空搜索表单
      clearSearch() {
        this.moreSearch.forEach((item) => {
          item.value = item.multiSelect ? [] : '';
        });
        this.getList(1);
      },
      changePageSize() {
        if (this.customPaging.page_size < 5) {
          this.customPaging.page_size = 5;
        } else if (this.customPaging.page_size > 100) {
          this.customPaging.page_size = 100;
        }

        this.getList(1);
      },
      // 点击分页回调
      pageChange(page) {
        this.customPaging.page = page;
        this.getList();
      },
      /**
       * 打开二次确认弹窗
       * @param {Object} item 操作数据项
       * @param {type} type 操作类型
       */
      openConfirmDialog(item, type) {
        if (type === 'delete' && !this.checkfowManagePermisson(item)) {
          return;
        }
        if (type === 'restore' && !this.checkfowRestorePermisson(item)) {
          return;
        }
        const titleMap = new Map([
          ['delete', this.$t('m.flowManager["流程版本删除确认"]')],
          ['restore', this.$t('m.flowManager["流程版本还原确认"]')],
          ['export', this.$t('m.flowManager["流程版本导出确认"]')],
          ['batchDelete', this.$t('m.flowManager["流程版本批量删除确认"]')],
        ]);
        const contentMap = new Map([
          ['delete', this.$t('m.flowManager["删除之后服务将无法关联这些流程版本"]')],
          ['restore', this.$t('m.flowManager["还原后请移步到流程设计处编辑"]')],
          ['export', this.$t('m.flowManager["确认后将导出当前版本的流程数据为JSON格式的文件"]')],
          ['batchDelete', this.$t('m.flowManager["删除之后服务将无法关联这些流程版本"]')],
        ]);
        if (item.service_cnt && type === 'delete') {
          return;
        }

        this.deleteInfo.info = item;
        this.deleteInfo.type = type;
        this.$bkInfo({
          type: 'warning',
          title: titleMap.get(type),
          subTitle: contentMap.get(type),
          confirmFn: () => {
            this.submitFn();
          },
        });
      },
      submitFn() {
        if (this.deleteInfo.type === 'delete') {
          this.deleteSubmit();
        } else if (this.deleteInfo.type === 'restore') {
          this.restoreSubmit();
        } else if (this.deleteInfo.type === 'export') {
          this.exportSubmit();
        } else if (this.deleteInfo.type === 'batchDelete') {
          this.batchDeleteSubmit();
        }
      },
      // 批量删除
      batchDeleteSubmit() {
        if (this.secondClick) {
          return;
        }
        this.secondClick = true;
        const idArr = this.checkList.map(item => item.id);
        const id = idArr.join(',');
        this.$store.dispatch('workflowVersion/batchDelete', { id }).then(() => {
          this.$bkMessage({
            message: this.$t('m.flowManager["批量删除成功"]'),
            theme: 'success',
          });
          this.checkList = [];
          this.getList();
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.secondClick = false;
          });
      },
      // 删除
      deleteSubmit() {
        if (this.secondClick) {
          return;
        }
        this.secondClick = true;
        this.$store.dispatch('workflowVersion/delete', this.deleteInfo.info.id).then(() => {
          this.$bkMessage({
            message: this.$t('m.flowManager["删除成功"]'),
            theme: 'success',
          });
          this.getList(1);
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.secondClick = false;
          });
      },
      // 还原
      restoreSubmit() {
        if (this.secondClick) {
          return;
        }
        this.secondClick = true;
        this.$store.dispatch('workflowVersion/restore', this.deleteInfo.info.id).then(() => {
          this.$bkMessage({
            message: this.$t('m.flowManager["成功还原该流程，请前往【流程设计】查看"]'),
            theme: 'success',
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.secondClick = false;
          });
      },
      // 流程预览
      onFlowPreview(item) {
        if (!this.checkfowManagePermisson(item)) {
          return;
        }
        const { id } = item;
        if (!id) {
          return;
        }
        this.processInfo.isShow = !this.processInfo.isShow;
        this.processInfo.loading = true;
        axios.all([
          this.$store.dispatch('deployCommon/getNodeVersion', { id }),
          this.$store.dispatch('deployCommon/getLineVersion', { id }),
        ]).then(axios.spread((userResp, reposResp) => {
          this.addList = userResp.data;
          for (let i = 0; i < this.addList.length; i++) {
            this.addList[i].indexInfo = i;
          }
          this.lineList = reposResp.data.items;
        }))
          .finally(() => {
            this.processInfo.loading = false;
          });
      },
      // 关闭版本提示信息
      closeVersion() {
        this.versionStatus = false;
      },
      // 流程版本管理权限校验
      checkfowManagePermisson(item) {
        if (!this.hasPermission(['flow_version_manage'], item.auth_actions)) {
          const { projectInfo } = this.$store.state.project;
          const resourceData = {
            project: [{
              id: projectInfo.key,
              name: projectInfo.name,
            }],
            flow_version: [{
              id: item.id,
              name: item.name,
            }],
          };
          this.applyForPermission(['flow_version_manage'], item.auth_actions, resourceData);
          return false;
        }
        return true;
      },
      // check 流程版本还原权限
      checkfowRestorePermisson(item) {
        if (!this.hasPermission(['flow_version_restore'], item.auth_actions)) {
          const { projectInfo } = this.$store.state.project;
          const resourceData = {
            project: [{
              id: projectInfo.key,
              name: projectInfo.name,
            }],
            flow_version: [{
              id: item.id,
              name: item.name,
            }],
            workflow: [{
              id: item.workflow_id,
              name: item.name,
            }],
          };
          this.applyForPermission(['flow_version_restore'], item.auth_actions, resourceData);
          return false;
        }
        return true;
      },
    },
  };
</script>

<style lang='scss' scoped>
    .filter-btn /deep/ .icon-search-more {
        font-size: 14px;
    }
</style>
