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
  <div class="tag-table">
    <label v-if="!hiddenLabel" class="table-label">{{ label }}</label>
    <bk-table
      ref="tagTable"
      :data="form.value"
      :border="true">
      <bk-table-column
        v-for="(item) in column"
        :key="item.key"
        :label="item.name"
        :prop="item.key">
        <template slot-scope="scope">
          <ViewItem
            :scheme="getScheme(item, scope.row[item.key])"
            :form="scope.row[item.key]">
          </ViewItem>
        </template>
      </bk-table-column>
    </bk-table>
  </div>
</template>

<script>
  import { getFormMixins } from '../formMixins';
  const tableAttrs = {
    column: {
      type: Array,
      default: () => ([
        {
          name: '操作',
          type: 'text',
          key: 'column1',
        },
        {
          name: '关联相关内容',
          key: 'column2',
          scheme: 'table_text_scheme',
          attrs: {
          },
        },
        {
          name: '申请期限',
          type: 'text',
          key: 'column3',
          attrs: {
            sort: true,
          },
        },
      ]),
    },
    value: {
      type: Array,
      default: () => ([]),
    },
  };
  export default {
    name: 'TagTable',
    components: {
      ViewItem: () => import('../ViewItem.vue'),
    },
    mixins: [getFormMixins(tableAttrs)],
    methods: {
      /**
       * scheme 优先级：from.scheme > item.scheme > item.type
       */
      getScheme(item, form) {
        const { schemes } = this.getContext();
        if (form && form.scheme && schemes[form.scheme]) {
          return schemes[form.scheme];
        }
        if (item.scheme) {
          return schemes[item.scheme];
        }
        if (form && form.type) {
          return {
            type: form.type,
          };
        }
        return {
          type: item.type,
        };
      },
    },
  };
</script>
<style lang="scss">
.tag-data-table {
    .view-item {
        &:first-child {
            margin-top: 0;
        }
    }
}
</style>
<style lang="scss" scoped>
.tag-table {
    width: 100%;
}
.table-breadcrumb {
    margin: 0;
    margin-bottom: 15px;
    color: #63656e;
    font-size: 14px;
    font-weight: 700px;
    text-align: left;
}
.table-label {
    margin-bottom: 8px;
    display: block;
    width: 100%;
    text-align: left;
    font-weight: bold;
    word-break: break-all;
    font-size: 12px;
    color: #63656e;
}
</style>
