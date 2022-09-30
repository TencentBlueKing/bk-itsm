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
        v-bkloading="{ isLoading: listLoading }"
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
              <bk-link class="table-link mr10" theme="primary" @click="onOpenApprovalDialog(props.row.id, true)">{{ $t(`m.managePage['通过']`) }}</bk-link>
              <bk-link class="table-link" theme="primary" @click="onOpenApprovalDialog(props.row.id, false)">{{ $t(`m.manageCommon['拒绝']`) }}</bk-link>
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
      </bk-table>
    </div>
    <!-- 审批弹窗 -->
    <approval-dialog
      :is-show.sync="isApprovalDialogShow"
      :approval-info="approvalInfo"
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
        approvalInfo: {
          showAllOption: false,
          result: true,
          approvalList: [],
        },
        isExportDialogShow: false,
        isApprovalDialogShow: false,
        // 批量审批选中单
        selectedList: [],
      };
    },
    methods: {
      // 批量审批
      onBatchApprovalClick() {
        this.isApprovalDialogShow = true;
        this.approvalInfo = {
          result: true,
          showAllOption: true,
          approvalList: this.selectedList.map(item => ({ ticket_id: item.id })),
        };
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
      onOpenApprovalDialog(id, result) {
        this.isApprovalDialogShow = true;
        this.approvalInfo = {
          result,
          approvalList: [{ ticket_id: id }],
        };
      },
      onApprovalDialogHidden(result) {
        this.isApprovalDialogShow = false;
        this.approvalInfo = {
          result: true,
          showAllOption: false,
          approvalList: [],
        };
        if (result) {
          this.initData();
        }
      },
    },
  };
</script>
<style lang="scss" scoped>
    @import './ticketList.scss';
</style>
