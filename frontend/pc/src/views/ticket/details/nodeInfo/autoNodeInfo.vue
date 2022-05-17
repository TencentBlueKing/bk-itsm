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
  <div class="bk-auto-node-content">
    <div class="bk-page bk-auto-node-basic">
      <p class="bk-header-bold">{{ $t('m.newCommon["节点信息"]') }}</p>
      <div class="bk-main bk-flex">
        <div class="bk-base-field">
          <span class="bk-base-label">
            {{ $t('m.newCommon["节点名称"]') }} :
          </span>
          <span>{{ nodeInfo.name || "--" }}</span>
        </div>
        <div class="bk-base-field">
          <span class="bk-base-label">
            {{ $t('m.newCommon["API接口"]') }} :
          </span>
          <span>{{ apiName || "--" }}</span>
        </div>
        <div class="bk-base-field">
          <span class="bk-base-label">
            {{ $t('m.newCommon["处理时间"]') }} :
          </span>
          <span>{{ nodeInfo.update_at || "--" }}</span>
        </div>
      </div>
    </div>
    <div class="bk-page bk-auto-node-basic">
      <p class="bk-header-bold">
        <span class="bk-label">
          {{ $t('m.newCommon["输入参数"]') }}
          <a
            v-bk-tooltips.right="
              $t(`m.newCommon['调用该API传递的参数信息']`)
            "
            class="bk-text-danger mr0"
          >
            <i class="bk-icon icon-question-circle"></i>
          </a>
        </span>
      </p>
      <div>
        <div>
          <!-- get/query/参数 -->
          <div
            class="bk-param"
            v-if="
              nodeInfo.api_info.remote_api_info.req_params &&
                nodeInfo.api_info.remote_api_info.req_params.length
            "
          >
            <get-param
              ref="getParam"
              :query-value="nodeInfo.api_info.req_params"
              :is-static="true"
              :api-detail="nodeInfo.api_info.remote_api_info"
            ></get-param>
          </div>
          <!-- post/body/参数 -->
          <div
            class="bk-param"
            v-if="
              nodeInfo.api_info.remote_api_info.req_body &&
                Object.keys(
                  nodeInfo.api_info.remote_api_info.req_body
                ).length &&
                nodeInfo.api_info.remote_api_info.req_body
                  .properties &&
                Object.keys(
                  nodeInfo.api_info.remote_api_info.req_body
                    .properties
                ).length
            "
          >
            <post-param
              ref="postParam"
              :body-value="nodeInfo.api_info.req_body"
              :is-static="true"
              :api-detail="nodeInfo.api_info.remote_api_info"
            ></post-param>
          </div>
        </div>
      </div>
      <p class="bk-header-bold" style="margin-top: 10px">
        <span class="bk-label">
          {{ $t('m.newCommon["返回变量"]') }}
          <a
            v-bk-tooltips.right="
              $t(`m.newCommon['调用成功后API将会返回的变量信息']`)
            "
            class="bk-text-danger mr0"
          >
            <i class="bk-icon icon-question-circle"></i>
          </a>
        </span>
      </p>
      <template
        v-if="
          nodeInfo.api_info &&
            nodeInfo.api_info.output_variables &&
            nodeInfo.api_info.output_variables.length
        "
      >
        <bk-table
          :data="nodeInfo.api_info.output_variables"
          :size="'small'"
        >
          <bk-table-column
            :label="$t(`m.newCommon['变量名']`)"
            prop="name"
          ></bk-table-column>
          <bk-table-column
            :label="$t(`m.newCommon['变量值']`)"
            prop="value"
          ></bk-table-column>
        </bk-table>
      </template>
      <p
        class="bk-partition bk-selector bk-header-bold"
        :class="{ open: isShowAce }"
        style="margin-top: 10px"
        v-if="!!bodyDetailConfig.value"
      >
        <template v-if="isShowAce">
          <i
            style="cursor: pointer"
            class="bk-icon bk-selector-icon icon-angle-down"
            :class="{ 'icon-angle-down': isShowAce }"
            @click="isShowAce = !isShowAce"
          ></i>
        </template>
        <template v-else>
          <i
            style="cursor: pointer"
            class="bk-icon icon-angle-right bk-selector-icon"
            @click="isShowAce = !isShowAce"
          ></i>
        </template>
        <span class="bk-label">
          {{ $t('m.newCommon["接口返回"]') }}
          <a
            v-bk-tooltips.right="
              $t(`m.newCommon['调用成功后API将会返回的数据信息']`)
            "
            class="bk-text-danger mr0"
          >
            <i class="bk-icon icon-question-circle"></i>
          </a>
        </span>
      </p>
      <div class="bk-ace" v-if="isShowAce">
        <div class="bk-ace-full">
          <span class="bk-font-icon" @click="isFull = !isFull">
            <i class="bk-itsm-icon icon-icon-full-srceen"></i>
            <!-- 全屏 -->
          </span>
        </div>
        <div>
          <ace
            :value="bodyDetailConfig.value"
            :width="bodyDetailConfig.width"
            :height="bodyDetailConfig.height"
            :read-only="bodyDetailConfig.readOnly"
            :lang="bodyDetailConfig.lang"
            :full-screen="bodyDetailConfig.fullScreen"
            :theme="'textmate'"
            @blur="blur"
            @init="editorInitAfter"
          ></ace>
        </div>
        <div class="bk-ace-full-screen" v-if="isFull">
          <div
            class="bk-ace-full-change"
            style="width: 100%; height: 45px"
          >
            <span>{{ $t('m.newCommon["接口返回"]') }}</span>
            <span class="bk-font-icon" @click="isFull = !isFull">
              <i class="bk-itsm-icon icon-icon-back-full"></i>
              <!-- 小屏 -->
            </span>
          </div>
          <div style="width: 100%; height: calc(100% - 45px)">
            <ace
              :value="bodyDetailConfig.value"
              :width="'100%'"
              :height="'100%'"
              :read-only="bodyDetailConfig.readOnly"
              :lang="bodyDetailConfig.lang"
              :full-screen="bodyDetailConfig.fullScreen"
              :theme="'textmate'"
              @blur="blur"
              @init="editorInitAfter"
            ></ace>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import getParam from '@/views/processManagement/processDesign/nodeConfigue/addField/getParam.vue';
  import postParam from '@/views/processManagement/processDesign/nodeConfigue/addField/postParam.vue';
  import ace from '@/views/commonComponent/aceEditor';

  export default {
    name: 'autoNodeInfo',
    components: {
      getParam,
      postParam,
      ace,
    },
    props: {
      nodeInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      // 自动节点信息
      apiInfo: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        // 返回数据 -- ace编辑器展示
        bodyDetailConfig: {
          value: '',
          width: '100%',
          height: 200,
          readOnly: true,
          fullScreen: true,
          lang: 'json',
        },
        isShowAce: false,
        isFull: false,
      };
    },
    computed: {
      // 拼接/接口名
      apiName() {
        const remoteSystem =                this.nodeInfo.api_info.remote_api_info.remote_system_name || '';
        const remoteApi = this.nodeInfo.api_info.remote_api_info.name || '';
        return `${remoteSystem}/${remoteApi}`;
      },
    },
    async mounted() {
      await this.nodeInfo;
      if (this.nodeInfo && Object.keys(this.bodyDetailConfig.value).length) {
        this.bodyDetailConfig.value = JSON.stringify(
          this.nodeInfo.api_info.response,
          null,
          4
        );
      }
    },
    methods: {
      editorInitAfter() {
        // ...
      },
      blur(content) {
        this.bodyDetailConfig.value = content;
      },
    },
  };
