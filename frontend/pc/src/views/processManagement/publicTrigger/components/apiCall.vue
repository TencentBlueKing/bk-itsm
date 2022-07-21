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
  <div class="bk-api-call">
    <template v-for="(itemInfo, index) in item.wayInfo.field_schema">
      <bk-form-item :ext-cls="'bk-field-schema mb20'"
        :label="itemInfo.name"
        :required="itemInfo.required"
        :key="index"
        :desc="itemInfo.tips">
        <template v-if="itemInfo.key === 'api_source'">
          <bk-select :ext-cls="'bk-form-display'"
            v-model="itemInfo.systemId"
            :clearable="false"
            :placeholder="$t(`m.treeinfo['请选择接入系统']`)"
            searchable
            @selected="changeCode(...arguments, itemInfo)">
            <bk-option v-for="option in apiSysList"
              :key="option.id"
              :id="option.id"
              :name="option.name">
            </bk-option>
          </bk-select>
          <template v-if="itemInfo.systemId">
            <bk-select :ext-cls="'bk-form-display'"
              v-model="itemInfo.apiId"
              :clearable="false"
              searchable
              @selected="changeApi(...arguments, itemInfo)">
              <bk-option v-for="option in apiList"
                :key="option.id"
                :id="option.id"
                :name="option.name">
              </bk-option>
            </bk-select>
          </template>
        </template>
        <template v-if="itemInfo.type === 'API_INFO' && apiId">
          <div style="min-height: 100px;" v-bkloading="{ isLoading: isLoading }">
            <input-params v-if="!isLoading"
              :item-info="itemInfo">
            </input-params>
          </div>
        </template>
      </bk-form-item>
    </template>
  </div>
</template>
<script>
  import { errorHandler } from '../../../../utils/errorHandler';
  import inputParams from '../apiContent/inputParams.vue';

  export default {
    name: 'apiCall',
    components: {
      inputParams,
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
        apiSysList: [],
        apiList: [],
        apiId: '',
        isLoading: false,
      };
    },
    mounted() {
      this.getRemoteSystemData();
      this.initData();
    },
    methods: {
      initData() {
        this.item.wayInfo.field_schema.forEach(schema => {
          if (schema.key === 'api_source' && schema.value) {
            this.getApiContent(schema.value);
          }
        });
      },
      getRemoteSystemData() {
        const params = {
          project_key: this.$route.query.project_id,
        };
        this.$store.dispatch('apiRemote/get_all_remote_system', params).then(res => {
          this.apiSysList = res.data.filter(item => item.is_activated);
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
          });
      },
      changeCode() {
        this.getApiTableList(arguments[2].systemId);
        arguments[2].apiId = '';
        this.apiId = '';
      },
      getApiTableList(id) {
        console.log(id);
        const params = {
          remote_system: id || '',
        };
        this.$store.dispatch('apiRemote/get_remote_api', params).then(res => {
          this.apiList = res.data.filter(ite => ite.is_activated);
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {

          });
      },
      changeApi(value) {
        this.isLoading = true;
        const apiContent = this.apiList.filter(item => item.id === arguments[0])[0];
        this.item.wayInfo.field_schema.forEach(item => {
          item.apiContent = apiContent;
          this.$set(item.apiContent, 'bodyTableData', []);
        });
        this.apiId = value;
        setTimeout(() => {
          this.isLoading = false;
        }, 1000);
      },
      getApiContent(id) {
        this.isLoading = true;
        const params = {
          id,
        };
        this.$store.dispatch('apiRemote/get_remote_api_detail', params).then(res => {
          const backValue = res.data;
          // 二次赋值渲染操作
          this.item.wayInfo.field_schema.forEach(schema => {
            if (schema.key === 'api_source' && schema.value) {
              schema.apiId = id;
              schema.systemId = backValue.remote_system;
            } else {
              schema.apiContent = backValue;
              this.$set(schema.apiContent, 'bodyTableData', []);
            }
          });
          this.getApiTableList(backValue.remote_system);
          this.apiId = id;
          setTimeout(() => {
            this.isLoading = false;
          }, 1000);
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {

          });
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../../scss/mixins/clearfix.scss';

    .bk-field-schema {
        padding: 0 18px;
    }
    .bk-form-display {
        float: left;
        width: 359px;
        margin-right: 10px;
        &:last-child{
            margin-right: 0;
        }
    }
</style>
