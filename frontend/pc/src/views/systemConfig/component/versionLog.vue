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
  <div class="versionLog">
    <bk-table
      v-bkloading="{ isLoading: isDataLoading }"
      :data="versionData"
      :size="'small'">
      <bk-table-column :label="$t(`m.home['旧版本']`)" prop="version_from"></bk-table-column>
      <bk-table-column :label="$t(`m.home['新版本']`)" prop="version_to"></bk-table-column>
      <bk-table-column :label="$t(`m.home['升级人']`)" prop="operator"></bk-table-column>
      <bk-table-column :label="$t(`m.home['时间']`)" prop="create_at"></bk-table-column>
      <bk-table-column :label="$t(`m.home['备注']`)" prop="note"></bk-table-column>
    </bk-table>
    <div style="margin-top: 20px">
      <bk-button
        theme="default"
        :title="$t(`m.home['取消']`)"
        class="mr10"
        @click="versionLogData.show = false">
        {{ $t('m.home["取消"]') }}
      </bk-button>
    </div>
  </div>
</template>

<script>
  import { errorHandler } from '../../../utils/errorHandler';
  export default {
    name: 'versionLog',
    props: {
      versionLogData: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        versionData: [],
        isDataLoading: false,
      };
    },
    mounted() {
      this.getHistory();
    },
    methods: {
      getHistory() {
        this.isDataLoading = true;
        this.$store.dispatch('version/updateHistory').then((res) => {
          this.versionData = res.data.data;
          this.versionData.forEach((item) => {
            if (item.version_from) {
              item.version_from = `V${item.version_from}`;
            }
            if (item.version_to) {
              item.version_to = `V${item.version_to}`;
            }
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
      },
    },
  };
</script>

<style lang="scss" scoped>

</style>
