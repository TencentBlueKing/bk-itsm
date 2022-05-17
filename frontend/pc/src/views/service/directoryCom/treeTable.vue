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
  <div class="bk-tree-table-directory">
    <div class="bk-table-search">
      <div class="bk-search-word">
        <span>{{nameInfo}}</span>
      </div>
      <div class="bk-form-content" v-if="treeInfo.node.level">
        <bk-button :theme="'primary'"
          data-test-id="serviceCatalogue_button_create"
          :title="$t(`m.managePage['新增']`)"
          icon="plus"
          class="mr10 plus-cus"
          @click="openShade">
          {{$t(`m.managePage['新增']`)}}
        </bk-button>
        <bk-button :theme="'default'"
          data-test-id="serviceCatalogue_button_batchDelete"
          :title="$t(`m.serviceConfig['批量移除']`)"
          class="mr10"
          :disabled="!checkList.length"
          @click="deleteCheck">
          {{$t(`m.serviceConfig['批量移除']`)}}
        </bk-button>
        <div class="bk-search-input">
          <bk-input
            data-test-id="serviceCatalogue_input_searchKey"
            :placeholder="$t(`m.serviceConfig['请输入关键字']`)"
            :clearable="true"
            :right-icon="'bk-icon icon-search'"
            v-model="searchInfo.key"
            @enter="serchEntry"
            @clear="clearInfo">
          </bk-input>
        </div>
      </div>
    </div>
    <!-- 表格拖拽 -->
    <!-- <draggable tag="tbody" v-model="listInfo" @end="updateInfo" handle=".move-handler-content"></draggable> -->
    <div class="mt15 bk-draggable" v-bkloading="{ isLoading: isTableLoading }">
      <table data-test-id="serviceCatalogue_table_drag" class="bk-draggable-table">
        <thead>
          <tr>
            <th v-if="listInfo.length">
              <bk-checkbox
                data-test-id="directiory-checkbox-check"
                :true-value="trueStatus"
                :false-value="falseStatus"
                v-model="allCheck"
                @change="handleSelectAll">
              </bk-checkbox>
            </th>
            <th>No.</th>
            <th style="min-width: 130px; max-width: 300px">{{ $t('m.serviceConfig["服务名称"]') }}</th>
            <th style="min-width: 100px; max-width: 300px">{{ $t('m.serviceConfig["服务类型"]') }}</th>
            <th style="min-width: 100px;">{{ $t('m.deployPage["状态"]') }}</th>
            <th style="max-width: 250px">{{ $t('m.serviceConfig["服务说明"]') }}</th>
            <th style="min-width: 100px;">{{ $t('m.serviceConfig["操作"]') }}</th>
          </tr>
        </thead>
        <draggable tag="tbody" v-model="listInfo" @end="updateInfo" handle=".move-handler-content">
          <template v-if="listInfo.length">
            <tr v-for="(item, index) in listInfo" :key="index"
              :class="{ 'move-handler-content': !searchInfo.key }">
              <td>
                <!-- <i class="bk-icon icon-move-new move-handler" v-if="!searchInfo.key"></i> -->
                <bk-checkbox
                  data-test-id="service_checkbox_check"
                  :true-value="trueStatus"
                  :false-value="falseStatus"
                  v-model="item.checkValue"
                  @change="handleSelect(item, index)">
                </bk-checkbox>
              </td>
              <td><span>{{index + 1}}</span></td>
              <td style="min-width: 130px; max-width: 300px" :title="item.name">
                <span>{{item.name || '--'}}</span>
              </td>
              <td style="min-width: 100px; max-width: 300px">
                <span v-for="node in serviceTypesMap"
                  v-if="item.key === node.key"
                  :key="node.key"
                  :title="node.name">
                  {{node.name || '--'}}
                </span>
              </td>
              <td>
                <span class="bk-status-color" :class="{ 'bk-status-gray': !item.is_valid }"></span>
                <span style="margin-left: 5px;"
                  :title="item.is_valid ? $t(`m.deployPage['启用']`) : $t(`m.deployPage['关闭']`)">
                  {{item.is_valid ? $t(`m.deployPage["启用"]`) : $t(`m.deployPage["关闭"]`)}}
                </span>
              </td>
              <td style="min-width: 120px;" :title="item.desc">
                <div class="bk-overflow-line">
                  <span :title="item.desc">{{item.desc || '--'}}</span>
                </div>
              </td>
              <td style="min-width: 100px;">
                <bk-button data-test-id="serviceCatalogue_button_deleteService" theme="primary" text @click="deleteOne(item)">
                  {{ $t('m.serviceConfig["移除"]') }}
                </bk-button>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-cloak>
              <td colspan="10" class="bk-none-content">
                <i class="bk-table-empty-icon bk-icon icon-empty"></i>
                <p class="bk-none-info">{{ $t('m.treeinfo["暂无数据"]') }}</p>
              </td>
            </tr>
          </template>
        </draggable>
      </table>
    </div>
    <!-- <bk-table
            v-bkloading="{ isLoading: isTableLoading }"
            :data="listInfo"
            :size="'small'"
            @select-all="handleSelectAll"
            @select="handleSelect">
            <bk-table-column type="selection" width="60" align="center"></bk-table-column>
            <bk-table-column type="index" label="No." align="center" width="60"></bk-table-column>
            <bk-table-column :label="$t(`m.serviceConfig['服务名称']`)" prop="name" min-width="180"></bk-table-column>
            <bk-table-column :label="$t(`m.serviceConfig['服务类型']`)">
                <template slot-scope="props">
                    <span v-for="node in serviceTypesMap"
                        v-if="props.row.key === node.key"
                        :key="node.key">
                        {{node.name || '--'}}
                    </span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.serviceConfig['状态']`)">
                <template slot-scope="props">
                    <span class="bk-status-color"
                        :class="{ 'bk-status-gray': !props.row.is_valid }"></span>
                    <span style="margin-left: 5px;">
                        {{(props.row.is_valid ? $t(`m.serviceConfig["启用"]`) : $t(`m.serviceConfig["关闭"]`))}}
                    </span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.serviceConfig['服务说明']`)" width="150">
                <template slot-scope="props">
                    {{ props.row.desc || '--' }}
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.serviceConfig['操作']`)" width="150">
                <template slot-scope="props">
                    <bk-button theme="primary" text @click="deleteOne(props.row)">
                        {{ $t('m.serviceConfig["移除"]') }}
                    </bk-button>
                </template>
            </bk-table-column>
        </bk-table> -->
    <!-- 新增服务 -->
    <bk-sideslider
      :is-show.sync="entryInfo.show"
      :title="entryInfo.title"
      :width="entryInfo.width"
      :quick-close="true">
      <div slot="content" style="padding: 20px" v-if="entryInfo.show">
        <bk-table
          v-bkloading="{ isLoading: isDataLoading }"
          :data="entryInfo.listInfo"
          :size="'small'"
          :pagination="entryInfo.pagination"
          @page-change="addPageChange"
          @page-limit-change="addPageLimitChange"
          @select-all="addSelectAll"
          @select="addSelect">
          <bk-table-column type="selection" width="60" align="center"></bk-table-column>
          <bk-table-column type="index" label="NO." align="center" width="60"></bk-table-column>
          <bk-table-column :label="$t(`m.serviceConfig['服务名称']`)" prop="name" min-width="180"></bk-table-column>
          <bk-table-column :label="$t(`m.serviceConfig['服务类型']`)">
            <template slot-scope="props">
              <span v-for="node in serviceTypesMap"
                v-if="props.row.key === node.key"
                :key="node.key">
                {{node.name || '--'}}
              </span>
            </template>
          </bk-table-column>
        </bk-table>
        <div class="mt20">
          <bk-button
            data-test-id="serviceCatalogue_button_serviceCreate"
            theme="primary"
            :title="$t(`m.serviceConfig['新增']`)"
            v-if="!entryInfo.listInfo.length"
            @click="addEntry">
            {{ $t('m.serviceConfig["新增"]') }}
          </bk-button>
          <bk-button
            data-test-id="serviceCatalogue_button_serviceConfirm"
            theme="primary"
            :title="$t(`m.serviceConfig['确认']`)"
            :disabled="!entryInfo.checkList.length"
            :loading="secondClick"
            v-else
            @click="submitEntry">
            {{ $t('m.serviceConfig["确认"]') }}
          </bk-button>
          <bk-button
            data-test-id="serviceCatalogue_button_serviceCancel"
            theme="default"
            :title="$t(`m.serviceConfig['取消']`)"
            :loading="secondClick"
            @click="closeShade">
            {{ $t('m.serviceConfig["取消"]') }}
          </bk-button>
        </div>
      </div>
    </bk-sideslider>
  </div>
</template>
<script>
  import draggable from 'vuedraggable';
  import { errorHandler } from '../../../utils/errorHandler';
  export default {
    components: {
      draggable,
    },
    props: {
      treeInfo: {
        type: Object,
        default() {
          return { node: {} };
        },
      },
    },
    data() {
      return {
        isDataLoading: false,
        isTableLoading: false,
        trueStatus: true,
        falseStatus: false,
        allCheck: false,
        // 二次点击
        secondClick: false,
        // 模糊查询
        searchInfo: {
          key: '',
        },
        serviceTypesMap: {},
        // 选择
        checkList: [],
        listInfo: [],
        // 新增服务
        entryInfo: {
          show: false,
          title: this.$t('m.serviceConfig["添加服务"]'),
          width: 700,
          listInfo: [],
          pagination: {
            current: 1,
            count: 10,
            limit: 10,
          },
          checkList: [],
        },
        nameInfo: '',
      };
    },
    watch: {
      'treeInfo.node'() {
        this.getTableList();
      },
    },
    mounted() {
      this.getServiceTypes();
      this.getTableList();
    },
    methods: {
      // 服务类型
      getServiceTypes() {
        this.$store.dispatch('getCustom').then((res) => {
          this.serviceTypesMap = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 获取表格数据
      getTableList() {
        const nameList = [];
        if (this.treeInfo.node.route && this.treeInfo.node.route.length) {
          this.treeInfo.node.route.forEach((node) => {
            nameList.push(node.name);
          });
        }
        nameList.push(this.treeInfo.node.name);
        this.nameInfo = nameList.join(' / ');
        // 状态复位
        this.isTableLoading = true;
        this.checkList = [];
        const params = {
          catalog_id: this.treeInfo.node.id,
          name: this.searchInfo.key,
          project_key: this.$store.state.project.id,
        };
        if (!this.treeInfo.node.id) {
          return;
        }
        this.$store.dispatch('catalogService/getServices', params).then((res) => {
          this.listInfo = res.data;
          this.listInfo.forEach((item) => {
            this.$set(item, 'checkValue', false);
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isTableLoading = false;
          });
      },
      // 全选 半选
      handleSelectAll(value) {
        this.checkList = value ? this.listInfo : [];
        this.listInfo.forEach((item) => {
          item.checkValue = value;
        });
      },
      handleSelect(item) {
        if (item.checkValue) {
          this.checkList.push(item);
        } else {
          this.checkList = this.checkList.filter(node => node.id !== item.id);
        }
        this.allCheck = this.checkList.length === this.listInfo.length;
      },
      // 拖动结束后的数据
      updateInfo(evt) {
        const currentNode = this.listInfo[evt.newIndex];
        const newOrderList = this.listInfo.map(node => node.id);
        if (this.secondClick || !currentNode.bounded_relations[0]) {
          return;
        }
        this.secondClick = true;
        const params = {
          new_order: newOrderList,
        };
        const id = currentNode.bounded_relations[0].bond_id;
        this.$store.dispatch('serviceCatalog/moveTableNode', { params, id }).then(() => {
          // ...
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.secondClick = false;
          });
      },
      // 模糊查询
      serchEntry() {
        this.getTableList();
      },
      clearInfo() {
        this.searchInfo.key = '';
        this.getTableList();
      },
      // 删除
      deleteOne(item) {
        const params = {
          catalog_id: this.treeInfo.node.id,
          services: [item.id],
        };
        this.deleteSubmit(params);
      },
      deleteCheck() {
        const idList = this.checkList.map(item => item.id);
        const params = {
          catalog_id: this.treeInfo.node.id,
          services: idList,
        };
        this.deleteSubmit(params);
      },
      deleteSubmit(params) {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.serviceConfig["确认移除服务？"]'),
          subTitle: this.$t('m.serviceConfig["移除后，将无法在该目录下找到该服务，请谨慎操作"]'),
          confirmFn: () => {
            if (this.secondClick) {
              return;
            }
            this.secondClick = true;
            this.$store.dispatch('catalogService/removeServices', params).then(() => {
              this.$bkMessage({
                message: this.$t('m.serviceConfig["删除成功"]'),
                theme: 'success',
              });
              this.getTableList();
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
      // 新增服务
      openShade() {
        this.getEntryList();
        this.closeShade();
      },
      closeShade() {
        this.entryInfo.show = !this.entryInfo.show;
        this.entryInfo.allCheck = false;
      },
      submitEntry() {
        // 添加服务
        const params = {
          catalog_id: this.treeInfo.node.id,
          services: this.entryInfo.checkList.map(item => item.id),
          project_key: this.$store.state.project.id,
        };
        if (this.secondClick) {
          return;
        }
        this.secondClick = true;
        // 批量添加服务
        this.$store.dispatch('catalogService/addServices', params).then(() => {
          this.$bkMessage({
            message: this.$t('m.serviceConfig["添加成功"]'),
            theme: 'success',
          });
          this.getTableList();
          this.closeShade();
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.secondClick = false;
          });
      },
      // 调转到服务进行添加
      addEntry() {
        this.$router.push({
          name: 'projectServiceList',
          query: {
            project_id: this.$store.state.project.id,
          },
        });
      },
      // 获取服务数据
      getEntryList(page) {
        if (page !== undefined) {
          this.entryInfo.pagination.current = page;
        }
        this.entryInfo.checkList = [];
        const params = {
          page: this.entryInfo.pagination.current,
          page_size: this.entryInfo.pagination.limit,
          no_classified: true,
          is_valid: true,
          project_key: this.$store.state.project.id,
        };
        this.isDataLoading = true;
        this.$store.dispatch('serviceEntry/getList', params).then((res) => {
          this.entryInfo.listInfo = res.data.items;
          // 分页
          this.entryInfo.pagination.current = res.data.page;
          this.entryInfo.pagination.count = res.data.count;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
      },
      // 分页过滤数据
      addPageLimitChange() {
        this.entryInfo.pagination.limit = arguments[0];
        this.getEntryList();
      },
      addPageChange(page) {
        this.entryInfo.pagination.current = page;
        this.getEntryList();
      },
      // 全选 半选
      addSelectAll(selection) {
        this.entryInfo.checkList = selection;
      },
      addSelect(selection) {
        this.entryInfo.checkList = selection;
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../scss/mixins/clearfix.scss';
    @import '../../../scss/mixins/scroller.scss';
    @import '../../../scss/mixins/table.scss';

    .bk-tree-table-directory {
        padding: 20px 10px 10px 10px;
        .bk-table-search {
            padding-bottom: 10px;
            @include clearfix;
            .bk-search-word {
                float: left;
                font-size: 14px;
                color: #737987;
                line-height: 36px;
                width: calc(100% - 450px);
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            .bk-form-content {
                float: right;
                position: relative;
                margin-left: 0px;
            }
            .bk-search-input {
                float: right;
                width: 250px;
            }
        }
    }
    .move-handler-content {
        cursor: move;
        .move-handler {
            margin-right: 5px;
            position: relative;
            top: 1px;
            opacity: 0;
        }
    }
    .bk-draggable {
        @include table;
    }
</style>
