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
  <div class="service-ticket-form">
    <div v-if="formList.length" class="form-list" style="padding: 10px 0">
      <bk-form form-type="vertical">
        <draggable
          data-test-id="service_draggable_serviceFormDrag"
          handle=".dragElement"
          :value="formList"
          :group="{
            name: 'view-form',
            pull: false,
            put: ['view-form', 'half-row-field', 'form-view-item']
          }"
          @end="onRowDragEnd"
          @add="onHalfRowDragToRow">
          <template v-for="(form, index) in formList">
            <!-- 半行表单 -->
            <half-row-form
              v-if="Array.isArray(form)"
              :key="index"
              :row-index="index"
              :workflow-id="serviceInfo.workflow_id"
              :node-id="nodeId"
              :fields="forms"
              :row-forms="form"
              :add-field-status="addFieldStatus"
              :crt-form="crtForm"
              @onHalfRowDragToHalfRow="onHalfRowDragToHalfRow"
              @onFormEditClick="onFormEditClick"
              @onFormCloneClick="onFormCloneClick"
              @onFormDeleteClick="$emit('fieldDelete', $event)"
              @onEditCancel="onEditCancel"
              @onEditConfirm="onEditConfirm">
            </half-row-form>
            <!-- 全行表单 -->
            <template v-else>
              <form-view-item
                :data-id="form.id"
                :key="form.id"
                :fields="forms"
                :form="form"
                :add-field-status="addFieldStatus"
                :crt-form="crtForm"
                @onFormEditClick="onFormEditClick"
                @onFormCloneClick="onFormCloneClick"
                @onFormDeleteClick="$emit('fieldDelete', $event)">
                <div class="dragElement" slot="draggable">
                  <i class="bk-itsm-icon icon-move-new"></i>
                </div>
              </form-view-item>
            </template>
          </template>
        </draggable>
      </bk-form>
    </div>
    <div v-else class="no-form">
      <h3>{{ $t(`m.tickets['暂无服务表单']`) }}</h3>
      <p>{{ $t(`m.tickets['请在左侧的“控件库”或“已有字段”点击添加']`) }}</p>
    </div>
  </div>
</template>

