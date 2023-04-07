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
  <div class="chart-card">
    <div class="card-header">
      <h4>
        {{ title }}
        <i v-if="desc" class="bk-icon icon-info" v-bk-tooltips="{
          content: desc,
          placement: 'top',
          theme: 'light'
        }">
        </i>
      </h4>
      <div class="search-wrap" v-if="showSearch">
        <bk-input
          right-icon="bk-icon icon-search"
          :placeholder="placeholder"
          v-model="searchStr"
          :clearable="true"
          @change="onSearch"
          @clear="onClear">
        </bk-input>
      </div>
    </div>
    <div class="card-content" v-bkloading="{ isLoading: loading, opacity: 1 }">
      <slot></slot>
    </div>
  </div>
</template>
<script>
  import debounce from 'lodash/debounce';

  export default {
    name: 'ChartCard',
    props: {
      title: {
        type: String,
        default: '',
      },
      desc: {
        type: String,
        default: '',
      },
      showSearch: {
        type: Boolean,
        default: false,
      },
      placeholder: {
        type: String,
        default: '',
      },
      loading: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        searchStr: '',
      };
    },
    created() {
      this.onSearch = debounce(this.searchHandler, 500);
    },
    methods: {
      searchHandler(val) {
        this.$emit('search', val);
      },
      onClear() {
        this.$emit('clear');
      },
    },
  };
</script>
<style lang="scss" scoped>
    .chart-card {
        position: relative;
        padding: 0 16px;
        background: #ffffff;
        height: 400px;
        border-radius: 2px;
        box-shadow: 0 2px 2px 0 rgba(0, 0, 0, 0.1);
    }
    .card-header {
        & > h4 {
            margin: 16px 0;
            color: #000000;
            font-size: 14px;
            font-weight: normal;
            line-height: 19px;
        }
        i {
            color: #979ba5;
            cursor: pointer;
        }
        .search-wrap {
            position: absolute;
            right: 20px;
            top: 10px;
            width: 320px;
        }
    }
    .card-content {
        min-height: 200px;
    }
</style>
