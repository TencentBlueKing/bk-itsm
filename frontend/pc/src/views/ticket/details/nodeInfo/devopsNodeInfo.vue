<template>
  <div class="bk-sops-node-content">
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
      <div>
        <div class="bk-param">
          <bk-table
            v-if="true"
            :data="nodeInfo.api_info.devops_info"
            :ext-cls="'bk-editor-table'">
            <bk-table-column :label="$t(`m.treeinfo['字段名']`)" prop="name"></bk-table-column>
            <bk-table-column :label="$t(`m.treeinfo['参数值']`)" width="400">
              <template slot-scope="props">
                <span>{{props.row.value || '--'}}</span>
              </template>
            </bk-table-column>
          </bk-table>
        </div>
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
              'statusSuccess': nodeInfo.status === 'FINISHED',
              'statusRunning': nodeInfo.status === 'RUNNING',
              'statusFailed': nodeInfo.status === 'FAILED' }">
            {{ taskStatus[nodeInfo.status] || '--' }}</span>
        </p>
        <p class="bk-partition">
          <b class="bk-base-label">{{ $t('m.taskTemplate["任务详情："]') }}</b>
          <template v-if="nodeInfo.api_info.devops_build_url">
            <a :href="nodeInfo.api_info.devops_build_url"
              target="_blank"
              style="color: #5482F4;">
              {{ $t('m["跳转蓝盾查看"]') }}
            </a>
          </template>
          <template v-else>
            <span style="color: #DC5D5D;">--</span>
          </template>
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
    name: 'devopsNodeInfo',
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
        taskStatus: {
          FINISHED: this.$t('m.task["执行成功"]'),
          RUNNING: this.$t('m.task["执行中"]'),
          FAILED: this.$t('m.task["执行失败"]'),
        },
      };
    },
  };
</script>

<style scoped lang='scss'>
    @import '../../../../scss/mixins/clearfix.scss';
    @import '../../../../scss/mixins/scroller.scss';

    .bk-sops-node-content {
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