<script>
  import draggable from 'vuedraggable';
  import HalfRowForm from './HalfRowForm';
  // import FormEditItem from './FormEditItem'
  import FormViewItem from './FormViewItem';

  export default {
    name: 'ServiceForm',
    components: {
      draggable,
      HalfRowForm,
      // FormEditItem,
      FormViewItem,
    },
    props: {
      serviceInfo: Object,
      nodeId: Number,
      forms: Array,
      crtForm: [String, Number],
      addFieldStatus: Boolean,
    },
    data() {
      return {
        formList: this.transFieldsToDraggable(this.forms),
      };
    },
    watch: {
      forms(val) {
        this.formList = this.transFieldsToDraggable(val);
      },
    },
    mounted() {
    },
    methods: {
      // 将字段列表转换为拖拽组件所需格式
      transFieldsToDraggable(data) {
        const list = [];
        data.forEach((item) => {
          const lastForm = list[list.length - 1];
          if (item.layout === 'COL_6') {
            if (Array.isArray(lastForm) && lastForm[1] === undefined && item.meta.layout_position === 'right') {
              lastForm[1] = item;
            } else {
              const halfRowForm = item.meta.layout_position === 'right' ? [undefined, item] : [item, undefined];
              list.push(halfRowForm);
            }
            return;
          }
          list.push(item);
        });
        return list;
      },
      // 整行表单拖拽
      onRowDragEnd(evt) {
        // console.log('整行拖拽', evt)
        const id = Number(evt.item.dataset.id);
        const field = this.forms.find(item => item.id === id);
        let targetIndex = evt.newIndex;
        for (let i = 0; i < evt.newIndex; i++) { // 考虑半行表单的情况
          if (Array.isArray(this.formList[i]) && this.formList[i].every(item => item !== undefined)) {
            targetIndex += 1;
          }
        }
        this.$emit('dragUpdateList', targetIndex, field);
      },
      // 半行表单拖拽到整行
      onHalfRowDragToRow(evt) {
        // console.log('半行表单拖拽到整行', evt)
        const id = Number(evt.item.dataset.id);
        let targetIndex = evt.newIndex;
        if (this.forms.find(item => item.id === id)) {
          const field = this.forms.find(item => item.id === id);
          for (let i = 0; i < evt.newIndex; i++) { // 考虑半行表单的情况
            const rowForms = this.formList[i];
            if (Array.isArray(rowForms)) {
              // 存在包含两个半行表单行，且不存在当前拖拽表单
              if (rowForms.every(item => item !== undefined && item.id !== id)) {
                targetIndex += 1;
              }
              // 存在包含一个半行表单行，且该表单为当前拖拽表单
              if (rowForms.some(item => item === undefined) && rowForms.find(item => item && item.id === id)) {
                targetIndex -= 1;
              }
            }
          }
          field.meta.layout_position = 'left';
          this.$emit('dragUpdateList', targetIndex, field);
        } else {
          const field = {
            api_info: evt.item._underlying_vm_.api_info,
            workflow: '',
            id: '',
            key: '',
            name: evt.item._underlying_vm_.name,
            type: evt.item._underlying_vm_.type,
            desc: '',
            layout: 'COL_12',
            validate_type: 'REQUIRE',
            choice: [],
            showFeild: true,
            is_builtin: false,
            source_type: evt.item._underlying_vm_.source_type || 'CUSTOM',
            source_uri: '',
            regex: 'EMPTY',
            custom_regex: '',
            is_tips: false,
            tips: '',
            meta: {},
            default: '',
          };
          this.$emit('onAddFormClick', targetIndex, field);
        }
      },
      // 半行表单拖拽到半行
      onHalfRowDragToHalfRow(evt) {
        let targetIndex;
        const id = Number(evt.item.dataset.id);
        const rowIndex = Number(evt.target.dataset.rowindex);
        const rowForms = this.formList[rowIndex];
        const otherForm = rowForms.find(item => item);
        const otherFormIndex = this.forms.findIndex(item => item.id === otherForm.id);
        if (this.forms.find(item => item.id === id)) {
          const field = this.forms.find(item => item.id === id);
          if (rowForms[0] === undefined) {
            field.meta.layout_position = 'left';
            targetIndex = (field.id === otherForm.id || otherFormIndex === 0) ? otherFormIndex : otherFormIndex - 1;
          } else {
            field.meta.layout_position = 'right';
            targetIndex = (field.id === otherForm.id || otherFormIndex === this.forms.length - 1) ? otherFormIndex : otherFormIndex + 1;
          }
          this.$emit('dragUpdateList', targetIndex, field);
        } else {
          const field = {
            api_info: evt.item._underlying_vm_.api_info,
            workflow: '',
            id: '',
            key: '',
            name: evt.item._underlying_vm_.name,
            type: evt.item._underlying_vm_.type,
            desc: '',
            layout: 'COL_6',
            validate_type: 'REQUIRE',
            choice: [],
            showFeild: true,
            is_builtin: false,
            source_type: evt.item._underlying_vm_.source_type || 'CUSTOM',
            source_uri: '',
            regex: 'EMPTY',
            custom_regex: '',
            is_tips: false,
            tips: '',
            meta: {},
            default: '',
          };
          if (rowForms[0] === undefined) {
            field.meta.layout_position = 'left';
            targetIndex = (field.id === otherForm.id || otherFormIndex === 0) ? otherFormIndex : otherFormIndex - 1;
          } else {
            field.meta.layout_position = 'right';
            targetIndex = (field.id === otherForm.id || otherFormIndex === this.forms.length - 1) ? otherFormIndex : otherFormIndex + 1;
          }
          this.$emit('onAddFormClick', targetIndex, field);
        }
      },
      // 切换为字段编辑
      onFormEditClick(form) {
        this.$emit('onFormEditClick', form);
      },
      // 字段克隆
      onFormCloneClick(form) {
        if (this.crtForm) {
          this.$bkMessage({
            message: this.$t('m["请先将当前字段属性关闭再进行操作"]'),
            theme: 'warning',
          });
          return;
        }
        this.$emit('fieldClone', form);
      },
      // 字段编辑取消
      onEditCancel() {
        if (this.crtForm === 'add') {
          this.$emit('cancelAdd');
        } else {
          this.$emit('update:crtForm', '');
        }
      },
      // 字段编辑保存
      onEditConfirm(form) {
        const originForm = this.forms.find(item => item.id === form.id);
        if (originForm) {
          if (form.layout === 'COL_12') {
            form.layout_position = '';
          } else {
            if (originForm.layout === 'COL_12') {
              form.layout_position = 'left';
            }
          }
        } else {
          if (form.layout === 'COL_6') {
            form.layout_position = 'left';
          }
        }
        this.$emit('saveField', Object.assign({}, originForm, form));
      },
    },
  };
</script>
<style lang='scss' scoped>
@import '~@/scss/mixins/scroller.scss';
.service-ticket-form {
    // margin-top: 16px;
    position: relative;
    // padding: 20px 40px;
    background: #ffffff;
    box-shadow: 0px 2px 6px 0px rgba(6, 6, 6, 0.1);
    min-height: 207px;
    .form-list {
        height: calc(100vh - 212px);
        padding: 10px 0px;
        overflow: auto;
        @include scroller;
    }
    .no-form {
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
        h3 {
            color: #737987;
            font-size: 14px;
        }
        p {
            margin-top: 9px;
            font-size: 12px;
            color: #979ba5;
        }
    }
}
/deep/ .drag-entry {
    position: relative;
    width: 100%;
    height: 0;
    font-size: 0;
    border-top: 2px solid #bdd1f0;
}
</style>
