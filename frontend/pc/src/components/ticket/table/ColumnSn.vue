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
  <!-- 单号 -->
  <div class="sn-content">
    <router-link
      class="table-link"
      target="_blank"
      :to="{ name: 'TicketDetail', query: { id: row.id, from: fromRouter, project_id: row.project_key } }">
      {{ row.sn }}
    </router-link>
    <!-- 母子单 -->
    <bk-popover
      v-if="row.related_type && openFunction.CHILD_TICKET_SWITCH"
      placement="top"
      :theme="'light'"
      :on-show="getInheritTicket">
      <i class="bk-itsm-icon icon-it-new-inherit"></i>
      <div slot="content">
        <template v-if="!inheritLoading">
          <!-- 母单 -->
          <template v-if="parent && parent.id">
            <p class="inherit-title">{{ $t('m.newCommon["母子单"]') }}(1)</p>
            <p :class="[{ 'no-auth': !parent.can_view }]">
              <router-link
                v-cursor="{ active: !parent.can_view }"
                class="table-link auto-width"
                target="_blank"
                :to="{ name: 'TicketDetail', query: { id: parent.id, from: fromRouter, project_id: parent.project_key } }">
                <span class="sn-id">{{ parent.sn }}</span>
                <span class="inherit-link">{{ parent.title }}</span>
              </router-link>
            </p>
          </template>
          <!-- 子单 -->
          <template v-if="children && children.length">
            <p class="inherit-title">{{ $t('m.newCommon["母子单"]') }}({{ children.length }})</p>
            <p v-for="(child, index) in children" :key="index" :class="[{ 'no-auth': !child.can_view }]">
              <router-link
                class="table-link auto-width"
                target="_blank"
                v-cursor="{ active: !child.can_view }"
                :to="{ name: 'TicketDetail', query: { id: child.id, from: fromRouter, project_id: child.project_key } }">
                <span class="sn-id">{{ child.sn }}</span>
                <span class="inherit-link">{{child.title}}</span>
              </router-link>
            </p>
          </template>
        </template>
        <template v-else>
          {{ $t(`m.manageCommon["加载中..."]`) }}
        </template>
      </div>
    </bk-popover>
    <!-- 关联单 -->
    <bk-popover
      v-if="row.has_relationships"
      placement="top"
      :theme="'light'"
      :on-show="getAssociatedTickets">
      <i class="bk-itsm-icon icon-it-new-associate"></i>
      <div slot="content">
        <template v-if="!associateLoading">
          <div v-if="associates">
            <p class="inherit-title">{{$t('m.newCommon["关联单"]')}}({{associates.length}})</p>
            <p v-for="(ite,index) in associates" :key="index" :class="[{ 'no-auth': !ite.can_view }]">
              <router-link
                v-cursor="{ active: !ite.can_view }"
                class="table-link auto-width"
                target="_blank"
                :to="{ name: 'TicketDetail', query: { id: ite.id, from: fromRouter, project_id: ite.project_key } }">
                <span class="sn-id">{{ ite.sn }}</span>
                <span class="inherit-link">{{ite.title}}</span>
              </router-link>
            </p>
          </div>
        </template>
        <template v-else>
          {{$t(`m.manageCommon["加载中..."]`)}}
        </template>
      </div>
    </bk-popover>
  </div>
</template>

<script>
  import { errorHandler } from '../../../utils/errorHandler';
  export default {
    name: 'ColumnSn',
    props: {
      row: {
        type: Object,
        default: () => ({}),
      },
      from: {
        type: String,
        default: '',
      },
    },
    data() {
      return {
        fromRouter: this.from || this.$route.name,
        parent: {},
        children: [],
        associates: [], // 关联单
        inheritLoading: false,
        associateLoading: false,
      };
    },
    computed: {
      openFunction() {
        return this.$store.state.openFunction;
      },
    },
    methods: {
      // 获取母子单
      getInheritTicket() {
        if (this.parent.id || this.children.length) {
          return;
        }
        this.inheritLoading = true;
        const params = {
          id: this.row.id,
        };
        this.$store.dispatch('change/getInheritState', params).then((res) => {
          if (res.data.related_type === 'slave') {
            this.parent = JSON.parse(JSON.stringify(res.data.master_slave_tickets[0]));
          } else {
            this.children = res.data.master_slave_tickets;
          }
        })
          .catch((res) => {
            errorHandler(res);
          })
          .finally(() => {
            this.inheritLoading = false;
          });
      },
      // 获取关联单
      getAssociatedTickets() {
        if (this.associates.length) {
          return;
        }
        this.associateLoading = true;
        const params = {
          id: this.row.id,
        };
        this.$store.dispatch('deployOrder/getAssociatedTickets', params).then((res) => {
          this.associates = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.associateLoading = false;
          });
      },

    },
  };
</script>
<style lang='scss' scoped>
.table-link {
    display: inline-block;
    width: 130px;
    color: #3a84ff;
    &.auto-width {
        width: auto;
    }
    .sn-id {
        display: inline-block;
        width: 140px;
    }
}
.sn-content {
    width: 200px;
    .inherit-content {
        padding: 0 10px;
        color: #63656E;
        font-size: 12px;
    }
    .inherit-title {
        height: 16px;
        line-height: 16px;
        font-weight: bold;
    }
    .inherit-link {
        display: inline-block;
        max-width: 150px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .icon-it-new-inherit {
        font-size: 16px;
        cursor: pointer;
    }
    .icon-it-new-associate {
        font-size: 16px;
        cursor: pointer;
    }
    .icon-inherit-cus {
        font-size: 16px;
        cursor: pointer;
    }
}
.no-auth {
    .table-link, .inherit-link {
        color: #C4C6CC;
        cursor: not-allowed;
        pointer-events: none;
    }
}
</style>
