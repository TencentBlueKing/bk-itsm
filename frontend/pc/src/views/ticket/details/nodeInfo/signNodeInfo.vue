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
  <div class="bk-sign-node-content" v-bkloading="{ isLoading: getLogFlag }">
    <div class="bk-log-flow">
      <template v-if="logs.length">
        <time-line :line-list="logs" :parent="'sign'">
          <template v-slot:header="{ item }">
            <div class="bk-timeline-user-header">
              <span class="bk-inline-block bk-default-width"
                v-bk-tooltips.top="item.message">{{ item.message}}</span>
              <span class="bk-inline-block button" v-if="item.tag !== 'processors'">
                <span class="bk-inline-block isOn auto" @click="item.showMore = !item.showMore"
                  v-if="!item.showMore">{{ $t('m.newCommon["展开"]') }}
                  <i class="bk-icon icon-angle-down bk-selector-icon ml5"></i>
                </span>
                <span class="bk-inline-block isOff auto" @click="item.showMore = !item.showMore" v-else>{{ $t('m.newCommon["收起"]') }}<i class="bk-icon icon-angle-up bk-selector-icon ml5"></i>
                </span>
              </span>
            </div>
          </template>
          <template v-slot:content="{ item }">
            <div class="bk-timeline-user-content">
              <div v-if="item.showMore" class="bk-area-show-back">
                <!-- 静态展示 -->
                <template v-for="(ite, inde) in item.form_data">
                  <fields-done
                    :key="inde"
                    :item="ite"
                    origin="log"
                  ></fields-done>
                </template>
              </div>
              <div class="bk-timeline-user-footer">
                {{ item.operate_at }}
              </div>
            </div>
          </template>
        </time-line>
      </template>
      <template v-else>
        <p class="no-data">{{$t(`m.newCommon['暂无信息']`)}}</p>
      </template>
    </div>
  </div>
</template>

<script>
  import timeLine from '../components/timeLine';
  import fieldsDone from '../components/fieldsDone';
  import { errorHandler } from '@/utils/errorHandler';
  export default {
    name: 'signNodeInfo',
    components: {
      timeLine,
      fieldsDone,
    },
    props: {
      nodeInfo: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        logs: {},
        getLogFlag: false,
      };
    },
    async mounted() {
      await this.nodeInfo;
      await this.initData();
    },
    methods: {
      async initData() {
        this.getLogFlag = true;
        await this.getLogs();
        const waitProcessors = [];
        this.nodeInfo.tasks.forEach((processor) => {
          if (processor.status === 'WAIT') {
            waitProcessors.push(processor.processor);
          }
        });
        const tempLog = {
          message: waitProcessors.length + this.$t('m.newCommon[\'人待处理\']'),
          operate_at: this.getFormatDate(),
          tag: 'processors',
        };
        tempLog.message += waitProcessors.length ? this.$t('m.newCommon[\'：\']') + waitProcessors.join(',') : '';
        this.logs.unshift(tempLog);
        this.getLogFlag = false;
      },
      getFormatDate() {
        const date = new Date();
        let month = date.getMonth() + 1;
        let strDate = date.getDate();
        if (month >= 1 && month <= 9) {
          month = `0${month}`;
        }
        if (strDate >= 0 && strDate <= 9) {
          strDate = `0${strDate}`;
        }
        const currentDate = `${date.getFullYear()}-${month}-${strDate
        } ${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`;
        return currentDate;
      },
      async getLogs() {
        const params = {
          ticket: this.nodeInfo.ticket_id,
          status: this.nodeInfo.id,
          type: 'SIGN',
        };
        await this.$store.dispatch('apiRemote/get_sign_logs', params).then((res) => {
          res.data.forEach((item) => {
            this.$set(item, 'showMore', false);
          });
          this.logs = res.data;
          this.logs.reverse();
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
    },
  };
</script>

<style scoped lang='scss'>
    @import '../../../../scss/mixins/clearfix.scss';
    @import '../../../../scss/mixins/scroller.scss';
    /* 表格样式 */
    .bk-sign-node-content {
        font-size: 14px;
        color: #63656E;

        .bk-log-flow{
            position: relative;
            padding: 10px;
            color: #737987;
            font-size: 14px;
            width: 100%;

            .no-data{
                color: #63656E;
            }

            .bk-timeline-user-header {
                .bk-inline-block {
                    display: inline-block;
                    font-size: 12px;

                    &.button {
                        cursor: pointer;
                        padding: 0 10px;
                        color: #3A84FF;
                        position: relative;
                        width: 65px;
                        float: right;

                        .bk-selector-icon {
                            top: 2px;
                            right: -12px;
                            transform: scale(0.8);
                        }

                        .auto {
                            position: relative;
                            width: auto;
                            padding-right: 2px;
                            display: inline-flex;
                            align-items: center;
                        }
                    }

                    &.bk-default-width {
                        vertical-align: text-top;
                        text-overflow: ellipsis;
                        white-space: nowrap;
                        overflow: hidden;
                        max-width: calc(100% - 67px)
                    }
                }
            }

            .bk-timeline-user-content {
                font-size: 12px;

                .bk-timeline-user-footer {
                    padding-top: 0px;
                    padding-bottom: 12px;
                    color: rgba(196, 198, 204, 1);
                }

                .bk-area-show-back {
                    background-color: #fafbfd;
                    padding: 4px 8px;
                }
            }

        }
    }

</style>
