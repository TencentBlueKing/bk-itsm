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
  <div class="bk-timeline-contain">
    <div class="bk-timeline-contain-va">
      <template v-for="(item, index) in lineList">
        <li :key="index" :class="{ 'bk-timeline-item': true, 'content-va-sign': parent === 'sign' }">
          <div :class="{ 'bk-timeline-item-head-va': true, 'head-va-sign': parent === 'sign', 'head-va-sign-first': parent === 'sign' && !index }">
            <div class="bk-timeline-item-head">
              <header>
                <slot name="header" v-bind:item="item">
                </slot>
              </header>
            </div>
          </div>
          <div class="bk-timeline-item-content-va">
            <div class="bk-timeline-item-content">
              <main>
                <slot name="content" v-bind:item="item">
                </slot>
              </main>
            </div>
          </div>
        </li>
      </template>
    </div>
  </div>
</template>
<script>
  export default {
    name: 'timeLine',
    props: {
      lineList: {
        type: [Array, Object],
        default() {
          return [];
        },
      },
      parent: {
        type: String,
        default: 'normal',
      },
    },
    data() {
      return {

      };
    },
  };
</script>
<style lang='scss' scoped>
    .bk-timeline-contain {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        .bk-timeline-contain-va {
            .bk-timeline-item {
                position: relative;
                overflow: hidden;
            }
            .bk-timeline-item::before {
                content: "";
                height: 100%;
                width: 2px;
                background-color: #3c96ff;
                left: 5px;
                position: absolute;
                top: 0;
            }
            .content-va-sign::before{
                width: 1px;
                background-color: #D8D8D8;
            }

            .bk-timeline-item:last-child{
                &:before{
                    width: 0;
                }
            }

            .bk-timeline-item-content-va,
            .bk-timeline-item-head-va {
                position: relative;
                margin: 0;
                padding: 0;
                padding-left: 19px;

            }
            .bk-timeline-item-head {
                transform: translateY(-2px);
                font-size: 12px;
            }
            .bk-timeline-item-head-va::before {
                content: "";
                border: 2px solid #3c96ff;
                content: "";
                height: 8px;
                width: 8px;
                background-color: #fff;
                left: 0px;
                position: absolute;
                z-index: 1;
                border-radius: 20px;
                top: calc(50% - 6px);
                top: 0;
            }
            .head-va-sign::before{
                border: 2px solid #40C024;
                background-color: #40C024;
            }

            .head-va-sign-first::before{
                border: 2px solid #D8D8D8;
                background-color: white;
            }
            .bk-timeline-item-head-va.bk-timeline-item-head-va-bottom::before {
                bottom: 20px;
            }
        }
    }
    main,
    header {
        padding: 0;
        margin: 0;
        position: relative;
    }
</style>
