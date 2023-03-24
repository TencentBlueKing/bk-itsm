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
    <div class="is-title" :class="{ 'bk-title-left': !sliderStatus }">
      <p class="bk-come-back">
        {{ $t(`m["触发器"]`) }}
      </p>
    </div>
    <div class="itsm-page-content">
      <empty-tip
        v-if="projectId && !isLoading && triggerList.length === 0 && searchToggle"
        :title="emptyTip.title"
        :sub-title="emptyTip.subTitle"
        :desc="emptyTip.desc"
        :links="emptyTip.links">
        <template slot="btns">
          <bk-button
            data-test-id="triggers_button_create_permission"
            :theme="'primary'"
            v-cursor="{ active: !hasPermission(['triggers_create'], $store.state.project.projectAuthActions) }"
            :class="{
              'btn-permission-disable': !hasPermission(['triggers_create'], $store.state.project.projectAuthActions)
            }"
            @click="addTrigger">
            {{ $t('m["立即创建"]') }}
          </bk-button>
        </template>
      </empty-tip>
      <template v-else>
        <!-- 提示信息 -->
        <div class="bk-itsm-version itsm-notify" v-if="versionStatus" style="margin: 10px 20px 10px 0;">
          <div class="notify-icon">
            <i class="bk-icon icon-info-circle"></i>
          </div>
          <div class="notify-content">
            {{ $t('m.trigger["公共触发器：供其他流程在配置过程中引用。"]') }} <br />
            {{ $t('m.trigger["引用原则：与引用位置相匹配的触发器。如：在节点中引用触发器，只能引用“触发事件类型=节点信号”的公共触发器。在流转条件配置时引用触发器，只能引用“触发事件类型=线条信号”的公共触发器。系统会根据引用位置来自动过滤不适用的公共触发器。"]') }}
          </div>
          <i class="bk-icon icon-close" @click="closeVersion"></i>
        </div>
        <div class="bk-normal-search">
          <bk-button :theme="'primary'"
            data-test-id="triggers_button_create"
            v-cursor="{ active: !hasPermission(['triggers_create'], $store.state.project.projectAuthActions) }"
            :title="$t(`m.managePage['新增']`)"
            icon="plus"
            :class="['mr10', 'plus-cus', {
              'btn-permission-disable': !hasPermission(['triggers_create'], $store.state.project.projectAuthActions)
            }]"
            @click="addTrigger">
            {{ $t('m.managePage["新增"]') }}
          </bk-button>
          <div class="bk-search-key">
            <bk-input
              data-test-id="triggers_button_search"
              :clearable="true"
              :right-icon="'bk-icon icon-search'"
              v-model="searchKey"
              @enter="searchInfo"
              @clear="clearSearch">
            </bk-input>
          </div>
        </div>
        <div style="min-height: 300px;" v-bkloading="{ isLoading: isLoading }">
          <!-- table -->
          <ul class="bk-trigger-content">
            <li v-for="(item, index) in triggerList"
              :key="index">
              <span class="bk-trigger-icon">
                <i class="bk-itsm-icon icon-info-circle icon-slide" style="font-size: 24px"></i>
              </span>
              <span class="bk-trigger-name"
                :title="item.name"
                @click="changeTrigger(item, index)">
                {{ item.name || '--' }}
                <span v-if="item.is_draft" style="color: #3A84FF;">{{ $t('m.taskTemplate["(草稿)"]') }}</span>
              </span>
              <span class="bk-trigger-delete" @click.stop="deleteTrigger(item, index)">
                <i class="bk-icon icon-delete"></i>
              </span>
            </li>
          </ul>
          <!-- <div v-if="!searchToggle" class="search-tip">{{ $t('m["未查找到触发器"]') }}</div> -->
          <empty style="text-align: center;" v-if="triggerList.length === 0" :is-search="!searchToggle" @onClearSearch="onClearSearch"></empty>
        </div>
      </template>
    </div>
    <!-- 新建触发器弹窗 -->
    <div class="bk-add-slider">
      <bk-sideslider
        :is-show.sync="sliderInfo.show"
        :title="sliderInfo.title"
        :width="sliderInfo.width">
        <div slot="content"
          v-bkloading="{ isLoading: sliderInfo.addLoading }"
          style="min-height: 300px;">
          <add-trigger v-if="sliderInfo.show"
            :trigger-info="triggerInfo"
            :project-id="projectId"
            @closeTrigger="closeTrigger"
            @getList="getList">
          </add-trigger>
        </div>
      </bk-sideslider>
    </div>
  </div>
