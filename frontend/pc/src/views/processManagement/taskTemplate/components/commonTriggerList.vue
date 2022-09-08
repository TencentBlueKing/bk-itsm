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
  <div class="mt20 mb20">
    <div
      v-if="openFunction.TRIGGER_SWITCH && origin !== 'workflow' && origin !== 'transition'"
      class="more-configuration" data-test-id="trigger-div-showMoreConfig" @click="showMoreConfig = !showMoreConfig">
      <i v-if="!showMoreConfig" class="bk-icon icon-down-shape"></i>
      <i v-else class="bk-icon icon-up-shape"></i>
      <span>{{$t(`m.taskTemplate['高级配置']`)}}</span>
    </div>
    <div v-if="showMoreConfig"
      class="common-section-card-block mt20"
      :class="[{ 'inner-mode': origin === 'workflow' || origin === 'transition' }]">
      <label class="common-section-card-label">
        {{$t(`m.newCommon['触发器']`)}}
      </label>
      <div class="common-section-card-body">
        <template v-if="showMoreConfig">
          <collapse-transition>
            <div>
              <!-- 触发器列表 -->
              <div>
                <ul class="bk-trigger-content">
                  <li v-for="(item, index) in boundTriggerList" :key="index" @click.stop="openNew('add', item)" :class="{ 'li-transition': origin === 'transition' }">
                    <span class="bk-trigger-icon">
                      <i class="bk-itsm-icon icon-info-circle icon-slide" style="font-size: 24px"></i>
                    </span>
                    <span class="bk-trigger-name" :title="item.name">{{ item.name || '--' }}
                      <span v-if="item.is_draft" style="color: #3A84FF;">{{ $t('m.taskTemplate["(草稿)"]') }}</span>
                    </span>
                    <span class="bk-trigger-delete">
                      <i class="bk-icon icon-delete" @click.stop="delTrigger(item)"></i>
                    </span>
                  </li>
                  <bk-dropdown-menu trigger="click" style="float: left;">
                    <div class="bk-trigger-add" slot="dropdown-trigger" :title="$t(`m.taskTemplate['添加触发器']`)">
                      <i class="bk-icon icon-plus"></i>
                    </div>
                    <ul class="bk-dropdown-list" slot="dropdown-content">
                      <li><a href="javascript:;" data-test-id="taskTemplate-li-addTrigger" @click="openNew('add')">{{$t(`m.taskTemplate['新建']`)}}</a></li>
                      <li><a href="javascript:;" data-test-id="taskTemplate-li-quoteCommonTrigger" @click="openNew('cite')">{{$t(`m.taskTemplate['引用公共触发器']`)}}</a></li>
                    </ul>
                  </bk-dropdown-menu>
                </ul>
              </div>
            </div>
          </collapse-transition>
        </template>
      </div>
      <!-- 引用公共触发器 -->
      <template>
        <bk-dialog v-model="triggerDialogInfo.isShow"
          theme="primary"
          width="660"
          :mask-close="false">
          <div slot="header" class="trigger-dialog-header">
            <span>{{$t(`m.taskTemplate['引用公共触发器']`)}}</span>
            <div class="bk-search-key">
              <bk-input
                :clearable="true"
                :right-icon="'bk-icon icon-search'"
                v-model="triggerDialogInfo.searchKey"
                @enter="searchInfo"
                @clear="clearSearch">
              </bk-input>
            </div>
          </div>
          <div class="trigger-dialog-box" v-bkloading="{ isLoading: triggerDialogInfo.listLoading }">
            <p class="dialog-none-content" v-if="triggerDialogInfo.list.length === 0">
              <i class="bk-icon icon-info-circle"></i>
              <span>{{$t(`m.taskTemplate['暂无匹配的公共触发器，']`)}}</span>
              <span class="bk-primary" @click="newTrigger">{{$t(`m.taskTemplate['跳转创建']`)}}</span>
            </p>
            <!-- table -->
            <template v-else>
              <span>{{$t(`m.taskTemplate['根据您当前的引用位置，系统已筛选出适用的公共触发器。']`)}}</span>
              <ul class="bk-trigger-content">
                <li v-for="(item, index) in triggerDialogInfo.list"
                  :class="{ 'li-checked': item.checked }"
                  :key="index" @click="item.checked = !item.checked">
                  <span class="bk-trigger-icon">
                    <i class="bk-itsm-icon icon-info-circle" :class="[item.iconKey]" style="font-size: 24px"></i>
                  </span>
                  <span class="bk-trigger-name" :title="item.name">{{ item.name || '--' }}</span>
                  <span class="bk-trigger-delete">
                    <bk-checkbox :value="item.checked"></bk-checkbox>
                  </span>
                </li>
              </ul>
            </template>
          </div>
          <div slot="footer" class="trigger-dialog-footer">
            <bk-checkbox :value="Boolean((triggerDialogInfo.list.length === citeList.length) && triggerDialogInfo.list.length)"
              :ext-cls="'checkbox'"
              :disabled="!triggerDialogInfo.list.length"
              @change="selectAllFn">{{$t(`m.taskTemplate['全选']`)}}</bk-checkbox>
            <span>{{$t(`m.taskTemplate['已选']`)}}<span>{{citeList.length}}</span>个</span>
            <bk-button theme="primary"
              data-test-id="common-trigger-confirm"
              class="mr10"
              :title="$t(`m.taskTemplate['确定']`)"
              @click="citeTrigger">
              {{$t(`m.taskTemplate['确定']`)}}
            </bk-button>
            <bk-button theme="default"
              class="mr10"
              :title="$t(`m.taskTemplate['取消']`)"
              @click="initDialogInfo">
              {{$t(`m.taskTemplate['取消']`)}}
            </bk-button>
          </div>
        </bk-dialog>
      </template>
      <!-- 新增触发器 -->
      <template>
        <bk-sideslider
          :is-show.sync="triggerSliderInfo.isShow"
          :title="triggerSliderInfo.title"
          :width="triggerSliderInfo.width">
          <div slot="content" v-bkloading="{ isLoading: triggerSliderInfo.addLoading }" style="min-height: 300px;">
            <add-trigger
              v-if="triggerSliderInfo.isShow"
              :node-type="nodeType"
              :trigger-info="triggerSliderInfo.item"
              :origin-info-to-trigger="originInfoToTrigger"
              @closeTrigger="triggerSliderInfo.isShow = false"
              @getList="getBoundTriggerList">
            </add-trigger>
          </div>
        </bk-sideslider>
      </template>
    </div>
  </div>
