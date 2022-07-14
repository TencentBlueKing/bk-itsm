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
  <div class="bk-default-value">
    <!-- 单行文本 -->
    <template v-if="formInfo.type === 'STRING'">
      <bk-input :ext-cls="'bk-half'"
        :clearable="true"
        v-model="formInfo.default_value"
        :placeholder="$t(`m.treeinfo['请输入']`)">
      </bk-input>
    </template>
    <!-- 多行文本 -->
    <template v-if="formInfo.type === 'TEXT'">
      <div style="height: 30px;">
        <textarea style="width: 49%;"
          rows="8"
          class="bk-form-textarea bk-textarea-tanble"
          :placeholder="$t(`m.treeinfo['请输入']`)"
          v-model.trim="formInfo.default_value">
                </textarea>
      </div>
    </template>
    <!-- 富文本 -->
    <template v-if="formInfo.type === 'RICHTEXT'">
      <div>
        <rich-text-editor
          v-model="formInfo.default_value"
          :id="'default-rich-text-editor'"
          :full-title="label">
        </rich-text-editor>
      </div>
    </template>
    <!-- 下拉框 -->
    <template v-if="formInfo.type === 'MULTISELECT' || formInfo.type === 'CHECKBOX' || formInfo.type === 'SELECT' || formInfo.type === 'RADIO' || formInfo.type === 'INPUTSELECT'">
      <template v-if="formInfo.source_type === 'API' || formInfo.source_type === 'RPC'">
        <bk-input :ext-cls="'bk-half'"
          :clearable="true"
          v-model="formInfo.default_value"
          :placeholder="$t(`m.treeinfo['请输入']`)">
        </bk-input>
      </template>
      <template v-else>
        <bk-select :ext-cls="'bk-half'"
          v-model="formInfo.default_value"
          :multiple="(formInfo.type === 'MULTISELECT' || formInfo.type === 'CHECKBOX')"
          searchable
          @toggle="getSelectList">
          <bk-option v-for="option in selectList"
            :key="option.key"
            :id="option.key"
            :name="option.name">
          </bk-option>
        </bk-select>
      </template>
    </template>
    <!-- 数字类型 -->
    <template v-if="formInfo.type === 'INT'">
      <div class="bk-half">
        <bk-input :clearable="true"
          type="number"
          :precision="precision"
          v-model="formInfo.default_value">
        </bk-input>
      </div>
    </template>
    <!-- 日期 -->
    <template v-if="formInfo.type === 'DATE'">
      <div class="bk-half">
        <bk-date-picker v-model="formInfo.default_value"
          :placeholder="$t(`m.newCommon['选择日期']`)">
        </bk-date-picker>
      </div>
    </template>
    <!-- 时间 -->
    <template v-if="formInfo.type === 'DATETIME'">
      <div class="bk-half">
        <bk-date-picker v-model="formInfo.default_value"
          :type="'datetime'"
          :placeholder="$t(`m.newCommon['选择日期时间']`)">
        </bk-date-picker>
      </div>
    </template>
    <!-- 人员 -->
    <template v-if="formInfo.type === 'MEMBER'">
      <div style="width: 49%;">
        <member-select v-model="formInfo.default_value" :multiple="false"></member-select>
      </div>
    </template>
    <template v-if="formInfo.type === 'MEMBERS'">
      <div style="width: 49%;">
        <member-select v-model="formInfo.default_value">
        </member-select>
      </div>
    </template>
    <template v-if="formInfo.type === 'CUSTOM-FORM'">
      <div class="editor-wrap">
        <div class="editor-btn-group">
          <router-link
            target="_blank"
            :to="{ name: 'CustomFormTest' }"
            class="opt-item">{{ $t(`m.common['查看模板']`) }}</router-link>
          <span class="opt-item"
            @click="downCustomFormTempalte">
            {{ $t(`m.common['下载模板']`) }}</span>
        </div>
        <code-editor
          v-model="formInfo.default_value"
          :options="{ language: 'json' }">
        </code-editor>

      </div>
      <p v-if="checkStatus.customFormStatus" class="bk-field-error">
        {{ $t(`m.treeinfo['格式错误！（JSON 语法错误或者根元素缺少 schemes 和 form_data 属性）']`) }}
      </p>
    </template>
  </div>
