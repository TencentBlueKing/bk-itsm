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
  <div class="bk-api-editor">
    <div class="bk-basic-item mt20">
      <div class="bk-service-name">
        <h1><span class="is-outline"></span>{{ $t('m.systemConfig["基本设置"]') }}</h1>
      </div>
      <div class="bk-basic-content">
        <api-editor-basic ref="apiEditorBasic"
          :detail-info-ori="DetailInfo"
          :tree-list="treeList"
          :path-list="pathList"
          :is-builtin-id-list="isBuiltinIdList"
          @changeRequest="changeRequest">
        </api-editor-basic>
      </div>
    </div>
    <div class="bk-basic-item mt20">
      <div class="bk-service-name">
        <h1><span class="is-outline"></span>{{ $t('m.systemConfig["请求参数"]') }}</h1>
      </div>
      <div class="bk-basic-content">
        <api-editor-request
          :detail-info-ori="DetailInfo">
        </api-editor-request>
      </div>
    </div>
    <div class="bk-basic-item mt20">
      <div class="bk-service-name">
        <h1><span class="is-outline"></span>{{ $t('m.systemConfig["请求数据加工"]') }}</h1>
      </div>
      <div class="bk-basic-content">
        <ace
          :value="DetailInfo.before_req"
          :width="dataProcess.width"
          :height="dataProcess.height"
          :lang="dataProcess.lang"
          :full-screen="dataProcess.fullScreen"
          :theme="'monokai'"
          @blur="reqChangBlur">
        </ace>
      </div>
    </div>
    <div class="bk-basic-item mt20">
      <div class="bk-service-name">
        <h1><span class="is-outline"></span>{{ $t('m.systemConfig["返回数据加工"]') }}</h1>
      </div>
      <div class="bk-basic-content">
        <ace
          :value="DetailInfo.map_code"
          :width="dataProcess.width"
          :height="dataProcess.height"
          :lang="dataProcess.lang"
          :full-screen="dataProcess.fullScreen"
          :theme="'monokai'"
          @blur="changBlur">
        </ace>
      </div>
    </div>
    <div class="bk-basic-item mt20">
      <div class="bk-service-name">
        <h1><span class="is-outline"></span>{{ $t('m.systemConfig["返回结果"]') }}</h1>
      </div>
      <div class="bk-basic-content">
        <api-editor-result
          :detail-info-ori="DetailInfo">
        </api-editor-result>
      </div>
    </div>
    <div class="bk-basic-item mt20">
      <div class="bk-service-name">
        <h1><span class="is-outline"></span>{{ $t('m.systemConfig["其他"]') }}</h1>
      </div>
      <div class="bk-basic-content">
        <api-editor-others
          :detail-info-ori="DetailInfo">
        </api-editor-others>
      </div>
    </div>
    <div class="bk-basic-btn" v-if="!DetailInfo.is_builtin">
      <bk-button
        :theme="'primary'"
        data-test-id="apiDetail_button_editUpdateApi"
        :title="$t(`m.systemConfig['保存']`)"
        @click="updateApi">
        {{$t(`m.systemConfig['保存']`)}}
      </bk-button>
    </div>
  </div>
</template>

