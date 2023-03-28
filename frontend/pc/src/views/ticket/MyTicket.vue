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
  <div
    class="my-ticket-page"
    v-bkloading="{ isLoading: tabLoading || countLoading }"
  >
    <nav-title :title-name="$t(`m.navigation['我的工单']`)">
      <bk-tab
        v-if="!countLoading"
        slot="tab"
        :active.sync="activePanel"
        type="unborder-card"
        @tab-change="handleTabChange"
      >
        <bk-tab-panel
          v-for="(panel, index) in panels"
          v-bind="panel"
          :key="index"
        >
          <template slot="label">
            <span class="panel-name">{{ panel.label }}</span>
            <span
              class="panel-count"
              v-if="
                tabCount[panel.name] ||
                  tabCount[panel.name] === 0
              "
            >
              {{ tabCount[panel.name] }}
            </span>
            <span
              class="red-dot"
              v-if="tabCount[panel.name]"
            ></span>
          </template>
        </bk-tab-panel>
      </bk-tab>
    </nav-title>
    <div class="table-wrap">
      <advanced-search
        class="advanced-search"
        ref="advancedSearch"
        :forms="searchForms"
        @search="handleSearch"
        @clear="handleClearSearch"
        @formChange="handleSearchFormChange"
      >
        <div class="slot-content">
          <bk-button
            class="export"
            :title="$t(`m.tickets['导出']`)"
            @click="openExportList"
          >
            {{ $t('m.tickets["导出"]') }}</bk-button
            >
          <bk-button
            v-if="activePanel === 'approval'"
            :theme="'default'"
            :title="$t(`m.managePage['批量审批']`)"
            class="mr10 plus-cus"
            :disabled="!selectedList.length"
            @click="onBatchApprovalClick"
          >
            {{ $t(`m.managePage['批量审批']`) }}
          </bk-button>
        </div>
      </advanced-search>
      <bk-table
        ref="ticketList"
        v-if="!tabLoading"
        class="ticket-table"
        :data="ticketList"
        :pagination="pagination"
        :size="setting.size"
        :row-style="getRowStyle"
        @sort-change="onSortChange"
        @page-change="handlePageChange"
        @page-limit-change="handlePageLimitChange"
        @select-all="handleSelectAll"
      >
        <bk-table-column
          v-if="activePanel === 'approval'"
          type="selection"
          width="60"
          :selectable="canSelected"
        >
          <template slot-scope="props">
            <bk-checkbox
              v-if="props.row.waiting_approve"
              v-model="props.row.checkStatus"
              @change="changeSelection(props.row)"
            >
            </bk-checkbox>
          </template>
        </bk-table-column>
        <!-- 关注单据 -->
        <bk-table-column prop="remind_btn" width="30">
          <template slot-scope="{ row }">
            <bk-popover
              :content="
                !row.hasAttention
                  ? $t(`m.manageCommon['关注单据']`)
                  : $t(`m.manageCommon['取消关注']`)
              "
              :interactive="false"
              placement="top"
            >
              <div class="attention-icon">
                <i
                  class="bk-itsm-icon icon-rate"
                  @click="onChangeAttention(row)"
                ></i>
                <i
                  class="bk-itsm-icon icon-favorite"
                  :class="{
                    'is-attention': row.hasAttention
                  }"
                  @click="onChangeAttention(row)"
                ></i>
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
          :prop="field.prop"
        >
          <template slot-scope="props">
            <!-- 单号 -->
            <column-sn
              v-if="field.id === 'id'"
              :row="props.row"
              :from="fromRouter"
            ></column-sn>
            <!-- 当前步骤 -->
            <column-current-step
              v-else-if="field.id === 'current_steps'"
              :row="props.row"
            ></column-current-step>
            <!-- 状态 -->
            <span
              v-else-if="field.id === 'status'"
              :title="props.row.current_status_display"
              class="bk-status-color-info"
              :style="getstatusColor(props.row)"
            >
              {{ props.row.current_status_display || "--" }}
            </span>
            <!-- 优先级 -->
            <span
              v-else-if="field.id === 'priority'"
              class="bk-priority-button"
              :style="getPriorityColor(props.row)"
            >
              {{ props.row.priority_name || "--" }}
            </span>
            <!-- 操作 -->
            <template v-else-if="field.id === 'operate'">
              <template v-if="activePanel === 'approval'">
                <bk-link
                  class="table-link mr10"
                  theme="primary"
                  @click="
                    onOpenApprovalDialog(props.row.id, true)
                  "
                >
                  {{ $t(`m.managePage['通过']`) }}
                </bk-link>
                <bk-link
                  class="table-link"
                  theme="primary"
                  @click="
                    onOpenApprovalDialog(
                      props.row.id,
                      false
                    )
                  "
                >
                  {{ $t(`m.manageCommon['拒绝']`) }}
                </bk-link>
              </template>
              <bk-link
                v-else-if="props.row.can_comment"
                class="table-link mr10"
                theme="primary"
                @click="onOpenEvaluationTicketModal(props.row)"
              >
                {{ $t('m.manageCommon["满意度评价"]') }}
              </bk-link>
              <router-link
                v-else
                target="_blank"
                class="table-link mr10"
                :to="{
                  name: 'TicketDetail',
                  query: {
                    id: props.row.id,
                    from: fromRouter
                  }
                }"
              >
                {{
                  props.row.can_operate
                    ? $t(`m.manageCommon['处理']`)
                    : $t('m.manageCommon["查看"]')
                }}
              </router-link>
              <!-- 重新提单，我的申请单中状态为已撤销出现 -->
              <bk-link
                v-if="
                  activePanel === 'created' &&
                    props.row.current_status === 'REVOKED'
                "
                class="table-link"
                theme="primary"
                @click="reCreateTicket(props.row)"
              >
                {{ $t('m.manageCommon["复制提单"]') }}
              </bk-link>
            </template>
            <!-- 其他 -->
            <span v-else :title="props.row[field.id]">{{
              props.row[field.id] || "--"
            }}</span>
          </template>
        </bk-table-column>
        <bk-table-column type="setting">
          <bk-table-setting-content
            :size="setting.size"
            :fields="setting.fields"
            :selected="setting.selectedFields"
            @setting-change="handleSettingChange"
          >
          </bk-table-setting-content>
        </bk-table-column>
      </bk-table>
    </div>
    <!-- 审批弹窗 -->
    <approval-dialog
      :is-show.sync="isApprovalDialogShow"
      :approval-info="approvalInfo"
      @cancel="onApprovalDialogHidden"
    >
    </approval-dialog>
    <!-- 评价弹窗 -->
    <evaluation-ticket-modal
      ref="evaluationModal"
      :ticket-info="evaluationTicketInfo"
      @submitSuccess="getTicketList"
    >
    </evaluation-ticket-modal>
    <!-- 导出 -->
    <export-ticket-dialog
      :is-show="isExportDialogShow"
      :pagination="pagination"
      :view-type="'my_' + activePanel"
      :search-params="lastSearchParams"
      @close="isExportDialogShow = false"
    >
    </export-ticket-dialog>
  </div>
