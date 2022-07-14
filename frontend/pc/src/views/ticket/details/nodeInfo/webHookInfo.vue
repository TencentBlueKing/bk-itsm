<template>
  <div class="bk-webhook-node-content">
    <div class="bk-page bk-auto-node-basic">
      <p class="bk-header-bold">{{ $t('m.newCommon["基本信息"]') }}</p>
      <div class="bk-main bk-flex">
        <div class="bk-node-name">
          <span>{{ $t('m.newCommon["节点名称"]') }} : </span>
          <span>{{nodeInfo.name || '--'}}</span>
        </div>
      </div>
    </div>
    <div class="bk-page bk-auto-node-basic">
      <p class="bk-header-bold">{{ $t('m.newCommon["任务参数"]') }}</p>
      <div class="bk-param">
        <p class="bk-partition">
          <b class="bk-base-label">Url:</b>
          <span>{{nodeInfo.api_info.webhook_info.url || '--'}}</span>
        </p>
        <p class="bk-partition">
          <b class="bk-base-label">Method:</b>
          <span>{{nodeInfo.api_info.webhook_info.method || '--'}}</span>
        </p>
        <!-- params -->
        <p class="bk-partition">
          <b class="bk-base-label">Query:</b>
          <span v-if="queryList.length === 0">--</span>
        </p>
        <bk-table
          v-if="queryList.length !== 0"
          :data="queryList"
          :ext-cls="'bk-editor-table'">
          <bk-table-column :label="$t(`m.treeinfo['字段名']`)" prop="key"></bk-table-column>
          <bk-table-column :label="$t(`m.treeinfo['参数值']`)" width="400">
            <template slot-scope="props">
              <span>{{props.row.value || '--'}}</span>
            </template>
          </bk-table-column>
        </bk-table>
        <!-- body -->
        <p class="bk-partition">
          <b class="bk-base-label">Body:</b>
          <span>{{ bodyParams.raw || '--' }}</span>
        </p>
        <bk-table
          v-if="bodyParams.form.length !== 0"
          :data="bodyParams.form"
          :ext-cls="'bk-editor-table'">
          <bk-table-column :label="$t(`m.treeinfo['字段名']`)" prop="key"></bk-table-column>
          <bk-table-column :label="$t(`m.treeinfo['参数值']`)" width="400">
            <template slot-scope="props">
              <span>{{props.row.value || '--'}}</span>
            </template>
          </bk-table-column>
        </bk-table>
        <!-- settings -->
        <p class="bk-partition">
          <b class="bk-base-label">Settings:</b>
        </p>
        <p class="bk-partition">
          <b class="bk-base-label">{{$t(`m.treeinfo['请求超时']`)}}:</b>
          <span>{{nodeInfo.api_info.webhook_info.timeout || '--'}}</span>
        </p>
        <p class="bk-partition">
          <b class="bk-base-label">{{$t(`m.treeinfo['返回变量']`)}}:</b>
          <span v-if="variableList.length === 0">--</span>
        </p>
        <bk-table
          v-if="variableList.length !== 0"
          :data="variableList"
          :ext-cls="'bk-editor-table'">
          <bk-table-column :label="$t(`m.treeinfo['字段名']`)" prop="name"></bk-table-column>
          <bk-table-column :label="$t(`m.treeinfo['参数值']`)">
            <template slot-scope="props">
              <span>{{ convertValue(props.row.value) }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.treeinfo['路径']`)" prop="ref_path"></bk-table-column>
        </bk-table>
      </div>
    </div>
    <div class="bk-page bk-auto-node-basic">
      <p class="bk-header-bold">{{ $t('m.taskTemplate["执行详情"]') }}</p>
      <div>
        <p class="bk-partition">
          <b class="bk-base-label">{{ $t('m.taskTemplate["执行状态："]') }}</b>
          <span
            :class="{
              'statusShow': true,
              'statusSuccess': status === 'FINISHED',
              'statusRunning': status === 'RUNNING',
              'statusFailed': status === 'FAILED' }">
            {{status || '--'}}</span>
        </p>
        <p class="bk-partition">
          <b class="bk-base-label">{{ $t('m.common["开始时间："]') }}</b>
          <span>{{nodeInfo.create_at}}</span>
        </p>
        <p class="bk-partition">
          <b class="bk-base-label">{{ $t('m.common["结束时间："]') }}</b>
          <span>{{ nodeInfo.end_at || $t('m.taskTemplate["尚未结束"]') }}
          </span>
        </p>
        <div class="bk-partition errorDiv">
          <b class="bk-base-label">{{ $t('m.taskTemplate["错误信息："]') }}</b>
        </div>
        <div class="langError">{{nodeInfo.api_info.error_message || '--'}}</div>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'webHookInfo',
    props: {
      nodeInfo: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        status: '',
        isFormData: false,
      };
    },
    computed: {
      queryList() {
        if ('query_params' in this.nodeInfo.api_info.webhook_info) {
          const list = this.nodeInfo.api_info.webhook_info.query_params;
          const result = [];
          for (const key in list) {
            result.push({
              key,
              value: list[key],
            });
          }
          return result;
        }
        return [];
      },
      bodyParams() {
        const params = {
          raw: '',
          form: [],
        };
        if ('body' in this.nodeInfo.api_info.webhook_info) {
          const { body } = this.nodeInfo.api_info.webhook_info;
          if (typeof body === 'string') {
            params.raw = body;
          }
        }
        return { ...params };
      },
      variableList() {
        if ('variables' in this.nodeInfo.api_info) {
          if (Object.keys(this.nodeInfo.api_info.variables).length !== 0) {
            return this.nodeInfo.api_info.variables;
          }
          // const { outputs } = this.nodeInfo.api_info.webhook_info.variables
          return [];
        }
        return [];
      },
    },
    mounted() {
      this.status = this.nodeInfo.status;
    },
    methods: {
      convertValue(value) {
        if (value === null) {
          return '--';
        }
        return JSON.stringify(value);
      },
    },
  };
</script>

<style scoped lang='scss'>
    @import '../../../../scss/mixins/clearfix.scss';
    @import '../../../../scss/mixins/scroller.scss';
    
    .bk-webhook-node-content {
        font-size: 14px;
        color: #63656E;

        .bk-header-bold {
            font-weight: bold;
            padding: 10px 0;
        }
    }

    .bk-page {
        display: block;
        height: auto;
        margin-bottom: 10px;

        .bk-flex {
            display: flex;
            // align-items: center;
            flex-wrap: wrap;

            & > div {
                width: 50%;
                line-height: 2;
            }
        }

        .errorDiv {
            display: inline-block;
            position: relative;
            top: -285px;
        }

        .bk-partition {
            padding: 10px 0;
            font-size: 12px;
            .statusShow {
                border-radius: 2px;
                color: white;
                font-size: 10px;
                margin-left: 14px;
            }

            .statusSuccess {
                background: #4EBB49;
            }

            .statusRunning {
                background: #4C7CF4;
            }

            .statusFailed {
                background: #DC5D5D;
            }

            & > span, a {
                margin: 10px;
                padding: 1px 4px;
            }
        }

        .langError {
            @include scroller;
            display: inline-block;
            padding: 2px 4px;
            margin-top: 10px;
            margin-left: 10px;
            height: 300px;
            width: 80%;
            overflow-y: auto;
            overflow-x: hidden;
            word-wrap: break-word;
            word-break: break-all;
        }
    }
    .bk-base-label {
        font-weight: bold;
    }
    .bk-node-name {
        width: 100%;
        font-size: 12px;
    }
</style>
