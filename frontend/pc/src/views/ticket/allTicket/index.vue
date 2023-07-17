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
  <div class="all-ticket-page">
    <div class="ticket-tab">
      <nav-title :title-name="titleName"></nav-title>
      <div class="ticket-content">
        <div class="operate-wrapper">
          <advanced-search
            class="advanced-search"
            ref="advancedSearch"
            :forms="searchForms"
            @search="handleSearch"
            @onChangeHighlight="getAllTicketList()"
            @formChange="handleSearchFormChange"
            @clear="handleClearSearch">
            <div class="slot-content">
              <bk-button
                data-test-id="ticket_button_export"
                class="export"
                :title="$t(`m.tickets['导出']`)"
                @click="openExportList">
                {{ $t('m.tickets["导出"]') }}
              </bk-button>
            </div>
          </advanced-search>
        </div>
        <div class="table-wrapper">
          <table-content
            v-bkloading="{ isLoading: ticketListLoading }"
            :data-list="ticketList"
            :pagination="pagination"
            :get-list-error="listError"
            :color-hex-list="colorHexList"
            @submitSuccess="evaluationSubmitSuccess"
            @orderingClick="orderingClick"
            @handlePageLimitChange="handlePageLimitChange"
            @handlePageChange="handlePageChange"
            @clearSearch="$refs.advancedSearch[0].onClearClick()">
          </table-content>
        </div>
      </div>
    </div>
    <!-- 导出 -->
    <export-ticket-dialog
      :is-show="isExportDialogShow"
      :pagination="pagination"
      :view-type="''"
      :search-params="searchParams"
      @close="isExportDialogShow = false">
    </export-ticket-dialog>
  </div>
