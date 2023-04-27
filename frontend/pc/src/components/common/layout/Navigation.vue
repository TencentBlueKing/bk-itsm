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
  <bk-navigation
    navigation-type="top-bottom"
    theme-color="#ffffff"
    :default-open="isSideOpen"
    :side-title="appName"
    :need-menu="sideRouters.length > 0"
    @toggle-click="isSideOpen = $event">
    <template slot="side-icon">
      <img src="../../../images/itsm-logo.png" alt="" style="width: 36px; height: 36px;">
    </template>
    <template slot="header">
      <div class="nav-header">
        <!-- <bk-button
          data-test-id="navigation-button-createTicket"
          theme="primary"
          icon="plus"
          size="small"
          class="create-bill-btn"
          @click="isCreateTicketDialogShow = true">
          {{ $t(`m.navigation["提单"]`) }}
        </bk-button> -->
        <ul class="nav-list">
          <li
            v-for="router in topNav"
            :key="router.id"
            :class="['nav-item', { active: router.id === activeNav }]">
            <router-link :to="router.path" :data-test-id="`navigation-router-navRouter-${router.id}`" event="" @click.native.prevent="handleTopNavClick(router, $event)">{{ router.name }}</router-link>
          </li>
        </ul>
      </div>
      <div class="quick-entry">
        <bk-popover theme="navigation-popover" :arrow="false" offset="0, 2" :tippy-options="{ animateFill: false, hideOnClick: false }">
          <div class="language" style="margin: 0 10px;">
            <span :class="['language-btn bk-itsm-icon', curLanguage === 'zh' ? 'icon-yuyanqiehuanzhongwen' : 'icon-yuyanqiehuanyingwen']"></span>
          </div>
          <template slot="content">
            <ul class="nav-language-list">
              <li class="language-item" :class="{ 'active': curLanguage === 'zh' }" @click="changeLanguage('zh')">
                <span class="bk-itsm-icon icon-yuyanqiehuanzhongwen"></span>
                <span>{{ $t(`m["中文"]`) }}</span>
              </li>
              <li class="language-item" :class="{ 'active': curLanguage === 'en' }" @click="changeLanguage('en')">
                <span class="bk-itsm-icon icon-yuyanqiehuanyingwen"></span>
                <span>{{ $t(`m["英文"]`) }}</span>
              </li>
            </ul>
          </template>
        </bk-popover>
        <bk-popover theme="navigation-popover" :arrow="false" offset="0, 2" :tippy-options="{ animateFill: false, hideOnClick: false }">
          <div class="right-question-icon">
            <svg class="bk-icon" style="margin-top: 2px; width: 1em; height: 1em;vertical-align: middle;fill: currentColor;overflow: hidden;" viewBox="0 0 64 64" version="1.1" xmlns="http://www.w3.org/2000/svg">
              <path d="M32,4C16.5,4,4,16.5,4,32c0,3.6,0.7,7.1,2,10.4V56c0,1.1,0.9,2,2,2h13.6C36,63.7,52.3,56.8,58,42.4S56.8,11.7,42.4,6C39.1,4.7,35.6,4,32,4z M31.3,45.1c-1.7,0-3-1.3-3-3s1.3-3,3-3c1.7,0,3,1.3,3,3S33,45.1,31.3,45.1z M36.7,31.7c-2.3,1.3-3,2.2-3,3.9v0.9H29v-1c-0.2-2.8,0.7-4.4,3.2-5.8c2.3-1.4,3-2.2,3-3.8s-1.3-2.8-3.3-2.8c-1.8-0.1-3.3,1.2-3.5,3c0,0.1,0,0.1,0,0.2h-4.8c0.1-4.4,3.1-7.4,8.5-7.4c5,0,8.3,2.8,8.3,6.9C40.5,28.4,39.2,30.3,36.7,31.7z"></path>
            </svg>
          </div>
          <template slot="content">
            <ul class="nav-operate-list">
              <li class="operate-item">
                <a :href="bkDocUrl" target="_blank">{{ $t(`m.wiki["产品文档"]`) }}</a>
              </li>
              <li class="operate-item">
                <div @click="isVersionLogShow = true">{{ $t(`m.wiki["版本日志"]`) }}</div>
              </li>
              <li class="operate-item">
                <a href="https://bk.tencent.com/s-mart/community" target="_blank">{{ $t(`m.wiki["问题反馈"]`) }}</a>
              </li>
            </ul>
          </template>
        </bk-popover>
        <bk-popover data-test-id="navigation-popover-user" theme="navigation-popover" :arrow="false" offset="0, 7" :tippy-options="{ animateFill: false, hideOnClick: false }">
          <div class="user-name">
            <span>{{ userName }}</span>
            <i class="bk-icon icon-down-shape"></i>
          </div>
          <template slot="content">
            <ul class="nav-operate-list">
              <li class="operate-item">
                <span @click="onGoToProjectList">{{ $t(`m["项目管理"]`) }}</span>
              </li>
              <li class="operate-item">
                <span data-test-id="navigation-span-logout" @click="onLogOut">{{ $t(`m.wiki["退出"]`) }}</span>
              </li>
            </ul>
          </template>
        </bk-popover>
      </div>
    </template>
    <template slot="menu">
      <bk-select
        data-test-id="navigation-select-projectList"
        v-if="activeNav === 'project'"
        :value="selectedProject"
        class="project-select"
        ext-popover-cls="project-select-popover"
        :loading="projectListLoading"
        :clearable="false"
        :searchable="true"
        @selected="onSelectProject">
        <bk-option
          v-for="item in projectList"
          :key="item.key"
          :id="item.key"
          :disabled="!hasPermission(['project_view'], item.auth_actions)"
          :name="item.name">
          <div
            v-cursor="{ active: !hasPermission(['project_view'], item.auth_actions) }"
            :class="['project-item', { 'text-permission-disable': !hasPermission(['project_view'], item.auth_actions) }]"
            @click="applyForProjectViewPerm(item, 'project_view')">
            {{ item.name }}
          </div>
        </bk-option>
        <div slot="extension" class="project-select-extension">
          <div
            data-test-id="navigation-div-createProject"
            v-cursor="{ active: !hasPermission(['project_create']) }"
            :class="['action-item', { 'text-permission-disable': !hasPermission(['project_create']) }]"
            @click="handleCreateProject">
            <i class="bk-icon icon-plus-circle"></i>
            {{ $t(`m['新建项目']`) }}
          </div>
          <div
            data-test-id="navigation-div-manageProject"
            class="action-item"
            @click="goToProjectManage">
            <i class="bk-icon icon-apps"></i>
            {{ $t(`m['项目管理']`) }}
          </div>
        </div>
      </bk-select>
      <bk-navigation-menu
        item-active-bg-color="#e1ecff"
        item-active-color="#3a84ff"
        item-default-color="#979ba5"
        item-default-icon-color="#979ba5"
        item-active-icon-color="#3a84ff"
        :toggle-active="true"
        :default-active="activeSideRouter">
        <template v-for="router in sideNav">
          <div
            v-if="Array.isArray(router.subRouters) && router.subRouters.length > 0"
            class="nav-group-wrap"
            :key="router.id">
            <div class="group-name">{{ !isSideOpen && $store.state.language === 'en' ? router.abbrName : router.name }}</div>
            <bk-navigation-menu-item
              v-for="item in router.subRouters"
              :data-test-id="`navigation-menu-${item.id}`"
              :key="item.id"
              :id="item.id"
              :disabled="item.disabled"
              :icon="item.icon"
              @click="handleSideRouterClick(item)">
              {{ item.name }}
            </bk-navigation-menu-item>
          </div>
          <bk-navigation-menu-item
            :data-test-id="`navigation-menu-platformRouter-${router.id}`"
            v-else
            :key="router.id"
            :id="router.id"
            :has-child="false"
            :icon="router.icon"
            :disabled="router.disabled"
            @click="handleSideRouterClick(router)">
            {{ router.name }}
          </bk-navigation-menu-item>
        </template>

      </bk-navigation-menu>
    </template>
    <div class="page-container">
      <slot></slot>
      <version-log v-if="isVersionLogShow" @close="isVersionLogShow = false"></version-log>
      <create-ticket-dialog :is-show.sync="isCreateTicketDialogShow"></create-ticket-dialog>
      <edit-project-dialog
        :title="$t(`m['新建项目']`)"
        :is-show="isEditDialogShow"
        :project="projectForm"
        :edit-dialog-form-disable="editDialogFormDisable"
        @confirm="onProjectDialogConfirm"
        @cancel="onProjectDialogCancel">
      </edit-project-dialog>
    </div>
  </bk-navigation>
