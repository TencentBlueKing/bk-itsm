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
  <div class="project-page" v-bkloading="{ isLoading: projectDetailLoading }">
    <router-view v-if="$store.state.project.id && !projectDetailLoading"></router-view>
  </div>
</template>
<script>
  import { mapState } from 'vuex';
  import { errorHandler } from '@/utils/errorHandler';
  import permission from '@/mixins/permission.js';

  export default {
    name: 'ProjectHome',
    mixins: [permission],
    data() {
      return {
        projectDetailLoading: false,
      };
    },
    computed: {
      ...mapState({
        projectListLoading: state => state.project.projectListLoading,
      }),
    },
    watch: {
      '$store.state.project.id'(val) {
        if (val) {
          this.getProjectDetail();
        }
      },
    },
    created() {
      if (this.$store.state.project.id !== this.$route.query.project_id && this.$route.query.project_id !== '') {
        this.$store.commit('project/setProjectId', this.$route.query.project_id);
      }
      this.getProjectList();
      if (this.$store.state.project.id) {
        this.getProjectDetail();
      }
    },
    methods: {
      async getProjectDetail() {
        try {
          this.projectDetailLoading = true;
          await this.$store.dispatch('project/getProjectDetail', this.$store.state.project.id);
        } catch (e) {
          errorHandler(e, this);
        } finally {
          this.projectDetailLoading = false;
        }
      },
      async getProjectList() {
        try {
          this.$store.commit('project/setProjectListLoading', true);
          const res = await this.$store.dispatch('project/getProjectAllList');
          this.$store.commit('project/setProjectList', res.data);
          const projectsWithViewPerm = this.$store.state.project.projectList.filter(item => item.auth_actions.includes('project_view'));
          if (projectsWithViewPerm.length === 0) {
            this.$router.replace({ name: 'ProjectGuide' });
          }
          if (!this.$store.state.project.id && projectsWithViewPerm.length !== 0) {
            this.$store.commit('project/setProjectId', projectsWithViewPerm[0].key);
            this.$store.dispatch('project/changeDefaultProject', projectsWithViewPerm[0].key);
            this.$router.replace({ name: 'projectServiceList', query: { project_id: projectsWithViewPerm[0].key } });
          }
        } catch (e) {
          errorHandler(e, this);
        } finally {
          this.$store.commit('project/setProjectListLoading', false);
        }
      },
    },
  };
</script>
<style lang="scss" scoped>
    .project-page {
        height: calc(100vh - 52px);
    }
</style>
