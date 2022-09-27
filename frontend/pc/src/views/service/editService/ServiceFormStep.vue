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
  <div class="service-form" :class="{ 'hide-field-option': !showFieldOption }">
    <!-- 字段选择 -->
    <div :class="['field-option', isShowField ? 'field-hide' : '']">
      <div style="overflow: hidden; height: 100%;">
        <div class="field-type">{{ $t(`m['字段类型']`)}}</div>
        <div class="show-field" @click="handleShowField">
          <i :class="['bk-itsm-icon', isShowField ? 'icon-xiangyou1' : 'icon-xiangzuo1']"></i>
        </div>
        <div style="    display: flex; height: calc(100% - 100px); flex-direction: column;">
          <div class="field-content">
            <!-- <div class="field-title">控件库</div> -->
            <div class="field-title">
              <span>{{ $t(`m['控件库']`) }}</span>
              <bk-input class="search-field" size="small" :right-icon="'bk-icon icon-search'" @enter="handleSearchLibrary"></bk-input>
            </div>
            <ul class="field-list">
              <li class="field-item" v-for="(field, index) in fieldsLibrary" :key="index" @click="onAddFormClick(field)">
                <span v-bk-tooltips.light="field.name" class="field-name">{{ field.name }}</span>
              </li>
            </ul>
            <div v-if="fieldsLibrary.length === 0" class="public-field"><i class="bk-itsm-icon icon-itsm-icon-four-zero" style="font-size: 14px"></i> 已有字段不存在你搜索的内容</div>
          </div>
          <div class="field-content">
            <!-- <div class="field-title">已有字段</div> -->
            <div class="field-title">
              <span>{{ $t(`m['已有字段']`) }}</span>
              <bk-input class="search-field" size="small" :right-icon="'bk-icon icon-search'" @enter="handleSearchField"></bk-input>
            </div>
            <ul class="field-list">
              <li class="field-item" v-for="(field, index) in publicFields" :key="index" @click="addField(field)">
                <span class="field-name" v-bk-tooltips.light="field.name">{{ field.name }}</span>
              </li>
            </ul>
            <div v-if="publicFields.length === 0" class="public-field"><i class="bk-itsm-icon icon-itsm-icon-four-zero" style="font-size: 14px"></i> 已有字段不存在你搜索的内容</div>
          </div>
        </div>
      </div>
    </div>
    <!-- 基础信息 -->
    <div class="basic-body">
      <section data-test-id="servie_section_serviceticketInformation" class="settion-card create-info-card">
        <!-- 选择服务模板1 -->
        <div v-if="!showFieldOption" class="service-template">
          <div class="template-type" v-for="(way, index) in serviceFormCreateWays.slice(0, 2)"
            :key="index"
            data-test-id="servie_section_QuicklyCreateForm"
            @click="onCreateFormWayCLick(way)">
            <i class="bk-itsm-icon icon-it-new-globalview"></i>
            <span>{{way.name}}</span>
          </div>
        </div>
        <div class="create-service-form" v-bkloading="{ isLoading: formLoading }">
          <div>
            <ServiceForm
              ref="serviceForm"
              :add-field-status="addFieldStatus"
              :service-info="serviceInfo"
              :node-id="createTicketNodeId"
              :forms="ticketNodeForm"
              :crt-form.sync="crtForm"
              @dragUpdateList="dragUpdateList"
              @onAddFormClick="onAddFormClick"
              @addField="addField"
              @onFormEditClick="onFormEditClick"
              @cancelAdd="cancelAddField"
              @fieldClone="fieldClone"
              @fieldDelete="fieldDelete"
              @saveField="saveField">
            </ServiceForm>
          </div>
        </div>
      </section>
    </div>
    <div v-show="crtForm" class="drag-line" @mousedown="handleDragLine"></div>
    <div v-show="crtForm" class="edit-service-field">
      <div class="edit-service-title">{{$t(`m['字段属性']`) }}</div>
      <div class="edit-service-forms">
        <template v-for="form in ticketNodeForm">
          <form-edit-item
            v-if="form.id === crtForm"
            :key="form.id"
            :fields="ticketNodeForm"
            :form="form"
            :workflow-id="serviceInfo.workflow_id"
            :node-id="createTicketNodeId"
            @onEditCancel="onEditCancel"
            @getAddFieldStatus="getAddFieldStatus"
            @onEditConfirm="onEditConfirm">
          </form-edit-item>
        </template>
      </div>
    </div>
    <bk-dialog
      width="800"
      :value="isCreateService"
      :mask-close="false"
      :title="$t(`m['创建服务']`)"
      :auto-close="false"
      @confirm="onBasicFormSubmit"
      @cancel="onBasicFormCancel">
      <bk-form
        ref="basicForm"
        form-type="vertical"
        :label-width="300"
        class="basic-form"
        :rules="rules"
        :model="formData">
        <bk-form-item
          data-test-id="service-input-serviceName"
          :label="$t(`m.newCommon['服务名称']`)"
          :required="true"
          property="name"
          error-display-type="normal">
          <bk-input v-model="formData.name" :maxlength="100" :show-word-limit="true"></bk-input>
        </bk-form-item>
        <bk-form-item
          :label="$t(`m.serviceConfig['服务描述']`)"
          property="desc">
          <bk-input v-model="formData.desc" type="textarea" :row="3" :maxlength="255"></bk-input>
        </bk-form-item>
        <bk-form-item
          data-test-id="service-select-serviceDirectory"
          :label="$t(`m.tickets['所属目录']`)"
          :required="true"
          property="catalog_id"
          error-display-type="normal">
          <select-tree
            v-model="formData.catalog_id"
            :list="dirList"
            ext-cls="bk-form-width">
          </select-tree>
        </bk-form-item>
        <bk-form-item
          data-test-id="service-select-serviceType"
          :label="$t(`m.serviceConfig['服务类型']`)"
          :required="true"
          property="key"
          error-display-type="normal">
          <bk-select v-model="formData.key"
            :placeholder="$t(`m.serviceConfig['请选择服务类型']`)"
            :clearable="false"
            searchable
            :font-size="'medium'">
            <bk-option v-for="option in serviceTypeList"
              :key="option.key"
              :id="option.key"
              :name="option.name">
            </bk-option>
          </bk-select>
        </bk-form-item>
      </bk-form>
    </bk-dialog>
    <!-- 选择服务模板 -->
    <choose-service-template-dialog
      :is-show.sync="isShowChooseSerTempDialog"
      :create-info="currCreateFormWay"
      :service-id="serviceId"
      @updateServiceSource="updateServiceSource">
    </choose-service-template-dialog>
  </div>
