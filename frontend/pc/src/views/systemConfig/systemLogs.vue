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
        {{ $t('m.navigation["接口日志"]') }}
      </p>
    </div>
    <div class="itsm-page-content">
      <div class="bk-only-btn">
        <div class="bk-more-search">
          <bk-button :theme="'primary'"
            :title="$t(`m.systemConfig['批量导出']`)"
            :disabled="checkList.length === 0"
            @click="exportLogs">
            {{$t(`m.systemConfig['批量导出']`)}}
          </bk-button>
          <div class="bk-search-name">
            <div class="bk-search-content">
              <bk-input
                :placeholder="moreSearch[0].placeholder || $t(`m.deployPage['请输入流程名']`)"
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
      <bk-table
        v-bkloading="{ isLoading: isDataLoading }"
        :data="dataList"
        :size="'small'"
        :pagination="pagination"
        @page-change="handlePageChange"
        @page-limit-change="handlePageLimitChange"
        @select-all="handleSelectAll"
        @select="handleSelect">
        <bk-table-column type="selection" width="60" align="center"></bk-table-column>
        <bk-table-column :label="$t(`m.systemConfig['接口地址']`)" width="350">
          <template slot-scope="props">
            <span class="bk-lable-primary"
              :title="props.row.url"
              @click="seeLogs(props.row)">
              {{props.row.url || '--'}}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.systemConfig['请求方法']`)">
          <template slot-scope="props">
            <span :title="props.row.method">{{ props.row.method || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.systemConfig['状态']`)">
          <template slot-scope="props">
            <span :title="props.row.status_code">{{ props.row.status_code}}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.systemConfig['请求时间']`)">
          <template slot-scope="props">
            <span :title="props.row.date_created">{{ props.row.date_created || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.systemConfig['耗时']`)">
          <template slot-scope="props">
            <span :title="props.row.duration">{{ props.row.duration || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.systemConfig['接口ID']`)">
          <template slot-scope="props">
            <span :title="props.row.api_instance_id">{{ props.row.api_instance_id}}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.systemConfig['操作']`)" width="150">
          <template slot-scope="props">
            <bk-button
              theme="primary"
              text
              @click="exportLog(props.row)">
              {{ $t('m.systemConfig["导出"]') }}
            </bk-button>
          </template>
        </bk-table-column>
      </bk-table>
    </div>
    <!-- 查看详情 -->
    <div class="bk-logs">
      <bk-sideslider
        :is-show.sync="customSettings.isShow"
        :title="customSettings.title"
        :quick-close="true"
        :width="customSettings.width">
        <div class="p20" slot="content" v-if="customSettings.isShow">
          <logs-info :logs-object="customSettings.logsObject"></logs-info>
        </div>
      </bk-sideslider>
    </div>
  </div>
</template>
<script>
  import searchInfo from '../commonComponent/searchInfo/searchInfo.vue';
  import logsInfo from './component/logsInfo.vue';
  import commonMix from '../commonMix/common.js';
  import { errorHandler } from '../../utils/errorHandler';

  export default {
    name: 'SystemLogs',
    components: {
      searchInfo,
      logsInfo,
    },
    mixins: [commonMix],
    data() {
      return {
        isDataLoading: false,
        secondClick: false,
        // table数据和分页
        dataList: [],
        pagination: {
          current: 1,
          count: 10,
          limit: 10,
        },
        // 选中的数据
        checkList: [],
        // 查询
        moreSearch: [
          {
            name: this.$t('m.systemConfig["接口地址"]'),
            placeholder: this.$t('m.systemConfig["请输入接口地址"]'),
            typeKey: 'name__contains',
            type: 'input',
            value: '',
            list: [],
          },
          {
            name: this.$t('m.systemConfig["请求方法"]'),
            type: 'select',
            typeKey: 'method',
            value: '',
            list: [
              { key: 'GET', name: 'GET' },
              { key: 'POST', name: 'POST' },
              { key: 'PUT', name: 'PUT' },
              { key: 'DELETE', name: 'DELETE' },
              { key: 'PATCH', name: 'PATCH' },
            ],
          },
          {
            name: this.$t('m.systemConfig["状态码"]'),
            type: 'select',
            typeKey: 'status',
            value: '',
            list: [
              { key: '20X', name: '20X' },
              { key: '30X', name: '30X' },
              { key: '40X', name: '40X' },
              { key: '50X', name: '50X' },
            ],
          },
          {
            name: this.$t('m.systemConfig["接口ID"]'),
            type: 'input',
            typeKey: 'api_instance_id',
            value: '',
            list: [],
          },
          {
            name: this.$t('m.systemConfig["单据ID"]'),
            type: 'input',
            typeKey: 'ticket_id',
            value: '',
            list: [],
          },
          {
            name: this.$t('m.systemConfig["请求时间"]'),
            type: 'datetime',
            value: '',
            list: [],
          },
        ],
        // 日志详情
        customSettings: {
          isShow: false,
          title: this.$t('m.systemConfig["日志详情"]'),
          width: 700,
          logsObject: {},
        },
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
          if (item.type === 'datetime' && item.value && item.value[0]) {
            const d = new Date(item.value[0]);
            const gteTime = `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()} ${d.getHours()}:${d.getMinutes()}:${d.getSeconds()}`;
            const lte = new Date(item.value[1]);
            const lteTime = `${lte.getFullYear()}-${lte.getMonth() + 1}-${lte.getDate()} ${lte.getHours()}:${lte.getMinutes()}:${lte.getSeconds()}`;
            params.date_created__gte = gteTime;
            params.date_created__lte = lteTime;
          } else {
            if (item.value && item.typeKey) {
              params[item.typeKey] = Array.isArray(item.value) ? item.value.join(',') : item.value;
            }
          }
        });
        // 请求方法
        this.isDataLoading = true;
        this.$store.dispatch('systemLog/list', params).then((res) => {
          this.dataList = res.data.items;
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
        this.checkList = selection;
      },
      handleSelect(selection) {
        this.checkList = selection;
      },
      // 查看日志
      seeLogs(item) {
        this.customSettings.logsObject = item;
        this.customSettings.isShow = true;
      },
      // 导出日志
      exportLog(item) {
        window.open(`${window.SITE_URL}api/tracker/records/${item.id}/exports/`);
      },
      // 批量导出日志
      exportLogs() {
        const idArr = this.checkList.map(item => item.id);
        const logs = idArr.join(',');
        window.open(`${window.SITE_URL}api/tracker/records/batch_exports/?logs=${logs}`);
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
          item.value = '';
        });
        this.getList(1);
      },
    },
  };
</script>

<style lang='scss' scoped>
    .filter-btn /deep/ .icon-search-more {
        font-size: 14px;
    }
</style>
