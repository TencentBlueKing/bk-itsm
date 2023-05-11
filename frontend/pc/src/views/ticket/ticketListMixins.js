/*
 * Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 * BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
 *
 * License for BK-ITSM 蓝鲸流程服务:
 * --------------------------------------------------------------------
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
 * LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
 * NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
 */

import ColumnCurrentStep from '@/components/ticket/table/ColumnCurrentStep.vue';
import ColumnSn from '@/components/ticket/table/ColumnSn.vue';
import { errorHandler } from '@/utils/errorHandler';
import { deepClone } from '@/utils/util';
import i18n from '@/i18n/index.js';

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
    name: i18n.t('m["项目"]'),
    desc: i18n.t('m["项目"]'),
    type: 'select',
    key: 'project_key',
    display: true,
    value: '',
    list: [],
    placeholder: i18n.t('m["请选择项目"]'),
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
    display: false,
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

const ticketListMixins = {
  components: {
    ColumnCurrentStep,
    ColumnSn,
  },
  props: {
    serviceId: [Number, String],
  },
  data() {
    return {
      searchForms: deepClone(SEARCH_FORMS),
      ticketList: [],
      setting: {
        fields: [],
        selectedFields: [],
        size: 'medium',
      },
      lastSearchParams: {}, // 搜索参数
      orderKey: '-create_at', // 排序参数
      colorHexList: [],
      pagination: {
        current: 1,
        count: 10,
        limit: 10,
      },
      listLoading: false,
      searchResultList: {
        todo: [],
        approval: [],
        attention: [],
        created: [],
      },
      approvalInfo: {
        showAllOption: false,
        result: true,
        approvalList: [],
      },
      isApprovalDialogShow: false,
      listError: false,
      searchToggle: false,
    };
  },
  computed: {
    openFunction() {
      return this.$store.state.openFunction;
    },
    currTabSettingCache() {
      this.$store.commit('ticket/getTicketSettingformLocalStorage');
      return this.$store.state.ticket.settingCache[this.type];
    },
  },
  watch: {
    type(newVal, oldVal) {
      const defaultType = ['event', 'change', 'request', 'question'];
      if (newVal !== oldVal && defaultType.includes(newVal)) {
        this.getTypeStatus();
      }
    },
  },
  created() {
    this.getTypeStatus();
    this.initData();
  },
  methods: {
    initData() {
      let defaultFields = ['id', 'title', 'service_name', 'current_steps', 'current_processors', 'create_at', 'creator', 'operate', 'status'];
      // 表格设置有缓存，使用缓存数据
      if (this.currTabSettingCache) {
        const { fields, size } = this.currTabSettingCache;
        defaultFields = fields;
        this.setting.size = size;
      }
      this.setting.fields = this.columnList.slice(0);
      this.setting.selectedFields = this.columnList.slice(0).filter(m => defaultFields.includes(m.id));
      if (this.$route.query.project_id) this.searchForms[1].value = this.$route.query.project_id || '';
      this.getTicketList();
      this.getTicketStatusTypes();
      this.getBusinessList();
      this.getServiceTree();
    },
    // 获取单据所有状态分类列表
    getTicketStatusTypes() {
      const params = {
        source_uri: 'ticket_status',
      };
      this.$store.dispatch('ticketStatus/getOverallTicketStatuses', params).then((res) => {
        this.searchForms.find(item => item.key === 'current_status__in').list = res.data;
      })
        .catch((res) => {
          errorHandler(res, this);
        });
    },
    getBusinessList() {
      this.$store.dispatch('eventType/getAppList').then((res) => {
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
      this.$store.dispatch('serviceCatalog/getTreeData', params).then((res) => {
        const formItem = this.searchForms.find(item => item.key === 'catalog_id');
        formItem.list = res.data[0] ? res.data[0].children : [];
      })
        .catch((res) => {
          errorHandler(res, this);
        });
    },
    getServiceData(val) {
      const params = {
        catalog_id: val,
        is_valid: 1,
      };
      this.$store.dispatch('catalogService/getServices', params).then((res) => {
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
    // 获取单据列表
    getTicketList() {
      const searchParams = JSON.stringify(this.lastSearchParams) === '{}'
        ? { service_id__in: this.$route.query.service_id || undefined, project_key: this.$route.query.project_id || undefined } // 没有参数时默认将 url 参数作为查询参数
        : this.lastSearchParams;
      this.listLoading = true;
      this.listError = false;
      return this.$store.dispatch('change/getList', {
        page_size: this.pagination.limit,
        page: this.pagination.current,
        is_draft: 0,
        view_type: `my_${this.type}`,
        ordering: this.orderKey,
        ...searchParams,
      }).then((resp) => {
        if (resp.result) {
          this.ticketList = resp.data.items.map((item) => {
            const attention = (item.followers || []).some(name => name === window.username);

            this.$set(item, 'hasAttention', attention);
            this.$set(item, 'checkStatus', false);
            return item;
          });
          this.pagination.count = resp.data.count;
          // 异步加载列表中的某些字段信息
          this.asyncReplaceTicketListAttr(this.ticketList);
        }
      })
        .catch((res) => {
          this.listError = true;
          errorHandler(res, this);
        })
        .finally(() => {
          this.listLoading = false;
        });
    },
    // @param {Array} exclude 排除字段（不需要去加载的字段）
    /**
         * 异步加载列表中的某些字段信息
         * @param {Array} originList 单据列表
         */
    asyncReplaceTicketListAttr(originList) {
      if (originList.length === 0) {
        return;
      }
      this.getTicketsProcessors(originList);
      this.getTicketsCreator(originList);
      this.getTicketscanOperate(originList);
    },
    // 异步获取单据处理人
    getTicketsProcessors(originList) {
      const copyList = deepClone(originList);
      originList.forEach((ticket) => {
        this.$set(ticket, 'current_processors', '加载中...');
      });
      const ids = copyList.map(ticket => ticket.id);
      this.$store.dispatch('ticket/getTicketsProcessors', { ids: ids.toString() }).then((res) => {
        if (res.result && res.data) {
          originList.forEach((ticket, index) => {
            const replaceValue = Object.prototype.hasOwnProperty.call(res.data, ticket.id)
              ? res.data[ticket.id]
              : copyList[index].current_processors;
            this.$set(ticket, 'current_processors', replaceValue);
          });
        }
      })
        .catch((res) => {
          errorHandler(res, this);
        });
    },
    // 异步获取提单人
    getTicketsCreator(originList) {
      const copyList = deepClone(originList);
      originList.forEach((ticket) => {
        this.$set(ticket, 'creator', '加载中...');
      });
      const ids = copyList.map(ticket => ticket.id);
      this.$store.dispatch('ticket/getTicketsCreator', { ids: ids.toString() }).then((res) => {
        if (res.result && res.data) {
          originList.forEach((ticket, index) => {
            const replaceValue = Object.prototype.hasOwnProperty.call(res.data, copyList[index].creator)
              ? res.data[copyList[index].creator]
              : copyList[index].creator;
            this.$set(ticket, 'creator', replaceValue);
          });
        }
      })
        .catch((res) => {
          errorHandler(res, this);
        });
    },
    // 异步获取单据 can_operate
    getTicketscanOperate(originList) {
      const copyList = deepClone(originList);
      originList.forEach((ticket) => {
        // 开始是都不能操作
        this.$set(ticket, 'can_operate', false);
      });
      const ids = copyList.map(ticket => ticket.id);
      this.$store.dispatch('ticket/getTicketscanOperate', { ids: ids.toString() }).then((res) => {
        if (res.result && res.data) {
          originList.forEach((ticket) => {
            const replaceValue = Object.prototype.hasOwnProperty.call(res.data, ticket.id)
              ? res.data[ticket.id] : false;
            this.$set(ticket, 'can_operate', replaceValue);
          });
        }
      })
        .catch((res) => {
          errorHandler(res, this);
        });
    },
    getRowStyle({ row }) {
      return `background-color: ${row.sla_color}`;
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
    getPriorityColor(row) {
      const priorityList = ['#A4AAB3', '#FFB848', '#FF5656'];
      let priorityIndex = 1;
      if (row.meta.priority) {
        priorityIndex = row.meta.priority.key > 3 ? 3 : Number(row.meta.priority.key);
      }
      return row.priority_name === '--' ? {
        background: 'none',
        color: '#424950',
      } : { backgroundColor: priorityList[priorityIndex - 1] };
    },
    getstatusColor(row) {
      const statusColor = this.colorHexList.filter(item => item.service_type === row.service_type
                && item.key === row.current_status);
      return statusColor.length
        ? { color: statusColor[0].color_hex, border: `1px solid ${statusColor[0].color_hex}` }
        : { color: '#3c96ff', border: '1px solid #3c96ff' };
    },
    handleSearch(params, toggle) {
      this.lastSearchParams = params;
      this.searchToggle = true;
      this.getTicketList();
      if (Object.keys(params).length === 0 || !toggle) return;
      this.searchResultList[this.type].push(params);
    },
    deteleSearchResult(type, index) {
      this.searchResultList[type].splice(index, 1);
    },
    handleClearSearch() {
      this.searchForms.forEach((item) => {
        if (item.key === 'service_id__in') {
          item.display = false;
        }
      });
      this.searchToggle = false;
    },
    handleSearchFormChange(key, val) {
      // to do something
      if (key === 'catalog_id') {
        const formItem = this.searchForms.find(item => item.key === 'service_id__in');
        formItem.display = val.length;
        if (val.length) {
          const serviceCatalogId = val[val.length - 1];
          // 当服务目录的数据发生变化时，清空服务数据
          formItem.value = [];
          this.getServiceData(serviceCatalogId);
        }
      }
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
        type: this.type,
        value: { fields: fieldIds, size },
      });
      this.$store.commit('ticket/setTicketSettingToLocalStorage');
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
          errorHandler(res, this);
        });
    },
    onOpenApprovalDialog(id, result) {
      this.isBatch = false;
      this.isApprovalDialogShow = true;
      this.approvalInfo = {
        result,
        approvalList: [{ ticket_id: id }],
      };
    },
    onApprovalDialogHidden() {
      this.isApprovalDialogShow = false;
      this.approvalInfo = {
        result: true,
        showAllOption: false,
        approvalList: [],
      };
      // if (result) this.initData();
    },
  },
};

export default ticketListMixins;
