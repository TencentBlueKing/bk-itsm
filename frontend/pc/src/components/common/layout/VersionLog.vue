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
  <div class="version-log-wrap">
    <!-- 版本信息 -->
    <div class="bk-version-shade"></div>
    <div class="bk-itsm-version" v-bkloading="{ isLoading: loading }">
      <!-- 版本号 -->
      <div class="bk-version-left">
        <div class="bk-version-blank"></div>
        <div class="bk-version-number">
          <ul>
            <li v-for="(item, index) in versionList"
              :class="{
                'bk-border-bottom': (index === versionList.length - 1),
                'bk-click': versionInfo.version === item.version
              }"
              :key="index"
              @click="changeVersion(item, index)">
              <p :class="{
                'bk-number-name': true,
                'bk-version-click-color': versionInfo.version === item.version }">
                <span>V{{item.version}}</span>
              </p>
              <p :class="{
                'bk-number-time': true,
                'bk-version-click-color': versionInfo.version === item.version }">
                {{item.create_at}}
                <span class="bk-current-version"
                  v-if="item.is_latest === true">{{ $t('m.wiki["当前版本"]')}}</span>
              </p>
              <div class="bk-version-click" v-if="versionInfo.version === item.version"></div>
            </li>
          </ul>
        </div>
        <!-- 版本日志 -->
        <div class="bk-version-blank"></div>
      </div>
      <div class="bk-version-content">
        <div class="bk-content-close" @click="$emit('close')">
          <i class="bk-icon icon-close" style="right: 6px;"></i>
        </div>
        <div class="bk-content-title">
          {{ $t('m.wiki["【"]')}}V{{versionInfo.version}}{{ $t('m.wiki["】版本更新明细"]')}}
        </div>
        <div class="bk-content-markdown" v-html="markdownText"></div>
      </div>
    </div>
  </div>
</template>

<script>
  import { errorHandler } from '@/utils/errorHandler.js';
  import _ from 'lodash';

  export default {
    name: 'VersionLog',
    data() {
      return {
        loading: false,
        markdownText: '',
        versionList: [],
        versionInfo: {
          version: '',
        },
      };
    },
    computed: {},
    watch: {},
    created() {

    },
    async mounted() {
      await this.getVersionList();
      this.initData();
    },
    methods: {
      initData() {
        if (this.versionList.length) {
          this.versionInfo = this.versionList[0];
          this.changeVersion(this.versionList[0]);
        }
      },
      async getVersionList() {
        this.loading = true;
        return this.$store.dispatch('version/version_logs').then((res) => {
          this.versionList = res.data.data;
        })
          .catch((res) => {
            errorHandler(res.data.message, this);
          })
          .finally(() => {
            this.loading = false;
          });
      },
      changeVersion(item) {
        this.versionInfo = item;
        if (typeof this.versionInfo.log === 'string') {
          this.versionInfo.log = _.split(this.versionInfo.log, '\n');
        }
        this.markdownText = '';
        this.markdownText = this.addSpan(this.versionInfo.log);
      },
      addSpan(log) {
        let result = '';
        log.forEach((item) => {
          const arrayStr = item.split('');
          arrayStr.splice(arrayStr.findIndex(str => str === '[' || str === '【'), 0, '<span>');
          arrayStr.splice(arrayStr.findIndex(str => str === ']' || str === '】') + 1, 0, '</span>');
          result += arrayStr.join('');
        });
        return result;
      },
    },
  };
</script>
<style lang='scss' scoped>
@import '../../../scss/mixins/clearfix.scss';
@import '../../../scss/mixins/scroller.scss';
/* 版本信息 */
.version-log-wrap {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1001;
}
.bk-version-shade {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 0;
    background: rgba(0, 0, 0, 0.6);
}

.bk-itsm-version {
    position: absolute;
    padding: 0;
    top: 50%;
    left: 50%;
    width: 850px;
    height: 460px;
    border-radius: 2px;
    transform: translate(-50%, -50%);
    background: #fff;
    z-index: 1002;
    @include clearfix;

    .bk-version-left {
        float: left;
        height: 100%;
        width: 180px;
        border-right: 1px solid #DCDEE5;

        .bk-version-blank {
            width: 100%;
            height: 20px;
            background: #FAFBFD;
        }

        .bk-version-number {
            width: 100%;
            height: calc(100% - 40px);
            overflow: auto;
            @include scroller;

            ul {
                width: 100%;
                background-color: #FAFBFD;

                li {
                    width: 100%;
                    height: 54px;
                    padding: 2px 0 8px 30px;
                    color: #63656E;
                    font-size: 12px;
                    position: relative;
                    border-top: 1px solid #DCDEE5;

                    cursor: pointer;

                    .bk-number-time {
                        height: 17px;
                        font-size: 12px;
                        font-weight: 400;
                        color: rgba(151, 155, 165, 1);
                        line-height: 17px;
                    }

                    .bk-number-name {
                        color: #313238;
                        font-size: 16px;
                        position: relative;
                        font-weight: 700;
                      }
                    .bk-number-time {
                      .bk-current-version {
                          display: inline-block;
                          margin-left: 10px;
                          background: #699DF4;
                          color: #fff;
                          padding: 0 5px;
                          line-height: 20px;
                          font-size: 12px;
                          border-radius: 3px;
                      }
                    }
                    .bk-version-click {
                        position: absolute;
                        top: -2px;
                        left: 0;
                        width: 6px;
                        height: 55px;
                        background-color: #3A84FF;
                    }

                    .bk-version-click-color {
                        color: #3A84FF;
                    }

                    &:hover {
                        background-color: white;
                    }
                }
            }

            .bk-click {
                background: #fff;
                border-right: none;
            }

            .bk-border-bottom {
                border-bottom: 1px solid #DCDEE5;
            }
        }
    }

    .bk-version-content {
        float: left;
        width: calc(100% - 180px);
        background: #fff;
        padding: 25px 0 35px 35px;
        height: 100%;
        position: relative;

        .bk-content-title {
            font-size: 24px;
            height: 33px;
            line-height: 33px;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .bk-content-close {
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 12px;
            color: #979BA5;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            text-align: center;
            line-height: 30px;
            cursor: pointer;

            &:hover {
                background-color: #D8D8D8;
                color: #fff;
            }
        }

        .bk-content-markdown {
            height: calc(100% - 33px);
            overflow: auto;
            @include scroller;

            /deep/ p {
                font-size: 14px;
                font-weight: 500;
                color: #313238;
                line-height: 28px;
                margin-left: 5px;
                margin-top: 5px;

                span {
                    font-weight: bold;
                }
            }
        }
    }
}
</style>