</template>
<script>
  import { mapState } from 'vuex';
  import Cookies from 'js-cookie';
  import bus from '@/utils/bus.js';
  import permission from '@/mixins/permission.js';
  import ROUTER_LIST from '@/constants/routerList.js';
  import VersionLog from '@/components/common/layout/VersionLog.vue';
  import CreateTicketDialog from '@/components/common/modal/CreateTicketDialog.vue';
  import EditProjectDialog from '@/views/project/editProjectDialog.vue';
  import { errorHandler } from '../../../utils/errorHandler';
  import { getCookie } from '../../../utils/util';

  export default {
    name: 'Navigation',
    components: {
      VersionLog,
      CreateTicketDialog,
      EditProjectDialog,
    },
    inject: ['reload'],
    mixins: [permission],
    data() {
      return {
        appName: window.log_name || '流程服务管理',
        userName: window.username || '--',
        bkDocUrl: window.DOC_URL,
        routerList: ROUTER_LIST.slice(0),
        isSideOpen: true,
        sideRouters: [],
        activeNav: '',
        activeSideRouter: '',
        selectedProject: this.$store.state.project.id,
        isEditDialogShow: false,
        isVersionLogShow: false,
        isCreateTicketDialogShow: false,
        projectForm: {
          name: '',
          key: '',
          desc: '',
          color: '',
        },
        editDialogFormDisable: false,
        curLanguage: 'zh',
      };
    },
    computed: {
      ...mapState({
        openFunction: state => state.openFunction,
        systemPermission: state => state.common.systemPermission,
        projectList: state => state.project.projectList,
        projectListLoading: state => state.project.projectListLoading,
      }),
      // 顶部导航项
      topNav() {
        return this.routerList.filter((item) => {
          if (item.id === 'wiki') { // 知识库只在全局配置中对应开关打开时显示
            return this.openFunction.WIKI_SWITCH;
          }
          if (item.id === 'manage') {
            return this.systemPermission.includes('platform_manage_access');
          }
          return true;
        });
      },
      // 侧边栏导航项
      sideNav() {
        const list = [];
        this.sideRouters.forEach((router) => {
          if (router.id === 'sla') {
            this.openFunction.SLA_SWITCH && list.push(router);
          } else if (router.id === 'processManage') {
            const subRouters = router.subRouters.filter((item) => {
              if (item.id === 'processManageTpl') {
                return this.openFunction.TASK_SWITCH;
              }
              if (item.id === 'processManageTrigger') {
                return this.openFunction.TRIGGER_SWITCH;
              }
              return true;
            });
            list.push(Object.assign({}, router, { subRouters }));
          } else {
            list.push(router);
          }
        });
        return list;
      },
    },
    watch: {
      '$route.fullPath': {
        handler() {
          this.setActive();
        },
        immediate: true,
      },
      '$store.state.project.id'(val) {
        if (val) {
          this.selectedProject = val;
        }
      },
      isEditDialogShow(val) {
        if (val) {
          this.getProjectList();
        }
      },
    },
    created() {
      this.curLanguage = getCookie('blueking_language') === 'en' ? 'en' : 'zh';
      this.getAccessService();
      bus.$on('openCreateTicketDialog', () => {
        this.isCreateTicketDialogShow = true;
      });
      bus.$on('openCreateProjectDialog', () => {
        this.handleCreateProject();
      });
    },
    methods: {
      async getProjectList() {
        try {
          this.editDialogFormDisable = true;
          this.$store.commit('project/setProjectListLoading', true);
          const res = await this.$store.dispatch('project/getProjectAllList');
          this.$store.commit('project/setProjectList', res.data);
        } catch (e) {
          errorHandler(e, this);
        } finally {
          this.editDialogFormDisable = false;
          this.$store.commit('project/setProjectListLoading', false);
        }
      },
      changeLanguage(language) {
        this.curLanguage = language;
        const local = language === 'zh' ? 'zh-cn' : 'en';
        Cookies.set('blueking_language', local, {
          expires: 1,
          domain: window.location.hostname.replace(/^[^.]+(.*)$/, '$1'),
          path: '/',
        });
        window.location.reload();
      },
      // 高亮顶部和侧边栏导航项
      setActive() {
        const hasMatched = this.routerList.some((nav) => {
          const navId = nav.id;
          if (Array.isArray(nav.subRouters) && nav.subRouters.length > 0) {
            const matched = this.traverseSubRouter(nav.subRouters, navId);
            if (matched.navId) {
              this.activeNav = matched.navId;
              this.activeSideRouter = matched.sideRouterId;
              this.sideRouters = nav.subRouters;
              if (this.$route.query.from !== 'projectTicket' && (this.$route.name === 'CreateTicket' || this.$route.name === 'TicketDetail')) {
                this.sideRouters = [];
              }
              return true;
            } if (this.isMatchedByPrefix(nav.prefix)) {
              this.activeNav = nav.id;
              this.activeSideRouter = '';
              this.sideRouters = nav.subRouters;
              return true;
            }
          } else {
            if (this.$route.path === nav.path) {
              this.activeNav = nav.id;
              this.activeSideRouter = '';
              this.sideRouters = [];
              return true;
            }
          }
        });
        if (!hasMatched) {
          this.activeNav = this.$route.name;
          this.activeSideRouter = '';
          this.sideRouters = [];
        }
      },
      traverseSubRouter(routers, navId) {
        let matched = {};
        routers.some((item) => {
          if (Array.isArray(item.subRouters) && item.subRouters.length > 0) {
            matched = this.traverseSubRouter(item.subRouters, navId);
          } else {
            if (this.$route.path === item.path || this.isMatchedByPrefix(item.prefix)) {
              matched = {
                navId,
                sideRouterId: item.id,
              };
            }
          }
          return !!matched.navId;
        });
        return matched;
      },
      isMatchedByPrefix(prefix) {
        if (!prefix) {
          return false;
        }
        return prefix.some((path) => {
          if (typeof path === 'string') {
            return this.$route.path.indexOf(path) === 0;
          }
          if (typeof path === 'function') {
            const res = path(this.$route);
            return res && this.$route.path.indexOf(res) === 0;
          }
        });
      },
      // @todo 获取可展示到页面的服务，工单管理改版后没有这些服务的导航项，应该去掉
      getAccessService() {
        return this.$store.dispatch('getCustom').then((res) => {
          const customList = res.data;
          this.$store.commit('changeMsg', customList);
          this.$store.commit('changeCustom', customList);
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 头部导航点击
      async handleTopNavClick(router) {
        // if (router.id === 'manage') {
        //     await this.$store.dispatch('project/getProjectInfo')
        //     if (this.hasPermission(['project_view'])) {
        //         bus.$emit('togglePermissionApplyPage', false)
        //         this.$router.push(router.path)
        //     } else {
        //         const projectInfo = this.$store.state.project.projectInfo
        //         const resourceData = {
        //             project: [{
        //                 id: projectInfo.resource_id,
        //                 name: projectInfo.resource_name
        //             }]
        //         }
        //         const data = this.applyForPermission(['project_view'], [], resourceData, true)
        //         bus.$emit('togglePermissionApplyPage', true, 'other', data)
        //         this.activeNav = 'manage'
        //         this.sideRouters = []
        //         return
        //     }
        // }
        if (router.id === 'project') {
          this.$router.push({ name: 'projectServiceList', query: { project_id: this.$store.state.project.id } });
        } else {
          this.$router.push(router.path);
        }
        if (router.path === this.$route.path) {
          this.reload();
        }
      },
      // 侧边栏导航点击
      handleSideRouterClick(router) {
        if (this.activeNav === 'project') {
          const query = {};
          if (this.$store.state.project.id) {
            query.project_id = this.$store.state.project.id;
          }
          this.$router.push({ name: router.id, query });
        } else {
          this.$router.push(router.path);
        }
        if (router.path === this.$route.path) {
          this.reload();
        }
      },
      onGoToProjectList() {
        this.$router.push({ name: 'ProjectList' });
      },
      onLogOut() {
        location.href = `${window.login_url}?c_url=${window.location.href}`;
      },
      // 切换项目
      onSelectProject(val) {
        this.selectedProject = val;
        window.DEFAULT_PROJECT = val;
        this.$store.commit('project/setProjectId', val);
        this.$store.dispatch('project/changeDefaultProject', val);
        // 申请权限页面新建项目跳到项目单据下
        let path = this.$route.name;
        if (this.$route.name === 'projectServiceEdit') {
          path = 'projectServiceList';
        }
        this.$router.push({ name: this.$route.name === 'ProjectGuide' ? 'projectServiceList' : path, query: { project_id: val } });
      },
      applyForProjectViewPerm(project, perm) {
        if (!this.hasPermission([perm], project.auth_actions)) {
          const resourceData = {
            project: [{
              id: project.key,
              name: project.name,
            }],
          };
          this.applyForPermission([perm], project.auth_actions, resourceData);
          return false;
        }
        return true;
      },
      handleCreateProject() {
        if (!this.hasPermission(['project_create'])) {
          this.applyForPermission(['project_create'], [], {});
          return;
        }
        this.projectForm.color = ['#90a1ff', '#bb90ff', '#ffd990'][this.projectList.length % 3];
        this.isEditDialogShow = true;
      },
      goToProjectManage() {
        this.$router.push({ name: 'ProjectList' });
      },
      onProjectDialogConfirm(key) {
        this.isEditDialogShow = false;
        this.getProjectList();
        this.onSelectProject(key);
      },
      onProjectDialogCancel() {
        this.isEditDialogShow = false;
      },
    },
  };
</script>
<style lang="scss" scoped>
    .logo-icon {
        color: #3a84ff;
        font-size: 24px;
    }
    .nav-header {
        display: flex;
        align-items: center;
    }
    .create-bill-btn {
        margin-right: 40px;
        padding: 0 8px;
    }
    .nav-list {
        display: flex;
        .nav-item {
            display: flex;
            height: 50px;
            align-items: center;
            margin-right: 40px;
            font-size: 14px;
            & > a {
                color: #96a2b9;
            }
            &.active > a {
                color: #ffffff;
            }
            &:hover {
                > a {
                    color: #d3d9e4;
                }
            }
        }
    }
    .quick-entry {
        position: absolute;
        right: 30px;
        top: 10px;
        display: flex;
        align-items: center;
        .right-question-icon {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 10px;
            height: 32px;
            width: 32px;
            color: #768197;
            font-size: 16px;
            border-radius: 50%;
            cursor: pointer;
            &:hover {
                background: #252f43;
                color: #3a84ff;
            }
        }
        .user-name {
            color: #96a2b9;
            font-size: 14px;
            cursor: pointer;
            &:hover {
                color: #ffffff;
            }
        }
        .language-btn {
          color: #768197;
          font-size: 18px;
          &:hover {
            color: #3a84ff;
          }
        }
    }
    /deep/ .project-select.bk-select {
        border: none;
        border-bottom: 1px solid #cec6cc;
        box-shadow: none;
        .bk-select-name {
            padding: 3px 22px 15px;
            font-size: 14px;
            font-weight: bold;
            height: 32px;
            line-height: 1;
        }
        .bk-select-angle {
            top: 0;
            right: 6px;
        }
    }
    .page-container {
        height: 100%;
    }
    .navigation-menu-item {
        margin: 0;
        flex: 0 0 42px;
        padding: 0 12px 0 22px;
    }
    .nav-group-wrap {
        width: 100%;
        .group-name {
            padding: 0 12px 0 22px;
            line-height: 42px;
            font-size: 12px;
            color: #c3c6cc;
        }
    }
</style>
<style lang="scss">
    .tippy-popper .tippy-tooltip.navigation-popover-theme {
        padding: 0;
        background: #ffffff;
        box-shadow: 0px 2px 4px 0px rgba(0, 0, 0, 0.1);
        border-radius: 0;
    }
    .nav-operate-list, .nav-language-list {
        padding: 4px 0;
        .operate-item, .language-item {
            min-width: 80px;
            height: 30px;
            line-height: 30px;
            color: #63656e;
            text-align: center;
            cursor: pointer;
            > a {
                color: #63656e;
            }
            &:hover {
                background-color: #eaf3ff;
                color: #3a84ff;
                > a {
                    color: #3a84ff;
                }
            }
        }
        .active {
          background-color: #eaf3ff;
        }
    }
    .project-select-extension {
        padding: 12px 0;
        overflow: hidden;
        .action-item {
            float: left;
            width: 50%;
            line-height: 1;
            text-align: center;
            cursor: pointer;
            &:hover {
                color: #3a84ff;
            }
            &:first-child {
                border-right: 1px solid #dcdee5;
            }
        }
    }
</style>
<style lang="scss">
    .project-select-popover {
        .bk-option-content {
            padding: 0;
        }
        .project-item {
            padding: 0 16px;
        }
    }
</style>
