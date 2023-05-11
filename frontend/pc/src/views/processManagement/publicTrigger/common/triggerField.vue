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
  <div class="bk-trigger-field">
    <template v-if="item.type === 'STRING' || item.type === 'TEXT'">
      <bk-input v-model="item.value"
        :maxlength="120">
      </bk-input>
    </template>
    <template v-else-if="item.type === 'INT'">
      <bk-input :clearable="true"
        type="number"
        v-model="item.value">
      </bk-input>
    </template>
    <template v-else-if="item.type === 'SELECT' || item.type === 'RADIO'">
      <bk-select searchable
        v-model="item.value"
        :loading="item.loading">
        <bk-option v-for="option in item.options"
          :key="option.key"
          :id="option.key"
          :name="option.name">
        </bk-option>
      </bk-select>
    </template>
    <template v-else-if="item.type === 'CHECKBOX' || item.type === 'MULTISELECT'">
      <bk-select searchable
        multiple
        v-model="item.value"
        :loading="item.loading">
        <bk-option v-for="option in item.options"
          :key="option.key"
          :id="option.key"
          :name="option.name">
        </bk-option>
      </bk-select>
    </template>
    <template v-else-if="item.type === 'MEMBERS' || item.type === 'MULTI_MEMBERS' || item.type === 'MEMBER'">
      <member-select
        v-model="item.value">
      </member-select>
    </template>
    <template v-else-if="item.type === 'DATE'">
      <bk-date-picker v-model="item.value"
        :placeholder="$t(`m.newCommon['选择日期']`)">
      </bk-date-picker>
    </template>
    <template v-else-if="item.type === 'DATETIME'">
      <bk-date-picker v-model="item.value"
        :type="'datetime'"
        :placeholder="$t(`m.newCommon['选择日期时间']`)">
      </bk-date-picker>
    </template>
    <template v-else>
      <bk-input v-model="item.value"
        :maxlength="120">
      </bk-input>
    </template>
  </div>
</template>
<script>
  import memberSelect from '../../../commonComponent/memberSelect';
  import { mapState } from 'vuex';
  import { errorHandler } from '../../../../utils/errorHandler';

  export default {
    name: 'triggerFields',
    components: {
      memberSelect,
    },
    props: {
      item: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        keyList: [],
      };
    },
    computed: {
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
      ...mapState('trigger', {
        triggerVariables: state => state.triggerVariables,
      }),
    },
    watch: {
      triggerVariables(newVal) {
        this.keyList = newVal;
      },
    },
    created() {
      // 当存在值的时候，初始化拉取数据
      if (this.item.value) {
        this.keyList = this.triggerVariables;
        this.getConditionList();
      }
    },
    methods: {
      // 根据条件的不同，填充不同的conditionList数据
      getConditionList() {
        // 获取选中的项
        const checkItem = this.keyList.filter(item => item.key === this.item.key)[0];
        const typeList = ['SELECT', 'RADIO', 'MULTISELECT', 'CHECKBOX'];
        if (typeList.some(item => item === checkItem.type)) {
          // 数据字典
          this.$set(this.item, 'loading', true);
          this.$set(this.item, 'options', []);
          if (checkItem.source_type === 'DATADICT') {
            this.$store.dispatch('datadict/get_data_by_key', {
              key: checkItem.source_uri,
              field_key: checkItem.key,
            }).then((res) => {
              this.item.options = res.data.map((ite) => {
                const temp = {
                  key: ite.key,
                  name: ite.name,
                };
                return temp;
              });
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.item.loading = false;
              });
          } else if (checkItem.source_type === 'API') {
            this.$store.dispatch('apiRemote/get_data_workflow', {
              kv_relation: checkItem.kv_relation,
              api_instance_id: checkItem.api_instance_id,
            }).then((res) => {
              this.item.options = res.data.map((ite) => {
                const temp = {
                  key: ite.key,
                  name: ite.name,
                };
                return temp;
              });
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.item.loading = false;
              });
          } else if (checkItem.source_type === 'RPC') {
            this.$store.dispatch('apiRemote/getRpcData', {
              meta: checkItem.meta,
              source_uri: checkItem.source_uri,
            }).then((res) => {
              this.item.options = res.data.map((ite) => {
                const temp = {
                  key: ite.key,
                  name: ite.name,
                };
                return temp;
              });
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.item.loading = false;
              });
          } else {
            this.item.options = checkItem.choice.map((ite) => {
              const temp = {
                key: ite.key,
                name: ite.name,
              };
              return temp;
            });
            this.item.loading = false;
          }
        }
      },
    },
  };
</script>


