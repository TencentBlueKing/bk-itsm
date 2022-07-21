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
  <div class="bk-editor-notice">
    <bk-form
      :label-width="150"
      :model="formInfo"
      form-type="vertical"
      ref="wechatForm"
      :rules="rules"
      :key="checkId">
      <template v-if="checkId === 'WEIXIN'">
        <bk-form-item
          v-if="isShowTitle"
          :label="$t(`m.slaContent['标题']`)"
          :required="true"
          :property="'title'"
          :icon-offset="240">
          <bk-input
            type="text"
            :ext-cls="'bk-remindway-form'"
            v-model="formInfo.title">
          </bk-input>
          <div class="bk-select-btn">
            <bk-button
              theme="default"
              :title="$t(`m.slaContent['插入变量']`)"
              class="bk-form-btn plus-cus"
              icon="plus">
              {{ $t('m.slaContent["插入变量"]') }}
            </bk-button>
            <bk-select v-model="insertVariable.titleId"
              ext-cls="bk-select-btn-opacity"
              searchable
              :font-size="'medium'"
              @selected="changeInsert(...arguments,'title')">
              <bk-option v-for="option in variableList"
                :key="option.key"
                :id="option.key"
                :name="option.name">
              </bk-option>
            </bk-select>
          </div>
        </bk-form-item>
        <bk-form-item
          :label="$t(`m.slaContent['提醒内容']`)"
          :required="true"
          :property="'message'"
          :icon-offset="240">
          <bk-input type="textarea"
            v-cursorIndex="'editorNotice'"
            :ext-cls="'bk-remindway-form'"
            :rows="customRow || 5"
            v-model="formInfo.message">
          </bk-input>
          <div class="bk-select-btn">
            <bk-button
              theme="default"
              :title="$t(`m.slaContent['插入变量']`)"
              class="bk-form-btn plus-cus"
              icon="plus">
              {{ $t('m.slaContent["插入变量"]') }}
            </bk-button>
            <bk-select v-model="insertVariable.id"
              ext-cls="bk-select-btn-opacity"
              searchable
              :font-size="'medium'"
              @selected="changeInsert(...arguments,'message')">
              <bk-option v-for="option in variableList"
                :key="option.key"
                :id="option.key"
                :name="option.name">
              </bk-option>
            </bk-select>
          </div>
        </bk-form-item>
      </template>
      <template v-else-if="checkId === 'EMAIL'">
        <bk-form-item
          :label="$t(`m.slaContent['标题']`)"
          :required="true"
          :property="'title'"
          :icon-offset="240">
          <bk-input
            type="text"
            :ext-cls="'bk-remindway-form'"
            v-model="formInfo.title">
          </bk-input>
          <div class="bk-select-btn">
            <bk-button
              theme="default"
              :title="$t(`m.slaContent['插入变量']`)"
              class="bk-form-btn plus-cus"
              icon="plus">
              {{ $t('m.slaContent["插入变量"]') }}
            </bk-button>
            <bk-select v-model="insertVariable.titleId"
              ext-cls="bk-select-btn-opacity"
              searchable
              :font-size="'medium'"
              @selected="changeInsert(...arguments,'title')">
              <bk-option v-for="option in variableList"
                :key="option.key"
                :id="option.key"
                :name="option.name">
              </bk-option>
            </bk-select>
          </div>
        </bk-form-item>
        <bk-form-item
          :label="$t(`m.slaContent['邮件内容']`)"
          :required="true"
          :property="'message'"
          :icon-offset="240">
          <bk-input type="textarea"
            v-cursorIndex="'editorNotice'"
            :ext-cls="'bk-remindway-form'"
            :rows="customRow || 22"
            v-model="formInfo.message">
          </bk-input>
          <div class="bk-select-btn">
            <bk-button
              theme="default"
              :title="$t(`m.slaContent['插入变量']`)"
              class="bk-form-btn plus-cus"
              icon="plus">
              {{ $t('m.slaContent["插入变量"]') }}
            </bk-button>
            <bk-select v-model="insertVariable.id"
              ext-cls="bk-select-btn-opacity"
              searchable
              :font-size="'medium'"
              @selected="changeInsert(...arguments,'message')">
              <bk-option v-for="option in variableList"
                :key="option.key"
                :id="option.key"
                :name="option.name">
              </bk-option>
            </bk-select>
          </div>
        </bk-form-item>
      </template>
      <template v-else-if="checkId === 'SMS'">
        <bk-form-item
          v-if="isShowTitle"
          :label="$t(`m.slaContent['标题']`)"
          :required="true"
          :property="'title'"
          :icon-offset="240">
          <bk-input
            type="text"
            :ext-cls="'bk-remindway-form'"
            v-model="formInfo.title">
          </bk-input>
          <div class="bk-select-btn">
            <bk-button
              theme="default"
              :title="$t(`m.slaContent['插入变量']`)"
              class="bk-form-btn plus-cus"
              icon="plus">
              {{ $t('m.slaContent["插入变量"]') }}
            </bk-button>
            <bk-select v-model="insertVariable.titleId"
              ext-cls="bk-select-btn-opacity"
              searchable
              :font-size="'medium'"
              @selected="changeInsert(...arguments,'title')">
              <bk-option v-for="option in variableList"
                :key="option.key"
                :id="option.key"
                :name="option.name">
              </bk-option>
            </bk-select>
          </div>
        </bk-form-item>
        <bk-form-item
          :label="$t(`m.slaContent['短信内容']`)"
          :required="true"
          :property="'message'"
          :icon-offset="240">
          <bk-input type="textarea"
            v-cursorIndex="'editorNotice'"
            :ext-cls="'bk-remindway-form'"
            :rows="customRow || 15"
            v-model="formInfo.message">
          </bk-input>
          <div class="bk-select-btn">
            <bk-button
              theme="default"
              :title="$t(`m.slaContent['插入变量']`)"
              class="bk-form-btn plus-cus"
              icon="plus">
              {{ $t('m.slaContent["插入变量"]') }}
            </bk-button>
            <bk-select v-model="insertVariable.id"
              ext-cls="bk-select-btn-opacity"
              searchable
              :font-size="'medium'"
              @selected="changeInsert(...arguments,'message')">
              <bk-option v-for="option in variableList"
                :key="option.key"
                :id="option.key"
                :name="option.name">
              </bk-option>
            </bk-select>
          </div>
        </bk-form-item>
      </template>
      <template v-else>
        <bk-form-item
          v-if="isShowTitle"
          :label="$t(`m.slaContent['标题']`)"
          :required="true"
          :property="'title'"
          :icon-offset="240">
          <bk-input
            type="text"
            :ext-cls="'bk-remindway-form'"
            v-model="formInfo.title">
          </bk-input>
          <div class="bk-select-btn">
            <bk-button
              theme="default"
              :title="$t(`m.slaContent['插入变量']`)"
              class="bk-form-btn plus-cus"
              icon="plus">
              {{ $t('m.slaContent["插入变量"]') }}
            </bk-button>
            <bk-select v-model="insertVariable.titleId"
              ext-cls="bk-select-btn-opacity"
              searchable
              :font-size="'medium'"
              @selected="changeInsert(...arguments,'title')">
              <bk-option v-for="option in variableList"
                :key="option.key"
                :id="option.key"
                :name="option.name">
              </bk-option>
            </bk-select>
          </div>
        </bk-form-item>
        <bk-form-item
          :label="$t(`m['内容']`)"
          :required="true"
          :property="'message'"
          :icon-offset="240">
          <bk-input type="textarea"
            v-cursorIndex="'editorNotice'"
            :ext-cls="'bk-remindway-form'"
            :rows="customRow || 15"
            v-model="formInfo.message">
          </bk-input>
          <div class="bk-select-btn">
            <bk-button
              theme="default"
              :title="$t(`m.slaContent['插入变量']`)"
              class="bk-form-btn plus-cus"
              icon="plus">
              {{ $t('m.slaContent["插入变量"]') }}
            </bk-button>
            <bk-select v-model="insertVariable.id"
              ext-cls="bk-select-btn-opacity"
              searchable
              :font-size="'medium'"
              @selected="changeInsert(...arguments,'message')">
              <bk-option v-for="option in variableList"
                :key="option.key"
                :id="option.key"
                :name="option.name">
              </bk-option>
            </bk-select>
          </div>
        </bk-form-item>
      </template>
    </bk-form>
    <div v-if="isShowFooter" class="bk-add-btn">
      <bk-button
        v-cursor="{ active: !hasPermission(['ticket_state_manage']) }"
        theme="primary"
        :class="{
          'btn-permission-disable': !hasPermission(['ticket_state_manage'])
        }"
        :title="$t(`m.serviceConfig['确认']`)"
        :loading="secondClick"
        @click="submitNotice">
        {{ $t('m.serviceConfig["确认"]') }}
      </bk-button>
      <bk-button
        theme="default"
        :title="$t(`m.serviceConfig['取消']`)"
        :loading="secondClick"
        @click="closeNotice">
        {{ $t('m.serviceConfig["取消"]') }}
      </bk-button>
    </div>
  </div>
