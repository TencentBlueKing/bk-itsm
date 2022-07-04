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
  <div class="bk-field-preview" id="bkPreview" ref="fieldContent">
    <bk-form :label-width="labelWidth" form-type="vertical" :ext-cls="'bk-ext-form'">
      <template v-for="(item, index) in fields">
        <div :key="index" v-if="item.showFeild" :class="{ 'bk-field-line': item.layout === 'COL_12', 'bk-field-half': item.layout === 'COL_6', 'bk-field-trigger': origin === 'trigger' }">
          <component :ref="'component' + index"
            :is="'CW-' + item.type"
            :item="item"
            :fields="fields"
            :basic-infomation="basicInfomation"
            :type-info="typeInfo"
            :disabled="disabled">
          </component>
          <!-- api和rpc字段添加刷新 -->
          <template v-if="origin !== 'trigger'">
            <i class="bk-icon icon-refresh bk-icon-refresh"
              :class="{ 'not-rotate': !rotate,'rotate': rotate }"
              v-if="item.source_type === 'API'"
              @click="freshBtn(item)">
            </i>
            <i class="bk-icon icon-refresh bk-icon-refresh"
              :class="{ 'not-rotate': !rotate,'rotate': rotate }"
              v-if="item.source_type === 'RPC'"
              @click="freshRpc(item)">
            </i>
          </template>
        </div>
      </template>
    </bk-form>
  </div>
