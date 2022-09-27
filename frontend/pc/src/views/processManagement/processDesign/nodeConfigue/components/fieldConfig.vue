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
  <div class="bk-field-info mb20">
    <p v-if="isShowTitle" class="bk-field-title">{{ $t(`m['字段配置']`) }}</p>
    <div class="bk-node-btn">
      <bk-button
        data-test-id="fieldConfig-button-addField"
        v-if="configur.type !== 'APPROVAL'"
        :theme="'default'"
        :title="$t(`m.treeinfo['新增字段']`)"
        class="mr10"
        @click="addField">
        {{$t(`m.treeinfo['新增字段']`)}}
      </bk-button>
      <bk-button
        data-test-id="fieldConfig-button-addModelField"
        v-if="configur.type !== 'APPROVAL' && configur.type !== 'SIGN' && !templateStage"
        :theme="'default'"
        :title="$t(`m.treeinfo['选择模型字段']`)"
        class="mr10"
        @click="openAddModule">
        {{$t(`m.treeinfo['选择模型字段']`)}}
      </bk-button>
      <bk-button :theme="'default'"
        data-test-id="fieldConfig-button-previewField"
        :title="$t(`m.treeinfo['字段预览']`)"
        class="mr10"
        style="float: right; border: 0"
        :disabled="!showTabList.length"
        @click="previewField">
        <i class="bk-itsm-icon icon-itsm-icon-three" style="font-size: 16px"></i>
        {{$t(`m.treeinfo['字段预览']`)}}
      </bk-button>
    </div>
    <!-- 表格拖拽 -->
    <div class="mt15 bk-draggable" v-bkloading="{ isLoading: isDataLoading }">
      <table class="bk-draggable-table">
        <thead>
          <tr>
            <th>{{ $t('m.treeinfo["字段名称"]') }}</th>
            <th style="max-width: 150px;">{{ $t('m.treeinfo["唯一标识"]') }}</th>
            <th>{{ $t('m.treeinfo["字段类型"]') }}</th>
            <!-- <th style="max-width: 100px;">{{ $t('m.treeinfo["字段值"]') }}</th> -->
            <th>{{ $t('m.treeinfo["是否只读"]') }}</th>
            <th style="min-width: 50px;">{{ $t('m.treeinfo["布局"]') }}</th>
            <th style="max-width: 100px;">{{ $t('m.treeinfo["字段描述"]') }}</th>
            <th>{{ $t('m.treeinfo["是否必填"]') }}</th>
            <th>{{ $t('m.treeinfo["更新人"]') }}</th>
            <th>{{ $t('m.treeinfo["操作"]') }}</th>
          </tr>
        </thead>
        <draggable tag="tbody" v-model="showTabList" @end="updateInfo" handle=".move-handler-content">
          <template v-if="showTabList.length">
            <tr v-for="(item, index) in showTabList" :key="index">
              <td class="move-handler-content">
                <span><i class="bk-itsm-icon icon-move-new move-handler"></i>{{item.name}}</span>
              </td>
              <td style="max-width: 150px;" :title="item.key">
                {{item.key}}
              </td>
              <td>
                {{item.typeName || '--'}}
              </td>
              <!-- <td style="max-width: 100px;" :title="item.fieldValue">
                                {{item.fieldValue || '--'}}
                            </td> -->
              <td style="max-width: 100px;"
                :title="item.is_readonly ? $t(`m.treeinfo['是']`) : $t(`m.treeinfo['否']`)">
                {{item.is_readonly ? $t('m.treeinfo["是"]') : $t('m.treeinfo["否"]')}}
              </td>
              <td style="min-width: 50px;">
                {{item.layout === 'COL_6' ? $t('m.treeinfo["半行"]') : $t('m.treeinfo["整行"]')}}
              </td>
              <td style="max-width: 100px;" :title="item.desc">
                <pre><span>{{item.desc || '--'}}</span></pre>
              </td>
              <td>
                {{item.is_required || '--'}}
              </td>
              <td>
                {{item.updated_by || '--'}}
              </td>
              <td>
                <bk-button theme="primary"
                  class="table-opt-button"
                  :disabled="checkEditDisabled(item)"
                  text
                  @click="openField(item)">
                  {{ $t('m.user["编辑"]') }}
                </bk-button>
                <bk-button theme="primary"
                  class="table-opt-button"
                  :disabled="checkDeleteDisabled(item)"
                  text
                  @click="deleteTable(item)">
                  {{ $t('m.user["删除"]') }}
                </bk-button>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-cloak>
              <td colspan="10" class="bk-none-content">
                <i class="bk-table-empty-icon bk-icon icon-empty"></i>
                <p class="bk-none-info">{{ $t('m.treeinfo["暂无数据"]') }}</p>
              </td>
            </tr>
          </template>
        </draggable>
      </table>
    </div>
    <!-- 字段预览 -->
    <bk-dialog v-model="processInfo.isShow"
      width="760"
      :position="processInfo.position"
      :draggable="processInfo.draggable"
      :title="processInfo.title"
      :render-directive="'if'"
      :ext-cls="'bk-preview-overflow'">
      <field-preview :fields="previewTab"></field-preview>
      <div slot="footer">
        <bk-button
          theme="default"
          @click="processInfo.isShow = false">
          {{ $t('m.home["取消"]') }}
        </bk-button>
      </div>
    </bk-dialog>
    <!-- 新增字段 -->
    <bk-sideslider
      :is-show.sync="sliderInfo.show"
      :title="sliderInfo.title"
      :width="sliderInfo.width">
      <div class="p20" slot="content" v-if="sliderInfo.show">
        <add-field
          :change-info="changeInfo"
          :template-info="templateInfo"
          :template-stage="templateStage"
          :nodes-list="nodesList"
          :add-origin="addOrigin"
          :table-list="showTabList"
          :is-edit-public="isEditPublic"
          :workflow="flowInfo ? flowInfo.id : 0"
          :state="configur.id ? configur.id : 0"
          @closeShade="closeShade">
        </add-field>
      </div>
    </bk-sideslider>
    <!-- 模型字段 -->
    <bk-dialog
      v-model="moduleInfo.isShow"
      :render-directive="'if'"
      :width="moduleInfo.width"
      :header-position="moduleInfo.headerPosition"
      :loading="secondClick"
      :auto-close="moduleInfo.autoClose"
      :mask-close="moduleInfo.autoClose"
      @confirm="submitModule">
      <p slot="header">{{ $t(`m.treeinfo["选择模型字段"]`) }}</p>
      <div class="bk-add-module">
        <inherit-state
          ref="inheritState"
          :workflow="flowInfo ? flowInfo.id : 0"
          :state="configur.id ? configur.id : 0"
          :configur="configur"
          :show-tab-list="showTabList">
        </inherit-state>
      </div>
    </bk-dialog>
  </div>