</template>

<script>
  import commonMix from '../../commonMix/common.js';
  import insertText from '@/utils/insertText.js';
  import { errorHandler } from '../../../utils/errorHandler.js';
  import permission from '@/mixins/permission.js';

  export default {
    name: 'editorNotice',
    mixins: [commonMix, permission],
    props: {
      checkId: {
        type: String,
        default: '',
      },
      noticeInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      isShowFooter: {
        type: Boolean,
        default: true,
      },
      isShowTitle: {
        type: Boolean,
        default: false,
      },
      customRow: Number,
    },
    data() {
      return {
        secondClick: false,
        formInfo: {
          title: '',
          message: '',
        },
        variableList: [],
        searchable: true,
        insertVariable: {
          id: '',
          content: {},
          titleId: '',
          titleContent: {},
        },
        // 校验
        checkInfo: {
          title: false,
          message: false,
        },
        rules: {},
      };
    },
    mounted() {
      this.initData();
      this.rules.message = this.checkCommonRules('select').select;
      this.rules.title = this.checkCommonRules('select').select;
    },
    methods: {
      initData() {
        this.formInfo.title = this.noticeInfo.title_template;
        this.formInfo.message = this.noticeInfo.content_template;
        this.getVariableList();
      },
      // 获取变量数据
      getVariableList() {
        this.$store.dispatch('noticeConfigure/getVariableList').then((res) => {
          this.variableList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 保存
      submitNotice() {
        if (!this.hasPermission(['ticket_state_manage'])) {
          this.applyForPermission(['ticket_state_manage'], this.$store.state.project.projectAuthActions, {});
          return;
        }
        this.$refs.wechatForm.validate().then(() => {}, () => {});
        if (this.checkNotice()) {
          return;
        }
        const params = {
          content_template: this.formInfo.message,
        };
        if (this.checkId === 'EMAIL') {
          params.title_template = this.formInfo.title;
        }
        const id = this.noticeInfo.id;
        if (this.secondClick) {
          return;
        }
        this.secondClick = true;
        this.$store.dispatch('noticeConfigure/changeNotice', { params, id }).then(() => {
          this.$bkMessage({
            message: this.$t('m.deployPage["保存成功"]'),
            theme: 'success',
          });
          this.$parent.$parent.getNoticeList();
          this.closeNotice();
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.secondClick = false;
          });
      },
      closeNotice() {
        this.$emit('closeEditor');
      },
      checkNotice() {
        this.checkInfo.title = !this.formInfo.title;
        this.checkInfo.message = !this.formInfo.message;
        return (this.checkInfo.title || this.checkInfo.message);
      },
      changeInsert(...value) {
        if (value[2] === 'message') {
          this.formInfo.message = insertText(
            document.querySelector('.bk-editor-notice .bk-remindway-form .bk-form-textarea'),
            'editorNotice',
            this.formInfo.message,
            `\${${value[0]}}`,
            this
          );
        } else {
          this.formInfo.title += `\${${value[0]}}`;
        }
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../scss/mixins/clearfix.scss';
    @import '../../../scss/mixins/scroller.scss';

    .bk-editor-notice {
        .bk-form-content {
            @include clearfix;
        }
        .bk-form-textarea,
        .bk-form-input {
            float: left;
            width: 485px;
            margin-right: 10px;
        }
        .bk-form-textarea {
            height: 94px;
        }
        .bk-form-btn {
            line-height: 32px;
            padding: 0 10px;
            float: left;
        }
    }
    .bk-remindway-form {
        float: left;
        width: 400px;
        margin-right: 10px;
    }
    .bk-select-btn {
        float: left;
        position: relative;
        width: 200px;
        .bk-select-btn-opacity {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            opacity: 0;
        }
    }
    .bk-form-textarea {
        padding: 0 10px;
        line-height: 25px!important;
        min-height: 400px;
        resize: vertical;
    }
</style>
