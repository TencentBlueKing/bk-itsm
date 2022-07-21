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
  <div class="bk-api-editor-result">
    <ul class="bk-request-ul">
      <li v-for="(item, index) in jsonTitleList"
        :key="index"
        :class="{ 'bk-api-check': jsonCheckIndex === index }"
        @click="changTitle(item, index)">
        <span>{{item.name}}</span>
      </li>
    </ul>
    <template v-if="!jsonCheckIndex">
      <div class="mb10">
        <bk-button :theme="'primary'"
          data-test-id="apiDetail_button_importResultJSON"
          :title="$t(`m.systemConfig['导入JSON']`)"
          :disabled="basicInfo.is_builtin"
          @click="closeDictionary">
          {{$t(`m.systemConfig['导入JSON']`)}}
        </bk-button>
      </div>
      <api-request-body
        :is-builtin="basicInfo.is_builtin"
        :tree-data-list="responseTreeDataList"
        @addBrotherLine="addBodyLine"
        @addChildLine="addBodyChild"
        @deleteLine="deleteBodyLine">
      </api-request-body>
    </template>
    <template v-else>
      <ace
        :value="bodyDetailConfig.value"
        :width="bodyDetailConfig.width"
        :height="bodyDetailConfig.height"
        :read-only="bodyDetailConfig.readOnly"
        :lang="bodyDetailConfig.lang"
        :full-screen="bodyDetailConfig.fullScreen"
        :theme="'textmate'"
        @init="editorInitAfter">
      </ace>
    </template>
    <bk-dialog
      v-model="dictDataTable.showDialog"
      :render-directive="'if'"
      :width="dictDataTable.width"
      :header-position="dictDataTable.headerPosition"
      :loading="secondClick"
      :auto-close="dictDataTable.autoClose"
      :mask-close="dictDataTable.autoClose"
      :title="$t(`m.systemConfig['导入JSON']`)"
      @confirm="submitDictionary">
      <div class="bk-add-module">
        <ace
          :value="responseDetailConfig.value"
          :width="responseDetailConfig.width"
          :height="responseDetailConfig.height"
          :read-only="responseDetailConfig.readOnly"
          :lang="responseDetailConfig.lang"
          :full-screen="responseDetailConfig.fullScreen"
          :theme="'textmate'"
          @blur="blur"
          @init="importEditorInitAfter">
        </ace>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
  import apiRequestBody from './apiRequestBody.vue';
  import ace from '../../../commonComponent/aceEditor/index.js';
  import mixins from '../../../commonMix/mixins_api.js';

  export default {
    components: {
      apiRequestBody,
      ace,
    },
    mixins: [mixins],
    props: {
      detailInfoOri: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        secondClick: false,
        // 导入JSON
        dictDataTable: {
          showDialog: false,
          width: 700,
          headerPosition: 'left',
          autoClose: false,
          precision: 0,
          formInfo: {
            name: '',
            desc: '',
            id: '',
            code: '',
          },
          checkout: {
            name: '',
          },
        },
        bodyDetailConfig: {
          value: '',
          width: '100%',
          height: 300,
          readOnly: true,
          fullScreen: true,
          lang: 'json',
        },
        responseDetailConfig: {
          value: '',
          width: '100%',
          height: 200,
          readOnly: false,
          fullScreen: true,
          lang: 'json',
        },
        // tag
        titleList: [
          { name: 'JSON' },
          { name: 'RAW' },
        ],
        jsonTitleList: [
          { name: this.$t('m.systemConfig["模板"]') },
          { name: this.$t('m.systemConfig["预览"]') },
        ],
        checkIndex: 0,
        jsonCheckIndex: 0,
        // RAW
        rawInfo: {
          value: '',
        },
        bodyInfo: {
          checkInfo: {},
        },
      };
    },
    computed: {
      // 基本设置
      basicInfo: {
        // getter
        get() {
          return this.detailInfoOri;
        },
        // setter
        set(newVal) {
          this.$parent.DetailInfo = newVal;
        },
      },
      responseTreeDataList: {
        // getter
        get() {
          const responseTreeDataList = this.basicInfo.responseTreeDataList ? [...this.basicInfo.responseTreeDataList] : [];
          responseTreeDataList.forEach((item) => {
            this.recordParent(item, '');
          });
          return responseTreeDataList;
        },
        // setter
        set(newVal) {
          this.$set(this.$parent.DetailInfo, 'responseTreeDataList', newVal);
        },
      },
    },
    watch: {},
    mounted() {

    },
    methods: {
      async changTitle(item, index) {
        if (this.titleList.indexOf(item) !== -1) {
          this.checkIndex = index;
          return;
        }
        if (item.name === this.$t('m.systemConfig["预览"]') && this.jsonCheckIndex !== index) {
          const rootdata = await this.listToJsonschema(this.basicInfo.responseTreeDataList);
          this.bodyDetailConfig.value = JSON.stringify(this.jsonschemaToJson(rootdata).root, null, 4);
        }
        this.jsonCheckIndex = index;
      },
      editorInitAfter() {
        // ...
      },
      importEditorInitAfter() {
        // ...
      },
      importChange() {
        // ...
      },
      blur(content) {
        this.responseDetailConfig.value = content;
      },
      // 新增Body
      addBodyLine(node) {
        this.bodyInfo.checkInfo = node;
        if (!node.parentInfo) {
          return;
        }
        const addnode = {
          has_children: false,
          showChildren: false,
          checkInfo: false,
          key: '',
          is_necessary: false,
          default: '',
          type: 'string',
          desc: '',
          parentInfo: node.parentInfo,
        };
        node.parentInfo.children.splice(node.parentInfo.children.indexOf(node), 0, addnode);
      },
      addBodyChild(node) {
        this.bodyInfo.checkInfo = node;
        const addnode = {
          has_children: false,
          showChildren: false,
          checkInfo: false,
          key: node.type === 'array' ? 'items' : '',
          is_necessary: false,
          default: '',
          type: 'string',
          desc: '',
          parentInfo: this.bodyInfo.checkInfo,
        };
        if (!node.children || !node.children.length) {
          this.$set(node, 'children', []);
          node.has_children = true;
          node.showChildren = true;
        }
        node.children.push(addnode);
      },
      // 删除
      deleteBodyLine(node) {
        this.bodyInfo.checkInfo = node;
        if (!node.parentInfo) {
          return;
        }
        node.parentInfo.children.splice(node.parentInfo.children.indexOf(node), 1);
      },
      recordParent(tree, parentInfo) {
        tree.parentInfo = parentInfo;
        if (tree.children === null || (tree.children && !tree.children.length)) {
          return;
        }
        tree.children.forEach((item) => {
          this.recordParent(item, tree);
        });
      },
      closeDictionary(e, id) {
        this.dictDataTable = Object.assign({}, {
          showDialog: !this.dictDataTable.showDialog,
          title: this.$t('m.systemConfig["导入JSON"]'),
          formInfo: {
            name: '',
            desc: '',
            id: id || '',
            code: '',
          },
          checkout: {
            name: '',
          },
          width: 700,
          headerPosition: 'left',
          autoClose: false,
          precision: 0,
        });
      },
      // 导入JSON
      async submitDictionary() {
        let rootJsonschemaData = {};
        try {
          rootJsonschemaData = this.jsonToJsonschema(JSON.parse(this.responseDetailConfig.value));
          this.basicInfo.responseTreeDataList = this.jsonschemaToList(rootJsonschemaData);
          this.closeDictionary();
        } catch (err) {
          this.$bkMessage({
            message: err.message ? err.message : err,
            theme: 'error',
          });
        }
      },
    },
  };
</script>

<style lang="scss" scoped>
    @import '../../../../scss/mixins/clearfix.scss';
    @import '../../../../scss/mixins/scroller.scss';

    .bk-request-ul {
        @include clearfix;
        margin-bottom: 10px;
        li {
            float: left;
            padding: 0 12px;
            line-height: 36px;
            color: #737987;
            font-size: 14px;
            cursor: pointer;
        }
        .bk-api-check {
            border-bottom: 2px solid #3c96ff;
            color: #3c96ff;
        }
    }
</style>
