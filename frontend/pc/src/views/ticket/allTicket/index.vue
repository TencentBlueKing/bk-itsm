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
  <div class="all-ticket-page" v-bkloading="{ isLoading: loading }">
    <template v-if="!loading">
      <div class="ticket-tab">
        <nav-title :title-name="titleName">
          <div slot="tab">
            <div class="nav-list">
              <draggable
                class="drag-scroll"
                v-model="serviceList"
                @end="onEnd"
                filter=".forbid">
                <li
                  class="drag-list"
                  v-for="(item, index) in serviceList"
                  :key="item.key"
                  :class="{
                    active: item.name === currentTab,
                    forbid: fixedTabs.includes(item.name)
                  }"
                  @click="changeTag(item.name)">
                  <span>{{ item.name }}</span>
                  <span v-if="counts[item.key]" class="ticket-file-count">{{
                    counts[item.key]
                  }}</span>
                  <template
                    v-if="!fixedTabs.includes(item.name) && isInProject">
                    <span
                      style="font-size: 18px; margin-left: 4px"
                      class="bk-itsm-icon icon-edit-new"
                      @click.stop="editProjectTab(item)"></span>
                    <i
                      class="bk-itsm-icon icon-itsm-icon-three-one"
                      @click.stop="closePanel(index, item)"></i>
                  </template>
                </li>
                <li
                  v-if="isInProject"
                  class="drag-list forbid bk-itsm-icon icon-jia-2"
                  @click.stop="addPanel"
                  title="添加自定义tab"></li>
              </draggable>
            </div>
          </div>
        </nav-title>
        <template v-for="item in serviceList">
          <div
            class="ticket-content"
            v-if="serviceType === item.key"
            :key="item.key">
            <div class="operate-wrapper">
              <advanced-search
                class="advanced-search"
                ref="advancedSearch"
                :forms="searchForms"
                :panel="item.key"
                :cur-servcie="item"
                :is-custom-tab="isCustomTab"
                :search-result-list="searchResultList"
                @search="handleSearch"
                @deteleSearchResult="deteleSearchResult"
                @onClickSearchResult="onClickSearchResult"
                @onChangeHighlight="getAllTicketList()"
                @formChange="handleSearchFormChange"
                @clear="handleClearSearch">
                <div class="slot-content">
                  <bk-button
                    data-test-id="ticket_button_export"
                    class="export"
                    :title="$t(`m.tickets['导出']`)"
                    @click="openExportList">
                    {{ $t('m.tickets["导出"]') }}
                  </bk-button>
                </div>
              </advanced-search>
            </div>
            <div class="table-wrapper">
              <table-content
                v-bkloading="{ isLoading: tableLoading }"
                :data-list="dataList"
                :pagination="pagination"
                :search-toggle="searchToggle"
                :get-list-error="listError"
                :color-hex-list="colorHexList"
                :service-type="serviceType"
                @submitSuccess="evaluationSubmitSuccess"
                @orderingClick="orderingClick"
                @handlePageLimitChange="handlePageLimitChange"
                @handlePageChange="handlePageChange"
                @clearSearch="$refs.advancedSearch[0].onClearClick()">
              </table-content>
            </div>
          </div>
        </template>
      </div>
    </template>
    <!-- 自定义tab -->
    <bk-dialog
      v-model="showCustomTabEdit"
      width="1000"
      :draggable="false"
      theme="primary"
      :mask-close="false"
      :auto-close="false"
      :title="isEditTab ? $t(`m['编辑标签']`) : $t(`m['新建标签']`)"
      @confirm="handleAddTabs('add')"
      @cancel="handleCloseTabs">
      <bk-form
        ref="customFrom"
        :label-width="150"
        class="bk-form"
        form-type="horizontal"
        :model="customTabForm"
        :rules="customRules">
        <template>
          <p class="bk-form-title">{{ $t(`m['基本信息']`) }}</p>
          <bk-form-item
            class="bk-form-item"
            :label="$t(`m['自定义tab名称']`)"
            :required="true"
            :property="'name'">
            <bk-input
              v-model="customTabForm.name"
              :maxlength="20"
              :show-word-limit="true"
              :placeholder="$t(`m['请输入名称']`)"></bk-input>
          </bk-form-item>
          <bk-form-item :label="$t(`m['描述信息']`)">
            <bk-input
              v-model="customTabForm.desc"
              :type="'textarea'"
              :placeholder="$t(`m['请输入描述信息']`)"></bk-input>
          </bk-form-item>
          <p class="bk-form-title">{{ $t(`m['筛选信息']`) }}</p>
          <template v-for="(item, index) in customForm">
            <bk-form-item
              :label="item.name"
              v-if="item.type === 'input'"
              :key="index">
              <bk-input
                v-model="customTabForm.conditions[item.key]"
                :placeholder="item.placeholder">
              </bk-input>
            </bk-form-item>
            <bk-form-item
              :label="item.name"
              v-if="item.type === 'select'"
              :key="index">
              <bk-select
                searchable
                :placeholder="item.placeholder"
                :show-select-all="item.multiSelect"
                :multiple="item.multiSelect"
                v-model="customTabForm.conditions[item.key]">
                <bk-option
                  v-for="option in item.list"
                  :key="option.key"
                  :id="option.key"
                  :name="option.name">
                </bk-option>
              </bk-select>
            </bk-form-item>
            <bk-form-item
              :label="item.name"
              v-if="item.type === 'datetime'"
              :key="index">
              <bk-date-picker
                style="width: 100%"
                v-model="customTabForm.conditions[item.key]"
                :placeholder="item.placeholder"
                :type="'datetimerange'">
              </bk-date-picker>
            </bk-form-item>
            <!-- 级联类型 -->
            <bk-form-item
              :label="item.name"
              v-if="item.type === 'cascade'"
              :key="index">
              <bk-cascade
                style="width: 100%"
                v-model="customTabForm.conditions[item.key]"
                :list="item.list"
                :check-any-level="true"
                clearable
                :ext-popover-cls="'custom-cls'">
              </bk-cascade>
            </bk-form-item>
            <!-- 人员 -->
            <bk-form-item
              :label="item.name"
              v-if="item.type === 'member'"
              :key="index">
              <member-select
                v-model="customTabForm.conditions[item.key]"
                :multiple="false"
                :placeholder="item.placeholder"></member-select>
            </bk-form-item>
          </template>
        </template>
      </bk-form>
    </bk-dialog>
    <!-- 导出 -->
    <export-ticket-dialog
      :is-show="isExportDialogShow"
      :pagination="pagination"
      :view-type="''"
      :search-params="searchParams"
      @close="isExportDialogShow = false">
    </export-ticket-dialog>
  </div>
