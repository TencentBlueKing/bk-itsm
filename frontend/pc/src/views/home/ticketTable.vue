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
  <div class="ticket-table-section" v-bkloading="{ isLoading: loading }">
    <template v-if="!loading">
      <router-link class="enter-my-tickets" :to="{ name: 'myTodoTicket' }">{{ $t(`m.common['进入我的单据']`) }} >></router-link>
      <bk-tab :active.sync="activePanel" type="unborder-card">
        <bk-tab-panel
          v-for="panel in panels"
          :key="panel.name"
          v-bind="panel">
          <template slot="label">
            <span class="panel-name">{{ panel.label }}</span>
            <span class="panel-count">{{ count[panel.name] }}</span>
          </template>
          <bk-table :data="ticketList" v-bkloading="{ isLoading: tabLoading }" @sort-change="onSortChange">
            <bk-table-column :label="$t(`m.manageCommon['单号']`)">
              <template slot-scope="props">
                <router-link
                  class="table-link"
                  target="_blank"
                  :to="{ name: 'TicketDetail', query: { id: props.row.id, project_id: props.row.project_key, from: 'Home' } }">
                  {{ props.row.sn }}
                </router-link>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.manageCommon['标题']`)" :width="200" prop="title"></bk-table-column>
            <bk-table-column :label="$t(`m.manageCommon['服务']`)" :width="140" :sortable="true" prop="service_name"></bk-table-column>
            <bk-table-column :label="$t(`m.newCommon['当前步骤']`)" :width="100">
              <template slot-scope="props">
                <div v-if="props.row.current_steps.length > 0" class="current-steps-wrap">
                  <bk-popover placement="top" :theme="'light'">
                    <span
                      class="bk-current-step">
                      {{props.row.current_steps[0].name}}
                    </span>
                    <div slot="content" style="max-width: 200px;">
                      <span class="bk-current-step auto-width"
                        style=""
                        v-for="(othernode, otherNodeIndex) in props.row.current_steps"
                        :key="otherNodeIndex">
                        {{othernode.name}}
                      </span>
                    </div>
                  </bk-popover>
                </div>
                <span v-else>--</span>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.manageCommon['当前处理人']`)" :width="140" prop="current_processors">
              <template slot-scope="props">
                <span :title="props.row.current_processors">{{ props.row.current_processors || '--' }}</span>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.manageCommon['提单人']`)" :width="140" :sortable="true" prop="creator"></bk-table-column>
            <bk-table-column :label="$t(`m.manageCommon['提单时间']`)" :width="180" :sortable="true" prop="create_at"></bk-table-column>
            <bk-table-column :label="$t(`m.manageCommon['操作']`)" :width="100" fixed="right">
              <template slot-scope="props">
                <template v-if="activePanel === 'approval'">
                  <bk-link theme="primary" @click="onOpenApprovalDialog(props.row.id, true)">{{ $t(`m.managePage['通过']`) }}</bk-link>
                  <bk-link theme="primary" @click="onOpenApprovalDialog(props.row.id, false)">{{ $t(`m.manageCommon['拒绝']`) }}</bk-link>
                </template>
                <router-link
                  v-else
                  target="_blank"
                  class="table-link"
                  :to="{ name: 'TicketDetail', query: { id: props.row.id, project_id: props.row.id, from: 'Home' } }">
                  {{ props.row.can_operate ? $t(`m.manageCommon['处理']`) : $t('m.manageCommon["查看"]') }}
                </router-link>
              </template>
            </bk-table-column>
          </bk-table>
          <router-link v-if="count[panel.name] > 10" class="view-all" :to="{ name: panel.id }">{{ $t(`m.common['查看全部']`) }}</router-link>
        </bk-tab-panel>
      </bk-tab>
    </template>
    <div v-else style="height: 400px;"></div>
    <!-- 审批弹窗 -->
    <approval-dialog :is-show.sync="isApprovalDialogShow"
      :approval-info="approvalInfo"
      @cancel="onApprovalDialogHidden">
    </approval-dialog>
  </div>
</template>
<script>
  import i18n from '@/i18n/index.js';
  import ApprovalDialog from '@/components/ticket/ApprovalDialog.vue';
  import ticketListMixins from '@/mixins/ticketList.js';
  import { errorHandler } from '../../utils/errorHandler';

  const PANELS = [
    {
      name: 'todo',
      id: 'myTodoTicket',
      label: i18n.t('m.managePage[\'我的待办\']'),
    },
    {
      name: 'approval',
      id: 'myApprovalTicket',
      label: i18n.t('m.home[\'待我审批\']'),
    },
    {
      name: 'created',
      id: 'myCreatedTicket',
      label: i18n.t('m.home[\'我的申请\']'),
    },
    {
      name: 'attention',
      id: 'myAttentionTicket',
      label: i18n.t('m.home[\'我的关注\']'),
    },
  ];

  export default {
    name: 'TicketTable',
    components: {
      ApprovalDialog,
    },
    mixins: [ticketListMixins],
    data() {
      return {
        panels: PANELS,
        activePanel: PANELS[0].name,
        todoList: [],
        createdList: [],
        attentionList: [],
        approvalList: [],
        count: {},
        loading: false,
        todoListLoading: false,
        createdListLoading: false,
        attentionListLoading: false,
        approvalListLoading: false,
        isApprovalDialogShow: false,
        approvalInfo: {
          showAllOption: false,
          result: true,
          approvalList: [],
        },
      };
    },
    computed: {
      ticketList() {
        return this[`${this.activePanel}List`];
      },
      tabLoading() {
        return this[`${this.activePanel}ListLoading`];
      },
    },
    created() {
      this.getData();
    },
    methods: {
      getData() {
        this.loading = true;
        Promise.all([
          this.getToDoList(),
          this.getCreatedList(),
          this.getAttentionList(),
          this.getApprovalList(),
        ]).then(() => {
          this.loading = false;
        });
      },
      // 待我处理的
      getToDoList(ordering = '-create_at') {
        this.todoListLoading = true;
        return this.$store.dispatch('change/getList', {
          page_size: 10,
          page: 1,
          is_draft: 0,
          view_type: 'my_todo',
          ordering,
        }).then((resp) => {
          if (resp.result) {
            this.todoList = resp.data.items;
            this.$set(this.count, 'todo', resp.data.count);
            // 异步加载列表中的某些字段信息
            this.__asyncReplaceTicketListAttr(this.todoList);
          }
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.todoListLoading = false;
          });
      },
      // 我创建的
      getCreatedList(ordering = '-create_at') {
        this.createdListLoading = true;
        return this.$store.dispatch('change/getList', {
          page_size: 10,
          page: 1,
          is_draft: 0,
          view_type: 'my_created',
          ordering,
        }).then((resp) => {
          if (resp.result) {
            this.createdList = resp.data.items;
            this.$set(this.count, 'created', resp.data.count);
            // 异步加载列表中的某些字段信息
            this.__asyncReplaceTicketListAttr(this.createdList);
          }
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.createdListLoading = false;
          });
      },
      // 我关注的
      getAttentionList(ordering = '-create_at') {
        this.attentionListLoading = true;
        return this.$store.dispatch('change/getList', {
          page_size: 10,
          page: 1,
          is_draft: 0,
          view_type: 'my_attention',
          ordering,
        }).then((resp) => {
          if (resp.result) {
            this.attentionList = resp.data.items;
            this.$set(this.count, 'attention', resp.data.count);
            // 异步加载列表中的某些字段信息
            this.__asyncReplaceTicketListAttr(this.attentionList);
          }
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.attentionListLoading = false;
          });
      },
      // 我审批的
      getApprovalList(ordering = '-create_at') {
        this.approvalListLoading = true;
        return this.$store.dispatch('change/getList', {
          page_size: 10,
          page: 1,
          is_draft: 0,
          view_type: 'my_approval',
          ordering,
        }).then((resp) => {
          if (resp.result) {
            this.approvalList = resp.data.items;
            this.$set(this.count, 'approval', resp.data.count);
            // 异步加载列表中的某些字段信息
            this.__asyncReplaceTicketListAttr(this.approvalList);
          }
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.approvalListLoading = false;
          });
      },
      onSortChange(data) {
        const ordering = data.order ? (data.order === 'ascending' ? `-${data.prop}` : data.prop) : undefined;
        switch (this.activePanel) {
          case 'todo':
            this.getToDoList(ordering);
            break;
          case 'created':
            this.getCreatedList(ordering);
            break;
          case 'attention':
            this.getAttentionList(ordering);
            break;
          case 'approval':
            this.getApprovalList(ordering);
            break;
        }
      },
      onOpenApprovalDialog(id, result) {
        this.isApprovalDialogShow = true;
        this.approvalInfo.result = result;
        this.approvalInfo.approvalList = [{ ticket_id: id }];
      },
      async onApprovalDialogHidden(result) {
        this.isApprovalDialogShow = false;
        this.approvalInfo = {
          result: true,
          showAllOption: false,
          approvalList: [],
        };
        if (result) {
          this.loading = true;
          await this.getApprovalList();
          this.loading = false;
        }
      },
    },
  };
</script>
<style lang="scss" scoped>
    .ticket-table-section {
        position: relative;
        margin-top: 16px;
        padding: 0 20px 20px;
        background: #ffffff;
        box-shadow: 0px 2px 4px 0px rgba(0,0,0,0.1);
    }
    .enter-my-tickets {
        position: absolute;
        top: 18px;
        right: 20px;
        font-size: 12px;
        color: #3a84ff;
        z-index: 1;
        &:hover {
            text-decoration: underline;
        }
    }
    .table-link {
        color: #3a84ff;
    }
    /deep/ .bk-link .bk-link-text {
        font-size: 12px;
    }
    /deep/ .bk-tab-label-item {
        .panel-name,
        .panel-count {
            display: inline-block;
            margin: 0 3px;
        }
        .panel-count {
            min-width: 24px;
            height: 16px;
            padding: 0 4px ;
            line-height: 16px;
            border-radius: 8px;
            text-align: center;
            font-style: normal;
            font-size: 12px;
            font-weight: bold;
            font-family: Helvetica, Arial;
            color: #979ba5;
            background-color: #f0f1f5;
        }
        &.active {
            .panel-count {
                background: #e1ecff;
                color: #3a84ff;
            }
        }
    }
    /deep/ .bk-tab-section {
        padding: 20px 0 24px 0;
    }
    .view-all {
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 12px;
        color: #3a84ff;
        &:hover {
            text-decoration: underline;
        }
    }
</style>
