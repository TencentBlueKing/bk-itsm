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
  <div class="bk-get-param">
    <bk-table
      v-if="isStatic"
      :data="sopsTableInfo"
      :ext-cls="'bk-editor-table'">
      <bk-table-column :label="$t(`m.treeinfo['字段名']`)" prop="name"></bk-table-column>
      <bk-table-column :label="$t(`m.treeinfo['参数值']`)" width="400">
        <template slot-scope="props">
          <span>{{props.row.value || '--'}}</span>
        </template>
      </bk-table-column>
    </bk-table>
    <!-- <bk-table :ext-cls="'bk-editor-table'"
            :data="paramTableShow"
            :size="'small'">
            <bk-table-column :label="$t(`m.treeinfo['字段名']`)" prop="name"></bk-table-column>
            <template v-if="!isStatic">
                <bk-table-column :label="$t(`m.treeinfo['字段类型']`)" prop="custom_type"></bk-table-column>
            </template>
            <bk-table-column :label="$t(`m.treeinfo['参数值']`)" width="400">
                <template slot-scope="props">
                    <template v-if="!isStatic">
                        <div style="width: 120px; position: absolute; top: 5px; left: 15px;">
                            <bk-select v-model="props.row.source_type"
                                :clearable="false"
                                searchable
                                :font-size="'medium'">
                                <bk-option v-for="option in sourceTypeList"
                                    :key="option.key"
                                    :id="option.key"
                                    :name="option.name">
                                </bk-option>
                            </bk-select>
                        </div>
                        <div class="bk-normal-textarea"
                            v-if="!props.row.source_type || (props.row.source_type === 'custom')"
                            style="width: 240px; position: absolute; top: 4px; right: 15px;">
                            <textarea style="width: 240px;"
                                class="bk-form-textarea bk-textarea-tanble"
                                :placeholder="$t(`m.treeinfo['请输入参数值，换行分隔']`)"
                                v-model.trim="props.row.value">
                            </textarea>
                        </div>
                        <div v-else style="width: 240px; position: absolute; top: 4px; right: 15px;">
                            <bk-select :ref="'selectSops' + props.row.key"
                                v-model="props.row.value"
                                :clearable="false"
                                searchable
                                :font-size="'medium'">
                                <bk-option v-for="option in stateList"
                                    :key="option.key"
                                    :id="option.key"
                                    :name="option.name">
                                </bk-option>
                                <div slot="extension" @click="addNewItem(props.row)" style="cursor: pointer;">
                                    <i class="bk-icon icon-plus-circle mr10"></i>{{ $t('m.treeinfo["添加变量"]') }}
                                </div>
                            </bk-select>
                        </div>
                    </template>
                    <template v-else>
                        <span>{{props.row.value || '--'}}</span>
                    </template>
                </template>
            </bk-table-column>
        </bk-table> -->
    <div class="sops-form">
      <render-form
        ref="renderForm"
        :form-option="formOptions"
        :constants="constants"
        :context="context"
        :key="renderKey"
        v-model="formData"
        :hooked="hookedVarList"
        @configLoadingChange="configLoading = $event">
        <template slot="tagHook" slot-scope="{ scheme }">
          <div class="hook-area">
            <bk-checkbox
              :disabled="disabled || disabledRenderForm"
              :value="!!hookedVarList[scheme.tag_code]"
              @change="onHookChange($event, scheme)">
              {{ $t(`m.tickets["引用变量"]`) }}
            </bk-checkbox>
            <div v-if="hookedVarList[scheme.tag_code]" class="var-select">
              <bk-select
                :disabled="disabled || disabledRenderForm"
                :clearable="false"
                searchable
                :value="formData[scheme.tag_code].replace(/^\$\{/, '').replace(/\}$/, '')"
                @selected="onSelectVar($event, scheme)">
                <bk-option
                  v-for="varItem in stateList"
                  :key="varItem.key"
                  :id="varItem.key"
                  :name="varItem.name">
                  {{ varItem.name }}
                </bk-option>
              </bk-select>
            </div>
          </div>
        </template>
      </render-form>
    </div>
    <div class="bk-add-slider" v-if="sliderInfo.show && isStatic === false">
      <bk-sideslider
        :is-show.sync="sliderInfo.show"
        :title="sliderInfo.title"
        :width="sliderInfo.width">
        <div class="p20" slot="content">
          <add-field
            :change-info="changeInfo"
            :sosp-info="showTabData"
            :workflow="flowInfo.id"
            :state="configur.id"
            @closeShade="closeShade"
            @getRelatedFields="getRelatedFields">
          </add-field>
        </div>
      </bk-sideslider>
    </div>
  </div>
</template>