</template>
<script>
  import { errorHandler } from '../../../utils/errorHandler';
  import permission from '@/mixins/permission.js';
  import addTrigger from './addTrigger.vue';
  import EmptyTip from '../../project/components/emptyTip.vue';
  import Empty from '../../../components/common/Empty.vue';

  export default {
    name: 'publicTrigger',
    components: {
      addTrigger,
      EmptyTip,
      Empty,
    },
    mixins: [permission],
    props: {
      projectId: String,
    },
    data() {
      return {
        versionStatus: true,
        searchKey: '',
        searchToggle: false,
        triggerList: [],
        iconList: [
          { key: 'icon-icon-notice-new', name: '', typeName: 'message' },
          { key: 'icon-icon-user-new', name: '', typeName: 'user' },
          { key: 'icon-icon-status-new', name: '', typeName: 'status' },
          { key: 'icon-icon-api-new', name: '', typeName: 'api' },
        ],
        isLoading: false,
        // 新增
        sliderInfo: {
          show: false,
          title: this.$t('m.taskTemplate["创建触发器"]'),
          width: 950,
          addLoading: false,
        },
        triggerInfo: {},
        emptyTip: {
          title: this.$t('m[\'当前项目下还没有 <触发器>\']'),
          subTitle: this.$t('m[\'有些情况下，我们需要在服务特殊的人员或情境时，让流程相关的服务人员感知到高优处理级别、响应时长等要求，并严阵以待！<触发器>可以设置在服务流程中，当服务信息满足指定条件后，自动触发某些预设好的指令。\']'),
          desc: [
            {
              src: require('../../../images/illustration/set-trigger.svg'),
              title: this.$t('m[\'设置触发器的规则和动作\']'),
              content: this.$t('m[\'<触发器>可以设置通用的事件、亦或是服务流程中的特定事件触发，支持复杂的多条分支和多层嵌套条件判断，并配置对应的处理动作，如API自动调用、或者更改服务单据的字段信息等等...\']'),
            },
            {
              src: require('../../../images/illustration/auto-excute.svg'),
              title: this.$t('m[\'事件触发满足时自动执行\']'),
              content: this.$t('m[\'当用户或系统行为满足条件后，触发器会按照用户预设的动作自动执行；触发器可以帮助用户快速的为一些公共事件或人员，在全局的服务流程范围内设置同样的处理逻辑。\']'),
            },
          ],
          links: [
            {
              text: this.$t('m[\'如何在服务流程中配置触发器？\']'),
              btn: this.$t('m[\'产品白皮书\']'),
              href: 'https://bk.tencent.com/docs/document/6.0/145/6603',
            },
          ],
        },
      };
    },
    computed: {
      sliderStatus() {
        return this.$store.state.common.slideStatus;
      },
    },
    mounted() {
      this.getList();
    },
    methods: {
      closeVersion() {
        this.versionStatus = false;
      },
      // 新增触发器
      addTrigger() {
        if (!this.hasPermission(['triggers_create'], this.$store.state.project.projectAuthActions)) {
          const { projectInfo } = this.$store.state.project;
          const resourceData = {
            project: [{
              id: projectInfo.key,
              name: projectInfo.name,
            }],
          };
          this.applyForPermission(['triggers_create'], this.$store.state.project.projectAuthActions, resourceData);
          return;
        }
        this.triggerInfo = {};
        this.sliderInfo.title = this.$t('m.taskTemplate["创建触发器"]');
        this.sliderInfo.show = true;
      },
      // 搜索
      searchInfo() {
        this.getList();
      },
      onClearSearch() {
        this.searchKey = '';
        this.getList();
      },
      clearSearch() {
        this.getList();
      },
      getList() {
        const params = {
          source_id__in: 0,
          source_type__in: 'basic',
          sender__in: 0,
          name__icontains: this.searchKey,
        };
        if (this.projectId) {
          params.project_key = this.projectId;
        }
        this.searchToggle = !this.searchKey;
        this.isLoading = true;
        this.$store.dispatch('trigger/getTriggerTable', params).then((res) => {
          this.triggerList = res.data.map(trigger => ({
            ...trigger,
            iconKey: this.iconList.find(icon => icon.typeName === trigger.icon).key,
          }));
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isLoading = false;
          });
      },
      // 修改触发器
      changeTrigger(item) {
        if (!this.hasPermission(['triggers_manage'], [...this.$store.state.project.projectAuthActions, ...item.auth_actions])) {
          const { projectInfo } = this.$store.state.project;
          const resourceData = {
            project: [{
              id: projectInfo.key,
              name: projectInfo.name,
            }],
            trigger: [{
              id: item.id,
              name: item.name,
            }],
          };
          this.applyForPermission(['triggers_manage'], [...this.$store.state.project.projectAuthActions, ...item.auth_actions], resourceData);
          return;
        }
        this.triggerInfo = item;
        this.sliderInfo.title = this.$t('m.trigger["编辑触发器"]');
        this.sliderInfo.show = true;
      },
      closeTrigger() {
        this.sliderInfo.show = false;
      },
      // 删除触发器
      deleteTrigger(item) {
        if (!this.hasPermission(['triggers_manage'], [...this.$store.state.project.projectAuthActions, ...item.auth_actions])) {
          const { projectInfo } = this.$store.state.project;
          const resourceData = {
            project: [{
              id: projectInfo.key,
              name: projectInfo.name,
            }],
            trigger: [{
              id: item.id,
              name: item.name,
            }],
          };
          this.applyForPermission(['triggers_manage'], [...this.$store.state.project.projectAuthActions, ...item.auth_actions], resourceData);
          return;
        }
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.trigger["确认删除触发器？"]'),
          subTitle: this.$t('m.trigger["触发器删除将不可使用"]'),
          confirmFn: () => {
            const { id } = item;
            this.$store.dispatch('trigger/deleteTrigger', id).then(() => {
              this.$bkMessage({
                message: this.$t('m.systemConfig["删除成功"]'),
                theme: 'success',
              });
              this.getList();
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {

              });
          },
        });
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import './triggerCss/index.scss';
    .search-tip {
        text-align: center;
        font-size: 14px;
        color: #63656e;
        margin: 40px;
    }
    .itsm-notify {
        padding: 6px 10px;
        padding-right: 30px;
        display: flex;
        justify-content: start;
        line-height: 20px;
        .notify-icon .icon-info-circle {
            margin-top: 4px;
        }
        .notify-content {
            line-height: 20px;
        }
    }
</style>
