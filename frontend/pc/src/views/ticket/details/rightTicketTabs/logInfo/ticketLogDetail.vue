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
  <div>
    <bk-sideslider
      :width="600"
      :is-show="show"
      :quick-close="true"
      :before-close="
        () => {
          $emit('close');
        }
      "
    >
      <template v-if="logInfo">
        <div slot="header">
          {{ logInfo.from_state_name || logInfo.message }}
        </div>
        <div class="p20" slot="content">
          <div class="bk-timeline-user-content">
            <div class="bk-area-show-back">
              <!-- 基础信息 -->
              <div class="bk-logs-basic">
                <h3 class="bk-basic-h3">
                  {{ $t('m.newCommon["基本信息"]') }}
                </h3>
                <ul>
                  <li
                    v-for="(baseItem, index) in basicList"
                    :key="index"
                  >
                    <span class="bk-basic-title"
                    >{{ baseItem.name }}：</span
                    >
                    <span
                      class="bk-basic-value"
                      :title="logInfo[baseItem.key]"
                    >{{
                      logInfo[baseItem.key] || "--"
                    }}</span
                    >
                  </li>
                </ul>
              </div>
              <!-- 节点信息 -->
              <template v-if="logInfo.form_data.length">
                <!-- 普通节点 -->
                <template
                  v-if="logInfo.from_state_type === 'NORMAL'"
                >
                  <h3 class="bk-basic-h3">
                    {{ $t('m.newCommon["节点信息"]') }}
                  </h3>
                  <field-preview
                    :comment-id="'fields-view'"
                    :fields="logInfo.form_data"
                    :ticket-id="logInfo.ticket_id"
                    :stated-id="logInfo.id"
                  >
                  </field-preview>
                </template>
                <!-- 标准运维节点 -->
                <sops-node-log
                  v-else-if="
                    logInfo.from_state_type === 'TASK-SOPS'
                  "
                  :sops-info="logInfo.form_data[0].value"
                >
                </sops-node-log>
                <devops-node-log
                  v-else-if="
                    logInfo.from_state_type ===
                      'TASK-DEVOPS'
                  "
                  :node-info="logInfo.form_data[0].value"
                >
                </devops-node-log>
                <!-- api 节点 -->
                <auto-node-info
                  v-else-if="
                    logInfo.from_state_type === 'TASK'
                  "
                  :node-info="{
                    api_info: logInfo.form_data[0].value,
                    name: logInfo.from_state_name,
                    update_at: logInfo.operate_at
                  }"
                >
                </auto-node-info>
                <template v-else>
                  <h3 class="bk-basic-h3">
                    {{ $t('m.newCommon["节点信息"]') }}
                  </h3>
                  <template
                    v-for="(ite, inde) in logInfo.form_data"
                  >
                    <fields-done
                      :key="inde"
                      :item="ite"
                      :origin="'log'"
                    >
                    </fields-done>
                  </template>
                </template>
              </template>
              <!-- 日志详情 -->
              <h3 class="bk-basic-h3 mt25 mb20">
                {{ $t('m.systemConfig["日志详情"]') }}
              </h3>
              <p class="opt-info">{{ logInfo.message }}</p>
            </div>
          </div>
        </div>
      </template>
    </bk-sideslider>
  </div>
</template>

<script>
  import fieldsDone from '../../components/fieldsDone.vue';
  import autoNodeInfo from '../../nodeInfo/autoNodeInfo.vue';
  import sopsNodeLog from './sopsNodeLog.vue';
  import devopsNodeLog from './devopsNodeLog.vue';
  import fieldPreview from '@/views/commonComponent/fieldPreview/index.vue';

  export default {
    name: 'ticketLogDetail',
    components: {
      fieldsDone,
      autoNodeInfo,
      sopsNodeLog,
      fieldPreview,
      devopsNodeLog,
    },
    props: {
      show: {
        type: Boolean,
        default: false,
      },
      logInfo: {
        type: Object,
        default: () => null,
      },
    },
    data() {
      return {
        basicList: [
          {
            name: this.$t('m.newCommon["节点名称"]'),
            value: '',
            key: 'from_state_name',
          },
          {
            name: this.$t('m.newCommon["处理人"]'),
            value: '',
            key: 'operator',
          },
          {
            name: this.$t('m.newCommon["处理时间"]'),
            value: '',
            key: 'operate_at',
          },
        ],
      };
    },
  };
</script>

<style lang="scss" scoped>
@import "../../../../../scss/mixins/clearfix.scss";
.bk-timeline-user-content {
    font-size: 12px;
    .bk-area-show-back {
        padding: 4px 8px;
        .opt-info {
            color: #63656e;
        }
    }
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
            color: #63656e;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
            font-size: 12px;
            .bk-basic-title {
                display: inline-block;
                min-width: 70px;
                font-weight: bold;
            }
        }

        li:first-child {
            width: 100%;
        }
    }
}
.bk-basic-h3 {
    color: #63656e;
}
</style>
