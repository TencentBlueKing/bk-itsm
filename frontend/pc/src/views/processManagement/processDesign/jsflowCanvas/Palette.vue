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
  <ul>
    <li v-bk-tooltips.right="$t(`m.treeinfo['开始节点']`)">
      <div class="entry-item entry-start"
        data-type="START">
        {{ $t('m.treeinfo["开始"]') }}
      </div>
      <div class="entry-disabled"></div>
    </li>
    <li v-bk-tooltips.right="$t(`m.treeinfo['结束节点']`)">
      <div class="entry-item"
        data-type="END">
        {{ $t('m.treeinfo["结束"]') }}
      </div>
      <div class="entry-disabled"></div>
    </li>
    <li v-bk-tooltips.right="$t(`m.treeinfo['手动节点']`)">
      <div class="entry-item entry-gateway" data-type="NORMAL" style="margin: 10px 0 0;">
        <i class="bk-itsm-icon icon-icon-artificial" style="font-size: 26px;"></i>
      </div>
    </li>
    <li v-bk-tooltips.right="$t(`m.treeinfo['API节点']`)">
      <div class="entry-item entry-gateway" data-type="TASK" style="margin: 12px 0 2px;">
        <i class="bk-itsm-icon icon-api-node" style="font-size: 26px;"></i>
      </div>
    </li>
    <li v-bk-tooltips.right="$t(`m.treeinfo['标准运维节点']`)">
      <div class="entry-item entry-gateway" data-type="TASK-SOPS" style="margin: 12px 0 2px;">
        <i class="bk-itsm-icon icon-task-icon" style="font-size: 26px;"></i>
      </div>
    </li>
    <li v-bk-tooltips.right="$t(`m.treeinfo['会签节点']`)">
      <div class="entry-item entry-gateway" data-type="SIGN" style="margin: 12px 0 2px;">
        <i class="bk-itsm-icon icon-sign-node" style="font-size: 26px;"></i>
      </div>
    </li>
    <li v-bk-tooltips.right="$t(`m.treeinfo['审批节点']`)">
      <div class="entry-item entry-gateway" data-type="APPROVAL" style="margin: 12px 0 2px;">
        <i class="bk-itsm-icon icon-approval-node" style="font-size: 26px;"></i>
      </div>
    </li>
    <li v-bk-tooltips.right="$t(`m.treeinfo['并行网关']`)">
      <div class="entry-item entry-gateway" data-type="ROUTER-P">
        <i class="bk-itsm-icon icon-flow-convergence"></i>
      </div>
    </li>
    <li v-bk-tooltips.right="$t(`m.treeinfo['汇聚网关']`)">
      <div class="entry-item entry-gateway" data-type="COVERAGE">
        <i class="bk-itsm-icon icon-flow-branch"></i>
      </div>
    </li>
  </ul>
</template>
<script>
  export default {
    name: 'Palette',
    mounted() {
      // this.$emit('registerPaletteEvent')
    },
  };
</script>
<style lang="scss" scoped>
    ul {
        margin: 0;
        padding: 0;
        list-style: none;
        li {
            text-align: center;
            position: relative;
            &:hover {
                .entry-title {
                    display: block;
                }
            }
            .entry-disabled {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                cursor: not-allowed;
                z-index: 2;
            }
            .bk-itsm-icon {
                color: #737987;
                &:hover {
                    color: #3A84FF;
                }
            }
        }
        .entry-item {
            display: inline-block;
            margin: 10px 0;
            width: 34px;
            height: 34px;
            line-height: 32px;
            border: 1px solid #C3CDD7;
            border-radius: 50%;
            user-select: none;
            cursor: move;
            color: #C6CFD9;
            font-size: 12px;
        }
        .entry-gateway {
            border: none;
            .bk-itsm-icon {
                font-size: 36px;
            }
        }
        .entry-cursor {
            border: none;
            cursor: pointer;
            .bk-itsm-icon {
                font-size: 26px;
            }
        }
        .entry-title {
            position: absolute;
            top: 12px;
            left: 65px;
            background-color: #181818;
            color: #fff;
            width: 90px;
            font-size: 12px;
            text-align: center;
            line-height: 26px;
            z-index: 1000;
            display: none;
            .bk-title-triangle {
                position: absolute;
                top: 10px;
                left: -3px;
                width: 6px;
                height: 6px;
                background-color: #181818;
                transform: rotate(45deg);
            }
        }
    }
</style>
