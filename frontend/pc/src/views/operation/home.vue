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
  <div class="operation-home" ref="operationHome">
    <div class="date-selector" :class="{ 'selector-fixed': isDateSelectorFixed }">
      <bk-date-picker
        type="daterange"
        :clearable="false"
        :shortcuts="shortcuts"
        :value="dateRange"
        @change="onSelectDate">
      </bk-date-picker>
    </div>
    <div class="summary-data statistics-section" v-bkloading="{ isLoading: loading.summary, opacity: 1 }">
      <summary-card
        :title="$t(`m.operation['单据总数']`)"
        :card-data="{ total: summaryData.total.count, week: summaryData.week.ticket }">
        <i class="bk-icon icon-order-shape" slot="icon"></i>
      </summary-card>
      <summary-card
        :title="$t(`m.operation['服务总数']`)"
        :card-data="{ total: summaryData.total.service_count, week: summaryData.week.service }">
        <i class="bk-icon icon-heart-shape" slot="icon"></i>
      </summary-card>
      <summary-card
        :title="$t(`m.operation['业务总数']`)"
        :card-data="{ total: summaryData.total.biz_count, week: summaryData.week.biz }">
        <i class="bk-icon icon-folder-open-shape" slot="icon"></i>
      </summary-card>
      <summary-card
        :title="$t(`m.operation['用户总数']`)"
        :card-data="{ total: summaryData.total.user_count, week: summaryData.week.user }">
        <i class="bk-icon icon-user-shape" slot="icon"></i>
      </summary-card>
    </div>
    <div class="global-statistics statistics-section">
      <h4>{{ $t(`m.operation['全局统计']`) }}</h4>
      <div class="charts-wrap">
        <chart-card
          style="height: 568px;"
          :title="$t(`m.operation['服务使用统计']`)"
          :show-search="!loading.bizList"
          :placeholder="$t(`m.operation['请输入服务名称']`)"
          :loading="loading.serviceUse"
          @search="handleServiceSearch"
          @clear="handleServiceClear">
          <table-chart
            :show-pagination="true"
            :pagination="serviceTablePagination"
            :columns="serviceTableColumns"
            :chart-data="serviceUseData"
            :list-error="searchAndErrorToggles.service.error"
            :search-toggle="searchAndErrorToggles.service.search"
            @clearSearch="handleServiceClear"
            @onPageChange="onServiceTablePageChange"
            @onOrderChange="onServiceTableOrderChange">
          </table-chart>
        </chart-card>
        <chart-card
          style="height: 568px;"
          :title="$t(`m.operation['业务使用统计']`)"
          :desc="$t(`m.operation['按照业务维度，统计业务的单量以及服务使用量。']`)"
          :placeholder="$t(`m.operation['请输入业务名称']`)"
          :show-search="true"
          :loading="loading.bizUse"
          @search="handleBizSearch"
          @clear="handleBizClear">
          <table-chart
            :show-pagination="true"
            :pagination="bizTablePagination"
            :columns="bizTableColumns"
            :chart-data="bizUseData"
            :list-error="searchAndErrorToggles.biz.error"
            :search-toggle="searchAndErrorToggles.biz.search"
            @onPageChange="onBizTablePageChange"
            @onOrderChange="onBizTableOrderChange">
          </table-chart>
        </chart-card>
        <chart-card :title="$t(`m.operation['单据数量-按类型统计']`)" :loading="loading.ticketClassify">
          <bar-chart
            :loading="loading.ticketClassify"
            :y-axis-name="$t(`m.operation['单量（条）']`)"
            :chart-data="ticketClassifyData">
          </bar-chart>
        </chart-card>
        <chart-card :title="$t(`m.operation['单据状态占比']`)" :loading="loading.ticketStatus">
          <pie-chart
            :loading="loading.ticketStatus"
            :chart-data="ticketStatusData">
          </pie-chart>
        </chart-card>
      </div>
    </div>
    <div class="ticket-statistics statistics-section">
      <h4>{{ $t(`m.operation['提单统计']`) }}</h4>
      <div class="charts-wrap">
        <chart-card
          style="height: 410px;"
          :title="$t(`m.operation['提单人数']`)"
          :loading="loading.creator">
          <line-chart
            :loading="loading.creator"
            :min="0"
            :gradient-color="['rgba(58, 132, 255, 0)', 'rgba(58, 132, 255, 0.3)']"
            :y-axis-name="$t(`m.operation['人数（人）']`)"
            :chart-data="creatorData"
            :dimension="creatorChartDismension"
            @onDimensionChange="onCreatorDimensionChange">
          </line-chart>
        </chart-card>
        <chart-card
          style="height: 410px;"
          :title="$t(`m.operation['Top 10 提单用户']`)"
          :loading="loading.top10CreateTicketUser"
          @search="getTop10CreateTicketUserData()">
          <table-chart
            :loading="loading.top10CreateTicketUser"
            :columns="creatorTableColumns"
            :list-error="searchAndErrorToggles.top10.error"
            :search-toggle="searchAndErrorToggles.top10.search"
            :chart-data="top10CreateTicketUserData">
          </table-chart>
        </chart-card>
        <chart-card
          style="height: 410px;"
          :title="$t(`m.operation['Top 10 单据分布占比']`)"
          :desc="$t(`m.operation['按组织架构统计']`)"
          :loading="loading.top10TicketOrganization">
          <pie-chart
            :loading="loading.top10TicketOrganization"
            :chart-data="top10TicketOrganizationData">
          </pie-chart>
        </chart-card>
      </div>
    </div>
    <div class="added-statistics statistics-section">
      <h4>{{ $t(`m.operation['新增统计']`) }}</h4>
      <div class="charts-wrap">
        <chart-card :title="$t(`m.operation['新增单量']`)" :desc="$t(`m.operation['选定周期内，新增的单量']`)" :loading="loading.addedTicket">
          <line-chart
            :loading="loading.addedTicket"
            :gradient-color="['rgba(37, 91, 175, 0)', 'rgba(37, 91, 175, 0.3)']"
            :y-axis-name="$t(`m.operation['单量（条）']`)"
            :chart-data="addedTicketData"
            :dimension="addedTicketChartDismension"
            @onDimensionChange="onAddedTicketDimensionChange">
          </line-chart>
        </chart-card>
        <chart-card :title="$t(`m.operation['新增用户数']`)" :desc="$t(`m.operation['选定周期内，新增的用户']`)" :loading="loading.addedUser">
          <line-chart
            :loading="loading.addedUser"
            :min="0"
            :gradient-color="['rgba(19, 143, 203, 0)', 'rgba(23, 142, 207, 0.3)']"
            :y-axis-name="$t(`m.operation['人数（人）']`)"
            :chart-data="addedUserData"
            :dimension="addedUserChartDismension"
            @onDimensionChange="onAddedUserDimensionChange">
          </line-chart>
        </chart-card>
        <chart-card :title="$t(`m.operation['新增服务']`)" :desc="$t(`m.operation['选定周期内，新增的服务']`)" :loading="loading.addedService">
          <line-chart
            :loading="loading.addedService"
            :min="0"
            :gradient-color="['rgba(123, 227, 221, 0)', 'rgba(69, 195, 184, 0.3)']"
            :y-axis-name="$t(`m.operation['服务（个）']`)"
            :chart-data="addedServiceData"
            :dimension="addedServiceChartDismension"
            @onDimensionChange="onAddedServiceDimensionChange">
          </line-chart>
        </chart-card>
      </div>
    </div>
  </div>
