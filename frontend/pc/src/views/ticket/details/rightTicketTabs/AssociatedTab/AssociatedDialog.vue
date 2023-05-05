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
  <div class="bk-derive">
    <p class="bk-ticket-title">{{ $t(`m.manageCommon['关联类型']`) }}</p>
    <div class="bk-ticket-content">
      <bk-radio-group v-model="typeSelected" @change="clearFieldList">
        <template v-for="radio in typeSelectRadio">
          <bk-radio
            :value="radio.key"
            :key="radio.key"
            class="mr20"
          >{{ radio.name }}</bk-radio
          >
        </template>
      </bk-radio-group>
    </div>
    <template v-if="typeSelected === 'associate'">
      <p class="bk-ticket-title">
        {{ $t('m.manageCommon["可关联的列表"]') }}
      </p>
      <div class="bk-ticket-content">
        <div class="bk-content-search">
          <bk-select
            style="width: 200px; float: left; margin-right: 10px"
            searchable
            :font-size="'medium'"
            multiple
            :placeholder="$t(`m.serviceConfig['服务类型']`)"
            v-model="searchInfo.serviceType"
            @toggle="serviceSearch"
            @clear="clearSearch"
          >
            <bk-option
              v-for="option in serviceTypeList"
              :key="option.key"
              :id="option.key"
              :name="option.name"
            >
            </bk-option>
          </bk-select>
          <bk-input
            style="width: 200px; float: left"
            :placeholder="$t(`m.manageCommon['请输入标题/单号']`)"
            :clearable="true"
            :right-icon="'bk-icon icon-search'"
            v-model="searchInfo.keyword"
            @enter="getList"
            @clear="clearInfo"
          >
          </bk-input>
        </div>
        <bk-table
          v-bkloading="{ isLoading: isTableLoading }"
          :data="tabShowList"
          :size="'small'"
          :pagination="pagination"
          @page-change="handlePageChange"
          @page-limit-change="handlePageLimitChange"
          @select-all="handleSelectAll"
          @select="handleSelect"
        >
          <bk-table-column
            type="selection"
            width="60"
            align="center"
            :selectable="disabledFn"
          >
          </bk-table-column>
          <bk-table-column
            type="index"
            label="No."
            align="center"
            width="60"
          ></bk-table-column>
          <bk-table-column
            :label="$t(`m.newCommon['单号']`)"
            min-width="140"
            :render-header="$renderHeader"
          >
            <template slot-scope="props">
              <span
                class="bk-lable-primary"
                @click="checkOne(props.row)"
                :title="props.row.sn"
              >
                {{ props.row.sn }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column
            :label="$t(`m.manageCommon['标题']`)"
            min-width="120"
            :show-overflow-tooltip="true"
            :render-header="$renderHeader"
          >
            <template slot-scope="props">
              <span :title="props.row.title">
                {{ props.row.title || "--" }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column
            :label="$t(`m.manageCommon['提单人']`)"
            :show-overflow-tooltip="true"
            :render-header="$renderHeader"
            prop="creator"
          ></bk-table-column>
          <bk-table-column
            :label="$t(`m.manageCommon['提单时间']`)"
            :show-overflow-tooltip="true"
            :render-header="$renderHeader"
            prop="create_at"
          ></bk-table-column>
          <bk-table-column
            :label="$t(`m.manageCommon['状态']`)"
            :show-overflow-tooltip="true"
            :render-header="$renderHeader"
            min-width="120"
          >
            <template slot-scope="props">
              <span
                :title="props.row.current_status_display"
                class="bk-status-color-info"
                :style="getstatusColor(props.row)"
              >
                {{ props.row.current_status_display || "--" }}
              </span>
            </template>
          </bk-table-column>
          <div class="empty" slot="empty">
            <empty
              :is-error="listError"
              @onRefresh="getList()">
            </empty>
          </div>
        </bk-table>
      </div>
      <div class="bk-ticket-button">
        <bk-button
          class="mr10"
          theme="primary"
          :loading="buttonDisabled"
          :disabled="!checkList.length"
          :title="$t(`m.treeinfo['提交']`)"
          @click="bindTicket"
        >
          {{ $t('m.treeinfo["提交"]') }}
        </bk-button>
        <bk-button
          theme="default"
          :disabled="buttonDisabled"
          :title="$t(`m.treeinfo['取消']`)"
          @click="closeOpen"
        >
          {{ $t('m.treeinfo["取消"]') }}
        </bk-button>
      </div>
    </template>
    <template v-else>
      <select-service
        ref="SelectService"
        :custom-id="customId"
        :is-get-field="isGetField"
        @getFieldList="getFieldList"
      >
      </select-service>
      <div v-bkloading="{ isLoading: showField || !fieldList.length }">
        <p class="bk-ticket-title mt20">
          {{ $t('m.manageCommon["单据信息"]') }}
        </p>
        <div class="bk-ticket-content" style="min-height: 50px">
          <field-info ref="fieldInfo" :fields="fieldList">
          </field-info>
        </div>
        <div class="mt20">
          <bk-button
            class="mr10"
            theme="primary"
            :loading="buttonDisabled"
            :title="$t(`m.treeinfo['提交']`)"
            @click="setFields"
          >
            {{ $t('m.treeinfo["提交"]') }}
          </bk-button>
          <bk-button
            theme="default"
            :disabled="buttonDisabled"
            :title="$t(`m.treeinfo['取消']`)"
            @click="closeOpen"
          >
            {{ $t('m.treeinfo["取消"]') }}
          </bk-button>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
  import SelectService from './SelectService.vue';
  import fieldInfo from '@/views/managePage/billCom/fieldInfo.vue';
  import apiFieldsWatch from '@/views/commonMix/api_fields_watch';
  import axios from 'axios';
  import { errorHandler } from '../../../../../utils/errorHandler';
  import Empty from '../../../../../components/common/Empty.vue';

  export default {
    name: 'AssociatedDialog',
    components: {
      SelectService,
      fieldInfo,
      Empty,
    },
    mixins: [apiFieldsWatch],
    props: {
      ticketInfo: {
        type: Object,
        default: () => ({}),
      },
    },
    data() {
      return {
        typeSelectRadio: [
          {
            key: 'associate',
            name: this.$t('m.manageCommon["关联到已有单据"]'),
          },
          {
            key: 'new',
            name: this.$t('m.manageCommon["创建新单"]'),
          },
        ],
        // 表格数据
        tabShowList: [],
        addAssociation: true,
        isTableLoading: false,
        pagination: {
          current: 1,
          count: 10,
          limit: 10,
        },
        checkList: [],
        colorHexList: [],
        // 创建新单
        customId: 'all',
        isGetField: true,
        showField: false,
        fieldList: [],
        typeSelected: 'associate',
        getUrlInfo: '',
        buttonDisabled: false,
        // 搜索信息
        searchInfo: {
          serviceType: [],
          keyword: '',
        },
        listError: false,
      };
    },
    computed: {
      serviceTypeList() {
        return this.$store.state.choice_type_list;
      },
    },
    mounted() {
      this.getList();
      this.getTypeStatus();
    },
    methods: {
      // 切换关联方式时清空fieldList
      clearFieldList() {
        this.fieldList = [];
      },
      checkOne(rowData) {
        const { id } = rowData;
        const { href } = this.$router.resolve({
          name: 'commonInfo',
          params: {
            id,
          },
          query: {
            id: `${id}`,
          },
        });
        window.open(href, '_blank');
      },
      // 获取已有单据列表
      getList() {
        const params = {
          page: this.pagination.current,
          page_size: this.pagination.limit,
          is_draft: 0,
          service_type__in: this.searchInfo.serviceType.join(','),
          // 单号/标题 keyword
          keyword: this.searchInfo.keyword.replace(/(^\s*)|(\s*$)/g, ''),
          access: 'true',
          exclude_ticket_id__in: this.ticketInfo.id,
          project_key: this.ticketInfo.project_key,
        };
        let resUrl = '';
        this.getUrlInfo = '';
        for (const key in params) {
          this.getUrlInfo += `${key}=${params[key]}`;
          resUrl += `${key}=${params[key]}`;
        }
        this.isTableLoading = true;
        this.listError = false;
        this.$store
          .dispatch('change/getList', params)
          .then((res) => {
            if (resUrl !== this.getUrlInfo) {
              return;
            }
            this.tabShowList = res.data.items;
            // 分页
            this.pagination.current = res.data.page;
            this.pagination.count = res.data.count;
          })
          .catch((res) => {
            this.listError = true;
            errorHandler(res, this);
          })
          .finally(() => {
            this.isTableLoading = false;
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
        return !item.has_relationships;
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
      // 搜索
      serviceSearch(val) {
        if (!val && this.searchInfo.serviceType.length) {
          this.getList();
        }
      },
      clearSearch() {
        this.searchInfo.serviceType = [];
        this.getList();
      },
      clearInfo() {
        this.searchInfo.keyword = '';
        this.getList();
      },
      // 获取服务字段并自动填写
      getFieldList() {
        this.showField = true;
        if (!this.$refs.SelectService.formData.service_id) {
          this.fieldList = [];
          return;
        }
        const params = {
          service_id: this.$refs.SelectService.formData.service_id,
        };
        axios
          .all([
            this.$store.dispatch('change/getSubmitFields', params),
            this.$store.dispatch(
              'change/getAllFields',
              this.ticketInfo.id
            ),
          ])
          .then(axios.spread((firstResp, allResp) => {
            firstResp.data.forEach((item) => {
              this.$set(item, 'val', '');
              item.type =                                item.type === 'CASCADE' ? 'SELECT' : item.type;
              this.$set(item, 'showFeild', true);
              this.$set(
                item,
                'service',
                this.$refs.SelectService.formData.key
              );
              allResp.data.forEach((tempResItem) => {
                if (item.key === tempResItem.key) {
                  item.val = tempResItem.value || '';
                }
              });
            });
            this.fieldList = firstResp.data;
            this.isNecessaryToWatch(
              { fields: this.fieldList },
              'submit'
            );
          }))
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.showField = false;
          });
      },
      // 提交函数
      setFields() {
        if (this.disabled) {
          return;
        }
        const SelectServiceForm = {
          catalog_id: this.$refs.SelectService.formData.cascadeId,
          service_id: this.$refs.SelectService.formData.service_id,
          service_type: this.$refs.SelectService.formData.key,
        };
        const formData = {};
        formData.from_ticket_id = this.ticketInfo.id * 1;
        formData.catalog_id = SelectServiceForm.catalog_id;
        formData.service_id = SelectServiceForm.service_id;
        formData.service_type = SelectServiceForm.service_type;
        // 将字段中的时间转换一遍
        formData.fields = [];
        this.$refs.fieldInfo.fieldChange();
        this.fieldList.forEach((item) => {
          formData.fields.push({
            type: item.type,
            id: item.id,
            key: item.key,
            value: item.showFeild ? item.value : '',
            choice: item.choice,
          });
        });
        this.buttonDisabled = true;
        this.$store
          .dispatch('change/submit', formData)
          .then((res) => {
            if (res.code === 'OK') {
              this.$bkMessage({
                message: this.$t('m.common["提交成功！"]'),
                theme: 'success',
              });
              this.$emit('submitSuccess');
            }
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.buttonDisabled = false;
          });
      },
      // 关闭测弹窗
      closeOpen() {
        this.$emit('close');
      },
      bindTicket() {
        const tempList = this.checkList.map(item => item.id);
        const params = {
          from_ticket: this.ticketInfo.id,
          to_tickets: tempList,
        };
        this.$store
          .dispatch('change/bindTicket', params)
          .then(() => {
            this.$bkMessage({
              message: this.$t('m.manageCommon["关联成功"]'),
              theme: 'success',
            });
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.checkList = [];
            this.$emit('submitSuccess');
          });
      },
    },
  };
</script>

<style scoped lang="scss">
@import "../../../../../scss/mixins/clearfix.scss";
@import "../../../../../scss/mixins/scroller.scss";
.bk-ticket-title {
    font-weight: bold;
    font-size: 14px;
    color: #666;
    line-height: 30px;
}
.bk-ticket-content {
    margin-bottom: 20px;
    position: relative;
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
.bk-content-search {
    position: absolute;
    top: -40px;
    right: 0;
}
</style>
