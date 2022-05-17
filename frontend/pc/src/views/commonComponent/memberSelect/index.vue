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
  <div :class="[extCls]" test-posi-id="bk-member-selector">
    <bk-user-selector
      :value="value"
      class="ui-user-selector"
      :fixed-height="true"
      :api="api"
      :disabled="disabled"
      :multiple="multiple"
      :placeholder="placeholder"
      :default-alternate="customUserList"
      :fuzzy-search-method="specifyIdList.length ? fuzzySearchMethod : null"
      @change="onChange">
    </bk-user-selector>
  </div>
</template>

<script>
  import BkUserSelector from '@blueking/user-selector';
  import jsonp from 'jsonp';
  import i18n from '@/i18n/index.js';

  export default {
    name: 'MemberSelector',
    components: {
      BkUserSelector,
    },
    model: {
      prop: 'value',
      event: 'change',
    },
    props: {
      /**
       * 指定的人员 id
       * 配置了该数组，就只能在该人员列表中选择
       */
      specifyIdList: {
        type: Array,
        default() {
          return [];
        },
      },
      placeholder: {
        type: String,
        default: i18n.t('m.newCommon["请选择"]'),
      },
      disabled: {
        type: Boolean,
        default: false,
      },
      // 多选
      multiple: {
        type: Boolean,
        default: true,
      },
      value: {
        type: Array,
        default() {
          return [];
        },
      },
      // 外部设置的 class name
      extCls: {
        type: String,
        default: '',
      },
    },
    data() {
      return {
        customUserList: [],
        users: [],
      };
    },
    computed: {
      api() {
        const host = window.BK_USER_MANAGE_HOST || location.origin;
        return `${host}/api/c/compapi/v2/usermanage/fs_list_users/`;
      },
    },
    created() {
      if (this.specifyIdList.length) {
        this.getCustomUserListByspecifyIdList();
      }
    },
    methods: {
      // 查询指定 id 用户信息
      getUserInfo(userIds) {
        return new Promise((resolve, reject) => {
          jsonp(`${this.api}?app_code=bk-magicbox&exact_lookups=${userIds.join(',')}&page_size=100&page=1`, null, (err, res) => {
            if (err) {
              reject(err);
            } else {
              resolve(res.data.results);
            }
          });
        });
      },
      // 通过指定用户 id 获取自定义备选列表数据
      getCustomUserListByspecifyIdList() {
        // 去除人员id中的（）
        const ids = this.specifyIdList.map(id => id.replace(/\(.*\)$/, ''));
        this.getUserInfo(ids).then((results) => {
          this.customUserList = results;
        });
      },
      // 模糊搜索匹配值，有 dataList 时生效
      fuzzySearchMethod(keyword) {
        const results = this.customUserList.filter((item) => {
          const names = item.username + item.display_name;
          return names.indexOf(keyword) > -1;
        });
        return Promise.resolve({
          next: true,
          results,
        });
      },
      onChange(value) {
        this.$emit('change', value);
      },
    },
  };
</script>

<style lang="scss" scoped>
    .ui-user-selector {
        width: 100%;
    }
</style>
