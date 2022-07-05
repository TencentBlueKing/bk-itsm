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
  <div class="bk-add-api">
    <bk-form
      data-test-id="api_form_ApiInfo"
      :label-width="200"
      form-type="vertical"
      :model="directory.formInfo"
      :rules="rules"
      ref="addApiForm">
      <bk-form-item
        :label="$t(`m.systemConfig['接口分类']`)"
        :required="true"
        :property="'key'">
        <bk-select :disabled="!isAll && !!directory.formInfo.key"
          v-model="directory.formInfo.key"
          :clearable="false"
          searchable
          @selected="changeCode">
          <bk-option v-for="option in treeList.slice(1)"
            :key="option.id"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <template v-if="typeInfo === 'JOIN'">
        <bk-form-item
          :label="$t(`m.systemConfig['选择接口']`)"
          :required="true"
          :property="'road'">
          <bk-select :disabled="!directory.formInfo.key"
            v-model="directory.formInfo.road"
            :clearable="false"
            searchable
            @selected="changeMethod">
            <bk-option v-for="option in pathList"
              :key="option.path"
              :id="option.path"
              :name="option.name">
            </bk-option>
          </bk-select>
        </bk-form-item>
      </template>
      <bk-form-item
        :label="$t(`m.systemConfig['接口名称']`)"
        :required="true"
        :property="'name'">
        <bk-input maxlength="120"
          :placeholder="$t(`m.systemConfig['请输入接口名称']`)"
          v-model="directory.formInfo.name">
        </bk-input>
      </bk-form-item>
      <bk-form-item :label="$t(`m.systemConfig['负责人：']`)">
        <member-select v-model="directory.formInfo.ownersInputValue"></member-select>
      </bk-form-item>
      <bk-form-item
        :label="$t(`m.systemConfig['函数名称']`)">
        <!-- eslint-disable vue/camelcase -->
        <bk-input
          :placeholder="$t(`m.systemConfig['请输入函数名称']`)"
          v-model="directory.formInfo.func_name">
        </bk-input>
        <!-- eslint-enable -->
      </bk-form-item>
      <bk-form-item
        :label="$t(`m.systemConfig['接口路径']`)">
        <bk-input v-model="directory.formInfo.road" placeholder="please input path"
          :disabled="(directory.formInfo.category === 'component' || directory.formInfo.category === 'buffet_component') && typeInfo !== 'ADD'">
          <template slot="prepend">
            <bk-dropdown-menu class="group-text"
              @show="dropdownShow"
              @hide="dropdownHide"
              ref="requestwayDrop"
              slot="append"
              :font-size="'normal'">
              <bk-button type="primary" slot="dropdown-trigger">
                <span> {{ directory.formInfo.type }} </span>
                <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShow }]"></i>
              </bk-button>
              <ul class="bk-dropdown-list" slot="dropdown-content">
                <li v-for="(requestway, requestwayIndex) in typeList" :key="requestwayIndex">
                  <a href="javascript:;" @click="requestHandler(requestway, requestwayIndex)">
                    {{ requestway.name }}
                  </a>
                </li>
              </ul>
            </bk-dropdown-menu>
          </template>
        </bk-input>
      </bk-form-item>
      <bk-form-item
        :label="$t(`m.systemConfig['版本号']`)">
        <bk-input
          :placeholder="$t(`m.systemConfig['请输入版本号']`)"
          v-model="directory.formInfo.version">
        </bk-input>
      </bk-form-item>
      <bk-form-item
        :label="$t(`m.systemConfig['API描述']`)">
        <bk-input
          :placeholder="$t(`m.systemConfig['请输入API描述']`)"
          :type="'textarea'"
          :rows="3"
          v-model="directory.formInfo.desc">
        </bk-input>
      </bk-form-item>
    </bk-form>
    <p class="bk-form-message">
      {{ $t('m.systemConfig["注：详细的接口数据可以在编辑页面中添加"]') }}
    </p>
    <div class="mb20">
      <bk-button theme="primary"
        data-test-id="api_button_AccessApi_createApi"
        :title="$t(`m.systemConfig['确认']`)"
        :loading="secondClick"
        class="mr10"
        @click="submitAdd">
        {{ $t('m.systemConfig["确认"]') }}
      </bk-button>
      <bk-button theme="default"
        data-test-id="api_button_closeSideslider"
        :title="$t(`m.systemConfig['取消']`)"
        :disabled="secondClick"
        @click="closeAdd">
        {{ $t('m.systemConfig["取消"]') }}
      </bk-button>
    </div>
  </div>