<script>
  import ace from '../../../commonComponent/aceEditor/index.js';
  import mixins from '../../../commonMix/mixins_api.js';
  import apiEditorBasic from './apiEditorBasic.vue';
  import apiEditorRequest from './apiEditorRequest.vue';
  import apiEditorResult from './apiEditorResult.vue';
  import apiEditorOthers from './apiEditorOthers.vue';
  import { errorHandler } from '../../../../utils/errorHandler.js';

  export default {
    components: {
      apiEditorBasic,
      apiEditorRequest,
      apiEditorResult,
      apiEditorOthers,
      ace,
    },
    mixins: [mixins],
    props: {
      apiDetailInfoCommon: {
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
    },
    data() {
      return {
        secondClick: false,
        dataProcess: {
          width: '100%',
          height: 300,
          fullScreen: true,
          lang: 'python',
        },
      };
    },
    computed: {
      // 基本设置
      DetailInfo: {
        // getter
        get() {
          return this.apiDetailInfoCommon;
        },
        // setter
        set(newVal) {
          this.$parent.apiDetailInfoCommon = newVal;
        },
      },
    },
    watch: {
      // apiDetailInfoCommon(newVal, oldVal){
      //     this.DetailInfo = JSON.parse(JSON.stringify(newVal))
      // },
      // DetailInfo: {
      //     handler: function (newVal, oldVal) {
      //         console.info('value changed ', newVal)
      //     },
      //     deep: true
      // }
    },
    mounted() {
    },
    methods: {
      changBlur(val) {
        this.DetailInfo.map_code = val;
      },
      reqChangBlur(val) {
        this.DetailInfo.before_req = val;
      },
      getRemoteApiDetail(id) {
        this.$parent.$parent.getRemoteApiDetail(id);
      },
      async updateApi() {
        if (this.secondClick || !this.DetailInfo.treeDataList || !this.DetailInfo.responseTreeDataList) {
          return;
        }
        this.DetailInfo.req_headers = this.DetailInfo.req_headers.filter(item => !!item.name);
        this.DetailInfo.req_params = this.DetailInfo.req_params.filter(item => !!item.name);
        // body Jsonschema数据结构
        const rootdata = await this.listToJsonschema(this.DetailInfo.treeDataList);
        this.DetailInfo.req_body = await rootdata.root; // root初始 Jsonschema数据结构

        // response Jsonschema数据结构
        const responseRootdata = await this.listToJsonschema(this.DetailInfo.responseTreeDataList);
        this.DetailInfo.rsp_data = await responseRootdata.root; // root初始 Jsonschema数据结构
        this.DetailInfo.owners = this.DetailInfo.ownersInputValue.join(',');
        delete this.DetailInfo.ownersInputValue;
        await delete this.DetailInfo.treeDataList;
        await delete this.DetailInfo.responseTreeDataList;

        const params = this.DetailInfo;
        this.secondClick = true;
        await this.$store.dispatch('apiRemote/put_remote_api', params).then(() => {
          this.$bkMessage({
            message: this.$t('m.systemConfig["更新成功"]'),
            theme: 'success',
          });
          this.getRemoteApiDetail(this.DetailInfo.id);
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.secondClick = false;
          });
      },
      // 切换接口类型，改变请求参数数据
      changeRequest(val) {
        if (val === 'POST') {
          // 如果this.DetailInfo.req_params的数据存在值时弹出提示清空
          if (this.DetailInfo.req_params && this.DetailInfo.req_params.length && this.DetailInfo.req_params.some(item => (item.name || item.sample !== ''))) {
            this.$bkInfo({
              type: 'warning',
              title: this.$t('m.systemConfig[\'此操作将清空请求参数\']'),
              confirmFn: () => {
                this.DetailInfo.req_params = [{
                  name: '',
                  is_necessary: 0,
                  sample: '',
                  desc: '',
                  value: '',
                }];
                this.$refs.apiEditorBasic.changeMethod(val);
              },
            });
          } else {
            this.$refs.apiEditorBasic.changeMethod(val);
          }
        } else {
          if (this.DetailInfo.treeDataList[0].children && this.DetailInfo.treeDataList[0].children.length) {
            this.$bkInfo({
              type: 'warning',
              title: this.$t('m.systemConfig[\'此操作将清空请求参数\']'),
              confirmFn: () => {
                this.DetailInfo.treeDataList[0].children = [];
                this.$refs.apiEditorBasic.changeMethod(val);
              },
            });
          } else {
            this.$refs.apiEditorBasic.changeMethod(val);
          }
        }
      },
    },
  };
</script>

<style lang="scss" scoped>

    .bk-basic-item {
        padding-bottom: 20px;
        border-bottom: 1px solid #E9EDF1;
        margin-bottom: 20px;
    }
    .bk-basic-content {
        padding: 0 20px;
    }
    .bk-basic-btn {
        position: absolute;
        bottom: 0;
        left: 0;
        text-align: center;
        width: 100%;
        height: 50px;
        background-color: #fff;
        z-index: 10;
        line-height: 50px;
    }
</style>