</template>

<script>
  import { errorHandler } from '../../../utils/errorHandler.js';
  import commonMix from '../../commonMix/common.js';
  import { deepClone } from '../../../utils/util.js';
  import SelectTree from '../../../components/form/selectTree/index.vue';
  import ServiceForm from './ServiceForm.vue';
  import ChooseServiceTemplateDialog from './ChooseServiceTemplateDialog.vue';
  import FormEditItem from './FormEditItem.vue';
  import i18n from '@/i18n/index.js';

  const fieldsLibrary = [
    { name: i18n.t('m[\'单行文本\']'), icon: 'icon-apps', type: 'STRING' },
    { name: i18n.t('m[\'多行文本\']'), icon: 'icon-apps', type: 'TEXT' },
    { name: i18n.t('m[\'数字\']'), icon: 'icon-apps', type: 'INT' },
    { name: i18n.t('m[\'日期\']'), icon: 'icon-apps', type: 'DATE' },
    { name: i18n.t('m[\'时间\']'), icon: 'icon-apps', type: 'DATETIME' },
    { name: i18n.t('m[\'表格\']'), icon: 'icon-apps', type: 'TABLE' },
    { name: i18n.t('m[\'单选下拉框\']'), icon: 'icon-apps', type: 'SELECT' },
    { name: i18n.t('m[\'可输入单选下拉框\']'), icon: 'icon-apps', type: 'INPUTSELECT' },
    { name: i18n.t('m[\'多选下拉框\']'), icon: 'icon-apps', type: 'MULTISELECT' },
    { name: i18n.t('m[\'复选框\']'), icon: 'icon-apps', type: 'CHECKBOX' },
    { name: i18n.t('m[\'单选框\']'), icon: 'icon-apps', type: 'RADIO' },
    { name: i18n.t('m[\'单选人员选择\']'), icon: 'icon-apps', type: 'MEMBER' },
    { name: i18n.t('m[\'多选人员选择\']'), icon: 'icon-apps', type: 'MEMBERS' },
    { name: i18n.t('m[\'富文本\']'), icon: 'icon-apps', type: 'RICHTEXT' },
    { name: i18n.t('m[\'附件上传\']'), icon: 'icon-apps', type: 'FILE' },
    { name: i18n.t('m[\'自定义表格\']'), icon: 'icon-apps', type: 'CUSTOMTABLE' },
    { name: i18n.t('m[\'树形选择\']'), icon: 'icon-apps', type: 'TREESELECT' },
    { name: i18n.t('m[\'链接\']'), icon: 'icon-apps', type: 'LINK' },
    { name: i18n.t('m[\'自定义表单\']'), icon: 'icon-apps', type: 'CUSTOM-FORM' },
  ];
  const serviceFormCreateWays = [
    { name: i18n.t('m[\'选择推荐服务模板\']'), key: 'recom', icon: 'icon-apps' },
    { name: i18n.t('m[\'从已有的服务复制\']'), key: 'created', icon: 'icon-apps' },
    { name: i18n.t('m[\'自定义表单\']'), key: 'custom', icon: 'icon-apps' },
  ];
  export default {
    name: 'ServiceFormStep',
    components: {
      SelectTree,
      ServiceForm,
      ChooseServiceTemplateDialog,
      FormEditItem,
    },
    mixins: [commonMix],
    props: {
      type: {
        type: String,
        default: 'new',
      },
      serviceId: {
        type: [String, Number],
        default: '',
      },
      serviceInfo: {
        type: Object,
        default: () => ({}),
      },
      createTicketNodeId: Number,
    },
    data() {
      return {
        isCreateService: false,
        fieldsLibrary,
        serviceFormCreateWays,
        publicFields: [], // 已有字段
        isSubmitting: false,
        isDropdownShow: false,
        showFieldOption: false,
        isBasicFormEditting: true, // 基础信息处于编辑状态
        isShowChooseSerTempDialog: false, // 选择服务模板
        currCreateFormWay: {},
        ticketNodeForm: [], // 提单节点字段列表
        ticketNodeDetail: {}, // 提单节点详情
        formLoading: false,
        detailLoading: false,
        crtForm: '', // 当前编辑的字段
        active: 'library-fields',
        formData: {
          name: '',
          desc: '',
          key: '',
          catalog_id: '',
        },
        rules: {},
        dirList: [], // 服务目录
        serviceTypeList: [], // 服务类型
        pending: {
          deleteField: false,
          saveField: false,
        },
        serviceTemplateDisable: false,
        isShowField: false,
        isShowRightEdit: false,
        addFieldStatus: true,
        dragLine: {
          base: 0,
          move: 0,
          startX: null,
          maxLength: 0,
          canMove: false,
        },
        fieldIndex: '',
        fieldlist: [],
        fieldsLibrarylist: fieldsLibrary,
        servcieList: [],
      };
    },
    computed: {
      catalogDisplayName() {
        return this.serviceInfo.bounded_catalogs ? this.serviceInfo.bounded_catalogs.join('/') : '';
      },
    },
    watch: {
      isBasicFormEditting: {
        handler(val) {
          if (val) this.getServiceDirectory();
        },
        immediate: true,
      },
    },
    created() {
      const nameRules = [
        {
          required: true,
          message: this.$t('m.treeinfo["字段必填"]'),
          trigger: 'blur',
        },
        {
          validator: this.handleRepeatServiceName,
          message: this.$t('m[\'服务名称重复，请重新输入\']'),
          trigger: 'blur',
        },
      ];
      this.rules.name = nameRules;
      this.rules.directory_id = this.checkCommonRules('required').required;
      this.rules.key = this.checkCommonRules('required').required;
      this.showFieldOption = this.type === 'edit' && !!this.serviceInfo.source;
      this.isBasicFormEditting = this.type === 'new';
      this.serviceTemplateDisable = this.serviceId !== '';
    },
    async mounted() {
      this.getAllServcie();
      this.getPublicFieldList();
      this.getServiceTypes();
      const { name, desc, catalog_id: catalogId, key } = this.serviceInfo;
      this.formData.name = name;
      this.formData.desc = desc;
      this.formData.catalog_id = catalogId;
      this.formData.key = key;
      if (this.type === 'edit') {
        this.getCreateTicketNodeForm();
        this.getCreateTicketNodeDetail();
      } else {
        this.isCreateService = true;
        this.formData.catalog_id = this.$route.query.catalog_id || '';
      }
    },
    methods: {
      getAllServcie() {
        const params = {
          project_key: this.$store.state.project.id,
          catalog_id: 1,
        };
        this.$store.dispatch('catalogService/getServices', params).then(res => {
          this.servcieList = res.data || [];
        });
      },
      async handleRepeatServiceName(val) {
        return !this.servcieList.find(item => item.name === val);
      },
      handleDragLine(e) {
        document.addEventListener('mouseup', this.handleMouseUp, false);
        document.addEventListener('mousemove', this.handleLineMouseMove, false);
        const el = document.querySelector('.edit-service-field');
        this.dragLine.maxLength = el.clientWidth;
        this.dragLine.startX = e.pageX;
        this.dragLine.canMove = true;
      },
      handleMouseUp() {
        document.removeEventListener('mouseup', this.handleMouseUp, false);
        document.removeEventListener('mousemove', this.handleLineMouseMove, false);
        this.dragLine.base = this.dragLine.move;
        this.dragLine.canMove = false;
      },
      handleLineMouseMove(e) {
        if (!this.dragLine.canMove) return;
        const el = document.querySelector('.edit-service-field');
        const { startX, base } = this.dragLine;
        const offsetX = e.pageX - startX;
        const moveX = base + offsetX;
        if (offsetX > 0 && 600 - moveX <= 500) return;
        window.requestAnimationFrame(() => {
          this.dragLine.move = moveX;
          el.style.width = `calc(600px - ${moveX}px)`;
        });
      },
      onFormEditClick(form) {
        this.isShowRightEdit = true;
        this.crtForm = form.id;
      },
      onEditConfirm(form) {
        this.$refs.serviceForm.onEditConfirm(form);
        this.isShowRightEdit = false;
      },
      onEditCancel() {
        this.cancelAddField();
        this.crtForm = '';
        this.isShowRightEdit = false;
      },
      getAddFieldStatus(status) {
        this.addFieldStatus = status;
      },
      // 获取已有字段（公共字段）
      getPublicFieldList() {
        this.$store.dispatch('publicField/get_template_common_fields', { project_key: this.$store.state.project.id }).then((res) => {
          // 隐藏字段
          // const list = res.data.filter(item => item.key !== 'title' && !item.is_builtin && item.key !== 'bk_biz_id')
          this.fieldlist = res.data;
          this.publicFields = res.data;
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      filterFiled(value, fieldlist, field) {
        if (value !== '') {
          const list = fieldlist.filter(item => {
            const reg = RegExp(value);
            if (item.name.match(reg)) {
              return item;
            }
          });
          this[`${field}`] = list;
        } else {
          this[`${field}`] = fieldlist;
        }
      },
      handleSearchLibrary(value) {
        this.filterFiled(value, this.fieldsLibrarylist, 'fieldsLibrary');
      },
      handleSearchField(value) {
        this.filterFiled(value, this.fieldlist, 'publicFields');
      },
      // 服务类型
      getServiceTypes() {
        this.$store.dispatch('getCustom').then((res) => {
          this.serviceTypeList = res.data;
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      // 获取提单节点字段
      getCreateTicketNodeForm() {
        this.formLoading = true;
        this.$store.dispatch('deployCommon/getFieldList', {
          workflow: this.serviceInfo.workflow_id,
          state: this.createTicketNodeId,
        }).then(res => {
          res.data.forEach(item => {
            item.checkValue = false;
            item.val = Object.prototype.hasOwnProperty.call(item, 'default') ? deepClone(item.default) : '';
            item.showFeild = true;
          });
          this.ticketNodeForm = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.formLoading = false;
          });
      },
      // 获取提单节点详情
      getCreateTicketNodeDetail() {
        this.detailLoading = true;
        this.$store.dispatch('deployCommon/getOneStateInfo', {
          id: this.createTicketNodeId,
        }).then(res => {
          this.ticketNodeDetail = res.data;
        })
          .finally(() => {
            this.detailLoading = false;
          });
      },
      onBasicFormSubmit() {
        if (this.isSubmitting) {
          return;
        }
        this.$refs.basicForm.validate().then(async () => {
          const params = JSON.parse(JSON.stringify(this.formData));
          params.id = this.serviceId || undefined;
          params.project_key = this.$store.state.project.id;
          this.isSubmitting = true;
          if (this.type === 'edit') {
            await this.updateServiceInfo(params);
          } else {
            await this.createService(params);
          }
          this.isSubmitting = false;
        });
      },
      onBasicFormCancel() {
        if (this.type === 'new') {
          this.isCreateService = false;
          this.$bkInfo({
            type: 'warning',
            title: this.$t('m.slaContent["确认返回？"]'),
            confirmFn: () => {
              this.goBackToServiceList();
            },
            cancelFn: () => {
              this.isCreateService = true;
            },
          });
        } else {
          this.isBasicFormEditting = false;
        }
      },
      goBackToServiceList() {
        this.$router.push({
          name: 'projectServiceList',
          query: {
            project_id: this.$store.state.project.id,
            catalog_id: this.$route.query.catalog_id,
          },
        });
      },
      // 创建服务
      createService(params) {
        this.$store.dispatch('serviceEntry/createService', params).then(res => {
          this.$bkMessage({
            message: this.$t('m.deployPage["保存成功"]'),
            theme: 'success',
          });
          this.$router.push({
            name: 'projectServiceEdit',
            params: {
              type: 'edit',
              step: 'basic',
            },
            query: {
              serviceId: res.data.id,
              project_id: this.$store.state.project.id,
            },
          });
          this.isBasicFormEditting = false;
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      // 修改服务
      updateServiceInfo(params) {
        this.$store.dispatch('serviceEntry/updateService', params).then(res => {
          this.$bkMessage({
            message: this.$t('m.serviceConfig["修改成功"]'),
            theme: 'success',
          });
          this.isBasicFormEditting = false;
          this.$emit('updateServiceInfo', res.data);
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      // 关联目录树组件
      async getServiceDirectory() {
        await this.$store.dispatch('serviceCatalog/getTreeData', {
          show_deleted: true,
          project_key: this.$store.state.project.id,
        }).then(res => {
          this.dirList = (res.data[0] && res.data[0].children) ? res.data[0].children : res.data;
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      async onCreateFormWayCLick(way) {
        if (this.isBasicFormEditting) {
          try {
            await this.$refs.basicForm.validate();
          } catch (error) {
            return console.warn(error);
          }
        }
        const key = way.key;
        if (key === 'recom' || key === 'created') {
          this.isShowChooseSerTempDialog = true;
          this.currCreateFormWay = way;
        } else {
          this.updateServiceSource('custom');
        }
      },
      createServicePopoverShow() {
        this.isDropdownShow = true;
      },
      createServicePopoverHide() {
        this.isDropdownShow = false;
      },
      // 更新原字段列表顺序
      dragUpdateList(targetIndex, field) {
        if (!field) {
          this.$bkMessage({
            message: this.$t('m["请先保存字段"]'),
            offsetY: 80,
          });
          return;
        }
        const index = this.ticketNodeForm.findIndex(item => item.id === field.id);
        this.ticketNodeForm.splice(index, 1);
        this.ticketNodeForm.splice(targetIndex, 0, field);
        if (field.layout === 'COL_6') { // 如果拖动表单存在半行位置字段，则需要保存更新后的位置信息
          this.saveHalfRowDragPos(field);
        }
      },
      // 点击字段控件
      onAddFormClick(val) {
        const field = {
          workflow: '',
          id: '',
          key: '',
          name: '',
          type: val.type,
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
          meta: {},
          default: '',
        };
        this.addField(field);
      },
      // 添加字段
      addField(field) {
        if (this.crtForm !== '') {
          this.$bkMessage({
            message: this.$t('m["请先将字段属性关闭"]'),
          });
          return;
        }
        this.isShowRightEdit = true;
        const form = Object.assign(deepClone(field), { id: 'add' });
        this.ticketNodeForm.push(form);
        this.crtForm = 'add';
      },
      // 取消添加字段
      cancelAddField() {
        const index = this.ticketNodeForm.findIndex(item => item.id === 'add');
        if (index !== -1) {
          this.ticketNodeForm.splice(index, 1);
        }
        this.crtForm = '';
      },
      // 字段克隆
      fieldClone(form) {
        const index = this.ticketNodeForm.findIndex(item => item.id === form.id);
        const clonedForm = Object.assign(deepClone(form), { id: 'add' });
        this.ticketNodeForm.splice(index + 1, 0, clonedForm);
        this.crtForm = 'add';
      },
      fieldDelete(form) {
        if (this.crtForm) {
          this.$bkMessage({
            message: this.$t('m["请先将当前字段属性关闭再进行操作"]'),
            theme: 'warning',
          });
          return;
        }
        if (form.id === 'add') {
          this.onEditCancel();
          return;
        }
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.treeinfo["确认删除此字段？"]'),
          subTitle: this.$t('m.treeinfo["字段一旦删除，此字段将不在可用。请谨慎操作。"]'),
          confirmFn: () => {
            if (this.pending.deleteField) {
              return;
            }
            this.pending.deleteField = true;
            this.crtForm = '';
            const data = {
              id: form.id,
              params: {
                state_id: this.createTicketNodeId,
              },
            };
            this.$store.dispatch('deployCommon/deleteField', data).then(() => {
              this.$bkMessage({
                message: this.$t('m.systemConfig["删除成功"]'),
                theme: 'success',
              });
              const index = this.ticketNodeForm.findIndex(item => item.id === form.id);
              this.ticketNodeForm.splice(index, 1);
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.pending.deleteField = false;
              });
          },
        });
        this.isShowRightEdit = false;
      },
      // 保存字段
      saveField(field) {
        const index = this.ticketNodeForm.findIndex(item => item.id === field.id);
        field.checkValue = false;
        field.showFeild = true;
        field.val = Object.prototype.hasOwnProperty.call(field, 'default') ? deepClone(field.default) : '';
        if (index > -1) { // 编辑
          this.ticketNodeForm.splice(index, 1, field);
        } else { // 新增
          this.ticketNodeForm.splice(-1, 1, field);
        }
        this.crtForm = '';
      },
      // 保存字段半行拖拽后的位置
      saveHalfRowDragPos(field) {
        const url = field.source === 'TABLE' ? 'cdeploy/changeNewModuleField' : 'cdeploy/changeNewField';
        this.$store.dispatch(url, { params: field, id: field.id });
      },
      /**
       * 记录服务表单创建来源
       */
      updateServiceSource(source) {
        this.getCreateTicketNodeForm(); // 刷新列表
        this.$store.dispatch('service/updateServiceSource', {
          id: this.serviceId,
          params: {
            source,
          },
        }).then(() => {
          this.serviceInfo.source = source;
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      // 校验当前步骤
      async validate() {
        if (this.isBasicFormEditting) {
          await this.$refs.basicForm.validate();
        }
        // if (!this.showFieldOption) {
        //     this.$bkMessage({
        //         message: '请选择服务提单信息创建方式',
        //         theme: 'error'
        //     })
        //     return { data: { result: false } }
        // }
        if (!this.formLoading && !this.detailLoading && this.$refs.serviceForm) {
          // 用全量节点详情字段，传到后台接口，会抛出节点 desc 字段不能为空校验失败信息
          const {
            assignors, assignors_type, can_deliver, delivers, delivers_type, distribute_type, extras,
            is_draft, is_terminable, name, processors, processors_type, tag, type, workflow,
          } = this.ticketNodeDetail;
          const fields = this.ticketNodeForm.filter(item => typeof item.id === 'number').map(item => item.id);
          const nodeDetail = {
            assignors,
            assignors_type,
            can_deliver,
            delivers,
            delivers_type,
            distribute_type,
            extras,
            is_draft,
            is_terminable,
            name,
            processors,
            processors_type,
            tag,
            type,
            workflow,
            fields,
          };
          return this.$store.dispatch('deployCommon/updateNode', {
            params: nodeDetail,
            id: this.createTicketNodeId,
          }).then(() => {
            this.$bkMessage({
              message: this.$t('m.treeinfo["保存成功"]'),
              theme: 'success',
            });
          }, (res) => {
            errorHandler(res, this);
            return Promise.reject(res);
          });
        }
      },
      handleShowField() {
        this.isShowField = !this.isShowField;
      },
    },
  };
</script>
<style lang='scss' scoped>
@import '~@/scss/mixins/scroller.scss';
@import '~@/scss/mixins/ellipsis.scss';
.field-tab {
    /deep/ .bk-tab-label-wrapper {
        display: flex;
        justify-content: center;
    }
    /deep/ .bk-tab-section {
        position: relative;
        padding: 0;
        height: calc(100vh - 268px);
        overflow: auto;
        @include scroller;
    }
}
.dropdown-trigger-text {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    color: #737987;
    font-weight: normal;
    cursor: pointer;
}
.dropdown-trigger-text .bk-icon {
    font-size: 22px;
}
.bk-dropdown-list {
    width: 120px;
    background: #ffffff;
    border: 1px solid #dcdee5;
    border-radius: 2px;
    > li {
        padding: 0 10px;
        width: 100%;
        height: 32px;
        line-height: 32px;
        font-size: 12px;
        color: #63656e;
        @include ellipsis(100%);
        cursor: pointer;
        font-weight: normal;
        &:hover {
            color: #3a84ff;
            background: #f4f6fa;
        }
    }
}
.service-form {
    display: flex;
    height: calc(100vh - 164px);
    overflow: hidden;
    &.hide-field-option {
        .basic-body {
            width: 100%;
        }
    }
    .field-hide {
        border-right: 0px solid #dde4eb !important;
        width: 0 !important;
    }
    .field-option {
        height: calc(100vh - 164px);
        float: left;
        width: 280px;
        position: relative;
        background: #fcfcfc;
        border-right: 1px solid #dde4eb;
        border-top: 1px solid #dde4eb;
        display: flex;
        flex-direction: column;
        // transition: width 0.5s ease-in;
        .field-type {
            width: 100%;
            height: 45px;
            padding: 0 21px;
            line-height: 45px;
            font-size: 14px;
            font-weight: 500;
            color: #313238;
            border-bottom: 1px solid #e0e0e0;
        }
        .show-field {
            position: absolute;
            right: -14px;
            width: 14px;
            height: 64px;
            top: 50%;
            background-color: #dcdee5;
            border-radius: 0px 4px 4px 0px;
            line-height: 64px;
            text-align: center;
            cursor: pointer;
        }
        .field-content {
            flex: 1;
            width: 100%;
            padding: 0 7px 0px 12px;
            margin: 4px 0;
            .field-title {
                width: 100%;
                height: 36px;
                padding: 8px 0;
                line-height: 20px;
                color: #c4c6cc;
                font-size: 12px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                .search-field {
                    width: 150px;
                    margin-right: 8px;
                }
            }
            .field-list {
                overflow: auto;
                @include scroller;
                width: 100%;
                max-height: calc((100vh - 300px) / 2);
                .field-item {
                    width: 120px;
                    padding: 0 20px;
                    margin: 4px;
                    float: left;
                    height: 32px;
                    line-height: 32px;
                    border-radius: 2px;
                    background: #ffffff;
                    border: 1px solid #e0e0e0;
                    color: #63656e;
                    font-size: 12px;
                    cursor: pointer;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }
            }
            .public-field {
                height: 300px;
                width: 100%;
                line-height: 300px;
                font-size: 12px;
                text-align: center;
                color: #c4c6cc
            }
        }
    }
    .basic-body {
        flex: 1;
        // width: 632px;
        margin: 24px;
        // float: left;
        // padding: 15px;create-info-card
        // width: calc(100% - 280px);
        // height: calc(100vh - 225px);
        overflow: auto;
        @include scroller;
    }
    .drag-line {
        width: 2px;
        height: 100%;
        background-color: #fff;
        &:hover {
            // width: px;
            background-color: #3a84ff;
            cursor: col-resize;
        }
    }
    .edit-service-field {
        width: 500px;
        background: #ffffff;
        border-left: 1px solid #dde4eb;
        border-top: 1px solid #dde4eb;
        box-shadow: 0px 2px 6px 0px rgba(6,6,6,0.10);
        .edit-service-title {
            width: 100%;
            height: 40px;
            line-height: 22px;
            font-size: 14px;
            padding: 9px 24px;
            border-bottom: 1px solid #dde4eb;
        }
        .edit-service-forms {
            width: 100%;
            height: calc(100% - 40px);
            overflow-y: auto;
            overflow-x: hidden;
            @include scroller;
        }
    }
}
.settion-card {
    margin: auto;
    // max-width: 1000px;
    .card-title {
        margin: 0;
        font-size: 14px;
        font-weight: 700;
        color: #63656e;
    }
    .card-content {
        margin-top: 16px;
        background: #ffffff;
        border-radius: 2px;
        box-shadow: 0px 2px 6px 0px rgba(6,6,6,0.10);
        overflow: hidden;
    }
}
.basic-info-card {
    .basic-form {
        margin: auto;
        width: 600px;
    }
    .card-content {
        padding-bottom: 0;
    }
    .sbmit-buttons {
        margin-top: 60px;
        padding: 7px 0;
        display: flex;
        justify-content: flex-end;
        box-shadow: 0px -1px 0px 0px #dde4eb;
        .button-item {
            margin-left: 5px;
        }
    }
    .service-basic-form {
        padding: 32px 20px;
        padding-bottom: 0;
    }
    .service-basic-info {
        padding: 32px 20px;
        position: relative;
        padding-bottom: 31px;
        &:hover {
            background: #fcfcfc;
            .mask {
                display: block;
            }
            .opt-btns {
                right: 0;
            }
        }
        .mask {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            display: block;
            z-index: 1;
        }
        .opt-btns {
            display: flex;
            align-items: center;
            justify-content: center;
            position: absolute;
            right: -32px;
            top: 0;
            width: 32px;
            height: 100%;
            z-index: 2;
            border-left: 1px solid #dde4eb;
            text-align: center;
            transition: right .3s;
            .btn-item {
                margin-top: 8px;
                display: inline-block;
                color: #979ba5;
                cursor: pointer;
                &:hover {
                    color: #63656E;
                }
            }
        }
        .service-title {
            font-size: 16px;
            font-weight: 700;
            color: #313238;
            line-height: 21px;
        }
        .service-dir, .service-desc {
            font-size: 12px;
            color: #737987;
            line-height: 16px;
        }
        .service-dir {
            margin-left: 8px;
            display: inline-block;
        }
    }
}
// 提单信息
.create-info-card {
    height: calc(100vh - 212px);
    overflow: hidden;
    box-shadow: 0px 2px 6px 0px rgba(6,6,6,0.10);
    background-color: #fff;
    // margin-top: 32px;
    .service-template {
        width: 100%;
        height: 96px;
        padding: 24px 12px;
        display: flex;
        justify-content: space-between;
        .template-type {
            border: 1px dashed #dcdee5;
            flex: 1;
            margin: 0 12px;
            height: 48px;
            font-size: 14px;
            text-align: center;
            line-height: 48px;
            cursor: pointer;
            i {
                color: #c4c6cc;
            }
            span {
                color: #737987;
                margin-left: 14px;
            }
        }
    }
    .card-title {
        display: flex;
        justify-content: space-between;
    }
    .create-way {
        margin-top: 16px;
        display: flex;
        height: 348px;
        border: 1px dashed #dde4eb;
        background: #fcfcfc;
        .create-way-item {
            flex: 1;
            height: 100%;
            display: inline-block;
            text-align: center;
            &:not(:first-child) {
                border-left: 1px dashed #dde4eb;
            }
            .bk-icon {
                display: block;
                margin-top: 96px;
                font-size: 60px;
                color: #dde4eb;
            }
            .create-way-desc {
                margin-top: 50px;
                font-size: 14px;
                color: #737987;
            }
            .button-tips {
                .button-item {
                    margin-top: 25px;
                }
            }
        }
    }
}
</style>
<style lang="scss">
    .create-service-popover {
        .tippy-tooltip {
            padding: 0;
        }
    }
</style>
