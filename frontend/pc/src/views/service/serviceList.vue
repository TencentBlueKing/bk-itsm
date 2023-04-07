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
  <div>
    <nav-title :title-name="$t(`m.serviceConfig['服务']`)"></nav-title>
    <div class="page-content">
      <!-- btn -->
      <div :class="['service-left', isHiddenDirectory ? 'hide' : '']">
        <tree-info :tree-info="treeInfo" :dir-list="dirList"></tree-info>
        <div class="hidden-tree" @click="hiddenTree">
          <i :class="['bk-itsm-icon', isHiddenDirectory ? 'icon-arrow-right' : 'icon-xiangzuo1']"></i>
        </div>
      </div>
      <div :class="['service-right', isHiddenDirectory ? 'auto-wight' : '']">
        <div class="bk-only-btn">
          <div class="bk-more-search">
            <bk-button
              data-test-id="service_button_createService"
              v-cursor="{ active: !hasPermission(['service_create'], $store.state.project.projectAuthActions) }"
              :theme="'primary'"
              icon="plus"
              :class="['mr10', 'plus-cus', {
                'btn-permission-disable': !hasPermission(['service_create'], $store.state.project.projectAuthActions)
              }]"
              :title="$t(`m.serviceConfig['新增']`)"
              @click="onServiceCreatePermissonCheck">
              {{$t(`m.serviceConfig['新增']`)}}
            </bk-button>
            <bk-button :theme="'default'"
              class="mr10"
              data-test-id="service_button_batchImportService"
              :title="$t(`m['导入']`)"
              @click="importService">
              {{$t(`m['导入']`)}}
            </bk-button>
            <bk-button :theme="'default'"
              data-test-id="service_button_batchDeleteService"
              :title="$t(`m.serviceConfig['批量删除']`)"
              :disabled="!checkList.length"
              @click="deleteCheck">
              {{$t(`m.serviceConfig['批量删除']`)}}
            </bk-button>
            <div class="bk-search-name">
              <div class="bk-search-content">
                <bk-input
                  :placeholder="moreSearch[0].placeholder || $t(`m.serviceConfig['请输入服务名']`)"
                  :clearable="true"
                  :right-icon="'bk-icon icon-search'"
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
          ref="serviceTable"
          v-bkloading="{ isLoading: isDataLoading }"
          :data="dataList"
          :size="'small'"
          :pagination="pagination"
          @cell-mouse-enter="cellMouseEnter"
          @cell-mouse-leave="cellMouseLeave"
          @page-change="handlePageChange"
          @page-limit-change="handlePageLimitChange"
          @select-all="handleSelectAll"
          @select="handleSelect">
          <bk-table-column
            type="selection"
            width="60"
            align="center">
            <template slot-scope="props">
              <template v-if="!hasPermission(['service_manage'], [...$store.state.project.projectAuthActions, ...props.row.auth_actions])">
                <div style="height: 100%; display: flex; justify-content: center; align-items: center;">
                  <span
                    v-cursor
                    class="checkbox-permission-disable"
                    @click="onServicePermissonCheck(['service_manage'], props.row)">
                  </span>
                </div>
              </template>
              <template v-else>
                <bk-checkbox
                  data-test-id="service_checkbox_checkService"
                  :true-value="trueStatus"
                  :false-value="falseStatus"
                  v-model="props.row.checkStatus"
                  @change="changeCheck(props.row)">
                </bk-checkbox>
              </template>
            </template>
          </bk-table-column>
          <bk-table-column
            v-for="field in setting.selectedFields"
            :key="field.id"
            :label="field.label"
            :width="field.width"
            :show-overflow-tooltip="true"
            :min-width="field.minWidth"
            :render-header="$renderHeader"
            :prop="field.id">
            <div slot-scope="{ row }">
              <template v-if="field.id === 'name'">
                <span
                  v-if="!hasPermission(['service_manage'], [...$store.state.project.projectAuthActions, ...row.auth_actions])"
                  v-cursor
                  class="bk-lable-primary text-permission-disable"
                  :title="row.name"
                  @click="onServicePermissonCheck(['service_manage'], row)">
                  {{ row.name }}
                </span>
                <template v-else>
                  <div v-if="row.id !== changeFrom.name" class="bk-lable-display">
                    <span
                      class="bk-lable-primary"
                      :title="row.name"
                      @click="changeEntry(row, 'edit')">
                      {{ row.name }}
                    </span>
                    <i v-show="tableHoverId === row.id" @click.stop="handleChange('name', row)" class="bk-itsm-icon icon-itsm-icon-six"></i>
                  </div>
                  <div v-else class="hover-show-icon">
                    <bk-input v-model="editValue"></bk-input>
                    <div class="operation">
                      <i class="bk-itsm-icon icon-itsm-icon-fill-fit" @click="submitEditService('name', row)"></i>
                      <i class="bk-itsm-icon icon-itsm-icon-three-one" @click="closeEdit"></i>
                    </div>
                  </div>
                </template>
              </template>
              <template v-else-if="field.id === 'key'">
                <template v-if="row.id !== changeFrom.serviceType">
                  <template v-for="(type, typeIndex) in serviceTypesMap">
                    <span v-if="row.key === type.key"
                      :title="type.name"
                      :key="typeIndex">
                      {{ type.name }}
                      <i v-show="tableHoverId === row.id" @click="handleChange('key', row)" class="bk-itsm-icon icon-itsm-icon-six"></i>
                    </span>
                  </template>
                </template>
                <div v-else class="hover-show-icon">
                  <bk-select v-model="editValue"
                    :placeholder="$t(`m.serviceConfig['请选择服务类型']`)"
                    :clearable="false"
                    style="width: 150px"
                    searchable
                    :font-size="'medium'">
                    <bk-option v-for="option in serviceTypeList"
                      :key="option.key"
                      :id="option.key"
                      :name="option.name">
                    </bk-option>
                  </bk-select>
                  <div class="operation">
                    <i class="bk-itsm-icon icon-itsm-icon-fill-fit" @click="submitEditService('key', row)"></i>
                    <i class="bk-itsm-icon icon-itsm-icon-three-one" @click="closeEdit"></i>
                  </div>
                </div>
              </template>
              <template v-else-if="field.id === 'desc'">
                <span
                  v-if="!hasPermission(['service_manage'], [...$store.state.project.projectAuthActions, ...row.auth_actions])"
                  v-cursor
                  class="bk-lable-primary text-permission-disable"
                  :title="row.desc"
                  @click="onServicePermissonCheck(['service_manage'], row)">
                  {{ row.desc }}
                </span>
                <template v-else>
                  <div v-if="row.id !== changeFrom.desc" class="bk-lable-display">
                    <span
                      :title="row.desc">
                      {{ row.desc || '--' }}
                    </span>
                    <i v-show="tableHoverId === row.id" @click.stop="handleChange('desc', row)" class="bk-itsm-icon icon-itsm-icon-six"></i>
                  </div>
                  <div v-else class="hover-show-icon">
                    <bk-input v-model="editValue"></bk-input>
                    <div class="operation">
                      <i class="bk-itsm-icon icon-itsm-icon-fill-fit" @click="submitEditService('desc', row)"></i>
                      <i class="bk-itsm-icon icon-itsm-icon-three-one" @click="closeEdit"></i>
                    </div>
                  </div>
                </template>
              </template>
              <template v-else-if="field.id === 'bounded_catalogs'">
                <span v-if="row.id !== changeFrom.bounded_catalogs" :title="row.bounded_catalogs[0]">{{ row.bounded_catalogs[0] || '--' }}<i v-show="tableHoverId === row.id" @click="handleChange('catalog_id', row)" class="bk-itsm-icon icon-itsm-icon-six"></i></span>
                <div v-else class="hover-show-icon">
                  <bk-cascade
                    :list="dirList"
                    clearable
                    :check-any-level="true"
                    style="width: 250px;"
                    :ext-popover-cls="'custom-cls'"
                    @change="handleChangeTree">
                  </bk-cascade>
                  <div class="operation">
                    <i class="bk-itsm-icon icon-itsm-icon-fill-fit" @click="submitEditService('catalog_id', row)"></i>
                    <i class="bk-itsm-icon icon-itsm-icon-three-one" @click="closeEdit"></i>
                  </div>
                </div>
              </template>
              <template v-else-if="field.id === 'is_valid'">
                <span class="bk-status-color"
                  :class="{ 'bk-status-gray': !row.is_valid }"></span>
                <span style="margin-left: 5px;"
                  :title="row.is_valid ? $t(`m.serviceConfig['启用']`) : $t(`m.serviceConfig['关闭']`)">
                  {{(row.is_valid ? $t(`m.serviceConfig["启用"]`) : $t(`m.serviceConfig["关闭"]`))}}
                </span>
              </template>
              <template v-else-if="field.id === 'supervise_type'">
                <span :title="setDisplayType(row)">{{setDisplayType(row)}}</span>
              </template>
              <template v-else>
                <span :title="row[field.id]">{{row[field.id] || '--'}}</span>
              </template>
            </div>
          </bk-table-column>
          <bk-table-column :label="$t(`m.serviceConfig['操作']`)" width="120" fixed="right">
            <template slot-scope="props">
              <!-- sla -->
              <template v-if="openFunction.SLA_SWITCH">
                <bk-button
                  v-if="!hasPermission(['service_manage'], [...props.row.auth_actions, ...$store.state.project.projectAuthActions])"
                  v-cursor
                  text
                  theme="primary"
                  class="btn-permission-disable"
                  @click="onServicePermissonCheck(['service_manage'], props.row)">
                  SLA
                </bk-button>
                <router-link v-else data-test-id="service_link_linkToSLA" class="bk-button-text bk-primary" :to="{ name: 'projectServiceSla', params: { id: props.row.id }, query: { project_id: $store.state.project.id, catalog_id: $route.query.catalog_id } }">SLA</router-link>
              </template>
              <!-- 编辑 -->
              <bk-button
                v-if="!hasPermission(['service_manage'], [...props.row.auth_actions, ...$store.state.project.projectAuthActions])"
                v-cursor
                text
                theme="primary"
                class="btn-permission-disable"
                @click="onServicePermissonCheck(['service_manage'], props.row)">
                {{ $t('m.serviceConfig["编辑"]') }}
              </bk-button>
              <bk-button
                v-else
                data-test-id="service_button_editService"
                theme="primary"
                text
                @click="changeEntry(props.row, 'edit')">
                {{ $t('m.serviceConfig["编辑"]') }}
              </bk-button>
              <!-- 克隆 -->
              <bk-button
                v-if="!hasPermission(['service_manage'], [...props.row.auth_actions, ...$store.state.project.projectAuthActions])"
                v-cursor
                text
                theme="primary"
                class="btn-permission-disable"
                @click="onServicePermissonCheck(['service_manage'], props.row)">
                {{ $t('m.serviceConfig["克隆"]') }}
              </bk-button>
              <bk-button
                v-else
                data-test-id="service_button_editService"
                theme="primary"
                text
                @click="changeEntry(props.row, 'clone')">
                {{ $t('m.serviceConfig["克隆"]') }}
              </bk-button>
              <!-- 删除 -->
              <bk-popover placement="bottom" theme="light">
                <i class="bk-itsm-icon icon-move-new"></i>
                <div slot="content" style="white-space: normal;">
                  <bk-button
                    style="font-size: 12px;"
                    data-test-id="service_button_deleteService1"
                    v-if="!hasPermission(['service_manage'], [...props.row.auth_actions, ...$store.state.project.projectAuthActions])"
                    v-cursor
                    text
                    theme="primary"
                    class="btn-permission-disable"
                    @click="onServicePermissonCheck(['service_manage'], props.row)">
                    {{ $t('m.serviceConfig["删除"]') }}
                  </bk-button>
                  <template v-else>
                    <bk-button
                      style="font-size: 12px;"
                      data-test-id="service_button_deleteService3"
                      theme="primary"
                      text
                      @click="deleteOne(props.row)">
                      {{ $t('m.serviceConfig["删除"]') }}
                    </bk-button>
                  </template>
                  <bk-button
                    style="font-size: 12px; display: block"
                    data-test-id="service_button_deleteService3"
                    theme="primary"
                    text
                    @click="exportService(props.row)">
                    {{ $t('m["导出"]') }}
                  </bk-button>
                </div>
              </bk-popover>
            </template>
          </bk-table-column>
          <bk-table-column type="setting" :tippy-options="{ zIndex: 3000 }">
            <bk-table-setting-content
              :fields="setting.fields"
              :selected="setting.selectedFields"
              :max="setting.max"
              :size="setting.size"
              @setting-change="handleSettingChange">
            </bk-table-setting-content>
          </bk-table-column>
          <div class="empty" slot="empty">
            <empty
              :is-error="listError"
              :is-search="searchToggle"
              @onRefresh="getList()"
              @onClearSearch="clearSearch()">
            </empty>
          </div>
        </bk-table>
      </div>
      <bk-dialog
        width="800"
        v-model="isImportServiceShow"
        :title="$t(`m['导入服务']`)"
        theme="primary"
        :auto-close="false"
        :mask-close="false"
        @confirm="importConfirm"
        @cancel="closeImport">
        <bk-form ref="importForm" id="importForm">
          <bk-form-item :label="$t(`m['选择目录']`)" required>
            <bk-cascade
              v-model="importCatalogId"
              :list="dirList"
              clearable
              :check-any-level="true"
              :ext-popover-cls="'custom-cls'"
              @change="handleChangeTree">
            </bk-cascade>
          </bk-form-item>
          <bk-form-item :label="$t(`m['选择文件']`)" required>
            <bk-button class="bk-btn-file" style="width: 100px">
              <input class="bk-input-file" type="file" ref="importInput" @change="handleFile" />
              {{ $t(`m['选择文件']`) }}
              <span class="bk-input-tip">{{ $t(`m['仅支持json文件！']`) }}</span>
            </bk-button>
          </bk-form-item>
          <template v-if="importFileNameList.length !== 0">
            <div class="file-list" v-for="(item, index) in importFileNameList" :key="index">{{ item }}
              <i class="bk-itsm-icon icon-itsm-icon-three-one" @click="closeFile"></i>
            </div>
          </template>
          <p v-if="isCheckImport" class="import-error-tip">{{ errorName + $t(`m['为必选项!']`) }}</p>
        </bk-form>
      </bk-dialog>
    </div>
  </div>
