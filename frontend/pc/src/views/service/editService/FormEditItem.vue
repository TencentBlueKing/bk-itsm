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
  <div ref="formEditItem" class="form-edit-item">
    <add-field
      ref="addField"
      form-align="horizontal"
      :change-info="formData"
      :workflow="workflowId"
      :state="nodeId"
      :auto-selected-type="false"
      @onConfirm="onConfirmClick"
      @getAddFieldStatus="getAddFieldStatus"
      @onCancel="$emit('onEditCancel')">
    </add-field>
  </div>
</template>
<script>
  import AddField from '../../processManagement/processDesign/nodeConfigue/addField';
  import { deepClone } from '../../../utils/util.js';

  export default {
    name: 'FormEditItem',
    components: {
      AddField,
    },
    props: {
      form: Object,
      workflowId: Number,
      nodeId: Number,
    },
    data() {
      const formData = deepClone(this.form);
      return {
        formData,
      };
    },
    mounted() {
      this.$refs.formEditItem.scrollIntoView({ block: 'center' });
    },
    methods: {
      onConfirmClick(form) {
        this.$emit('onEditConfirm', deepClone(form));
      },
      getAddFieldStatus(status) {
        // console.log(arguments)
        this.$emit('getAddFieldStatus', status);
      },
    },
  };
</script>
<style lang="scss" scoped>
    .form-edit-item {
        width: 100%;
        padding: 24px;
        background: #fcfcfc;
        border-top: 1px solid #dde4eb;
        border-bottom: 1px solid #dde4eb;
    }
    /deep/ .bk-halfline-item {
        display: block;
        width: 100%;
    }
    /deep/ .bk-half {
        width: 100%;
    }
    /deep/.bk-add-field {
        & > .bk-form {
            margin: 0 auto;
            max-width: 600px;
            & > .bk-form-item {
                & > .bk-label {
                    width: 100px !important;
                }
                & > .bk-form-content {
                    clear: unset;
                    margin-left: 100px !important;
                }
            }
            .bk-data-source {
                .bk-halfline-item:first-child {
                    margin-bottom: 6px;
                }
            }
            .bk-custom-line .bk-custom-icon .bk-itsm-icon {
                margin-right: 0;
            }
            .field-input-tips {
                width: 100%;
            }
            .field-tips-checkbox {
                margin-left: 0px !important;
                position: relative;
                top: 36px;
            }
            .bk-label-tips {
                right: 0;
                left: auto;
            }
            .bk-hidden-conditions .bk-between-operat {
                width: 60px;
                .bk-itsm-icon {
                    font-size: 14px;
                }
                .icon-flow-add {
                    margin-right: 4px;
                }
            }
            .bk-default-value {
                .editor-btn-group {
                    top: -24px;
                    font-size: 12px;
                }
            }
        }
        .operate-btns {
            margin: 0 20px;
            padding: 8px 0;
            border-top: 1px solid #dde4eb;
            text-align: right;
        }
    }
</style>
