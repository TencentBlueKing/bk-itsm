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
  <div class="bk-task-history" v-bkloading="{ isLoading: loading }" :style="!isShowSla ? 'height: calc(100vh - 436px);' : 'height: calc(100vh - 320px);'">
    <div class="history-table">
      <bk-collapse v-model="activeName">
        <bk-collapse-item name="ticket">
          {{$t(`m['单据触发器']`)}}
          <div slot="content" class="f13">
            <bk-table
              :header-cell-attributes="headerCellAttributes"
              :data="ticketAction"
              :size="'small'"
              @sort-change="orderingClick">
              <bk-table-column :label="$t(`m.task['执行时间']`)" :render-header="$renderHeader" :show-overflow-tooltip="true" :sortable="'custom'">
                <template slot-scope="props">
                  <span :title="props.row.end_time">
                    {{props.row.end_time || '--'}}
                  </span>
                </template>
              </bk-table-column>
              <bk-table-column :label="$t(`m.task['响应动作']`)" :render-header="$renderHeader" :show-overflow-tooltip="true">
                <template slot-scope="props">
                  <span
                    :title="props.row.display_name"
                    style="color: #3A84FF;cursor: pointer"
                    @click="openDetail(props.row)">
                    {{props.row.component_name || '--'}}
                  </span>
                </template>
              </bk-table-column>
              <bk-table-column :label="$t(`m.task['执行状态']`)" :render-header="$renderHeader" :show-overflow-tooltip="true" :sortable="'custom'">
                <template slot-scope="props">
                  <span class="bk-status-success"
                    :class="{ 'bk-status-failed': props.row.status === 'FAILED' }"
                    :title="props.row.status_name">
                    {{props.row.status_name || '--'}}
                  </span>
                </template>
              </bk-table-column>
              <bk-table-column :label="$t(`m.task['操作人']`)" :render-header="$renderHeader" :show-overflow-tooltip="true">
                <template slot-scope="props">
                  <span :title="props.row.operator_username">
                    {{props.row.operator_username || '--'}}
                  </span>
                </template>
              </bk-table-column>
              <div class="empty" slot="empty">
                <empty
                  :is-error="listError"
                  @onRefresh="getHistoryList()">
                </empty>
              </div>
            </bk-table>
          </div>
        </bk-collapse-item>
        <bk-collapse-item :name="item.name" v-for="item in nodeActions" :key="item.name">
          {{$t(`m['节点']`) + '：' + item.name}}
          <div slot="content" class="f13">
            <bk-table
              :data="item.actions"
              :size="'small'"
              @sort-change="orderingClick">
              <bk-table-column :label="$t(`m.task['执行时间']`)" :show-overflow-tooltip="true" :sortable="'custom'">
                <template slot-scope="props">
                  <span :title="props.row.end_time">
                    {{props.row.end_time || '--'}}
                  </span>
                </template>
              </bk-table-column>
              <bk-table-column :label="$t(`m.task['响应动作']`)" :show-overflow-tooltip="true">
                <template slot-scope="props">
                  <span
                    :title="props.row.display_name"
                    style="color: #3A84FF;cursor: pointer"
                    @click="openDetail(props.row)">
                    {{props.row.component_name || '--'}}
                  </span>
                </template>
              </bk-table-column>
              <bk-table-column :label="$t(`m.task['执行状态']`)" :show-overflow-tooltip="true" :sortable="'custom'">
                <template slot-scope="props">
                  <span class="bk-status-success"
                    :class="{ 'bk-status-failed': props.row.status === 'FAILED' }"
                    :title="props.row.status_name">
                    {{props.row.status_name || '--'}}
                  </span>
                </template>
              </bk-table-column>
              <bk-table-column :label="$t(`m.task['操作人']`)" :show-overflow-tooltip="true">
                <template slot-scope="props">
                  <span :title="props.row.operator_username">
                    {{props.row.operator_username || '--'}}
                  </span>
                </template>
              </bk-table-column>
              <div class="empty" slot="empty">
                <empty
                  :is-error="listError"
                  @onRefresh="getHistoryList()">
                </empty>
              </div>
            </bk-table>
          </div>
        </bk-collapse-item>
      </bk-collapse>
    </div>
    <!-- 任务记录详情 -->
    <bk-sideslider
      :is-show.sync="historyDetail.isShow"
      :title="historyDetail.title"
      :width="historyDetail.width"
      :quick-close="true">
      <div slot="content">
        <history-detail v-if="historyDetail.isShow"
          :history-id="historyDetail.id"
          :basic-infomation="basicInfomation"
          :node-id-map="nodeIdMap"
          :node-list="nodeList">
        </history-detail>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import historyDetail from './taskHistoryDetail.vue';
  import { errorHandler } from '@/utils/errorHandler';
  import Empty from '../../../../components/common/Empty.vue';

  export default {
    name: 'taskHistory',
    components: {
      historyDetail,
      Empty,
    },
    props: {
      basicInfomation: {
        type: Object,
        default() {
          return {};
        },
      },
      nodeList: {
        type: Array,
        default() {
          return [];
        },
      },
      isShowSla: Boolean,
    },
    data() {
      return {
        activeName: ['ticket'], // 默认全部打开
        loading: false,
        historyList: [],
        historyDetail: {
          isShow: false,
          title: this.$t('m.task[\'记录详情\']'),
          loading: false,
          width: 660,
          id: '',
        },
        ticketAction: [],
        nodeActions: [],
        nodeIdMap: {},
        listError: false,
      };
    },
    computed: {
      taskHistoryRefresh() {
        return this.$store.state.taskHistoryRefresh;
      },
    },
    watch: {
      taskHistoryRefresh() {
        this.getHistoryList();
      },
    },
    mounted() {
      this.getHistoryList();
    },
    methods: {
      // 设置触发器table-header title
      headerCellAttributes() {
        return {
          title: arguments[0].column.label,
        };
      },
      getHistoryList() {
        // 获取单据手动触发器
        this.loading = true;
        this.listError = false;
        const { id } = this.basicInfomation;
        this.$store.dispatch('trigger/getTicketTriggerRecord', { id }).then((res) => {
          // this.historyList = res.data.filter(item => item.status === 'FAILED' || item.status === 'SUCCEED');
          // 单据触发器
          this.ticketAction = res.data.ticket_actions.filter(item => item.status === 'FAILED' || item.status === 'SUCCEED');
          // 节点触发器
          this.nodeIdMap = res.data.state_map;
          this.nodeActions = Object.keys(res.data.state).map(state => {
            this.activeName.push(this.nodeIdMap[state]);
            return {
              name: this.nodeIdMap[state],
              actions: res.data.state[state],
            };
          });
        })
          .catch((res) => {
            this.listError = true;
            errorHandler(res, this);
          })
          .finally(() => {
            this.loading = false;
          });
      },
      openDetail(task) {
        this.historyDetail.isShow = true;
        this.historyDetail.id = task.id;
      },
      orderingClick(value) {
        this.historyList.sort(this.sortCompare('status', value.order));
      },
      sortCompare(prop, type) {
        return (obj1, obj2) => {
          let val1 = obj1[prop];
          let val2 = obj2[prop];
          if (!isNaN(Number(val1)) && !isNaN(Number(val2))) {
            val1 = Number(val1);
            val2 = Number(val2);
          }
          if (val1 < val2) {
            return (type === 'ascending' ? -1 : 1);
          } if (val1 > val2) {
            return (type === 'ascending' ? 1 : -1);
          }
          return 0;
        };
      },
    },
  };
</script>

<style scoped lang='scss'>
    .bk-task-history{
        .history-table{
          padding-bottom: 20px;
        }
    }
    .bk-status-success{
        color: #2DCB56;
    }
    .bk-status-failed{
        color: #FF5656;
    }
</style>