</template>
<script>
  import memberSelect from '../../../../commonComponent/memberSelect';
  import RichTextEditor from '../../../../../components/form/richTextEditor/richTextEditor.vue';
  import CodeEditor from '../../../../../components/CodeEditor';
  import { CUSTOM_FORM_TEMPLATE } from '../../../../../constants/customFormTemplate';
  import { errorHandler } from '../../../../../utils/errorHandler';

  export default {
    name: 'defaultValue',
    components: {
      memberSelect,
      RichTextEditor,
      CodeEditor,
    },
    props: {
      formInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      fieldInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      dictionaryData: {
        type: Object,
        default() {
          return {};
        },
      },
      changeInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      label: {
        type: String,
        default: '',
      },
      checkStatus: {
        type: Object,
        default() {
          return {
          };
        },
      },
    },
    data() {
      return {
        selectList: [],
        // 记录是否更新过数据
        updateStatus: false,
        typeList: ['MULTISELECT', 'CHECKBOX', 'MEMBERS', 'MEMBER'],
        precision: 0,
      };
    },
    watch: {
      // 当字段类型，数据源发生变化时，清空数据
      'formInfo.source_type'() {
        if (this.updateStatus) {
          this.formInfo.default_value = (this.typeList.some(typeItem => typeItem === this.formInfo.type)) ? [] : '';
        }
        if (this.formInfo.source_type !== this.changeInfo.source_type) {
          this.updateStatus = true;
          this.formInfo.default_value = (this.typeList.some(typeItem => typeItem === this.formInfo.type)) ? [] : '';
        }
        if (this.formInfo.source_type === 'API' || this.formInfo.source_type === 'RPC') {
          this.formInfo.default_value = '';
        }
      },
      'formInfo.type'() {
        if (this.updateStatus) {
          this.formInfo.default_value = (this.typeList.some(typeItem => typeItem === this.formInfo.type)) ? [] : '';
        }
        if (this.formInfo.type !== this.changeInfo.type) {
          this.updateStatus = true;
          this.formInfo.default_value = (this.typeList.some(typeItem => typeItem === this.formInfo.type)) ? [] : '';
        }
        if (this.formInfo.source_type === 'API' || this.formInfo.source_type === 'RPC') {
          this.formInfo.default_value = '';
        }
      },
      'formInfo.default_value'() {
        if (this.formInfo.type === 'CUSTOM-FORM') {
          this.checkStatus.customFormStatus = false;
        }
      },
    },
    mounted() {
      if (this.changeInfo.id) {
        if (this.changeInfo.source_type === 'DATADICT') {
          this.getDictionList(this.changeInfo.source_uri);
        }
      }
      if (this.formInfo.default_value !== '') {
        this.getSelectList(this.formInfo.default_value);
      }
    },
    methods: {
      getSelectList(val) {
        this.selectList = [];
        if (val) {
          if (this.formInfo.source_type === 'CUSTOM') {
            // 自定义数据(去掉当前key和name不存在数据)
            this.selectList = this.fieldInfo.list.filter(item => (item.key && item.name));
          } else if (this.formInfo.source_type === 'DATADICT') {
            // 数据字典数据
            if (this.dictionaryData.check) {
              this.getDictionList(this.dictionaryData.check);
            }
          } else if (this.formInfo.source_type === 'API' || this.formInfo.source_type === 'RPC') {
            // 接口数据, RPC数据
            this.getApiList();
          }
        }
      },
      getDictionList(key) {
        const params = {
          key,
        };
        this.$store.dispatch('datadict/get_data_by_key', params).then((res) => {
          this.selectList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      downCustomFormTempalte() {
        const link = document.createElement('a');
        const time = +new Date();
        link.download = `bk_itsm_custom_form_template_${time}.json`;
        link.href = `data:text/plain,${JSON.stringify(CUSTOM_FORM_TEMPLATE, null, 4)}`;
        link.click();
      },
      getApiList() {
        // ...
        // const params = {
        //     api_instance_id: '',
        //     kv_relation: {}
        // }
        // this.$store.dispatch('apiRemote/get_data_workflow', params).then((res) => {
        //     this.selectList = res.data
        // }).catch(res => {
        //     this.$bkMessage({
        //         message: res.data.msg,
        //         theme: 'error'
        //     })
        // })
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../../../scss/mixins/scroller';
    .bk-half {
        width: 49%;
        position: relative;
        z-index: 2;
    }
    .bk-textarea-tanble {
        position: absolute;
        float: left;
        padding: 5px 10px;
        width: 225px;
        height: 32px;
        min-height: 32px;
        line-height: 1.5 !important;
        overflow-y: scroll;
        @include scroller;
        &:focus {
            height: 160px!important;
            z-index: 10;
        }
    }
    .editor-wrap {
        position: relative;
        width: 100%;
        height: 300px;
        .editor-btn-group {
            position: absolute;
            right: 0;
            top: -30px;
            z-index: 1;
            .opt-item {
                color: #3a84ff;
                cursor: pointer;
                &:not(:first-child) {
                    margin-left: 8px;
                }
            }
        }
    }
    .bk-field-error {
        margin-bottom: 10px;
        line-height: 32px;
        color: #ff5656;
        font-size: 12px;
    }
</style>
