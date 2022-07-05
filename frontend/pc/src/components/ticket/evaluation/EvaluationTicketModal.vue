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
  <bk-dialog v-model="isShow"
    width="650"
    theme="primary"
    header-position="left"
    :mask-close="false"
    :title="$t(`m.newCommon['满意度评价']`)">
    <!-- 发送评价内容 -->
    <div class="evaluation-wrap" v-bkloading="{ isLoading: loading }">
      <evaluation-ticket-content
        v-if="!satisfactInfo.stars && !satisfactInfo.has_invited && !loading"
        ref="evaluationContent"
        :satisfact-info="satisfactInfo"
        :ticket-info="ticketInfo"
        :is-show-submit-btn="false"
        @beforeSubmit="onBeforeSubmit"
        @submitSuccess="onSubmitSuccess">
      </evaluation-ticket-content>
    </div>
    <div slot="footer">
      <bk-button
        theme="primary"
        :loading="submitting"
        @click="onModelSubmitBtnClick">
        {{ $t('m.newCommon["提交"]') }}
      </bk-button>
      <bk-button
        theme="default"
        @click="isShow = false">
        {{ $t('m.newCommon["取消"]') }}
      </bk-button>
    </div>
  </bk-dialog>
</template>

<script>
  import EvaluationTicketContent from './EvaluationTicketContent.vue';
  import { errorHandler } from '../../../utils/errorHandler';

  export default {
    name: 'EvaluationTicketModal',
    components: {
      EvaluationTicketContent,
    },
    props: {
      ticketInfo: {
        type: Object,
        default: () => ({}),
      },
    },
    data() {
      return {
        submitting: false,
        loading: false,
        isShow: false,
        satisfactInfo: {},
      };
    },
    watch: {
      isShow(val) {
        if (val) {
          this.getEvaluation();
        }
      },
    },
    methods: {
      // 获取评论
      async getEvaluation() {
        this.loading = true;
        const params = {
          id: this.ticketInfo.comment_id,
        };
        if (this.$route.query.token) {
          params.token = this.$route.query.token;
        }
        await this.$store.dispatch('evaluation/getEvaluation', params).then((res) => {
          this.satisfactInfo = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.loading = false;
          });
      },
      show() {
        this.isShow = true;
      },
      onModelSubmitBtnClick() {
        this.$refs.evaluationContent.onSubmit();
        return false;
      },
      onSubmitSuccess() {
        this.isShow = false;
        this.submitting = false;
        this.$emit('submitSuccess');
      },
      onBeforeSubmit() {
        this.submitting = true;
      },
    },
  };
</script>
<style lang='scss' scoped>
.evaluation-wrap {
    width: 100%;
    height: 305px;
}
</style>
