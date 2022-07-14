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
    <div class="bk-trigger-condition" v-for="(item, index) in responseList" :key="index">
      <div class="bk-condition-name">
        <p>{{$t(`m.trigger['响应动作']`)}}</p>
        <div class="bk-between-operat">
          <i class="bk-itsm-icon icon-flow-add" @click="addResponse(item, index)"></i>
          <i class="bk-itsm-icon icon-flow-reduce"
            :class="{ 'bk-no-delete': responseList.length === 1 }"
            @click="deleteResponse(item, index)"></i>
        </div>
      </div>
      <div class="bk-condition-content">
        <div class="bk-response-way">
          <p class="bk-response-name">{{$t(`m.trigger['动作名称']`)}}<span class="bk-span-square">*</span></p>
          <bk-select ext-cls="bk-way-input"
            v-model="item.way"
            :clearable="false"
            searchable
            @selected="selectedWay(...arguments, item)">
            <bk-option v-for="option in responseWayList"
              :key="option.key"
              :id="option.key"
              :name="option.name">
            </bk-option>
          </bk-select>
          <p class="bk-error-info" v-if="item.wayStatus">{{$t(`m.trigger['动作名称为必填项']`)}}</p>
        </div>
        <div v-if="item.wayInfo.field_schema && item.wayInfo.field_schema.length"
          v-bkloading="{ isLoading: item.isLoading }"
          style="min-height: 100px;">
          <response-content
            v-if="!item.isLoading && item.wayInfo.field_schema && item.wayInfo.field_schema.length"
            :item="item"
            :signal="signal">
          </response-content>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
  import responseContent from './responseContent.vue';

  export default {
    name: 'responseCondition',
    components: {
      responseContent,
    },
    props: {
      responseWayList: {
        type: Array,
        default() {
          return [];
        },
      },
      responseList: {
        type: Array,
        default() {
          return [];
        },
      },
      signal: String,
    },
    data() {
      return {
        wayList: [],
        apiList: [],
      };
    },
    created() {

    },
    methods: {
      addResponse(item, index) {
        this.responseList.splice(index + 1, 0, {
          way: '',
          wayInfo: {},
          performData: {
            runMode: 'BACKEND',
            displayName: '',
            repeat: 'one',
          },
          isLoading: false,
        });
      },
      deleteResponse(item, index) {
        if (this.responseList.length === 1) {
          return;
        }
        this.responseList.splice(index, 1);
      },
      // 选中某一个类型
      async selectedWay() {
        // 当存在校验显示时，将校验显示还原
        if (arguments[2].wayStatus) {
          arguments[2].wayStatus = false;
        }
        arguments[2].isLoading = true;
        arguments[2].wayInfo = JSON.parse(JSON.stringify(this.responseWayList.filter(node => node.key === arguments[0])[0]));
        setTimeout(() => {
          arguments[2].isLoading = false;
        }, 1000);
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../../scss/mixins/clearfix.scss';

    .bk-trigger-condition {
        position: relative;
        border: 1px solid #DCDEE5;
        border-top: none;
        background-color: #FAFBFD;
        @include clearfix;
    }
    .bk-condition-name {
        color: #63656E;
        font-size: 12px;
        width: 100px;
        position: absolute;
        top: 50%;
        left: 50px;
        transform: translate(-50%, -50%);
        text-align: center;
        .bk-between-operat {
            line-height: 20px;
            font-size: 14px;
            .bk-itsm-icon {
                color: #C4C6CC;
                margin-right: 9px;
                cursor: pointer;
                &:hover {
                    color: #979BA5;
                }
            }
            .bk-no-delete {
                color: #DCDEE5;
                cursor: not-allowed;
                &:hover {
                    color: #DCDEE5;
                }
            }
        }
    }
    .bk-condition-content {
        float: right;
        width: calc(100% - 100px);
        border-left: 1px solid #DCDEE5;
        background-color: #ffffff;
    }
    .bk-response-way {
        padding: 15px;
        @include clearfix;
        .bk-response-name {
            float: left;
            font-size: 14px;
            color: #666;
            line-height: 32px;
            margin-right: 10px;
            .bk-span-square {
                color: #ff5656;
                vertical-align: middle;
                position: relative;
                top: 2px;
                left: 3px;
            }
        }
        .bk-way-input {
            width: 300px;
            float: left;
            margin-right: 10px;
        }
    }
    .bk-error-info {
        float: left;
        color: #ff5656;
        font-size: 12px;
        line-height: 30px;
        margin-left: 10px;
    }
</style>
