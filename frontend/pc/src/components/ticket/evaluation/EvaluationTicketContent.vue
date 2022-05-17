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
  <div class="evaluation-content">
    <p style="margin-bottom: 10px">
      {{$t('m.newCommon["单据已经处理完成，请对整体单据处理进行评价"]')}}</p>
    <div class="mb20">
      <bk-radio-group v-model="picked">
        <bk-radio :value="'One'" class="mr20">{{ $t('m.newCommon["直接评价"]') }}</bk-radio>
        <bk-radio :value="'Two'" class="mr20" v-if="isShowSMSComment">
          {{ $t('m.newCommon["短信评价"]') }}
        </bk-radio>
        <bk-radio :value="'Three'">{{ $t('m.newCommon["邮件评价"]') }}</bk-radio>
      </bk-radio-group>
    </div>
    <!-- 直接评价 -->
    <template v-if="picked === 'One'">
      <bk-form
        :label-width="200"
        form-type="vertical"
        :model="scoreInfo"
        ref="scoreForm">
        <bk-form-item
          :label="$t(`m.newCommon['评分：']`)"
          :required="true">
          <bk-rate :width="18"
            :height="18"
            :rate="scoreInfo.startInfo"
            :edit="true"
            @score="chooseRate">
          </bk-rate>
          <template v-if="scoreInfo.startInfo">
            {{ scoreInfo.scoreList[scoreInfo.startInfo - 1].name }}
          </template>
        </bk-form-item>
        <bk-form-item
          :label="$t(`m.newCommon['意见：']`)">
          <bk-input
            :placeholder="$t(`m.newCommon['请填写你的意见']`)"
            :type="'textarea'"
            :rows="3"
            v-model="scoreInfo.comments">
          </bk-input>
        </bk-form-item>
      </bk-form>
    </template>
    <!-- 短信评价 -->
    <template v-if="picked === 'Two'">
      <bk-form
        :label-width="200"
        form-type="vertical"
        :model="scoreInfo"
        ref="telephoneForm">
        <bk-form-item
          :label="$t(`m.newCommon['手机号码：']`)"
          :required="true">
          <bk-input :clearable="true"
            v-model="scoreInfo.telephone"
            :disabled="!!satisfactInfo.has_invited"
            :placeholder="$t(`m.newCommon['请输入，多个用英文逗号分隔']`)">
          </bk-input>
          <div style="margin-top: 4px;position: relative;">
            <span v-if="!satisfactInfo.has_invited" style="color: #979BA5">
              {{ $t('m.newCommon["提交后系统会发送信息至需求方进行满意度评价"]') }}</span>
            <span v-else style="color: #979BA5">
              {{ $t('m.newCommon["你已发送过满意度评价短信给"]') }}
              <span style="padding: 0 10px; color: #3c96ff;">{{satisfactInfo.has_invited}}</span>{{ $t('m.newCommon["的用户"]') }}
            </span>
          </div>
        </bk-form-item>
      </bk-form>
    </template>
    <!-- 邮件评价 -->
    <template v-if="picked === 'Three'">
      <bk-form
        :label-width="200"
        form-type="vertical"
        :model="scoreInfo"
        ref="emailForm">
        <bk-form-item
          :label="$t(`m.newCommon['接收人：']`)"
          :required="true">
          <member-select
            v-model="scoreInfo.emailTempInfo.val"
            class="member-select"
            :placeholder="$t(`m.newCommon['请输入蓝鲸用户']`)">
          </member-select>
          <business-card
            v-if="scoreInfo.emailTempInfo.val.length"
            class="bk-email-card"
            :item="{
              val: scoreInfo.emailTempInfo.val.join(',')
            }">
          </business-card>
        </bk-form-item>
      </bk-form>
      <div style="margin-top: 4px;position: relative;">
        <span v-if="!satisfactInfo.has_invited" style="color: #979BA5">{{$t('m.newCommon["提交后系统会发送邮件到接收人邮箱"]')}}</span>
        <span v-else style="color: #979BA5">{{$t('m.newCommon["你已发送过满意度评价邮件给"]')}}
          <span style="padding: 0 10px; color: #3c96ff;">{{satisfactInfo.has_invited}}</span>{{ $t('m.newCommon["的用户"]') }}
        </span>
      </div>
    </template>
    <bk-button v-if="isShowSubmitBtn"
      class="mr10 mt20"
      :theme="'primary'"
      :title="submitBtnInfo.name"
      :disabled="submitBtnInfo.disabled"
      @click="onSubmit">
      {{ submitBtnInfo.name }}
    </bk-button>
  </div>
</template>

