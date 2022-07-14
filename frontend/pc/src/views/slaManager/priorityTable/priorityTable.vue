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
  <div class="bk-priority-table">
    <!-- 影响范围 -->
    <div class="bk-priority-scope">
      <p class="bk-scope-title" :class="{ 'bk-scope-title-en': localeCookie }">{{ $t('m.slaContent["优先级"]') }}</p>
      <div class="bk-scope-list" :class="{ 'bk-min-height': !scopeList.length }">
        <span class="bk-scope-info" :class="{ 'bk-scope-info-en': localeCookie }">
          {{ $t('m.slaContent["影响范围"]') }}
        </span>
        <bk-checkbox-group v-model="scopCheckList" @change="changeScopeCheck">
          <ul class="bk-scope-ul" :class="{ 'bk-scope-ul-en': localeCookie }">
            <li v-for="(item, index) in scopeList"
              :key="index"
              :class="{ 'bk-scope-none': index === scopeList.length - 1, 'bk-editor-el': priorityConten.editorStatus }"
              :style="{
                background: 'rgba(220, 222, 229, ' + (index * 0.15 + 0.1) + ')'
              }">
              <div class="bk-form-content bk-check-info"
                v-if="priorityConten.editorStatus">
                <bk-checkbox :ext-cls="'cus-ellipsis'" :value="item.key" :title="item.name">{{ item.name }}</bk-checkbox>
              </div>
              <span class="bk-normal-word" v-else>{{ item.name }}</span>
            </li>
          </ul>
        </bk-checkbox-group>
      </div>
    </div>
    <!-- 紧急程度 -->
    <div class="bk-priority-degree">
      <p class="bk-priority-info">{{ $t('m.slaContent["紧急程度"]') }}</p>
      <bk-checkbox-group v-model="degreeCheckList" @change="changeDegreeCheck">
        <ul class="bk-degree-ul"
          :class="{ 'bk-degree-ul-en': localeCookie }"
          style="font-weight: bold; min-height: 43px;">
          <li v-for="(item, index) in degreeList"
            :key="index"
            :style="{
              width: (100 / degreeList.length) + '%',
              background: 'rgba(220, 222, 229, ' + (index * 0.15 + 0.1) + ')'
            }"
            :class="{ 'bk-scope-none': index === degreeList.length - 1, 'bk-editor-el': priorityConten.editorStatus }">
            <div class="bk-form-content" v-if="priorityConten.editorStatus">
              <bk-checkbox :ext-cls="'cus-ellipsis'" :value="item.key" :title="item.name">{{ item.name }}</bk-checkbox>
            </div>
            <span class="bk-normal-word" v-else>{{ item.name }}</span>
          </li>
        </ul>
      </bk-checkbox-group>
      <ul class="bk-degree-line" v-if="contentList.length">
        <li v-for="(scopeItem, scopeIndex) in scopeList" :key="scopeIndex">
          <ul class="bk-degree-ul"
            :class="{ 'bk-scope-none': scopeIndex === scopeList.length - 1, 'bk-degree-other-en': localeCookie }">
            <li v-for="(degreeItem, degreeIndex) in degreeList"
              :key="degreeIndex"
              :style="{
                width: (100 / degreeList.length) + '%'
              }"
              :class="{ 'bk-scope-none': degreeIndex === degreeList.length - 1, 'bk-editor-style': priorityConten.editorStatus }">
              <div v-for="contentItem in contentList" :key="contentItem.id">
                <template v-if="contentItem.impact === scopeItem.key && contentItem.urgency === degreeItem.key">
                  <div class="bk-form-content" v-if="priorityConten.editorStatus" :class="{ 'bk-border-error': scopeItem.is_enabled && degreeItem.is_enabled && !contentItem.priority && isSub }">
                    <bk-select v-model="contentItem.priority"
                      :clearable="false"
                      searchable
                      :font-size="'medium'">
                      <bk-option v-for="option in typeList"
                        :key="option.key"
                        :id="option.key"
                        :name="option.name">
                        <span
                          :style="'display: inline-block; margin-right: 10px; width: 8px; height: 8px;background-color: ' + typeColorList[option.key]"
                        ></span>
                        <span>{{ option.name }}</span>
                      </bk-option>
                    </bk-select>
                    <span class="in-select-icon" :style="'background-color: ' + typeColorList[contentItem.priority]"></span>
                  </div>
                  <span class="select-icon-father" v-else>
                    <span class="in-select-icon" :style="'background-color: ' + typeColorList[contentItem.priority]"></span>
                    {{typeList.filter(typeNode => typeNode.key === contentItem.priority).length ? typeList.filter(typeNode => typeNode.key === contentItem.priority)[0].name : '--'}}
                  </span>
                  <!-- 禁用面板 -->
                  <div class="bk-disabled-li" v-if="!degreeItem.is_enabled || !scopeItem.is_enabled"></div>
                </template>
              </div>
            </li>
          </ul>
        </li>
      </ul>
      <template v-else>
        <div class="bk-result">
          <img src="../../../images/box.png">
          <div class="bk-page-info">
            <p class="bk-p-black">
              {{ $t('m.deployPage["暂无数据"]') }}
            </p>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
  import cookie from 'cookie';
  export default {
    name: 'priorityTable',
    props: {
      priorityConten: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        // 程度颜色
        typeColorList: ['', '#99C5FF', '#FE9C00', '#EA3536'],
        // 影响范围
        scopeList: [],
        scopCheckList: [],
        // 紧急程度
        degreeList: [],
        degreeCheckList: [],
        contentList: [],
        typeList: [],
        isSub: false,
        localeCookie: false,
      };
    },
    mounted() {
      this.initDate();
      // 获取英文的cookie值
      this.localeCookie = cookie.parse(document.cookie).blueking_language !== 'zh-cn';
    },
    methods: {
      initDate() {
        // 影响范围
        this.scopeList = JSON.parse(JSON.stringify(this.priorityConten.info.impact));
        this.scopCheckList = this.scopeList.map(item => {
          if (item.is_enabled) {
            return item.key;
          }
        }).filter(item => item);
        // 紧急程度
        this.degreeList = JSON.parse(JSON.stringify(this.priorityConten.info.urgency));
        this.degreeCheckList = this.degreeList.map(item => {
          if (item.is_enabled) {
            return item.key;
          }
        }).filter(item => item);
        this.contentList = JSON.parse(JSON.stringify(this.priorityConten.info.priority_matrix));
        this.typeList = JSON.parse(JSON.stringify(this.priorityConten.info.priority));
      },
      changeScopeCheck(newVal) {
        this.scopeList.forEach(item => {
          item.is_enabled = newVal.some(check => check === item.key);
        });
      },
      changeDegreeCheck(newVal) {
        this.degreeList.forEach(item => {
          item.is_enabled = newVal.some(check => check === item.key);
        });
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../scss/mixins/clearfix.scss';
    @import '../../../scss/mixins/scroller.scss';

    .bk-priority-table {
        @include clearfix;
        border: 1px solid #DCDEE5;
        .cus-ellipsis{
            display: flex;
            justify-content: center;
            align-items: center;
            /deep/.bk-checkbox-text{
                text-overflow: ellipsis;
                overflow: hidden;
                white-space: nowrap;
            }
        }
    }
    .bk-priority-scope {
        float: left;
        width: 200px;
        text-align: center;
        .bk-scope-title {
            line-height: 84px;
            color: #313238;
            font-weight: bold;
            background-color: #fff;
            border-bottom: 1px solid #DCDEE5;
            border-right: 1px solid #DCDEE5;
        }
        .bk-scope-title-en {
            line-height: 97px;
        }
        .bk-scope-list {
            font-size: 12px;
            color: #63656E;
            background-color: #fff;
            @include clearfix;
            position: relative;
            border-right: 1px solid #DCDEE5;
            /* 中文样式 */
            .bk-scope-info {
                width: 10px;
                position: absolute;
                top: 50%;
                left: 15px;
                word-wrap: break-word;
                transform: translateY(-50%);
                color: #979BA5;
            }
            .bk-scope-ul {
                float: right;
                width: calc(100% - 42px);
                line-height: 16px;
                text-align: center;
                font-weight: bold;
                border-left: 1px solid #DCDEE5;
                background-color: #f7f7f7;
                li {
                    padding: 15px 20px;
                    border-bottom: 1px solid #DCDEE5;
                }
                .bk-editor-el {
                    padding: 11px 20px;
                }
                .bk-scope-none {
                    border-bottom: none;
                }
                .bk-check-info {
                    @include clearfix;
                    .bk-form-checkbox {
                        float: left;
                        height: 34px;
                        line-height: 34px;
                        font-weight: normal;
                    }
                }
            }
            /* 英文样式 */
            .bk-scope-info-en {
                left: 10px;
                word-wrap: normal;
            }
            .bk-scope-ul-en {
                width: calc(100% - 62px);
                li {
                    height: 65px;
                    position: relative;
                    span {
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%);
                        word-break: break-all;
                    }
                }
                .bk-check-info {
                    .bk-form-checkbox {
                        height: 44px;
                        line-height: 18px;
                        text-align: left;
                    }
                    .bk-checkbox-text {
                        display: inline;
                        word-break: break-all;
                    }
                }
            }
        }
    }
    .bk-normal-word {
        display: block;
        font-size: 12px;
        color: #63656e;
        font-weight: bold;
    }
    .bk-min-height {
        min-height: 200px;
        .bk-scope-ul {
            min-height: 200px;
        }
    }
    .bk-priority-degree {
        float: left;
        width: calc(100% - 200px);
        font-size: 12px;
        color: #63656E;
        .bk-priority-info {
            text-align: center;
            line-height: 41px;
            color: #979BA5;
            border-bottom: 1px solid #DCDEE5;
            background-color: #fff;
        }
        .bk-degree-line {
            background-color: #fff;
            .bk-scope-none {
                border-bottom: none;
            }
            .bk-degree-ul {
                li {
                    padding: 15px 20px;
                    line-height: 16px;
                }
            }
        }
        .bk-degree-ul {
            @include clearfix;
            border-bottom: 1px solid #DCDEE5;
            li {
                float: left;
                text-align: center;
                padding: 12px 20px;
                line-height: 18px;
                border-right: 1px solid #DCDEE5;
                position: relative;
            }
            .bk-editor-el {
                padding: 12px 20px;
            }
            .bk-scope-none {
                border-right: none;
            }
            li.bk-editor-style {
                padding: 12px 20px;
            }
            .bk-form-checkbox {
                font-weight: normal;
            }
            .bk-disabled-li {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: #FAFBFD;
                opacity: 0.5;
                cursor: not-allowed;
            }
            .bk-form-content,.select-icon-father {
                position: relative;
                .in-select-icon {
                    position: absolute;
                    left: 10px;
                    top: 50%;
                    width: 8px;
                    height: 8px;
                    transform: translateY(-50%);
                }
            }
            .select-icon-father {
                .in-select-icon {
                    left: -20px;
                }
            }
        }
        .bk-degree-ul-en {
            li {
                height: 55px;
                position: relative;
                span {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    width: calc(100% - 40px);
                    text-align: center;
                    word-break: break-all;
                }
            }
            .bk-editor-el {
                .bk-form-checkbox {
                    line-height: 32px;
                }
            }
        }
        .bk-degree-other-en {
            li {
                height: 64px;
                position: relative;
                span {
                    position: absolute;
                    top: 50%;
                    // left: 50%;
                    transform: translate(-50%, -50%);
                    width: calc(100% - 40px);
                    text-align: center;
                    word-break: break-all;
                }
            }
            li.bk-editor-style {
                padding: 15px 20px;
            }
        }
    }
</style>
