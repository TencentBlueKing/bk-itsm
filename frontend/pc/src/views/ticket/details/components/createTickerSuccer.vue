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
    <div class="tip-box">
        <div class="tip-content">
            <i class="bk-itsm-icon icon-success-fill"></i>
            <span>{{ $t(`m['提单成功']`) }}</span>
            <p>{{ $t(`m['当前流程已跳转至下一流程节点']`) }}，{{ time }}s{{ $t(`m['后将自动跳转至流程详情查看']`) }}</p>
            <div class="tip-operation">
                <bk-button :theme="'default'" type="submit" @click="onBackClick">{{ $t(`m['返回列表']`) }}</bk-button>
                <bk-button :theme="'primary'" @click="jumpPage">{{ $t(`m['查看流程详情']`) }}</bk-button>
            </div>
        </div>
    </div>
</template>
<script>
    export default {
        name: 'CreateTickerSuccer',
        props: {
            routerInfo: Object,
            times: {
                type: Number,
                default () {
                    return 30
                }
            }
        },
        data () {
            const time = this.times
            return {
                time,
                isStart: true
            }
        },
        mounted () {
            this.countDown()
        },
        methods: {
            countDown () {
                this.timer = setInterval(() => {
                    this.time--
                    if (this.time === 0 && this.isStart) {
                        clearInterval(this.timer)
                        this.jumpPage()
                    }
                }, 1000)
            },
            jumpPage () {
                this.isStart = false
                this.$router.push(this.routerInfo)
            },
            onBackClick () {
                this.isStart = false
                this.$emit('onBackIconClick')
            }
        }
    }
</script>
<style scoped lang="scss">
    .tip-box {
        text-align: center;
        margin: 0 auto;
        .tip-content {
            position: absolute;
            top: calc(50% - 125px);
            left: calc(50% - 300px);
            width: 600px;
            height: 250px;
            display: flex;
            padding: 20px;
            justify-content: space-between;
            flex-direction: column;
            i {
                font-size: 60px;
                color: rgb(45, 243, 128);
            }
            span {
                font-weight: 600;
                font-size: 20px;
            }
            p {
                color: #777880;
            }

        }
    }
</style>
