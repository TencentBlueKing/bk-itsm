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
        {{ $t('m.systemConfig["数据字典"]') }}
      </p>
    </div>
    <div class="itsm-page-content">
      <!-- 提示信息 -->
      <div class="bk-itsm-version" v-if="versionStatus">
        <i class="bk-icon icon-info-circle"></i>
        <span>{{ $t('m.systemConfig["数据字典的字段值，可直接作为流程设计中字段值的来源选项"]') }}</span>
        <i class="bk-icon icon-close" @click="closeVersion"></i>
      </div>
      <!-- button -->
      <div class="bk-only-btn">
        <bk-button theme="primary"
          :title="$t(`m.systemConfig['新增']`)"
          icon="plus"
          class="mr10 plus-cus"
          @click="openAddData({})">
          {{ $t('m.systemConfig["新增"]') }}
        </bk-button>
        <bk-button :theme="'default'"
          :title="$t(`m.systemConfig['批量删除']`)"
          class="mr10"
          :disabled="!checkList.length"
          @click="deleteAll">
          {{$t(`m.systemConfig['批量删除']`)}}
        </bk-button>
        <div class="bk-only-search">
          <bk-input
            :placeholder="$t(`m.systemConfig['请输入编码']`)"
            :clearable="true"
            :right-icon="'bk-icon icon-search'"
            v-model="searchInfo.key"
            @enter="getList(1)"
            @clear="getList(1)">
          </bk-input>
        </div>
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
        <bk-table-column type="selection"
          width="60"
          align="center"
          :selectable="disabledFn">
        </bk-table-column>
        <bk-table-column type="index" label="No." align="center" width="60"></bk-table-column>
        <bk-table-column :label="$t(`m.systemConfig['编码']`)" width="220">
          <template slot-scope="props">
            <span class="bk-lable-primary"
              :title="props.row.key"
              @click="openAddData(props.row)">
              {{props.row.key || '--'}}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.systemConfig['名称']`)">
          <template slot-scope="props">
            <span :title="props.row.name">{{ props.row.name || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.systemConfig['描述']`)">
          <template slot-scope="props">
            <span :title="props.row.desc || '--'">{{ props.row.desc || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.systemConfig['启用状态']`)">
          <template slot-scope="props">
            <span :title="props.row.is_enabled ? $t(`m.systemConfig['有效']`) : $t(`m.systemConfig['无效']`)">
              {{ props.row.is_enabled ? $t(`m.systemConfig["有效"]`) : $t(`m.systemConfig["无效"]`)}}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.systemConfig['负责人']`)">
          <template slot-scope="props">
            <span :title="props.row.owners">{{props.row.owners || '--'}}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.systemConfig['创建人']`)">
          <template slot-scope="props">
            <span :title="props.row.creator">{{props.row.creator || '--'}}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.systemConfig['更新人']`)">
          <template slot-scope="props">
            <span :title="props.row.updated_by">{{ props.row.updated_by || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.systemConfig['更新时间']`)">
          <template slot-scope="props">
            <span :title="props.row.update_at">{{ props.row.update_at || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.systemConfig['操作']`)" width="150">
          <template slot-scope="props">
            <bk-button theme="primary" text @click="openAddData(props.row)">
              {{ $t('m.systemConfig["编辑"]') }}
            </bk-button>
            <bk-button v-if="!props.row.is_builtin"
              theme="primary"
              text
              @click="deleteData(props.row)">
              {{ $t('m.systemConfig["删除"]') }}
            </bk-button>
          </template>
        </bk-table-column>
        <div class="empty" slot="empty">
          <empty
            :is-error="listError"
            :is-search="Boolean(searchInfo.key)"
            @onRefresh="getlist(1)"
            @onClearSearch="onClearSearch">
          </empty>
        </div>
      </bk-table>
    </div>
    <!-- 新增字典 -->
    <div class="bk-add-data">
      <bk-sideslider
        :is-show.sync="customSettings.isShow"
        :title="customSettings.title"
        :quick-close="true"
        :width="customSettings.width">
        <div class="p20" slot="content" v-if="customSettings.isShow">
          <add-data-directory :slide-data="slideData"
            @openAddData="openAddData"
            @getList="getList"
            @closeAddData="closeAddData">
          </add-data-directory>
        </div>
      </bk-sideslider>
    </div>
  </div>
</template>

<script>
  import { errorHandler } from '../../utils/errorHandler';
  import addDataDirectory from './component/addDataDirectory.vue';
  import Empty from '../../components/common/Empty.vue';

  export default {
    name: 'dataDictionary',
    components: {
      addDataDirectory,
      Empty,
    },
    props: {},
    data() {
      return {
        listError: false,
        isDataLoading: false,
        secondClick: false,
        versionStatus: true,
        // 模糊查询
        searchInfo: {
          key: '',
        },
        // table数据和分页
        dataList: [],
        pagination: {
          current: 1,
          count: 10,
          limit: 10,
        },
        // 批量删除数据
        checkList: [],
        // 新增字典
        customSettings: {
          isShow: false,
          title: this.$t('m.systemConfig["新增字典"]'),
          width: 700,
        },
        // 侧边栏数据
        slideData: {},
      };
    },
    computed: {
      sliderStatus() {
        return this.$store.state.common.slideStatus;
      },
    },
    watch: {},
    mounted() {
      this.getList();
    },
    methods: {
      onClearSearch() {
        this.searchInfo.key = '';
        this.getList(1);
      },
      // 获取列表数据
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
          key__contains: this.searchInfo.key,
        };
        this.isDataLoading = true;
        this.listError = false;
        this.$store.dispatch('datadict/list', params).then((res) => {
          this.dataList = res.data.items.map(item => ({ ...item, ownersInputValue: item.owners ? item.owners.split(',') : [] }));
          // 分页
          this.pagination.current = res.data.page;
          this.pagination.count = res.data.count;
        }, (res) => {
          this.listError = true;
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
      disabledFn(item) {
        return !item.is_builtin;
      },
      // 删除数据
      deleteData(item) {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.systemConfig["确认删除此数据字典？"]'),
          confirmFn: () => {
            const { id } = item;
            if (this.secondClick) {
              return;
            }
            this.secondClick = true;
            this.$store.dispatch('datadict/delete', id).then(() => {
              this.$bkMessage({
                message: this.$t('m.systemConfig["删除成功"]'),
                theme: 'success',
              });
              if (this.dataList.length === 1) {
                this.pagination.current = this.pagination.current === 1
                  ? 1 : this.pagination.current - 1;
              }
              this.getList();
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.secondClick = false;
              });
          },
        });
      },
      deleteAll() {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.systemConfig["确认删除此数据字典？"]'),
          confirmFn: () => {
            const id = this.checkList.map(item => item.id).join(',');
            if (this.secondClick) {
              return;
            }
            this.secondClick = true;
            this.$store.dispatch('datadict/batchDelete', { id }).then(() => {
              this.$bkMessage({
                message: this.$t('m.systemConfig["删除成功"]'),
                theme: 'success',
              });
              this.getList(1);
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.secondClick = false;
              });
          },
        });
      },
      // 新增字典
      openAddData(item) {
        this.slideData = item;
        this.customSettings.title = item.id ? this.$t('m.systemConfig["编辑字典"]') : this.$t('m.systemConfig["新增字典"]');
        this.customSettings.isShow = true;
      },
      closeAddData() {
        this.customSettings.isShow = false;
      },
      // 关闭版本提示信息
      closeVersion() {
        this.versionStatus = false;
      },
    },
  };
</script>

<style lang="scss" scoped>

</style>