</template>
<script>
  import addTrigger from '../../publicTrigger/addTrigger.vue';
  import collapseTransition from '@/utils/collapse-transition.js';
  import { errorHandler } from '../../../../utils/errorHandler';

  export default {
    name: 'commonTriggerList',
    components: {
      addTrigger,
      collapseTransition,
    },
    props: {
      sourceId: {
        type: [String, Number],
        default: '',
      },
      stepSignal: {
        type: String,
        default: '',
      },
      origin: {
        type: String,
        default: 'task',
      },
      sender: {
        type: [Number, String],
        default: '',
      },
      templateStage: {
        type: String,
        default: '',
      },
      table: {
        type: [Number, String],
        default: '',
      },
      nodeType: {
        type: String,
        default: '',
      },
    },
    data() {
      return {
        boundTriggerList: [],
        boundListLoading: false,
        showMoreConfig: false,
        triggerDialogInfo: {
          isShow: false,
          searchKey: '',
          list: [],
          listLoading: false,
        },
        triggerSliderInfo: {
          isShow: false,
          title: this.$t('m.taskTemplate[\'创建触发器\']'),
          width: 950,
          addLoading: false,
          item: {},
        },
        iconList: [
          { key: 'icon-icon-notice-new', name: '', typeName: 'message' },
          { key: 'icon-icon-user-new', name: '', typeName: 'user' },
          { key: 'icon-icon-status-new', name: '', typeName: 'status' },
          { key: 'icon-icon-api-new', name: '', typeName: 'api' },
        ],
        originInfoToTrigger: {},
        // 保存任务、节点、流程区别信息
        stage: '',
        signal: '', // 信号
        type: '',
        sourceType: '',
        senderId: '',
        triggerEventListFilter: '',
      };
    },
    computed: {
      citeList() {
        return this.triggerDialogInfo.list.filter(trigger => trigger.checked);
      },
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
      openFunction() {
        return this.$store.state.openFunction;
      },
      // 当前分类下的所有信号
      allSignal() {
        const SIGNAL_MAP = {
          state: 'STATE',
          transition: 'TRANSITION',
          workflow: 'FLOW',
        };
        // task
        if (this.stepSignal) {
          return this.stepSignal;
        }
        if (SIGNAL_MAP[this.origin]) {
          return Object.keys(this.globalChoise.trigger_signals[SIGNAL_MAP[this.origin]]).join(',');
        }
        return '';
      },
    },
    watch: {
      sourceId(newVal) {
        if (newVal) {
          this.initData();
        }
      },
      stepSignal() {
        this.initData();
      },
    },
    async mounted() {
      await this.initData();
    },
    methods: {
      async initData() {
        this.initParams();
        this.setFilterSignal();
        this.getPublicTriggerList();
        await this.getBoundTriggerList();
      },
      initParams() {
        this.senderId = this.sourceId;
        this.sourceType = 'workflow';
        // 任务模板配置
        if (this.stepSignal) {
          this.sourceType = 'task';
          this.triggerEventListFilter = 'TASK';
          this.type = 'task_schemas';
          this.stage = this.templateStage;
          return;
        }
        // 节点
        if (this.origin === 'state') {
          this.triggerEventListFilter = 'STATE';
          this.senderId = this.sender;
          this.type = 'states';
        }
        // 线条
        if (this.origin === 'transition') {
          this.showMoreConfig = true;
          this.triggerEventListFilter = 'TRANSITION';
          this.senderId = this.sender;
          this.type = 'transitions';
        }
        // 创建流程
        if (this.origin === 'workflow') {
          this.showMoreConfig = true;
          this.triggerEventListFilter = 'FLOW';
          this.type = 'templates';
        }
      },
      /**
       * 剔除不必要触发事件(信号)
       * @param { Array } condition 剔除条件
       */
      setFilterSignal(condition = []) {
        let conditions = condition;
        if (
          ['TASK', 'TASK-SOPS', 'SIGN'].indexOf(this.nodeType) > -1
          && this.origin === 'state'
        ) { // 根据节点类型过滤
          conditions = Array.from(new Set(['CLAIM_STATE', 'DELIVER_STATE', 'DISTRIBUTE_STATE', ...condition]));
        }
        const signalList = this.allSignal.split(',');
        this.signal = signalList.filter(key => conditions.indexOf(key) === -1).join(',');
      },
      async getBoundTriggerList() {
        if (!this.sourceId) {
          return;
        }
        const params = {
          source_id: this.sourceId,
          source_type: this.sourceType,
          sender: this.senderId,
          signal__in: this.signal,
          project_key: this.$store.state.project.id,
        };
        this.boundListLoading = true;
        await this.$store.dispatch('taskTemplate/getTemplateTriggers', params).then((res) => {
          this.boundTriggerList = res.data.map(trigger => ({
            ...trigger,
            iconKey: this.iconList.find(icon => icon.typeName === trigger.icon).key,
          }));
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.showMoreConfig = Boolean(this.boundTriggerList.length) || this.origin === 'workflow' || this.origin === 'transition';
            this.boundListLoading = false;
          });
      },
      // 全选函数
      selectAllFn() {
        const flag = this.triggerDialogInfo.list.length !== this.citeList.length;
        this.triggerDialogInfo.list.forEach((trigger) => {
          trigger.checked = flag;
        });
      },
      openNew(type, item = {}) {
        this.originInfoToTrigger = {
          id: this.sourceId,
          signal: this.signal,
          sender: this.senderId,
          filter: this.triggerEventListFilter,
          source: this.sourceType,
          type: this.type,
          stage: this.stage,
        };
        if (type === 'cite') {
          // 这里还有初始化已有配置的逻辑，todo
          this.triggerDialogInfo.isShow = true;
        } else {
          this.triggerSliderInfo.item = item;
          this.triggerSliderInfo.isShow = true;
        }
      },
      citeTrigger() {
        const params = {
          project_key: this.$store.state.project.id,
          src_trigger_ids: this.citeList.map(item => item.id),
          dst_source_id: this.sourceId,
          dst_source_type: this.sourceType,
          dst_sender: this.senderId,
        };
        this.$store.dispatch('taskTemplate/patchCloneTriggers', params).then(() => {
          this.$bkMessage({
            message: this.$t('m.taskTemplate[\'引用成功\']'),
            theme: 'success',
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.triggerDialogInfo.isShow = false;
            this.getBoundTriggerList();
          });
      },
      // 删除触发器
      delTrigger(trigger) {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.taskTemplate[\'确认删除触发器？\']'),
          subTitle: this.$t('m.taskTemplate[\'一旦删除，该触发器相关的动作将会一并删除。\']'),
          confirmFn: () => {
            this.doDelTrigger(trigger);
          },
        });
      },
      doDelTrigger(trigger) {
        this.$store.dispatch('taskTemplate/deleteTrigger', trigger.id).then(() => {
          this.$bkMessage({
            message: this.$t('m.flowManager[\'删除成功\']'),
            theme: 'success',
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.getBoundTriggerList();
          });
      },
      getPublicTriggerList() {
        const params = {
          // 来源为公共触发器，id为0
          source_id: 0,
          source_type: 'basic',
          sender: 0,
          is_draft: false,
          signal__in: this.signal,
          name__icontains: this.triggerDialogInfo.searchKey,
          project_key: this.$store.state.project.id,
        };
        if (this.table) {
          params.source_table_id = this.table;
        }
        this.triggerDialogInfo.listLoading = true;
        this.$store.dispatch('taskTemplate/getTemplateTriggers', params).then((res) => {
          this.triggerDialogInfo.list = res.data.map(pubTrigger => ({
            ...pubTrigger,
            checked: false,
            iconKey: this.iconList.find(icon => icon.typeName === pubTrigger.icon).key,
          }));
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.triggerDialogInfo.listLoading = false;
          });
      },
      // 引用/无触发器新建
      newTrigger() {
        this.initDialogInfo();
        this.$router.push({
          name: 'projectTrigger',
          query: {
            project_id: this.$route.query.project_id,
          },
        });
      },
      initDialogInfo() {
        this.triggerDialogInfo.isShow = false;
        this.triggerDialogInfo.searchKey = '';
      },
      searchInfo() {
        this.getPublicTriggerList();
      },
      clearSearch() {
        this.triggerDialogInfo.searchKey = '';
        this.getPublicTriggerList();
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../publicTrigger/triggerCss/index';
    @import '../taskCss/commonTrigger';
    @import '~@/scss/common-section-card.scss';
</style>
