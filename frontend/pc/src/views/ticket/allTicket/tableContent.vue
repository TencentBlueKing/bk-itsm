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
  <div class="all-ticket-table">
    <bk-table style="margin-top: 15px;"
      :data="allTicketList"
      :pagination="pagination"
      :size="setting.size"
      :row-style="getRowStyle"
      @sort-change="orderingClick"
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
                data-test-id="ticket_popover_unfollow"
                class="bk-itsm-icon icon-rate"
                @click="onChangeAttention(row)"></i>
              <i
                data-test-id="ticket_popover_follow"
                class="bk-itsm-icon icon-favorite"
                :class="{ 'is-attention': row.hasAttention }"
                @click="onChangeAttention(row)"></i>
            </div>
          </bk-popover>
        </template>
      </bk-table-column>
      <bk-table-column
        data-test-id="ticket_table_render"
        v-for="field in setting.selectedFields"
        :key="field.id"
        :label="field.label"
        :width="field.width"
        :min-width="field.minWidth"
        :render-header="$renderHeader"
        :show-overflow-tooltip="true"
        :sortable="field.sortable"
        :prop="field.prop">
        <div slot-scope="{ row }">
          <!-- 单号 -->
          <template v-if="field.id === 'id'">
            <column-sn :row="row" :from="from"></column-sn>
          </template>
          <!-- 类型 -->
          <template v-else-if="field.id === 'type'">
            <span :title="getServerType(row.service_type)">
              {{getServerType(row.service_type)}}
            </span>
          </template>
          <!-- 优先级 -->
          <template v-else-if="field.id === 'priority'">
            <span class="bk-priority-button" :style="priorityColor(row)">
              {{ row.priority_name || '--' }}
            </span>
          </template>
          <!-- 状态 -->
          <template v-else-if="field.id === 'status'">
            <span :title="row.current_status_display"
              class="bk-status-color-info"
              :style="getstatusColor(row)">
              {{ row.current_status_display || '--' }}
            </span>
          </template>
          <!-- 当前步骤 -->
          <template v-else-if="field.id === 'current_steps'">
            <column-current-step :row="row"></column-current-step>
          </template>
          <!-- 操作 -->
          <template v-else-if="field.id === 'operate'">
            <template v-if="row.can_comment || row.can_operate">
              <bk-button v-if="row.can_comment"
                data-test-id="ticket_button_appraise"
                theme="primary"
                text
                @click="checkOne(row)">
                {{ $t('m.tickets["满意度评价"]') }}
              </bk-button>
              <router-link
                data-test-id="ticket_link_detail"
                v-if="row.can_operate"
                target="_blank"
                class="table-link"
                :to="{ name: 'TicketDetail', query: { id: row.id, project_id: row.project_key, from } }">
                {{ $t('m.tickets["处理"]') }}
              </router-link>
            </template>
            <template v-else>
              <router-link
                data-test-id="ticket_link_view_details "
                class="table-link"
                target="_blank"
                :to="{ name: 'TicketDetail', query: { id: row.id, project_id: row.project_key, from } }">
                {{ $t('m.tickets["查看"]') }}
              </router-link>
            </template>
          </template>
          <template v-else>
            <span :title="row[field.id]">{{ row[field.id] || '--' }}</span>
          </template>
        </div>
      </bk-table-column>

      <bk-table-column type="setting">
        <bk-table-setting-content
          data-test-id="ticket_table_setting"
          :fields="setting.fields"
          :selected="setting.selectedFields"
          :size="setting.size"
          @setting-change="handleSettingChange">
        </bk-table-setting-content>
      </bk-table-column>
      <div class="empty" slot="empty">
        <empty
          :is-error="listError"
          :is-search="searchToggle"
          @onRefresh="$parent.getAllTicketList()"
          @onClearSearch="$emit('clearSearch')">
        </empty>
      </div>
    </bk-table>
    <!-- 评价弹窗 -->
    <evaluation-ticket-modal
      ref="evaluationModal"
      :ticket-info="ticketInfo"
      @submitSuccess="evaluationSubmitSuccess">
    </evaluation-ticket-modal>
  </div>