<script>
  import businessCard from '@/components/common/BusinessCard.vue';
  import memberSelect from '@/views/commonComponent/memberSelect/index.vue';
  import { SCORE_LIST } from '@/constants/ticket';
  import { errorHandler } from '../../../utils/errorHandler';

  export default {
    name: 'EvaluationTicketContent',
    components: {
      memberSelect,
      businessCard,
    },
    props: {
      satisfactInfo: {
        type: Object,
        default: () => ({}),
      },
      ticketInfo: {
        type: Object,
        default: () => ({}),
      },
      isShowSubmitBtn: {
        type: Boolean,
        default: true,
      },
    },
    data() {
      return {
        picked: 'One',
        // 评价
        scoreInfo: {
          // TODO: 临时解决方案
          scoreList: SCORE_LIST,
          comments: '',
          startInfo: 0,
          clickSecond: false,
          telephone: '',
          email: '',
          // 用于member组件临时使用
          emailTempInfo: {
            val: [],
            showFeild: true,
            desc: this.$t('m.newCommon["请输入蓝鲸用户"]'),
            evaluDisable: false,
          },
          teleCheck: false,
          title: '',
          content: '',
          inviteType: '',
        },
      };
    },
    computed: {
      submitBtnInfo() {
        if (this.picked === 'One') {
          return {
            name: this.$t('m.newCommon["提交"]'),
            disabled: this.scoreInfo.clickSecond,
          };
        }
        return {
          name: this.$t('m.newCommon["发送"]'),
          disabled: this.scoreInfo.clickSecond || !!this.satisfactInfo.has_invited,
        };
      },
      // 是否展示短信评论
      isShowSMSComment() {
        return this.$store.state.openFunction.SMS_COMMENT_SWITCH && window.run_site !== 'bmw';
      },
    },
    methods: {
      // 提交
      onSubmit() {
        if (this.picked === 'One') {
          this.postEvaluation();
        } else if (this.picked === 'Two') {
          this.openSendPhone();
        } else {
          this.openSendEmail();
        }
      },
      // 选择评价分数
      chooseRate(val) {
        this.scoreInfo.startInfo = val;
      },
      // 提交满意度评价
      postEvaluation() {
        if (this.scoreInfo.clickSecond) {
          return;
        }
        this.scoreInfo.clickSecond = true;
        const params = {
          ticket: this.ticketInfo.id,
          stars: this.scoreInfo.startInfo,
          comments: this.scoreInfo.comments,
          source: 'WEB',
          creator: window.username,
        };

        if (!this.scoreInfo.startInfo) {
          this.$bkMessage({
            message: this.$t('m.newCommon["请进行评分"]'),
            theme: 'error',
          });
          this.scoreInfo.clickSecond = false;
          return;
        }
        const id = this.ticketInfo.comment_id;

        this.$emit('beforeSubmit');
        this.$store.dispatch('evaluation/postEvaluation', { params, id }).then(() => {
          this.$bkMessage({
            message: this.$t('m.newCommon["评价成功"]'),
            theme: 'success',
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.$emit('submitSuccess');
            this.scoreInfo.clickSecond = false;
          });
      },
      openSendPhone() {
        if (this.scoreInfo.teleCheck || !this.scoreInfo.telephone) {
          this.$bkMessage({
            message: this.$t('m.newCommon["请输入正确的手机号"]'),
            theme: 'error',
          });
          return;
        }
        this.scoreInfo.title = this.$t('m.newCommon["确认发送此短信？"]');
        this.scoreInfo.content = this.$t('m.newCommon["发送一次以后不能再进行发送操作，请谨慎操作"]');
        this.scoreInfo.inviteType = 'mobile';
        this.$bkInfo({
          type: 'warning',
          title: this.scoreInfo.title,
          subTitle: this.scoreInfo.content,
          confirmFn: () => {
            this.sendTelephone();
          },
        });
      },
      openSendEmail() {
        if (this.checkEmail()) {
          this.$bkMessage({
            message: this.$t('m.newCommon["未找到当前用户邮箱信息或发送失败"]'),
            theme: 'error',
          });
          return;
        }
        this.scoreInfo.title = this.$t('m.newCommon["确认发送此邮件？"]');
        this.scoreInfo.content = this.$t('m.newCommon["发送一次以后不能再进行发送操作，请谨慎操作"]');
        this.scoreInfo.inviteType = 'email';
        this.$bkInfo({
          type: 'warning',
          title: this.scoreInfo.title,
          subTitle: this.scoreInfo.content,
          confirmFn: () => {
            this.sendTelephone();
          },
        });
      },
      checkEmail() {
        if (!this.scoreInfo.emailTempInfo.val.length) {
          return true;
        }
        const params = {
          users: this.scoreInfo.emailTempInfo.val.join(','),
          properties: 'all',
        };
        this.$store.dispatch('getPersonInfo', params).then(res => !res.data[0].email)
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 邀请评价
      // 校验电话规则
      checkTelephone() {
        const res = /^1[34578]\d{9}$/;
        const val = this.scoreInfo.telephone.trim().split(',');
        const result = val.some(item => !res.test(item));
        this.scoreInfo.teleCheck = result;
      },
      sendTelephone() {
        if (this.scoreInfo.clickSecond) {
          return;
        }
        this.scoreInfo.clickSecond = true;
        let url = '';
        const params = {};
        let id = '';
        if (this.scoreInfo.inviteType === 'mobile') {
          url = 'evaluation/sendTelephone';
          params.receiver = this.scoreInfo.telephone;
          params.comment_id = this.ticketInfo.comment_id;
          id = this.ticketInfo.id;
        } else {
          url = 'evaluation/sendEmail';
          params.receiver = this.scoreInfo.emailTempInfo.val.join(',');
          id = this.ticketInfo.id;
        }

        this.$emit('beforeSubmit');
        this.$store.dispatch(url, { params, id }).then(() => {
          this.$bkMessage({
            message: this.$t('m.newCommon["发送成功"]'),
            theme: 'success',
          });
          this.$emit('submitSuccess');
        })
          .catch(() => {
            errorHandler(this);
          })
          .finally(() => {
            this.scoreInfo.clickSecond = false;
          });
      },
    },
  };
</script>
<style lang='scss' scoped>
.evaluation-content {
    color: #737987;
    font-size: 14px;
    .member-select {
        display: inline-block;
        width: calc(100% - 30px);
    }
    .bk-email-card {
        display: inline-block;
        vertical-align: top;
    }
}
</style>