<script>
  import addField from '../addField/index.vue';
  import { deepClone } from '@/utils/util.js';

  export default {
    name: 'sopsGetParam',
    components: {
      addField,
    },
    props: {
      quoteVars: Array,
      constantDefaultValue: Object,
      context: {
        type: Object,
        default() {
          return {};
        },
      },
      constants: {
        type: Array,
        default() {
          return [];
        },
      },
      isStaticData: {
        type: Array,
        default() {
          return [];
        },
      },
      configur: {
        type: Object,
        default() {
          return {};
        },
      }, // 流程信息
      flowInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      // 节点信息
      stateList: {
        type: Array,
        default() {
          return [];
        },
      },
      // 是否仅展示 数据
      isStatic: {
        type: Boolean,
        default() {
          return false;
        },
      },
      hookedVarList: Object,
      isHook: {
        type: Boolean,
        default() {
          return true;
        },
      },
      isEdit: {
        type: Boolean,
        default() {
          return true;
        },
      },
      initFormDate: Object,
    },
    data() {
      return {
        disabled: false,
        ticketDisable: false,
        disabledRenderForm: false,
        // quoteVarsLoading: false,
        configLoading: false,
        quoteErrors: [], // 变量引用校验不同通过列表
        renderKey: '',
        formData: {},
        formOptions: {
          showRequired: true,
          showGroup: true,
          showLabel: true,
          showHook: this.isHook,
          showDesc: true,
          formEdit: !this.disabled && !this.disabledRenderForm && this.isEdit,
        },
        fieldList: [],
        checkInfo: {
          name: '',
          road: '',
        },
        biz: [
          {
            name: this.$t('m.treeinfo["业务"]'),
            custom_type: '',
            source_type: 'custom',
            value: '--',
            key: 1,
          },
        ],
        changeInfo: {
          workflow: '',
          id: '',
          key: '',
          name: '',
          type: 'STRING',
          desc: '',
          layout: 'COL_12',
          validate_type: 'REQUIRE',
          choice: [],
          is_builtin: false,
          source_type: 'CUSTOM',
          source_uri: '',
          regex: 'EMPTY',
          custom_regex: '',
          is_tips: false,
          tips: '',
        },
        sourceTypeList: [
          {
            id: 1,
            key: 'custom',
            name: this.$t('m.treeinfo["自定义"]'),
          },
          {
            id: 2,
            key: 'component_inputs',
            name: this.$t('m.treeinfo["引用变量"]'),
          },
        ],
        sliderInfo: {
          title: this.$t('m.treeinfo["添加变量"]'),
          show: false,
          width: 700,
        },
        showTabData: {},
        sopsTableInfo: [],
      };
    },
    computed: {},
    watch: {
      constants: {
        handler() {
          this.renderKey = new Date().getTime();
        },
        deep: true,
      },
      isEdit() {
        this.renderKey = new Date().getTime();
      },
    },
    mounted() {
      if (this.isStatic) {
        this.sopsTableInfo = [];
        this.isStaticData.forEach((item) => {
          const ite = {
            name: item.name,
            value: item.value,
          };
          this.sopsTableInfo.push(ite);
        });
      }
    },
    methods: {
      onHookChange(val, scheme) {
        this.$emit('onChangeHook', scheme.tag_code, val);
        const constantItem = this.constants.find(item => item.key === scheme.tag_code);
        constantItem.is_quoted = val;
        if (val) {
          this.formData[scheme.tag_code] = '';
        } else {
          this.formData[scheme.tag_code] = constantItem ? deepClone(this.constantDefaultValue[scheme.tag_code]) : this.initFormDate[scheme.tag_code].value;
          const index = this.quoteErrors.findIndex(item => item === scheme.tag_code);
          if (index > -1) {
            this.quoteErrors.splice(index, 1);
          }
        }
      },
      changeTicketformDisable(val) {
        this.$set(this.$refs.renderForm.formOption, 'formEdit', val);
      },
      onSelectVar(val, scheme) {
        this.formData[scheme.tag_code] = `\${${val}}`;
      },
      getRenderFormValidate() {
        return this.$refs.renderForm.validate();
      },
      getRelatedFields() {
        this.$parent.getRelatedFields();
      },
      addNewItem(data) {
        this.showTabData = data;
        this.sliderInfo.show = true;
        this.$refs[`selectSops${data.key}`].close();
      },
      closeShade() {
        this.sliderInfo.show = false;
      },
      showNew(sopsinfo, res) {
        this.paramTableShow.forEach((item) => {
          if (item.key === sopsinfo.key) {
            item.value = res.data.key;
          }
        });
      },
    },
  };
</script>

<style lang="scss" scoped>
.hook-area {
    display: flex;
    height: 32px;
    flex-wrap: nowrap;
    align-items: center;
    .var-select {
        position: relative;
        margin-left: 14px;
        width: 200px;
        .quote-error {
            border-color: #ff5757;
        }
    }
    .quote-error-text {
        position: absolute;
        bottom: -20px;
        left: 0;
        color: #ff5757;
    }
    .update-tips {
        position: absolute;
        right: -20px;
        top: 10px;
        font-size: 14px;
        color: #ff9c01;
        cursor: pointer;
    }
}
/deep/ .el-input__inner {
    width: 60%;
}
/deep/ .rf-tag-hook {
    top: 40px;
}
/deep/ .rf-tag-form {
    width: 76%;
}
</style>