</template>
<script>
  import draggable from 'vuedraggable';
  import apiFieldsWatch from '../../../../commonMix/api_fields_watch';
  import fieldPreview from './fieldPreview.vue';
  import addField from '../addField';
  import inheritState from './inheritState';
  import { errorHandler } from '../../../../../utils/errorHandler';

  export default {
    name: 'fieldInfo',
    components: {
      draggable,
      fieldPreview,
      addField,
      inheritState,
    },
    mixins: [apiFieldsWatch],
    props: {
      // 流程信息
      flowInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      // 节点信息
      configur: {
        type: Object,
        default() {
          return {};
        },
      },
      templateStage: {
        type: String,
        default: '',
      },
      templateInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      isShowTitle: {
        type: Boolean,
        default() {
          return false;
        },
      },
    },
    data() {
      return {
        nodesList: [],
        isDataLoading: false,
        secondClick: false,
        showTabList: [],
        // 字段信息
        changeInfo: {},
        // 新增编辑字段
        sliderInfo: {
          title: this.$t('m.treeinfo["新增字段"]'),
          show: false,
          width: 700,
        },
        // 字段预览
        processInfo: {
          isShow: false,
          title: this.$t('m.treeinfo["字段预览"]'),
          position: {
            top: 150,
          },
          draggable: true,
        },
        previewTab: [],
        // 模型字段
        isEditPublic: false,
        moduleInfo: {
          isShow: false,
          width: 700,
          headerPosition: 'left',
          autoClose: false,
        },
        // 任务模板添加字段与公共字段逻辑保持一致
        addOrigin: {
          isOther: false,
        },
      };
    },
    computed: {
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
    },
    watch: {
      'templateInfo.id'() {
        this.initData();
      },
      templateStage() {
        this.initData();
      },
    },
    async mounted() {
      await this.initData();
    },
    beforeDestroy() {
      this.clearFieldsIndexInfo();
    },
    methods: {
      async initData() {
        if (this.templateStage) {
          this.addOrigin.isOther = true;
          this.addOrigin.addOriginInfo = {
            type: 'templateField',
            addUrl: 'taskTemplate/createTemplateField',
            updateUrl: 'taskTemplate/updateTemplateField',
          };
        }
        await this.getTableList();
      },
      // 初始化数据
      getTableList() {
        let url = 'deployCommon/getFieldList';
        const params = {};
        if (this.templateInfo.id) {
          url = 'taskTemplate/getTemplateFields';
          params.task_schema_id = this.templateInfo.id;
          params.stage = this.templateStage;
        } else if (this.flowInfo && this.flowInfo.id) {
          params.workflow = this.flowInfo.id;
          params.state = this.configur.id;
        } else {
          return;
        }
        this.isDataLoading = true;
        this.$store.dispatch(url, params).then((res) => {
          this.showTabList = this.orderByCacheInfo(res.data);
          this.showTabList.forEach((item) => {
            // 字段类型
            this.globalChoise.field_type.forEach((node) => {
              if (item.type === node.typeName) {
                this.$set(item, 'typeName', node.name);
              }
            });
            if (item.type === 'COMPLEX-MEMBERS') {
              this.$set(item, 'typeName', this.$t('m.newCommon[\'处理人\']'));
            }
            if (item.type === 'SOPS_TEMPLATE') {
              this.$set(item, 'typeName', this.$t('m.newCommon[\'流程模板\']'));
            }
            // 是否必填
            this.globalChoise.validate_type.forEach((node) => {
              if (item.validate_type === node.typeName) {
                this.$set(item, 'is_required', node.name);
              }
            });
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
      },
      // 是否可以删除
      checkDeleteDisabled(item) {
        const defaultKet = ['impact', 'urgency', 'priority', 'current_status'];
        const taskDefaultKet = ['processors', 'task_name'];
        if (item.is_builtin && this.configur.is_first_state && defaultKet.indexOf(item.key) === -1) {
          return true;
        }
        if (item.meta.code === 'APPROVE_RESULT') {
          return true;
        }
        if (taskDefaultKet.indexOf(item.key) !== -1) {
          return true;
        }
        // 审批节点不能操作
        if (this.configur.type === 'APPROVAL') {
          return true;
        }
        return false;
      },
      // 是否可以编辑
      checkEditDisabled() {
        return this.configur.type === 'APPROVAL';
      },
      // 拖动结束后的数据
      updateInfo() {
        this.cacheFieldsIndexInfo();
      },
      // 新增编辑弹窗
      closeShade() {
        this.sliderInfo.show = false;
      },
      /**
       * @description 根据缓存顺序进行排序
       * 拖动字段顺序信息将存在缓存中，避免新增字段成功后重新刷新列表，
       * 因为之前字段列表顺序未保存而需要再次重新编辑。
       */
      orderByCacheInfo(data) {
        const hasCacheIndexList = [];
        const newList = [];
        data.forEach((item) => {
          const index = this.getOneFieldCacheIndex(item.id);
          if (index || index === 0) {
            hasCacheIndexList[index] = item;
          } else {
            newList.push(item);
          }
        });
        return hasCacheIndexList.filter(m => !!m).concat(newList);
      },
      // 缓存当前字段列表顺序
      cacheFieldsIndexInfo() {
        const indexMap = this.showTabList.reduce((acc, curr, index) => {
          // username_流程id_节点_字段id
          const key = `${window.username}_${this.flowInfo.id}_${this.configur.id}_${curr.id}`;
          acc[key] = index;
          return acc;
        }, {});
        sessionStorage.setItem('fieldsIndexMap', JSON.stringify(indexMap));
      },
      // 获取单个字段缓存排序 index
      getOneFieldCacheIndex(id) {
        const info = sessionStorage.getItem('fieldsIndexMap') || '{}';
        const indexMap = JSON.parse(info);
        const key = `${window.username}_${this.flowInfo.id}_${this.configur.id}_${id}`;
        return indexMap[key];
      },
      // 清除字段排序缓存信息
      clearFieldsIndexInfo() {
        sessionStorage.removeItem('fieldsIndexMap');
      },
      // 获取前置节点的字段信息
      getFrontNodesList() {
        if (!this.configur.id && !this.templateInfo.id) {
          return;
        }
        let url = '';
        const params = {};
        if (this.configur.id) {
          url = 'apiRemote/get_related_fields';
          params.workflow = this.workflow;
          params.state = this.configur.id;
        }
        if (this.templateInfo.id) {
          url = 'taskTemplate/getFrontFieldsList';
          params.id = this.templateInfo.id;
          params.stage = this.templateStage;
        }
        this.$store.dispatch(url, params).then((res) => {
          this.nodesList = res.data;
          this.sliderInfo.show = true;
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 新增字段
      addField() {
        this.changeInfo = {
          workflow: '',
          id: '',
          key: '',
          name: '',
          type: 'STRING',
          desc: '',
          layout: 'COL_12',
          validate_type: 'REQUIRE',
          choice: [],
          is_builtin: false,
          source_type: 'CUSTOM',
          source_uri: '',
          regex: 'EMPTY',
          custom_regex: '',
          is_tips: false,
          tips: '',
          meta: {},
        };
        this.sliderInfo.title = this.$t('m.treeinfo["新增字段"]');
        this.getFrontNodesList();
      },
      openField(item) {
        this.changeInfo = item;
        this.changeInfo.is_tips = item.is_tips || false;
        this.sliderInfo.title = this.$t('m.treeinfo["编辑字段"]');
        this.getFrontNodesList();
      },
      // 字段预览
      previewField() {
        if (!this.showTabList.length) {
          return;
        }
        this.previewTab = this.showTabList;
        const priorityReadonly = this.previewTab.some(item => item.key === 'impact' || item.key === 'urgency');
        for (let i = 0; i < this.previewTab.length; i++) {
          for (let j = 0; j < this.previewTab[i].choice.length; j++) {
            this.previewTab[i].choice[j].typeName = this.previewTab[i].choice[0] ? this.previewTab[i].choice[0].key : '';
          }
          this.$set(this.previewTab[i], 'val', (this.previewTab[i].default || ''));
          this.$set(this.previewTab[i], 'showFeild', true);
          if (this.previewTab[i].key === 'priority' && !priorityReadonly) {
            this.$set(this.previewTab[i], 'is_readonly', false);
          }
        }
        this.processInfo.isShow = true;
        this.isNecessaryToWatch({ fields: this.previewTab }, 'workflow');
      },
      // 删除字段
      deleteTable(item) {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.treeinfo["确认删除此字段？"]'),
          subTitle: this.$t('m.treeinfo["字段一旦删除，此字段将不在可用。请谨慎操作。"]'),
          confirmFn: () => {
            let url = 'deployCommon/deleteField';
            const patch = {
              id: item.id,
              params: {
                state_id: this.configur.id,
              },
            };
            if (this.templateInfo.id) {
              url = 'taskTemplate/deleteTemplateField';
              delete patch.params;
            }
            if (this.secondClick) {
              return;
            }
            this.secondClick = true;
            this.$store.dispatch(url, patch).then(() => {
              this.$bkMessage({
                message: this.$t('m.systemConfig["删除成功"]'),
                theme: 'success',
              });
              this.getTableList();
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.secondClick = false;
              });
          },
        });
      },
      // 模型字段
      openAddModule() {
        this.moduleInfo.isShow = true;
      },
      submitModule() {
        const checkList = this.$refs.inheritState.checkList.filter(item => !item.is_disabled);
        if (checkList.length) {
          const params = {
            fields: checkList,
          };
          const { id } = this.configur;
          if (this.secondClick) {
            return;
          }
          this.secondClick = true;
          this.$store.dispatch('basicModule/add_fields_from_table', { params, id }).then(() => {
            this.$bkMessage({
              message: this.$t('m.systemConfig["添加成功"]'),
              theme: 'success',
            });
            this.moduleInfo.isShow = false;
            this.getTableList();
          })
            .catch((res) => {
              errorHandler(res, this);
            })
            .finally(() => {
              this.secondClick = false;
            });
        } else {
          this.moduleInfo.isShow = false;
        }
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../../../scss/mixins/table.scss';
    @import '../../../../../scss/mixins/clearfix.scss';
    .bk-field-info{
        color: #63656E;
        font-size: 14px;
        .bk-field-title {
            display: block;
            height: 22px;
            margin: 8px 0px;
            color: #63656e;
        }
    }
    .bk-node-btn{
        font-size: 0;
    }

    .bk-service-name{

        h1{
            padding-left: 10px;
        }
    }

    .bk-add-module {
        max-height: 377px;
        overflow: auto;
    }
    .move-handler-content {

        .move-handler {
            margin-right: 5px;
            position: relative;
            top: -1px;
            opacity: 0;
            cursor: move;
        }
        &:hover{
            .move-handler{
                opacity: 1;
            }
        }
    }
    .bk-draggable {
        @include table;
        table{
            td{
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
        }
    }
    .table-opt-button {
        padding: 0 5px;
    }
</style>
