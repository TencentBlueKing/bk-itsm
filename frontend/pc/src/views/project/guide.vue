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
  <div class="project-guide-page">
    <empty-tip
      :title="emptyTip.title"
      :sub-title="emptyTip.subTitle"
      :desc="emptyTip.desc"
      :links="emptyTip.links">
      <template slot="btns">
        <bk-button theme="primary"
          v-cursor="{ active: !hasPermission(['project_create']) }"
          :class="{
            'btn-permission-disable': !hasPermission(['project_create'])
          }"
          @click="handleCreateProject">
          {{ $t(`m['立即创建']`) }}
        </bk-button>
        <bk-button style="margin-left: 6px;" @click="handleApplyProject">{{ $t('m["申请项目权限"]') }}</bk-button>
      </template>
    </empty-tip>
  </div>
</template>
<script>
  import EmptyTip from '../project/components/emptyTip.vue';
  import bus from '@/utils/bus';
  import permission from '@/mixins/permission.js';

  export default {
    name: 'ProjectGuidePage',
    components: {
      EmptyTip,
    },
    mixins: [permission],
    data() {
      return {
        emptyTip: {
          title: this.$t('m[\'你当前没有任何项目权限，你可以\']'),
          desc: [
            {
              src: require('../../images/illustration/apply.svg'),
              title: this.$t('m[\'申请已有项目权限 或 创建新项目\']'),
              content: this.$t('m[\'流程服务以“项目”维度来隔离不同服务团队的资源，根据你的需求选择创建全新的项目，或者申请已存在项目的访问权限来使用/管理你的服务吧。\']'),
            },
            {
              src: require('../../images/illustration/start-service.svg'),
              title: this.$t('m[\'开始使用流程服务\']'),
              content: this.$t('m[\'在这里，你可以按需定制化设计服务流程，来满足不同场景的 IT服务诉求，设置 SLA 保障流程的质量把控，帮助企业规范、高效的管理各种应用场景的流程。\']'),
            },
          ],
          links: [
            {
              text: this.$t('m[\'第一次使用流程服务？ 一键带你快速入门\']'),
              btn: this.$t('m[\'产品文档\']'),
              href: 'https://bk.tencent.com/docs/document/6.0/145/6592',
            },
            {
              text: this.$t('m[\'了解更详细的流程服务产品架构和功能介绍，点击查阅产品白皮书\']'),
              btn: this.$t('m[\'产品文档\']'),
              href: 'https://bk.tencent.com/docs/document/6.0/145/6592',
            },
          ],
        },
      };
    },
    async created() {
      const res = await this.$store.dispatch('project/getProjectAllList');
      this.$store.commit('project/setProjectList', res.data);
      const projectsWithViewPerm = res.data.filter(item => item.auth_actions.includes('project_view'));
      if (projectsWithViewPerm.length !== 0) {
        this.$router.replace({ name: 'projectTicket', query: { project_id: projectsWithViewPerm[0].key } });
      }
    },
    methods: {
      handleCreateProject() {
        bus.$emit('openCreateProjectDialog');
      },
      async handleApplyProject() {
        const projectInfo = this.$store.state.project.projectInfo;
        const resourceData = {
          project: [{
            id: projectInfo.key || '0',
            name: projectInfo.name || this.$t('m[\'默认项目\']'),
          }],
        };
        const params = this.applyForPermission(['project_view'], projectInfo.auth_actions, resourceData, true);
        const res = await this.$store.dispatch('common/getIamUrl', params);
        if (res.data) {
          window.open(res.data.url, '__blank');
        }
      },
    },
  };
</script>
<style lang="scss" scoped>
    .project-guide-page {
        padding: 20px;
    }
</style>
