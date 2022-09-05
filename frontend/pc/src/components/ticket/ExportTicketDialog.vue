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
  <bk-dialog
    :value="isShow"
    :render-directive="'if'"
    :width="exportInfo.width"
    :header-position="exportInfo.headerPosition"
    :loading="false"
    :auto-close="false"
    :mask-close="false"
    :title="$t(`m.tickets['请勾选需要导出的字段']`)"
    @cancel="cancelExport">
    <div class="export-content" v-bkloading="{ isLoading: exportInfo.serviceFieldLoading }">
      <h3 class="export-section-title">{{ $t(`m.tickets['通用字段']`) }}</h3>
      <p class="pb20">
        <bk-checkbox
          :true-value="true"
          :false-value="false"
          v-model="exportInfo.allCheck"
          @change="checkAll('general')">
          {{ $t(`m.tickets['全选']`) }}
        </bk-checkbox>
      </p>
      <bk-checkbox-group v-model="exportInfo.checkList">
        <template v-for="item in exportFieldsList">
          <bk-checkbox
            :value="item.id"
            :key="item.id"
            class="mr10 mb10"
            @change="checkOne('general', item)">
            {{item.name}}
          </bk-checkbox>
        </template>
      </bk-checkbox-group>
      <!-- 单服务提单信息 -->
      <h3 class="export-section-title">{{ $t(`m.tickets['提单字段']`) }}</h3>
      <template v-if="exportInfo.serviceFieldsList.length">
        <p class="pb20">
          <bk-checkbox
            :true-value="true"
            :false-value="false"
            v-model="exportInfo.serviceAllCheck"
            @change="checkAll('service')">
            {{ $t(`m.tickets['全选']`) }}
          </bk-checkbox>
        </p>
        <bk-checkbox-group v-model="exportInfo.serviceCheckList">
          <template v-for="item in exportInfo.serviceFieldsList">
            <bk-checkbox
              :value="item.id"
              :key="item.id"
              :disabled="item.disabled"
              class="mr10 mb10"
              @change="checkOne('service', item)">
              {{item.name}}
            </bk-checkbox>
          </template>
        </bk-checkbox-group>
      </template>
      <p v-else class="export-section-desc">{{ $t(`m.tickets['未指定服务，请先选择服务：']`) }}
        <bk-select
          v-model="exportInfo.serviceId"
          ext-cls="export-service-select"
          searchable
          :loading="serviceListLoading"
          @change="onServiceChange">
          <bk-option v-for="option in exportInfo.serviceList"
            :key="option.id"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
      </p>
    </div>
    <div slot="footer">
      <bk-button
        theme="primary"
        :disabled="!exportInfo.checkList.length"
        @click="submitExport">
        {{ $t('m.treeinfo["确定"]') }}
      </bk-button>
      <bk-button
        theme="default"
        @click="cancelExport">
        {{ $t('m.newCommon["取消"]') }}
      </bk-button>
    </div>
  </bk-dialog>
</template>

