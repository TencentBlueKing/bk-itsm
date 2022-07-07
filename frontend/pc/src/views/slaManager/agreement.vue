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
  <div class="bk-itsm-service" ref="agreement">
    <template v-if="!changeInfo.isShow">
      <div class="is-title" :class="{ 'bk-title-left': !sliderStatus }">
        <p class="bk-come-back">
          {{ $t('m.slaContent["服务协议"]') }}
        </p>
      </div>
      <div class="itsm-page-content">
        <empty-tip
          v-if="!isDataLoading && pagination.count === 0 && searchToggle"
          :title="emptyTip.title"
          :sub-title="emptyTip.subTitle"
          :desc="emptyTip.desc"
          :links="emptyTip.links">
          <template slot="btns">
            <bk-button
              data-test-id="sla_button_createAgreement_permission"
              v-cursor="{ active: !hasPermission(['sla_agreement_create'], $store.state.project.projectAuthActions) }"
              theme="primary"
              :class="{
                'btn-permission-disable': !hasPermission(['sla_agreement_create'], $store.state.project.projectAuthActions)
              }"
              @click="addAgreement({}, 'sla_agreement_create')">
              {{ $t('m["立即创建"]') }}
            </bk-button>
          </template>
        </empty-tip>
        <template v-else>
          <!-- 提示信息 -->
          <div class="bk-itsm-version" v-if="versionStatus">
            <i class="bk-icon icon-info-circle"></i>
            <span>{{ $t('m.slaContent["服务协议：制定不同的服务协议内容。包括不同优先级下的服务模式，服务解决时长。可以制定多个不同的服务协议策略，它将会应用到具体的每个服务中。"]') }}</span>
            <i class="bk-icon icon-close" @click="closeVersion"></i>
          </div>
          <div class="bk-only-btn">
            <div class="bk-more-search">
              <bk-button
                data-test-id="sla_button_createAgreement"
                v-cursor="{ active: !hasPermission(['sla_agreement_create'], $store.state.project.projectAuthActions) }"
                :theme="'primary'"
                :title="$t(`m.managePage['新增']`)"
                icon="plus"
                :class="['mr10', 'plus-cus', {
                  'btn-permission-disable': !hasPermission(['sla_agreement_create'], $store.state.project.projectAuthActions)
                }]"
                @click="addAgreement({}, 'sla_agreement_create')">
                {{ $t('m.managePage["新增"]') }}
              </bk-button>
              <div class="bk-search-name">
                <div class="bk-search-content">
                  <bk-input
                    data-test-id="sla_button_searchAgreement"
                    :placeholder="moreSearch[0].placeholder || $t(`m.deployPage['请输入流程名']`)"
                    :clearable="true"
                    :right-icon="'bk-icon icon-search'"
                    v-model="moreSearch[0].value"
                    @enter="searchContent"
                    @clear="clearSearch">
                  </bk-input>
                </div>
                <bk-button :title="$t(`m.deployPage['更多筛选条件']`)"
                  icon=" bk-itsm-icon icon-search-more"
                  class="ml10 filter-btn"
                  @click="searchMore">
                </bk-button>
              </div>
            </div>
            <search-info
              ref="searchInfo"
              :more-search="moreSearch">
            </search-info>
          </div>
          <bk-table
            v-bkloading="{ isLoading: isDataLoading }"
            :data="dataList"
            :size="'small'"
            :pagination="pagination"
            @page-change="handlePageChange"
            @page-limit-change="handlePageLimitChange">
            <bk-table-column :label="$t(`m.slaContent['协议名称']`)">
              <template slot-scope="props">
                <bk-button
                  data-test-id="sla_button_agreementEditFromName"
                  v-if="!hasPermission(['sla_agreement_edit'], [...props.row.auth_actions, ...$store.state.project.projectAuthActions])"
                  v-cursor
                  text
                  theme="primary"
                  class="btn-permission-disable"
                  @click="addAgreement(props.row, 'sla_agreement_edit')">
                  {{props.row.name || '--'}}
                </bk-button>
                <span
                  v-else
                  data-test-id="sla_span_agreementEditFromName"
                  class="bk-lable-primary"
                  @click="addAgreement(props.row, 'sla_agreement_edit')"
                  :title="props.row.name">
                  {{props.row.name || '--'}}
                </span>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.slaContent['应用服务数']`)">
              <template slot-scope="props">
                <bk-popover placement="top" trigger="click" theme="light" max-width="500px">
                  <span style="cursor: pointer;" :title="props.row.service_count || '0'">{{props.row.service_count || '0'}}</span>
                  <div slot="content" style="white-space: normal;">
                    <p>{{ props.row.service_names.toString() }}</p>
                  </div>
                </bk-popover>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.slaContent['更新时间']`)" prop="update_at">
              <template slot-scope="props">
                <span :title="props.row.update_at">{{props.row.update_at || '--'}}</span>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.slaContent['更新人']`)">
              <template slot-scope="props">
                <span :title="props.row.updated_by">{{props.row.updated_by || '--'}}</span>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.slaContent['是否启用']`)">
              <template slot-scope="props">
                <span class="bk-status-color"
                  :class="{ 'bk-status-gray': !props.row.is_enabled }"></span>
                <span style="margin-left: 5px;"
                  :title="(props.row.is_enabled ? $t(`m.deployPage['启用']`) : $t(`m.deployPage['关闭']`))">
                  {{(props.row.is_enabled ? $t(`m.deployPage["启用"]`) : $t(`m.deployPage["关闭"]`))}}
                </span>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.slaContent['操作']`)" width="150">
              <template slot-scope="props">
                <!-- 编辑 -->
                <bk-button
                  data-test-id="sla_button_agreementEditFromOperate1"
                  v-if="!hasPermission(['sla_agreement_edit'], [...$store.state.project.projectAuthActions, ...props.row.auth_actions])"
                  v-cursor
                  text
                  theme="primary"
                  class="btn-permission-disable"
                  @click="addAgreement(props.row, 'sla_agreement_edit')">
                  {{ $t('m.deployPage["编辑"]')}}
                </bk-button>
                <bk-button
                  data-test-id="sla_button_agreementEditFromOperate2"
                  v-else
                  theme="primary"
                  text
                  @click="addAgreement(props.row, 'sla_agreement_edit')">
                  {{ $t('m.deployPage["编辑"]')}}
                </bk-button>
                <!-- 删除 -->
                <bk-button
                  data-test-id="sla_button_agreementDeleteFromOperate1"
                  v-if="!hasPermission(['sla_agreement_delete'], [...$store.state.project.projectAuthActions, ...props.row.auth_actions])"
                  v-cursor
                  text
                  theme="primary"
                  class="btn-permission-disable"
                  @click="deleteAgreement(props.row, ['sla_agreement_delete'])">
                  {{ $t('m.deployPage["删除"]') }}
                </bk-button>
                <bk-button theme="primary"
                  data-test-id="sla_button_agreementDeleteFromOperate2"
                  text
                  v-else-if="props.row.service_count > 0 || props.row.is_builtin"
                  :disabled="props.row.service_count > 0 || props.row.is_builtin"
                  :title="$t(`m.slaContent['应用服务数大于0或者服务协议属于系统内置的不可删除']`)">
                  {{ $t('m.deployPage["删除"]') }}
                </bk-button>
                <bk-button theme="primary" text v-else
                  data-test-id="sla_button_agreementDeleteFromOperate3"
                  @click="deleteAgreement(props.row)">
                  {{ $t('m.deployPage["删除"]') }}
                </bk-button>
              </template>
            </bk-table-column>
          </bk-table>
        </template>
      </div>
    </template>
    <!-- 新增/修改 -->
    <add-agreement
      v-else
      :model-list="modelList"
      :model-priority="modelPriority"
      :notify-event-list="notifyEventList"
      :change-info="changeInfo">
    </add-agreement>
  </div>
</template>

<script>
  import { errorHandler } from '../../utils/errorHandler';
  import searchInfo from '../commonComponent/searchInfo/searchInfo.vue';
  import addAgreement from './newAddAgreement';
  import EmptyTip from '../project/components/emptyTip.vue';
  import permission from '@/mixins/permission.js';
  import { mapState } from 'vuex';

  export default {
    name: 'agreement',
    components: {
      searchInfo,
      addAgreement,
      EmptyTip,
    },
    mixins: [permission],
    data() {
      return {
        isDataLoading: true,
        versionStatus: true,
        secondClick: false,
        // table数据和分页
        dataList: [],
        pagination: {
          current: 1,
          count: 10,
          limit: 10,
        },
        // 搜索
        moreSearch: [
          {
            name: this.$t('m.slaContent["协议名称"]'),
            key: 'name',
            placeholder: this.$t('m.slaContent["请输入协议名称"]'),
            type: 'input',
            typeKey: 'name',
            value: '',
            list: [],
          },
          {
            name: this.$t('m.deployPage["更新人"]'),
            type: 'member',
            typeKey: 'updated_by',
            multiSelect: true,
            value: [],
            list: [],
          },
          {
            name: this.$t('m.deployPage["启用状态"]'),
            type: 'select',
            typeKey: 'is_enabled',
            value: '',
            list: [
              { key: 0, name: this.$t('m.deployPage["关闭"]') },
              { key: 1, name: this.$t('m.deployPage["启用"]') },
            ],
          },
        ],
        searchToggle: false,
        notifyEventList: {},
        emailNotifyEventList: [],
        weixinNotifyEventList: [],
        // 服务模式
        modelList: [],
        modelPriority: [],
        // 新增 修改
        changeInfo: {
          isShow: false,
          is_reply_need: true,
          info: {},
        },
        emptyTip: {
          title: this.$t('m[\'当前项目下还没有 <SLA协议>\']'),
          subTitle: this.$t('m[\'SLA（即服务级别协议）是服务支撑团队与组织机构内最终用户之间的“服务合同”。通常，SLA 是通过定义所提供的服务必须遵守的质量标准以及交付服务的时间表来建立对服务和服务质量的清晰理解；加快服务响应时间、减少等待时长、降低运营成本，一套合理且适用的 SLA 将是您实现这些目标的最佳选择。\']'),
          desc: [
            {
              src: require('../../images/illustration/apply.svg'),
              title: this.$t('m[\'设计服务模式并制定协议\']'),
              content: this.$t('m[\'通常我们会先设定团队的服务时间段，然后进一步配置在规定的服务时间段内，针对不同的服务工单紧急程度约定响应和处理时长，为的是保障用户的服务体验、提升用户满意度。\']'),
            },
            {
              src: require('../../images/illustration/start-service.svg'),
              title: this.$t('m[\'为服务配置合适的 SLA\']'),
              content: this.$t('m[\'接下来就是为不同的服务配置合适的 SLA 了，因为很多服务的处理流程中可能会需要多个不同职能团队来处理，所以我们支持在一个服务内针对不同的流程区间设置差异化的服务协议，满足对不同服务团队的SLA要求。\']'),
            },
          ],
          links: [
            {
              text: this.$t('m[\'如何设计一套合理有效的 SLA ？\']'),
              btn: this.$t('m[\'产品白皮书\']'),
              href: 'https://bk.tencent.com/docs/document/6.0/145/6594',
            },
          ],
        },
      };
    },
    computed: {
      sliderStatus() {
        return this.$store.state.common.slideStatus;
      },
      ...mapState({
        noticeType: state => state.common.configurInfo.notify_type,
      }),
    },
    mounted() {
      this.getList(1);
      this.getModelList();
      this.getTicketHighlight();
      this.getModelPriority();
      // this.getNoticeList('EMAIL')
      // this.getNoticeList('WEIXIN')
      // this.getNoticeList('VOICE')
      // console.log(this.noticeType)
      this.noticeType.forEach(item => {
        this.getNoticeList(item.typeName);
      });
      if (this.$route.query.key === 'create') {
        let itemObj = {};
        if ('item' in this.$route.query) itemObj = JSON.parse(this.$route.query.item);
        this.addAgreement(itemObj);
      }
    },
    methods: {
      getList(page) {
        if (page !== undefined) {
          this.pagination.current = page;
        }
        const params = {
          page: this.pagination.current,
          page_size: this.pagination.limit,
          project_key: this.$store.state.project.id,
        };
        this.moreSearch.forEach(item => {
          if (Array.isArray(item.value) ? !!item.value.length : item.value !== '') {
            params[item.typeKey] = Array.isArray(item.value) ? item.value.join(',') : item.value;
          }
        });
        this.isDataLoading = true;
        this.$store.dispatch('slaManagement/getProtocolsList', { params }).then((res) => {
          this.dataList = res.data.items;
          this.searchToggle = res.data.items.length !== 0;
          // 分页
          this.pagination.current = res.data.page;
          this.pagination.count = res.data.count;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
      },
      // 获取数据
      getNoticeList(checkId) {
        this.isDataLoading = true;
        const checkIdL = checkId.toLowerCase();
        const params = {
          notify_type: checkId,
          used_by: 'SLA',
        };
        this.$store.dispatch('noticeConfigure/getNoticeList', { params }).then((res) => {
          const list = res.data.map(item => ({ id: item.id, name: item.action_name }));
          this.$set(this.notifyEventList, checkIdL, list);
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
      },
      // 分页过滤数据
      handlePageLimitChange() {
        this.pagination.limit = arguments[0];
        this.getList();
      },
      handlePageChange(page) {
        this.pagination.current = page;
        this.getList();
      },
      // 获取服务模式列表数据
      getModelList() {
        const params = {
          project_key: this.$store.state.project.id,
        };
        this.$store.dispatch('sla/getScheduleList', params).then(res => {
          this.modelList = res.data;
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      // 获取单据高亮颜色
      getTicketHighlight() {
        this.$store.dispatch('sla/getTicketHighlight').then(({ data }) => {
          this.highlightObj = data.items[0];
        })
          .catch(res => {
            this.$bkMessage({
              message: res.data.msg,
              theme: 'error',
            });
          });
      },
      // 单据高亮设置确认
      HighlightSettingComfirm() {
        this.isHighlightSetting = false;
        this.$store.dispatch('sla/updateTicketHighlight', this.highlightObj).then(({ result, data }) => {
          if (result) {
            this.$bkMessage({
              message: data.msg || this.$t('m.slaContent[\'成功更新单据高亮颜色\']'),
              theme: 'success',
            });
          } else {
            this.getTicketHighlight();
          }
        })
          .catch(res => {
            this.$bkMessage({
              message: res.data.msg,
              theme: 'error',
            });
          });
      },
      // 获取服务优先级
      getModelPriority() {
        const params = {
          dict_table__key: 'PRIORITY',
        };
        this.$store.dispatch('slaManagement/getPriority', { params }).then(res => {
          this.modelPriority = res.data;
        })
          .catch(res => {
            errorHandler(res, this);
          });
      },
      closeVersion() {
        this.versionStatus = false;
      },
      // 新增
      addAgreement(item, reqPerm) {
        const authResources = reqPerm === 'sla_agreement_create' ? this.$store.state.project.projectAuthActions : [...this.$store.state.project.projectAuthActions, ...item.auth_actions];
        if (!this.hasPermission([reqPerm], authResources)) {
          const projectInfo = this.$store.state.project.projectInfo;
          const resourceData = {
            project: [{
              id: projectInfo.key,
              name: projectInfo.name,
            }],
          };
          if (item.id) {
            resourceData.sla_agreement = [{
              id: item.id,
              name: item.name,
            }];
          }
          this.applyForPermission([reqPerm], reqPerm === 'sla_agreement_create' ? [] : [...this.$store.state.project.projectAuthActions, ...item.auth_actions], resourceData);
        } else {
          this.changeInfo.is_reply_need = item.is_reply_need;
          this.changeInfo.info = item;
          // 区分新增和编辑
          if (!item.id) {
            this.changeInfo.is_reply_need = true;
            this.changeInfo.info = {
              action_policies: [],
              policies: [],
            };
          }
          this.changeInfo.isShow = true;
        }
      },
      closeAgreement() {
        this.changeInfo.isShow = false;
      },
      // 删除
      deleteAgreement(item) {
        if (!this.hasPermission(['sla_agreement_delete'], [...this.$store.state.project.projectAuthActions, ...item.auth_actions])) {
          const projectInfo = this.$store.state.project.projectInfo;
          const resourceData = {
            project: [{
              id: projectInfo.key,
              name: projectInfo.name,
            }],
            sla_agreement: [{
              id: item.id,
              name: item.name,
            }],
          };
          this.applyForPermission(['sla_agreement_delete'], [...this.$store.state.project.projectAuthActions, ...item.auth_actions], resourceData);
        } else {
          this.$bkInfo({
            type: 'warning',
            title: this.$t('m.slaContent["确定删除该服务协议？"]'),
            confirmFn: () => {
              const id = item.id;
              if (this.secondClick) {
                return;
              }
              this.secondClick = true;
              this.$store.dispatch('slaManagement/deleteProtocol', id).then(() => {
                this.$bkMessage({
                  message: this.$t('m.systemConfig["删除成功"]'),
                  theme: 'success',
                });
                this.getList(1);
              })
                .catch((res) => {
                  errorHandler(res, this);
                })
                .finally(() => {
                  this.secondClick = false;
                });
            },
          });
        }
      },
      // 简单查询
      searchContent() {
        this.getList(1);
      },
      searchMore() {
        this.$refs.searchInfo.searchMore();
      },
      // 清空搜索表单
      clearSearch() {
        this.moreSearch.forEach(item => {
          item.value = item.multiSelect ? [] : '';
        });
        this.getList(1);
      },
    },
  };
</script>

<style lang='scss' scoped>
    .itsm-page-content {
        padding-top: 14px;
        .bk-only-btn {
            .ticket-setting {
                display: inline-block;
                margin:0 10px;
                color:#3A84FF;
                font-size: 12px;
                cursor: pointer;
            }
        }
    }
    .filter-btn /deep/ .icon-search-more {
        font-size: 14px;
    }
    .bk-highlight-setting {
        position: relative;
        padding-top: 14px;
        .bk-itsm-version {
            position: absolute;
            left: 0;
            top: -26px;
            width: 100%;
        }
        .bk-color-box {
            padding-left: 20px;
            color: #63656E;
            margin-top: 30px;
            span {
                margin-right: 8px;
            }
        }
    }
</style>
