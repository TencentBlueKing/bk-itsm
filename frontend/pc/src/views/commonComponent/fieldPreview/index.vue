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
  <div class="field-view">
    <template v-for="(item, index) in cloneFields">
      <li v-if="item.type === 'TABLE'" style="width: 100%; margin-bottom: 10px;" :key="index">
        <span class="bk-li-left">{{item.name}}：</span>
        <div class="bk-form-content bk-over-more" style="margin-left: 0px; overflow: hidden; width: 100%;">
          <bk-table :data="item.value"
            :size="'small'">
            <template v-for="title in item.choice">
              <bk-table-column :label="title.name" :key="title.key">
                <template slot-scope="props">
                  <span :title="props.row[title.key]">{{ props.row[title.key] }}</span>
                </template>
              </bk-table-column>
            </template>
          </bk-table>
        </div>
      </li>
      <li v-else-if="item.type === 'CUSTOMTABLE'" style="width: 100%; margin-bottom: 10px;" :key="index">
        <span class="bk-li-left">{{item.name}}：</span>
        <div class="bk-form-content bk-over-more" style="margin-left: 0px; overflow: hidden; width: 100%;">
          <bk-table :data="item.value"
            :size="'small'">
            <template v-for="column in item.meta.columns">
              <bk-table-column :label="column.name" :key="column.key">
                <template slot-scope="props">
                  <span :title="props.row[column.key]">{{ getCustomTableDisplayValue(column, props.row) || '--' }}</span>
                </template>
              </bk-table-column>
            </template>
          </bk-table>
        </div>
      </li>
      <li v-else-if="item.type === 'FILE'"
        :class="{ 'bk-big-width': item.layout === 'COL_12' }"
        :key="index">
        <div v-for="(file, ind) in item.fileShow" :key="ind">
          <p style="line-height: 30px;">
            <span class="bk-li-left"><span v-if="ind === 0">{{item.name}}：</span></span>
            <span class="bk-li-right" @click="downFile(file,item)" style="cursor: pointer;">
              <i v-if="item.value !== ''" style="color: rgb(60, 150, 255)"
                class="bk-icon icon-download bk-tab-cursor"></i>
              {{file.name}}
            </span>
          </p>
        </div>
      </li>
      <li v-else-if="item.type === 'RICHTEXT'"
        :class="{ 'bk-big-width': item.layout === 'COL_12' }"
        :key="index">
        <span class="bk-li-left" style="float: initial;">{{item.name}}：</span>
        <span class="bk-li-right"
          v-html="item.value">
        </span>
      </li>
      <li v-else-if="item.type === 'TEXT'"
        :class="{ 'bk-big-width': item.layout === 'COL_12' }"
        :key="index">
        <span class="bk-li-left" style="float: initial;">{{item.name}}：</span>
        <span class="bk-li-right"
          :title="item.display_value">
          <pre>{{item.display_value || item.value || '--'}}</pre>
        </span>
      </li>
      <li v-else-if="item.type === 'LINK'"
        :class="{ 'bk-big-width': item.layout === 'COL_12' }"
        :key="index" :title="item.value">
        <span class="bk-li-left">{{item.name}}：</span>
        <span class="bk-pot-after bk-li-link" @click="goToLink(item.value)">{{ $t('m.newCommon["点击查看"]') }}</span>
      </li>
      <li v-else-if="item.type === 'CUSTOM-FORM'"
        :class="{ 'bk-big-width': item.layout === 'COL_12' }"
        :key="index">
        <div class="bk-li-left">{{item.name}}：</div>
        <div style="clear: left;">
          <render-view
            :form-data="item.value.form_data"
            :context="{ schemes: item.value.schemes }">
          </render-view>
        </div>
      </li>
      <li v-else
        :class="{ 'bk-big-width': item.layout === 'COL_12' }"
        :key="index">
        <span class="bk-li-left">{{item.name}}：</span>
        <span class="bk-li-right"
          :title="item.display_value">{{item.display_value || item.value || '--'}}</span>
      </li>
    </template>
  </div>
</template>

<script>
  import RenderView from '../../../components/renderview/RenderView';
  import { deepClone } from '../../../utils/util.js';
  import { getCustomTableDisplayValue } from '@/components/RenderField/fieldUtils';

  export default {
    name: 'fieldPreview',
    components: {
      RenderView,
    },
    props: {
      fields: {
        type: Array,
        required: true,
        default: () => [],
      },
      ticketId: {
        type: [Number, String],
        default: () => '',
      },
      statedId: {
        type: [Number, String],
        default: () => '',
      },
      commentId: {
        type: String,
        default: () => '',
      },
    },
    data() {
      return {
        downFileUrl: '',
        cloneFields: [],
        customForm: {
          formData: [],
          context: {},
        },
      };
    },
    watch: {
      fields: {
        handler() {
          this.initFields();
        },
        immediate: true,
      },
    },
    methods: {
      initFields() {
        this.cloneFields = deepClone(this.fields);
        this.cloneFields.forEach((item) => {
          if (item.type === 'CUSTOM-FORM') {
            item.value = typeof item.value === 'string' ? JSON.parse(item.value) : item.value;
          }
          if (item.type === 'FILE') {
            this.$set(item, 'fileShow', []);
            const temp = JSON.parse(item.value);
            for (const key in temp) {
              item.fileShow.push({ ...temp[key], key });
            }
          }
        });
      },
      goToLink(url) {
        if (url.indexOf('http') !== 0) {
          url = `http://${url}`;
        }
        window.open(url, '_blank');
      },
      valToList() {
        const tempObj = JSON.parse(this.item.value);
        for (const key in tempObj) {
          this.fileList.push(tempObj[key]);
        }
      },
      downFile(file, item) {
        this.downFileUrl = `${window.SITE_URL}api/ticket/fields/${item.id}/download_file/?unique_key=${file.key}&file_type=ticket`;
        window.open(this.downFileUrl);
      },
      onBlur() {
        const markValue = this.editor.getMarkdown();
        this.item.val = markValue;
      },
      getCustomTableDisplayValue(column, value) {
        return getCustomTableDisplayValue(column, value);
      },
    },
  };
</script>

<style scoped lang='scss'>
    @import '../../../scss/mixins/clearfix.scss';
    @import '../../../scss/mixins/scroller.scss';

    .bk-table .th-center {
        text-align: center;
    }

    .field-view {
        @include clearfix;
        @include scroller;

        .bk-li-link{
            color: #3a84ff;
            cursor: pointer;
            font-weight: bold;
        }

        .bk-tab-cursor {
            cursor: pointer;
        }

        li {
            width: 50%;
            padding-right: 10px;
            float: left;
            color: #63656E;
            line-height: 28px;
            font-size: 12px;
            word-wrap: break-word;
        }

        .bk-li-left {
            font-weight: bold;
            float: left;
        }

        .bk-li-right {
            padding-left: 5px;
            color: #63656E;
        }

        .bk-big-width {
            width: 100%;
        }
    }

    .bk-over-more {
        overflow: auto;
        @include scroller(#e6e9ea);
    }

    .bk-hover-info {
        position: absolute;
        top: 20px;
        left: 0;
        border: 1px solid #ccc;
        color: #737987;
        line-height: 20px;
        font-size: 12px;
        padding: 0 15px;
        line-height: 24px;
        background-color: #fff;
        border-radius: 4px;
        display: none;
        z-index: 100;
    }
</style>
