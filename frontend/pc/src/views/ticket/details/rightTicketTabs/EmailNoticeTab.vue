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
  <!-- 通知关注人 -->
  <div class="bk-log-flow">
    <bk-form
      :label-width="200"
      form-type="vertical">
      <bk-form-item
        :label="$t(`m.newCommon['收件人']`)"
        :required="true">
        <deal-person
          ref="personSelect"
          class="recipient-person"
          form-type="vertical"
          :value="personSelectCheckValue"
          :shortcut="true"
          :show-role-type-list="includeTypes"
          :required-msg="$t(`m.newCommon['请选择收件人']`)">
        </deal-person>
      </bk-form-item>
      <bk-form-item
        :label="$t(`m.newCommon['通知内容']`)"
        :required="true">
        <bk-input
          :placeholder="$t(`m.newCommon['请输入通知内容，长度不能超过200']`)"
          :type="'textarea'"
          :rows="3"
          :maxlength="200"
          v-model="followers.comments">
        </bk-input>
      </bk-form-item>
      <bk-form-item>
        <bk-button :theme="'primary'" class="mr10 mt10"
          :title="$t(`m.newCommon['发送']`)"
          :disabled="followers.clickSecond"
          @click="postFollowlogs">
          {{ $t('m.newCommon["发送"]') }}
        </bk-button>
      </bk-form-item>
    </bk-form>
    <template v-if="flowList.length && ticketInfo.can_invite_followers">
      <h3 class="setion-title">{{ $t('m.newCommon["发送历史"]') }}</h3>
    </template>
    <bk-timeline
      ext-cls="log-time-line"
      :list="flowList">
    </bk-timeline>
  </div>
</template>

<script>
  import DealPerson from '@/views/processManagement/processDesign/nodeConfigue/components/dealPerson';
  import { errorHandler } from '@/utils/errorHandler.js';

  export default {
    name: 'EmailNoticeTab',
    components: {
      DealPerson,
    },
    props: {
      ticketInfo: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        flowStartText: this.$t('m.newCommon["流程开始"]'),
        flowList: [],
        // 关注
        followers: {
          comments: '',
          clickSecond: false,
        },
        includeTypes: [],
        personSelectCheckValue: {
          type: 'PERSON',
          value: '',
        },
      };
    },
    created() {
      const includeTypes = ['GENERAL', 'PERSON'];
      if (this.ticketInfo.is_biz_need) {
        includeTypes.push('CMDB');
      }
      this.includeTypes = includeTypes;
    },
    mounted() {
      this.getflowList();
    },
    methods: {
      // 获取流转日志-关注人日志
      getflowList() {
        if (!this.id) {
          return;
        }
        const params = {
          ticket_id: this.id,
        };
        if (this.$route.query.token) {
          params.token = this.$route.query.token;
        }
        this.$store.dispatch('cdeploy/getfllowLog', params).then((res) => {
          this.flowList = [];
          if (res.data.length) {
            res.data.forEach((item) => {
              const line = {};
              // XXX 通知关注人 。。。
              line.content = `<div title="${item.group}" style="word-break: break-all;
                            display: -webkit-box;
                            -webkit-line-clamp: 2;
                            -webkit-box-orient: vertical;
                            overflow: hidden;">${item.creator_zh}${this.$t('m.newCommon["邮件通知："]')} ${item.group}</div>`;
              line.tag = item.create_at;
              if (item.message !== this.flowStartText) {
                this.flowList.push(line);
              }
            });
          }
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 发送关注到人
      postFollowlogs() {
        if (this.followers.clickSecond || !this.$refs.personSelect.verifyValue()) {
          return;
        }
        if (this.followers.comments.length > 200 || !this.followers.comments) {
          this.$bkMessage({
            message: this.$t('m.memberSelect["必填项且字数不能超过200"]'),
            theme: 'error',
          });
          return;
        }

        this.followers.clickSecond = true;
        const personSelectValue = this.$refs.personSelect.getValue();
        const params = {
          ticket_id: this.ticketInfo.id,
          state_name: this.ticketInfo.current_state_name,
          followers: personSelectValue.value,
          followers_type: personSelectValue.type,
          message: this.followers.comments,
        };
        this.$store.dispatch('cdeploy/postFollowlogs', { params }).then(() => {
          this.$bkMessage({
            message: this.$t('m.newCommon["发送成功"]'),
            theme: 'success',
          });
          this.clearFollowlogs();
          this.getflowList();
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.followers.clickSecond = false;
          });
      },
      // 清空关注信息
      clearFollowlogs() {
        // 关注
        this.followers = {
          comments: '',
          clickSecond: false,
        };
        this.personSelectCheckValue = {
          type: 'PERSON',
          value: '',
        };
      },
    },
  };
</script>
<style lang='scss' scoped>
.recipient-person {
    /deep/ .bk-form-width {
        width: 100%;
    }
}
.log-time-line {
    padding: 20px;
}
.setion-title {
    margin-top: 20px;
    padding-bottom: 13px;
    color: #313238;
    font-size: 14px;
    line-height: 20px;
    border-bottom: 1px solid #cacedb;
}
</style>