</template>

<script>
  import commonMix from '../../commonMix/common.js';
  import memberSelect from '../../commonComponent/memberSelect';
  import { errorHandler } from '../../../utils/errorHandler.js';

  export default {
    name: 'addApiInfo',
    components: { memberSelect },
    mixins: [commonMix],
    props: {
      treeList: {
        type: Array,
        default() {
          return [];
        },
      },
      pathList: {
        type: Array,
        default() {
          return [];
        },
      },
      firstLevelInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      typeInfo: {
        type: String,
        default() {
          return '';
        },
      },
    },
    data() {
      return {
        secondClick: false,
        is_builtin: true,
        // 数据
        directory: {
          formInfo: {
            name: '',
            key: '',
            type: 'GET',
            road: '',
            is_activated: true,
            func_name: '',
            version: 'v1',
            category: '',
            ownersInputValue: [],
            desc: '',
          },
        },
        // 校验
        checkInfo: {
          name: '',
          road: '',
        },
        // 请求方式
        typeList: [
          { name: 'GET' },
          { name: 'POST' },
          // { name: 'DELETE' },
          // { name: 'PUT' },
          // { name: 'PATCH' }
        ],
        isDropdownShow: false,
        // 校验
        rules: {},
      };
    },
    computed: {
      isAll() {
        if (this.firstLevelInfo.code) {
          this.directory.formInfo.key = this.firstLevelInfo.id;
          this.$parent.$parent.$parent.getChannelPathList(this.firstLevelInfo.code);
          return false;
        }
        return true;
      },
    },
    mounted() {
      // 校验
      this.rules.key = this.checkCommonRules('select').select;
      this.rules.road = this.checkCommonRules('select').select;
      this.rules.name = this.checkCommonRules('name').name;
    },
    methods: {
      // 取消
      closeAdd() {
        this.$parent.$parent.openShade();
      },
      // 添加
      submitAdd() {
        this.$refs.addApiForm.validate().then(() => {
          this.addHandel();
        }, (validator) => {
          console.warn(validator);
        });
      },
      getRemoteSystemData() {
        this.$parent.$parent.getRemoteSystemData();
      },
      // 新增api
      addHandel() {
        if (this.secondClick) {
          return;
        }
        const params = {
          remote_system: this.directory.formInfo.key,
          name: this.directory.formInfo.name,
          method: this.directory.formInfo.type,
          owners: this.directory.formInfo.ownersInputValue.join(','),
          path: this.directory.formInfo.road,
          is_activated: this.directory.formInfo.is_activated,
          desc: this.directory.formInfo.desc,
          func_name: this.directory.formInfo.func_name || 'func_name',
          version: this.directory.formInfo.version,
          category: this.directory.formInfo.category,
          req_params: [],
          req_headers: [],
          rsp_data: {},
          req_body: {},
        };
        this.secondClick = true;
        this.$store.dispatch('apiRemote/post_remote_api', params).then(() => {
          this.$bkMessage({
            message: this.$t('m.systemConfig["添加成功"]'),
            theme: 'success',
          });
          this.getRemoteSystemData();
          this.closeAdd();
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.secondClick = false;
          });
      },
      switchChange(isActivated) {
        this.directory.formInfo.is_activated = isActivated;
      },
      changeMethod(path) {
        const dataItem = this.pathList.filter(item => item.path === path)[0];
        this.directory.formInfo.type = dataItem.method;
        this.directory.formInfo.func_name = dataItem.func_name;
        this.directory.formInfo.name = dataItem.label;
        this.directory.formInfo.version = dataItem.version || 'v1';
        this.directory.formInfo.category = dataItem.category;
      },
      changeCode(id) {
        // 切换 清空
        this.directory.formInfo = {
          name: '',
          key: id,
          type: 'GET',
          road: '',
          is_activated: true,
          func_name: '',
          version: 'v1',
          category: 'component',
          ownersInputValue: [],
          desc: '',
        };
        const dataItem = this.treeList.slice(1).filter(item => item.id === id)[0];
        this.$parent.$parent.$parent.getChannelPathList(dataItem.code);
      },
      dropdownShow() {
        this.isDropdownShow = true;
      },
      dropdownHide() {
        this.isDropdownShow = false;
      },
      requestHandler(requestway) {
        this.directory.formInfo.type = requestway.name;
        this.$refs.requestwayDrop.hide();
      },
    },
  };
</script>

<style lang="scss" scoped>
    .bk-form-message {
        font-size: 14px;
        color: #63656E;
        margin-bottom: 20px;
    }
</style>