</template>
<script>
  import dayjs from 'dayjs';
  import throttle from 'lodash/throttle';
  import SummaryCard from './components/summaryCard.vue';
  import ChartCard from './components/chartCard.vue';
  import TableChart from './components/tableChart.vue';
  import LineChart from './components/lineChart.vue';
  import BarChart from './components/barChart.vue';
  import PieChart from './components/pieChart.vue';
  import i18n from '@/i18n/index.js';

  const FORMAT = 'YYYY-MM-DD';

  const SERVICE_TABLE_COLUMNS = [
    {
      key: 'order',
      name: 'No',
      colorMark: true,
      width: 80,
    },
    {
      key: 'service_name',
      name: i18n.t('m[\'服务名称\']'),
      link: true,
      handler(data) {
        this.$router.push({ name: this.$route.query.project_id ? 'projectOperationService' : 'OperationService', params: { id: data.service_id }, query: { project_id: this.$route.query.project_id } });
      },
    },
    {
      key: 'category',
      name: i18n.t('m[\'服务类型\']'),
    },
    {
      key: 'count',
      name: i18n.t('m[\'单量（占比）\']'),
      sort: true,
      align: 'right',
      format(data) {
        return `${data.count}(${data.ratio})`;
      },
    },
    {
      key: 'creator_count',
      name: i18n.t('m[\'用户数\']'),
      sort: true,
      align: 'right',
      width: 100,
    },
    {
      key: 'biz_count',
      name: i18n.t('m[\'业务使用数\']'),
      sort: true,
      align: 'right',
      width: 110,
    },
  ];
  const BIZ_TABLE_COLUMNS = [
    {
      key: 'order',
      name: 'No',
      colorMark: true,
      width: 80,
    },
    {
      key: 'bk_biz_name',
      name: i18n.t('m[\'业务名\']'),
    },
    {
      key: 'service_count',
      name: i18n.t('m[\'使用服务数量\']'),
      sort: true,
      align: 'right',
    },
    {
      key: 'count',
      name: i18n.t('m[\'单量\']'),
      sort: true,
      align: 'right',
      width: 120,
    },
  ];
  const CREATOR_TABLE_COLUMNS = [
    {
      key: 'order',
      name: 'No',
      colorMark: true,
      width: 60,
    },
    {
      key: 'creator',
      name: i18n.t('m[\'用户ID\']'),
      width: 120,
    },
    {
      key: 'organization',
      name: i18n.t('m[\'所在组织\']'),
    },
    {
      key: 'count',
      name: i18n.t('m[\'提单量\']'),
      colorMark: true,
      align: 'right',
      width: 120,
    },
  ];

  const STATUS_MAP = {
    RUNNING: i18n.t('m[\'进行中\']'),
    FINISHED: i18n.t('m[\'已完成\']'),
    REVOKED: i18n.t('m[\'已撤销\']'),
    TERMINATED: i18n.t('m[\'已终止\']'),
  };

  export default {
    name: 'OperationHome',
    components: {
      SummaryCard,
      ChartCard,
      TableChart,
      LineChart,
      BarChart,
      PieChart,
    },
    data() {
      const end = dayjs().format(FORMAT);
      const start = dayjs().subtract(1, 'month')
        .format(FORMAT);
      return {
        dateRange: [start, end],
        isDateSelectorFixed: false,
        summaryData: {
          total: {
            count: 0,
            service_count: 0,
            biz_count: 0,
            user_count: 0,
          },
          week: {
            ticket: {
              this_week_count: 0,
              last_week_count: 0,
              ratio: '--',
            },
            service: {
              this_week_count: 0,
              last_week_count: 0,
              ratio: '--',
            },
            biz: {
              this_week_count: 0,
              last_week_count: 0,
              ratio: '--',
            },
            user: {
              this_week_count: 0,
              last_week_count: 0,
              ratio: '--',
            },
          },
        },
        bizList: [],
        bizSearchIds: undefined,
        serviceUseData: [],
        serviceSearchStr: undefined,
        bizUseData: [],
        ticketClassifyData: {},
        ticketStatusData: {},
        creatorData: {},
        top10CreateTicketUserData: [],
        top10TicketOrganizationData: {},
        addedTicketData: {},
        addedUserData: {},
        addedServiceData: {},
        serviceTableColumns: SERVICE_TABLE_COLUMNS,
        bizTableColumns: BIZ_TABLE_COLUMNS,
        creatorTableColumns: CREATOR_TABLE_COLUMNS,
        creatorChartDismension: 'days',
        addedTicketChartDismension: 'days',
        addedUserChartDismension: 'days',
        addedServiceChartDismension: 'days',
        serviceTablePagination: {
          size: 'small',
          current: 1,
          count: 0,
          limit: 10,
          'show-limit': false,
        },
        bizTablePagination: {
          size: 'small',
          current: 1,
          count: 0,
          limit: 10,
          'show-limit': false,
        },
        shortcuts: [
          {
            text: this.$t('m[\'今天\']'),
            value() {
              const end = dayjs().format(FORMAT);
              const start = dayjs().format(FORMAT);
              return [start, end];
            },
          },
          {
            text: this.$t('m[\'昨天\']'),
            value() {
              const end = dayjs().format(FORMAT);
              const start = dayjs().subtract(1, 'day')
                .format(FORMAT);
              return [start, end];
            },
          },
          {
            text: this.$t('m[\'前天\']'),
            value() {
              const end = dayjs().format(FORMAT);
              const start = dayjs().subtract(2, 'day')
                .format(FORMAT);
              return [start, end];
            },
          },
          {
            text: this.$t('m[\'一周前\']'),
            value() {
              const end = dayjs().format(FORMAT);
              const start = dayjs().subtract(1, 'week')
                .format(FORMAT);
              return [start, end];
            },
          },
          {
            text: this.$t('m[\'一个月前\']'),
            value() {
              const end = dayjs().format(FORMAT);
              const start = dayjs().subtract(1, 'month')
                .format(FORMAT);
              return [start, end];
            },
          },
          {
            text: this.$t('m[\'三个月前\']'),
            value() {
              const end = dayjs().format(FORMAT);
              const start = dayjs().subtract(3, 'month')
                .format(FORMAT);
              return [start, end];
            },
          },
          {
            text: this.$t('m[\'半年前\']'),
            value() {
              const end = dayjs().format(FORMAT);
              const start = dayjs().subtract(6, 'month')
                .format(FORMAT);
              return [start, end];
            },
          },
          {
            text: this.$t('m[\'一年前\']'),
            value() {
              const end = dayjs().format(FORMAT);
              const start = dayjs().subtract(1, 'year')
                .format(FORMAT);
              return [start, end];
            },
          },
        ],
        loading: {
          summary: false,
          bizList: false,
          serviceUse: false,
          bizUse: false,
          ticketClassify: false,
          ticketStatus: false,
          creator: false,
          top10CreateTicketUser: false,
          top10TicketOrganization: false,
          addedTicket: false,
          addedUser: false,
          addedService: false,
        },
        project_key: this.$route.query.project_id || undefined,
        searchAndErrorToggles: { // 搜索和获取数据错误
          service: { // 使用服务
            search: false,
            error: false,
          },
          biz: { // 业务
            search: false,
            error: false,
          },
          top10: { // top 10 提单用户
            search: false,
            error: false,
          },
        },
      };
    },
    created() {
      this.getSummaryData();
      this.getDetailData();
      this.getBizList();
      this.handleDateSelectorPosition = throttle(this.scrollHandler, 300);
    },
    mounted() {
      this.$parent.$el.addEventListener('scroll', this.handleDateSelectorPosition, false);
    },
    beforeDestroy() {
      this.$parent.$el.removeEventListener('scroll', this.handleDateSelectorPosition, false);
    },
    methods: {
      getDetailData() {
        this.getServiceUseData();
        this.getBizUseData();
        this.getTicketClassifyData();
        this.getTicketStatusData();
        this.getCreatorData();
        this.getTop10CreateTicketUserData();
        this.getTop10TicketOrganizationData();
        this.getAddedTicketData();
        this.getAddedUserData();
        this.getAddedServiceData();
      },
      // 概览数据
      async getSummaryData() {
        this.loading.summary = true;
        try {
          const params = {
            project_key: this.project_key,
          };
          const resp = await Promise.all([
            this.$store.dispatch('operation/getSummaryTotalData', params),
            this.$store.dispatch('operation/getSummaryWeekData', params),
          ]);
          this.summaryData = {
            total: resp[0].data,
            week: resp[1].data,
          };
        } catch (e) {
          console.error(e);
        } finally {
          this.loading.summary = false;
        }
      },
      // 加载业务列表
      async getBizList() {
        this.loading.bizList = true;
        try {
          const params = {
            project_key: this.project_key,
          };
          const resp = await this.$store.dispatch('eventType/getAppList', params);
          this.bizList = resp.data;
        } catch (e) {
          console.error(e);
        } finally {
          this.loading.bizList = false;
        }
      },
      // 服务使用统计
      async getServiceUseData(order) {
        this.loading.serviceUse = true;
        try {
          const params = {
            project_key: this.project_key,
            create_at__gte: this.dateRange[0],
            create_at__lte: this.dateRange[1],
            page: this.serviceTablePagination.current,
            service_name: this.serviceSearchStr,
            order_by: order,
          };
          const resp = await this.$store.dispatch('operation/getServiceUseData', params);
          this.serviceTablePagination.count = resp.data.count;
          this.serviceUseData = resp.data.items;
        } catch (e) {
          console.error(e);
        } finally {
          this.loading.serviceUse = false;
        }
      },
      // 业务使用统计
      async getBizUseData(order) {
        this.loading.bizUse = true;
        this.searchAndErrorToggles.biz.error = false;
        try {
          const params = {
            project_key: this.project_key,
            create_at__gte: this.dateRange[0],
            create_at__lte: this.dateRange[1],
            page: this.bizTablePagination.current,
            biz_id: this.bizSearchIds,
            order_by: order,
          };
          const resp = await this.$store.dispatch('operation/getBizUseData', params);
          this.bizTablePagination.count = resp.data.count;
          this.bizUseData = resp.data.items;
        } catch (e) {
          this.searchAndErrorToggles.biz.error = false;
          console.error(e);
        } finally {
          this.loading.bizUse = false;
        }
      },
      // 单据数量-按类型统计
      async getTicketClassifyData() {
        this.loading.ticketClassify = true;
        try {
          const params = {
            project_key: this.project_key,
            create_at__gte: this.dateRange[0],
            create_at__lte: this.dateRange[1],
          };
          const resp = await this.$store.dispatch('operation/getTicketClassifyData', params);
          const data = {
            x: [],
            y: [],
          };
          resp.data.forEach((item) => {
            const { count, service_type } = item;
            data.x.push(service_type);
            data.y.push(count);
          });
          this.ticketClassifyData = data;
        } catch (e) {
          console.error(e);
        } finally {
          this.loading.ticketClassify = false;
        }
      },
      // 单据状态占比
      async getTicketStatusData() {
        this.loading.ticketStatus = true;
        try {
          const params = {
            project_key: this.project_key,
            create_at__gte: this.dateRange[0],
            create_at__lte: this.dateRange[1],
          };
          const resp = await this.$store.dispatch('operation/getTicketStatusData', params);
          const data = {
            labels: [],
            value: [],
          };
          resp.data.forEach((item) => {
            const { status, count } = item;
            data.labels.push(STATUS_MAP[status]);
            data.value.push(count);
          });
          this.ticketStatusData = data;
        } catch (e) {
          console.error(e);
        } finally {
          this.loading.ticketStatus = false;
        }
      },
      // 提单人数
      async getCreatorData() {
        this.loading.creator = true;
        try {
          const params = {
            project_key: this.project_key,
            create_at__gte: this.dateRange[0],
            create_at__lte: this.dateRange[1],
            timedelta: this.creatorChartDismension,
            resource_type: 'creator',
          };
          const resp = await this.$store.dispatch('operation/getResourceCountData', params);
          const data = {
            x: [],
            y: [],
          };
          resp.data.forEach((item) => {
            const { count, date } = item;
            data.x.push(date);
            data.y.push(count);
          });
          this.creatorData = data;
        } catch (e) {
          console.error(e);
        } finally {
          this.loading.creator = false;
        }
      },
      // top 10 提单用户
      async getTop10CreateTicketUserData() {
        this.loading.top10CreateTicketUser = true;
        try {
          const params = {
            project_key: this.project_key,
            create_at__gte: this.dateRange[0],
            create_at__lte: this.dateRange[1],
          };
          this.searchAndErrorToggles.top10.error = false;
          const resp = await this.$store.dispatch('operation/getTop10CreateTicketUserData', params);
          const data = resp.data.map((item) => {
            if (item.organization.length > 0) {
              const fullOrganization = this.getFullOrganization(item.organization);
              item.organization_full = fullOrganization.reverse().join('/');
              item.organization = item.organization[0].name;
            } else {
              item.organization = '--';
            }
            return item;
          });
          this.top10CreateTicketUserData = data;
        } catch (e) {
          this.searchAndErrorToggles.top10.error = true;
          console.error(e);
        } finally {
          this.loading.top10CreateTicketUser = false;
        }
      },
      // top 10 单据分布占比
      async getTop10TicketOrganizationData() {
        this.loading.top10TicketOrganization = true;
        try {
          const params = {
            project_key: this.project_key,
            create_at__gte: this.dateRange[0],
            create_at__lte: this.dateRange[1],
          };
          const resp = await this.$store.dispatch('operation/getTop10TicketOrganizationData', params);
          const data = {
            labels: [],
            value: [],
          };
          resp.data.forEach((item) => {
            const { organization, count } = item;
            data.labels.push(organization);
            data.value.push(count);
          });
          this.top10TicketOrganizationData = data;
        } catch (e) {
          console.error(e);
        } finally {
          this.loading.top10TicketOrganization = false;
        }
      },
      // 新增单量
      async getAddedTicketData() {
        this.loading.addedTicket = true;
        try {
          const params = {
            project_key: this.project_key,
            create_at__gte: this.dateRange[0],
            create_at__lte: this.dateRange[1],
            timedelta: this.addedTicketChartDismension,
            resource_type: 'ticket',
          };
          const resp = await this.$store.dispatch('operation/getResourceCountData', params);
          const data = {
            x: [],
            y: [],
          };
          resp.data.forEach((item) => {
            const { count, date } = item;
            data.x.push(date);
            data.y.push(count);
          });
          this.addedTicketData = data;
        } catch (e) {
          console.error(e);
        } finally {
          this.loading.addedTicket = false;
        }
      },
      // 新增用户数
      async getAddedUserData() {
        this.loading.addedUser = true;
        try {
          const params = {
            project_key: this.project_key,
            create_at__gte: this.dateRange[0],
            create_at__lte: this.dateRange[1],
            timedelta: this.addedUserChartDismension,
            resource_type: 'user',
          };
          const resp = await this.$store.dispatch('operation/getResourceCountData', params);
          const data = {
            x: [],
            y: [],
          };
          resp.data.forEach((item) => {
            const { count, date } = item;
            data.x.push(date);
            data.y.push(count);
          });
          this.addedUserData = data;
        } catch (e) {
          console.error(e);
        } finally {
          this.loading.addedUser = false;
        }
      },
      // 新增服务
      async getAddedServiceData() {
        this.loading.addedService = true;
        try {
          const params = {
            project_key: this.project_key,
            create_at__gte: this.dateRange[0],
            create_at__lte: this.dateRange[1],
            timedelta: this.addedServiceChartDismension,
            resource_type: 'service',
          };
          const resp = await this.$store.dispatch('operation/getResourceCountData', params);
          const data = {
            x: [],
            y: [],
          };
          resp.data.forEach((item) => {
            const { count, date } = item;
            data.x.push(date);
            data.y.push(count);
          });
          this.addedServiceData = data;
        } catch (e) {
          console.error(e);
        } finally {
          this.loading.addedService = false;
        }
      },
      getFullOrganization(organization) {
        const target = organization[0];
        let fullOrganization = [target.name];
        if (target.family && target.family.length > 0) {
          const nextName = this.getFullOrganization(target.family);
          fullOrganization = fullOrganization.concat(nextName);
        }
        return fullOrganization;
      },
      onSelectDate(value) {
        this.dateRange = value;
        this.serviceTablePagination.current = 1;
        this.bizTablePagination.current = 1;
        this.getDetailData();
      },
      scrollHandler(e) {
        this.isDateSelectorFixed = e.target.scrollTop > 150;
      },
      handleServiceSearch(val) {
        this.serviceSearchStr = val || undefined;
        this.searchAndErrorToggles.service.search = true;
        this.serviceTablePagination.current = 1;
        this.getServiceUseData();
      },
      handleBizClear() {
        this.searchAndErrorToggles.biz.search = false;
        this.getBizUseData();
      },
      handleServiceClear() {
        this.serviceSearchStr = '';
        this.searchAndErrorToggles.service.search = false;
        this.getServiceUseData();
      },
      handleBizSearch(val) {
        this.bizTablePagination.current = 1;
        if (val !== '') {
          this.searchAndErrorToggles.biz.search = true;
          const matched = this.bizList.filter(item => item.name.toLowerCase().includes(val));
          if (matched.length > 0) {
            this.bizSearchIds = matched.map(item => item.key).join(',');
            this.getBizUseData();
          } else {
            this.bizTablePagination.count = 0;
            this.bizUseData = [];
            this.bizSearchIds = undefined;
          }
        } else {
          this.bizSearchIds = undefined;
          this.getBizUseData();
          this.searchAndErrorToggles.biz.search = false;
        }
      },
      onServiceTablePageChange(page) {
        this.serviceTablePagination.current = page;
        this.getServiceUseData();
      },
      onServiceTableOrderChange(order) {
        this.serviceTablePagination.current = 1;
        this.getServiceUseData(order);
      },
      onBizTablePageChange(page) {
        this.bizTablePagination.current = page;
        this.getBizUseData();
      },
      onBizTableOrderChange(order) {
        this.bizTablePagination.current = 1;
        this.getBizUseData(order);
      },
      onCreatorDimensionChange(val) {
        this.creatorChartDismension = val;
        this.getCreatorData();
      },
      onAddedTicketDimensionChange(val) {
        this.addedTicketChartDismension = val;
        this.getAddedTicketData();
      },
      onAddedUserDimensionChange(val) {
        this.addedUserChartDismension = val;
        this.getAddedUserData();
      },
      onAddedServiceDimensionChange(val) {
        this.addedServiceChartDismension = val;
        this.getAddedServiceData();
      },
    },
  };
