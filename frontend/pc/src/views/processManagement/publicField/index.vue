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
  <div class="bk-itsm-service">
    <div class="is-title" :class="{ 'bk-title-left': !sliderStatus }">
      <p class="bk-come-back">
        {{ title }}
      </p>
    </div>
    <div class="itsm-page-content">
      <empty-tip
        v-if="projectId && !isDataLoading && pagination.count === 0 && searchToggle"
        :title="emptyTip.title"
        :sub-title="emptyTip.subTitle"
        :desc="emptyTip.desc"
        :links="emptyTip.links">
        <template slot="btns">
          <bk-button :theme="'primary'"
            data-test-id="field_button_createField"
            v-cursor="{ active: !hasPermission(createFieldPerm, curPermission) }"
            :class="{
              'btn-permission-disable': !hasPermission(createFieldPerm, curPermission)
            }"
            @click="addField">
            {{ $t('m["立即创建"]') }}
          </bk-button>
        </template>
      </empty-tip>
      <template v-else>
        <div class="bk-only-btn">
          <div class="bk-more-search">
            <bk-button :theme="'primary'"
              data-test-id="field_button_addField"
              v-cursor="{ active: !hasPermission(createFieldPerm, curPermission) }"
              :title="$t(`m.deployPage['新增']`)"
              icon="plus"
              :class="['mr10', 'plus-cus', {
                'btn-permission-disable': !hasPermission(createFieldPerm, curPermission)
              }]"
              @click="addField">
              {{ $t('m.deployPage["新增"]') }}
            </bk-button>
            <div class="bk-search-name">
              <div class="bk-search-content">
                <bk-input
                  data-test-id="field_input_searchField"
                  :clearable="true"
                  :right-icon="'bk-icon icon-search'"
                  :placeholder="moreSearch[0].placeholder"
                  v-model="moreSearch[0].value"
                  @enter="searchContent"
                  @clear="clearSearch">
                </bk-input>
              </div>
              <bk-button :title="$t(`m.deployPage['更多筛选条件']`)"
                icon=" bk-itsm-icon icon-search-more"
                class="ml10 filter-btn"
                @click="searchMore">
              </bk-button>
            </div>
          </div>
          <search-info
            ref="searchInfo"
            :more-search="moreSearch">
          </search-info>
        </div>
        <bk-table
          v-bkloading="{ isLoading: isDataLoading }"
          :data="dataList"
          :size="'small'"
          :pagination="pagination"
          @sort-change="handleSortChange"
          @page-change="handlePageChange"
          @page-limit-change="handlePageLimitChange">
          <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.treeinfo['字段名称']`)" min-width="150">
            <template slot-scope="props">
              <bk-button
                v-if="!hasPermission(
                  editFieldPerm,
                  [...$store.state.project.projectAuthActions, ...props.row.auth_actions]
                )"
                data-test-id="field_button_viewfield"
                v-cursor
                text
                theme="primary"
                class="btn-permission-disable"
                @click="openField(props.row, editFieldPerm)">
                {{props.row.name}}
              </bk-button>
              <span v-else class="bk-lable-primary"
                @click="openField(props.row)"
                :title="props.row.name">
                {{props.row.name}}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.treeinfo['唯一标识']`)" min-width="150">
            <template slot-scope="props">
              <span :title="props.row.key">{{ props.row.key || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.treeinfo['字段类型']`)" min-width="150">
            <template slot-scope="props">
              <span :title="typeTransition(props.row.type)">
                {{ typeTransition(props.row.type) || '--' }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.treeinfo['字段值']`)" width="220">
            <template slot-scope="props">
              <span :title="valueTransition(props.row)">{{ valueTransition(props.row) || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.treeinfo['字段描述']`)" width="150">
            <template slot-scope="props">
              <span :title="props.row.desc">{{ props.row.desc || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.treeinfo['最近更新人']`)" width="150">
            <template slot-scope="props">
              <span :title="props.row.updated_by">{{ props.row.updated_by || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column
            sortable
            :render-header="$renderHeader"
            :show-overflow-tooltip="true"
            :sort-orders="['descending', 'ascending', null]"
            :label="$t(`m.treeinfo['最近更新时间']`)" width="150">
            <template slot-scope="props">
              <span :title="props.row.update_at">{{ props.row.update_at || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.treeinfo['操作']`)" width="150" fixed="right">
            <template slot-scope="props">
              <!-- 编辑 -->
              <bk-button
                v-if="!hasPermission(
                  editFieldPerm,
                  [...$store.state.project.projectAuthActions, ...props.row.auth_actions]
                )"
                v-cursor
                data-test-id="field_button_editfield_permission"
                text
                theme="primary"
                class="btn-permission-disable"
                @click="openField(props.row, editFieldPerm)">
                {{ $t('m.deployPage["编辑"]') }}
              </bk-button>
              <bk-button
                data-test-id="field_button_editfield"
                v-else theme="primary"
                text
                @click="openField(props.row)">
                {{ $t('m.deployPage["编辑"]') }}
              </bk-button>
              <!-- 删除 -->
              <bk-button
                v-if="!hasPermission(
                  deleteFieldPerm,
                  [...$store.state.project.projectAuthActions, ...props.row.auth_actions]
                )"
                data-test-id="field_button_deletefield_permission"
                v-cursor
                text
                theme="primary"
                class="btn-permission-disable"
                @click="deleteField(props.row)">
                {{ $t('m.deployPage["删除"]') }}
              </bk-button>
              <bk-button
                data-test-id="field_button_deletefield"
                v-else
                theme="primary"
                text
                :disabled="!!props.row.is_builtin"
                @click="deleteField(props.row)">
                {{ $t('m.deployPage["删除"]') }}
              </bk-button>
            </template>
          </bk-table-column>
          <div class="empty" slot="empty">
            <empty
              :is-error="listError"
              :is-search="!searchToggle"
              @onRefresh="getList()"
              @onClearSearch="clearSearch()">
            </empty>
          </div>
        </bk-table>
      </template>
    </div>
    <!-- 新增字段 -->
    <div class="bk-add-slider">
      <bk-sideslider
        :is-show.sync="sliderInfo.show"
        :title="sliderInfo.title"
        :quick-close="true"
        :before-close="closeSideslider"
        :width="sliderInfo.width">
        <div class="p20" slot="content" v-if="sliderInfo.show">
          <add-field
            ref="addField"
            :change-info="changeInfo"
            :table-list="listInfo"
            :is-edit-public="isEditPublic"
            :workflow="workflow"
            :add-origin="addOrigin"
            :state="stateId"
            @closeShade="closeShade">
          </add-field>
        </div>
      </bk-sideslider>
    </div>
  </div>
</template>
<script>
  import i18n from '@/i18n/index.js';
  import commonMix from '../../commonMix/common.js';
  import permission from '@/mixins/permission.js';
  import searchInfo from '../../commonComponent/searchInfo/searchInfo.vue';
  import addField from '../processDesign/nodeConfigue/addField';
  import EmptyTip from '../../project/components/emptyTip.vue';
  import { errorHandler } from '../../../utils/errorHandler.js';
  import Empty from '../../../components/common/Empty.vue';

  export default {
    name: 'publicField',
    components: {
      addField,
      searchInfo,
      EmptyTip,
      Empty,
    },
    mixins: [commonMix, permission],
    props: {
      projectId: String,
      title: {
        type: String,
        default: i18n.t('m[\'字段\']'),
      },
    },
    data() {
      return {
        ordering: '-update_at',
        secondClick: false,
        isDataLoading: false,
        // 列表数据
        dataList: [],
        pagination: {
          current: 1,
          count: 10,
          limit: 10,
        },
        // 查询
        moreSearch: [
          {
            name: this.$t('m.publicField["字段名"]'),
            placeholder: this.$t('m.publicField["请输入字段名"]'),
            typeKey: 'name__contains',
            type: 'input',
            value: '',
            list: [],
          },
          {
            name: this.$t('m.publicField["唯一标识"]'),
            typeKey: 'key',
            type: 'input',
            value: '',
            list: [],
          },
          {
            name: this.$t('m.publicField["字段类型"]'),
            type: 'select',
            multiSelect: true,
            typeKey: 'type__in',
            value: [],
            list: [],
          },
          {
            name: this.$t('m.publicField["更新人"]'),
            type: 'member',
            multiSelect: true,
            typeKey: 'updated_by__in',
            value: [],
            list: [],
          },
          {
            name: this.$t('m.publicField["更新时间"]'),
            typeKey: 'date_update',
            type: 'datetime',
            value: '',
            list: [],
          },
        ],
        searchToggle: false,
        listError: false,
        listInfo: [],
        // 新增
        workflow: 0,
        stateId: 0,
        sliderInfo: {
          title: this.$t('m.deployPage["新增字段"]'),
          show: false,
          width: 700,
        },
        changeInfo: {},
        addOrigin: {
          isOther: true,
          addOriginInfo: {
            type: 'publicField',
            addUrl: 'publicField/add_template_fields',
            updateUrl: 'publicField/update_template_fields',
          },
        },
        fieldsList: [],
        isEditPublic: true,
        emptyTip: {
          title: this.$t('m[\'当前项目下还没有 <字段> 元素\']'),
          subTitle: this.$t('m[\'「字段」是服务表单设计的必要元素之一，将一些常用的字段沉淀下来提供给不同的服务引用，对后续的统一管理维护可以起到很大的帮助！\']'),
          desc: [
            {
              src: require('../../../images/illustration/field.svg'),
              title: this.$t('m[\'设计字段的数据结构\']'),
              content: this.$t('m[\'在创建字段时，需要根据字段含义配置字段名、填写方式（如文本框、选择器）、是否必填、校验规则、用户提示等等，尽可能的贴合服务场景进行友好的用户体验设计。\']'),
            },
            {
              src: require('../../../images/illustration/use-field.svg'),
              title: this.$t('m[\'在服务表单中使用它\']'),
              content: this.$t('m[\'在设计服务的填写表单时，可以从已经沉淀的字段元素列表中挑选符合场景的字段，从而达到相同含义的字段可以跨服务间进行统一的配置，提高管理效率。\']'),
            },
          ],
          links: [
            {
              text: this.$t('m[\'了解更多关于服务的设计流程和细节\']'),
              btn: this.$t('m[\'产品文档\']'),
              href: 'https://bk.tencent.com/docs/document/6.0/145/6600',
            },
            {
              text: this.$t('m[\'如何按分类结构化的管理你的诸多服务？\']'),
              btn: this.$t('m[\'产品文档\']'),
              href: 'https://bk.tencent.com/docs/document/6.0/145/6608',
            },
          ],
        },
      };
    },
    computed: {
      emptyStatus() {
        let status;
        if (!this.searchToggle) {
          status = 'search-empty';
        } else if (this.listError) {
          status = '500';
        } else {
          status = 'empty';
        }
        return status;
      },
      createFieldPerm() {
        return this.projectId ? ['field_create'] : ['public_field_create'];
      },
      editFieldPerm() {
        return this.projectId ? ['field_edit'] : ['public_field_edit'];
      },
      deleteFieldPerm() {
        return this.projectId ? ['field_delete'] : ['public_field_delete'];
      },
      sliderStatus() {
        return this.$store.state.common.slideStatus;
      },
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
      curPermission() {
        return this.projectId ? this.$store.state.project.projectAuthActions : [];
      },
    },
    mounted() {
      this.getList();
    },
    methods: {
      getList(page) {
        // 查询时复位页码
        if (page !== undefined) {
          this.pagination.current = page;
        }
        const params = {
          page: this.pagination.current,
          page_size: this.pagination.limit,
          ordering: this.ordering,
        };
        params.project_key = this.projectId || 'public';
        // 过滤条件
        this.moreSearch.forEach((item) => {
          if (item.type === 'datetime') {
            if (item.value && item.value[0]) {
              const gteTime = this.standardTime(item.value[0]);
              const lteTime = this.standardTime(item.value[1]);
              params.update_at__gte = gteTime;
              params.update_at__lte = lteTime;
            }
          } else {
            if (item.type === 'input') {
              params[item.typeKey] = item.value;
            } else {
              if (((Array.isArray(item.value) && item.value.length) && (item.value)) && item.typeKey) {
                params[item.typeKey] = Array.isArray(item.value) ? item.value.join(',') : item.value;
              }
            }
          }
        });
        this.isDataLoading = true;
        this.listError = false;
        this.$store.dispatch('publicField/get_template_fields', params).then((res) => {
          this.dataList = res.data.items;
          this.searchToggle = res.data.items.length !== 0;
          // 分页
          this.pagination.current = res.data.page;
          this.pagination.count = res.data.count;
        })
          .catch((res) => {
            console.log(res);
            this.listError = true;
            errorHandler(res, this);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
      },
      // 分页过滤数据
      handleSortChange(data) {
        const { order } = data;
        if (order === 'descending') {
          this.ordering = '-update_at';
        } else {
          this.ordering = undefined;
        }
        this.getList();
      },
      handlePageLimitChange() {
        this.pagination.limit = arguments[0];
        this.getList();
      },
      handlePageChange(page) {
        this.pagination.current = page;
        this.getList();
      },
      // 简单查询
      searchContent() {
        this.getList(1);
      },
      searchMore() {
        // 类型
        this.moreSearch[2].list = this.globalChoise.field_type.map(item => ({
          key: item.typeName,
          name: item.name,
        }));
        this.$refs.searchInfo.searchMore();
      },
      // 清空搜索表单
      clearSearch() {
        this.moreSearch.forEach((item) => {
          item.value = item.multiSelect ? [] : '';
        });
        this.getList(1);
      },
      // 删除字段
      deleteField(item) {
        const isAuth = this.hasPermission(
          this.deleteFieldPerm,
          [
            ...this.$store.state.project.projectAuthActions,
            ...item.auth_actions,
          ]
        );
        if (!isAuth) {
          let resourceData = null;
          if (this.projectId) {
            const { projectInfo } = this.$store.state.project;
            resourceData = {
              project: [{
                id: projectInfo.key,
                name: projectInfo.name,
              }],
              field: [{
                id: item.id,
                name: item.name,
              }],
            };
          } else {
            resourceData = {
              public_field: [{
                id: item.id,
                name: item.name,
              }],
            };
          }
          this.applyForPermission(
            this.deleteFieldPerm,
            [
              ...this.$store.state.project.projectAuthActions,
              ...item.auth_actions],
            resourceData
          );
        } else {
          this.$bkInfo({
            type: 'warning',
            title: this.$t('m.treeinfo["确认删除此字段？"]'),
            subTitle: this.$t('m.treeinfo["字段一旦删除，此字段将不在可用。请谨慎操作。"]'),
            confirmFn: () => {
              const { id } = item;
              if (this.secondClick) {
                return;
              }
              this.secondClick = true;
              this.$store.dispatch('publicField/delet_template_fields', { id }).then(() => {
                this.$bkMessage({
                  message: this.$t('m.systemConfig["删除成功"]'),
                  theme: 'success',
                });
                if (this.dataList.length === 1) {
                  this.pagination.current = this.pagination.current === 1
                    ? 1 : this.pagination.current - 1;
                }
                this.getList();
              })
                .catch((res) => {
                  errorHandler(res, this);
                })
                .finally(() => {
                  this.secondClick = false;
                });
            },
          });
        }
      },
      // 新增字段
      addField() {
        if (!this.hasPermission(this.createFieldPerm, this.curPermission)) {
          let resourceData = {};
          if (this.projectId) {
            const { projectInfo } = this.$store.state.project;
            resourceData = {
              project: [{
                id: projectInfo.key,
                name: projectInfo.name,
              }],
            };
          }
          this.applyForPermission(this.createFieldPerm, this.curPermission, resourceData);
          return;
        }
        this.changeInfo = {
          workflow: '',
          id: '',
          key: '',
          name: '',
          type: 'STRING',
          desc: '',
          layout: 'COL_12',
          validate_type: 'REQUIRE',
          choice: [],
          is_builtin: false,
          source_type: 'CUSTOM',
          source_uri: '',
          regex: 'EMPTY',
          custom_regex: '',
          is_tips: false,
          tips: '',
          meta: {
            code: '',
          },
        };
        this.changeInfo.project_key = this.projectId || 'public';
        this.sliderInfo.title = this.$t('m.deployPage["新增字段"]');
        this.sliderInfo.show = true;
      },
      closeShade() {
        this.sliderInfo.show = false;
      },
      // 编辑字段
      openField(item, reqPerm) {
        const isAuth = this.hasPermission(
          reqPerm,
          [
            ...this.$store.state.project.projectAuthActions,
            ...item.auth_actions,
          ]
        );
        if (!isAuth) {
          let resourceData = null;
          if (this.projectId) {
            const { projectInfo } = this.$store.state.project;
            resourceData = {
              project: [{
                id: projectInfo.key,
                name: projectInfo.name,
              }],
              field: [{
                id: item.id,
                name: item.name,
              }],
            };
          } else {
            resourceData = {
              public_field: [{
                id: item.id,
                name: item.name,
              }],
            };
          }
          this.applyForPermission(
            reqPerm,
            [
              ...this.$store.state.project.projectAuthActions,
              ...item.auth_actions,
            ],
            resourceData
          );
          return;
        }
        this.changeInfo = item;
        this.changeInfo.is_tips = item.is_tips || false;
        this.sliderInfo.title = this.$t('m.treeinfo["编辑字段"]');
        this.sliderInfo.show = true;
      },
      // 关闭前验证字段表单
      closeSideslider() {
        this.$bkInfo({
          title: this.$t('m["内容未保存，离开将取消操作！"]'),
          confirmLoading: true,
          confirmFn: () => {
            this.sliderInfo.show = false;
          },
          cancelFn: () => {
            this.sliderInfo.show = true;
          },
        });
      },
    },
  };
</script>

<style lang='scss' scoped>
    .filter-btn /deep/ .icon-search-more {
        font-size: 14px;
    }
</style>