<script>
  import { errorHandler } from '@/utils/errorHandler';
  import { isEmpty } from '../../utils/util';
  export default {
    name: 'ExportTicketDialog',
    components: {},
    props: {
      isShow: {
        type: Boolean,
        default: false,
      },
      pagination: {
        type: Object,
        default: () => ({}),
      },
      viewType: {
        type: String,
        default: '',
      },
      searchParams: {
        type: Object,
        default: () => ({}),
      },
    },
    data() {
      return {
        serviceListLoading: false,
        // 导出
        exportInfo: {
          serviceFieldLoading: false,
          width: 700,
          headerPosition: 'left',
          allCheck: false,
          checkList: [],
          serviceCheckList: [],
          serviceFieldsList: [],
          serviceList: [],
          serviceId: '',
        },
      };
    },
    computed: {
      exportFieldsList() {
        return this.$store.state.common.wayInfo.export_fields;
      },
    },
    watch: {
      isShow(val) {
        if (val) {
          this.initData();
        }
      },
    },
    methods: {
      async initData() {
        this.exportInfo = {
          serviceFieldLoading: false,
          width: 700,
          headerPosition: 'left',
          allCheck: false,
          serviceAllCheck: false,
          checkList: [],
          serviceCheckList: [],
          serviceFieldsList: [],
          serviceList: [],
          serviceId: '',
        };
        // 搜索条件中有且只有一个服务，则可以导出提单字段
        const catalogId = this.searchParams.catalog_id;
        const serviceId = this.searchParams.service_id__in;
        if (catalogId && !serviceId) { // 选择了目录没有选服务
          this.getServiceData(catalogId);
        } else if (!isEmpty(serviceId) && serviceId.split(',').length === 1) { // 选择了一个服务
          this.getServiceFieldList(serviceId);
        } else if (!isEmpty(serviceId) && serviceId.split(',').length > 1) { // 选择了多个服务，只能在这几个服务中选
          await this.getServiceList();
          const serviceIds = serviceId.split(',');
          this.exportInfo.serviceList = this.exportInfo.serviceList.filter(item => serviceIds.includes(String(item.id)));
        } else { // 其他，可以选择任意服务
          this.getServiceList();
        }
      },
      // 获取所有服务
      async getServiceList() {
        this.serviceListLoading = true;
        try {
          const resp = await this.$store.dispatch('service/getServiceList');
          this.exportInfo.serviceList = resp.data;
        } catch (e) {
          console.error(e);
        } finally {
          this.serviceListLoading = false;
        }
      },
      // 根据服务目录获取服务
      getServiceData(val) {
        this.serviceListLoading = true;
        const params = {
          catalog_id: val,
          is_valid: 1,
        };
        this.$store.dispatch('catalogService/getServices', params).then((resp) => {
          this.exportInfo.serviceList = resp.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.serviceListLoading = false;
          });
      },
      // 导出弹框全选变化
      checkAll(type) {
        if (type === 'general') {
          if (this.exportInfo.checkList.length === this.exportFieldsList.length) {
            this.exportInfo.checkList = [];
            this.exportInfo.allCheck = false;
          } else {
            this.exportInfo.checkList = this.exportFieldsList.map(item => item.id);
            this.exportInfo.allCheck = true;
          }
        } else {
          if (this.exportInfo.serviceCheckList.length === this.exportInfo.serviceFieldsList.length) {
            this.exportInfo.serviceCheckList = [];
            this.exportInfo.serviceAllCheck = false;
          } else {
            this.exportInfo.serviceCheckList = this.exportInfo.serviceFieldsList.map(item => item.id);
            this.exportInfo.serviceAllCheck = true;
          }
        }
      },
      // 导出弹框checkbox变化
      checkOne(type, item) {
        const { checkList, serviceCheckList } = this.exportInfo;
        if (type === 'general') {
          if (checkList.some(checkItem => checkItem === item.id)) {
            this.exportInfo.checkList = checkList.filter(checkItem => checkItem !== item.id);
          } else {
            this.exportInfo.checkList.push(item.id);
          }
          this.exportInfo.allCheck = this.exportInfo.checkList.length === this.exportFieldsList.length;
        } else {
          if (serviceCheckList.some(checkItem => checkItem === item.id)) {
            this.exportInfo.serviceCheckList = serviceCheckList.filter(checkItem => checkItem !== item.id);
          } else {
            this.exportInfo.serviceCheckList.push(item.id);
          }
          this.exportInfo.serviceAllCheck = this.exportInfo.serviceCheckList.length === this.exportInfo.serviceFieldsList.length;
        }
      },
      submitExport() {
        const params = {
          page_size: this.pagination.limit,
          page: this.pagination.current,
          ordering: '-create_at',
          is_draft: 0,
          view_type: this.viewType,
          export_fields: this.exportInfo.checkList.toString(),
          ...this.searchParams,
        };

        // 如果是通过导出选择的服务，则覆盖原本高级搜索中的服务参数
        if (this.exportInfo.serviceId) {
          params.service_id__in = this.exportInfo.serviceId;
        }

        let base64ServiceFields;
        const { serviceCheckList } = this.exportInfo;
        if (serviceCheckList.length) {
          const serviceId = params.service_id__in;
          try {
            const params = JSON.stringify({
              [serviceId]: serviceCheckList,
            });
            base64ServiceFields = window.btoa(params);
          } catch (error) {
            errorHandler(error, this);
          }
        }
        const { resolved } = this.$router.resolve({
          path: `${window.SITE_URL}api/ticket/receipts/export_group_by_service/`,
          query: params,
        });
        const url = resolved.fullPath + (base64ServiceFields ? `&service_fields=${base64ServiceFields}` : '');
        console.log(url);
        window.open(url);
      },
      // 取消导出
      cancelExport() {
        this.$emit('close');
        this.exportInfo.checkList = [];
        this.exportInfo.allCheck = false;
      },
      getServiceFieldList(serviceId) {
        this.exportInfo.serviceFieldLoading = true;
        const params = {
          service_id: serviceId,
        };
        return this.$store.dispatch('change/getSubmitFields', params).then(async (res) => {
          const disabledTypes = ['TABLE', 'CUSTOMTABLE', 'FILE']; // 不能导出的字段
          this.exportInfo.serviceFieldsList = res.data.map(field => ({
            id: field.key,
            name: field.name,
            disabled: disabledTypes.includes(field.type),
          }));
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.exportInfo.serviceFieldLoading = false;
          });
      },
      onServiceChange(id) {
        this.getServiceFieldList(id);
      },
    },
  };
</script>
<style lang='scss' scoped>
.export-section-title {
    font-size: 16px;
    color: #63656e;
}
.export-section-desc {
    font-size: 14px;
    color: #979ba5;
}
.export-service-select {
    width: 250px;
    display: inline-block;
    vertical-align: middle;
}
</style>
