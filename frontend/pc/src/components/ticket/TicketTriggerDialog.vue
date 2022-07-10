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
  <div class="trigger-dialog-box">
    <bk-dialog v-model="isTrigger"
      width="930"
      theme="primary"
      :mask-close="false"
      :auto-close="false"
      header-position="left"
      :title="trigger.component_name"
      @confirm="confirmTrigger">
      <p style="margin-bottom: 10px">{{ $t(`m['触发器名称：']`) + trigger.display_name }}</p>
      <bk-form
        v-if="isshowForm"
        :key="new Date().getTime()"
        :form-type="'horizontal'"
        :label-width="100"
        ref="conductorForm">
        <template v-if="item && item.key === 'api'">
          <api-call :item="item">
          </api-call>
        </template>
        <template v-else-if="item && item.key === 'modify_field'">
          <modify-field :field-schema="item"></modify-field>
        </template>
        <template v-else>
          <template v-for="(itemInfo, index) in item.field_schema">
            <!-- 对于多层嵌套和单层嵌套的区别 -->
            <template v-if="itemInfo.type === 'SUBCOMPONENT'">
              <send-message :key="index"
                :is-show-var="false"
                :item-info="itemInfo">
              </send-message>
            </template>
            <template v-else>
              <bk-form-item :ext-cls="itemInfo.required ? 'bk-field-schema mb20' : 'bk-field-schema no-require-item mb20'"
                :label="itemInfo.name"
                :required="itemInfo.required"
                :key="index"
                :desc="itemInfo.tips">
                <change-conductor
                  :is-show-var="false"
                  :item-info="itemInfo">
                </change-conductor>
              </bk-form-item>
            </template>
          </template>
        </template>
      </bk-form>
      <p v-if="errorTip" class="error-tip" style="color: red; margin-top: 4px">
        <i class="bk-itsm-icon icon-itsm-icon-square-one"></i>
        {{ $t(`m['带*的表单项不能为空！']`)}}
      </p>
    </bk-dialog>
    <bk-dialog v-model="info.show"
      theme="primary"
      :mask-close="false"
      :show-footer="false"
      @confirm="refechTicket">
      <div class="status">
        <i v-if="info.status === 'success'" style="color: #3fc06d" class="bk-itsm-icon icon-success status-icon"></i>
        <i v-else-if="info.status === 'error'" style="color: red" class="bk-itsm-icon icon-itsm-icon-four status-icon"></i>
        <i v-else class="bk-itsm-icon icon-icon-loading status-load-icon"></i>
        <p class="title">{{ info.title}}</p>
        <p class="title">{{ info.subTitle}}</p>
      </div>
    </bk-dialog>
  </div>
