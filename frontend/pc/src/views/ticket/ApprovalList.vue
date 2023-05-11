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
  <div class="approval-list-wrap ticket-table-wrap">
    <div class="table-wrap">
      <advanced-search
        class="advanced-search"
        ref="advancedSearch"
        :forms="searchForms"
        :is-iframe="isIframe"
        :panel="type"
        :search-result-list="searchResultList"
        @deteleSearchResult="deteleSearchResult"
        @search="handleSearch"
        @clear="handleClearSearch"
        @formChange="handleSearchFormChange">
        <div class="slot-content">
          <bk-button
            class="export"
            :title="$t(`m.tickets['导出']`)"
            @click="isExportDialogShow = true">
            {{ $t('m.tickets["导出"]') }}</bk-button>
          <bk-button
            :theme="'default'"
            :title="$t(`m.managePage['批量审批']`)"
            class="mr10 plus-cus"
            :disabled="!selectedList.length"
            @click="onBatchApprovalClick">
            {{ $t(`m.managePage['批量审批']`) }}
          </bk-button>
        </div>
      </advanced-search>
      <bk-table
        ref="ticketList"
        class="ticket-table"
        v-bkloading="{ isLoading: listLoading && !approveLoadingID }"
        :data="ticketList"
        :pagination="pagination"
        :size="setting.size"
        :row-style="getRowStyle"
        @sort-change="onSortChange"
        @page-change="handlePageChange"
        @page-limit-change="handlePageLimitChange"
        @select-all="handleSelectAll">
        <bk-table-column type="selection" width="60" :selectable="canSelected">
          <template slot-scope="props">
            <bk-checkbox
              v-if="props.row.waiting_approve"
              v-model="props.row.checkStatus"
              @change="changeSelection(props.row)">
            </bk-checkbox>
          </template>
        </bk-table-column>
        <!-- 关注单据 -->
        <bk-table-column
          prop="remind_btn"
          width="30">
          <template slot-scope="{ row }">
            <bk-popover :content="!row.hasAttention ? $t(`m.manageCommon['关注单据']`) : $t(`m.manageCommon['取消关注']`)"
              :interactive="false"
              placement="top">
              <div class="attention-icon">
                <i class="bk-itsm-icon icon-rate" @click="onChangeAttention(row)"></i>
                <i
                  class="bk-itsm-icon icon-favorite"
                  :class="{ 'is-attention': row.hasAttention }"
                  @click="onChangeAttention(row)">
                </i>
              </div>
            </bk-popover>
          </template>
        </bk-table-column>
        <bk-table-column
          v-for="field in setting.selectedFields"
          :key="field.id"
          :label="field.label"
          :width="field.width"
          :render-header="$renderHeader"
          :show-overflow-tooltip="true"
          :min-width="field.minWidth"
          :sortable="field.sortable"
          :prop="field.prop">
          <template slot-scope="props">
            <!-- 单号 -->
            <column-sn v-if="field.id === 'id'" from="ticket_approval" :row="props.row"></column-sn>
            <!-- 当前步骤 -->
            <column-current-step v-else-if="field.id === 'current_steps'"
              :row="props.row"></column-current-step>
            <!-- 状态 -->
            <span v-else-if="field.id === 'status'"
              :title="props.row.current_status_display"
              class="bk-status-color-info"
              :style="getstatusColor(props.row)">
              {{ props.row.current_status_display || '--' }}
            </span>
            <!-- 优先级 -->
            <span v-else-if="field.id === 'priority'"
              class="bk-priority-button" :style="getPriorityColor(props.row)">
              {{ props.row.priority_name || '--' }}
            </span>
            <!-- 操作 -->
            <template v-else-if="field.id === 'operate'">
              <template v-if="approveLoadingID !== props.row.id">
                <bk-link class="table-link mr10" theme="primary" @click="onOpenApprovalDialog(props.row.id, true)">{{ $t(`m.managePage['通过']`) }}</bk-link>
                <bk-link class="table-link" theme="primary" @click="onOpenApprovalDialog(props.row.id, false)">{{ $t(`m.manageCommon['拒绝']`) }}</bk-link>
              </template>
              <div v-else class="table-link approve-laoding">
                <p>{{ $t(`m.task['处理中']`) }}</p>
                <p style="transform: translate(16px, 3px);" v-bkloading="{ isLoading: true, opacity: 1, zIndex: 10, theme: 'primary', mode: 'spin', size: 'mini' }"></p>
              </div>
            </template>
            <!-- 其他 -->
            <span v-else :title="props.row[field.id]">{{ props.row[field.id] || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column type="setting">
          <bk-table-setting-content
            :size="setting.size"
            :fields="setting.fields"
            :selected="setting.selectedFields"
            @setting-change="handleSettingChange">
          </bk-table-setting-content>
        </bk-table-column>
        <div class="empty" slot="empty">
          <!-- <empty
            :is-error="listError"
            :is-search="searchToggle"
            @onRefresh="getTicketList()"
            @onClearSearch="$refs.advancedSearch.onClearClick()">
          </empty> -->
        </div>
      </bk-table>
      <div class="loading" v-if="progressInfo.show">
        <bk-round-progress :width="progressInfo.width" :percent="progressInfo.percent" :config="progressInfo.config" :content="progressInfo.content"></bk-round-progress>
        <div class="approvel-tip">
          <span v-if="progressInfo.showTip">{{ $t(`m['批量审批中，若单据过多可能会耗时较长']`) }}</span>
        </div>
        <div style="transform: translateY(-70px);" v-bkloading="{ isLoading: progressInfo.loading, opacity: 1, zIndex: 10, theme: 'primary', mode: 'spin', size: 'mini' }"></div>
      </div>
    </div>
    <!-- 审批弹窗 -->
    <approval-dialog
      :is-show.sync="isApprovalDialogShow"
      :is-batch="isBatch"
      :approval-info="approvalInfo"
      :selected-list="selectedList"
      @BatchApprovalPolling="BatchApprovalPolling"
      @singleApproval="singleApproval"
      @openApprovalMask="openApprovalMask"
      @cancel="onApprovalDialogHidden">
    </approval-dialog>
    <!-- 导出 -->
    <export-ticket-dialog
      view-type="my_approval"
      :is-show="isExportDialogShow"
      :pagination="pagination"
      :search-params="lastSearchParams"
      @close="isExportDialogShow = false">
    </export-ticket-dialog>
  </div>
</template>
<script>
  import AdvancedSearch from '@/components/form/advancedSearch/NewAdvancedSearch';
  import ExportTicketDialog from '@/components/ticket/ExportTicketDialog.vue';
  import ApprovalDialog from '@/components/ticket/ApprovalDialog.vue';
  import i18n from '@/i18n/index.js';
  import ticketListMixins from './ticketListMixins.js';
  // import Empty from '../../components/common/Empty.vue';

  const COLUMN_LIST = [
    {
      id: 'id',
      label: i18n.t('m.manageCommon[\'单号\']'),
      width: '200',
      disabled: true,
    },
    {
      id: 'title',
      label: i18n.t('m.manageCommon[\'标题\']'),
      minWidth: '180' },
    {
      id: 'service_name',
      label: i18n.t('m.home[\'服务\']'),
      minWidth: '140',
      prop: 'service_name' },
    {
      id: 'service_type_name',
      label: i18n.t('m.manageCommon[\'类型\']'),
      minWidth: '80' },
    {
      id: 'priority',
      label: i18n.t('m.slaContent[\'优先级\']'),
      minWidth: '120',
      sortable: 'custom',
      prop: 'priority_name' },
    {
      id: 'current_steps',
      label: i18n.t('m.newCommon[\'当前步骤\']'),
      minWidth: '80',
      prop: 'current_steps' },
    {
      id: 'current_processors',
      label: i18n.t('m.manageCommon[\'当前处理人\']'),
      width: '130',
      prop: 'current_processors' },
    {
      id: 'status',
      label: i18n.t('m.manageCommon[\'状态\']'),
      minWidth: '120',
      sortable: 'custom',
      prop: 'status' },
    {
      id: 'create_at',
      label: i18n.t('m.manageCommon[\'提单时间\']'),
      minWidth: '140',
      sortable: 'custom',
      prop: 'create_at' },
    {
      id: 'creator',
      label: i18n.t('m.manageCommon[\'提单人\']'),
      minWidth: '140',
      prop: 'creator' },
    {
      id: 'operate',
      label: i18n.t('m.manageCommon[\'操作\']'),
      minWidth: '80' },
  ];

  export default {
    name: 'ApprovalList',
    components: {
      AdvancedSearch,
      ExportTicketDialog,
      ApprovalDialog,
      // Empty,
    },
    mixins: [ticketListMixins],
    props: {
      isIframe: Boolean,
      serviceId: [Number, String],
    },
    data() {
      const columnList = COLUMN_LIST.filter(column => this.$store.state.openFunction.SLA_SWITCH || column.id !== 'priority');
      return {
        columnList,
        type: 'approval',
        isExportDialogShow: false,
        // 批量审批选中单
        selectedList: [],
        progressInfo: {
          count: '', // 轮询后的剩余数
          countSum: '', // 审批单据的总数
          loading: false,
          show: false,
          showTip: true,
          percent: 0,
          width: '100px',
          content: '',
          config: {
            strokeWidth: 10,
            bgColor: '#f0f1f5',
            activeColor: '#3785ff',
          },
        },
        isBatch: true,
        approveLoadingID: '',
      };
    },
    methods: {
      // 批量审批
      onBatchApprovalClick() {
        this.isBatch = true;
        this.isApprovalDialogShow = true;
        this.approvalInfo = {
          result: true,
          showAllOption: true,
          approvalList: this.selectedList.map(item => ({ ticket_id: item.id })),
        };
      },
      // 单个审批
      singleApproval(id, result) {
        if (!result) {
          this.approveLoadingID = id;
        } else {
          if (result.result) {
            this.approveLoadingID = '';
            this.ticketList.splice(this.ticketList.findIndex(item => item.id === Number(id)), 1);
          }
        }
        this.updateSelectStatus();
      },
      // 获取审批状态
      async getTicketsApproveStatus(ids) {
        this.progressInfo.show = true;
        const params = {
          ticket_ids: ids,
        };
        const res = await this.$store.dispatch('ticket/getTicketsApproveStatus', params);
        if (res.result) {
          // 避免接口请求慢影响count记数
          if (res.data.count <= this.progressInfo.count) {
            this.progressInfo.count = res.data.count;
            const { count, countSum } = this.progressInfo;
            this.progressInfo.percent = 1 - (count / countSum);
            this.progressInfo.content = `${countSum - count}/${countSum}`;
            if (this.progressInfo.percent === 1) {
              this.progressInfo.config.activeColor = '#43e45f';
              this.progressInfo.content = this.$t('m["已完成"]');
              this.progressInfo.showTip = false;
              this.progressInfo.loading = false;
            }
          }
        }
      },
      // 批量审批轮询
      BatchApprovalPolling(ids, countSum) {
        this.progressInfo.countSum = countSum;
        this.progressInfo.count = countSum;
        this.progressInfo.showTip = true;
        this.progressInfo.config.activeColor = '#3785ff';
        const timer = setInterval(() => {
          if (this.progressInfo.count) {
            this.getTicketsApproveStatus(ids);
          } else {
            clearInterval(timer);
            this.progressInfo.percent = 0;
            this.progressInfo.showTip = true;
            this.progressInfo.show = false;
            this.progressInfo.content = '-/-';
            this.selectedList = [];
            this.initData();
          }
        }, 500);
      },
      openApprovalMask(sum) {
        this.progressInfo.loading = true;
        this.progressInfo.show = true;
        this.progressInfo.content = `0/${sum}`;
        this.onApprovalDialogHidden();
      },
      updateSelectStatus() {
        this.selectedList = this.ticketList.filter(item => item.checkStatus);
      },
      // 可以选中
      canSelected(row) {
        return row.waiting_approve;
      },
      // 全选 半选
      handleSelectAll(selection) {
        this.ticketList.forEach((item) => {
          item.checkStatus = !!selection.length;
        });
        this.selectedList = selection;
      },
      // 批量审批-单个选中
      // 改变中选态，与表头选择相呼应
      changeSelection(value) {
        this.$refs.ticketList.toggleRowSelection(value, value.checkStatus);
        if (value.checkStatus) {
          if (!this.selectedList.some(item => item.id === value.id)) {
            this.selectedList.push(value);
          }
        } else {
          this.selectedList = this.selectedList.filter(item => item.id !== value.id);
        }
      },
    },
  };
</script>
<style lang="scss" scoped>
    @import './ticketList.scss';
    .table-wrap {
      position: relative;
      .loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        position: absolute;
        top: 0;
        background: #fff;
        opacity: 0.9;
        z-index: 10;
        color: #575961;
        text-align: center;
        .approvel-tip {
          display: block;
          width: 100%;
          height: 40px;
          line-height: 40px;
        }
      }
    }
    .approve-laoding {
      display: flex;
    }
</style>
