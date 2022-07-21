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
  <div class="bk-history-detail" v-bkloading="{ isLoading: loading }">
    <div class="basic-information">
      <div class="info-content">
        <span class="info-title" :title="$t(`m.task['触发器名称：']`)">{{ $t('m.task["触发器名称："]') }}</span>
        <span class="info-info" :title="historyInfo.trigger_name || '--'">{{historyInfo.trigger_name || '--'}}</span>
      </div>
      <div class="info-content">
        <span class="info-title" :title="$t(`m.task['触发事件：']`)">{{ $t('m.task["触发事件："]') }}</span>
        <span class="info-info" :title="historyInfo.signal_name || '--'">{{historyInfo.signal_name || '--'}}</span>
      </div>
      <div class="info-content">
        <span class="info-title" :title="$t(`m.task['响应动作：']`)">{{ $t('m.task["响应动作："]') }}</span>
        <span class="info-info" :title="historyInfo.component_name || '--'">{{historyInfo.component_name || '--'}}</span>
      </div>
      <div class="info-content">
        <span class="info-title" :title="$t(`m.task['执行人：']`)">{{ $t('m.task["执行人："]') }}</span>
        <span class="info-info" :title="historyInfo.operator_username || '--'">{{historyInfo.operator_username || '--'}}</span>
      </div>
      <div class="info-content">
        <span class="info-title" :title="$t(`m.task['执行方式：']`)">{{ $t('m.task["执行方式："]') }}</span>
        <span class="info-info" :title="historyInfo.operate_type || '--'">{{historyInfo.operate_type || '--'}}</span>
      </div>
      <div class="info-content">
        <span class="info-title" :title="$t(`m.task['执行状态：']`)">{{ $t('m.task["执行状态："]') }}</span>
        <span class="info-info" :style="{ color: historyInfo.status === 'SUCCEED' ? '#2DCB56' : '#FF5656' }" :title="historyInfo.status_name || '--'">{{historyInfo.status_name || '--'}}</span>
      </div>
      <div class="info-content">
        <span class="info-title" :title="$t(`m.task['执行时间：']`)">{{ $t('m.task["执行时间："]') }}</span>
        <span class="info-info" :title="historyInfo.create_at || '--'">{{historyInfo.create_at || '--'}}</span>
      </div>
    </div>
    <div class="field-information">
      <div class="field-content" v-for="(field, fIndex) in historyInfo.fields" :key="fIndex">
        <div class="field-content-box" v-if="field.key === 'sub_message_component'">
          <bk-tab :active="activeName" @tab-change="changPanel" type="border-card">
            <bk-tab-panel
              v-for="(panel, index) in field.value"
              v-bind="panel"
              :key="index">
              <template slot="label">
                <i class="bk-icon" :class="[panel.icon]"></i>
                <span class="panel-name">{{ panel.label }}</span>
              </template>
              <div v-for="(subPanel, subIndex) in field.value"
                :key="subIndex"
                v-if="activeName === subPanel.name">
                <div v-for="(schema, sIndex) in subPanel.fields"
                  :key="sIndex" class="mb20" style="display: flex">
                  <span class="field-title inline" :title="schema.name">{{schema.name}}</span>
                  <span class="field-value inline" :title="schema.value || '--'">{{schema.value || '--'}}</span>
                </div>
              </div>
            </bk-tab-panel>
          </bk-tab>
        </div>
        <div class="field-content-box" v-else-if="field.key === 'req_params'">
          <bk-table
            :data="apiTableData"
            :size="'small'">
            <bk-table-column :label="$t(`m.treeinfo['名称']`)" min-width="150">
              <template slot-scope="props">
                <div class="bk-more">
                  <span :style="{ paddingLeft: 20 * props.row.level + 'px' }">
                    <span
                      v-if="props.row.has_children"
                      :class="['bk-icon', 'tree-expanded-icon', props.row.showChildren ? 'icon-down-shape' : 'icon-right-shape']"
                      @click="changeState(props.row)">
                    </span>
                    <span class="bk-icon bk-more-icon" v-else> </span>
                    <span>{{props.row.key || '--'}}</span>
                  </span>
                </div>
              </template>
            </bk-table-column>
            <bk-table-column :label="'类型'">
              <template slot-scope="props">
                {{ props.row.type }}
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.treeinfo['备注']`)" width="120">
              <template slot-scope="props">
                <span :title="props.row.desc">{{props.row.desc || '--'}}</span>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.treeinfo['参数值']`)" width="280">
              <template slot-scope="props">
                <span>{{props.row.value}}</span>
              </template>
            </bk-table-column>
          </bk-table>
        </div>
        <div class="field-content-box" v-else>
          <p class="field-title inline" :title="field.name">{{field.name}}</p>
          <p class="field-value inline" :title="field.value">{{field.value}}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { errorHandler } from '@/utils/errorHandler.js';
  import mixins from '../../../commonMix/mixins_api.js';
  export default {
    name: 'taskHistoryDetail',
    mixins: [mixins],
    props: {
      historyId: {
        type: [String, Number],
        default: '',
      },
      basicInfomation: {
        type: Object,
        default() {
          return {};
        },
      },
      nodeList: {
        type: Array,
        default() {
          return [];
        },
      },
      nodeIdMap: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        loading: false,
        historyInfo: '',
        activeName: 'send_email_message',
      };
    },
    computed: {
      apiTableData() {
        let temp = [];
        if (this.historyInfo.fields[1] && this.historyInfo.fields[1].key === 'req_params' && this.historyInfo.fields[1].apiContent) {
          temp = this.historyInfo.fields[1].apiContent.bodyTableData.filter(item => item.isShow);
        }
        return temp;
      },
    },
    watch: {
      historyId() {
        this.getDetail();
      },
    },
    async created() {
      await this.getDetail();
    },
    methods: {
      getDetail() {
        if (!this.historyId) {
          return;
        }
        this.loading = true;
        this.$store.dispatch('taskFlow/getHistoryDetail', this.historyId).then(res => {
          this.historyInfo = res.data;
          this.giveSignalInfo();
          this.historyInfo.fields.forEach(async field => {
            if (field.key === 'sub_message_component') {
              this.giveMessageData();
            }
            if (field.key === 'api_source') {
              await this.giveApiData();
            }
            if (field.key === 'states') {
              field.value = this.nodeList.find(node => Number(node.state_id) === Number(field.value)).name;
            }
            if (field.key === 'field_key') {
              let tempAllFields = [];
              this.nodeList.forEach(node => {
                tempAllFields = tempAllFields.concat(node.fields);
              });
              field.value = tempAllFields.find(item => item.key === field.value).name;
            }
            if (field.key === 'processors') {
              if (Object.prototype.hasOwnProperty.call(field.value, 'members')) {
                field.value = JSON.parse(JSON.stringify(field.value)).members.replace(/^(\s|,)+|(\s|,)+$/g, '');
              }
            }
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.loading = false;
          });
      },
      giveSignalInfo() {
        let senderName = '';
        if (this.historyInfo.signal_type === 'STATE') {
          // senderName = this.nodeList.find(node => Number(node.state_id) === Number(this.historyInfo.sender)).name;
          senderName = this.nodeIdMap[this.historyInfo.sender];
        } else {
          senderName = this.basicInfomation.title;
        }
        this.historyInfo.signal_name += this.$t('m.task["["]') + senderName + this.$t('m.task["]"]');
      },
      giveMessageData() {
        this.historyInfo.fields[0].value.forEach(item => {
          this.$set(item, 'checked', (item.checked || false));
          this.$set(item, 'label', item.name);
          this.$set(item, 'icon', '');
          switch (item.code) {
            case 'send_email_message':
              item.icon = 'icon-email';
              break;
            case 'send_sms_message':
              item.icon = 'icon-mobile';
              break;
            case 'send_wechat_message':
              item.icon = 'icon-weixin';
              break;
          }
          item.name = item.code;
        });
      },
      giveApiData() {
        const params = {
          id: this.historyInfo.fields[0].value,
        };
        this.$store.dispatch('apiRemote/get_remote_api_detail', params).then(res => {
          const backValue = res.data;
          this.historyInfo.fields.forEach(async field => {
            if (field.key === 'api_source') {
              field.value = `${backValue.remote_system_name}/${backValue.name}`;
            } else {
              this.$set(field, 'apiContent', backValue);
              this.$set(field.apiContent, 'bodyTableData', []);
              this.$set(field.apiContent, 'treeDataList', {});
              field.apiContent.treeDataList = await this.jsonschemaToList({
                root: JSON.parse(JSON.stringify(field.apiContent.req_body)),
              });
              // 如果数据已经存在，则进行表格初始化赋值
              if (field.value) {
                field.apiContent.treeDataList = this.jsonValueTreeList(field.value, JSON.parse(JSON.stringify(field.apiContent.treeDataList)));
              }
              // 生成table表格数据
              field.apiContent.bodyTableData = await this.treeToTableList(JSON.parse(JSON.stringify(field.apiContent.treeDataList[0].children)));
              const bodyTableData = JSON.parse(JSON.stringify(field.apiContent.bodyTableData));
              // 加入/引用变量
              bodyTableData.forEach(item => {
                item.name = item.key || '';
                item.children = [];
                item.value = (item.value !== undefined) ? item.value : '';
              });
              // 多层列表数据 关联 table表格数据
              this.recordChildren(bodyTableData);
              field.apiContent.bodyTableData = await bodyTableData;
            }
          });
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      jsonValueTreeList(jsonData, treeDataList) {
        const listToJsonStep = function (lastObject, insertObject, key, item, lastType) {
          if (lastType === 'object') {
            const reqData = insertObject.filter(ite => ite.key === key);
            if (!reqData.length) {
              return;
            }
            // reqData[0]
            if (item.constructor.name.toLowerCase() === 'array') {
              if (!reqData[0].children || !reqData[0].children.length) {
                return;
              }
              const oneItem = JSON.parse(JSON.stringify(Object.assign({ parentInfo: '' }, reqData[0].children[0])));
              for (let i = 1; i < item.length; i++) {
                reqData[0].children.push(oneItem);
              }
              for (const j in item) {
                listToJsonStep(reqData[0].children, reqData[0].children[j], 'items', item[j], 'array');
              }
            } else if (item.constructor.name.toLowerCase() === 'object') {
              for (const j in item) {
                listToJsonStep(reqData[0], reqData[0].children, j, item[j], 'object');
              }
            } else {
              reqData[0].value = item;
            }
          } else if (lastType === 'array') {
            if (item.constructor.name.toLowerCase() === 'array') {
              const reqData = insertObject.filter(ite => ite.key === key);
              if (!reqData.length) {
                return;
              }
              if (!reqData[0].children || !reqData[0].children.length) {
                return;
              }
              const oneItem = JSON.parse(JSON.stringify(insertObject.children[0]));
              for (let i = 1; i < item.length; i++) {
                insertObject.children.push(oneItem);
              }
              for (const j in item) {
                listToJsonStep(insertObject.children, insertObject.children[j], 'items', item[j], 'array');
              }
            } else if (item.constructor.name.toLowerCase() === 'object') {
              for (const j in item) {
                listToJsonStep(insertObject, insertObject.children, j, item[j], 'object');
              }
            } else {
              insertObject.value = item;
            }
          }
        };
        for (const key in jsonData) {
          listToJsonStep(treeDataList[0], treeDataList[0].children, key, jsonData[key], 'object', 0);
        }
        return treeDataList;
      },
      recordChildren(tableData, levelInitial) {
        const levelList = tableData.map(item => item.level);
        const maxLevel = Math.max(...levelList);
        const recordChildrenStep = function (tableData, item) {
          tableData.filter(ite => (ite.level === item.level - 1 && ite.primaryKey === item.parentPrimaryKey && ite.ancestorsList.toString() === item.ancestorsList.slice(0, -1).toString()))[0].children.push(item);
        };
        for (let i = maxLevel; i > (levelInitial || 0); i--) {
          tableData.filter(item => item.level === i).forEach(ite => {
            recordChildrenStep(tableData, ite);
          });
        }
      },
      // 展示子集
      changeState(item) {
        item.showChildren = !item.showChildren;
        item.children.forEach(ite => {
          ite.isShow = item.showChildren;
        });
        if (!item.showChildren) {
          this.closeChildren(item);
        }
      },
      // 关闭所有子集
      closeChildren(item) {
        item.children.forEach(ite => {
          ite.isShow = false;
          if (ite.has_children) {
            ite.showChildren = false;
            this.closeChildren(ite);
          }
        });
      },
      changPanel(name) {
        this.activeName = name;
      },
    },
  };
</script>

<style scoped lang='scss'>
    @import '../../../../scss/mixins/scroller';
    .bk-history-detail{
        padding: 23px;
        color: #63656E;
        font-size: 12px;
        .basic-information{
            padding: 0 14px;
            .info-content{
                margin-bottom: 12px;
                display: inline-flex;
                width: 49%;
                .info-title{
                    display: inline-block;
                    width: 120px;
                    font-weight: bold;
                    overflow: hidden;
                    white-space: nowrap;
                    text-overflow: ellipsis;
                }
                .info-info{
                    display: inline-block;
                    width: calc(100% - 125px);
                    word-break: break-all;
                }
            }
        }
        .field-information{
            padding: 0 14px;
            margin-top: 30px;
            .field-content{
                .field-content-box{
                    display: flex;
                    align-items: center;
                    margin-bottom: 12px;
                    /deep/ .bk-table-body-wrapper{
                        @include scroller;
                    }
                    /deep/.bk-tab-label-item{
                        min-width: 130px;
                        box-shadow: 0 2px 6px 0 rgba(0, 0, 0, 0.1);
                    }
                    /deep/ .bk-tab-border-card{
                        width: 100%;
                    }
                }
            }
        }
    }
    .inline{
        display: inline-block;
    }
    .field-title{
        width: 120px;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        font-weight: bold;
    }
    .field-value{
        width: calc(100% - 125px);
        word-break: break-all;
    }
    /deep/ .bk-tab > .bk-tab-section {
        border: 1px solid #dcdee5;
        border-top: none;
    }
</style>