</template>
<script>
  import i18n from '@/i18n/index.js';
  import { errorHandler } from '@/utils/errorHandler';
  import { deepClone } from '@/utils/util';
  import NavTitle from '@/components/common/layout/NavTitle';
  import ColumnCurrentStep from '@/components/ticket/table/ColumnCurrentStep.vue';
  import ColumnSn from '@/components/ticket/table/ColumnSn.vue';
  import ApprovalDialog from '@/components/ticket/ApprovalDialog.vue';
  import ExportTicketDialog from '@/components/ticket/ExportTicketDialog.vue';
  import AdvancedSearch from '@/components/form/advancedSearch/NewAdvancedSearch';
  import EvaluationTicketModal from '@/components/ticket/evaluation/EvaluationTicketModal.vue';
  import ticketListMixins from '@/mixins/ticketList.js';

  const PANELS = [
    {
      name: 'todo',
      label: i18n.t('m.tickets[\'我的待办\']'),
    },
    {
      name: 'approval',
      label: i18n.t('m.tickets[\'待我审批\']'),
    },
    {
      name: 'created',
      label: i18n.t('m.tickets[\'我的申请\']'),
    },
    {
      name: 'attention',
      label: i18n.t('m.tickets[\'我的关注\']'),
    },
    {
      name: 'history',
      label: i18n.t('m.tickets[\'我的历史\']'),
    },
  ];
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
      minWidth: '180',
    },
    {
      id: 'service_name',
      label: i18n.t('m.home[\'服务\']'),
      minWidth: '140',
      prop: 'service_name',
    },
    {
      id: 'service_type_name',
      label: i18n.t('m.manageCommon[\'类型\']'),
      minWidth: '80',
    },
    {
      id: 'priority',
      label: i18n.t('m.slaContent[\'优先级\']'),
      minWidth: '120',
      sortable: 'custom',
      prop: 'priority_name',
    },
    {
      id: 'current_steps',
      label: i18n.t('m.newCommon[\'当前步骤\']'),
      minWidth: '80',
      prop: 'current_steps',
    },
    {
      id: 'current_processors',
      label: i18n.t('m.manageCommon[\'当前处理人\']'),
      width: '130',
      prop: 'current_processors',
    },
    {
      id: 'status',
      label: i18n.t('m.manageCommon[\'状态\']'),
      minWidth: '120',
      sortable: 'custom',
      prop: 'status',
    },
    {
      id: 'create_at',
      label: i18n.t('m.manageCommon[\'提单时间\']'),
      minWidth: '140',
      sortable: 'custom',
      prop: 'create_at',
    },
    {
      id: 'creator',
      label: i18n.t('m.manageCommon[\'提单人\']'),
      minWidth: '140',
      prop: 'creator',
    },
    {
      id: 'operate',
      label: i18n.t('m.manageCommon[\'操作\']'),
      minWidth: '80',
    },
  ];
  const SEARCH_FORMS = [
    {
      name: i18n.t('m.tickets[\'单号/标题\']'),
      desc: i18n.t('m.tickets[\'单号/标题\']'),
      type: 'input',
      key: 'keyword',
      display: true,
      value: '',
      list: [],
      placeholder: i18n.t('m.tickets["请选择单号/标题"]'),
    },
    {
      name: i18n.t('m.tickets["服务目录"]'),
      type: 'cascade',
      key: 'catalog_id',
      multiSelect: true,
      display: true,
      value: [],
      list: [],
      placeholder: i18n.t('m.tickets["请选择服务目录"]'),
    },
    {
      name: i18n.t('m.tickets["服务"]'),
      type: 'select',
      key: 'service_id__in',
      multiSelect: true,
      display: true,
      value: [],
      list: [],
      placeholder: i18n.t('m.tickets["请选择服务"]'),
    },
    {
      name: i18n.t('m.tickets["提单人"]'),
      type: 'member',
      key: 'creator__in',
      multiSelect: true,
      display: true,
      value: [],
      list: [],
      placeholder: i18n.t('m.tickets["请选择提单人"]'),
    },
    {
      name: i18n.t('m.tickets["处理人"]'),
      type: 'member',
      key: 'current_processor',
      multiSelect: true,
      display: true,
      value: [],
      list: [],
      placeholder: i18n.t('m.tickets["请选择处理人"]'),
    },
    {
      name: i18n.t('m.tickets["状态"]'),
      type: 'select',
      key: 'current_status__in',
      multiSelect: true,
      display: true,
      value: [],
      list: [],
      placeholder: i18n.t('m.tickets["请选择状态"]'),
    },
    {
      name: i18n.t('m.tickets["提单时间"]'),
      key: 'date_update',
      type: 'datetime',
      display: true,
      value: [],
      list: [],
      placeholder: i18n.t('m.tickets["请选择提单时间"]'),
    },
    {
      name: i18n.t('m.tickets["业务"]'),
      key: 'bk_biz_id',
      type: 'select',
      display: true,
      value: '',
      list: [],
      placeholder: i18n.t('m.tickets["请选择业务"]'),
    },
  ];
  export default {
    name: 'MyTicket',
    components: {
      ColumnSn,
      ColumnCurrentStep,
      NavTitle,
      ApprovalDialog,
      AdvancedSearch,
      EvaluationTicketModal,
      ExportTicketDialog,
    },
    mixins: [ticketListMixins],
    data() {
      return {
        panels: PANELS,
        searchForms: [],
        isExportDialogShow: false,
        isApprovalDialogShow: false,
        approvalInfo: {
          showAllOption: false,
          result: true,
          approvalList: [],
        },
        colorHexList: [],
        ticketList: [],
        activePanel: 'todo',
        tabLoading: false,
        tabCount: {
          todo: 0,
          approval: 0,
        },
        countLoading: false,
        pagination: {
          current: 1,
          count: 10,
          limit: 10,
        },
        setting: {
          fields: [],
          selectedFields: [],
          size: 'medium',
        },
        lastSearchParams: {}, // 搜索参数
        orderKey: '-create_at', // 排序参数
        // 批量审批选中单
        selectedList: [],
        // 评价
        evaluationTicketInfo: {},
      };
    },
    computed: {
      openFunction() {
        return this.$store.state.openFunction;
      },
      currTabSettingCache() {
        return this.$store.state.ticket.settingCache[this.activePanel];
      },
      fromRouter() {
        return `${this.$route.name}_${this.$route.params.type}`;
      },
    },
    watch: {
      $route() {
        this.pagination = {
          current: 1,
          count: 10,
          limit: 10,
        };
        this.lastSearchParams = {};
        this.orderKey = '-create_at';
        if (this.$refs.advancedSearch) {
          this.$refs.advancedSearch.showMore = false;
        }
        this.initData();
      },
    },
    created() {
      this.initData();
    },
    methods: {
      initData() {
        let defaultFields = [
          'id',
          'title',
          'service_name',
          'current_steps',
          'current_processors',
          'create_at',
          'creator',
          'operate',
        ];
        // 表格设置有缓存，使用缓存数据
        if (this.currTabSettingCache) {
          const { fields, size } = this.currTabSettingCache;
          defaultFields = fields;
          this.setting.size = size;
        }
        // 我的待办去掉处理人，我的申请单去掉提单人,优先级（SLA_SWITCH）
        const columnList = COLUMN_LIST.filter((column) => {
          if (
            (this.activePanel === 'created'
            && column.id === 'creator')
            || (!this.openFunction.SLA_SWITCH && column.id === 'priority')
          ) {
            return false;
          }
          return true;
        });
        this.setting.fields = columnList.slice(0);
        this.setting.selectedFields = columnList
          .slice(0)
          .filter(m => defaultFields.includes(m.id));

        this.activePanel = this.$route.params.type;
        this.getTicketList();
        this.getTicketsCount();
        // 高级搜索
        this.searchForms = deepClone(SEARCH_FORMS);
        this.getTicketStatusTypes();
        this.getTypeStatus();
        this.getBusinessList();
        this.getServiceTree();
      },
      // 获取单据列表
      getTicketList() {
        const { type } = this.$route.params;
        const searchParams = JSON.stringify(this.lastSearchParams) === '{}'
          ? { service_id__in: this.$route.query.service_id } // 没有参数时默认将 url 参数作为查询参数
          : this.lastSearchParams;
        this.tabLoading = true;
        return this.$store
          .dispatch('change/getList', {
            page_size: this.pagination.limit,
            page: this.pagination.current,
            is_draft: 0,
            view_type: `my_${type}`,
            ordering: this.orderKey,
            ...searchParams,
          })
          .then((resp) => {
            if (resp.result) {
              this.ticketList = resp.data.items.map((item) => {
                const attention = (item.followers || []).some(name => name === window.username);

                this.$set(item, 'hasAttention', attention);
                this.$set(item, 'checkStatus', false);
                return item;
              });
              if (['todo', 'approval'].includes(type)) {
                this.$set(this.tabCount, type, resp.data.count);
              }
              this.pagination.count = resp.data.count;
              this.reloadCount();
              // 异步加载列表中的某些字段信息
              this.__asyncReplaceTicketListAttr(this.ticketList);
            }
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.tabLoading = false;
          });
      },
      // 获取单据数量（待办、审批）
      getTicketsCount() {
        this.countLoading = true;
        this.$store
          .dispatch('ticket/getTicketsCount')
          .then((res) => {
            const { data } = res;
            if (data.my_approval) {
              this.tabCount.approval = data.my_approval;
            }
            if (data.my_todo) {
              this.tabCount.todo = data.my_todo;
            }
          })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 获取单据所有状态分类列表
      getTicketStatusTypes() {
        const params = {
          source_uri: 'ticket_status',
        };
        this.$store
          .dispatch('ticketStatus/getOverallTicketStatuses', params)
          .then((res) => {
            this.searchForms.find(item => item.key === 'current_status__in').list = res.data;
          })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 获取状态颜色接口
      getTypeStatus() {
        const params = {};
        const type = '';
        this.$store
          .dispatch('ticketStatus/getTypeStatus', { type, params })
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
            this.searchForms.find(item => item.key === 'bk_biz_id').list = res.data;
          })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 查询级联数据
      getServiceTree() {
        const params = {
          show_deleted: true,
        };
        this.$store
          .dispatch('serviceCatalog/getTreeData', params)
          .then((res) => {
            const formItem = this.searchForms.find(item => item.key === 'catalog_id');
            formItem.list = res.data[0] ? res.data[0].children : [];
          })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      getstatusColor(row) {
        const statusColor = this.colorHexList.filter(item => item.service_type === row.service_type
          && item.key === row.current_status);
        return statusColor.length
          ? {
            color: statusColor[0].color_hex,
            border: `1px solid ${statusColor[0].color_hex}`,
          }
          : { color: '#3c96ff', border: '1px solid #3c96ff' };
      },
      // 获取服务数据
      getServiceData(val) {
        const params = {
          catalog_id: val,
          is_valid: 1,
        };
        this.$store
          .dispatch('catalogService/getServices', params)
          .then((res) => {
            const formItem = this.searchForms.find(item => item.key === 'service_id__in');
            formItem.list = [];
            res.data.forEach((item) => {
              formItem.list.push({
                key: item.id,
                name: item.name,
              });
            });
          })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      getPriorityColor(row) {
        const priorityList = ['#A4AAB3', '#FFB848', '#FF5656'];
        let priorityIndex = 1;
        if (row.meta.priority) {
          priorityIndex =                    row.meta.priority.key > 3
            ? 3
            : Number(row.meta.priority.key);
        }
        return row.priority_name === '--'
          ? {
            background: 'none',
            color: '#424950',
          }
          : { backgroundColor: priorityList[priorityIndex - 1] };
      },
      reloadCount() {
        this.countLoading = true;
        setTimeout(() => {
          this.countLoading = false;
        });
      },
      // 复制参数重新提单
      reCreateTicket(row) {
        const { href } = this.$router.resolve({
          name: 'CreateTicket',
          query: {
            from: this.fromRouter,
            service_id: row.service_id,
            rc_ticket_id: row.id,
          },
        });
        window.open(href, '_blank');
      },
      handleTabChange(name) {
        this.$router.push({
          name: 'MyTicket',
          params: {
            type: name,
          },
        });
      },
      // 优先级、提单时间、状态添加排序
      onSortChange(value) {
        const sortKetMap = {
          priority_name: 'priority_order',
          status: 'current_status_order',
          create_at: 'create_at',
        };
        let order = sortKetMap[value.prop];
        if (value.order === 'descending') {
          order = `-${order}`;
        }
        this.orderKey = order;
        this.getTicketList();
      },
      handlePageChange(page) {
        this.pagination.current = page;
        this.getTicketList();
      },
      handlePageLimitChange(limit) {
        this.pagination.current = 1;
        this.pagination.limit = limit;
        this.getTicketList();
      },
      handleSettingChange({ fields, size }) {
        this.setting.size = size;
        this.setting.selectedFields = fields;
        const fieldIds = fields.map(m => m.id);
        this.$store.commit('ticket/setSettingCache', {
          type: this.activePanel,
          value: { fields: fieldIds, size },
        });
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
      // 批量审批
      onBatchApprovalClick() {
        this.isApprovalDialogShow = true;
        this.approvalInfo = {
          result: true,
          showAllOption: true,
          approvalList: this.selectedList.map(item => ({
            ticket_id: item.id,
          })),
        };
      },
      handleSearch(params) {
        this.lastSearchParams = params;
        this.getTicketList();
      },
      handleClearSearch() {
        this.searchForms.forEach((item) => {
          if (item.key === 'service_id__in') {
            item.display = false;
          }
        });
      },
      handleSearchFormChange(key, val) {
        // to do something
        if (key === 'catalog_id') {
          const formItem = this.searchForms.find(item => item.key === 'service_id__in');
          formItem.display = val.length;
          if (val.length) {
            const serviceCatalogId = val[val.length - 1].id;
            // 当服务目录的数据发生变化时，清空服务数据
            formItem.value = [];
            this.getServiceData(serviceCatalogId);
          }
        }
      },
      openExportList() {
        this.isExportDialogShow = true;
      },
      // 添加关注/取消关注
      onChangeAttention(row) {
        const { id } = row;
        const params = {
          attention: !row.hasAttention,
        };
        let bkMessage = '';
        this.$store
          .dispatch('deployOrder/setAttention', { params, id })
          .then(() => {
            if (row.hasAttention) {
              row.hasAttention = false;
              bkMessage = this.$t('m.manageCommon[\'取消关注成功~\']');
            } else {
              row.hasAttention = true;
              bkMessage = this.$t('m.manageCommon[\'添加关注成功~\']');
            }
            this.$bkMessage({
              message: bkMessage,
              theme: 'success',
              ellipsisLine: 0,
            });
          })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 清空已选列表
      clearSelectedList() {
        this.selectedList = [];
      },
      // 全选 半选
      handleSelectAll(selection) {
        this.ticketList.forEach((item) => {
          item.checkStatus = !!selection.length;
        });
        this.selectedList = selection;
      },
      handleSelect(selection) {
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
      // 可以选中
      canSelected(row) {
        return row.waiting_approve;
      },
      // 打开满意度评价
      onOpenEvaluationTicketModal(row) {
        this.$refs.evaluationModal.show();
        this.evaluationTicketInfo = row;
      },
      getRowStyle({ row }) {
        return `background-color: ${row.sla_color}`;
      },
    },
  };
</script>

<style lang="scss" scoped>
@import "../../scss/mixins/scroller.scss";
.my-ticket-page {
    min-height: 400px;
    /deep/ .bk-tab-section {
        padding: 0;
    }
}
.table-wrap {
    padding: 14px 18px 15px 22px;
    height: calc(100vh - 146px);
    overflow: auto;
    @include scroller;
    .advanced-search {
        .export {
            width: 86px;
        }
    }
    .ticket-table {
        margin-top: 15px;
        background: #ffffff;
    }
}

.table-link {
    color: #3a84ff;
    vertical-align: baseline;
    /deep/ .bk-link-text {
        font-size: 12px;
    }
}
/deep/ .bk-tab-label-item {
    .panel-name,
    .panel-count {
        display: inline-block;
        vertical-align: middle;
        margin: 0 3px;
    }
    .panel-count {
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
    &.active {
        .panel-count {
            background: #e1ecff;
            color: #3a84ff;
        }
    }
    .red-dot {
        position: absolute;
        top: 6px;
        right: 20px;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #ea3536;
    }
}
.bk-status-color-info {
    margin-top: 3px;
    padding: 0 6px;
    display: inline-block;
    text-align: center;
    color: #3c96ff;
    border-radius: 2px;
    border: 1px solid #3c96ff;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
    height: 22px;
    line-height: 20px;
}
.bk-priority-button {
    margin-top: 3px;
    min-width: 52px;
    width: auto;
    padding: 2px 4px;
    display: inline-block;
    text-align: center;
    line-height: 18px;
    border-radius: 2px;
    background-color: #ea3536;
    color: rgba(255, 255, 255, 1);
    max-width: 80px;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
}
// 关注
.bk-table-row {
    &.hover-row {
        .icon-rate {
            display: block;
        }
    }
}
.attention-icon {
    position: relative;
    height: 16px;
    width: 16px;
    &:hover {
        .icon-favorite {
            display: block;
            color: #ffb848;
        }
    }
    .bk-itsm-icon {
        position: absolute;
        font-size: 16px;
        cursor: pointer;
    }
    .icon-rate {
        z-index: 9;
        display: none;
        color: #979ba5;
    }
    .icon-favorite {
        z-index: 10;
        display: none;
        color: #fe9c00;
        &.is-attention {
            display: block;
        }
    }
}
/deep/ .bk-tab-label-item {
    border-bottom: 2px solid #3a84ff;
}
</style>
