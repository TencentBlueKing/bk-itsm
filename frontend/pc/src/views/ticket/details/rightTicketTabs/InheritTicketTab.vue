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
  <div class="bk-flowlog-inherit">
    <div class="mb20">
      <bk-button
        :theme="'default'"
        class="mr10"
        data-test-id="ticket_button_createInheritTicket"
        :title="
          ticketInfo.is_over || !ticketInfo.can_operate
            ? $t(`m.newCommon['暂无权限或单据已结束']`)
            : $t(`m.newCommon['新建']`)
        "
        :disabled="ticketInfo.is_over || !ticketInfo.can_operate"
        @click="openAddInheritSlider"
      >
        {{ $t('m.newCommon["新建"]') }}
      </bk-button>
      <bk-button
        :theme="'default'"
        class="icon-cus"
        data-test-id="ticket_button_InheritTicketBindingHistory"
        :title="
          historyList.length
            ? $t(`m.newCommon['绑定历史']`)
            : $t(`m.newCommon['暂无关联历史']`)
        "
        icon=" bk-itsm-icon icon-history"
        :disabled="!historyList.length"
        @click="showHistory"
      >
      </bk-button>
    </div>
    <div
      class="mb20"
      v-if="masterOrSlave === 'slave' || !inheritStateList.length"
    >
      <p class="inherit-table-tittle">{{ $t('m.newCommon["母单"]') }}</p>
      <bk-table
        v-bkloading="{ isLoading: tableLoading }"
        :data="inheritStateList"
        :size="'small'"
      >
        <bk-table-column
          :label="$t(`m.newCommon['单号']`)"
          min-width="140"
          :show-overflow-tooltip="true"
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
        <bk-table-column :label="$t(`m.newCommon['绑定时间']`)" :render-header="$renderHeader" :show-overflow-tooltip="true">
          <template slot-scope="props">
            <span
              v-if="props.row.related_status === 'UNBIND_FAILED'"
              class="bk-failed-status"
            ></span>
            <i
              v-if="props.row.related_status === 'RUNNING'"
              class="bk-itsm-icon icon-inherit-loading bk-running-status"
            ></i>
            <span
              v-if="
                props.row.related_status === 'UNBIND_FAILED' ||
                  props.row.related_status === 'RUNNING'
              "
            >{{ props.row.status }}</span
            >
            <span v-else>{{ props.row.bind_at }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.newCommon['操作']`)" width="100">
          <template slot-scope="props">
            <bk-button
              theme="primary"
              text
              :disabled="props.row.related_status === 'RUNNING'"
              @click="giveUnbindInfo('one', props.row)"
            >
              {{ $t('m.newCommon["取消关联"]') }}
            </bk-button>
          </template>
        </bk-table-column>
        <div class="empty" slot="empty">
          <empty
            :is-error="listError"
            @onRefresh="getInheritStateList()">
          </empty>
        </div>
      </bk-table>
    </div>
    <div
      class="mb20"
      v-if="masterOrSlave === 'master' || !inheritStateList.length"
    >
      <p class="inherit-table-tittle">{{ $t('m.newCommon["子单"]') }}</p>
      <bk-table
        v-bkloading="{ isLoading: tableLoading }"
        :data="inheritStateList"
        :size="'small'"
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
          :label="$t(`m.newCommon['单号']`)"
          min-width="140"
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
        <bk-table-column :label="$t(`m.newCommon['绑定时间']`)">
          <template slot-scope="props">
            <span
              v-if="props.row.related_status === 'UNBIND_FAILED'"
              class="bk-failed-status"
            ></span>
            <i
              v-if="props.row.related_status === 'RUNNING'"
              class="bk-itsm-icon icon-inherit-loading bk-running-status loading"
            ></i>
            <span
              v-if="
                props.row.related_status === 'UNBIND_FAILED' ||
                  props.row.related_status === 'RUNNING'
              "
            >{{ props.row.status }}</span
            >
            <span v-else>{{ props.row.bind_at }}</span>
          </template>
        </bk-table-column>
      </bk-table>
    </div>
    <div class="inherit-bottom-button">
      <bk-button
        data-test-id="ticket_button_batchUnbind"
        theme="default"
        :title="$t(`m.newCommon['批量解绑']`)"
        :disabled="!checkList.length"
        @click="giveUnbindInfo('batch')"
      >
        {{ $t('m.newCommon["批量解绑"]') }}
      </bk-button>
    </div>
    <bk-dialog
      v-model="historyInfo.isShow"
      :render-directive="'if'"
      :title="historyInfo.title"
      :width="historyInfo.width"
      :header-position="historyInfo.headerPosition"
      :loading="secondClick"
      :auto-close="historyInfo.autoClose"
      :mask-close="historyInfo.autoClose"
    >
      <div style="width: 100%; max-height: 347px">
        <bk-table
          v-bkloading="{ isLoading: historyTableLoading }"
          :data="historyList"
          :size="'small'"
        >
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
            :label="$t(`m.newCommon['状态']`)"
            width="80"
          >
            <template slot-scope="props">
              {{
                props.row.related_type === "master"
                  ? $t('m.newCommon["母单"]')
                  : $t('m.newCommon["子单"]')
              }}
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
        </bk-table>
      </div>
      <div slot="footer">
        <bk-button theme="default" @click="closeHistory">
          {{ $t('m.home["取消"]') }}
        </bk-button>
      </div>
    </bk-dialog>

    <!-- 新建母子单 -->
    <bk-sideslider
      :is-show.sync="isShowAddInheritTicket"
      :quick-close="true"
      :title="$t(`m.newCommon['新建母子单']`)"
      :before-close="closeSideslider"
      :width="750"
    >
      <div class="p20" slot="content">
        <inherit-ticket-add-dialog
          ref="addInheritTicket"
          v-if="isShowAddInheritTicket"
          :template-info="inheritStateInfo"
          :ticket-info="ticketInfo"
          @close="isShowAddInheritTicket = false"
        >
        </inherit-ticket-add-dialog>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import InheritTicketAddDialog from './InheritTicketAddDialog';
  import { errorHandler } from '@/utils/errorHandler';
  import Empty from '../../../../components/common/Empty.vue';

  export default {
    name: 'InheritTicketTab',
    components: {
      InheritTicketAddDialog,
      Empty,
    },
    inject: ['reloadTicket'],
    props: {
      ticketInfo: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        isShowAddInheritTicket: false,
        secondClick: false,
        masterOrSlave: '',
        inheritStateList: [],
        tableLoading: false,
        childTableLoading: false,
        historyTableLoading: false,
        historyInfo: {
          isShow: false,
          width: 700,
          headerPosition: 'left',
          autoClose: false,
          precision: 0,
          title: this.$t('m.newCommon["绑定历史"]'),
        },
        inheritStateInfo: {
          options: [
            {
              key: 'chooseMother',
              name: this.$t('m.newCommon["母单"]'),
            },
            {
              key: 'chooseChild',
              name: this.$t('m.newCommon["子单"]'),
            },
          ],
          inheritType: 'chooseMother',
          otherTitle: this.$t('m.newCommon["新建母子单"]'),
        },
        historyList: [],
        unBindInfo: {
          type: 'throwMother',
          title: '',
          content: '',
        },
        unBindItem: '',
        checkList: [],
        listError: false,
      };
    },
    async mounted() {
      this.getInheritStateList();
      await this.getHistoryList();
    },
    methods: {
      closeSideslider() {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m["内容未保存，离开将取消操作！"]'),
          confirmLoading: true,
          confirmFn: () => {
            this.isShowAddInheritTicket = false;
          },
          cancelFn: () => {
            this.isShowAddInheritTicket = true;
          },
        });
      },
      showHistory() {
        if (!this.historyList.length) {
          return;
        }
        this.historyInfo.isShow = true;
      },
      giveUnbindInfo(type, item = {}) {
        if (type === 'batch') {
          this.unBindItem = this.inheritStateList.map(item => item.id);
          this.unBindInfo.type = 'throwChild';
          this.unBindInfo.title = this.$t('m.newCommon["确认解绑子单？"]');
          this.unBindInfo.content = this.$t('m.newCommon["解绑后，子单将不会同步母单状态及处理信息，单据的后续处理各自独立，不在影响"]');
        } else {
          if (item.related_status === 'RUNNING') {
            return;
          }
          this.unBindItem = item;
          this.unBindInfo.type = 'throwMother';
          this.unBindInfo.title = this.$t('m.newCommon["确认解绑母单？"]');
          this.unBindInfo.content = this.$t('m.newCommon["解绑后，母单将不会同步子单状态及处理信息，单据的后续处理各自独立，不在影响"]');
        }
        this.$bkInfo({
          type: 'warning',
          title: this.unBindInfo.title,
          subTitle: this.unBindInfo.content,
          confirmFn: () => {
            this.unbindFun();
          },
        });
      },
      getInheritStateList() {
        const params = {
          id: this.ticketInfo.id,
        };
        if (this.$route.query.token) {
          params.token = this.$route.query.token;
        }
        this.tableLoading = true;
        this.listError = false;
        this.$store
          .dispatch('change/getInheritState', params)
          .then((res) => {
            this.masterOrSlave = res.data.related_type;

            this.inheritStateList = res.data.master_slave_tickets.map((item) => {
              let tempStatusName = '';
              switch (item.related_status) {
                case 'BIND_SUCCESS':
                  tempStatusName =                                        this.$t('m.newCommon["已绑定"]');
                  break;
                case 'BIND_FAILED':
                  tempStatusName = this.$t('m.newCommon["绑定失败"]');
                  break;
                case 'UNBIND_SUCCESS':
                  tempStatusName = this.$t('m.newCommon["解绑成功"]');
                  break;
                case 'RUNNING':
                  tempStatusName =                                        this.$t('m.newCommon["解绑中"]');
                  break;
                case 'UNBIND_FAILED':
                  tempStatusName = this.$t('m.newCommon["解绑失败"]');
                  break;
                default:
                  break;
              }
              return { ...item, status: tempStatusName };
            });
          })
          .catch((res) => {
            this.listError = true;
            errorHandler(res, this);
          })
          .finally(() => {
            this.tableLoading = false;
          });
      },
      // 全选 半选
      handleSelectAll(selection) {
        this.checkList = selection;
      },
      handleSelect(selection) {
        this.checkList = selection;
      },
      disabledFn() {
        return this.masterOrSlave !== 'slave';
      },
      openAddInheritSlider() {
        if (this.ticketInfo.is_over) {
          return;
        }
        this.isShowAddInheritTicket = true;
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
      unbindFun() {
        const params = {};
        if (this.unBindInfo.type === 'throwMother') {
          params.master_ticket_id = this.unBindItem.id;
          params.slave_ticket_ids = [this.ticketInfo.id];
        } else {
          params.master_ticket_id = this.ticketInfo.id;
          params.slave_ticket_ids = this.checkList.map(it => it.id);
        }
        if (this.secondClick) {
          return;
        }
        this.secondClick = true;
        this.$store
          .dispatch('change/unBindInherit', params)
          .then(() => {
            this.$bkMessage({
              message: this.$t('m.newCommon["解绑成功"]'),
              theme: 'success',
            });
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.checkList = [];
            this.secondClick = false;
            this.getInheritStateList();
            this.getHistoryList();
            // this.reloadTicket()
          });
      },
      async getHistoryList() {
        const params = {
          id: this.ticketInfo.id,
          type: 'MASTER_SLAVE',
        };
        await this.$store
          .dispatch('change/getBindHistory', params)
          .then((res) => {
            this.historyList = res.data;
          })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      closeHistory() {
        this.historyInfo.isShow = false;
      },
    },
  };
</script>

<style scoped lang="scss">
.icon-cus {
    font-size: 18px;
    padding: 0 9px !important;
    /deep/ .bk-itsm-icon {
        top: 0;
        width: auto;
    }
}
.inherit-table-tittle {
    font-size: 14px;
    font-weight: bold;
    display: inline-block;
    line-height: 36px;
    height: 36px;
    color: #6e656e;
}
.bk-failed-status {
    display: inline-block;
    height: 8px;
    width: 8px;
    background-color: #ff5656;
    border-radius: 50%;
    margin-right: 5px;
}
.bk-running-status {
    display: inline-block;
    margin-right: 5px;
}
.loading {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    animation: loading 2s linear 0.2s infinite;
}

@keyframes loading {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}
</style>