</template>
<script>
  import { errorHandler } from '../../utils/errorHandler';
  import modifyField from '../../views/processManagement/publicTrigger/components/modifyField.vue';
  import sendMessage from '../../views/processManagement/publicTrigger/components/sendMessage.vue';
  import apiCall from '../../views/processManagement/publicTrigger/components/apiCall.vue';
  import changeConductor from '../../views/processManagement/publicTrigger/components/changeConductor.vue';
  export default {
    name: 'TicketTriggerDialog',
    components: {
      sendMessage,
      apiCall,
      changeConductor,
      modifyField,
    },
    props: {
      item: {
        type: Object,
        default: () => {},
      },
    },
    data() {
      return {
        isTrigger: false,
        trigger: '',
        checkedbox: false,
        errorTip: false,
        info: {
          show: false,
          status: 'loading',
          title: 'loading…',
          subTitle: '',
        },
      };
    },
    computed: {
      isshowForm() {
        return this.item || false;
      },
    },
    methods: {
      openDialog(trigger) {
        this.isTrigger = true;
        this.trigger = trigger;
      },
      refechTicket() {
        this.$store.commit('taskHistoryRefreshFunc');
        if (this.trigger.need_refresh || !this.trigger.can_repeat) {
          this.$emit('init-info');
        }
      },
      getTriggerStatus(id) {
        this.$store.dispatch('ticket/getTriggerStatus', id).then(res => {
          const list = ['FAILED', 'SUCCEED'];
          if (!list.includes(res.data.status)) {
            const setTimeoutFunc = setTimeout(() => {
              this.getTriggerStatus(id);
            }, 1000);
            this.$once('hook:beforeDestroy', () => {
              clearInterval(setTimeoutFunc);
            });
          } else {
            this.info.title = res.data.status_name;
            this.info.status = res.data.status === 'FAILED' ? 'error' : 'success';
          }
        });
      },
      /* eslint-disable */
      checkInfo() {
        let status = false;
        if (this.item.key === 'api') {
          this.item.wayInfo.field_schema.forEach(schema => {
            if (schema.key === 'req_params') {
              for (const key in schema.value) {
                if (Array.isArray(schema.value[key])) {
                  schema.value[key].forEach(schemaValue => {
                    if (schemaValue.value === '') status = true;
                  });
                } else {
                  if (schema.value === '') status = true;
                }
              }
            } else {
              if (schema.value === '') status = true;
            }
          });
        } else {
          this.item.field_schema.forEach(schema => {
            if (schema.type === 'SUBCOMPONENT') {
              const checked = schema.sub_components.some(check => check.checked);
              if (!checked) this.checkedbox = this.$t('m[\'至少勾选一项\']');
              schema.sub_components.forEach(schemaItem => {
                if (schemaItem.checked) {
                  schemaItem.field_schema.forEach(field => {
                    if (field.type === 'MEMBERS' || field.type === 'MULTI_MEMBERS') {
                      if (field.value[0].value.length === 0 || field.key === '') {
                        status = true;
                      }
                    } else {
                      if (field.value === '') {
                        status = true;
                      }
                    }
                  });
                }
              });
            } else {
              if (schema.required) {
                if (schema.type === 'MEMBERS' || schema.type === 'MULTI_MEMBERS') {
                  schema.value.forEach(schemaValue => {
                    if (schemaValue.value.length === 0 || schemaValue.key === '') {
                      status = true;
                    }
                  });
                } else {
                  if (schema.value === '') {
                    status = true;
                  }
                }
              }
            }
          });
        }
        return status;
      },
      /* eslint-disable */
      executeTrigger() {
        this.errorTip = false;
        if (this.checkInfo() || this.checkedbox) {
          this.errorTip = true;
          return;
        }
        const paramsItem = {};
        paramsItem.params = [];
        if (this.item.key === 'api') {
          this.item.wayInfo.field_schema.forEach(wayItem => {
            if (wayItem.key === 'api_source') {
              paramsItem.params.push({
                key: wayItem.key,
                value: wayItem.apiId,
              });
            } else {
              const valueInfo = {
                key: wayItem.key,
                value: {},
              };
              valueInfo.value = this.treeToJson(wayItem.apiContent.bodyTableData.filter(item => (!item.level)));
              paramsItem.params.push(valueInfo);
            }
          });
          // paramsItem.params.push(valueList)
        } else {
          this.item.field_schema.forEach(field => {
            if (field.type === 'SUBCOMPONENT') {
              const subContent = {
                key: field.key,
                sub_components: [],
              };
              field.sub_components.forEach(subItem => {
                if (subItem.checked) {
                  const subInfo = {
                    key: subItem.key,
                    params: [],
                  };
                  subItem.field_schema.forEach(subField => {
                    let valueItem = [];
                    if (subField.type === 'MULTI_MEMBERS' || subField.type === 'MEMBERS') {
                      const value = {};
                      value.ref_type = subField.referenceType;
                      value.value = {
                        member_type: subField.value[0].key,
                        members: subField.value[0].value.toString(),
                      };
                      valueItem.push(value);
                    } else {
                      valueItem = subField.value;
                    }
                    const paramsContent = {
                      key: subField.key,
                      value: valueItem,
                      ref_type: subField.referenceType,
                    };
                    subInfo.params.push(paramsContent);
                  });
                  subContent.sub_components.push(subInfo);
                }
              });
              paramsItem.params.push(subContent);
            } else {
              let valueItem = [];
              if (field.type === 'MEMBERS') {
                const value = {};
                value.ref_type = field.referenceType;
                value.value = {
                  member_type: field.value[0].key,
                  members: field.value[0].value.toString(),
                };
                valueItem.push(value);
              } else {
                valueItem = field.value;
              }
              const paramsContent = {
                key: field.key,
                value: valueItem,
                ref_type: field.referenceType,
              };
              paramsItem.params.push(paramsContent);
            }
            // params.push(paramsItem)
          });
        }
        this.$store.dispatch('trigger/executeTrigger', { params: paramsItem, id: this.trigger.id }).then(res => {
          if (res.result) {
            this.info.show = true;
            this.getTriggerStatus(res.data.action_id);
          }
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isTrigger = false;
          });
      },
      treeToJson(listData) {
        const jsonDataDict = {};
        const treeToJsonStep = function (jsonDataDict, item, level, lastType) {
          if (!item.key) {
            return;
          }
          if (item.type === 'array') {
            const baseItem = [];
            if (lastType === 'array') {
              jsonDataDict.push(baseItem);
              for (const j in item.children) {
                treeToJsonStep(jsonDataDict[jsonDataDict.length - 1], item.children[j], 1, 'array');
              }
            }
            if (lastType === 'object') {
              const baseItem = {};
              baseItem[item.key] = [];
              Object.assign(jsonDataDict, baseItem);
              for (const j in item.children) {
                treeToJsonStep(jsonDataDict[item.key], item.children[j], 1, 'array');
              }
            }
          } else if (item.type === 'object') {
            const baseItem = {};
            if (lastType === 'array') {
              jsonDataDict.push(baseItem);
              for (const j in item.children) {
                treeToJsonStep(jsonDataDict[jsonDataDict.length - 1], item.children[j], 1, 'object');
              }
            }
            if (lastType === 'object') {
              baseItem[item.key] = {};
              Object.assign(jsonDataDict, baseItem);
              for (const j in item.children) {
                treeToJsonStep(jsonDataDict[item.key], item.children[j], 1, 'object');
              }
            }
          } else {
            if (item.type === 'number') {
              item.value = Number(item.value);
            }
            if (lastType === 'array') {
              const baseItem = {
                is_leaf: ((item.type !== 'object') && (item.type !== 'array')),
                ref_type: item.source_type === 'CUSTOM' ? 'custom' : 'reference',
                value: item.source_type === 'CUSTOM' ? item.value : item.value_key,
              };
              // item.source_type === 'CUSTOM' ? item.value
              //     : `\$\{params\_${item.value_key}\}`
              jsonDataDict.push(baseItem);
            }
            if (lastType === 'object') {
              const baseItem = {};
              baseItem[item.key] = {
                is_leaf: ((item.type !== 'object') && (item.type !== 'array')),
                ref_type: item.source_type === 'CUSTOM' ? 'custom' : 'reference',
                value: item.source_type === 'CUSTOM' ? item.value : item.value_key,
              };
              // item.source_type === 'CUSTOM' ? item.value
              //     : `\$\{params\_${item.value_key}\}`
              Object.assign(jsonDataDict, baseItem);
            }
          }
        };
        for (const i in listData) {
          treeToJsonStep(jsonDataDict, listData[i], 0, 'object');
        }
        return jsonDataDict;
      },
      confirmTrigger() {
        this.executeTrigger();
      },
    },
  };
</script>
<style lang='scss' scoped>
/deep/ .bk-dialog-wrapper .bk-dialog-body {
    max-height: 600px;
    overflow: auto;
}
/deep/ .bk-send-message {
    border: 1px solid #dcdee5;
}
@keyframes rotation {
    from {
        -webkit-transform: rotate(0deg);
    }
    to {
        -webkit-transform: rotate(360deg);
    }
}
.status {
    text-align: center;
    .status-icon {
        display: inline-block;
        width: 60px;
        height: 60px;
        font-size: 60px;
        margin-top: 20px;
    }
    .status-load-icon {
        display: inline-block;
        width: 60px;
        height: 60px;
        color: #3a84ff;
        font-size: 60px;
        -webkit-transform: rotate(360deg);
        animation: rotation 1.5s linear infinite;
        -moz-animation: rotation 1.5s linear infinite;
        -webkit-animation: rotation 1.5s linear infinite;
        -o-animation: rotation 1.5s linear infinite;
    }
    .title {
        margin-top: 10px;
        font-size: 20px;
    }
}
</style>