</template>

<script>
  import axios from 'axios';
  import NavTitle from '@/components/common/layout/NavTitle';
  import searchInfo from '../commonComponent/searchInfo/searchInfo.vue';
  import permission from '@/mixins/permission.js';
  import commonMix from '@/views/commonMix/common.js';
  import { errorHandler } from '../../utils/errorHandler';
  import treeInfo from './directoryCom/treeInfo.vue';
  import { deepClone } from '../../utils/util';
  import i18n from '@/i18n/index.js';
  import Empty from '../../components/common/Empty.vue';
  // import selectTree from '@/components/form/selectTree/index.vue'
  const FIELDS = [
    {
      id: 'id',
      label: 'ID',
      width: 60,
    },
    {
      id: 'name',
      label: i18n.t('m["服务名称"]'),
      minWidth: 200,
    },
    {
      id: 'key',
      label: i18n.t('m["类型"]'),
      minWidth: 200,
    },
    {
      id: 'desc',
      label: i18n.t('m["描述"]'),
      minWidth: 200,
    },
    {
      id: 'creator',
      label: i18n.t('m["创建人"]'),
      minWidth: 100,
    },
    {
      id: 'updated_by',
      label: i18n.t('m["更新人"]'),
      minWidth: 100,
    },
    {
      id: 'update_at',
      label: i18n.t('m["更新时间"]'),
      minWidth: 150,
    },
    {
      id: 'supervise_type',
      label: i18n.t('m["可见范围"]'),
      minWidth: 150,
    },
    {
      id: 'bounded_catalogs',
      label: i18n.t('m["关联目录"]'),
      minWidth: 200,
    },
    {
      id: 'is_valid',
      label: i18n.t('m["状态"]'),
      minWidth: 200,
    },
  ];
  export default {
    name: 'ServiceList',
    components: {
      NavTitle,
      searchInfo,
      treeInfo,
      Empty,
      // selectTree
    },
    mixins: [permission, commonMix],
    data() {
      return {
        treeInfo: {
          node: {},
        },
        rules: {},
        tableSettings: [],
        setting: {
          fields: FIELDS,
          selectedFields: FIELDS,
          size: 'small',
        },
        importCatalogId: [],
        isCheckImport: false,
        isHasFile: false,
        importFileNameList: [],
        errorName: '',
        formData: {
          name: '',
          desc: '',
          key: '',
          catalog_id: '',
        },
        dirList: [], // 服务目录
        serviceTypeList: [], // 服务类型
        isBasicFormEditting: false,
        isSubmitting: false,
        isHiddenDirectory: false,
        trueStatus: true,
        falseStatus: false,
        isDataLoading: false,
        // 服务类型数据
        serviceTypesMap: [],
        dataList: [],
        // 选择
        checkList: [],
        pagination: {
          current: 1,
          count: 10,
          limit: 10,
        },
        // 查询
        moreSearch: [
          {
            name: this.$t('m.serviceConfig["服务名称"]'),
            type: 'input',
            typeKey: 'name',
            value: '',
            placeholder: this.$t('m.serviceConfig["请输入服务名"]'),
          },
          {
            name: this.$t('m.serviceConfig["类型"]'),
            type: 'select',
            typeKey: 'key',
            value: '',
            list: [],
          },
          {
            name: this.$t('m.serviceConfig["服务级别"]'),
            type: 'select',
            typeKey: 'sla',
            value: '',
            list: [],
          },
        ],
        addList: [],
        lineList: [],
        // 流程预览
        processInfo: {
          isShow: false,
          title: this.$t('m.serviceConfig["流程预览"]'),
          position: {
            top: 150,
          },
          draggable: true,
          loading: true,
        },
        changeFrom: {
          name: '',
          serviceType: '',
          desc: '',
          bounded_catalogs: '',
        },
        editValue: '',
        tableHoverId: '',
        isImportServiceShow: false,
        displayTypeList: [],
        userList: [],
        listError: false,
        searchToggle: false,
      };
    },
    computed: {
      openFunction() {
        return this.$store.state.openFunction;
      },
    },
    watch: {
      'treeInfo.node'() {
        this.getList(1);
      },
      importCatalogId(val) {
        if (val.length !== 0) {
          this.isCheckImport = false;
        }
      },
      isImportServiceShow(val) {
        if (!val) {
          this.importFileNameList = [];
          this.$nextTick(() => {
            this.$refs.importInput.value = '';
          });
        }
      },
    },
    created() {
      this.rules.name = this.checkCommonRules('name').name;
      this.rules.directory_id = this.checkCommonRules('required').required;
      this.rules.key = this.checkCommonRules('required').required;
    },
    mounted() {
      this.getDisplayType();
      const curTableSetting = localStorage.getItem('tableSettings') ? JSON.parse(localStorage.getItem('tableSettings')).find(item => item.type === 'service') : null;
      if (curTableSetting) {
        this.setting.size = curTableSetting.size;
        this.setting.selectedFields = this.setting.fields.slice(0).filter(m => curTableSetting.fields.find(item => item.id === m.id));
      }
      this.getServiceTypes();
      this.getList();
      this.getSlaList();
      this.getServiceDirectory();
    },
    methods: {
      getDisplayType() {
        const params = {
          project_key: this.$store.state.project.id || this.$route.query.project.id,
        };
        Promise.all([this.$store.dispatch('deployCommon/getUser', {
          is_processor: true,
          project_key: this.$store.state.project.id,
        }), this.$store.dispatch('deployCommon/getSecondUser', params)]).then(res => {
          this.displayTypeList = res[0].data;
          this.userList = res[1].data;
        });
      },
      setDisplayType(row) {
        const type = this.displayTypeList.find(item => item.type === row.display_type);
        if (type === undefined) {
          return i18n.t('m["不可见"]');
        }
        if (row.display_role === '') {
          return type.name;
        }
        const fields = row.display_role.split(',');
        const users = this.userList.filter(item => item.role_type === row.display_type);
        const result = [];
        if (users) {
          users.forEach(item => {
            if (fields.includes(item.role_key)) {
              result.push(item.name);
            }
          });
        }
        return result.length !== 0 ? `${type.name}/${result}` : type.name;
      },
      handleSettingChange({ fields, size }) {
        const curTableSetting = deepClone(this.tableSettings.find(item => item.type === 'service'));
        if (curTableSetting) {
          curTableSetting.size = size;
          curTableSetting.fields = fields;
        } else {
          this.tableSettings.push({
            type: 'service',
            size,
            fields,
          });
        }
        localStorage.setItem('tableSettings', JSON.stringify(this.tableSettings));
        this.setting.size = size;
        this.setting.selectedFields = fields;
      },
      cellMouseEnter(row) {
        this.tableHoverId = row.id;
      },
      cellMouseLeave() {
        this.tableHoverId = '';
      },
      handleChangeTree(val) {
        this.editValue = val[val.length - 1];
      },
      closeFile() {
        this.importFileNameList = [];
        this.$refs.importInput.value = '';
      },
      handleFile(e) {
        const filename = e.target.value.split('\\').slice(-1);
        this.importFileNameList = [];
        if (filename.length !== 0 && filename[0] !== '') {
          this.importFileNameList.push(filename[0]);
          this.isCheckImport = false;
        }
      },
      closeImport() {
        this.importCatalogId = [];
        this.isCheckImport = false;
        this.isImportServiceShow = false;
      },
      importConfirm() {
        const formdata = new FormData();
        formdata.append('file', this.$refs.importInput.files[0]);
        formdata.append('catalog_id', this.importCatalogId.slice(-1));
        formdata.append('project_key', this.$route.query.project_id);
        if (this.importCatalogId.length === 0) {
          this.isCheckImport = true;
          this.errorName = this.$t('m["目录"]');
          return;
        }
        if (this.importFileNameList.length === 0) {
          this.isCheckImport = true;
          this.errorName = this.$t('m["文件"]');
          return;
        }
        this.isImportServiceShow = false;
        this.$store.dispatch('serviceEntry/importService', formdata).then(res => {
          this.$bkMessage({
            message: res.message,
            theme: 'success',
          });
          this.importCatalogId = [];
          this.isImportServiceShow = false;
          this.isCheckImport = false;
          this.getList(1);
        });
      },
      importService() {
        this.isImportServiceShow = true;
      },
      exportService(row) {
        window.open(`${window.SITE_URL}api/service/projects/${row.id}/export/`);
      },
      handleChange(type, row) {
        // this.editValue = row.name
        switch (type) {
          case 'name':
            this.changeFrom.name = row.id;
            this.changeFrom.serviceType = '';
            this.changeFrom.bounded_catalogs = '';
            this.changeFrom.desc = '';
            this.editValue = row.name;
            break;
          case 'desc':
            this.changeFrom.desc = row.id;
            this.changeFrom.serviceType = '';
            this.changeFrom.name = '';
            this.changeFrom.bounded_catalogs = '';
            this.editValue = row.desc;
            break;
          case 'key':
            this.changeFrom.serviceType = row.id;
            this.changeFrom.name = '';
            this.changeFrom.desc = '';
            this.changeFrom.bounded_catalogs = '';
            this.editValue = row.key;
            break;
          case 'catalog_id':
            this.changeFrom.bounded_catalogs = row.id;
            this.changeFrom.name = '';
            this.changeFrom.desc = '';
            this.changeFrom.serviceType = '';
            break;
        }
      },
      closeEdit() {
        this.changeFrom.name = '';
        this.changeFrom.desc = '';
        this.changeFrom.serviceType = '';
        this.changeFrom.bounded_catalogs = '';
      },
      submitEditService(type, row) {
        const curRow = row;
        curRow[type] = this.editValue;
        const params = {
          catalog_id: curRow.catalog_id,
          id: curRow.id,
          key: curRow.key,
          name: curRow.name,
          desc: curRow.desc,
          project_key: curRow.project_key,
        };
        this.$store.dispatch('serviceEntry/updateService', params).then(() => {
          this.$bkMessage({
            message: this.$t('m.serviceConfig["修改成功"]'),
            theme: 'success',
          });
          this.editValue = '';
          this.closeEdit();
          this.getList();
        });
      },
      // 获取数据
      getList(page) {
        // 查询时复位页码
        if (page !== undefined) {
          this.pagination.current = page;
        }
        // 重新获取数据时清空选中的数据
        this.checkList = [];
        const params = {
          page: this.pagination.current,
          page_size: this.pagination.limit,
          project_key: this.$store.state.project.id,
          ordering: '-update_at',
          catalog_id: this.$route.query.catalog_id || this.treeInfo.node.id,
        };
        this.moreSearch.forEach(item => {
          if (item.value !== '' && item.typeKey) {
            params[item.typeKey] = Array.isArray(item.value) ? item.value.join(',') : item.value;
          }
        });
        if (!this.treeInfo.node.id) {
          return;
        }
        this.isDataLoading = true;
        this.listError = false;
        this.$store.dispatch('catalogService/getServices', params).then(res => {
          if (res.data !== null) {
            if (Object.keys(res.data).length > 0) {
              this.dataList = res.data.items;
              this.dataList.forEach(item => {
                this.$set(item, 'checkStatus', false);
              });
              // 分页
              this.pagination.current = res.data.page;
              this.pagination.count = res.data.count;
            } else {
              this.dataList = [];
            }
          } else {
            this.dataList = [];
          }
        })
          .catch(res => {
            this.listError = true;
            errorHandler(res, this);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
      },
      getServiceDirectory() {
        this.$store.dispatch('serviceCatalog/getTreeData', {
          show_deleted: true,
          project_key: this.$store.state.project.id,
        }).then(res => {
          this.dirList = (res.data[0] && res.data[0].children) ? res.data[0].children : res.data;
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      onBasicFormSubmit() {
        this.$refs.basicForm.validate().then(async () => {
          const params = JSON.parse(JSON.stringify(this.formData));
          params.id = this.serviceId || undefined;
          params.project_key = this.$store.state.project.id;
          this.isSubmitting = true;
          await this.createService(params);
          this.isSubmitting = false;
        });
      },
      onBasicFormCancel() {
        this.isBasicFormEditting = false;
      },
      createService(params) {
        this.$store.dispatch('serviceEntry/createService', params).then(res => {
          this.$bkMessage({
            message: this.$t('m.deployPage["保存成功"]'),
            theme: 'success',
          });
          this.$router.push({
            name: 'projectServiceEdit',
            params: {
              type: 'new',
              step: 'basic',
            },
            query: {
              serviceId: res.data.id,
              project_id: this.$store.state.project.id,
              fromCatalog: this.treeInfo.node.id,
            },
          });
          this.isBasicFormEditting = false;
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      // 服务类型
      getServiceTypes() {
        this.$store.dispatch('getCustom').then((res) => {
          this.serviceTypeList = res.data;
          this.serviceTypesMap = res.data;
          this.moreSearch[1].list = res.data;
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      // 服务级别列表
      getSlaList() {
        const params = {
          is_enabled: true,
          project_key: this.$store.state.project.id,
        };
        this.$store.dispatch('slaManagement/getProtocolsList', { params }).then(res => {
          this.slaList = res.data;
          this.moreSearch[2].list = res.data;
          this.moreSearch[2].list.forEach(item => {
            this.$set(item, 'key', item.id);
          });
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      disabledFn(item) {
        return !item.bounded_catalogs[0];
      },
      // 创建服务权限点击时校验
      onServiceCreatePermissonCheck() {
        if (!this.hasPermission(['service_create'], this.$store.state.project.projectAuthActions)) {
          const projectInfo = this.$store.state.project.projectInfo;
          const resourceData = {
            project: [{
              id: projectInfo.key,
              name: projectInfo.name,
            }],
          };
          this.applyForPermission(['service_create'], this.$store.state.project.projectAuthActions, resourceData);
        } else {
          // this.isBasicFormEditting = true
          this.$router.push({
            name: 'projectServiceEdit',
            params: {
              type: 'new',
              step: 'basic',
            },
            query: {
              project_id: this.$route.query.project_id,
              catalog_id: this.$route.query.catalog_id,
            },
          });
        }
      },
      // 编辑
      async changeEntry(item, type) {
        let serviceId = item.id;
        if (type === 'clone') {
          // 获取克隆id
          try {
            const res = await this.$store.dispatch('serviceEntry/cloneService', item.id);
            serviceId = res.data.id;
            if (res.data && res.data.id) {
              this.$router.push({
                name: 'projectServiceEdit',
                params: {
                  type: 'edit',
                  step: 'basic',
                },
                query: {
                  serviceId,
                  project_id: this.$store.state.project.id,
                  catalog_id: this.$route.query.catalog_id,
                },
              });
            }
          } catch (e) {
            this.$bkMessage({
              theme: 'warning',
              message: e.data.message,
            });
          }
        } else {
          this.$router.push({
            name: 'projectServiceEdit',
            params: {
              type: 'edit',
              step: 'basic',
            },
            query: {
              serviceId,
              project_id: this.$store.state.project.id,
              catalog_id: this.$route.query.catalog_id,
            },
          });
        }
      },
      /**
       * 单个服务操作项点击时校验
       * @params {Array} required 需要的权限
       * @params {Object} row 数据对象
       */
      onServicePermissonCheck(required, row) {
        const projectInfo = this.$store.state.project.projectInfo;
        const resourceData = {
          service: [{
            id: row.id,
            name: row.name,
          }],
          project: [{
            id: projectInfo.key,
            name: projectInfo.name,
          }],
        };
        this.applyForPermission(required, [...this.$store.state.project.projectAuthActions, ...row.auth_actions], resourceData);
      },
      deleteCheck() {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.serviceConfig["确认删除服务？"]'),
          subTitle: this.$t('m.serviceConfig["服务一旦删除，对应的服务将不可用。请谨慎操作。"]'),
          confirmFn: () => {
            const idArr = this.checkList.map(item => item.id);
            const id = idArr.join(',');
            if (this.secondClick) {
              return;
            }
            this.secondClick = true;
            this.$store.dispatch('serviceEntry/batchDeleteService', { id }).then(() => {
              this.$bkMessage({
                message: this.$t('m.serviceConfig["删除成功"]'),
                theme: 'success',
              });
              this.getList(1);
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
      // 删除
      deleteOne(item) {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.serviceConfig["确认删除服务？"]'),
          subTitle: this.$t('m.serviceConfig["服务一旦删除，对应的服务将不可用。请谨慎操作。"]'),
          confirmFn: () => {
            const id = item.id;
            if (this.secondClick) {
              return;
            }
            this.secondClick = true;
            this.$store.dispatch('serviceEntry/deleteService', id).then(() => {
              this.$bkMessage({
                message: this.$t('m.serviceConfig["删除成功"]'),
                theme: 'success',
              });
              if (this.dataList.length === 1) {
                this.pagination.current = this.pagination.current === 1 ? 1 : this.pagination.current - 1;
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
      },
      // 简单查询
      searchContent() {
        this.searchToggle = true;
        this.getList(1);
      },
      // 清空搜索表单
      clearSearch() {
        this.moreSearch.forEach(item => {
          item.value = '';
        });
        this.getList(1);
        this.searchToggle = false;
      },
      searchMore() {
        this.$refs.searchInfo.searchMore();
        this.searchToggle = true;
      },
      handlePageChange(page) {
        this.pagination.current = page;
        this.getList();
      },
      // 分页过滤数据
      handlePageLimitChange() {
        this.pagination.limit = arguments[0];
        this.getList();
      },
      changeCheck(value) {
        // 改变中选态，与表头选择相呼应
        this.$refs.serviceTable.toggleRowSelection(value, value.checkStatus);
        if (value.checkStatus) {
          if (!this.checkList.some(item => item.id === value.id)) {
            this.checkList.push(value);
          }
        } else {
          this.checkList = this.checkList.filter(item => item.id !== value.id);
        }
      },
      // 全选 半选
      handleSelectAll(selection) {
        this.dataList.forEach(item => {
          if (this.hasPermission(['service_manage'], [...this.$store.state.project.projectAuthActions, ...item.auth_actions])) {
            item.checkStatus = !!selection.length;
          }
        });
        // 选中有权限数据
        this.checkList = selection.filter(item => this.hasPermission(['service_manage'], [...this.$store.state.project.projectAuthActions, ...item.auth_actions]));
      },
      handleSelect(selection) {
        this.checkList = selection;
      },
      // 流程预览
      processShow(item) {
        const id = item.workflow;
        this.processInfo.isShow = !this.processInfo.isShow;
        this.processInfo.loading = true;
        axios.all([
          this.$store.dispatch('deployCommon/getNodeVersion', { id }),
          this.$store.dispatch('deployCommon/getLineVersion', { id }),
        ]).then(axios.spread((userResp, reposResp) => {
          this.addList = userResp.data;
          for (let i = 0; i < this.addList.length; i++) {
            this.addList[i].indexInfo = i;
          }
          this.lineList = reposResp.data.items;
        }))
          .finally(() => {
            this.processInfo.loading = false;
          });
      },
      hiddenTree() {
        this.isHiddenDirectory = !this.isHiddenDirectory;
      },
    },
  };
</script>
<style lang='scss' scoped>
@import '~@/scss/mixins/scroller.scss';
.icon-itsm-icon-fill-fit {
    color: #2bcb55;
}
.hover-show-icon {
    display: flex;
    align-items: center;
    .operation {
        height: 100%;
        font-size: 20px;
        display: flex;
        i {
            cursor: pointer;
        }
    }
}
.icon-itsm-icon-six {
    display: inline-block;
    font-size: 16px;
    cursor: pointer;
    &:hover {
        color: #3a84ff;
    }
}
.page-content {
    position: relative;
    z-index: 100;
    height: calc(100vh - 104px);
    overflow: auto;
    @include scroller;
    .service-left {
        position: relative;
        height: 100%;
        padding-bottom: 48px;
        width: 240px;
        float: left;
        background-color: #fafbfd;
        transition: width 0.5s ease-in;
        box-shadow: 1px 2px 4px 0px rgba(25,25,41,0.05);
        .hidden-tree {
            position: absolute;
            top: calc(50% - 30px);
            right: -14px;
            width: 14px;
            height: 61px;
            line-height: 61px;
            background-color: #dcdee5;
            cursor: pointer;
            color: #ffffff;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }
    }
    .service-right {
        margin: 24px 24px 0 24px;
        background-color: #f5f7fa;
        float: left;
        transition: width 0.5s ease-in;
        width: calc(100% - 288px);
        /deep/ .bk-table-body-wrapper {
            background: #ffffff;
        }
    }
    .bk-only-btn {
        padding: 12px 0;
        border: 0;
    }
    .hide {
        width: 0;
    }
    .auto-wight {
        width: calc(100% - 48px);
    }
    .bk-search-content {
        width: 400px;
    }
}
.filter-btn /deep/ .icon-search-more {
    font-size: 14px;
}
.bk-form-checkbox {
    padding: 0;
    width: 16px;
    margin: 0 auto;
}
.bk-btn-file {
    float: left;
    line-height: 30px;
    position: relative;
    cursor: pointer;

    .bk-input-file {
        position: absolute;
        top: 0;
        left: 0;
        width: 100px;
        height: 32px;
        overflow: hidden;
        opacity: 0;
        cursor: pointer;
    }
    .bk-input-tip {
        position: absolute;
        top: 0;
        left: 110px;
        font-size: 12px;
        color: #979ba5;
        cursor: auto;
    }
}
.file-list {
    border: 1px solid #e1ecff;
    position: relative;
    margin-left: 150px;
    margin-top: 10px;
    font-size: 12px;
    padding: 1px 5px;
    color: #979ba5;
    .icon-itsm-icon-three-one {
        display: none;
        position: absolute;
        right: 3px;
        top: 4px;
        cursor: pointer;
    }
    &:hover {
        border: 1px solid #3a84ff;
        .icon-itsm-icon-three-one {
            display: block;
            color: red;
        }
    }
}
.import-error-tip {
    font-size: 14px;
    margin-left: 150px;
    margin-top: 10px;
    color: red;
}
.bk-lable-display {
    height: 16px;
    display: flex;
    overflow: hidden;
    max-width: calc(100% - 20px);
}
.bk-lable-primary {
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
}

</style>
