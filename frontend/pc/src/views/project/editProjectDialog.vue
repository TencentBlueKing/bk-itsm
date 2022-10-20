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
  <bk-dialog
    :value="isShow"
    render-directive="if"
    :title="title"
    :width="600"
    :auto-close="false"
    :mask-close="false"
    :loading="editProjectPending"
    @confirm="onEditProjectConfirm"
    @cancel="$emit('cancel')">
    <div class="project-form">
      <bk-form
        ref="projectForm"
        form-type="vertical"
        :model="projectForm"
        :rules="projectRules">
        <bk-form-item property="name" :label="$t(`m['项目名称']`)" :required="true" error-display-type="normal">
          <bk-input
            v-model="projectForm.name"
            :maxlength="100"
            :show-word-limit="true"
            :disabled="editDialogFormDisable"
            :placeholder="$t(`m['请输入项目名称，不超过100个字符']`)">
          </bk-input>
        </bk-form-item>
        <bk-form-item property="key" :label="$t(`m['项目代号']`)" :required="true" error-display-type="normal">
          <bk-input
            v-model="projectForm.key"
            :maxlength="32"
            :show-word-limit="true"
            :disabled="!!project.key || editDialogFormDisable"
            :placeholder="$t(`m['请输入项目代号，以英文字母开头，可包含小写字母、数字、下划线、中横线']`)">
          </bk-input>
        </bk-form-item>
        <bk-form-item property="desc" :label="$t(`m['项目说明']`)">
          <bk-input
            v-model="projectForm.desc"
            type="textarea"
            :maxlength="255"
            :label="$t(`m['请输入项目说明']`)"
            :placeholder="$t(`m['请输入项目说明']`)">
          </bk-input>
        </bk-form-item>
      </bk-form>
    </div>
  </bk-dialog>
</template>
<script>
  import { deepClone } from '@/utils/util';
  import { errorHandler } from '@/utils/errorHandler.js';
  import i18n from '@/i18n/index.js';

  export default {
    name: 'EditProjectDialog',
    props: {
      isShow: {
        type: Boolean,
        default: false,
      },
      title: String,
      project: {
        type: Object,
        default() {
          return {
            name: '',
            key: '',
            desc: '',
            color: '',
          };
        },
      },
      editDialogFormDisable: Boolean,
    },
    data() {
      return {
        projectForm: deepClone(this.project),
        editProjectPending: false,
        projectRules: {
          name: [
            {
              required: true,
              message: '必填项',
              trigger: 'blur',
            },
            {
              validator: this.validateName,
              message(val) {
                return `${val}-此项目名称已存在`;
              },
              trigger: 'blur',
            },
          ],
          key: [
            {
              required: true,
              message: '必填项',
              trigger: 'blur',
            },
            {
              regex: /^[a-z][a-z0-9-_]+$/,
              message: '由小写字母，数字，下划线，横线组成，必须以英文字母开头',
              trigger: 'blur',
            },
            {
              validator: this.validateKey,
              message(val) {
                return `${val}-此项目代号已存在`;
              },
              trigger: 'blur',
            },
          ],
          desc: [
          ],
        },
      };
    },
    watch: {
      isShow(val) {
        if (val) {
          this.projectForm = deepClone(this.project);
        }
      },
    },
    methods: {
      projectValidateList(list, type) {
        const projectList = [];
        projectList.push(list);
        if (this.title === i18n.t('m["编辑项目"]')) {
          projectList.length = 0;
          const result = list.filter(item => item[type] !== this.project[type]);
          projectList.push(result);
        }
        return projectList[0];
      },
      async validateName(val) {
        const projectList = this.projectValidateList(this.$store.state.project.projectList, 'name');
        return !projectList.map(item => item.name).includes(val);
      },
      async validateKey(val) {
        const projectList = this.projectValidateList(this.$store.state.project.projectList, 'key');
        return !projectList.map(item => item.key).includes(val);
      },
      onEditProjectConfirm() {
        this.$refs.projectForm.validate().then(async (result) => {
          if (result) {
            this.editProjectPending = true;
            const url = this.project.key ? 'project/updateProject' : 'project/createProject';
            try {
              await this.$store.dispatch(url, this.projectForm);
              this.$emit('confirm', this.projectForm.key);
            } catch (e) {
              errorHandler(e, this);
            } finally {
              this.editProjectPending = false;
            }
          }
        });
      },
    },
  };
</script>
