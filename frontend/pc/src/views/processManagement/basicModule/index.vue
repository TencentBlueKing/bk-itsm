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
        {{ $t('m.basicModule["基础模型"]') }}
      </p>
    </div>
    <div class="itsm-page-content">
      <div class="bk-only-btn">
        <div class="bk-more-search">
          <bk-button :theme="'primary'"
            :title="$t(`m.deployPage['新增']`)"
            icon="plus"
            class="mr10 plus-cus"
            @click="openField({})">
            {{ $t(`m.deployPage['新增']`) }}
          </bk-button>
          <div class="bk-search-name">
            <div class="bk-search-content">
              <bk-input
                :clearable="true"
                :right-icon="'bk-icon icon-search'"
                :placeholder="moreSearch[0].placeholder"
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
        class="model-table"
        :data="dataList"
        :size="'small'"
        :pagination="pagination"
        @page-change="handlePageChange"
        @page-limit-change="handlePageLimitChange">
        <bk-table-column :label="$t(`m.basicModule['模型名称']`)">
          <template slot-scope="props">
            <span :title="props.row.name">{{ props.row.name || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.basicModule['模型描述']`)" width="150">
          <template slot-scope="props">
            <span :title="props.row.desc">{{ props.row.desc || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.deployPage['更新时间']`)" prop="update_at">
          <template slot-scope="props">
            <span :title="props.row.update_at">{{ props.row.update_at || '--' }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.treeinfo['更新人']`)">
          <template slot-scope="props">
            <span :title="props.row.updated_by">{{props.row.updated_by || '--'}}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.treeinfo['操作']`)" width="150">
          <template slot-scope="props">
            <bk-button theme="primary" text @click="openField(props.row)">
              {{ $t('m.deployPage["编辑"]') }}
            </bk-button>
            <bk-button
              theme="primary"
              :disabled="props.row.is_builtin"
              text
              @click="deleteTable(props.row)">
              {{ $t('m.deployPage["删除"]') }}
            </bk-button>
          </template>
        </bk-table-column>
      </bk-table>
    </div>
    <!-- 新增字段 -->
    <div class="bk-add-slider">
      <bk-sideslider
        :is-show.sync="sliderInfo.show"
        :title="sliderInfo.title"
        :width="sliderInfo.width">
        <div slot="content" v-bkloading="{ isLoading: addLoading }" style="min-height: 300px;">
          <add-basic-module
            v-if="!addLoading && sliderInfo.show"
            :public-list="publicList"
            :slide-data="slideData">
          </add-basic-module>
        </div>
      </bk-sideslider>
    </div>
  </div>
</template>
<script>
  import commonMix from '../../commonMix/common.js';
  import addBasicModule from './addBasicModule.vue';
  import searchInfo from '../../commonComponent/searchInfo/searchInfo.vue';
  import { errorHandler } from '../../../utils/errorHandler.js';

  export default {
    name: 'basicModule',
    components: {
      searchInfo,
      addBasicModule,
    },
    mixins: [commonMix],
    data() {
      return {
        // 数据
        isDataLoading: false,
        secondClick: false,
        dataList: [],
        pagination: {
          current: 1,
          count: 10,
          limit: 10,
        },
        // 查询
        moreSearch: [
          {
            name: this.$t('m.basicModule["模型名称"]'),
            placeholder: this.$t('m.basicModule["请输入模型名称"]'),
            typeKey: 'name__contains',
            type: 'input',
            value: '',
            list: [],
          },
          {
            name: this.$t('m.deployPage["更新人"]'),
            type: 'member',
            typeKey: 'updated_by__contains',
            multiSelect: true,
            value: [],
            list: [],
          },
          {
            name: this.$t('m.deployPage["更新时间"]'),
            typeKey: 'date_update',
            type: 'datetime',
            multiSelect: true,
            value: [],
            list: [],
          },
        ],
        // 侧边栏数据
        publicList: [],
        addLoading: false,
        sliderInfo: {
          title: this.$t('m.basicModule["新增模型"]'),
          show: false,
          width: 700,
        },
        slideData: {},
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
        const params = {
          page: this.pagination.current,
          page_size: this.pagination.limit,
        };
        // 过滤条件
        this.moreSearch.forEach((item) => {
          if (item.type === 'datetime' && item.value && item.value[0]) {
            const gteTime = this.standardTime(item.value[0]);
            const lteTime = this.standardTime(item.value[1]);
            params.update_at__gte = gteTime;
            params.update_at__lte = lteTime;
          } else {
            if (Array.isArray(item.value) ? !!item.value.length : !!item.value) {
              params[item.typeKey] = Array.isArray(item.value) ? item.value.join(',') : item.value;
            }
          }
        });
        this.isDataLoading = true;
        this.$store.dispatch('basicModule/get_tables', params).then((res) => {
          this.dataList = res.data.items;
          // 分页
          this.pagination.current = res.data.page;
          this.pagination.count = res.data.count;
        }, (res) => {
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
          item.value = item.multiSelect ? [] : '';
        });
        this.getList(1);
      },
      // 删除字段
      deleteTable(item) {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.basicModule["确认删除此模型？"]'),
          subTitle: this.$t('m.basicModule["模型一旦删除，此模型将不在可用。请谨慎操作。"]'),
          confirmFn: () => {
            const { id } = item;
            if (this.secondClick) {
              return;
            }
            this.secondClick = true;
            this.$store.dispatch('basicModule/delet_tables', { id }).then(() => {
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
      closeShade() {
        this.sliderInfo.show = false;
      },
      // 编辑字段
      openField(item) {
        this.getPublicFieldList();
        this.slideData = item;
        this.sliderInfo.title = item.id ? this.$t('m.basicModule["编辑模型"]') : this.$t('m.basicModule["新增模型"]');
        this.sliderInfo.show = true;
      },
      getPublicFieldList() {
        this.addLoading = true;
        this.$store.dispatch('publicField/get_template_common_fields', {}).then((res) => {
          this.publicList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.addLoading = false;
          });
      },
    },
  };
</script>

<style lang='scss' scoped>
    .filter-btn /deep/ .icon-search-more {
        font-size: 14px;
    }
</style>