</script>
<style lang="scss" scoped>
    .operation-home {
        position: relative;
        padding: 20px 20px 60px;
    }
    .date-selector {
        position: absolute;
        top: 158px;
        right: 0;
        padding: 10px 20px 10px;
        z-index: 100;
        .bk-date-picker {
            float: right;
            width: 360px;
            background: #ffffff;
        }
        &.selector-fixed {
            position: fixed;
            top: 52px;
            left: 0;
            right: 0;
            width: 100%;
            background: #ffffff;
            box-shadow: 0px 3px 6px 0px rgba(0,0,0,0.1);
        }
    }
    .statistics-section {
        margin-bottom: 30px;
        & > h4 {
            margin: 0 0 16px;
            font-size: 16px;
            font-weight: 700;
            color: #63656e;
            line-height: 21px;
        }
    }
    .summary-data {
        display: flex;
        justify-content: space-between;
        .summary-card {
            width: 24.5%;
        }
    }
    .charts-wrap {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        .chart-card {
            margin-bottom: 16px;
        }
    }
    .global-statistics {
        .chart-card {
            &:nth-child(2n) {
                width: 39%;
            }
            &:nth-child(2n + 1) {
                width: 60%;
            }
        }
        /deep/ .bk-table {
            td, th {
                height: 40px;
            }
        }
    }
    .ticket-statistics,
    .added-statistics {
        .charts-wrap {
            flex-wrap: nowrap;
        }
        .chart-card {
            margin-right: 16px;
            flex: 1;
            &:nth-child(3n) {
                margin-right: 0;
            }
        }
        /deep/ .bk-table {
            td, th {
                height: 30px;
                border-bottom-color: #ffffff;
            }
            th {
                background: #f0f1f5;
                .cell {
                    height: 30px;
                }
            }
            td {
                background: #fafbfd;
            }
        }
    }
</style>