</template>
<script>
  import ColumnSn from '@/components/ticket/table/ColumnSn';
  import ColumnCurrentStep from '@/components/ticket/table/ColumnCurrentStep';
  import EvaluationTicketModal from '@/components/ticket/evaluation/EvaluationTicketModal.vue';
  import Empty from '../../../components/common/Empty.vue';
  export default {
    name: 'allTicketTable',
    components: {
      ColumnSn,
      ColumnCurrentStep,
      EvaluationTicketModal,
      Empty,
    },
    props: {
      from: String,
      searchToggle: Boolean,
      listError: Boolean,
      pagination: {
        type: Object,
        default() {
          return {};
        },
      },
      dataList: {
        type: Array,
        default() {
          return [];
        },
      },
      // 状态颜色
      colorHexList: {
        type: Array,
        default() {
          return [];
        },
      },
      // 当前服务
      // serviceType
      serviceType: {
        type: String,
        default: '',
      },
    },
    data() {
      return {
        priorityColors: ['#A4AAB3', '#FFB848', '#FF5656'],
        allTicketList: [],
        setting: {
          fields: [],
          selectedFields: [],
          size: 'medium',
        },
        ticketInfo: {},
      };
    },
    computed: {
      choiceTypeList() {
        return this.$store.state.choice_type_list;
      },
      openFunction() {
        return this.$store.state.openFunction;
      },
      currTabSettingCache() {
        this.$store.commit('ticket/getTicketSettingformLocalStorage');
        return this.$store.state.ticket.settingCache[`all_${this.serviceType}`];
      },
    },
    watch: {
      dataList: {
        handler(val) {
          this.allTicketList = val.map((item) => {
            const attention = (item.followers || []).some(name => name === window.username);
            this.$set(item, 'hasAttention', attention);
            return item;
          });
        },
        immediate: true,
      },
    },
    async mounted() {
      this.getFields();
    },
    methods: {
      // 获取当前视图表格头显示字段
      getFields() {
        let defaultColumn = ['id', 'title', 'service_name', 'current_processors', 'create_at', 'creator', 'operate', 'status'];
        const allColumn = [
          { id: 'id', label: this.$t('m.tickets[\'单号\']'), width: '200', disabled: true, prop: 'sn' },
          { id: 'title', label: this.$t('m.tickets[\'标题\']'), minWidth: '180', prop: 'title' },
          { id: 'service_name', label: this.$t('m.tickets[\'服务\']'), minWidth: '140', prop: 'service_name' },
          { id: 'type', label: this.$t('m.manageCommon[\'类型\']'), minWidth: '80' },
          { id: 'priority', label: this.$t('m.slaContent[\'优先级\']'), minWidth: '100', sortable: 'custom', prop: 'priority' },
          { id: 'current_steps', label: this.$t('m.newCommon[\'当前步骤\']'), minWidth: '100', prop: 'current_steps' },
          { id: 'current_processors', label: this.$t('m.tickets[\'当前处理人\']'), minWidth: '140', prop: 'current_processors' },
          { id: 'status', label: this.$t('m.manageCommon[\'状态\']'), minWidth: '120', sortable: 'custom', prop: 'status' },
          { id: 'create_at', label: this.$t('m.tickets[\'提单时间\']'), minWidth: '160', sortable: 'custom', prop: 'create_at' },
          { id: 'creator', label: this.$t('m.tickets[\'提单人\']'), minWidth: '100', prop: 'creator' },
          { id: 'operate', label: this.$t('m.manageCommon[\'操作\']'), width: '120' },
        ];
        // 表格设置有缓存，使用缓存数据
        if (this.currTabSettingCache) {
          const { fields, size } = this.currTabSettingCache;
          defaultColumn = fields;
          this.setting.size = size;
        }
        const list = allColumn.filter((column) => {
          // sla 开关关闭
          if (!this.openFunction.SLA_SWITCH && column.id === 'priority') {
            return false;
          }
          return true;
        });
        this.setting.fields = list.slice(0);
        this.setting.selectedFields = list.slice(0).filter(m => defaultColumn.includes(m.id));
      },
      // 满意度评价
      checkOne(rowData) {
        this.$refs.evaluationModal.show();
        this.ticketInfo = rowData;
      },
      // 获取表格服务类型
      getServerType(type) {
        const choice = this.choiceTypeList.find(choice => choice.key === type);
        return choice ? choice.name : '--';
      },
      // 设置表优先级态样式
      priorityColor(row) {
        let priorityIndex = 1;
        if (row.meta.priority) {
          priorityIndex = row.meta.priority.key > 3 ? 3 : Number(row.meta.priority.key);
        }
        return row.priority_name === '--' ? {
          background: 'none',
          color: '#424950',
        } : { backgroundColor: this.priorityColors[priorityIndex - 1] };
      },
      // 设置表格状态样式
      getstatusColor(row) {
        const statusColor = this.colorHexList.filter(item => item.service_type === row.service_type && item.key === row.current_status);
        return statusColor.length
          ? { color: statusColor[0].color_hex, border: `1px solid ${statusColor[0].color_hex}` }
          : { color: '#3c96ff', border: '1px solid #3c96ff' };
      },
      // 排序功能
      orderingClick(value) {
        let order = '';
        switch (value.prop) {
          case 'priority':
            order = 'priority_order';
            break;
          case 'status':
            order = 'current_status_order';
            break;
          case 'create_at':
            order = 'create_at';
            break;
          case 'service_name':
            order = 'service_name';
            break;
          case 'current_steps':
            order = 'current_steps';
            break;
          case 'current_processors':
            order = 'current_processors';
            break;
          case 'creator':
            order = 'creator';
            break;
          default:
            return;
        }
        if (value.order === 'descending') {
          order = `-${order}`;
        }
        this.$emit('orderingClick', order || '-create_at');
      },
      // 添加关注/取消关注
      onChangeAttention(row) {
        const { id } = row;
        const params = {
          attention: !row.hasAttention,
        };
        let bkMessage = '';
        this.$store.dispatch('deployOrder/setAttention', { params, id }).then(() => {
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
            this.$bkMessage({
              message: res.data.msg,
              theme: 'error',
              ellipsisLine: 0,
            });
          });
      },
      // 评价回调
      evaluationSubmitSuccess() {
        this.$emit('submitSuccess');
      },
      // 分页过滤数据
      handlePageLimitChange(limit) {
        this.$emit('handlePageLimitChange', limit);
      },
      // 页容量过滤数据
      handlePageChange(page) {
        this.$emit('handlePageChange', page);
      },
      // 表格更多列设置变化
      handleSettingChange({ fields, size }) {
        this.setting.size = size;
        this.setting.selectedFields = fields;
        const fieldIds = fields.map(m => m.id);
        this.$store.commit('ticket/setSettingCache', {
          type: `all_${this.serviceType}`,
          value: { fields: fieldIds, size },
        });
        this.$store.commit('ticket/setTicketSettingToLocalStorage');
      },
      getRowStyle({ row }) {
        return `background-color: ${row.sla_color}`;
      },
    },
  };
</script>
<style lang="scss" scoped>
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
    .bk-priority-button {
        margin-top: 3px;
        min-width: 52px;
        width: auto;
        padding: 2px 4px;
        display: inline-block;
        text-align: center;
        line-height: 18px;
        border-radius: 2px;
        background-color: #EA3536;
        color: rgba(255, 255, 255, 1);
        max-width: 80px;
        text-overflow: ellipsis;
        white-space: nowrap;
        overflow: hidden;
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
    .current-steps-wrap /deep/ {
         .bk-tooltip, .bk-tooltip-ref {
            width: 100%;
        }
    }
    .bk-current-step {
        width: 100%;
        padding: 0 4px;
        display: inline-block;
        border: 1px solid #DCDEE5;
        height: 22px;
        line-height: 20px;
        border-radius: 2px;
        background-color: #FAFBFD;
        text-align: center;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        &.auto-width {
            margin-right: 5px;
            color: #424950;
            white-space:nowrap;
            width: auto;
        }
    }
    .table-link {
        color: #3a84ff;
        padding: 0 5px;
    }
    /deep/ .bk-table-pagination-wrapper {
        background-color: #fff;
    }
</style>
