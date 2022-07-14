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
  <div class="bk-dialog-form bk-change">
    <div class="bk-itsm-version" v-if="versionStatus">
      <span>{{ $t('m.newCommon["新建母子单："]') }}</span>
      <span>
        {{
          $t(
            'm.newCommon["可以通过母子单的创建，将一些需要进行相同处理操作的同类单据进行关联。一个母单可以关联多个子单，一个子单只能关联到一个母单。一旦关联，子单将冻结操作，子单的状态将全部跟随母单更新。"]'
          )
        }}
      </span>
      <i class="bk-icon icon-close" @click="closeVersion"></i>
    </div>
    <p class="bk-ticket-title">
      {{ $t('m.newCommon["选择以下单据作为"]') }}
    </p>
    <div class="bk-ticket-content">
      <bk-radio-group v-model="templateInfo.inheritType">
        <template v-for="radio in templateInfo.options">
          <bk-radio
            :value="radio.key"
            :key="radio.key"
            class="mr20"
            :disabled="getFlag(radio.key, ticketInfo)"
            @change="changeRadio"
          >
            {{ radio.name }}
          </bk-radio>
        </template>
      </bk-radio-group>
    </div>
    <p class="bk-ticket-title">
      {{ $t('m.manageCommon["可关联的列表"]') }}
    </p>
    <div class="bk-ticket-content">
      <div class="bk-content-search">
        <bk-input
          style="width: 200px; float: left"
          :clearable="true"
          :right-icon="'bk-icon icon-search'"
          v-model="searchForm.keyword"
          @enter="getList"
          @clear="clearInfo"
        ></bk-input>
      </div>
      <bk-table
        v-bkloading="{ isLoading: isDataLoading }"
        :data="tabInfoList"
        :size="'small'"
        :pagination="pagination"
        @page-change="handlePageChange"
        @page-limit-change="handlePageLimitChange"
      >
        <bk-table-column
          width="60"
          align="center"
          :render-header="renderRadio"
        >
          <template slot-scope="props">
            <bk-checkbox
              v-if="templateInfo.inheritType === 'chooseChild'"
              :value="props.row.check"
              :disabled="getItemFlag(props.row)"
              @change="checkOne(props.row)"
            ></bk-checkbox>
            <bk-radio
              v-else
              :value="props.row.check"
              :disabled="getItemFlag(props.row)"
              @change="checkOne(props.row)"
            ></bk-radio>
          </template>
        </bk-table-column>
        <bk-table-column
          :label="$t(`m.newCommon['单号']`)"
          min-width="120"
        >
          <template slot-scope="props">
            <span
              class="bk-lable-primary"
              @click="openNewPage(props.row)"
              :title="props.row.sn"
            >
              {{ props.row.sn }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column
          :label="$t(`m.manageCommon['标题']`)"
          prop="title"
          min-width="100"
        ></bk-table-column>
        <bk-table-column
          :label="$t(`m.manageCommon['提单人']`)"
          prop="creator"
        ></bk-table-column>
        <bk-table-column
          :label="$t(`m.manageCommon['提单时间']`)"
          prop="create_at"
        ></bk-table-column>
        <bk-table-column
          :label="$t(`m.manageCommon['状态']`)"
          min-width="80"
        >
          <template slot-scope="props">
            <span
              :title="props.row.current_status_display"
              class="bk-status-color-info"
              :style="getstatusColor(props.row)"
            >
              {{
                localeCookie
                  ? props.row.current_status_display
                  : props.row.current_status
              }}
            </span>
          </template>
        </bk-table-column>
      </bk-table>
    </div>
    <div class="bk-state-button">
      <bk-button
        class="mr10"
        theme="primary"
        :loading="secondClick"
        :disabled="!getButtonFlag()"
        :title="$t(`m.treeinfo['提交']`)"
        @click="submitTemplate"
      >
        {{ $t('m.treeinfo["提交"]') }}
      </bk-button>
      <bk-button
        theme="default"
        :disabled="secondClick"
        :title="$t(`m.treeinfo['取消']`)"
        @click="closeShow"
      >
        {{ $t('m.treeinfo["取消"]') }}
      </bk-button>
    </div>
  </div>
</template>

<script>
  import { errorHandler } from '../../../../utils/errorHandler';
  import cookie from 'cookie';

  export default {
    name: 'InheritTicketAddDialog',
    inject: ['reloadTicket'],
    props: {
      ticketInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      templateInfo: {
        type: Object,
        required: false,
        default: () => ({
          openShow: false,
          options: [],
          inheritType: 'chooseMother',
          currentInheritType: 'chooseChild',
          otherTitle: this.$t('m.newCommon["新建母子单"]'),
        }),
      },
    },
    data() {
      return {
        secondClick: false,
        tabInfoList: [],
        isDataLoading: false,
        getUrlInfo: '',
        searchForm: {
          keyword: '',
          creator: [],
          levelService: '',
          service: '',
          current_status: 0,
          processors: '',
          sn_title: '',
          view_type: '',
        },
        versionStatus: true,
        pagination: {
          current: 1,
          count: 10,
          limit: 10,
        },
        checkList: [],
        colorHexList: [],
        localeCookie: false,
      };
    },
    computed: {
      changeFields() {
        return this.fields;
      },
      fileStatus() {
        return this.$store.state.fileStatus;
      },
      // 选择
      allCheck() {
        return (
          this.tabInfoList.length
          && this.tabInfoList.filter(ticket => !this.getItemFlag(ticket))
            .length
          && this.tabInfoList.every(item => item.check || this.getItemFlag(item))
        );
      },
    },
    watch: {
      'templateInfo.inheritType'() {
        this.getList();
      },
    },
    async mounted() {
      if (this.ticketInfo.related_type === 'master') {
        this.templateInfo.inheritType = 'chooseChild';
      }
      await this.getTypeStatus();
      await this.getList();
      this.localeCookie =            cookie.parse(document.cookie).blueking_language !== 'zh-cn';
    },
    methods: {
      getFlag(flag, info) {
        const flag1 =                flag === 'chooseMother'
          && (info.related_type === 'slave'
          || info.related_type === 'master');
        const flag2 =                flag === 'chooseChild' && info.related_type === 'slave';
        return flag1 || flag2;
      },
      openNewPage(rowData) {
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
      changeRadio() {
        if (
          this.templateInfo.currentInheritType
          === this.templateInfo.inheritType
        ) {
          return;
        }
        this.templateInfo.currentInheritType =                this.templateInfo.inheritType;
        this.tabInfoList.forEach((item) => {
          item.check = false;
        });
      },
      // 判断单据是否可选
      getItemFlag(item) {
        return (
          (this.templateInfo.inheritType === 'chooseMother'
          && item.chooseMotherDisabled)
          || (this.templateInfo.inheritType === 'chooseChild'
          && item.chooseChildDisabled)
          || this.ticketInfo.related_type === 'slave'
        );
      },
      // 判断是否可以提交
      getButtonFlag() {
        return this.tabInfoList.find(item => item.check);
      },
      // 单选
      checkOne(item) {
        const check = JSON.parse(JSON.stringify(item.check));
        if (this.templateInfo.inheritType === 'chooseMother') {
          this.tabInfoList.forEach((item) => {
            item.check = false;
          });
        }
        item.check = !check;
        this.$forceUpdate();
      },
      // 获取列表
      async getList() {
        const params = {
          page: this.pagination.current,
          page_size: this.pagination.limit,
          is_draft: 0,
          // 单号/标题 keyword
          keyword: this.searchForm.keyword
            ? this.searchForm.keyword.replace(/(^\s*)|(\s*$)/g, '')
              || this.searchForm.sn_title.replace(/(^\s*)|(\s*$)/g, '')
            : '',
          // 提单人
          flow_id: this.ticketInfo.flow_id,
          exclude_ticket_id__in: this.ticketInfo.id,
          current_status__in: this.colorHexList
            .map((status) => {
              if (!status.is_over) {
                return status.key;
              }
            })
            .join(','),
        };
        let resUrl = '';
        this.getUrlInfo = '';
        for (const key in params) {
          this.getUrlInfo += `${key}=${params[key]}`;
          resUrl += `${key}=${params[key]}`;
        }
        this.isDataLoading = true;
        await this.$store
          .dispatch('change/getList', params)
          .then((res) => {
            if (resUrl !== this.getUrlInfo) {
              return;
            }
            this.tabInfoList = res.data.items;
            // 分页
            this.pagination.current = res.data.page;
            this.pagination.count = res.data.count;

            this.tabInfoList.forEach((item) => {
              this.$set(item, 'check', false);
              this.$set(
                item,
                'chooseMotherDisabled',
                item.related_type === 'slave'
              );
              this.$set(
                item,
                'chooseChildDisabled',
                item.related_type === 'master'
                  || item.related_type === 'slave'
              );
            });
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
      handleSelectAll() {
        if (this.allCheck) {
          this.tabInfoList.forEach((item) => {
            if (!this.getItemFlag(item)) {
              item.check = false;
            }
          });
        } else {
          this.tabInfoList.forEach((item) => {
            if (!this.getItemFlag(item)) {
              item.check = true;
            }
          });
        }
        this.$forceUpdate();
      },
      getstatusColor(row) {
        const statusColor = this.colorHexList.filter(item => item.key === row.current_status);
        return statusColor.length
          ? {
            color: statusColor[0].color_hex,
            border: `1px solid ${statusColor[0].color_hex}`,
          }
          : { color: '#3c96ff', border: '1px solid #3c96ff' };
      },
      async getTypeStatus() {
        const params = {};
        const type = this.ticketInfo.service_type;
        await this.$store
          .dispatch('ticketStatus/getTypeStatus', { type, params })
          .then((res) => {
            this.colorHexList = res.data;
          })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      clearInfo() {
        this.searchForm.keyword = '';
        this.getList();
      },
      closeShow() {
        this.$emit('close');
      },
      submitTemplate() {
        const params = {};
        if (this.templateInfo.inheritType === 'chooseChild') {
          params.from_ticket_ids = this.tabInfoList
            .filter(item => item.check)
            .map(ite => ite.id);
          params.to_ticket_id = this.ticketInfo.id;
        } else {
          params.from_ticket_ids = [this.ticketInfo.id];
          params.to_ticket_id = this.tabInfoList
            .filter(item => item.check)
            .map(ite => ite.id)[0];
        }
        if (this.secondClick) {
          return;
        }
        this.secondClick = true;
        this.$store
          .dispatch('change/mergeTickets', params)
          .then(() => {
            this.$bkMessage({
              message: this.$t('m.newCommon["关联成功"]'),
              theme: 'success',
            });
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.secondClick = false;
            this.checkList = [];
            this.closeShow();
            this.reloadTicket();
          });
      },
      closeVersion() {
        this.versionStatus = false;
      },
      renderRadio(h) {
        if (this.templateInfo.inheritType === 'chooseMother') {
          return h('bk-radio', {
            props: {
              disabled: true,
            },
          });
        }
        return h('bk-checkbox', {
          props: {
            value: this.allCheck,
            disabled:
              !this.tabInfoList.length
              || !this.tabInfoList.find(item => !this.getItemFlag(item)),
          },
          on: {
            change: this.handleSelectAll,
          },
        });
      },
    },
  };
</script>

<style lang="scss" scoped>
.bk-ticket-title {
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