</template>
<!-- 自定义tab 选择服务目录是只能选择下级目录 -->
<script>
  import NavTitle from '@/components/common/layout/NavTitle';
  import AdvancedSearch from '@/components/form/advancedSearch/NewAdvancedSearch';
  import TableContent from './tableContent';
  import ExportTicketDialog from '@/components/ticket/ExportTicketDialog.vue';
  import { errorHandler } from '../../../utils/errorHandler';
  import ticketListMixins from '@/mixins/ticketList.js';

  export default {
    name: 'AllTicket',
    components: {
      NavTitle,
      AdvancedSearch,
      TableContent,
      ExportTicketDialog,
    },
    mixins: [ticketListMixins],
    props: {
      projectId: String,
      from: String,
    },
    data() {
      const SEARCH_FORM = [
        {
          name: this.$t('m.tickets[\'单号/标题\']'),
          desc: this.$t('m.tickets[\'单号/标题\']'),
          type: 'input',
          key: 'keyword',
          display: true,
          value: '',
          list: [],
          placeholder: this.$t('m.tickets["请选择单号/标题"]'),
        },
        {
          name: this.$t('m["项目"]'),
          desc: this.$t('m["项目"]'),
          type: 'select',
          key: 'project_key',
          display: true,
          value: '',
          list: [],
          placeholder: this.$t('m["请选择项目"]'),
        },
        {
          name: this.$t('m.tickets["服务目录"]'),
          type: 'cascade',
          key: 'catalog_id',
          multiSelect: true,
          display: true,
          value: [],
          list: [],
          placeholder: this.$t('m.tickets["请选择服务目录"]'),
        },
        {
          name: this.$t('m.tickets["服务"]'),
          type: 'select',
          key: 'service_id__in',
          multiSelect: true,
          display: false,
          value: [],
          list: [],
          placeholder: this.$t('m.tickets["请选择服务"]'),
        },
        {
          name: this.$t('m.tickets["提单人"]'),
          type: 'member',
          key: 'creator__in',
          multiSelect: true,
          display: true,
          value: [],
          list: [],
          placeholder: this.$t('m.tickets["请选择提单人"]'),
        },
        {
          name: this.$t('m.tickets["处理人"]'),
          type: 'member',
          key: 'current_processor',
          multiSelect: true,
          display: true,
          value: [],
          list: [],
          placeholder: this.$t('m.tickets["请选择处理人"]'),
        },
        {
          name: this.$t('m.tickets["状态"]'),
          type: 'select',
          key: 'current_status__in',
          multiSelect: true,
          display: true,
          value: [],
          list: [],
          placeholder: this.$t('m.tickets["请选择状态"]'),
        },
        {
          name: this.$t('m.tickets["提单时间"]'),
          key: 'date_update',
          type: 'datetime',
          display: true,
          value: [],
          list: [],
          placeholder: this.$t('m.tickets["请选择提单时间"]'),
        },
        {
          name: this.$t('m.tickets["业务"]'),
          key: 'bk_biz_id',
          type: 'select',
          display: true,
          value: '',
          list: [],
          placeholder: this.$t('m.tickets["请选择业务"]'),
        },
      ];
      return {
        isExportDialogShow: false,
        titleName: this.$t('m.managePage["所有单据"]'),
        ticketList: [],
        ticketListLoading: false,
        pagination: {
          current: 1,
          count: 0,
          limit: 10,
        },
        // 状态颜色配置list
        colorHexList: [],
        // 查询
        searchForms: SEARCH_FORM.slice(0),
        searchParams: {}, // 高级搜索内容
        orderKey: '-create_at', // 排序
        listError: false,
      };
    },
    created() {
      this.initData();
    },
    methods: {
      async initData() {
        this.loading = true;
        // 获取所有tab的单据列表
        this.getAllTicketList();
        // 获取状态颜色接口
        this.getTypeStatus();
        // 获取全局视图状态
        this.getGlobalStatus();
        this.getBusinessList();
      },
      // 获取所有单据列表
      getAllTicketList() {
        const fixParams = {
          page_size: this.pagination.limit,
          page: this.pagination.current,
          ordering: this.orderKey,
        };

        // 项目下的所有单据
        if (this.projectId) {
          fixParams.project_key = this.projectId;
        }
        let searchParams;
        if (JSON.stringify(this.searchParams) === '{}') {
          searchParams = { service_id__in: this.$route.query.service_id }; // 没有参数时默认将 url 参数作为查询参数
        } else {
          searchParams = this.searchParams;
        }
        this.ticketListLoading = true;
        fixParams.is_draft = 0;
        fixParams.view_type = '';
        Object.assign(fixParams, searchParams);
        this.listError = false;
        return this.$store.dispatch('change/getList', fixParams)
          .then((res) => {
            this.ticketList = res.data.items;
            // 异步加载列表中的某些字段信息
            this.__asyncReplaceTicketListAttr(this.ticketList);
            // 分页
            this.pagination.current = res.data.page;
            this.pagination.count = res.data.count;
          })
          .catch(() => {
            this.listError = true;
          })
          .finally(() => {
            this.ticketListLoading = false;
          });
      },
      // 获取单据状态
      getGlobalStatus() {
        const params = {
          source_uri: 'ticket_status',
        };
        this.$store
          .dispatch('ticketStatus/getOverallTicketStatuses', params)
          .then((res) => {
            const formItem = this.searchForms.find((item) => item.key === 'current_status__in');
            formItem.list = res.data;
          })
          .catch((res) => {
            this.$bkMessage({
              message: res.data.msg,
              theme: 'error',
            });
          });
      },
      // 获取状态颜色接口
      getTypeStatus() {
        this.$store
          .dispatch('ticketStatus/getTypeStatus')
          .then((res) => {
            this.colorHexList = res.data;
          })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      getBusinessList() {
        this.$store
          .dispatch('eventType/getAppList')
          .then((res) => {
            this.searchForms.find((item) => item.key === 'bk_biz_id').list = res.data;
          })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 导出弹框
      openExportList() {
        this.isExportDialogShow = true;
      },
      handleSearch(params) {
        this.pagination.current = 1;
        this.searchParams = params;
        this.getAllTicketList();
      },
      // 清空搜索表单
      handleClearSearch() {
        this.searchForms.forEach((item) => {
          if (item.key === 'service_id__in') {
            item.display = false;
          }
        });
      },
      // 展开高级搜索
      handleSearchFormChange(key, val) {
        if (key === 'catalog_id') {
          const formItem = this.searchForms.find((item) => item.key === 'service_id__in');
          formItem.display = val.length;
          if (val.length) {
            // 当服务目录的数据发生变化时，清空服务数据
            formItem.value = [];
          }
        }
      },
      // 分页过滤数据
      handlePageLimitChange(limit) {
        this.pagination.current = 1;
        this.pagination.limit = limit;
        this.getAllTicketList();
      },
      handlePageChange(page) {
        this.pagination.current = page;
        this.getAllTicketList();
      },
      // 排序
      orderingClick(order) {
        this.orderKey = order;
        this.getAllTicketList();
      },
      // 评价成功回调
      evaluationSubmitSuccess() {
        this.getAllTicketList();
      },
    },
  };
</script>
<style lang="scss" scoped>
@import "~@/scss/mixins/scroller.scss";
.all-ticket-page {
  height: 100%;
  background: #fafbfd;
  /deep/ .bk-tab-section {
    padding: 0;
    background-color: #f5f7fa;
  }
  .bk-tab-label-item {
    .list-wrapper {
      display: flex;
      align-items: center;
      position: relative;
      .ticket-file-count {
        display: inline-block;
        vertical-align: middle;
        margin: 0 3px;
        min-width: 24px;
        height: 16px;
        padding: 0 4px;
        line-height: 16px;
        border-radius: 8px;
        text-align: center;
        font-style: normal;
        font-size: 12px;
        font-weight: bold;
        font-family: Helvetica, Arial;
        color: #979ba5;
        background-color: #f0f1f5;
      }
    }
    &.active,
    &:hover {
      .ticket-file-count {
        background: #e1ecff;
        color: #3a84ff;
      }
    }
  }
  /deep/ .bk-tab-label-wrapper {
    box-shadow: 0px 2px 2px 0px rgba(0, 0, 0, 0.1);
  }
  .ticket-content {
    padding: 14px 18px 15px 22px;
    height: calc(100vh - 146px);
    overflow: auto;
    @include scroller;
    .operate-wrapper {
      margin-bottom: 14px;
      .slot-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        .checkbox-wapper {
          display: flex;
          align-items: center;
        }
        .export {
          width: 86px;
        }
        .bk-form-checkbox {
          width: 78px;
          margin-right: 21px;
        }
      }
    }
  }
}
.nav-list {
  display: flex;
  height: 50px;
  overflow-x: auto;
  overflow-y: hidden;
  z-index: 999;
  @include scroller(#a5a5a5, 4px, 4px);
  .service-type-item {
    display: inline-block;
    padding: 2px 20px;
    height: 50px;
    line-height: 50px;
    font-size: 14px;
    color: #63656e;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
    cursor: pointer;
    &:hover {
      color: #3a84ff;
      .ticket-file-count {
        background: #3a84ff;
        color: white;
      }
    }
    &.active {
      color: #3a84ff;
      border-bottom: 4px solid #3a84ff;
    }
    .ticket-file-count {
      padding: 0 2px;
      font-size: 12px;
      background: #f0f1f5;
      border-radius: 7px;
    }
  }
}
.bk-form {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  .bk-form-title {
    width: 100%;
    margin-left: 2px;
    font-size: 14px;
    font-weight: 600;
  }
  .bk-form-item {
    width: 50%;
    min-height: 32px;
    /deep/ .bk-form-content {
      width: auto;
      min-height: 32px;
      margin-left: 150px;
      position: relative;
      outline: none;
      line-height: 0px;
    }
  }
}
</style>
