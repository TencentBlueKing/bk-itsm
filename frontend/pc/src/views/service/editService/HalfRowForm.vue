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
  <div class="half-row-form">
    <!-- <form-edit-item
            v-if="isEdit"
            :fields="fields"
            :form="editForm"
            :workflow-id="workflowId"
            :node-id="nodeId"
            @onEditCancel="$emit('onEditCancel')"
            @onEditConfirm="$emit('onEditConfirm', $event)">
        </form-edit-item> -->
    <div class="row-form-view">
      <template v-for="(group, index) in localForms">
        <draggable
          class="form-drag-wrap"
          handle=".view-form"
          :data-rowindex="rowIndex"
          :value="group"
          :key="index"
          :group="{
            name: 'view-form',
            put: halfRowFormPut
          }"
          @add="$emit('onHalfRowDragToHalfRow', $event)">
          <div class="half-form-item" v-for="item in group" :key="item.id" :data-id="item.id">
            <form-view-item
              :fields="fields"
              :form="item"
              :add-field-status="addFieldStatus"
              :crt-form="crtForm"
              @onFormEditClick="$emit('onFormEditClick', $event)"
              @onFormCloneClick="$emit('onFormCloneClick', $event)"
              @onFormDeleteClick="$emit('onFormDeleteClick', $event)">
              <div class="view-form" slot="draggable">
                <i class="bk-itsm-icon icon-move-new"></i>
              </div>
            </form-view-item>
          </div>
        </draggable>
      </template>
    </div>
  </div>
</template>
<script>
  import draggable from 'vuedraggable';
  // import FormEditItem from './FormEditItem'
  import FormViewItem from './FormViewItem';

  export default {
    name: 'HalfRowForm',
    components: {
      draggable,
      // FormEditItem,
      FormViewItem,
    },
    props: {
      rowIndex: Number,
      workflowId: Number,
      nodeId: Number,
      fields: Array, // 原始字段列表
      rowForms: { // 半行表单数组
        type: Array,
        default: () => ([]),
      },
      crtForm: {
        type: [String, Number],
        default: '',
      },
      addFieldStatus: Boolean,
    },
    data() {
      return {
        isEdit: this.checkEdit(),
        localForms: this.getLocalForms(this.rowForms),
      };
    },
    computed: {
      editForm() {
        if (this.isEdit) {
          return this.rowForms.find(item => item && item.id === this.crtForm);
        }
        return null;
      },
    },
    watch: {
      rowForms(val) {
        this.localForms = this.getLocalForms(val);
      },
      crtForm(val) {
        this.isEdit = val !== '' ? this.checkEdit() : false;
      },
    },
    methods: {
      getLocalForms(forms) {
        return forms.map(item => item === undefined ? [] : [item]);
      },
      checkEdit() {
        return this.rowForms.find(item => item && item.id === this.crtForm);
      },
      halfRowFormPut(to) {
        return to.el.children.length === 0;
      },
    },
  };
</script>
<style lang="scss" scoped>
    .click-status {
        background: rgba(225,236,255,0.50);
        border: 1px solid #a3c5fd;
    }
    .half-row-form {
        min-height: 82px;
        .row-form-view {
            display: flex;
            justify-content: flex-start;
            border-top: 1px solid transparent;
            border-bottom: 1px solid transparent;
            &:hover {
                background: #fcfcfc;
                border-top: 1px solid #dde4eb;
                border-bottom: 1px solid #dde4eb;
            }
            .form-drag-wrap {
                width: 50%;
                &:first-child {
                    /deep/ .form-view-item {
                        justify-content: flex-end;
                        .form-view-content {
                            // padding-right: 34px;
                        }
                    }
                }
                &:nth-child(2n) {
                    /deep/ .form-view-content {
                        // padding-left: 20px;
                    }
                }
            }
            .half-form-item {
                /deep/ .form-view-item {
                    display: flex;
                    border: none;
                    .form-view-content {
                        flex: 1;
                        margin: 0 35px 0 12px;
                    }
                }
            }
        }
    }
</style>
