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
  <div class="empty">
    <div class="status">
      <img :src="pictures[status]" alt="">
    </div>
    <div class="tip">
      <span class="title">{{ titleMap[status] }}</span>
      <p v-if="status === '500'" class="oper"><span class="oper-btn" @click="refresh">{{ $t(`m['刷新']`) }}</span></p>
      <p v-if="status === 'search-empty'" class="oper">{{ $t(`m['可以尝试 调试关键词 或']`) }}<span class="oper-btn"
        @click="clearSearch"> {{ $t(`m['清空筛选条件']`) }}</span></p>
      <slot name="create"></slot>
    </div>
  </div>
</template>
  
<script>
  export default {
    name: 'Empty',
    props: {
      isSearch: {
        type: Boolean,
        default: false,
      },
      isError: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      const titleMap = {
        empty: this.$t('m["暂无数据"]'),
        500: this.$t('m["数据获取异常"]'),
        'search-empty': this.$t('m["搜索结果为空"]'),
      };
      return {
        titleMap,
        pictures: {
          empty: require('../../images/empty.png'),
          500: require('../../images/error.png'),
          'search-empty': require('../../images/search-empty.png'),
        },
      };
    },
    computed: {
      status() {
        if (this.isError) return '500';
        if (this.isSearch) return 'search-empty';
        return 'empty';
      },
    },
    methods: {
      refresh() {
        this.$emit('onClearSearch');
        this.$emit('onRefresh');
      },
      clearSearch() {
        this.$emit('onClearSearch');
      },
    },
  };
</script>
<style lang="scss">
.bk-table-empty-block {
  background-color: #fff;
}
</style>
<style lang="scss" scoped>
.empty {
  width: 100%;
  height: 100%;
  .status {
    width: 100%;
    height: 100px;
    text-align: center;
    img {
      max-width: 220px;
      height: 100px;
    }
  }
  .tip {
    .title {
      display: block;
      width: 84px;
      height: 22px;
      font-family: MicrosoftYaHei;
      font-size: 14px;
      color: #63656E;
      letter-spacing: 0;
      text-align: center;
      line-height: 22px;
      margin: 8px auto 0;
    }
    .oper {
      display: block;
      color: #979ba5;
      font-size: 12px;
      line-height: 20px;
      margin: 8px auto 0;
      .oper-btn {
        color: #3a84ff;
        font-size: 12px;
        line-height: 20px;
        cursor: pointer;
      }
    }
  }
}
</style>