</script>

<style scoped lang="scss">
@import "../../../../scss/mixins/clearfix.scss";
@import "../../../../scss/mixins/scroller.scss";
/* 表格样式 */
.bk-auto-node-content {
    font-size: 14px;
    color: #63656e;

    .bk-header-bold {
        font-weight: bold;
        padding: 10px 0;

        .icon-question-circle {
            color: #000000;
        }
    }
}

.bk-page {
    display: block;
    height: auto;

    .bk-flex {
        display: flex;
        // align-items: center;
        flex-wrap: wrap;

        & > div {
            width: 50%;
            line-height: 2;
        }
    }

    .bk-partition {
        padding: 10px 0;

        .bk-selector-icon {
            left: 0px;
            right: unset;
        }

        .bk-selector.open .bk-selector-icon {
            transform: rotate(-180deg);
        }

        .icon-angle-down,
        .icon-angle-right {
            font-size: 22px;
        }
    }
}

.bk-ace {
    position: relative;

    .bk-ace-full {
        z-index: 1;
        top: 10px;
        right: 10px;
        position: absolute;
    }

    .bk-ace-full-change {
        color: #000000;
        font-size: 16px;
        background: white;
        border-bottom: 1px solid #dde4eb;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 16px;
    }

    .bk-ace-full-screen {
        position: fixed;
        z-index: 10;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
    }
}

.bk-font-icon {
    font-size: 16px;
    float: right;
    color: #979ba5;
    cursor: pointer;
    position: relative;
    margin-right: 0;
    width: 28px;
    height: 28px;
    background: rgba(240, 241, 245, 1);
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;

    .icon-icon-full-srceen,
    .icon-icon-back-full {
        color: #aaadb6;

        &:hover {
            color: #63656e;
        }
    }
}
.bk-base-field {
    line-height: 27px;
    font-size: 12px;
    .bk-base-label {
        font-weight: bold;
    }
}
</style>
