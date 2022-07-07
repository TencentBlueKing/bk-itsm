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
  <div class="bk-search-info">
    <!-- 更多搜索 -->
    <collapse-transition>
      <div class="bk-filter" v-if="showMore">
        <bk-form
          :label-width="200"
          form-type="vertical"
          ref="dynamicForm">
          <div class="bk-filter-line"
            v-for="(item, index) in moreSearch"
            v-if="!item.isHidden"
            :key="index">
            <bk-form-item :label="item.name" v-if="item.type === 'input'">
              <bk-input v-model="item.value"
                :placeholder="item.placeholder">
              </bk-input>
            </bk-form-item>
            <bk-form-item :label="item.name" v-if="item.type === 'select'">
              <bk-select
                searchable
                :show-select-all="item.multiSelect"
                :multiple="item.multiSelect"
                v-model="item.value">
                <bk-option v-for="option in item.list"
                  :key="option.key"
                  :id="option.key"
                  :name="option.name">
                </bk-option>
              </bk-select>
            </bk-form-item>
            <bk-form-item :label="item.name" v-if="item.type === 'datetime'">
              <bk-date-picker
                style="width: 100%;"
                v-model="item.value"
                :placeholder="item.placeholder"
                :type="'datetimerange'">
              </bk-date-picker>
            </bk-form-item>
            <!-- 级联类型 -->
            <bk-form-item :label="item.name" v-if="item.type === 'cascade'">
              <common-cascade
                style="width: 100%;"
                v-model="item.value"
                :options="item.list"
                :iscollect_first="false"
                :iscollect_two="false"
                :isshow-number="false"
                :isactive="true">
              </common-cascade>
            </bk-form-item>
            <!-- 人员 -->
            <bk-form-item :label="item.name" v-if="item.type === 'member'">
              <member-select v-model="item.value" :multiple="false"></member-select>
            </bk-form-item>
          </div>
        </bk-form>
        <!-- 查询清空 -->
        <div class="bk-filter-btn">
          <bk-button theme="primary"
            :title="$t(`m.deployPage['查询']`)"
            @click="searchContent">
            {{ $t('m.deployPage["查询"]') }}
          </bk-button>
          <bk-button theme="default"
            :title="$t(`m.deployPage['清空']`)"
            @click="clearSearch">
            {{ $t('m.deployPage["清空"]') }}
          </bk-button>
        </div>
      </div>
    </collapse-transition>
  </div>
</template>

<script>
  import collapseTransition from '../../../utils/collapse-transition';
  import commonCascade from '../commonCascade';
  import memberSelect from '../memberSelect';

  export default {
    name: 'searchInfo',
    components: {
      collapseTransition,
      commonCascade,
      memberSelect,
    },
    props: {
      moreSearch: {
        type: Array,
        default() {
          return [];
        },
      },
    },
    data() {
      return {
        searchWord: '',
        showMore: false,
      };
    },
    methods: {
      searchMore() {
        this.showMore = !this.showMore;
      },
      closeSearch() {
        this.showMore = false;
      },
      searchContent() {
        this.$parent.getList(1, true);
      },
      clearSearch() {
        this.$parent.clearSearch();
        this.$parent.getList(1, true);
      },
    },
  };
</script>

<style lang="scss" scoped>
    @import '../../../scss/mixins/clearfix.scss';
    @import '../../../scss/mixins/scroller.scss';

    .bk-search-info {
        position: relative;
        width: 100%;
    }

    .bk-filter {
        position: relative;
        box-sizing: content-box;
        color: #737987;
        background-color: #ffffff;
        margin-top: 12px;
        padding: 10px;
        padding-right: 0px;
        transition: .3s height ease-in-out, .3s padding-top ease-in-out, .3s padding-bottom ease-in-out;
        @include clearfix;
        .bk-filter-line {
            float: left;
            width: 50%;
            padding-right: 10px;
            height: 63px;
        }
        .bk-filter-btn {
            margin-top: 10px;
        }
    }
    @media screen and (min-width: 960px) and (max-width: 1380px) {
        .bk-filter {
            .bk-filter-line {
                width: 50%;
            }
        }
    }
    @media screen and (min-width: 1380px) and (max-width: 1680px) {
        .bk-filter {
            .bk-filter-line {
                width: 33.33%;
            }
        }
    }
    @media screen and (min-width: 1680px) {
        .bk-filter {
            .bk-filter-line {
                width: 25%;
            }
        }
    }
</style>
