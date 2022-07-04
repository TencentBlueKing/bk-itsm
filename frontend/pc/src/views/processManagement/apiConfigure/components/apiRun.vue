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
  <div class="bk-api-run">
    <div class="bk-basic-item mt20">
      <div class="bk-service-name">
        <h1><span class="is-outline"></span>{{ $t('m.systemConfig["配置"]') }}</h1>
      </div>
      <div class="bk-basic-content">
        <api-run-config
          ref="apiRunConfig"
          :api-detail-info-common="apiDetailInfoCommon">
        </api-run-config>
      </div>
    </div>
    <div class="bk-basic-item mt20">
      <div class="bk-service-name">
        <h1><span class="is-outline"></span>{{ $t('m.systemConfig["请求数据加工"]') }}</h1>
      </div>
      <div class="bk-basic-content" style="position: relative;">
        <ace
          :value="reqDataProcess.value"
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
      <div class="bk-basic-content" style="position: relative;">
        <ace
          :value="dataProcess.value"
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
        <h1><span class="is-outline"></span>Response</h1>
      </div>
      <div class="bk-basic-content" style="position: relative;">
        <div id="#editor">
          <ace
            :value="alarmDetailConfig.value"
            :width="alarmDetailConfig.width"
            :height="alarmDetailConfig.height"
            :read-only="alarmDetailConfig.readOnly"
            :lang="alarmDetailConfig.lang"
            :full-screen="alarmDetailConfig.fullScreen"
            :theme="'monokai'"
            @init="editorInitAfter">
          </ace>
        </div>
      </div>
    </div>
    <div class="bk-basic-btn" v-if="!apiDetailInfoCommon.is_builtin">
      <bk-button :disabled="isSuccess"
        @click="updateApi"
        data-test-id="apiDetail_button_runUpdateApi"
        :theme="'primary'"
        :title="$t(`m.systemConfig['保存参数']`)">
        {{$t(`m.systemConfig['保存参数']`)}}
      </bk-button>
    </div>
  </div>
</template>

<script>
  import apiRunConfig from './apiRunConfig.vue';
  import ace from '../../../commonComponent/aceEditor/index.js';
  import mixins from '../../../commonMix/mixins_api.js';
  import { errorHandler } from '../../../../utils/errorHandler';

  export default {
    components: {
      apiRunConfig,
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
    },
    data() {
      return {
        alarmDetailConfig: {
          value: '',
          width: '100%',
          height: 300,
          readOnly: true,
          fullScreen: true,
          lang: 'json',
        },
        reqDataProcess: {
          value: '',
          width: '100%',
          height: 300,
          fullScreen: true,
          lang: 'python',
        },
        dataProcess: {
          value: '',
          width: '100%',
          height: 300,
          fullScreen: true,
          lang: 'python',
        },
        // 是否执行成功
        isSuccess: true,
      };
    },
    computed: {},
    watch: {},
    mounted() {
      // this.initDate()
    },
    methods: {
      getRemoteApiDetail(id) {
        this.$parent.$parent.getRemoteApiDetail(id);
      },
      changBlur(val) {
        this.dataProcess.value = val;
      },
      reqChangBlur(val) {
        this.reqDataProcess.value = val;
      },
      editorInitAfter() {
      },
      async updateApi() {
        if (this.secondClick || !this.apiDetailInfoCommon.treeDataList || !this.apiDetailInfoCommon.responseTreeDataList) {
          return;
        }
        try {
          // 2.重置数据 参数和返回数据统一
          const resData = JSON.parse(this.alarmDetailConfig.value);
          this.apiDetailInfoCommon.bodyJsonschemaData = this.jsonToJsonschema(JSON.parse(this.$refs.apiRunConfig.bodyDetailConfig.value));
          this.apiDetailInfoCommon.resJsonschemaData = this.jsonToJsonschema(resData || {});
        } catch (err) {
          this.$bkMessage({
            message: err.message ? err.message : err,
            theme: 'error',
          });
          return;
        }
        // body Jsonschema数据结构
        this.apiDetailInfoCommon.req_body = this.apiDetailInfoCommon.bodyJsonschemaData.root; // root初始 Jsonschema数据结构
        // response Jsonschema数据结构
        this.apiDetailInfoCommon.rsp_data = this.apiDetailInfoCommon.resJsonschemaData.root; // root初始 Jsonschema数据结构
        // 删除多重数据
        await delete this.apiDetailInfoCommon.treeDataList;
        await delete this.apiDetailInfoCommon.responseTreeDataList;

        const params = this.apiDetailInfoCommon;
        if (params.req_body.required.length === 0) {
          delete params.req_body.required;
        }
        params.map_code = this.dataProcess.value;
        params.before_req = this.reqDataProcess.value;
        this.secondClick = true;
        await this.$store.dispatch('apiRemote/put_remote_api', params).then(() => {
          this.$bkMessage({
            message: this.$t('m.systemConfig["更新成功"]'),
            theme: 'success',
          });
          this.getRemoteApiDetail(this.apiDetailInfoCommon.id);
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.secondClick = false;
          });
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

    #editor {
        position: absolute;
        top: 0;
        right: 0;
        width: 100%;
        height: 100%;
    }

    .bk-api-run {
        .bk-form-content {
            margin-left: 0px;
        }
    }

    .bk-basic-btn {
        position: absolute;
        bottom: 0;
        left: 0;
        text-align: center;
        width: 100%;
        height: 50px;
        line-height: 50px;
        background-color: #fff;
        z-index: 10;
    }
</style>
