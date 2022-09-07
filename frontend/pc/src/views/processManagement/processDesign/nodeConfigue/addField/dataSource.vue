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
  <div class="bk-data-source">
    <!-- 总选数据框 -->
    <bk-select :ext-cls="typeClass"
      v-model="formInfo.source_type"
      :clearable="false"
      :disabled="dataSourceDisable"
      searchable
      @selected="changeSource">
      <bk-option v-for="option in sourceList"
        :key="option.typeName"
        :id="option.typeName"
        :name="option.name">
      </bk-option>
    </bk-select>
    <template v-if="formInfo.source_type === 'DATADICT'">
      <bk-select :ext-cls="'bk-halfline-item'"
        v-model="dictionaryData.check"
        :clearable="false"
        :disabled="dataSourceDisable"
        searchable>
        <bk-option v-for="option in dictionaryData.list"
          :key="option.key"
          :id="option.key"
          :name="option.name">
        </bk-option>
      </bk-select>
    </template>
    <template v-if="formInfo.source_type === 'API'">
      <bk-select :ext-cls="'bk-threeline-item bk-halfline-margin'"
        v-model="apiInfo.remote_system_id"
        :placeholder="$t(`m.treeinfo['请选择接入系统']`)"
        :clearable="false"
        :loading="isSystemLoading"
        searchable
        @selected="changeApiSystem">
        <bk-option v-for="option in apiSysList"
          :key="option.id"
          :id="option.id"
          :name="option.name">
        </bk-option>
      </bk-select>
      <bk-select :ext-cls="'bk-threeline-item'"
        v-model="apiInfo.remote_api_id"
        :placeholder="$t(`m.treeinfo['请选择接口']`)"
        :clearable="false"
        :loading="isApiLoading"
        searchable
        @selected="changeApiPort">
        <bk-option v-for="option in apiPortList"
          :key="option.id"
          :id="option.id"
          :name="option.name">
        </bk-option>
      </bk-select>
    </template>
    <template v-if="formInfo.source_type === 'RPC'">
      <bk-select :ext-cls="'bk-halfline-item'"
        v-model="prcData.check"
        :clearable="false"
        searchable
        @selected="changeRpc">
        <bk-option v-for="option in prcData.list"
          :key="option.key"
          :id="option.key"
          :name="option.name">
        </bk-option>
      </bk-select>
    </template>
  </div>
</template>
<script>
  import { errorHandler } from '../../../../../utils/errorHandler';
  export default {
    name: 'dataSource',
    components: {},
    mixins: [],
    props: {
      formInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      prcData: {
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
      apiInfo: {
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
    },
    data() {
      return {
        typeClass: '',
        isApiLoading: false,
        isSystemLoading: false,
        sourceList: [],
        apiSysList: [],
        apiPortList: [],
      };
    },
    computed: {
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
      dataSourceDisable() {
        return (this.changeInfo.is_builtin || this.changeInfo.source === 'TABLE' || (this.changeInfo.meta && this.changeInfo.meta.code === 'APPROVE_RESULT')) && this.formInfo.key !== 'bk_biz_id';
      },
    },
    watch: {
      'formInfo.type'() {
        this.initData();
        this.getSourceList();
      },
    },
    mounted() {
      this.initData();
      this.getSourceList();
    },
    methods: {
      initData() {
        this.typeClass = this.formInfo.source_type === 'API' ? 'bk-threeline-item bk-halfline-margin' : 'bk-halfline-item bk-halfline-margin';
        this.getApiSystemList();
        if (this.formInfo.source_type === 'API' && this.apiInfo.remote_system_id) {
          this.getApiPortList(this.apiInfo.remote_system_id);
        }
      },
      getSourceList() {
        // 根据不同类型来显示数据源类型列表
        const typeList = this.globalChoise.source_type.filter(item => item.typeName !== 'CUSTOM_API');
        if (this.formInfo.type === 'TABLE') {
          this.sourceList = typeList.filter(item => item.typeName === 'CUSTOM');
        } else if (this.formInfo.type === 'TREESELECT') {
          this.sourceList = typeList.filter(item => item.typeName === 'DATADICT' || item.typeName === 'RPC');
        } else {
          this.sourceList = typeList;
        }
      },
      // 获取Api系统列表
      getApiSystemList() {
        const params = {
          project_key: this.$store.state.project.id || 'public',
        };
        this.isSystemLoading = true;
        this.$store.dispatch('apiRemote/get_all_remote_system', params).then((res) => {
          this.apiSysList = res.data.filter(item => item.is_activated);
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isSystemLoading = false;
          });
      },
      getApiPortList(val) {
        const params = {
          remote_system: val || '',
        };
        this.isApiLoading = true;
        this.$store.dispatch('apiRemote/get_remote_api', params).then((res) => {
          this.apiPortList = res.data.filter(item => item.is_activated);
          const optionObject = this.apiPortList.filter(item => String(item.id) === String(this.apiInfo.remote_api_id))[0];
          const valueObject = Object.assign({}, optionObject);
          this.$emit('changeApiInfo', valueObject);
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isApiLoading = false;
          });
      },
      changeApiPort(val) {
        this.apiInfo.rsp_data = '';
        this.apiInfo.req_params = {};
        this.apiInfo.req_body = {};
        const optionObject = this.apiPortList.filter(item => String(item.id) === String(val))[0];
        const valueObject = Object.assign({}, optionObject);
        this.$emit('changeApiInfo', valueObject);
      },
      changeSource() {
        this.typeClass = this.formInfo.source_type === 'API' ? 'bk-threeline-item bk-halfline-margin' : 'bk-halfline-item bk-halfline-margin';
      },
      changeApiSystem(val) {
        this.apiInfo.remote_api_id = '';
        this.apiInfo.rsp_data = '';
        this.apiInfo.req_params = {};
        this.apiInfo.req_body = {};
        this.getApiPortList(val);
      },
      // rpc数据
      changeRpc(val) {
        const rpcObject = this.prcData.list.filter(item => item.key === val)[0].req_params;
        this.$emit('getRpcData', rpcObject);
      },
      // 校验
      checkSouce() {
        let checkStatus = false;
        if (this.formInfo.source_type === 'DATADICT') {
          checkStatus = !this.dictionaryData.check;
        } else if (this.formInfo.source_type === 'API') {
          checkStatus = !this.apiInfo.remote_system_id || !this.apiInfo.remote_api_id;
        } else if (this.formInfo.source_type === 'RPC') {
          checkStatus = !this.prcData.check;
        }
        if (checkStatus) {
          this.$bkMessage({
            theme: 'warning',
            message: this.$t('m.treeinfo["请选择正确的数据源"]'),
          });
        }
        return checkStatus;
      },
    },
  };
</script>

<style lang='scss' scoped>
    .bk-halfline-item {
        display: inline-block;
        width: 49%;
    }
    .bk-halfline-margin {
        margin-right: 1%;
    }
    .bk-threeline-item {
        display: inline-block;
        width: 32%;
    }
</style>
