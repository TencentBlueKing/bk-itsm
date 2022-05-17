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
  <div class="empty-page-tip">
    <div class="tip-content-wrap">
      <h3>{{ title }}</h3>
      <p>{{ subTitle }}</p>
      <div class="btns-area">
        <slot name="btns"></slot>
      </div>
      <div class="desc-area">
        <div class="desc-item" v-for="(item, index) in desc" :key="index">
          <div class="desc-img">
            <img :src="item.src" alt="tips" />
          </div>
          <div class="desc-content">
            <h4>{{ item.title }}</h4>
            <p>{{ item.content }}</p>
          </div>
        </div>
      </div>
      <div class="link-area">
        <div class="link-item" v-for="(item, index) in links" :key="index">
          {{item.text}}
          <a :href="item.href" target="_blank" class="link-btn">
            {{ item.btn }}
            <i class="bk-itsm-icon icon-itsm-icon-three-seven"></i>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
  export default {
    name: 'EmptyPageTip',
    props: {
      title: {
        type: String,
        value: '',
      },
      subTitle: {
        type: String,
        value: '',
      },
      desc: {
        type: Array,
        default: () => ([]),
        // eg: [{
        //     img: '',
        //     title: '',
        //     content: ''
        // }]
      },
      links: {
        type: Array,
        default: () => ([]),
        // eg: [{
        //     text: '',
        //     href: '',
        //     btn: ''
        // }]
      },
    },
  };
</script>
<style lang="scss" scoped>
    .empty-page-tip {
        .tip-content-wrap {
            margin: 30px auto 0;
            width: 1366px;
            & > h3 {
                margin: 0 0 18px;
                font-size: 24px;
                line-height: 32px;
                font-weight: 400;
                color: #2d3542;
            }
            & > p {
                margin: 0 0 30px;
                line-height: 22px;
                font-size: 16px;
                font-weight: 400;
                color: #2d3542;
            }
        }
        .desc-area {
            display: flex;
            justify-content: space-between;
            margin-top: 50px;
            padding: 80px 0;
            background: #ffffff;
            .desc-item {
                display: flex;
                justify-content: space-between;
                padding-right: 30px;
                width: 50%;
                &:first-child {
                    border-right: 1px solid #dcdee5;
                }
            }
            .desc-img {
                width: 320px;
                text-align: center;
            }
            .desc-content {
                width: 304px;
                & > h4 {
                    margin: 20px 0;
                    line-height: 24px;
                    font-size: 18px;
                    font-weight: 500;
                    color: #2d3542;
                }
                & > p {
                    line-height: 26px;
                    font-size: 14px;
                    color: #63656e;
                    word-break: break-all;
                }
            }
        }
        .link-area {
            margin-top: 60px;
            .link-item {
                margin-bottom: 12px;
                line-height: 22px;
                font-size: 16px;
                color: #63656e;
            }
            .link-btn {
                color: #3a84ff;
            }
        }
    }
</style>
