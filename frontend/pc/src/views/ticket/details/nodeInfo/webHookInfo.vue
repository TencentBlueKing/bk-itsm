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
                <bk-table
                    v-if="true"
                    :data="[]"
                    :ext-cls="'bk-editor-table'">
                    <bk-table-column :label="$t(`m.treeinfo['字段名']`)" prop="key"></bk-table-column>
                    <bk-table-column :label="$t(`m.treeinfo['参数值']`)" width="400">
                        <template slot-scope="props">
                            <span>{{props.row.value || '--'}}</span>
                        </template>
                    </bk-table-column>
                </bk-table>
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
                default () {
                    return {}
                }
            }
        },
        mounted () {
            if (this.nodeInfo.query_params) {
                console.log('555')
            }
        }
    }
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
