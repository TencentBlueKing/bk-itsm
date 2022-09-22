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
  <div class="bk-dialog-form bk-dialog-up">
    <bk-dialog
      v-model="dialogSetting.isShow"
      :render-directive="'if'"
      :title="dialogSetting.title"
      :width="dialogSetting.width"
      :header-position="dialogSetting.headerPosition"
      :loading="secondClick"
      :auto-close="dialogSetting.autoClose"
      :mask-close="dialogSetting.autoClose"
      @confirm="submitValidate"
      @cancel="cancelForm"
    >
      <bk-form
        :label-width="200"
        form-type="vertical"
        :model="formInfo"
        ref="ticketForm"
        :rules="rules"
      >
        <template v-if="ticketOperateType === 'suspend'">
          <bk-form-item
            :label="$t(`m.newCommon['挂起原因']`)"
            :desc="
              $t(
                `m.slaContent['挂起后单据流程将停止运行，且不计入SLA时长']`
              )
            "
            :required="true"
            :property="'suspend_message'"
          >
            <bk-input
              :placeholder="$t(`m.newCommon['请输入挂起原因']`)"
              :type="'textarea'"
              :rows="3"
              v-model="formInfo.suspend_message"
            >
            </bk-input>
          </bk-form-item>
        </template>
        <template v-if="ticketOperateType === 'close'">
          <!-- <bk-form-item
            :label="$t(`m.newCommon['关闭状态']`)"
            :required="true"
            :property="'closeState'"
          >
            <bk-select
              v-model="formInfo.closeState"
              searchable
              :font-size="'medium'"
              :clearable="falseStatus"
            >
              <bk-option
                v-for="option in endList"
                :key="option.key"
                :id="option.key"
                :name="option.name"
              >
              </bk-option>
            </bk-select>
          </bk-form-item> -->
          <bk-form-item
            :label="$t(`m.newCommon['关闭原因']`)"
            :required="true"
            :property="'close_message'"
          >
            <bk-input
              :placeholder="$t(`m.newCommon['请输入关闭原因']`)"
              :type="'textarea'"
              :rows="3"
              v-model="formInfo.close_message"
            >
            </bk-input>
          </bk-form-item>
        </template>
      </bk-form>
    </bk-dialog>
  </div>
</template>

<script>
  import commonMix from '@/views/commonMix/common.js';
  import { errorHandler } from '@/utils/errorHandler.js';

  export default {
    name: 'StepSubmitDialog',
    mixins: [commonMix],
    props: {
      ticketInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      ticketOperateType: {
        type: String,
        default: 'close',
      },
    },
    data() {
      return {
        secondClick: false,
        falseStatus: false,
        dialogSetting: {
          isAdd: true,
          isShow: false,
          width: 700,
          headerPosition: 'left',
          autoClose: false,
          precision: 0,
          content: '',
          title: '',
        },
        formInfo: {
          suspend_message: '',
          closeState: 'TERMINATED', // 关单初始值 ‘已终止’
          close_message: '',
        },
        endList: [],
        isDataLoading: false,
        checkInfo: {
          suspendFlag: false,
          closeFlag: false,
          closeReasonFlag: false,
        },
        rules: {},
      };
    },
    mounted() {
      this.rules.suspend_message = this.checkCommonRules('select').select;
      this.rules.closeState = this.checkCommonRules('select').select;
      this.rules.close_message = this.checkCommonRules('select').select;
    },
    methods: {
      openCel() {
        if (this.ticketOperateType === 'close') {
          this.dialogSetting.title = this.$t('m.newCommon["关单"]');
        } else if (this.ticketOperateType === 'suspend') {
          this.dialogSetting.title = this.$t('m.newCommon["挂起"]');
        } else {
          this.dialogSetting.title = this.$t('m.newCommon["是否恢复此单据？"]');
          this.dialogSetting.content =                    this.$t('m.newCommon["单据将恢复至【"]')
            + this.ticketInfo.pre_status_display
            + this.$t('m.newCommon["】"]');
          this.$bkInfo({
            type: 'warning',
            title: this.dialogSetting.title,
            subTitle: this.dialogSetting.content,
            confirmFn: () => {
              this.submitRestore();
            },
          });
        }
        if (
          this.ticketOperateType === 'close'
          || this.ticketOperateType === 'suspend'
        ) {
          this.dialogSetting.isShow = true;
          this.$nextTick(() => {
            this.getTypeStatus();
          });
        }
      },
      getTypeStatus() {
        if (this.ticketOperateType !== 'close') {
          return;
        }
        this.isDataLoading = true;
        const type = this.ticketInfo.service_type;
        const key = this.ticketInfo.current_status;
        this.$store
          .dispatch('deployOrder/getEndStatus', { type, key })
          .then((res) => {
            // 所有的关单都属于外力中途异常介入
            this.endList = res.data.filter(item => item.key === 'TERMINATED');
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
      },
      initFormInfo() {
        this.formInfo.suspend_message = '';
        this.formInfo.closeState = '';
        this.formInfo.close_message = '';
      },
      submitValidate() {
        this.$refs.ticketForm.validate().then(
          () => {
            this.submitForm();
          },
          (validator) => {
            console.warn(validator);
          }
        );
      },
      submitForm() {
        if (this.ticketOperateType === 'close') {
          const params = {
            current_status: this.formInfo.closeState,
            desc: this.formInfo.close_message,
          };
          const { id } = this.ticketInfo;
          this.$store
            .dispatch('deployOrder/closeTickets', { id, params })
            .then(() => {
              this.$bkMessage({
                message: this.$t('m.newCommon["关单成功"]'),
                theme: 'success',
              });
            })
            .catch((res) => {
              errorHandler(res, this);
            })
            .finally(() => {
              this.dialogSetting.isShow = false;
              this.endList.splice(0, this.endList.length);
              this.initFormInfo();
              this.$emit('submitSuccess');
            });
        } else if (this.ticketOperateType === 'suspend') {
          const params = {
            desc: this.formInfo.suspend_message,
          };
          const { id } = this.ticketInfo;
          this.$store
            .dispatch('deployOrder/suspendTickets', { id, params })
            .then(() => {
              this.$bkMessage({
                message: this.$t('m.newCommon["挂起成功"]'),
                theme: 'success',
              });
            })
            .catch((res) => {
              errorHandler(res, this);
            })
            .finally(() => {
              this.dialogSetting.isShow = false;
              this.initFormInfo();
              this.$emit('submitSuccess');
            });
        } else if (this.ticketOperateType === 'restore') {
          this.submitRestore();
        }
      },
      cancelForm() {
        this.dialogSetting.isShow = false;
      },
      submitRestore() {
        const { id } = this.ticketInfo;
        this.$store
          .dispatch('deployOrder/restoreTickets', id)
          .then(() => {
            this.$bkMessage({
              message: this.$t('m.newCommon["恢复成功"]'),
              theme: 'success',
            });
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.initFormInfo();
            this.$emit('submitSuccess');
          });
      },
    },
  };
</script>

<style scoped lang="scss"></style>
