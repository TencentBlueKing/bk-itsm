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
  <!-- 关联单-->
  <div class="bk-log-flow" v-bkloading="{ isLoading: loading }">
    <div class="mb20">
      <bk-button
        class="mr10"
        data-test-id="ticket_button_createAssociateTicket"
        theme="default"
        :title="$t(`m.newCommon['新建']`)"
        @click="openAddAssociation"
      >
        {{ $t('m.newCommon["新建"]') }}
      </bk-button>
      <bk-button
        data-test-id="ticket_button_associateTicketHistory"
        class="icon-cus"
        theme="default"
        icon=" bk-itsm-icon icon-history"
        :disabled="!historyList.length"
        :title="
          historyList.length
            ? $t(`m.newCommon['绑定历史']`)
            : $t(`m.newCommon['暂无关联历史']`)
        "
        @click="showHistory"
      >
      </bk-button>
    </div>
    <bk-table :data="associatedList" :size="'small'" v-bkloading="{ isLoading: associaLoading }">
      <bk-table-column :label="$t(`m.newCommon['单号']`)" min-width="140" :show-overflow-tooltip="true" :render-header="$renderHeader">
        <template slot-scope="props">
          <span
            class="bk-lable-primary"
            @click="checkOne(props.row, 'noInfo')"
            :title="props.row.sn"
          >
            {{ props.row.sn }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.newCommon['工单类型']`)" :show-overflow-tooltip="true" :render-header="$renderHeader">
        <template slot-scope="props">
          {{ props.row.service_type_name || "--" }}
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.newCommon['服务名称']`)" :show-overflow-tooltip="true" :render-header="$renderHeader">
        <template slot-scope="props">
          <span :title="props.row.service_name">{{
            props.row.service_name || "--"
          }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.newCommon['操作']`)" width="100">
        <template slot-scope="props">
          <bk-button
            theme="primary"
            text
            :disabled="!props.row.can_derive"
            @click="unBindDialogShow(props.row)"
          >
            {{ $t('m.newCommon["取消关联"]') }}
          </bk-button>
        </template>
      </bk-table-column>
      <div class="empty" slot="empty">
        <empty
          :is-error="listError"
          @onRefresh="getAssociatesHistory()">
        </empty>
      </div>
    </bk-table>
    <!-- 查看关联历史 -->
    <bk-dialog
      v-model="historyInfo.isShow"
      :render-directive="'if'"
      :title="historyInfo.title"
      :width="historyInfo.width"
      :header-position="historyInfo.headerPosition"
      :auto-close="historyInfo.autoClose"
      :mask-close="historyInfo.autoClose"
    >
      <div style="width: 100%; max-height: 347px">
        <bk-table :data="historyList" :size="'small'">
          <bk-table-column
            :label="$t(`m.newCommon['单号']`)"
            min-width="100"
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
            :label="$t(`m.newCommon['绑定时间']`)"
            prop="create_at"
          ></bk-table-column>
          <bk-table-column
            :label="$t(`m.newCommon['解绑时间']`)"
            prop="end_at"
          ></bk-table-column>
          <div class="empty" slot="empty">
            <empty
              :is-error="historyListError"
              @onRefresh="getAssociates()">
            </empty>
          </div>
        </bk-table>
      </div>
      <div slot="footer">
        <bk-button theme="default" @click="closeHistory">
          {{ $t('m.home["取消"]') }}
        </bk-button>
      </div>
    </bk-dialog>

    <bk-sideslider
      :is-show.sync="isShowAddAssociation"
      :title="$t(`m.manageCommon['新建关联单']`)"
      :quick-close="true"
      :before-close="closeSideslider"
      :width="750"
    >
      <div class="p20" slot="content">
        <associated-dialog
          ref="associated"
          v-if="isShowAddAssociation"
          :ticket-info="ticketInfo"
          @close="isShowAddAssociation = false"
          @submitSuccess="submitSuccess"
        >
        </associated-dialog>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import AssociatedDialog from './AssociatedDialog.vue';
  import { errorHandler } from '@/utils/errorHandler.js';
  import Empty from '../../../../../components/common/Empty.vue';
  export default {
    name: 'AssociatedTab',
    components: {
      AssociatedDialog,
      Empty,
    },
    props: {
      ticketInfo: {
        type: Object,
        default: () => ({}),
      },
    },
    data() {
      return {
        loading: false,
        associaLoading: false,
        isShowAddAssociation: false,
        // 关联单历史信息
        historyInfo: {
          isShow: false,
          width: 700,
          headerPosition: 'left',
          autoClose: false,
          precision: 0,
          title: this.$t('m.newCommon["绑定历史"]'),
        },
        historyList: [],
        associatedList: [],
        listError: false,
        historyListError: false,
      };
    },
    created() {},
    mounted() {
      this.getAssociates();
      this.getAssociatesHistory();
    },
    methods: {
      async getAssociates() {
        const params = {
          id: this.ticketInfo.id,
        };
        this.loading = true;
        this.historyListError = false;
        if (this.$route.query.token) {
          params.token = this.$route.query.token;
        }
        await this.$store
          .dispatch('deployOrder/getAssociatedTickets', params)
          .then((res) => {
            this.associatedList = res.data;
          })
          .catch((res) => {
            this.historyListError = true;
            errorHandler(res, this);
          })
          .finally(() => {
            this.loading = false;
          });
      },
      closeSideslider() {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m["内容未保存，离开将取消操作！"]'),
          confirmLoading: true,
          confirmFn: () => {
            // if (this.$refs.associated.typeSelected === 'associate') {
            //     this.$refs.associated.bindTicket()
            // } else {
            //     this.$refs.associated.setFields()
            // }
            this.isShowAddAssociation = false;
          },
          cancelFn: () => {
            this.isShowAddAssociation = true;
          },
        });
      },
      // 获取关联历史
      getAssociatesHistory() {
        const params = {
          id: this.ticketInfo.id,
          type: 'DERIVE',
        };
        this.associaLoading = true;
        this.listError = false;
        this.$store
          .dispatch('change/getBindHistory', params)
          .then((res) => {
            this.historyList = res.data;
          })
          .catch((res) => {
            this.listError = true;
            errorHandler(res, this);
          })
          .finally(() => {
            this.associaLoading = false;
          });
      },
      openAddAssociation() {
        this.isShowAddAssociation = true;
      },
      showHistory() {
        if (!this.historyList.length) {
          return;
        }
        this.historyInfo.isShow = true;
      },
      closeHistory() {
        this.historyInfo.isShow = false;
      },
      checkOne(rowData) {
        const routeUrl = this.$router.resolve({
          name: 'TicketDetail',
          query: {
            id: `${rowData.id}`,
            from: this.$route.query.from,
          },
        });
        window.open(routeUrl.href, '_blank');
      },
      // 取消关联
      unBindDialogShow(item) {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.manageCommon["确认取消关联？"]'),
          subTitle: this.$t('m.manageCommon["取消关联后，无法查看之间的关联信息"]'),
          confirmFn: () => {
            this.unBind(item);
          },
        });
      },
      async unBind(item) {
        const params = {
          from_ticket: this.ticketInfo.id,
          to_ticket: item.id,
        };
        await this.$store
          .dispatch('change/unbindTicket', params)
          .then(() => {
            this.$bkMessage({
              message: this.$t('m.manageCommon["取消关联成功"]'),
              theme: 'success',
            });
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.getAssociates();
            this.getAssociatesHistory();
          });
      },
      submitSuccess() {
        this.isShowAddAssociation = false;
        this.getAssociates();
        this.getAssociatesHistory();
      },
    },
  };
</script>
<style lang="scss" scoped></style>
