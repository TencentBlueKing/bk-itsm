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
  <div class="summary-card">
    <div class="icon-wrap">
      <slot name="icon">
        <i class="bk-icon icon-order"></i>
      </slot>
    </div>
    <div class="summary-data-wrap">
      <div class="title">{{ title }}</div>
      <div class="data-detail">
        <div class="total-num">{{ cardData.total }}</div>
        <div class="week-data">
          <div class="week-data-detail">
            <span class="week-item">
              {{ $t(`m.operation['上周']`) }}
              <span class="week-num">{{cardData.week.last_week_count}}</span>
            </span>
            <span class="week-item">
              {{ $t(`m.operation['本周']`) }}
              <span class="week-num">{{cardData.week.this_week_count}}</span>
            </span>
          </div>
          <div class="week-detail-ratio" :class="ratioCls">
            <span class="ratio-icon">
              <i class="bk-icon icon-arrows-right"></i>
            </span>
            <span class="ratio-value">{{ cardData.week.ratio }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
  export default {
    name: 'SummaryCard',
    props: {
      title: {
        type: String,
        default: '',
      },
      cardData: {
        type: Object,
        default: () => ({}),
      },
    },
    computed: {
      ratioCls() {
        if (this.cardData.week.this_week_count === this.cardData.week.last_week_count) {
          return 'ratio-equal';
        } if (this.cardData.week.this_week_count > this.cardData.week.last_week_count) {
          return 'ratio-up';
        }
        return 'ratio-down';
      },
    },
  };
</script>
<style lang="scss" scoped>
    .summary-card {
        display: flex;
        justify-content: center;
        align-items: center;
        background: #ffffff;
        border-radius: 2px;
        height: 130px;
        box-shadow: 0 2px 6px 0 rgba(0, 0, 0, 0.1);
    }
    .icon-wrap {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 26px;
        width: 80px;
        height: 80px;
        background: #f1f5fb;
        border-radius: 50%;
        i {
            font-size: 24px;
            color: #699df4;
        }
    }
    .summary-data-wrap {
        .title {
            margin-bottom: 7px;
            font-size: 14px;
            color: #63656e;
            line-height: 19px;
        }
        .data-detail {
            display: flex;
            justify-content: center;
            align-items: center;
            .total-num {
                margin-right: 16px;
                font-size: 36px;
                font-weight: 400;
                color: #313238;
                line-height: 42px;
            }
            .week-data-detail {
                font-size: 14px;
                color: #979ba5;
                line-height: 20px;
                .week-item {
                    margin-right: 12px;
                }
                .week-num {
                    font-weight: 700;
                }
            }
            .week-detail-ratio {
                display: flex;
                align-items: center;
                color: #63656e;
                &.ratio-up {
                    color: #ea3636;
                    .ratio-icon {
                        background: #fcdddc;
                        transform: rotate(-45deg);
                    }
                }
                &.ratio-down {
                    color: #14a568;
                    .ratio-icon {
                        background:#e4faf0;
                        transform: rotate(45deg);
                    }
                }
                .ratio-icon {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    width: 16px;
                    height: 16px;
                    font-size: 18px;
                    border-radius: 50%;
                    background: #f0f1f5;
                }
                .ratio-value {
                    margin-left: 6px;
                    font-size: 14px;
                    font-weight: 700;
                }
            }
        }
    }
</style>
