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
  <ul class="child-node">
    <li class="vue-tree-item" v-for="(item, index) in treeDataList" :key="index">
      <div :class="['tree-node',{ 'down': item.showChildren,'set-frist-pLeft': treeIndex + 1 === 1,'active': item.checkInfo }]"
        :style="pLeft" @click="toggle(item)">
        <i v-if="!item.showChildren"
          class="bk-icon icon-right-shape"
          :class="{ 'bk-padding': !item.has_children }"
          @click.stop="toggleChildren(item)"></i>
        <i v-else
          class="bk-icon icon-down-shape"
          :class="{ 'bk-padding': !item.has_children }"
          @click.stop="toggleChildren(item)"></i>
        <!-- 文件icon -->
        <i class="bk-icon icon-folder-open-shape"></i>
        <span class="name-text" :title="item.name">{{item.name}}</span>
        <!-- 选中 -->
        <i v-if="item.checkInfo"
          class="bk-icon icon-check-1"
          style="float: right; margin-top: 11px;"></i>
      </div>
      <collapse-transition>
        <template v-if="item.showChildren && item.children">
          <Tree
            :tree-data-list="item.children"
            :tree-index="treeIndex + 1"
            @toggle="toggle"
            @toggleChildren="toggleChildren">
          </Tree>
        </template>
      </collapse-transition>
    </li>
  </ul>
</template>
<script>
  import collapseTransition from '../../../utils/collapse-transition';
  export default {
    name: 'Tree',
    components: {
      collapseTransition,
    },
    props: {
      treeDataList: {
        type: Array,
        default: [],
      },
      treeIndex: {
        type: Number,
        default: 0,
      },
    },
    data() {
      return {
        pLeft: `padding-left:${15 * (this.treeIndex + 1)}px; padding-right: 10px;`,
      };
    },
    methods: {
      // 展开子级
      toggleChildren(item) {
        this.$emit('toggleChildren', item);
      },
      // 选中
      toggle(item) {
        this.$emit('toggle', item);
      },
    },
  };
</script>

<style  lang="scss" scoped>
    .tree-node {
        position: relative;
        padding-left: 20px;
        line-height: 36px;
        height: 36px;
        font-size:14px;
        font-weight:400;
        color: #63656E;
        cursor: pointer;
        transition: all 0.3s ease;
        .bk-icon {
            color: #C4C6CC;
        }
        &.set-frist-pLeft {
            padding-left: 20px !important;
        }
        &.down {
            transition: all 0.3s ease;
            .icon-user-triangle {
                transform: rotate(0);
            }
        }
        &:hover,&.active{
            background: #e1ecff;
            color: #4b8fff;
            .bk-icon {
                color: #4b8fff;
            }
            .unfold-icon .icon-user-triangle,.unfold-icon .tree-file {
                &::before {
                    color: #4b8fff;
                }
            }
            .icon-user-more {
                display: block;
                padding: 10px;
            }
        }
        .name-text {
            display: inline-block;
            vertical-align: middle;
            width: calc(100% - 110px);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            &.chang-width {
                max-width: 100px;
            }
            &.set-width {
                max-width: 45px;
            }
        }
        .unfold-icon {
            display: inline-block;
            vertical-align: middle;
            .tree-file {
                display: inline-block;
                vertical-align: middle;
                font-size: 14px;
                margin-right: 6px;
                font-size: 18px;
                &::before {
                    color: #c6d0d9;
                }
            }
        }
    }
    .icon-down-shape,
    .icon-right-shape {
        float: left;
        width: 24px;
        height: 36px;
        line-height: 36px;
    }
    .icon-folder-open-shape {
        float: left;
        margin-top: 11px;
        margin-right: 6px;
    }
    .bk-padding {
        opacity: 0;
    }
    .icon-user-triangle {
        opacity: 1;
        display: inline-block;
        vertical-align: middle;
        font-size: 10px;
        transform: rotate(-90deg);
        transition: all 0.3s ease;
        &::before {
            color: #c6d0d9;
        }
        &.hidden {
            opacity: 0;
        }
    }
    .check-icon {
        position: absolute;
        right: 19px;
        top: 50%;
        transform: translateY(-50%);
        display: block;
        width:18px;
        height:18px;
        background:rgba(255,255,255,1);
        border:1px solid rgba(151,155,165,1);
        border-radius: 50%;
        &.icon-user-sure {
            font-size: 20px;
            width: auto;
            height: auto;
            border-radius: 0;
            border: none;
            background: none;
            &::before {
                color: #3A84FF;
            }
        }
    }
</style>
