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
  <div class="build-detail-info">
    <!-- Info -->
    <div class="base-info">
      <h3 class="setion-title">Info</h3>
      <ul class="basic-list block">
        <li class="basic-item" v-for="(item, index) in infoList" :key="index">
          <span class="basic-name" style="width: 100px">{{ item.name }}：</span>
          <span class="basic-value">
            {{ item.value }}
          </span>
        </li>
      </ul>
    </div>
    <!-- 变量 -->
    <div class="base-info mt30">
      <bk-table
        :data="buildItem.properties">
        <bk-table-column label="键" prop="key" width="180"></bk-table-column>
        <bk-table-column label="值" prop="value"></bk-table-column>
      </bk-table>
    </div>
  </div>
</template>

<script>
  import dayjs from 'dayjs';

  const infoList = [
    { name: 'Name', key: 'name', value: '' },
    { name: 'Path', key: 'path', value: '' },
    { name: 'Size', key: 'size', value: '' },
    { name: 'Created', key: 'createTime', value: '--' },
    { name: 'Last Modified', key: 'modifiedTime', value: '' },
  ];
  export default {
    name: 'BuildDetailInfo',
    props: {
      buildItem: {
        type: Object,
        default: () => ({}),
      },
    },
    data() {
      return {
        infoList: [],
      };
    },
    mounted() {
      this.infoList = infoList.map((item) => {
        switch (item.key) {
          case 'modifiedTime':
            item.value = dayjs(this.buildItem.modifiedTime * 1000).format('YYYY-MM-DD hh:mm:ss');
            break;
          default:
            item.value = this.buildItem[item.key] || '--';
        }
        return item;
      });
    },
    methods: {

    },
  };
</script>
<style lang='scss' scoped>
@import '~@/scss/mixins/form.scss';
.build-detail-info {
    padding: 27px 29px;
}
</style>
