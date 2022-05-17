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
  <div class="bk-api-editor-basic">
    <bk-form
      :label-width="120"
      :model="basicInfo">
      <bk-form-item class="bk-editor-form"
        :required="true"
        :label="$t(`m.systemConfig['接口名称：']`)">
        <bk-input
          :disabled="basicInfo.is_builtin"
          :placeholder="$t(`m.systemConfig['请输入接口名称']`)"
          v-model="basicInfo.name">
        </bk-input>
      </bk-form-item>
      <template v-if="basicInfo.hasOwnProperty('method')">
        <bk-form-item class="bk-editor-form"
          :required="true"
          :label="$t(`m.systemConfig['接口路径：']`)">
          <bk-input v-model="basicInfo.path" placeholder="/path"
            :disabled="basicInfo.is_builtin">
            <template slot="prepend">
              <bk-dropdown-menu class="group-text"
                @show="dropdownShow"
                @hide="dropdownHide"
                ref="requestwayDrop"
                slot="append"
                :font-size="'normal'"
                :disabled="basicInfo.is_builtin">
                <bk-button type="primary" slot="dropdown-trigger">
                  <span> {{ basicInfo.method }} </span>
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
      </template>
      <bk-form-item class="bk-editor-form"
        :label="$t(`m.user['负责人：']`)">
        <member-select v-model="basicInfo.ownersInputValue"></member-select>
      </bk-form-item>
      <bk-form-item class="bk-editor-form"
        :label="$t(`m.systemConfig['备注：']`)">
        <bk-input :disabled="basicInfo.is_builtin "
          :placeholder="$t(`m.systemConfig['请输入描述']`)"
          :type="'textarea'"
          :rows="3"
          v-model="basicInfo.desc">
        </bk-input>
      </bk-form-item>
    </bk-form>
  </div>
</template>

<script>
  import memberSelect from '../../../commonComponent/memberSelect';
  export default {
    name: 'apiEditorBasic',
    components: { memberSelect },
    props: {
      detailInfoOri: {
        type: Object,
        default() {
          return {};
        },
      },
      // 分类列表
      treeList: {
        type: Array,
        default() {
          return [];
        },
      },
      // 接口列表
      pathList: {
        type: Array,
        default() {
          return [];
        },
      },
      // 内建系统列表
      isBuiltinIdList: {
        type: Array,
        default() {
          return [];
        },
      },
    },
    data() {
      return {
        // 请求方式
        typeList: [
          { name: 'GET' },
          { name: 'POST' },
          // { name: 'DELETE' },
          // { name: 'PUT' },
          // { name: 'PATCH' }
        ],
        // 状态
        stateList: [
          { id: 0, name: this.$t('m.systemConfig["未完成"]') },
          { id: 1, name: this.$t('m.systemConfig["已完成"]') },
        ],
        isDropdownShow: false,
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
    },
    watch: {},
    mounted() {
    },
    methods: {
      switchChange(isActivated) {
        this.basicInfo.is_activated = isActivated;
      },
      dropdownShow() {
        this.isDropdownShow = true;
      },
      dropdownHide() {
        this.isDropdownShow = false;
      },
      requestHandler(requestway) {
        this.$refs.requestwayDrop.hide();
        this.$emit('changeRequest', requestway.name);
      },
      changeMethod(val) {
        this.basicInfo.method = val;
      },
    },
  };
</script>

<style lang="scss" scoped>
    .bk-editor-form {
        width: 500px;
    }
</style>
