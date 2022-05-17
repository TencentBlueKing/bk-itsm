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
  <!-- 满意度评价 -->
  <div class="bk-satisfact-info" v-bkloading="{ isLoading: loading }">
    <template
      v-if="!(ticketInfo.is_commented || ticketInfo.can_comment)"
      class="bk-satisfact-mask"
    >
      <p
        v-if="ticketInfo.current_status === 'REVOKED'"
        style="margin-bottom: 10px"
      >
        {{ $t('m.tickets["单据已撤销，无需评价。"]') }}
      </p>
      <p v-else style="margin-bottom: 10px">
        {{
          $t(
            'm.newCommon["单据处理未完成或没有评价权限，不能评价！"]'
          )
        }}
      </p>
    </template>
    <template v-else>
      <!-- 发送评价内容 -->
      <evaluation-ticket-content
        v-if="
          !satisfactInfo.stars &&
            !satisfactInfo.has_invited &&
            !loading
        "
        :satisfact-info="satisfactInfo"
        :ticket-info="ticketInfo"
        @submitSuccess="getEvaluation"
      >
      </evaluation-ticket-content>
      <!-- 已评价显示 -->
      <template v-else>
        <template v-if="satisfactInfo.stars">
          <div class="bk-evaluation-cus">
            <span class="bk-evaluation-label-cus">{{
              $t('m.newCommon["状态"]')
            }}</span>
            <span style="float: left">{{
              $t('m.newCommon["："]')
            }}</span>
            <pre class="bk-evaluation-content">{{
                            $t('m.newCommon["已评价"]')
            }}</pre>
          </div>
          <div class="bk-evaluation-cus">
            <div class="bk-evaluation-done">
              <span class="bk-evaluation-label-cus">{{
                $t('m.newCommon["星级"]')
              }}</span>
              <span style="float: left">{{
                $t('m.newCommon["："]')
              }}</span>
              <span class="label-new-content">
                <label
                  class="bk-form-radio"
                  v-for="(node, index) in scoreList"
                  :key="index"
                  style="padding: 0"
                >
                  <img
                    src="@/images/evaluate/starblank.svg"
                    alt="starfill"
                    v-if="index >= satisfactInfo.stars"
                    width="16px"
                  />
                  <img
                    src="@/images/evaluate/starfill.svg"
                    alt="starblank"
                    v-else
                    width="16px"
                  />
                </label>
                <span v-if="satisfactInfo.stars > 0">
                  {{
                    scoreList[satisfactInfo.stars - 1].name
                  }}
                </span>
              </span>
            </div>
          </div>
          <div class="bk-evaluation-cus">
            <span class="bk-evaluation-label-cus">{{
              $t('m.newCommon["评论"]')
            }}</span>
            <span style="float: left">{{
              $t('m.newCommon["："]')
            }}</span>
            <pre class="bk-evaluation-content">{{
                            satisfactInfo.comments ||
                            $t('m.newCommon["这个朋友很懒，什么也没留下"]')
            }}</pre>
          </div>
          <div class="bk-evaluation-cus">
            <span class="bk-evaluation-label-cus">{{
              $t('m.newCommon["评价人"]')
            }}</span>
            <span style="float: left">{{
              $t('m.newCommon["："]')
            }}</span>
            <span class="bk-evaluation-content">{{
              satisfactInfo.creator || "--"
            }}</span>
          </div>
          <div class="bk-evaluation-cus">
            <span class="bk-evaluation-label-cus">{{
              $t('m.newCommon["评价时间"]')
            }}</span>
            <span style="float: left">{{
              $t('m.newCommon["："]')
            }}</span>
            <span class="bk-evaluation-content">{{
              satisfactInfo.update_at || "--"
            }}</span>
          </div>
        </template>
        <template v-else>
          <div class="bk-satis-info" style="margin-top: 10px">
            <span>
              {{
                $t('m.newCommon["你已发送过满意度评价短信给"]')
              }}
              <span style="padding: 0 10px; color: #3c96ff">{{
                satisfactInfo.has_invited || "--"
              }}</span>
            </span>
          </div>
        </template>
      </template>
    </template>
  </div>
</template>

<script>
  import EvaluationTicketContent from '@/components/ticket/evaluation/EvaluationTicketContent.vue';
  import { errorHandler } from '@/utils/errorHandler.js';
  import { SCORE_LIST } from '@/constants/ticket';

  export default {
    name: 'CommentTab',
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
        loading: false,
        picked: 'One',
        satisfactInfo: {},
        scoreList: SCORE_LIST,
      };
    },
    mounted() {
      this.getEvaluation();
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
        await this.$store
          .dispatch('evaluation/getEvaluation', params)
          .then((res) => {
            this.satisfactInfo = res.data;
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.loading = false;
          });
      },
    },
  };
</script>
<style lang="scss" scoped>
/* 满意度 */
.bk-satisfact-info {
    position: relative;
    color: #737987;
    font-size: 14px;
    width: 100%;
    .bk-satisfact-mask {
        position: absolute;
        width: 100%;
        height: 100%;
        background: #dcdee5;
    }

    .bk-lable-info {
        width: 89px;
        font-weight: normal;
    }

    .bk-evaluation {
        line-height: 30px;

        .bk-eval-span {
            width: 74px;
            float: left;
        }

        .bk-eval-pre {
            width: calc(100% - 74px);
            float: left;
            overflow: hidden;
            text-overflow: ellipsis;
        }
    }

    .bk-evaluation-done {
        line-height: 30px;
        display: inline-flex;
        align-items: center;

        .label-new-content {
            display: inline-flex;
            justify-content: flex-start;
            align-items: center;
            margin-left: 5px;

            span {
                display: inline-block;
                height: 30px;
                line-height: 30px;
            }

            label {
                margin-right: 0px;
                padding: 0 7px 0 0;
                display: inline-flex;
                align-items: center;

                img {
                    width: 20px;
                }
            }
        }
    }
}
.bk-evaluation-cus {
    line-height: 30px;
    height: 30px;
    width: 100%;
    margin-top: 10px;

    .bk-evaluation-label-cus {
        width: 75px;
        margin-right: 5px;
        float: left;
        font-weight: bold;
    }

    .bk-evaluation-content {
        width: calc(100% - 100px);
        float: left;
        word-wrap: break-word;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-left: 5px;
    }
}
</style>
