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
  <bk-dialog
    width="768"
    ext-cls="permission-dialog"
    :z-index="2010"
    :mask-close="false"
    :header-position="'left'"
    :title="''"
    :value="isModalShow"
    @cancel="onCloseDialog">
    <permission-content :permission-data="permissionData">
    </permission-content>
    <div class="permission-footer" slot="footer">
      <div class="button-group">
        <bk-button theme="primary" :loading="loading" @click="goToApply">{{hasClicked ? $t(`m.common['已申请']`) : $t(`m.common['去申请']`)}}</bk-button>
        <bk-button theme="default" @click="onCloseDialog">{{$t(`m['取消']`)}}</bk-button>
      </div>
    </div>
  </bk-dialog>
</template>
<script>
  import { errorHandler } from '@/utils/errorHandler.js';
  import PermissionContent from '../layout/PermissionContent.vue';
  export default {
    name: 'permissionModal',
    components: {
      PermissionContent,
    },
    data() {
      return {
        isModalShow: false,
        hasClicked: false,
        permissionData: {},
        loading: false,
        lock: require('../../../images/lock-radius.svg'),
      };
    },
    watch: {
      isModalShow(val) {
        if (val) {
          this.loadPermissionUrl();
        }
      },
    },
    methods: {
      async loadPermissionUrl() {
        try {
          this.loading = true;
          const res = await this.$store.dispatch('common/getIamUrl', this.permissionData);
          if (res.result) {
            this.url = res.data.url;
          } else {
            errorHandler(res, this);
          }
        } catch (err) {
          errorHandler(err, this);
        } finally {
          this.loading = false;
        }
      },
      show(data) {
        this.isModalShow = true;
        this.permissionData = data;
      },
      goToApply() {
        if (this.loading) {
          return;
        }
        if (this.hasClicked) {
          window.location.reload();
        } else {
          this.hasClicked = true;
          window.open(this.url, '__blank');
        }
      },
      onCloseDialog() {
        this.isModalShow = false;
      },
    },
  };
</script>
<style lang="scss" scoped>
    .button-group {
        .bk-button {
            margin-left: 7px;
        }
    }

</style>
