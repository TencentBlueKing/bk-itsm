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
  <div id="app" class="bk-app" @click="hiddenTree" v-bkloading="{ isLoading: loading }">
    <!-- has navigation-->
    <navigation v-if="!$route.meta.iframe">
      <div
        v-if="isShowView"
        v-bkloading="{ isLoading: localLoading }"
        class="bk-app-content">
        <permissionApply
          v-if="permissinApplyShow"
          ref="permissionApply"
          :permission-data="permissionData">
        </permissionApply>
        <router-view
          v-else
          :key="routerKey">
        </router-view>
      </div>
    </navigation>
    <!-- no navigation-->
    <template v-else>
      <div
        v-if="isShowView"
        v-bkloading="{ isLoading: localLoading }"
        class="bk-app-content">
        <permissionApply
          v-if="permissinApplyShow"
          ref="permissionApply"
          :permission-data="permissionData">
        </permissionApply>
        <router-view
          v-else
          :key="routerKey">
        </router-view>
      </div>
    </template>
    <PermissionModal ref="permissionModal"></PermissionModal>
  </div>
</template>
<script>
  import bus from './utils/bus';
  import Navigation from './components/common/layout/Navigation.vue';
  import PermissionModal from '@/components/common/modal/PermissionModal.vue';
  import permissionApply from '@/components/common/layout/permissionApply.vue';
  import permission from '@/mixins/permission.js';
  import { errorHandler } from './utils/errorHandler';
  export default {
    name: 'app',
    components: {
      Navigation,
      PermissionModal,
      permissionApply,
    },
    provide() {
      return {
        reload: this.reload,
      };
    },
    mixins: [permission],
    data() {
      return {
        loading: false,
        localLoading: false,
        isRouterAlive: true,
        permissinApplyShow: false,
        routerKey: +new Date(),
        permissionData: {
          type: 'project', // 无权限类型: project、other
          permission: [],
        },
      };
    },
    computed: {
      routerTable() {
        return this.$store.state.tableList;
      },
      subinfo() {
        return this.$store.state.subinfo;
      },
      isShowView() {
        return this.isRouterAlive && !this.loading;
      },
    },
    watch: {
      $route: {
        async handler() {
          // check the page auth
          if (!this.loading) {
            this.isRouterAlive = false;
            await this.handleCheckPagePermission();
            this.isRouterAlive = true;
          }
          this.clearAllTicketInterval();
        },
        immediate: true,
      },
    },
    async created() {
      bus.$on('showPermissionModal', (data) => {
        this.$refs.permissionModal && this.$refs.permissionModal.show(data);
      });
      bus.$on('togglePermissionApplyPage', (show, type, permission) => {
        this.permissinApplyShow = show;
        this.permissionData = {
          type,
          permission,
        };
        if (!show) {
          this.isRouterAlive = true;
        }
      });
      this.loading = true;
      await this.getPermissionMeta();
      // await this.loadProjectInfo()
      await this.getManagePermission();
      await this.initGetInfo();
    },
    async mounted() {
      const vm = this;
      window.onresize = function temp() {
        if (vm.timer) {
          return;
        }
        vm.timer = true;
        setTimeout(() => {
          vm.$store.commit('changeClient', document.body.clientWidth);
          vm.timer = false;
        }, 400);
      };
      // 组件升级统一获取字段
      this.initGetInfo();
      this.getPageFooter();
    },
    methods: {
      getPageFooter() {
        this.$store.dispatch('common/getPageFooter').then((res) => {
          this.$store.commit('common/setPageFooter', res.data);
        })
          .catch((res) => {
            errorHandler(res, this);
            this.$store.commit('common/setPageFooter', '<div class="copyright"><div>蓝鲸智云 版权所有</div></div>');
          });
      },
      // 组件升级统一获取字段
      initGetInfo() {
        const configurInfo = this.loadConfigurInfo();
        const theWay = this.loadTheWay();
        const systemSettings = this.loadSystemSettings();
        Promise.all([configurInfo, theWay, systemSettings]).then(async () => {
          await this.handleCheckPagePermission();
          this.loading = false;
        });
      },
      // 获取发现途径/工单类型/单据状态... 等公共信息
      loadTheWay() {
        return this.$store.dispatch('common/getTheWay').then((res) => {
          this.$store.commit('common/getWayInfo', res.data);
          const commomInfo = {
            choice_state_list_dict: {},
            export_fields: [],
            processor_type: [],
          };
          // 工单状态选择（增加全选）
          Object.entries(res.data.ticket_status).forEach((item) => {
            commomInfo.choice_state_list_dict[item[0]] = [{ id: 0, key: 'all', name: '全部' }].concat(item[1].map((item, index) => {
              const itemch = {};
              itemch.id = index + 1;
              itemch.name = item.pk_value || item.name;
              itemch.key = item.key;
              return itemch;
            }));
          });
          commomInfo.export_fields = res.data.export_fields;
          commomInfo.processor_type = res.data.processor_type;
          this.$store.commit('getTypeWay', commomInfo);
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 加载系统配置
      loadSystemSettings() {
        // 获取功能模块启用状态
        return this.$store.dispatch('attachmentStorage/getEnableStatus').then((res) => {
          const tempObj = {};
          res.data.forEach((item) => {
            if (item.key === 'SYS_FILE_PATH') {
              tempObj.SYS_FILE_PATH = item.value;
            } else if (item.key !== 'SERVICE_SWITCH') {
              tempObj[item.key] = item.value === 'on';
            }
          });
          this.$store.commit('changeOpenFunction', tempObj);
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 获取节点配置字段信息
      loadConfigurInfo() {
        return this.$store.dispatch('common/getConfigurInfo').then((res) => {
          const value = res.data;
          const globalInfo = {};
          for (const key in value) {
            const listInfo = [];
            // 区分返回的是数组还是对象
            if (Array.isArray(value[key])) {
              for (let i = 0; i < value[key].length; i++) {
                if (Array.isArray(value[key][i])) {
                  listInfo.push({
                    id: i + 1,
                    name: value[key][i][1] ? value[key][i][1] : this.$t('m.deployPage["无"]'),
                    typeName: value[key][i][0],
                  });
                } else {
                  listInfo.push(value[key][i]);
                }
              }
              globalInfo[key] = listInfo;
            } else {
              globalInfo[key] = value[key];
            }
          }
          this.$store.commit('common/changeConfigur', globalInfo);
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 获取平台管理权限及运营数据权限
      getManagePermission() {
        return this.$store.dispatch('common/getManagePermission').then((res) => {
          const pagePermission = Object.keys(res.data).filter((auth) => {
            if (res.data[auth]) {
              return res.data[auth];
            }
          });
          this.$store.commit('common/setSystemPermission', pagePermission);
        });
      },
      // 获取项目详情
      // loadProjectInfo () {
      //     return this.$store.dispatch('project/getProjectInfo')
      // },
      // 获取权限树
      getPermissionMeta() {
        return this.$store.dispatch('common/getPermissionMeta');
      },
      reloadCurPage() {
        this.routerKey = +new Date();
      },
      reload() {
        this.isRouterAlive = false;
        this.$nextTick(async () => {
          await this.handleCheckPagePermission();
          this.isRouterAlive = true;
        });
      },
      // 关闭服务目录树组件
      hiddenTree(event) {
        const treePanel = document.getElementById('treeOther');
        if (treePanel && !treePanel.contains(event.target)) {
          this.$store.commit('serviceCatalog/changeTreeOperat', false);
        }
      },
      // 页面权限校验，没有权限会先去刷新权限信息
      async handleCheckPagePermission() {
        // this.permissinApplyShow = true
        const { verified } = this.checkPagePermission();
        if (!verified) {
          await this.refreshPermissionInfo();
        } else {
          bus.$emit('togglePermissionApplyPage', false);
        }
      },
      // 刷新已有权限信息
      async refreshPermissionInfo() {
        this.localLoading = true;
        // await this.loadProjectInfo()
        const { verified, data } = this.checkPagePermission();
        if (!verified) {
          bus.$emit('togglePermissionApplyPage', true, 'other', data);
        } else {
          bus.$emit('togglePermissionApplyPage', false);
        }
        this.localLoading = false;
      },
      clearAllTicketInterval() {
        // 切换路由时，清空单据的轮询数据
        clearInterval(this.$store.state.deployOrder.intervalInfo.basic);
        clearInterval(this.$store.state.deployOrder.intervalInfo.lines);
        clearInterval(this.$store.state.taskFlow.intervalInfo);
        // 关闭计时器
        if (this.$store.state.deployOrder.intervalInfo.timeOut) {
          clearInterval(this.$store.state.deployOrder.intervalInfo.timeOut);
        }
      },
    },
  };
</script>

<style lang="scss">
    @import './scss/reset.scss';
    @import './scss/app.scss';
    @import './scss/bk-patch.scss';
    @import './scss/animation.scss';
    @import './scss/mixins/scroller.scss';
    @import './scss/bk-new-change.scss';
    @import './scss/mixins/scroller.scss';
    /* 新增右侧弹窗Form上下布局 */
    .bk-app {
        margin: 0 auto;
        height: 100%;
        width: 100%;
        .bk-navigation {
            min-width: 1366px;
            .navigation-container {
                max-width: unset!important;
            }
            .bk-navigation-wrapper .container-content {
                padding: 0;
            }
            .bk-navigation-header {
                position: relative;
            }
        }
        .bk-app-container {
            height: calc(100% - 60px);
        }
        .bk-app-silder {
            position: fixed;
            top: 0;
            left: 0;
            margin-top: 60px;
            height: 100%;
            z-index: 103;
        }
        .bk-app-content {
            position: relative;
            height: 100%;
            overflow: auto;
            @include scroller;
        }
    }
    .bk-add-data {
        .bk-form-content {
            margin-bottom: 15px;
            @include clearfix;

            .bk-form-p {
                font-size: 14px;
                color: #63656E;
                margin-bottom: 6px;
                line-height: 19px;

                .bk-p-xin {
                    color: #ff5656;
                }
            }
        }
    }
</style>
