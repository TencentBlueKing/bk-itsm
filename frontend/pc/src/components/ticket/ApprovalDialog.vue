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
  <bk-dialog
    render-directive="if"
    :width="635"
    :value="isShow"
    :mask-close="false"
    :auto-close="false"
    :title="$t(`m.manageCommon['审批']`)"
    :loading="approvalConfirmBtnLoading"
    @confirm="onApprovalConfirm"
    @cancel="onApprovalCancel">
    <bk-form ref="approvalForm" :model="formData" :rules="formRules">
      <bk-form-item :label="$t(`m.managePage['审批意见']`)" :label-width="140">
        <bk-radio-group v-if="approvalInfo.showAllOption"
          v-model="approvalInfo.result">
          <bk-radio :value="true" class="mr50">{{ $t(`m.managePage['通过']`) }}</bk-radio>
          <bk-radio :value="false">{{ $t(`m.manageCommon['拒绝']`) }}</bk-radio>
        </bk-radio-group>
        <span v-else
          :class="['result-tag', approvalInfo.result ? '' : 'reject']">
          {{ approvalInfo.result ? $t(`m.managePage['通过']`) : $t(`m.manageCommon['拒绝']`) }}
        </span>
      </bk-form-item>

      <bk-form-item :label="$t(`m.home['备注']`)" :label-width="140" :required="!approvalInfo.result" property="approvalNotice">
        <bk-input type="textarea" :row="4" :maxlength="200" v-model="formData.approvalNotice"></bk-input>
      </bk-form-item>
    </bk-form>
  </bk-dialog>
</template>

<script>
  import { errorHandler } from '../../utils/errorHandler';

  export default {
    name: 'ApprovalDialog',
    props: {
      isShow: {
        type: Boolean,
        default: false,
      },
      isBatch: Boolean,
      selectedList: Array,
      approvalInfo: {
        type: Object,
        default: () => ({
          result: true,
          showAllOption: false,
          approvalList: [],
        }),
      },
    },
    data() {
      return {
        approvalConfirmBtnLoading: false,
        formData: { approvalNotice: '' },
        formRules: {
          approvalNotice: [{
            validator: this.checkApprovalNotice,
            message: this.$t('m.systemConfig[\'备注\']') + this.$t('m.common["为必填项，请补充完善"]'),
            trigger: 'blur',

          }],
        },
      };
    },
    methods: {
      onApprovalConfirm() {
        this.approvalConfirmBtnLoading = true;
        this.$refs.approvalForm.validate().then(async (val) => {
          if (val) {
            const data = {
              result: this.approvalInfo.result.toString(),
              opinion: this.formData.approvalNotice,
              approval_list: this.approvalInfo.approvalList,
            };
            if (this.isBatch) {
              this.$emit('openApprovalMask', data.approval_list.length);
            } else {
              this.$emit('singleApproval', data.approval_list[0].ticket_id);
              this.$emit('cancel', !this.isBatch);
            }
            await this.$store.dispatch('workbench/batchApproval', data).then(res => {
              if (this.isBatch) {
                this.$emit('BatchApprovalPolling', data.approval_list.map(item => item.ticket_id).toString(), data.approval_list.length);
              } else {
                this.$emit('singleApproval', data.approval_list[0].ticket_id, res);
              }
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.formData.approvalNotice = '';
              });
          }
        })
          .finally(() => {
            this.approvalConfirmBtnLoading = false;
          });
      },
      onApprovalCancel() {
        this.formData.approvalNotice = '';
        this.approvalConfirmBtnLoading = false;
        this.$emit('cancel');
      },
      checkApprovalNotice(val) {
        if (!this.approvalInfo.result) {
          return val !== '';
        }
        return true;
      },
    },
  };
</script>
<style lang='scss' scoped>
.result-tag {
    display: inline-block;
    padding: 5px 10px;
    line-height: 1;
    color: #2dcb56;
    border: 1px solid #2dcb56;
    background: #dcffe2;
    font-size: 14px;
    font-weight: bold;
    border-radius: 2px;
    &.reject {
        color: #ff5656;
        border-color: #ff5656;
        background: #fedddc;
    }
}
</style>
