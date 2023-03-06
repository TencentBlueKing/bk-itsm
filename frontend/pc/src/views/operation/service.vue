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
  <div class="operation-service">
    <div class="section-nav">
      <div class="service-wrap">
        <i class="bk-icon icon-arrows-left back-icon" @click="$router.push({ name: $route.query.project_id ? 'projectOperationHome' : 'OperationHome', query: $route.query.project_id ? { project_id: $route.query.project_id } : '' })"></i>
        <bk-select
          class="service-selector"
          :value="serviceId"
          :searchable="true"
          :clearable="false"
          @toggle="onServicePanelToggle"
          @selected="onServiceChange">
          <div slot="trigger" class="selected-service" :class="{ 'panel-open': isServicePanelShow }">
            <span class="service-name">{{ serviceName }}</span>
            <i class="bk-icon icon-down-shape trigger-icon"></i>
          </div>
          <bk-option v-for="option in serviceList"
            :key="option.id"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
      </div>
    </div>
    <div class="section-content">
      <div class="date-selector" :class="{ 'selector-fixed': isDateSelectorFixed }">
        <bk-date-picker
          type="daterange"
          :clearable="false"
          :shortcuts="shortcuts"
          :options="datePickerOptions"
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
      <div class="service-statistics statistics-section">
        <h4>{{ $t(`m.operation['统计指标']`) }}</h4>
        <div class="charts-wrap">
          <chart-card
            style="width: 100%;"
            :title="$t(`m.operation['新增单量']`)"
            :loading="loading.addedTicket">
            <line-chart
              :gradient-color="['rgba(37, 91, 175, 0)', 'rgba(37, 91, 175, 0.3)']"
              :loading="loading.addedTicket"
              :y-axis-name="$t(`m.operation['单量（条）']`)"
              :chart-data="addedTicketData"
              :dimension="addedTicketChartDismension"
              @onDimensionChange="onAddedTicketDimensionChange">
            </line-chart>
          </chart-card>
          <chart-card
            style="width: 31%; height: 410px;"
            :title="$t(`m.operation['Top 10 提单用户']`)"
            :loading="loading.top10CreateTicketUser"
            @search="getTop10CreateTicketUserData">
            <table-chart
              :list-error="toggle.top10.error"
              :loading="loading.top10CreateTicketUser"
              :columns="creatorTableColumns"
              :chart-data="top10CreateTicketUserData">
            </table-chart>
          </chart-card>
          <chart-card
            style="width: 68%; height: 410px;"
            :title="$t(`m.operation['业务数量']`)"
            :loading="loading.biz">
            <line-chart
              :gradient-color="['rgba(19, 143, 203, 0)', 'rgba(23, 142, 207, 0.3)']"
              :loading="loading.biz"
              :y-axis-name="$t(`m.operation['人数（人）']`)"
              :chart-data="bizData"
              :dimension="bizChartDismension"
              @onDimensionChange="onAddedServiceDimensionChange">
            </line-chart>
          </chart-card>
        </div>
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
  import i18n from '@/i18n/index.js';

  const FORMAT = 'YYYY-MM-DD';

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

  export default {
    name: 'OperationService',
    components: {
      SummaryCard,
      ChartCard,
      TableChart,
      LineChart,
    },
    data() {
      const end = dayjs().format('YYYY-MM-DD');
      const start = dayjs().subtract(1, 'month')
        .format('YYYY-MM-DD');
      const serviceId = Number(this.$route.params.id);
      return {
        serviceId,
        serviceList: [],
        isServicePanelShow: false,
        dateRange: [start, end],
        isDateSelectorFixed: false,
        summaryData: {
          total: {
            count: 0,
            biz_count: 0,
            user_count: 0,
          },
          week: {
            ticket: {
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
        top10CreateTicketUserData: [],
        addedTicketData: {},
        bizData: {},
        creatorTableColumns: CREATOR_TABLE_COLUMNS,
        addedTicketChartDismension: 'days',
        bizChartDismension: 'days',
        datePickerOptions: {
          disabledDate(val) {
            return dayjs(val).isAfter(dayjs(), 'day');
          },
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
          serviceList: false,
          summary: false,
          addedTicket: false,
          top10CreateTicketUser: false,
          biz: false,
        },
        toggle: {
          top10: {
            error: false,
          },
        },
      };
    },
    computed: {
      serviceName() {
        const service = this.serviceList.find(item => item.id === this.serviceId);
        return service ? service.name : '--';
      },
    },
    created() {
      this.getServiceList();
      this.getSummaryData();
      this.getDetailData();
      this.handleDateSelectorPosition = throttle(this.scrollHandler, 300);
    },
    mounted() {
      document.querySelector('.section-content').addEventListener('scroll', this.handleDateSelectorPosition, false);
    },
    beforeDestroy() {
      document.querySelector('.section-content').removeEventListener('scroll', this.handleDateSelectorPosition, false);
    },
    methods: {
      async getServiceList() {
        this.loading.serviceList = true;
        try {
          const resp = await this.$store.dispatch('service/getServiceList');
          this.serviceList = resp.data;
        } catch (e) {
          console.error(e);
        } finally {
          this.loading.serviceList = false;
        }
      },
      getDetailData() {
        this.getTop10CreateTicketUserData();
        this.getAddedTicketData();
        this.getBizData();
      },
      // 概览数据
      async getSummaryData() {
        this.loading.summary = true;
        try {
          const resp = await Promise.all([
            this.$store.dispatch('operation/getSummaryTotalData', { service_id: this.serviceId }),
            this.$store.dispatch('operation/getSummaryWeekData', { service_id: this.serviceId }),
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
      // 新增单量
      async getAddedTicketData() {
        this.loading.addedTicket = true;
        try {
          const params = {
            create_at__gte: this.dateRange[0],
            create_at__lte: this.dateRange[1],
            timedelta: this.addedTicketChartDismension,
            resource_type: 'ticket',
            service_id: this.serviceId,
          };
          const resp = await this.$store.dispatch('operation/getResourceCountData', params);
          const data = {
            x: [],
            y: [],
          };
          resp.data.forEach(item => {
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
      // top 10 提单用户
      async getTop10CreateTicketUserData() {
        this.loading.top10CreateTicketUser = true;
        try {
          const params = {
            create_at__gte: this.dateRange[0],
            create_at__lte: this.dateRange[1],
            service_id: this.serviceId,
          };
          this.toggle.top10.error = false;
          const resp = await this.$store.dispatch('operation/getTop10CreateTicketUserData', params);
          const data = resp.data.map(item => {
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
          this.toggle.top10.error = true;
          console.error(e);
        } finally {
          this.loading.top10CreateTicketUser = false;
        }
      },
      // 业务数量
      async getBizData() {
        this.loading.biz = true;
        try {
          const params = {
            create_at__gte: this.dateRange[0],
            create_at__lte: this.dateRange[1],
            timedelta: this.bizChartDismension,
            resource_type: 'biz',
            service_id: this.serviceId,
          };
          const resp = await this.$store.dispatch('operation/getServiceCountData', params);
          const data = {
            x: [],
            y: [],
          };
          resp.data.forEach(item => {
            const { count, date } = item;
            data.x.push(date);
            data.y.push(count);
          });
          this.bizData = data;
        } catch (e) {
          console.error(e);
        } finally {
          this.loading.biz = false;
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
      onServicePanelToggle(isShow) {
        this.isServicePanelShow = isShow;
      },
      onServiceChange(id) {
        this.serviceId = id;
        this.getDetailData();
        this.$router.push({ name: 'OperationService', params: { id } });
      },
      onSelectDate(value) {
        this.dateRange = value;
        this.getDetailData();
      },
      scrollHandler(e) {
        this.isDateSelectorFixed = e.target.scrollTop > 150;
      },
      onAddedTicketDimensionChange(val) {
        this.addedTicketChartDismension = val;
        this.getAddedTicketData();
      },
      onAddedServiceDimensionChange(val) {
        this.bizChartDismension = val;
        this.getBizData();
      },
    },
  };
</script>
<style lang="scss" scoped>
    .section-nav {
        position: relative;
        display: flex;
        align-items: center;
        padding: 0 20px;
        height: 52px;
        background: #ffffff;
        box-shadow: 0px 2px 4px 0px rgba(49, 50, 56, 0.1);
        z-index: 1;
        .service-wrap {
            display: inline-flex;
            align-items: center;
            .back-icon {
                margin-right: 16px;
                font-size: 28px;
                color: #3a84ff;
                cursor: pointer;
            }
            .service-selector {
                border: none;
                box-shadow: none;
            }
            .selected-service {
                display: flex;
                align-items: center;
                width: 400px;
                font-size: 16px;
                color: #000000;
                &.panel-open {
                    .trigger-icon {
                        transform: rotate(-180deg);
                    }
                }
            }
            .trigger-icon {
                margin-left: 6px;
                color: #979ba5;
                font-size: 12px;
                transition: transform .3s cubic-bezier(.4,0,.2,1);
            }
        }
    }
    .section-content {
        position: relative;
        height: calc(100vh - 104px );
        padding: 20px 20px 60px;
        overflow: auto
    }
    .date-selector {
        position: absolute;
        top: 168px;
        right: 20px;
        z-index: 100;
        .bk-date-picker {
            width: 360px;
            background: #ffffff;
        }
        &.selector-fixed {
            position: fixed;
            top: 62px;
            right: 20px;
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
        justify-content: flex-start;
        .summary-card {
            margin-right: 16px;
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
    .service-statistics {
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
