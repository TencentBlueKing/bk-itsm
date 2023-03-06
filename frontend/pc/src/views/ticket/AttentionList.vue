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
  <div class="Attention-list-wrap ticket-table-wrap">
    <div class="table-wrap">
      <advanced-search
        class="advanced-search"
        ref="advancedSearch"
        :forms="searchForms"
        :panel="type"
        :search-result-list="searchResultList"
        @search="handleSearch"
        @deteleSearchResult="deteleSearchResult"
        @clear="handleClearSearch"
        @formChange="handleSearchFormChange">
        <div class="slot-content">
          <bk-button
            class="export"
            :title="$t(`m.tickets['导出']`)"
            @click="isExportDialogShow = true">
            {{ $t('m.tickets["导出"]') }}
          </bk-button>
        </div>
      </advanced-search>
      <bk-table
        class="ticket-table"
        v-bkloading="{ isLoading: listLoading }"
        :data="ticketList"
        :pagination="pagination"
        :size="setting.size"
        :row-style="getRowStyle"
        @sort-change="onSortChange"
        @page-change="handlePageChange"
        @page-limit-change="handlePageLimitChange">
        <!-- 关注单据 -->
        <bk-table-column
          prop="remind_btn"
          width="30">
          <template slot-scope="{ row }">
            <bk-popover :content="!row.hasAttention ? $t(`m.manageCommon['关注单据']`) : $t(`m.manageCommon['取消关注']`)"
              :interactive="false"
              placement="top">
              <div class="attention-icon">
                <i
                  class="bk-itsm-icon icon-rate"
                  @click="onChangeAttention(row)"></i>
                <i
                  class="bk-itsm-icon icon-favorite"
                  :class="{ 'is-attention': row.hasAttention }"
                  @click="onChangeAttention(row)"></i>
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
          :render-header="$renderHeader"
          :show-overflow-tooltip="true"
          :sortable="field.sortable"
          :prop="field.prop">
          <template slot-scope="props">
            <!-- 单号 -->
            <column-sn v-if="field.id === 'id'" :from="from" :row="props.row"></column-sn>
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
              <bk-link v-if="props.row.can_comment"
                class="table-link mr10"
                theme="primary"
                @click="onOpenEvaluationTicketModal(props.row)">
                {{ $t('m.manageCommon["满意度评价"]') }}
              </bk-link>
              <router-link
                v-else
                target="_blank"
                class="table-link mr10"
                :to="{ name: 'TicketDetail', query: { id: props.row.id, project_id: props.row.project_key, from } }">
                {{ props.row.can_operate ? $t(`m.manageCommon['处理']`) : $t('m.manageCommon["查看"]') }}
              </router-link>
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
          <empty
            :is-error="listError"
            :is-search="searchToggle"
            @onRefresh="getTicketList()"
            @onClearSearch="$refs.advancedSearch.onClearClick()">
          </empty>
        </div>
      </bk-table>
    </div>
    <!-- 评价弹窗 -->
    <evaluation-ticket-modal
      ref="evaluationModal"
      :ticket-info="evaluationTicketInfo"
      @submitSuccess="getTicketList">
    </evaluation-ticket-modal>
    <!-- 导出 -->
    <export-ticket-dialog
      view-type="my_attention"
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
  import EvaluationTicketModal from '@/components/ticket/evaluation/EvaluationTicketModal.vue';
  import i18n from '@/i18n/index.js';
  import ticketListMixins from './ticketListMixins.js';
  import Empty from '../../components/common/Empty.vue';

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
    name: 'AttentionList',
    components: {
      AdvancedSearch,
      ExportTicketDialog,
      EvaluationTicketModal,
      Empty,
    },
    mixins: [ticketListMixins],
    props: {
      from: String,
    },
    data() {
      const columnList = COLUMN_LIST.filter(column => this.$store.state.openFunction.SLA_SWITCH || column.id !== 'priority');
      return {
        columnList,
        type: 'attention',
        isExportDialogShow: false,
        // 评价
        evaluationTicketInfo: {},
      };
    },
    methods: {
      // 打开满意度评价
      onOpenEvaluationTicketModal(row) {
        this.$refs.evaluationModal.show();
        this.evaluationTicketInfo = row;
      },
    },
  };
</script>
<style lang="scss" scoped>
    @import './ticketList.scss';
</style>
