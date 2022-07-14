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
  <div class="bk-itsm-service">
    <!-- title -->
    <div class="is-title" :class="{ 'bk-title-left': !sliderStatus }">
      <p class="bk-come-back">
        {{ $t('m.slaContent["优先级管理"]') }}
      </p>
    </div>
    <div class="itsm-page-content">
      <!-- 提示信息 -->
      <!-- table切换栏 -->
      <ul class="bk-priority-type">
        <li v-for="(item, index) in choiceTypeList"
          :key="index"
          :class="{ 'bk-check-li': checkType.key === item.key }"
          @click="changeTab(item, index)">
          <span>{{item.name}}</span>
        </li>
      </ul>
      <div class="bk-itsm-version" v-if="versionStatus">
        <i class="bk-icon icon-info-circle"></i>
        <span>{{ $t('m.slaContent["优先级管理：通过影响范围和紧急程度两个维度来进行不同服务类型的优先级矩阵管理。"]') }}</span>
        <i class="bk-icon icon-close" @click="closeVersion"></i>
      </div>
      <!-- 优先级表格 -->
      <div class="bk-priority-table" v-bkloading="{ isLoading: isDataLoading }">
        <priority-table
          v-if="!isDataLoading"
          ref="priorityTable"
          :priority-conten="priorityConten">
        </priority-table>
      </div>
      <p class="bk-priority-message" v-if="!priorityConten.editorStatus">
        <span>{{ $t('m.slaContent["注：可在 "]') }}
          <span style="color: #3A84FF; cursor: pointer;"
            @click="gotoDataDictionary">
            {{ $t('m.slaContent["数据字典 "]') }}
          </span>
          {{ $t('m.slaContent["中修改 影响范围（IMPACT）、 紧急程度（URGENCY）以及 优先级（PRIORITY）的具体选项"]') }}
        </span>
      </p>
      <div class="other-choice" v-if="priorityConten.editorStatus">
        <span>{{ $t('m["应用到其它类型"]') }}: </span>
        <bk-checkbox-group class="choice-checkbox-group" v-model="serviceTypeList">
          <bk-checkbox class="choice-checkbox" v-for="choice in serviceTypeOptions" :key="choice.key" :value="choice.key">{{choice.name}}</bk-checkbox>
        </bk-checkbox-group>
      </div>
      <!-- 编辑操作 -->
      <div class="bk-priority-btn" :class="{ 'bk-margin-btn': priorityConten.editorStatus }">
        <template v-if="!priorityConten.editorStatus">
          <bk-button
            v-cursor="{ active: !hasPermission(['sla_priority_manage'], $store.state.project.projectAuthActions) }"
            :theme="'primary'"
            :title="$t(`m.eventdeploy['编辑']`)"
            :class="['mr10', {
              'btn-permission-disable': !hasPermission(['sla_priority_manage'], $store.state.project.projectAuthActions)
            }]"
            :loading="secondClick"
            @click="editorPriority">
            {{ $t('m.eventdeploy["编辑"]') }}
          </bk-button>
        </template>
        <template v-else>
          <bk-button :theme="'primary'"
            :title="$t(`m.eventdeploy['保存']`)"
            class="mr10"
            :loading="secondClick"
            @click="submitEditor">
            {{ $t('m.eventdeploy["保存"]') }}
          </bk-button>
          <bk-button :theme="'default'"
            :title="$t(`m.eventdeploy['取消']`)"
            class="mr10"
            :loading="secondClick"
            @click="closeEditor">
            {{ $t('m.eventdeploy["取消"]') }}
          </bk-button>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
  import { errorHandler } from '../../utils/errorHandler';
  import priorityTable from './priorityTable/priorityTable.vue';
  import permission from '@/mixins/permission.js';

  export default {
    name: 'priority',
    components: {
      priorityTable,
    },
    mixins: [permission],
    data() {
      return {
        serviceTypeList: [],
        isDataLoading: true,
        versionStatus: true,
        secondClick: false,
        checkType: {
          key: 'request',
        },
        priorityConten: {
          editorStatus: false,
          info: {},
        },
      };
    },
    computed: {
      sliderStatus() {
        return this.$store.state.common.slideStatus;
      },
      choiceTypeList() {
        return this.$store.state.choice_type_list;
      },
      serviceTypeOptions() {
        return this.$store.state.choice_type_list.filter(type => type.key !== this.checkType.key);
      },
    },
    watch: {

    },
    mounted() {
      this.getModelList();
    },
    methods: {
      getModelList() {
        this.isDataLoading = true;
        const params = {
          service_type: this.checkType.key,
        };
        this.$store.dispatch('slaManagement/getPriorityList', { params }).then((res) => {
          this.priorityConten.info = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
      },
      closeVersion() {
        this.versionStatus = false;
      },
      // 切换table
      changeTab(item) {
        if (this.priorityConten.editorStatus) {
          this.$bkInfo({
            type: 'warning',
            title: this.$t('m.slaContent["确认退出？"]'),
            subTitle: this.$t('m.slaContent["表格正在编辑，确认退出编辑状态将不会保存数据！"]'),
            confirmFn: () => {
              this.checkType.key = item.key;
              this.getModelList();
              this.priorityConten.editorStatus = false;
            },
          });
          return;
        }
        this.checkType.key = item.key;
        this.getModelList();
      },
      // 编辑
      editorPriority() {
        if (!this.hasPermission(['sla_priority_manage'])) {
          this.applyForPermission(['sla_priority_manage'], this.$store.state.project.projectAuthActions, {});
          return;
        }
        this.priorityConten.editorStatus = true;
      },
      // 取消
      closeEditor() {
        // 取消操作还原操作数据
        const childInfo = this.getChildInfo();
        if (JSON.stringify(childInfo.priority_matrix) !== JSON.stringify(this.priorityConten.info.priority_matrix)) {
          this.$bkInfo({
            type: 'warning',
            title: this.$t('m.slaContent["确认退出？"]'),
            subTitle: this.$t('m.slaContent["表格正在编辑，确认退出编辑状态将不会保存数据！"]'),
            confirmFn: () => {
              this.$refs.priorityTable.initDate();
              this.priorityConten.editorStatus = false;
            },
          });
        } else {
          this.priorityConten.editorStatus = false;
        }
        this.getModelList();
      },
      // 保存
      submitEditor() {
        // 校验
        if (this.$refs.priorityTable) {
          this.$refs.priorityTable.isSub = true;
        }
        let hasWrong = false;
        this.$refs.priorityTable.scopeList.forEach((scopeItem) => {
          this.$refs.priorityTable.degreeList.forEach((degreeItem) => {
            this.$refs.priorityTable.contentList.forEach((contentItem) => {
              if (contentItem.impact === scopeItem.key && contentItem.urgency === degreeItem.key && scopeItem.is_enabled && degreeItem.is_enabled && !contentItem.priority) {
                hasWrong = true;
              }
            });
          });
        });
        if (hasWrong) {
          return false;
        }
        const params = this.getChildInfo();
        this.secondClick = true;
        params.service_type = [this.checkType.key, ...this.serviceTypeList];
        this.$store.dispatch('slaManagement/submitPriority', { params }).then(() => {
          this.$bkMessage({
            message: this.$t('m.deployPage["保存成功"]'),
            theme: 'success',
          });
          this.priorityConten.editorStatus = false;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.secondClick = false;
            this.getModelList();
          });
      },
      // 获取子组件的数据
      getChildInfo() {
        let childInfo = {};
        if (this.$refs.priorityTable) {
          childInfo = {
            impact: this.$refs.priorityTable.scopeList,
            urgency: this.$refs.priorityTable.degreeList,
            priority_matrix: this.$refs.priorityTable.contentList,
          };
        }
        return childInfo;
      },
      // 前往数据字典页面
      gotoDataDictionary() {
        this.$router.push({
          path: '/dataDictionary',
        });
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../scss/mixins/clearfix.scss';
    @import '../../scss/mixins/scroller.scss';

    .bk-priority-type {
        @include clearfix;
        border-bottom: 1px solid #dde4eb;
        margin: -20px -20px 20px;
        padding: 0 20px;
        background-color: #ffffff;
        li {
            float: left;
            padding: 0 10px;
            line-height: 46px;
            text-align: center;
            color: #63656E;
            cursor: pointer;
            font-size: 14px;
            &:hover {
                color: #3a84ff;
            }
        }
        .bk-check-li {
            border-bottom: 2px solid #3a84ff;
            color: #3a84ff;
        }
    }
    .bk-priority-table {
        margin-top: 10px;
        min-height: 150px;
    }
    .bk-priority-message {
        margin-top: 7px;
        font-size: 12px;
        color: #979BA5;
        margin-bottom: 15px;
    }
    .bk-margin-btn {
        margin-top: 15px;
    }
    .other-choice {
        font-size: 14px;
        color: #63656E;
        .choice-checkbox-group {
            display: inline;
            .choice-checkbox {
                margin-left: 60px;
            }
            .choice-checkbox:first-of-type {
                margin-left: 20px;
            }
        }
        margin-top: 30px;
        margin-bottom: 14px;
    }
</style>
