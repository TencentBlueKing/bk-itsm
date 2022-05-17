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
  <div class="bk-logs-info" v-bkloading="{ isLoading: isDataLoading }">
    <!-- 基本信息 -->
    <div class="bk-logs-basic">
      <h3 class="bk-basic-h3">{{ $t('m.systemConfig["基本信息"]') }}</h3>
      <ul>
        <li v-for="(item, index) in basicList" :key="index">
          <span>{{item.name}}：</span>
          <span class="bk-basic-value">{{item.value || '--'}}</span>
        </li>
      </ul>
    </div>
    <!-- json数据 -->
    <div class="bk-logs-basic">
      <h3 class="bk-basic-h3">{{ $t('m.systemConfig["请求参数"]') }}</h3>
      <div class="bk-basic-form">
        <div class="bk-form-content" id="#editorRequest">
          <ace
            :value="requestResponse.request"
            :width="requestResponse.width"
            :height="requestResponse.height"
            :read-only="requestResponse.readOnly"
            :lang="requestResponse.lang"
            :full-screen="requestResponse.fullScreen"
            :theme="'monokai'">
          </ace>
        </div>
      </div>
    </div>
    <!-- json数据 -->
    <div class="bk-logs-basic">
      <h3 class="bk-basic-h3">{{ $t('m.systemConfig["返回结果"]') }}</h3>
      <div class="bk-basic-form">
        <div class="bk-form-content" id="#editorBack">
          <ace
            :value="requestResponse.response"
            :width="requestResponse.width"
            :height="requestResponse.height"
            :read-only="requestResponse.readOnly"
            :lang="requestResponse.lang"
            :full-screen="requestResponse.fullScreen"
            :theme="'monokai'">
          </ace>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { errorHandler } from '../../../utils/errorHandler';
  import ace from '../../commonComponent/aceEditor';

  export default {
    name: 'logsInfo',
    components: {
      ace,
    },
    props: {
      logsObject: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        basicList: [
          { name: this.$t('m.systemConfig["接口地址"]'), value: '', key: 'url' },
          { name: this.$t('m.systemConfig["请求方法"]'), value: '', key: 'method' },
          { name: this.$t('m.systemConfig["状态"]'), value: '', key: 'status_code' },
          { name: this.$t('m.systemConfig["请求时间"]'), value: '', key: 'date_created' },
          { name: this.$t('m.systemConfig["耗时"]'), value: '', key: 'duration' },
          { name: this.$t('m.systemConfig["接口ID"]'), value: '', key: 'api_instance_id' },
          { name: this.$t('m.systemConfig["单据ID"]'), value: '', key: 'ticket_id' },
          { name: this.$t('m.systemConfig["节点ID"]'), value: '', key: 'state_id' },
        ],
        requestResponse: {
          response: '',
          request: '',
          width: '100%',
          height: 300,
          readOnly: true,
          fullScreen: true,
          lang: 'json',
        },
        isDataLoading: false,
      };
    },
    mounted() {
      this.initData();
    },
    methods: {
      initData() {
        this.isDataLoading = true;
        this.$store.dispatch('systemLog/retrive', this.logsObject.id).then((res) => {
          for (let i = 0; i < this.basicList.length; i++) {
            const property = this.basicList[i];
            property.value = res.data[property.key];
          }
          this.requestResponse.request = res.data.request_message;
          this.requestResponse.response = JSON.stringify(res.data.response_message, null, 4);
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
    @import '../../../scss/mixins/clearfix.scss';
    @import '../../../scss/mixins/scroller.scss';

    .bk-logs-basic {
        margin-bottom: 25px;

        ul {
            @include clearfix;
        }

        li {
            float: left;
            width: 50%;
            font-size: 14px;
            line-height: 27px;
            color: #63656E;

            .bk-basic-value {
                color: #313238;
            }
        }

        li:first-child {
            width: 100%;
        }
        .bk-basic-form {
            position: relative;
            border: 1px solid #dfe0e5;
        }
    }

    .bk-basic-h3 {
        margin: 0;
        padding: 0;
        font-size: 14px;
        font-weight: bold;
        color: #63656E;
        line-height: 19px;
        margin-bottom: 10px;
    }
</style>
