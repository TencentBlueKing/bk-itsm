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
  <div class="bk-itsm-box">
    <div class="bk-itsm-service"
      v-if="!processStatus.addNew">
      <div class="is-title" :class="{ 'bk-title-left': !sliderStatus }">
        <p class="bk-come-back">
          {{ $t('m.slaContent["单据状态管理"]') }}
        </p>
      </div>
      <div class="itsm-page-content">
        <!-- 提示信息 -->
        <div class="bk-itsm-version" v-if="versionStatus">
          <i class="bk-icon icon-info-circle"></i>
          <span>{{$t('m.slaContent["单据状态：可根据需要，针对不同服务类型，定义及管理相应的单据状态、以及状态间的流转逻辑。单据状态的更新及变化，会体现在每一个具体的服务单据流转过程中。"]')}}</span>
          <i class="bk-icon icon-close" @click="closeVersion"></i>
        </div>
        <bk-table
          v-bkloading="{ isLoading: isDataLoading }"
          :data="dataList"
          :size="'small'">
          <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.slaContent['服务类型']`)" width="100">
            <template slot-scope="props">
              <span
                v-cursor="{ active: !hasPermission(['ticket_state_manage']) }"
                :class="['bk-lable-primary', {
                  'btn-permission-disable': !hasPermission(['ticket_state_manage'])
                }]"
                @click="trClick(props.row)"
                :title="props.row.service_type_name">
                {{props.row.service_type_name || '--'}}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.slaContent['单据状态']`)">
            <template slot-scope="props">
              <span :title="props.row.ticket_status">{{ props.row.ticket_status || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.slaContent['更新时间']`)" prop="update_at">
            <template slot-scope="props">
              <span :title="props.row.update_at">{{ props.row.update_at || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.slaContent['更新人']`)" width="120">
            <template slot-scope="props">
              <span :title="props.row.updated_by">{{ props.row.updated_by || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.slaContent['操作']`)" width="150" fixed="right">
            <template slot-scope="props">
              <bk-button theme="primary"
                v-if="!props.row.configured"
                v-cursor="{ active: !hasPermission(['ticket_state_manage']) }"
                icon="icon-exclamation-circle"
                text
                :class="{
                  'text-permission-disable': !hasPermission(['ticket_state_manage'])
                }"
                @click="configStatus(props.row)">
                {{ $t('m.slaContent["未配置"]') }}
              </bk-button>
              <bk-button theme="primary" text v-else
                v-cursor="{ active: !hasPermission(['ticket_state_manage']) }"
                :class="{
                  'text-permission-disable': !hasPermission(['ticket_state_manage'])
                }"
                @click="editStatus(props.row)">
                {{ $t('m.slaContent["编辑"]') }}
              </bk-button>
            </template>
          </bk-table-column>
          <div class="empty" slot="empty">
            <empty
              :is-error="listError"
              @onRefresh="getTypeStatusList()">
            </empty>
          </div>
        </bk-table>
      </div>
    </div>
    <!-- 流程状态步骤条 -->
    <template v-else>
      <div class="is-title" :class="{ 'bk-title-left': !sliderStatus }">
        <p class="bk-come-back" @click="backTab">
          <arrows-left-icon></arrows-left-icon>
          {{ tagName }}
        </p>
      </div>
      <div class="bk-itsm-tree">
        <div class="bk-tree-content">
          <div class="bk-tree-first" v-for="(item, index) in lineList" :key="item.id">
            <div class="bk-tree-shadow" @click="changeTree(index,'change',item)">
              <span
                class="bk-tree-step"
                :class="{ 'bk-tree-primary': item.type === 'primary', 'bk-tree-success': item.type === 'success', 'bk-tree-error': item.type === 'error' }">
                <i class="bk-icon icon-check-1" v-if="item.type === 'success'"></i>
                <i class="bk-icon icon-close" v-if="item.type === 'error'" style="font-size: 18px;"></i>
                <span v-if="item.type !== 'success' && item.type !== 'error'">{{item.id}}</span>
              </span>
              <span
                class="bk-tree-normal bk-tree-cursor"
                :class="{ 'bk-tree-info': (item.show || item.type !== 'normal') }">{{item.name}}</span>
            </div>
            <span class="bk-tree-line" v-if="item.id !== lineList.length"></span>
          </div>
        </div>
      </div>
      <!-- 流程操作步骤组件 -->
      <div class="bk-design-step">
        <first-step ref="first" v-if="lineList[0].show" :status-type="statusType"></first-step>
        <second-step ref="second" v-if="lineList[1].show" :status-type="statusType"></second-step>
      </div>
    </template>
  </div>
</template>

<script>
  import { errorHandler } from '../../utils/errorHandler';
  import firstStep from './ticketStatus/firstStep';
  import secondStep from './ticketStatus/secondStep';
  import permission from '@/mixins/permission.js';
  import Empty from '../../components/common/Empty.vue';

  export default {
    name: 'ticketStatus',
    components: {
      firstStep,
      secondStep,
      Empty,
    },
    mixins: [permission],
    data() {
      return {
        isDataLoading: false,
        business: false,
        // 列表数据
        dataList: [],
        // 新增流程页面切换
        processStatus: {
          addNew: false,
        },
        versionStatus: true,
        listError: false,
        // 流程树
        lineList: [
          {
            id: 1,
            name: this.$t('m.slaContent["单据状态"]'),
            type: 'primary',
            show: true,
          },
          {
            id: 2,
            name: this.$t('m.slaContent["流转设置"]'),
            type: 'normal',
            show: false,
          },
        ],
        // 编辑状态
        editInfo: {
          itemInfo: {},
          newNode: false,
        },
        // 类型状态列表
        treeTag: '',
        statusType: '',
        tagName: '',
      };
    },
    computed: {
      sliderStatus() {
        return this.$store.state.common.slideStatus;
      },
    },
    mounted() {
      this.getTypeStatusList();
    },
    methods: {
      getTypeStatusList() {
        this.isDataLoading = true;
        this.listError = false;
        this.$store.dispatch('ticketStatus/getFourTypesList').then((res) => {
          this.dataList = res.data;
          const temp = this.dataList.findIndex(item => item.id === 3);
          this.dataList.splice(temp, 1);
        })
          .catch((res) => {
            this.listError = true;
            errorHandler(res, this);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
      },
      // 编辑工单状态
      editStatus(item) {
        if (!this.hasPermission(['ticket_state_manage'], this.$store.state.project.projectAuthActions)) {
          this.applyForPermission(['ticket_state_manage'], this.$store.state.project.projectAuthActions, {});
          return;
        }
        this.tagName = item.service_type_name;
        this.statusType = item.service_type;
        this.editInfo.itemInfo = item;
        this.editInfo.newNode = item.id;
        this.processStatus.addNew = !this.processStatus.addNew;
        this.changeTree(0, 'first');
      },
      // 配置工单状态
      configStatus(item) {
        if (!this.hasPermission(['ticket_state_manage'], this.$store.state.project.projectAuthActions)) {
          this.applyForPermission(['ticket_state_manage'], this.$store.state.project.projectAuthActions, {});
          return;
        }
        this.tagName = item.service_type_name;
        this.statusType = item.service_type;
        this.editInfo.itemInfo = {};
        this.editInfo.newNode = null;
        this.processStatus.addNew = !this.processStatus.addNew;
        this.changeTree(0, 'first');
      },
      trClick(item) {
        if (item.configured) {
          this.editStatus(item);
        } else {
          this.configStatus(item);
        }
      },
      // 切换树状态
      changeTree(index, type) {
        if (this.editInfo.itemInfo.id) {
          if (type === 'first') {
            for (let i = 0; i < this.lineList.length; i++) {
              this.lineList[i].show = false;
              this.lineList[i].type = 'success';
            }
            this.lineList[0].show = true;
            this.lineList[0].type = 'primary';
          }
          if (type === 'next') {
            this.lineList[index].type = 'success';
            this.lineList[index].show = false;
            this.lineList[index + 1].type = 'primary';
            this.lineList[index + 1].show = 'true';
          }
          if (type === 'back') {
            this.lineList[index].type = 'success';
            this.lineList[index].show = false;
            this.lineList[index - 1].type = 'primary';
            this.lineList[index - 1].show = 'true';
          }
          if (type === 'change') {
            for (let i = 0; i < this.lineList.length; i++) {
              this.lineList[i].show = false;
              this.lineList[i].type = 'success';
            }
            this.lineList[index].type = 'primary';
            this.lineList[index].show = true;
          }
        } else {
          if (type === 'first') {
            for (let i = 0; i < this.lineList.length; i++) {
              this.lineList[i].show = false;
              this.lineList[i].type = 'normal';
            }
            this.lineList[0].show = true;
            this.lineList[0].type = 'primary';
          }
          if (type === 'next') {
            this.lineList[index].type = 'success';
            this.lineList[index].show = false;
            this.lineList[index + 1].type = 'primary';
            this.lineList[index + 1].show = 'true';
          }
          if (type === 'back') {
            this.lineList[index].type = 'normal';
            this.lineList[index].show = false;
            this.lineList[index - 1].type = 'primary';
            this.lineList[index - 1].show = 'true';
          }
          if (type === 'change') {
            if (this.lineList[index].type === 'normal') {
              return;
            }
            const temp = this.lineList.findIndex(item => item.show);
            this.lineList[temp].show = false;
            this.lineList[temp].type = 'normal';
            this.lineList[index].type = 'primary';
            this.lineList[index].show = true;
          }
        }
      },
      backTab() {
        this.statusType = '';
        this.editInfo.itemInfo = {};
        this.editInfo.newNode = null;
        this.processStatus.addNew = !this.processStatus.addNew;
        this.changeTree(0, 'first');
        this.getTypeStatusList();
      },
      // 关闭版本提示信息
      closeVersion() {
        this.versionStatus = false;
      },
    },
  };
</script>

<style scoped lang="scss">
    @import '../../scss/mixins/clearfix.scss';
    @import '../../scss/mixins/scroller.scss';
    .bk-design-step {
        padding: 20px;
    }

    .icon-exclamation-circle {
        color: #FF9C01;
        margin-right: 4px;
        font-size: 14px;
    }

    .bk-itsm-box {
        padding-top: 53px;
    }
    .bk-itsm-service {
        padding-top: 0;
    }
</style>
