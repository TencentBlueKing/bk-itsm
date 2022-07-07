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
  <div class="bk-api-content">
    <div class="is-title-back">
      <p class="bk-come-back" @click="backTab">
        <arrows-left-icon></arrows-left-icon>
        <template>{{ backName }}</template>
      </p>
    </div>
    <div class="itsm-page-content">
      <div class="bk-api-ul">
        <ul>
          <li v-for="(item, index) in titleList"
            :key="index"
            :class="{ 'bk-api-check': checkIndex === index }"
            @click="changTitle(item, index)">
            <span>{{item.name}}</span>
          </li>
        </ul>
      </div>
      <div class="bk-api-info">
        <api-basic
          :api-detail-info="apiDetailInfo"
          v-if="checkIndex === 0">
        </api-basic>
        <api-editor
          :api-detail-info-common="apiDetailInfoCommon"
          :tree-list="treeList"
          :path-list="pathList"
          :is-builtin-id-list="isBuiltinIdList"
          v-if="checkIndex === 1">
        </api-editor>
        <api-run
          :api-detail-info-common="apiDetailInfoCommon"
          v-if="checkIndex === 2">
        </api-run>
      </div>
    </div>
  </div>
</template>

<script>
  import apiBasic from './components/apiBasic.vue';
  import apiEditor from './components/apiEditor.vue';
  import apiRun from './components/apiRun.vue';

  export default {
    name: 'apiContent',
    components: {
      apiBasic,
      apiEditor,
      apiRun,
    },
    props: {
      apiDetailInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      treeList: {
        type: Array,
        default() {
          return [];
        },
      },
      pathList: {
        type: Array,
        default() {
          return [];
        },
      },
      isBuiltinIdList: {
        type: Array,
        default() {
          return [];
        },
      },
      secondLevelInfo: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        apiDetailInfoCommon: this.apiDetailInfo,
        // tag
        titleList: [
          { name: this.$t('m.systemConfig["预览"]') },
          { name: this.$t('m.systemConfig["编辑"]') },
          { name: this.$t('m.systemConfig["运行"]') },
        ],
        checkIndex: 1,
      };
    },
    computed: {
      backName() {
        return this.secondLevelInfo.name;
      },
    },
    watch: {
      apiDetailInfo(newVal) {
        this.apiDetailInfoCommon = JSON.parse(JSON.stringify(newVal));
        this.initData();
      },
    },
    mounted() {
      this.initData();
    },
    methods: {
      backTab() {
        this.$parent.displayInfo.level_1 = {};
      },
      changTitle(item, index) {
        this.checkIndex = index;
      },
      initData() {
        if (this.apiDetailInfoCommon.req_headers) {
          if (!this.apiDetailInfoCommon.req_headers.length) {
            this.apiDetailInfoCommon.req_headers = [
              {
                name: '',
                value: '',
                sample: '',
                desc: '',
              },
            ];
          }
          if (!this.apiDetailInfoCommon.req_params.length) {
            this.apiDetailInfoCommon.req_params = [
              {
                name: '',
                is_necessary: 0,
                sample: '',
                desc: '',
                value: '',
              },
            ];
          }
        }
      },
    },
  };
</script>

<style lang="scss" scoped>
    @import '../../../scss/mixins/clearfix.scss';
    @import '../../../scss/mixins/scroller.scss';

    .bk-api-content {
        padding: 0px 10px 60px 10px;
        height: 100%;
    }

    .bk-api-ul {
        ul {
            @include clearfix;
        }

        li {
            float: left;
            padding: 0 12px;
            line-height: 50px;
            color: #737987;
            font-size: 14px;
            cursor: pointer;
        }

        .bk-api-check {
            border-bottom: 2px solid #3c96ff;
            color: #3c96ff;
        }
    }

    .bk-api-info {
        width: 100%;
        height: calc(100% - 52px);
        overflow: auto;
        @include scroller;
        padding: 0 10px;
    }

    .is-title-back {
        padding: 10px;
        padding-bottom: 0px;
        font-size: 16px;
        color: #737987;
        cursor: pointer;

        i {
            color: #3c96ff;
            font-weight: bold;
        }
    }
</style>
