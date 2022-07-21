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
  <div class="bk-itsm-box">
    <!-- 首页列表 -->
    <div class="is-title" :class="{ 'bk-title-left': !sliderStatus }">
      <p class="bk-come-back">
        {{ $t('m.deployPage["流程设计"]') }}
      </p>
    </div>
    <div class="itsm-page-content">
      <div class="bk-itsm-version" v-if="versionStatus">
        <i class="bk-icon icon-info-circle"></i>
        <span>{{ $t('m.deployPage["流程设计：流程修改后，需要重新部署才能使改动生效"]') }}</span>
        <i class="bk-icon icon-close" @click="closeVersion"></i>
      </div>
      <div class="bk-design-table">
        <div class="bk-only-btn">
          <div class="bk-more-search">
            <bk-button
              v-cursor="{ active: !hasPermission(['workflow_create']) }"
              icon="plus"
              :class="['mr10', 'plus-cus', {
                'btn-permission-disable': !hasPermission(['workflow_create'])
              }]"
              :theme="'primary'"
              :title="$t(`m.deployPage['新增']`)"
              @click="addProcess">
              {{ $t('m.deployPage["新增"]') }}
            </bk-button>
            <bk-button
              v-if="!hasPermission(['workflow_create'])"
              v-cursor="{ active: !hasPermission(['workflow_create']) }"
              :theme="'default'"
              :title="$t(`m.deployPage['点击上传']`)"
              :class="['mr10', 'bk-btn-file', {
                'btn-permission-disable': !hasPermission(['workflow_create'])
              }]"
              @click="onProcessImportPermissonApply">
              {{ $t('m.deployPage["导入"]') }}
            </bk-button>
            <bk-button
              v-else
              :theme="'default'"
              :title="$t(`m.deployPage['点击上传']`)"
              class="mr10 bk-btn-file">
              <input type="file" :value="fileVal" class="bk-input-file" @change="handleFile">
              {{ $t('m.deployPage["导入"]') }}
            </bk-button>
            <div class="bk-search-name">
              <div class="bk-search-content">
                <bk-input
                  :clearable="true"
                  :right-icon="'bk-icon icon-search'"
                  :placeholder="moreSearch[0].placeholder"
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
          <bk-table-column :label="$t(`m.common['ID']`)" min-width="60">
            <template slot-scope="props">
              <span :title="props.row.id">{{ props.row.id || '--' }}</span>
            </template>
          </bk-table-column>

          <bk-table-column :label="$t(`m.deployPage['流程名']`)" min-width="200">
            <template slot-scope="props">
              <span class="bk-lable-primary"
                @click="onFlowEdit(props.row)"
                :title="props.row.name">
                {{props.row.name}}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.deployPage['说明']`)" min-width="200">
            <template slot-scope="props">
              <span :title="props.row.desc">{{ props.row.desc || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.common['负责人']`)">
            <template slot-scope="props">
              <span :title="props.row.owners">{{props.row.owners || '--'}}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.common['创建人']`)">
            <template slot-scope="props">
              <span :title="props.row.creator">{{props.row.creator || '--'}}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.common['更新人']`)" min-width="100">
            <template slot-scope="props">
              <span :title="props.row.updated_by">{{ props.row.updated_by || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.deployPage['更新时间']`)" width="180">
            <template slot-scope="props">
              <span :title="props.row.update_at">{{ props.row.update_at || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.deployPage['状态']`)" width="80">
            <template slot-scope="props">
              <span class="bk-status-color"
                :class="{ 'bk-status-gray':
                  !props.row.is_enabled, 'bk-status-primary': props.row.is_draft }">
              </span>
              <span style="margin-left: 5px;"
                :title="props.row.is_draft
                  ? $t(`m.deployPage['草稿']`) : (props.row.is_enabled
                    ? $t(`m.deployPage['启用']`) : $t(`m.deployPage['关闭']`))">
                {{props.row.is_draft
                  ? $t(`m.deployPage["草稿"]`) : (props.row.is_enabled
                    ? $t(`m.deployPage["启用"]`) : $t(`m.deployPage["关闭"]`))}}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.deployPage['操作']`)" width="300">
            <template slot-scope="props">
              <bk-button
                v-cursor="{ active: !hasPermission(['workflow_manage'], props.row.auth_actions) }"
                text
                theme="primary"
                :class="[{
                  'btn-permission-disable':
                    !hasPermission(['workflow_manage'], props.row.auth_actions)
                }]"
                @click="onFlowEdit(props.row)">
                {{ $t('m.deployPage["编辑"]') }}
              </bk-button>
              <bk-button
                v-cursor="{ active: !hasPermission(['workflow_deploy'], props.row.auth_actions) }"
                text
                theme="primary"
                :disabled="hasPermission(['workflow_deploy'], props.row.auth_actions)
                  && (props.row.is_draft || !props.row.is_enabled)"
                :class="[{
                  'btn-permission-disable':
                    !hasPermission(['workflow_deploy'], props.row.auth_actions)
                }]"
                @click="onFlowDeploy(props.row)">
                {{ $t('m.deployPage["部署"]') }}
              </bk-button>
              <bk-button
                v-cursor="{ active: !hasPermission(['workflow_manage'], props.row.auth_actions) }"
                text
                theme="primary"
                :class="[{
                  'btn-permission-disable':
                    !hasPermission(['workflow_manage'], props.row.auth_actions)
                }]"
                @click="onFlowPreview(props.row)">
                {{ $t('m.deployPage["预览"]') }}
              </bk-button>
              <bk-button
                v-cursor="{ active: !hasPermission(['workflow_manage'], props.row.auth_actions) }"
                text
                theme="primary"
                :disabled="hasPermission(['workflow_manage'], props.row.auth_actions)
                  && props.row.is_draft"
                :class="[{
                  'btn-permission-disable':
                    !hasPermission(['workflow_manage'], props.row.auth_actions)
                }]"
                @click="onFlowExport(props.row)">
                {{ $t('m.deployPage["导出"]') }}
              </bk-button>
              <bk-button
                v-cursor="{ active: !hasPermission(['workflow_manage'], props.row.auth_actions) }"
                text
                theme="primary"
                :class="[{
                  'btn-permission-disable':
                    !hasPermission(['workflow_manage'], props.row.auth_actions)
                }]"
                @click="deleteConfirm(props.row)">
                {{ $t('m.deployPage["删除"]') }}
              </bk-button>
            </template>
          </bk-table-column>
        </bk-table>
        <!-- 预览 -->
        <bk-dialog v-model="processInfo.isShow"
          width="760"
          :position="processInfo.position"
          :draggable="processInfo.draggable"
          :title="processInfo.title">
          <div style="width: 100%; height: 347px;" v-bkloading="{ isLoading: processInfo.loading }">
            <preview
              v-if="!processInfo.loading"
              :add-list="addList"
              :line-list="lineList"
              :preview-info="previewInfo"
              :normal-color="normalColor">
            </preview>
          </div>
          <div slot="footer">
            <bk-button
              theme="default"
              @click="processInfo.isShow = false">
              {{ $t('m.deployPage["关闭"]') }}
            </bk-button>
          </div>
        </bk-dialog>
        <!-- 部署确认 -->
        <bk-dialog
          v-model="deployInfo.isShow"
          :render-directive="'if'"
          :width="deployInfo.width"
          :header-position="deployInfo.headerPosition"
          :loading="secondClick"
          :auto-close="deployInfo.autoClose"
          :mask-close="deployInfo.autoClose"
          @confirm="submitForm">
          <p slot="header">{{ $t(`m.deployPage["确认部署"]`) }}</p>
          <div class="bk-add-project">
            <bk-form
              :label-width="200"
              form-type="vertical"
              :model="deployInfo.formInfo"
              :rules="rules"
              ref="deployForm">
              <bk-form-item
                :label="$t(`m.deployPage['部署流程名']`)"
                :required="true"
                :property="'name'">
                <bk-input v-model.trim="deployInfo.formInfo.name"
                  maxlength="120"
                  :placeholder="$t(`m.deployPage['请输入部署流程名']`)">
                </bk-input>
              </bk-form-item>
            </bk-form>
          </div>
        </bk-dialog>
      </div>
    </div>
  </div>
</template>
<script>
  import axios from 'axios';
  import commonMix from '../../../commonMix/common.js';
  import searchInfo from '../../../commonComponent/searchInfo/searchInfo.vue';
  import preview from '../../../commonComponent/preview';
  import permission from '@/mixins/permission.js';
  import { errorHandler } from '../../../../utils/errorHandler.js';

  export default {
    name: 'ProcessHome',
    components: {
      searchInfo,
      preview,
    },
    mixins: [commonMix, permission],
    data() {
      return {
        // 组件升级数据更新
        versionStatus: true,
        isDataLoading: false,
        secondClick: false,
        normalColor: true,
        // table数据和分页
        dataList: [],
        pagination: {
          current: 1,
          count: 10,
          limit: 10,
        },
        // 查询
        moreSearch: [
          {
            name: this.$t('m.deployPage["流程名"]'),
            desc: this.$t('m.deployPage["请输入流程名"]'),
            type: 'input',
            typeKey: 'name__icontains',
            value: '',
            multiSelect: false,
            list: [],
          },
          {
            name: this.$t('m.deployPage["更新人"]'),
            desc: this.$t('m.deployPage["请输入更新人"]'),
            type: 'member',
            typeKey: 'updated_by__contains',
            multiSelect: true,
            value: [],
            list: [],
          },
          {
            name: this.$t('m.deployPage["启用状态"]'),
            desc: this.$t('m.deployPage["请选择启用状态"]'),
            type: 'select',
            typeKey: 'is_enabled',
            multiSelect: false,
            value: '',
            list: [
              { key: -1, name: this.$t('m.deployPage["草稿"]') },
              { key: 0, name: this.$t('m.deployPage["关闭"]') },
              { key: 1, name: this.$t('m.deployPage["启用"]') },
            ],
          },
        ],
        // 导入流程文件
        fileVal: '',
        // 流程预览
        processInfo: {
          isShow: false,
          title: this.$t('m.flowManager["流程预览"]'),
          position: {
            top: 150,
          },
          draggable: true,
          loading: true,
        },
        previewInfo: {
          canClick: false,
          narrowSize: 0.8,
        },
        addList: [],
        lineList: [],
        // 部署
        deployInfo: {
          isShow: false,
          width: 700,
          headerPosition: 'left',
          autoClose: false,
          precision: 0,
          formInfo: {
            name: '',
            id: '',
          },
        },
        rules: {},
      };
    },
    computed: {
      sliderStatus() {
        return this.$store.state.common.slideStatus;
      },
    },
    mounted() {
      // 获取列表数据
      this.getList();
      // 校验
      this.rules.name = this.checkCommonRules('name').name;
    },
    methods: {
      // 获取列表数据
      getList(page) {
        if (page !== undefined) {
          this.pagination.current = page;
        }
        const params = {
          page: this.pagination.current,
          page_size: this.pagination.limit,
        };
        // 过滤条件
        this.moreSearch.forEach((item) => {
          if ((Array.isArray(item.value)
            ? !!item.value.length : item.value !== '') && item.typeKey !== 'is_enabled') {
            params[item.typeKey] = Array.isArray(item.value) ? item.value.join(',') : item.value;
          }
        });
        if (this.moreSearch[2].value === -1) {
          params.is_draft = 1;
          params.is_enabled = '';
        } else if (this.moreSearch[2].value === 0) {
          params.is_enabled = 0;
          params.is_draft = 0;
        } else if (this.moreSearch[2].value === 1) {
          params.is_enabled = 1;
        }

        this.isDataLoading = true;
        this.$store.dispatch('deployCommon/getList', params).then((res) => {
          this.dataList = res.data.items;
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
      // 分页过滤数据
      handlePageLimitChange() {
        this.pagination.limit = arguments[0];
        this.getList();
      },
      handlePageChange(page) {
        this.pagination.current = page;
        this.getList();
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
        this.moreSearch.forEach((item) => {
          item.value = item.multiSelect ? [] : '';
        });
        this.getList(1);
      },
      // 新增流程
      addProcess() {
        // 创建权限校验
        if (!this.hasPermission(['workflow_create'])) {
          const { projectInfo } = this.$store.state.project;
          const resourceData = {
            project: [{
              id: projectInfo.key,
              name: projectInfo.name,
            }],
          };
          this.applyForPermission(['workflow_create'], [], resourceData);
        } else {
          this.$router.push({
            name: 'ProcessEdit',
            params: {
              type: 'new',
              step: 'processInfo',
            },
          });
        }
      },
      // 编辑流程
      onFlowEdit(item) {
        // 流程管理权限校验
        if (!this.CheckFowPermisson(item)) {
          return;
        }
        this.$router.push({
          name: 'ProcessEdit',
          params: {
            type: 'edit',
            step: 'processInfo',
          },
          query: {
            processId: item.id,
          },
        });
      },
      // 上传文件模板
      handleFile(e) {
        const fileInfo = e.target.files[0];
        if (fileInfo.size <= 10 * 1024 * 1024) {
          const data = new FormData();
          data.append('file', fileInfo);
          const fileType = 'json';
          this.$store.dispatch('cdeploy/flowFileUpload', { fileType, data }).then((res) => {
            this.$bkMessage({
              message: `${this.$t('m.deployPage["成功导入"]')}
                                ${res.data.success}
                                ${this.$t('m.deployPage["个流程，"]')}
                                ${this.$t('m.deployPage["失败"]')}
                                ${res.data.failed}
                                ${this.$t('m.deployPage["个"]')}`,
              theme: 'success',
            });
            this.getList(1);
          })
            .catch((res) => {
              errorHandler(res, this);
            })
            .finally(() => {
              this.fileVal = '';
              e.target.value = null;
            });
        } else {
          this.fileVal = '';
          e.target.value = null;
          this.$bkMessage({
            message: this.$t('m.deployPage["文件大小不能超过10MB"]'),
            theme: 'error',
          });
        }
      },
      // 部署流程
      onFlowDeploy(item) {
        // 流程管理权限校验
        if (!this.CheckFowPermisson(item, ['workflow_deploy'])) {
          return;
        }
        if (item.is_draft || !item.is_enabled) {
          return;
        }
        this.deployInfo.isShow = true;
        this.deployInfo.formInfo.name = item.name;
        this.deployInfo.formInfo.id = item.id;
      },
      submitForm() {
        this.$refs.deployForm.validate().then(() => {
          if (this.secondClick) {
            return;
          }
          this.secondClick = true;
          const { id } = this.deployInfo.formInfo;
          const params = {
            name: this.deployInfo.formInfo.name,
          };
          this.$store.dispatch('cdeploy/deployFlow', { params, id }).then(() => {
            this.$bkMessage({
              message: this.$t('m.deployPage["流程部署成功，请关联服务后使用"]'),
              theme: 'success',
            });
          })
            .catch((res) => {
              errorHandler(res, this);
            })
            .finally(() => {
              this.secondClick = false;
              this.deployInfo.isShow = false;
            });
        }, () => {});
      },
      // 流程预览
      onFlowPreview(item) {
        // 流程管理权限校验
        if (!this.CheckFowPermisson(item)) {
          return;
        }
        const { id } = item;
        if (!id) {
          return;
        }
        this.processInfo.isShow = !this.processInfo.isShow;
        this.processInfo.loading = true;
        axios.all([
          this.$store.dispatch('deployCommon/getStates', { workflow: id }),
          this.$store.dispatch('deployCommon/getChartLink', {
            workflow: id,
            page_size: 1000,
          }),
        ]).then(axios.spread((userResp, reposResp) => {
          this.addList = userResp.data;
          for (let i = 0; i < this.addList.length; i++) {
            this.addList[i].indexInfo = i;
          }
          this.lineList = reposResp.data.items;
        }))
          .finally(() => {
            this.processInfo.loading = false;
          });
      },
      // 导出
      onFlowExport(item) {
        // 流程管理权限校验
        if (!this.CheckFowPermisson(item)) {
          return;
        }
        this.$bkInfo({
          title: this.$t('m.deployPage["确认导出？"]'),
          confirmFn: () => {
            window.open(`${window.SITE_URL}api/workflow/templates/${item.id}/exports/`);
          },
        });
      },
      // 删除确认
      deleteConfirm(item) {
        // 流程管理权限校验
        if (!this.CheckFowPermisson(item)) {
          return;
        }
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.deployPage["确认删除此流程？"]'),
          subTitle: this.$t('m.deployPage["流程一旦删除，将无法还原，请谨慎操作"]'),
          confirmFn: () => {
            const params = item.id;
            if (this.secondClick) {
              return;
            }
            this.secondClick = true;
            this.$store.dispatch('cdeploy/deleteDesign', { params }).then(() => {
              this.$bkMessage({
                message: this.$t('m.systemConfig["删除成功"]'),
                theme: 'success',
              });
              if (this.dataList.length === 1) {
                this.pagination.current = this.pagination.current === 1
                  ? 1 : this.pagination.current - 1;
              }
              this.getList();
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
      // 关闭版本提示信息
      closeVersion() {
        this.versionStatus = false;
      },
      // 导入流程权限校验
      onProcessImportPermissonApply() {
        // 创建权限校验
        if (!this.hasPermission(['workflow_create'])) {
          const { projectInfo } = this.$store.state.project;
          const resourceData = {
            project: [{
              id: projectInfo.key,
              name: projectInfo.name,
            }],
          };
          this.applyForPermission(['workflow_create'], [], resourceData);
        }
      },
      /**
       * 验证流程权限，默认校验流程管理权限
       * @param {Object} item 流程实例数据
       * @param {Array} req 申请的权限
       */
      CheckFowPermisson(item, req = ['workflow_manage']) {
        // 流程管理权限校验
        if (!this.hasPermission(req, item.auth_actions)) {
          const { projectInfo } = this.$store.state.project;
          const resourceData = {
            project: [{
              id: projectInfo.key,
              name: projectInfo.name,
            }],
            workflow: [{
              id: item.id,
              name: item.name,
            }],
          };
          this.applyForPermission(req, item.auth_actions, resourceData);
          return false;
        }
        return true;
      },
    },
  };
</script>

<style lang='scss' scoped>
.filter-btn {
    /deep/ .icon-search-more {
        font-size: 14px;
    }
}
.itsm-page-content {
    padding-top: 53px;
}
</style>
