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
  <div class="log-list" v-bkloading="{ isLoading: loading }">
    <div class="ticket-process-content" :style="!isShowSla ? 'height: calc(100vh - 430px);' : 'height: calc(100vh - 310px);'">
      <div class="ticket-process">
        <i class="bk-itsm-icon icon-basic-info" @click="viewProcess"> {{ $t(`m["查看完整流程"]`) }}</i>
      </div>
      <bk-timeline
        data-test-id="ticket_timeline_viewLog"
        ext-cls="log-time-line"
        :list="list"
        @select="handleSelect"></bk-timeline>
      <div v-if="isShowComment" class="process-detail">
        <div class="process-content">
          <img :src="imgUrl" alt="单据结束" />
          <template v-if="!ticketInfo.is_commented && ticketInfo.comment_id !== '-1'">
            <p>{{ $t(`m["当前流程已结束，快去评价吧"]`) }}</p>
            <span class="appraise" @click="$emit('ticketFinishAppraise')">{{ $t(`m["去评价"]`) }}</span>
          </template>
          <div v-else>
            {{ $t(`m["已完成评价"]`) }}
            <div class="comment-content">
              <div class="comment-content-item">
                <span>{{ $t(`m["星级"]`) }}:</span>
                <bk-rate style="margin-top: 3px" :rate="commentInfo.stars" :edit="false"></bk-rate>
              </div>
              <div class="comment-content-item">
                <span>{{ $t(`m["评价人"]`) }}:</span>
                <p>{{ commentInfo.creator || "--" }}</p>
              </div>
              <div class="comment-content-item">
                <span>{{ $t(`m["评价时间"]`) }}:</span>
                <p>{{ commentInfo.create_at || "--" }}</p>
              </div>
              <div class="comment-content-item">
                <span>{{ $t(`m["评价内容"]`) }}:</span>
                <p>{{ commentInfo.comments || $t('m.newCommon["这个朋友很懒，什么也没留下"]') }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- 操作日志详情 sideslider -->
    <ticket-log-detail
      :log-info.sync="dispalyLogInfo"
      :show="!!dispalyLogInfo"
      @close="
        () => {
          dispalyLogInfo = null;
        }
      ">
    </ticket-log-detail>
  </div>
</template>

<script>
  import ticketLogDetail from './logInfo/ticketLogDetail';
  import { errorHandler } from '@/utils/errorHandler';
  import fieldMix from '@/views/commonMix/field.js';
  import { mapState } from 'vuex';
  import i18n from '@/i18n/index.js';

  export default {
    name: 'LogTab',
    components: {
      ticketLogDetail,
    },
    mixins: [fieldMix],
    props: {
      ticketInfo: Object,
      isShowSla: Boolean,
    },
    data() {
      return {
        dispalyLogInfo: null,
        flowStartText: this.$t('m.newCommon["流程开始"]'),
        loading: false,
        list: [],
        isShowDetail: false,
        imgUrl: require('@/images/orderFinished.png'),
        commentInfo: {},
        processorList: [],
      };
    },
    computed: {
      isShowComment() {
        return this.ticketInfo.is_over && Number(this.ticketInfo.comment_id) !== -1;
      },
      ...mapState({
        nodeList: (state) => state.deployOrder.nodeList,
      }),
      token() {
        return this.$route.query.token;
      },
    },
    watch: {
      nodeList: {
        handler(val) {
          if (val.length !== 0 && !this.ticketInfo.is_over) {
            this.getCurrentProcess();
          }
        },
        deep: true,
      },
    },
    created() {
      // console.log(this.isShowSla);
      this.getOperationLogList();
      this.getTicktComment();
    },
    // 方法集合
    methods: {
      // 获取流转日志-操作日志
      getOperationLogList() {
        const id = this.$route.query.id;
        if (!id) {
          return;
        }
        this.loading = true;
        const params = {};
        params.ticket = id;
        if (this.$route.query.token) {
          params.token = this.$route.query.token;
        }
        this.$store
          .dispatch('change/getLog', params)
          .then((res) => {
            this.list = [];
            res.data.forEach((item) => {
              const line = {};
              line.content = item.message;
              line.tag = item.operate_at;
              if (item.message !== this.flowStartText) {
                // item.content = item.message
                // item.tag = item.operate_at
                item.content = item.operate_at;
                item.tag = item.message;
                item.type = 'primary';
                item.showMore = false;
                item.filled = true;
                delete item.type; // 删除原来的type 使用组件默认
                item.color = 'green';
                this.list.push(JSON.parse(JSON.stringify(item)));
              }
            });
            this.getCurrentProcess();
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.loading = false;
          });
      },
      getCurrentProcess() {
        this.list = this.list.filter(ite => ite.color !== 'blue');
        this.nodeList.forEach((item, index) => {
          const processor = {
            action: '',
            // content: this.ticketInfo.current_processors || '--',
            deal_time: '',
            detail_message: '',
            form_data: [],
            from_state_name: item.name || '',
            from_state_type: '',
            id: -index,
            message: `${i18n.t('m["正在进行中"]')}  ${item.processors}`,
            operate_at: item.update_at,
            operator: item.processors,
            processors: '',
            processors_type: '',
            showMore: false,
            tag:
              `【${item.name}】${i18n.t('m["正在进行中"]')}, ${i18n.t('m["当前处理人"]')}${item.processors}`
              || '--',
            ticket: this.ticketInfo.id,
            ticket_id: this.ticketInfo.id,
            type: 'primary',
            color: 'blue',
          };
          console.log(item.status);
          if (item.status === 'RUNNING' && this.list.findIndex((item) => item.id === processor.id) === -1) {
            this.list.push(processor);
          }
        });
      },
      getTicktComment() {
        if (!this.ticketInfo.is_over || !this.isShowComment) return;
        this.$store.dispatch('ticket/getTicktComment', this.ticketInfo.comment_id).then((res) => {
          if (Object.keys(res.data).length !== 0) {
            this.commentInfo = res.data;
          }
        });
      },
      handleSelect(item) {
        const copyItem = JSON.parse(JSON.stringify(item));
        copyItem.form_data.forEach((form) => {
          form.val = form.value;
          this.conditionField(form, copyItem.form_data);
        });
        copyItem.form_data = copyItem.form_data.filter((form) => form.showFeild);
        this.dispalyLogInfo = copyItem;
      },
      viewProcess() {
        this.$emit('viewProcess', true);
      },
      handleEvaluate() {
        console.log('去评价');
      },
    },
  };
</script>

<style lang="scss" scoped>
@import "../../../../scss/mixins/scroller.scss";
.ticket-process {
  margin-left: -5px;
  cursor: pointer;
  padding: 0px 0px 10px;
  font-size: 12px;
  color: #3a84ff;
}
.log-list {
  width: 100%;
  .ticket-process-content {
    overflow: auto;
    padding: 5px;
    height: calc(100vh - 320px);
    @include scroller;
  }
}
.log-time-line {
  /deep/ {
    .bk-timeline-title,
    .bk-timeline-content {
      font-size: 12px;
    }
    .bk-timeline-title {
      word-break: break-all;
      &:hover {
        color: #3a84ff;
      }
    }
    .bk-timeline-dot {
      padding-bottom: 10px;
    }
  }
}
.process-detail {
  .process-title {
    width: 56px;
    height: 22px;
    font-size: 14px;
    color: #63656e;
    font-weight: 700;
  }
  .process-header {
    margin-top: 11px;
    font-size: 12px;
    height: 24px;
    line-height: 24px;
    background: #f5f7fa;
    border-radius: 2px;
    color: #63656e;
    i {
      color: #c4c6cc;
    }
  }
  .process-content {
    text-align: center;
    font-size: 14px;
    line-height: 22px;
    img {
      margin-top: 55px;
      width: 110px;
      height: 89px;
    }
    p {
      font-size: 14px;
    }
    .appraise {
      color: #3a84ff;
      cursor: pointer;
    }
    .hide-comment {
      height: 0;
    }
    .comment-content {
      width: 100%;
      height: 250px;
      .comment-content-item {
        display: flex;
        margin-top: 5px;
        padding: 0 45px;
        span {
          width: 70px;
          text-align: left;
        }
        p {
          text-align: left;
          font-size: 12px;
          flex: 1;
          color: #9da0a9;
          word-wrap: break-word;
          word-break: break-all;
        }
      }
    }
  }
}
</style>
