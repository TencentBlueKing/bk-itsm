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
  <div class="permisson-apply">
    <div class="apply-content">
      <permission-content :permission-data="permissionData.permission">
      </permission-content>
      <div class="operation-btns">
        <bk-button
          ext-cls="apply-btn"
          theme="primary"
          :loading="loading"
          @click="applyBtnClick">
          {{hasClicked ? $t(`m.common['已申请']`) : $t(`m.common['去申请']`)}}
        </bk-button>
      </div>
    </div>
  </div>
</template>
<script>
  import PermissionContent from './PermissionContent.vue';
  import permission from '@/mixins/permission.js';
  import _ from 'lodash';
  import { errorHandler } from '@/utils/errorHandler.js';

  export default {
    name: 'PermissionApply',
    components: {
      PermissionContent,
    },
    mixins: [permission],
    props: {
      permissionData: {
        type: Object,
        default() {
          return {
            type: 'project', // 无权限类型: project、other
            permission: null,
          };
        },
      },
    },
    data() {
      return {
        url: '',
        loading: false,
        hasClicked: false,
        authActions: [],
      };
    },
    watch: {
      permissionData: {
        deep: true,
        immediate: true,
        handler(val, oldVal) {
          if (!_.isEqual(val, oldVal)) {
            this.loadPermissionUrl();
          }
        },
      },
    },
    created() {
      if (this.permissionData.permission) {
        this.loadPermissionUrl();
      }
    },
    methods: {
      applyBtnClick() {
        this.goToAuthCenter();
      },
      goToAuthCenter() {
        if (this.loading || !this.url) {
          return;
        }
        if (this.hasClicked) {
          window.location.reload();
        } else {
          this.hasClicked = true;
          window.open(this.url, '__blank');
        }
      },
      async loadPermissionUrl() {
        try {
          this.loading = true;
          const res = await this.$store.dispatch('common/getIamUrl', this.permissionData.permission);
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
    },
  };
</script>
<style lang="scss" scoped>
    .permisson-apply {
        width: 100%;
        height: 100%;
    }
    .apply-content {
        position: absolute;
        top: calc(50% - 60px);
        left: 50%;
        right: 0;
        width: 620px;
        text-align: center;
        transform: translate(-50% ,-50%);
        .operation-btns {
            margin-top: 20px;
            .apply-btn {
                width: 124px;
            }
        }
        & > h3 {
            margin: 0 0 30px;
            color: #313238;
            font-size: 20px;
        }
        & > p {
            margin: 0 0 30px;
            color: #979ba5;
            font-size: 14px;
        }
        .bk-button {
            height: 32px;
            line-height: 30px;
        }
    }
</style>
