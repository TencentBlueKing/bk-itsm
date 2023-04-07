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
  <div class="view-item">
    <!-- 面包屑 -->
    <div v-if="crumbsList.length > 1" class="bread-crumbs">
      <span
        v-for="(crumbs, index) in crumbsList"
        :key="index"
        class="crumbs-item"
        @click.stop="onCrumbsClick(index)">
        {{ crumbs.label }}
      </span>
    </div>
    <component
      v-if="crumbsList.length <= 1"
      :is="componentType"
      :form="form"
      v-bind="getAttrs(form)">
    </component>
    <render-view
      v-else
      ref="childrenView"
      :hidden-label="true"
      :form-data="childrenViewConfig.form_data"
      :context="getContext()">
    </render-view>
  </div>
</template>
<script>
  import TagText from './tags/TagText.vue';
  import TagTable from './tags/TagTable.vue';
  import { deepClone } from '../../utils/util';
  export default {
    name: 'ViewItem',
    components: {
      TagText,
      TagTable,
      RenderView: () => import('./RenderView'),
    },
    inject: ['getContext'],
    props: {
      scheme: {
        type: Object,
        default: () => ({}),
      },
      form: {
        type: Object,
        default: () => ({}),
      },
      isTop: {
        type: Boolean,
        default: false,
      },
      topIndex: {
        type: Number,
      },
    },
    data() {
      return {
        crumbsList: [],
        childrenViewConfig: {
          form_data: [],
        },
      };
    },
    computed: {
      componentType() {
        return `Tag${this.scheme.type.replace(/^[a-z]/, item => item.toUpperCase())}`;
      },
      currentDisplatCrumbs() {
        return this.crumbsList[this.crumbsList.length - 1] || {
          label: '默认',
          form_data: [],
        };
      },
    },
    created() {
      this.appendCrumbsItem(this.form.label, this.form);
    },
    methods: {
      getAttrs(form) {
        return { ...this.scheme.attrs, ...form };
      },
      /**
       * 追加面包屑项
       * @param { String  } label 面包屑名
       * @param { Array  } formData 渲染数据
       */
      appendCrumbsItem(label, formData) {
        this.crumbsList.push({
          label,
          form_data: deepClone(formData),
        });
        this.updateChildViewConfig();
      },
      getScheme(form) {
        const { schemes } = this.getContext();
        if (schemes[form.scheme]) {
          return schemes[form.scheme];
        }
        return {};
      },
      onCrumbsClick(index) {
        this.crumbsList = this.crumbsList.filter((item, i) => i <= index);
        this.updateChildViewConfig();
      },
      updateChildViewConfig() {
        this.childrenViewConfig = {
          form_data: deepClone(this.currentDisplatCrumbs.form_data),
        };
      },
    },
  };
</script>

<style lang="scss" scoped>
.render-view {
    width: 100%;
}
.view-item-wrap > .view-item {
    margin-top: 4px;
    word-break: break-all;
}
/deep/ .table-label {
  font-size: 14px;
}
.bread-crumbs {
    text-align: left;
    font-weight: bold;
    font-size: 12px;
    .crumbs-item {
        position: relative;
        margin-right: 10px;
        &:not(:first-child)::before {
            position: absolute;
            left: -8px;
            top: 0;
            content: '/';
        }
        &:not(:last-child) {
            cursor: pointer;
            color: #3a84ff;
        }
    }
}
// 提示 icon
/deep/ .bk-itsm-icon.icon-itsm-icon-help {
    font-size: 12px;
    cursor: pointer;
}
</style>