</template>
<!-- 自定义tab 选择服务目录是只能选择下级目录 -->
<script>
  import draggable from 'vuedraggable';
  import memberSelect from '../../../views/commonComponent/memberSelect';
  import NavTitle from '@/components/common/layout/NavTitle';
  import AdvancedSearch from '@/components/form/advancedSearch/NewAdvancedSearch';
  import TableContent from './tableContent';
  import ExportTicketDialog from '@/components/ticket/ExportTicketDialog.vue';
  import { errorHandler } from '../../../utils/errorHandler';
  import ticketListMixins from '@/mixins/ticketList.js';

  export default {
    name: 'AllTicket',
    components: {
      NavTitle,
      AdvancedSearch,
      TableContent,
      ExportTicketDialog,
      memberSelect,
      draggable,
    },
    mixins: [ticketListMixins],
    props: {
      projectId: String,
      from: String,
    },
    data() {
      const SEARCH_FORM = [
        {
          name: this.$t('m.tickets[\'单号/标题\']'),
          desc: this.$t('m.tickets[\'单号/标题\']'),
          type: 'input',
          key: 'keyword',
          display: true,
          value: '',
          list: [],
          placeholder: this.$t('m.tickets["请选择单号/标题"]'),
        },
        {
          name: this.$t('m["项目"]'),
          desc: this.$t('m["项目"]'),
          type: 'select',
          key: 'project_key',
          display: true,
          value: '',
          list: [],
          placeholder: this.$t('m["请选择项目"]'),
        },
        {
          name: this.$t('m.tickets["服务目录"]'),
          type: 'cascade',
          key: 'catalog_id',
          multiSelect: true,
          display: true,
          value: [],
          list: [],
          placeholder: this.$t('m.tickets["请选择服务目录"]'),
        },
        {
          name: this.$t('m.tickets["服务"]'),
          type: 'select',
          key: 'service_id__in',
          multiSelect: true,
          display: false,
          value: [],
          list: [],
          placeholder: this.$t('m.tickets["请选择服务"]'),
        },
        {
          name: this.$t('m.tickets["提单人"]'),
          type: 'member',
          key: 'creator__in',
          multiSelect: true,
          display: true,
          value: [],
          list: [],
          placeholder: this.$t('m.tickets["请选择提单人"]'),
        },
        {
          name: this.$t('m.tickets["处理人"]'),
          type: 'member',
          key: 'current_processor',
          multiSelect: true,
          display: true,
          value: [],
          list: [],
          placeholder: this.$t('m.tickets["请选择处理人"]'),
        },
        {
          name: this.$t('m.tickets["状态"]'),
          type: 'select',
          key: 'current_status__in',
          multiSelect: true,
          display: true,
          value: [],
          list: [],
          placeholder: this.$t('m.tickets["请选择状态"]'),
        },
        {
          name: this.$t('m.tickets["提单时间"]'),
          key: 'date_update',
          type: 'datetime',
          display: true,
          value: [],
          list: [],
          placeholder: this.$t('m.tickets["请选择提单时间"]'),
        },
        {
          name: this.$t('m.tickets["业务"]'),
          key: 'bk_biz_id',
          type: 'select',
          display: true,
          value: '',
          list: [],
          placeholder: this.$t('m.tickets["请选择业务"]'),
        },
      ];
      return {
        isExportDialogShow: false,
        loading: true,
        isTabLoading: false,
        titleName: this.$t('m.managePage["所有单据"]'),
        serviceList: [], // 所有单据列表
        currentTab: '', // 当前选择tab
        counts: {},
        // 当前选择服务
        serviceType: '',
        requestList: [],
        changeList: [],
        eventList: [],
        questionList: [],
        customTabList: [],
        requestLoading: false,
        changeLoading: false,
        eventLoading: false,
        questionLoading: false,
        customTabLoading: false,
        pagination: {
          current: 1,
          count: 10,
          limit: 10,
        },
        // 状态颜色配置list
        colorHexList: [],
        // 查询
        searchForms: SEARCH_FORM.slice(0),
        searchParams: {}, // 高级搜索内容
        orderKey: '-create_at', // 排序
        searchResultList: {
          // 搜索结果
          request: [],
          change: [],
          event: [],
          question: [],
        },
        searchToggle: true, // 点击搜索记录搜索是否添加记录
        showCustomTabEdit: false,
        customList: [],
        curService: '',
        isEditTab: false,
        isCustomTab: false,
        editTabId: '',
        fixedTabs: ['请求管理', '变更管理', '事件管理', '问题管理'],
        checkTabNameList: [],
        customForm: SEARCH_FORM.slice(0),
        customRules: {
          name: [
            {
              required: true,
              message: this.$t('m["请输入自定义TAB名称"]'),
              trigger: 'blur',
            },
            {
              validator: (val) => {
                const curEdit = this.serviceList.find((item) => item.id === this.editTabId);
                const list = this.isEditTab
                  ? this.checkTabNameList.filter((item) => item !== curEdit.name)
                  : this.checkTabNameList;
                return !list.includes(val);
              },
              message: this.$t('m["该TAB名称已存在"]'),
              trigger: 'blur',
            },
          ],
        },
        customCatalog: '',
        customTabForm: {
          name: '',
          desc: '',
          conditions: {
            keyword: '',
            catalog_id: [],
            creator__in: [],
            current_processor: [],
            overall_current_status__in: [],
            create_at__gte: '',
            create_at__lte: '',
            bk_biz_id: '',
          },
        },
        listError: false,
      };
    },
    computed: {
      tableLoading() {
        return this[`${this.serviceType}Loading`] || this.customTabLoading;
      },
      dataList() {
        return this[`${this.serviceType}List`] || this.customTabList;
      },
      isInProject() {
        return !!this.$route.query.project_id;
      },
    },
    watch: {
      curService: {
        handler(newVal, oldVal) {
          const defaultType = ['event', 'change', 'request', 'question'];
          if (newVal.key !== oldVal.key && defaultType.includes(newVal.key)) {
            this.serviceType = newVal.key;
            this.getTypeStatus();
          }
        },
        deep: true,
      },
    },
    created() {
      this.initData();
    },
    methods: {
      // 拖拽后变更自定义列表order
      onEnd(e) {
        const text = e.item.textContent.trim();
        const curDrag = this.customList.find((item) => item.name === text);
        const params = {
          new_order: e.newIndex - 3,
          tab_id: curDrag.id,
        };
        this.$store
          .dispatch('project/moveProjectTab', params)
          .then(() => {})
          .catch((res) => {
            this.$bkMessage({
              message: res.data.msg,
              theme: 'error',
            });
          });
      },
      async initData() {
        this.loading = true;
        // 获取所有服务类型列表
        await this.getServiceTypeList();
        // 获取所有tab的单据列表
        this.getAllTabTicketList();
        // 获取状态颜色接口
        this.getTypeStatus();
        // 查询服务目录级联数据
        this.getServiceTree();
        // 获取全局视图状态
        this.getGlobalStatus();
        this.getBusinessList();
        if (this.$route.query.project_id) {
          this.getProjectTabList();
        }
      },
      getTreebyId(list, id) {
        for (let i = 0; i < list.length; i++) {
          const node = list[i];
          if (node.id === id) {
            return node;
          }
          if (node.children && node.children.length > 0) {
            this.getTreebyId(node.children, id);
          }
        }
      },
      handleAddTabs() {
        this.$refs.customFrom
          .validate()
          .then(() => {
            const params = {
              name: this.customTabForm.name,
              desc: this.customTabForm.desc,
              conditions: this.customTabForm.conditions,
            };
            let url = 'project/createProjectTab';
            if (this.isEditTab) {
              params.id = this.editTabId;
              url = 'project/editProjectTab';
            } else {
              params.project_key = this.$route.query.project_id;
            }
            this.$store.dispatch(url, params).then((res) => {
              if (Object.keys(res.data).length !== 0) {
                this.$set(this.counts, res.data.id, 0);
                this.getProjectTabList();
              }
            });
            this.showCustomTabEdit = false;
          })
          .finally(() => {
            if (this.isEditTab) {
              this.currentTab = this.customTabForm.name;
              this.getAllTabTicketList(this.editTabId);
              this.editTabId = '';
            }
          });
      },
      onClickSearchResult(toggle) {
        this.searchToggle = toggle;
      },
      clearTabError() {
        this.$refs.customFrom.clearError();
      },
      handleCloseTabs() {
        this.showCustomTabEdit = false;
        this.customTabForm = {
          name: '',
          desc: '',
          conditions: {
            keyword: '',
            catalog_id: [],
            creator__in: [],
            current_processor: [],
            current_status__in: [],
            bk_biz_id: '',
          },
        };
        this.clearTabError();
      },
      // 获取自定义tab列表
      getProjectTabList() {
        this.isEditTab = false;
        const params = {
          project_key: this.$route.query.project_id,
        };
        this.$store
          .dispatch('project/getProjectTab', params)
          .then((res) => {
            res.data.forEach((item) => {
              item.key = String(item.id);
              this.customList.push(item);
            });
            this.customList = res.data;
            this.serviceList.splice(4);
            this.customList.forEach((ite) => {
              this.serviceList.push(ite);
            });
            this.checkTabNameList = this.serviceList.map((item) => item.name);
          })
          .catch((e) => {
            console.log(e);
          });
      },
      editProjectTab(panel) {
        this.isEditTab = true;
        this.isCustomTab = false;
        this.getServiceTree(true);
        this.editTabId = panel.id;
        this.customTabForm.name = panel.name;
        this.customTabForm.desc = panel.desc;
        this.$set(this.customTabForm, 'conditions', panel.conditions);
        this.showCustomTabEdit = true;
      },
      // 新增自定义tab
      addPanel() {
        // this.isAddTab = true
        this.isCustomTab = false;
        this.getServiceTree(true);
        this.isEditTab = false;
        this.customTabForm = {
          name: '',
          desc: '',
          conditions: {
            keyword: '',
            catalog_id: [],
            creator__in: [],
            current_processor: [],
            current_status__in: [],
            bk_biz_id: '',
          },
        };

        this.showCustomTabEdit = true;
      },
      // 删除自定义tab
      closePanel(index, panel) {
        // 固定tab
        if (!this.fixedTabs.includes(panel.name)) {
          this.$bkInfo({
            title: `请确认是否删除-[${panel.name}]`,
            confirmFn: () => {
              this.$store
                .dispatch('project/deleteProjectTab', this.serviceList[index].id)
                .then((res) => {
                  if (res.result) {
                    this.serviceList.splice(index, 1);
                    if (this.currentTab === panel.name) {
                      this.currentTab = '请求管理';
                      this.serviceType = 'request';
                    }
                    this.getProjectTabList();
                  }
                });
            },
          });
        }
      },
      changeTime(str) {
        if (str === '') return undefined;
        const time = new Date(str);
        return `${time.getFullYear()}-${
          time.getMonth() + 1
        }-${time.getDate()} ${time.getHours()}:${time.getMinutes()}:${time.getSeconds()}`;
      },
      // 获取所有服务类型列表
      async getServiceTypeList() {
        this.isTabLoading = true;
        return this.$store
          .dispatch('getCustom')
          .then((res) => {
            if (res.result) {
              this.serviceList = res.data;
              this.serviceList.forEach((item) => {
                item.label = item.name;
                this.$set(this.counts, item.key, 0);
              });
              this.serviceType = this.serviceList[0].key;
              this.currentTab = this.serviceList[0].name;
            }
          })
          .catch((res) => {
            this.$bkMessage({
              message: res.data.msg,
              theme: 'error',
            });
          })
          .finally(() => {
            this.isTabLoading = false;
          });
      },
      // 获取所有单据列表
      getAllTicketList(type = this.serviceType) {
        const fixParams = {
          page_size: this.pagination.limit,
          page: this.pagination.current,
          ordering: this.orderKey,
        };
        const excludeList = ['request', 'change', 'event', 'question'];
        let url = 'change/getList';
        // 项目下的所有单据
        if (this.projectId) {
          fixParams.project_key = this.projectId;
        }
        let searchParams;
        if (JSON.stringify(this.searchParams) === '{}') {
          searchParams = { service_id__in: this.$route.query.service_id }; // 没有参数时默认将 url 参数作为查询参数
        } else {
          searchParams = this.searchParams;
        }
        if (!excludeList.includes(type)) {
          this.customTabLoading = true;
          url = 'project/getProjectTabList';
          fixParams.project_key = this.$route.query.project_id;
          fixParams.tab_conditions = {
            keyword: this.curService.conditions.keyword || undefined,
            catalog_id:
              Number(this.curService.conditions.catalog_id.slice(-1).join())
              || undefined,
            creator__in:
              this.curService.conditions.creator__in.join() || undefined,
            current_processor:
              this.curService.conditions.current_processor.join() || undefined,
            overall_current_status__in:
              this.curService.conditions.current_status__in.join() || undefined,
            create_at__gte: this.curService.conditions.date_update
              ? this.changeTime(this.curService.conditions.date_update[0])
              : undefined,
            create_at__lte: this.curService.conditions.date_update
              ? this.changeTime(this.curService.conditions.date_update[1])
              : undefined,
            bk_biz_id: this.curService.conditions.bk_biz_id || undefined,
          };
          fixParams.extra_conditions = {
            overall_current_status__in: searchParams.current_status__in,
          };
          Object.assign(fixParams.extra_conditions, searchParams);
          fixParams.extra_conditions.current_status__in = undefined;
        } else {
          this[`${type}Loading`] = true;
          fixParams.is_draft = 0;
          fixParams.view_type = '';
          fixParams.service_type = type;
          Object.assign(fixParams, searchParams);
        }
        this.listError = false;
        return this.$store
          .dispatch(url, fixParams)
          .then((res) => {
            if (!excludeList.includes(type)) {
              // this.$set(this.counts, service.key, res.data.count)
              this.customTabList = res.data.items;
            } else {
              this[`${type}List`] = res.data.items;
              // 异步加载列表中的某些字段信息
              this.__asyncReplaceTicketListAttr(this[`${type}List`]);
              this.$set(this.counts, type, res.data.count);
            }
            // 分页
            this.pagination.current = res.data.page;
            if (this.serviceType === type) {
              this.pagination.count = res.data.count;
            }
          })
          .catch(() => {
            this.listError = true;
          })
          .finally(() => {
            this[`${type}Loading`] = false;
            this.customTabLoading = false;
          });
      },
      // 获取所有tab的单据列表
      getAllTabTicketList() {
        this.loading = true;
        const tableList = this.serviceList.map((item) => this.getAllTicketList(item.key));
        Promise.all(tableList).then(() => {
          this.loading = false;
        });
      },
      // 查询级联数据
      getServiceTree(type) {
        const params = {
          show_deleted: true,
        };
        if (!type) {
          params.key = this.serviceType;
        }
        if (this.projectId) {
          params.project_key = this.projectId;
        }
        this.$store
          .dispatch('serviceCatalog/getTreeData', params)
          .then((res) => {
            const formItem = this.searchForms.find((item) => item.key === 'catalog_id');
            formItem.list = res.data[0] ? res.data[0].children : [];
            // const current = this.serviceList.find(item => item.key === this.serviceType)
            // if (!this.fixedTabs.includes(current.name)) {
            //     const list = []
            //     this.searchForms.forEach(item => {
            //         if (item.key === 'catalog_id') {
            //             list.push(this.getTreebyId(item.list, current.conditions.catalog_id[0]))
            //         }
            //     })
            //     formItem.list = list
            // } else {
            //     formItem.list = res.data[0] ? res.data[0]['children'] : []
            // }
          })
          .catch((res) => {
            this.$bkMessage({
              message: res.data.msg,
              theme: 'error',
            });
          });
      },
      // 获取单据状态
      getGlobalStatus() {
        const params = {
          source_uri: 'ticket_status',
        };
        this.$store
          .dispatch('ticketStatus/getOverallTicketStatuses', params)
          .then((res) => {
            const formItem = this.searchForms.find((item) => item.key === 'current_status__in');
            formItem.list = res.data;
          })
          .catch((res) => {
            this.$bkMessage({
              message: res.data.msg,
              theme: 'error',
            });
          });
      },
      // 获取服务数据
      getServiceData(val) {
        const params = {
          catalog_id: val,
          service_key: this.serviceType,
          is_valid: 1,
        };
        if (this.projectId) {
          params.project_key = this.projectId;
        }
        this.$store
          .dispatch('catalogService/getServices', params)
          .then((res) => {
            const formItem = this.searchForms.find((item) => item.key === 'service_id__in');
            formItem.list = [];
            res.data.forEach((item) => {
              formItem.list.push({
                key: item.id,
                name: item.name,
              });
            });
          })
          .catch((res) => {
            this.$bkMessage({
              message: res.data.msg,
              theme: 'error',
            });
          })
          .finally(() => {});
      },
      // 获取状态颜色接口
      getTypeStatus() {
        const params = {};
        const type = this.serviceType;
        this.$store
          .dispatch('ticketStatus/getTypeStatus', { type, params })
          .then((res) => {
            this.colorHexList = res.data;
          })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      getBusinessList() {
        this.$store
          .dispatch('eventType/getAppList')
          .then((res) => {
            this.searchForms.find((item) => item.key === 'bk_biz_id').list = res.data;
          })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 切换不同的标签卡
      changeTag(val) {
        this.currentTab = val;
        this.pagination.limit = 10;
        this.pagination.current = 1;
        this.searchParams = {};
        this.orderKey = '-create_at';
        this.searchForms.forEach((item) => {
          item.value = item.multiSelect ? [] : '';
        });
        this.curService = this.serviceList.find((item) => item.name === val);
        this.serviceType = this.curService.key;
        if (this.fixedTabs.includes(this.curService.name)) {
          this.getServiceTree();
          this.isCustomTab = false;
        } else {
          this.isCustomTab = true;
        }
        this.getAllTicketList(this.serviceType);
      },
      // 导出弹框
      openExportList() {
        this.isExportDialogShow = true;
      },
      // 处理搜索结果
      handleSearchResult(params) {
        if (Object.keys(params).length === 0 || !this.searchToggle) return;
        this.$set(this.searchResultList, this.serviceType, []);
        this.searchResultList[this.serviceType].push(params);
      },
      // 删除搜索结果
      deteleSearchResult(type, index) {
        this.searchResultList[type].splice(index, 1);
        this.searchToggle = false;
      },
      handleSearch(params, toggle) {
        // this.isAddTab = false
        this.searchToggle = toggle;
        this.pagination.limit = 10;
        this.pagination.current = 1;
        this.searchParams = params;
        this.handleSearchResult(params);
        this.getAllTicketList(this.serviceType);
      },
      // 清空搜索表单
      handleClearSearch() {
        this.searchForms.forEach((item) => {
          if (item.key === 'service_id__in') {
            item.display = false;
          }
        });
      },
      // 展开高级搜索
      handleSearchFormChange(key, val) {
        if (key === 'catalog_id') {
          const formItem = this.searchForms.find((item) => item.key === 'service_id__in');
          formItem.display = val.length;
          if (val.length) {
            const serviceCatalogId = val[val.length - 1];
            // 当服务目录的数据发生变化时，清空服务数据
            formItem.value = [];
            this.getServiceData(serviceCatalogId);
          }
        }
      },
      // 分页过滤数据
      handlePageLimitChange(limit) {
        this.pagination.current = 1;
        this.pagination.limit = limit;
        this.getAllTicketList();
      },
      handlePageChange(page) {
        this.pagination.current = page;
        this.getAllTicketList();
      },
      // 排序
      orderingClick(order) {
        this.orderKey = order;
        this.getAllTicketList(this.serviceType);
      },
      // 评价成功回调
      evaluationSubmitSuccess() {
        this.getAllTicketList();
      },
    },
  };
</script>
<style lang="scss" scoped>
@import "~@/scss/mixins/scroller.scss";
.all-ticket-page {
  height: 100%;
  background: #fafbfd;
  /deep/ .bk-tab-section {
    padding: 0;
    background-color: #f5f7fa;
  }
  .bk-tab-label-item {
    .list-wrapper {
      display: flex;
      align-items: center;
      position: relative;
      .ticket-file-count {
        display: inline-block;
        vertical-align: middle;
        margin: 0 3px;
        min-width: 24px;
        height: 16px;
        padding: 0 4px;
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
    }
    &.active,
    &:hover {
      .ticket-file-count {
        background: #e1ecff;
        color: #3a84ff;
      }
    }
  }
  /deep/ .bk-tab-label-wrapper {
    box-shadow: 0px 2px 2px 0px rgba(0, 0, 0, 0.1);
  }
  .ticket-content {
    padding: 14px 18px 15px 22px;
    height: calc(100vh - 146px);
    overflow: auto;
    @include scroller;
    .operate-wrapper {
      margin-bottom: 14px;
      .slot-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        .checkbox-wapper {
          display: flex;
          align-items: center;
        }
        .export {
          width: 86px;
        }
        .bk-form-checkbox {
          width: 78px;
          margin-right: 21px;
        }
      }
    }
  }
}
.nav-list {
  display: flex;
  height: 50px;
  overflow-x: auto;
  overflow-y: hidden;
  z-index: 999;
  @include scroller(#a5a5a5, 4px, 4px);
  .drag-scroll {
    display: flex;
    justify-content: space-evenly;
    .drag-list {
      cursor: pointer;
      display: inline-block;
      height: 50px;
      line-height: 50px;
      font-size: 14px;
      padding: 2px 20px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      color: #63656e;
      &:hover {
        color: #3a84ff;
        .ticket-file-count {
          background: #3a84ff;
          color: white;
        }
        .icon-itsm-icon-three-one {
          display: inline-block;
        }
        .icon-edit-new {
          display: inline-block;
        }
      }
      .icon-itsm-icon-three-one {
        width: 20px;
        display: none;
      }
      .icon-edit-new {
        display: none;
        width: 20px;
      }
      .ticket-file-count {
        font-size: 12px;
        background: #f0f1f5;
        border-radius: 7px;
        padding: 0 2px;
      }
    }
    .active {
      color: #3a84ff;
      border-bottom: 4px solid #3a84ff;
    }
  }
}
.bk-form {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  .bk-form-title {
    width: 100%;
    margin-left: 2px;
    font-size: 14px;
    font-weight: 600;
  }
  .bk-form-item {
    width: 50%;
    min-height: 32px;
    /deep/ .bk-form-content {
      width: auto;
      min-height: 32px;
      margin-left: 150px;
      position: relative;
      outline: none;
      line-height: 0px;
    }
  }
}
</style>