</template>
<script>
  import string from '../../commonComponent/fieldComponent/string.vue';
  import link from '../../commonComponent/fieldComponent/link';
  import int from '../../commonComponent/fieldComponent/int.vue';
  import text from '../../commonComponent/fieldComponent/text.vue';
  import checkbox from '../../commonComponent/fieldComponent/checkbox.vue';
  import radio from '../../commonComponent/fieldComponent/radio.vue';
  import select from '../../commonComponent/fieldComponent/select.vue';
  import inputSelect from '../../commonComponent/fieldComponent/inputSelect';
  import multiselect from '../../commonComponent/fieldComponent/multiselect.vue';
  import date from '../../commonComponent/fieldComponent/date.vue';
  import datetime from '../../commonComponent/fieldComponent/datetime.vue';
  import member from '../../commonComponent/fieldComponent/member.vue';
  import members from '../../commonComponent/fieldComponent/members.vue';
  import table from '../../commonComponent/fieldComponent/table.vue';
  import customtable from '../../commonComponent/fieldComponent/customtable.vue';
  import editor from '../../commonComponent/fieldComponent/editor.vue';
  import tree from '../../commonComponent/fieldComponent/tree.vue';
  import file from '../../commonComponent/fieldComponent/file.vue';
  import cascade from '../../commonComponent/fieldComponent/cascade.vue';
  import sopsTemplate from '../../commonComponent/fieldComponent/sopsTemplate.vue';
  import devopsTemplate from '../../commonComponent/fieldComponent/devopsTemplate.vue';

  import apiFieldsWatch from '../../commonMix/api_fields_watch.js';
  import commonMix from '../../commonMix/common.js';
  import { isEmpty } from '../../../utils/util';
  import { errorHandler } from '../../../utils/errorHandler';

  export default {
    name: 'fieldInfo',
    components: {
      'CW-STRING': string,
      'CW-LINK': link,
      'CW-INT': int,
      'CW-TEXT': text,
      'CW-CHECKBOX': checkbox,
      'CW-RADIO': radio,
      'CW-SELECT': select,
      'CW-INPUTSELECT': inputSelect,
      'CW-MULTISELECT': multiselect,
      'CW-DATE': date,
      'CW-DATETIME': datetime,
      'CW-MEMBER': member,
      'CW-MEMBERS': members,
      'CW-TABLE': table,
      'CW-CUSTOMTABLE': customtable,
      'CW-RICHTEXT': editor,
      'CW-TREESELECT': tree,
      'CW-FILE': file,
      'CW-CASCADE': cascade,
      'CW-SOPS_TEMPLATE': sopsTemplate,
      'CW-DEVOPS_TEMPLATE': devopsTemplate,
    },
    mixins: [apiFieldsWatch, commonMix],
    props: {
      fields: {
        type: Array,
        required: true,
        default: () => [],
      },
      // fields 往往指的是单节点上的字段列表，allFields 表示所有节点上的字段列表
      allFieldList: {
        type: Array,
        default: () => [],
      },
      basicInfomation: {
        type: Object,
        default() {
          return {};
        },
      },
      origin: {
        type: String,
        default: 'normal',
      },
      typeInfo: {
        type: String,
        default() {
          return '';
        },
      },
      disabled: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        rotate: false,
        labelWidth: 200,
      };
    },
    created() {
      // 内置一个校验参数
      this.fields.forEach((item) => {
        this.$set(item, 'checkValue', false);
      });
    },
    mounted() {
      this.$nextTick(() => {
        this.labelWidth = this.$refs.fieldContent.clientWidth / 2 || 200;
      });
    },
    methods: {
      freshBtn(item) {
        this.rotate = !this.rotate;
        if (this.$route.name === 'CreateTicket') {
          this.freshApi(item, this.fields, 'submit');
        } else {
          this.freshApi(item, this.fields, 'field');
        }
      },
      freshRpc(item) {
        this.rotate = !this.rotate;
        this.$store.dispatch('apiRemote/getRpcData', item).then((res) => {
          item.choice = res.data;
          item.val = '';
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 字段值进行装换
      fieldChange() {
        this.fieldFormatting(this.fields);
      },
      // 内置任务模板字段校验 标准运维/蓝盾
      checkBuiltInTaskTemplate() {
        const checks = [];
        this.fields.forEach((item, index) => {
          if (item.type === 'SOPS_TEMPLATE' || item.type === 'DEVOPS_TEMPLATE') {
            checks.push(this.$refs[`component${index}`][0].validate());
          }
        });
        return checks.every(check => !!check);
      },
      // 字段间联合校验
      jointVerification() {
        let allPass = true;
        const relateValid = this.relatedRegex(this.fields, isEmpty(this.allFieldList) ? this.fields : this.allFieldList);
        relateValid.validList.forEach((item) => {
          if (!item.result) {
            allPass = false;
            item.validList.forEach((it) => {
              const target = this.fields.find(field => field.key === it.key);
              if (target && !target.checkValue) { // 字段处理验证通过状态才去改变，不然会去覆盖原来错误提示
                target.checkValue = true;
                target.checkMessage = it.tips;
              }
            });
          }
        });
        return allPass;
      },
      // 必填校验
      requiredVerification() {
        // 字段为空校验
        const requireValidList = this.fields.filter(it => it.showFeild && it.validate_type === 'REQUIRE').filter((it) => {
          if (it.type === 'CUSTOMTABLE') {
            // 自定义表格需要单独校验每一列
            return it.meta.columns.some(column => column.required);
          }
          if (it.type === 'SOPS_TEMPLATE' || it.type === 'DEVOPS_TEMPLATE') {
            return false;
          }
          return true;
        });
        const validateList = requireValidList.filter((it) => {
          let checkValue = false;
          it.checkValue = false;
          let msg = ''; // 自定义校验报错内容
          switch (it.type) {
            case 'TABLE': {
              let allEmpty1 = true;
              it.choice.forEach((item) => {
                if (it.value[0][item.key] !== '') {
                  allEmpty1 = false;
                } else {
                  msg += (`${item.name}, `);
                }
              });
              checkValue = allEmpty1;
              if (msg) {
                msg += this.$t('m.newCommon["为必填项！"]');
              }
              break;
            }
            case 'CUSTOMTABLE': {
              let allEmpty2 = false;
              it.meta.columns.forEach(column => it.value.forEach((row) => {
                if (column.required && isEmpty(row[column.key])) {
                  msg += (`${column.name}, `);
                  allEmpty2 = true;
                }
              }));
              checkValue = allEmpty2;
              if (msg) {
                msg += this.$t('m.newCommon["为必填项！"]');
              }
              break;
            }
            default: {
              checkValue = isEmpty(it.value);
            }
          }
          if (msg) {
            it.checkMessage = msg;
            checkValue = true;
          }
          it.checkValue = checkValue;
          return checkValue;
        });
        const sopStatus = this.checkBuiltInTaskTemplate();
        return !validateList.length && sopStatus;
      },
      /**
       * 字段校验
       * 1、当前 fields 里的 value 根据 type 转换
       * 2、联合字段校验
       * 3、必填校验
       */
      checkValue() {
        this.fieldChange();
        const allPass1 = this.requiredVerification();
        const allPass2 = this.jointVerification();
        return allPass1 && allPass2;
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../scss/mixins/clearfix.scss';
    @import '../../../scss/mixins/scroller.scss';

    .bk-ext-form {
        width: 100%;
        display: flex;
        flex-wrap: wrap;
        @include clearfix;
        .bk-field-line {
            width: 100%;
            position: relative;
            padding: 0 10px 10px 0;
        }
        .bk-field-half {
            width: 50%;
            position: relative;
            padding: 0 10px 10px 0;
        }
        .bk-field-trigger{
            width: 280px;
            position: relative;
            padding: 0 10px 10px 0;
            /deep/ .bk-label{
                display: none;
            }
        }
        .bk-icon-refresh {
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 16px;
            color: #3a84ff;
            cursor: pointer;
        }
        .rotate {
            transition: all 1s;
            transform: rotate(360deg);
        }
        .not-rotate{
            transform: rotate(0deg);
        }
    }
    .error-msg {
        word-wrap: break-word;
        word-break: break-all;
        overflow: hidden;
        font-size: 12px;
        color: #ff5656;
    }
    /deep/ .bk-form-item.is-required .bk-label{
        width: auto !important;
    }
</style>
