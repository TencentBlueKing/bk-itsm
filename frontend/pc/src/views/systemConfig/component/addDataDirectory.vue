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
  <div class="bk-add-dictionary">
    <bk-form
      :label-width="200"
      form-type="vertical"
      :model="addTableInfo.formInfo"
      :rules="rules"
      ref="dynamicForm">
      <bk-form-item
        :label="$t(`m.systemConfig['编码']`)"
        :required="true"
        :property="'key'">
        <bk-input v-model.trim="addTableInfo.formInfo.key"
          :placeholder="$t(`m.systemConfig['请输入编码']`)"
          :disabled="addTableInfo.formInfo.id !== '' && addTableInfo.formInfo.id !== undefined">
        </bk-input>
      </bk-form-item>
      <bk-form-item :label="$t(`m.user['负责人：']`)">
        <member-select v-model="addTableInfo.formInfo.ownersInputValue"></member-select>
      </bk-form-item>
      <bk-form-item
        :label="$t(`m.systemConfig['名称']`)"
        :required="true"
        :property="'name'">
        <bk-input v-model.trim="addTableInfo.formInfo.name"
          maxlength="120"
          :placeholder="$t(`m.systemConfig['请输入名称']`)">
        </bk-input>
      </bk-form-item>
      <bk-form-item
        :label="$t(`m.systemConfig['描述']`)">
        <bk-input type="textarea"
          v-model.trim="addTableInfo.formInfo.desc"
          :placeholder="$t(`m.systemConfig['请输入描述']`)">
        </bk-input>
      </bk-form-item>
      <bk-form-item
        :label="$t(`m.systemConfig['启用状态']`)">
        <bk-switcher v-model="addTableInfo.formInfo.is_enabled" size="small"></bk-switcher>
      </bk-form-item>
    </bk-form>
    <!-- button -->
    <div class="bk-add-btn" v-if="addTableInfo.formInfo.id">
      <bk-button theme="default"
        :title="$t(`m.systemConfig['添加']`)"
        icon="plus"
        class="plus-cus"
        :disabled="!addTableInfo.formInfo.id"
        @click="addDictionary">
        {{ $t('m.systemConfig["添加"]') }}
      </bk-button>
    </div>
    <bk-table
      class="mb15"
      v-if="addTableInfo.formInfo.id"
      v-bkloading="{ isLoading: isDataLoading }"
      :data="dataList"
      :size="'small'"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handlePageLimitChange">
      <bk-table-column type="index" label="No." align="center" width="60"></bk-table-column>
      <bk-table-column :label="$t(`m.systemConfig['名字']`)" prop="name"></bk-table-column>
      <bk-table-column :label="$t(`m.systemConfig['父级']`)" prop="parent_name"></bk-table-column>
      <bk-table-column :label="$t(`m.systemConfig['编码']`)" prop="key"></bk-table-column>
      <bk-table-column :label="$t(`m.systemConfig['排序']`)" prop="order"></bk-table-column>
      <bk-table-column :label="$t(`m.systemConfig['操作']`)" width="120">
        <template slot-scope="props">
          <bk-button theme="primary" text @click="openDataDialog(props.row)">
            {{ $t('m.systemConfig["编辑"]') }}
          </bk-button>
          <bk-button v-if="!props.row.is_builtin"
            theme="primary"
            text
            @click="openDelete(props.row)">
            {{ $t('m.systemConfig["删除"]') }}
          </bk-button>
        </template>
      </bk-table-column>
    </bk-table>
    <!-- button -->
    <div>
      <bk-button :theme="'primary'" :title="$t(`m.systemConfig['保存']`)" class="mr10" @click="save">
        {{$t(`m.systemConfig['保存']`)}}
      </bk-button>
      <bk-button :theme="'default'" :title="$t(`m.systemConfig['取消']`)" class="mr10" @click="cancel">
        {{$t(`m.systemConfig['取消']`)}}
      </bk-button>
    </div>
    <!-- 新增字典字段 -->
    <bk-dialog
      v-model="dictDataTable.isShow"
      :render-directive="'if'"
      :width="dictDataTable.width"
      :header-position="dictDataTable.headerPosition"
      :loading="secondClick"
      :auto-close="dictDataTable.autoClose"
      :mask-close="dictDataTable.autoClose"
      @confirm="submitDictionary">
      <p slot="header">
        {{ dictDataTable.formInfo.id
          ? $t('m.systemConfig["编辑字典数据"]') : $t('m.systemConfig["新增字典数据"]') }}
      </p>
      <div class="bk-add-project bk-add-module">
        <bk-form
          :label-width="200"
          form-type="vertical"
          :model="dictDataTable.formInfo"
          :rules="rules"
          ref="dialogForm">
          <bk-form-item
            :label="$t(`m.systemConfig['父级：']`)">
            <select-tree
              v-model="dictDataTable.formInfo.parent"
              :list="dictDataTable.treeDataList"
              @change="onParentChange">
            </select-tree>
          </bk-form-item>
          <bk-form-item
            :label="$t(`m.systemConfig['编码：']`)"
            :required="true"
            :property="'key'">
            <bk-input v-model.trim="dictDataTable.formInfo.key"
              :placeholder="$t(`m.systemConfig['请输入编码，格式为英文数字及下划线']`)"
              :disabled="dictDataTable.formInfo.id !== '' && dictDataTable.formInfo.id !== undefined">
            </bk-input>
          </bk-form-item>
          <bk-form-item
            :label="$t(`m.systemConfig['名称：']`)"
            :required="true"
            :property="'name'">
            <bk-input v-model.trim="dictDataTable.formInfo.name"
              :placeholder="$t(`m.systemConfig['请输入中文名称']`)">
            </bk-input>
          </bk-form-item>
          <bk-form-item
            :label="$t(`m.systemConfig['排序：']`)"
            :required="true">
            <bk-input :clearable="true"
              type="number"
              :min="0"
              :precision="dictDataTable.precision"
              v-model="dictDataTable.formInfo.order">
            </bk-input>
          </bk-form-item>
        </bk-form>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
  import memberSelect from '../../commonComponent/memberSelect';
  import SelectTree from '../../../components/form/selectTree/index.vue';
  import { errorHandler } from '../../../utils/errorHandler';

  export default {
    name: 'addData',
    components: {
      SelectTree,
      memberSelect,
    },
    props: {
      slideData: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        // 列表数据
        isDataLoading: false,
        secondClick: false,
        dataList: [],
        pagination: {
          current: 1,
          count: 10,
          limit: 10,
        },
        // 新增
        dictDataTable: {
          parentList: [],
          isShow: false,
          width: 700,
          headerPosition: 'left',
          autoClose: false,
          precision: 0,
          list: [],
          formInfo: {
            id: '',
            dict_table: '',
            key: '',
            name: '',
            parent: '',
            parentObj: '',
            is_readonly: false,
            order: 1,
          },
          // 树元素
          treeOpen: false,
          treeDataList: [],
        },
        // 是否启用
        addTableInfo: {
          formInfo: {
            id: '',
            key: '',
            name: '',
            desc: '',
            ownersInputValue: [],
            is_enabled: false,
          },
        },
        // 校验规则
        rules: {
          key: [
            {
              required: true,
              message: this.$t('m.systemConfig["编码格式为英文数字及下划线"]'),
              trigger: 'blur',
            },
            {
              regex: /^[a-zA-Z0-9_]+$/,
              message: this.$t('m.systemConfig["格式为长度小于120"]'),
              trigger: 'blur',
            },
          ],
          name: [
            {
              required: true,
              message: this.$t('m.systemConfig["格式为长度小于120"]'),
              trigger: 'blur',
            },
            {
              max: 120,
              message: this.$t('m.systemConfig["格式为长度小于120"]'),
              trigger: 'blur',
            },
          ],
        },
      };
    },
    watch: {
      'slideData.id'() {
        if (this.slideData.id) {
          this.initData();
        }
      },
    },
    mounted() {
      if (this.slideData.id) {
        this.initData();
      }
    },
    methods: {
      initData() {
        this.addTableInfo.formInfo.id = this.slideData.id;
        this.addTableInfo.formInfo.ownersInputValue = this.slideData.ownersInputValue;
        this.addTableInfo.formInfo.key = this.slideData.key;
        this.addTableInfo.formInfo.name = this.slideData.name;
        this.addTableInfo.formInfo.desc = this.slideData.desc;
        this.addTableInfo.formInfo.is_enabled = this.slideData.is_enabled;
        this.getList();
      },
      getList(page) {
        // 查询时复位页码
        if (page !== undefined) {
          this.pagination.current = page;
        }
        const params = {
          dict_table: this.slideData.id,
          page: this.pagination.current,
          page_size: this.pagination.limit,
        };

        this.isDataLoading = true;
        this.$store.dispatch('dictdata/list', params).then((res) => {
          this.dataList = res.data.items;
          // 分页
          this.pagination.current = res.data.page;
          this.pagination.count = res.data.count;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
      },
      // 分页过滤数据
      handlePageLimitChange() {
        this.pagination.limit = arguments[0];
        this.getList();
      },
      handlePageChange(page) {
        this.pagination.current = page;
        this.getList();
      },
      // 创建/更新数据字典
      save() {
        this.$refs.dynamicForm.validate().then(() => {
          // create or update
          const params = {
            ...this.addTableInfo.formInfo,
            owners: this.addTableInfo.formInfo.ownersInputValue.join(','),
          };
          delete params.ownersInputValue;
          if (!this.addTableInfo.formInfo.id) {
            this.$store.dispatch('datadict/create', params).then((res) => {
              this.$bkMessage({
                message: this.$t('m.systemConfig["添加成功"]'),
                theme: 'success',
              });
              this.$emit('getList', 1);
              this.$emit('openAddData', res.data);
            })
              .catch((res) => {
                errorHandler(res, this);
              });
          } else {
            this.$store.dispatch('datadict/update', params).then(() => {
              this.$bkMessage({
                message: this.$t('m.systemConfig["更新成功"]'),
                theme: 'success',
              });
              this.$emit('getList', 1);
              this.$emit('closeAddData');
            })
              .catch((res) => {
                errorHandler(res, this);
              });
          }
        });
      },
      // 取消
      cancel() {
        this.$emit('closeAddData');
      },
      // 新增字典字段
      addDictionary() {
        this.dictDataTable.formInfo = {
          id: '',
          dict_table: '',
          key: '',
          name: '',
          parent: '',
          order: 1,
          parentObj: {},
        };
        this.dictDataTable.isShow = true;
        this.getTreeInfo();
      },
      closeDictionary() {
        this.dictDataTable.isShow = false;
      },
      // 编辑字典
      async openDataDialog(item) {
        this.dictDataTable.formInfo = JSON.parse(JSON.stringify(item)) || {};
        this.dictDataTable.formInfo.parentObj = {};
        await this.getTreeInfo();
        this.dictDataTable.isShow = true;
      },
      // 删除
      openDelete(item) {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.systemConfig["确认删除该条数据？"]'),
          confirmFn: () => {
            const { id } = item;
            if (this.secondClick) {
              return;
            }
            this.secondClick = true;
            this.$store.dispatch('dictdata/delete', id).then(() => {
              this.$bkMessage({
                message: this.$t('m.systemConfig["删除成功"]'),
                theme: 'success',
              });
              if (this.dataList.length === 1) {
                this.pagination.current = this.pagination.current === 1
                  ? 1 : this.pagination.current - 1;
              }
              this.getList();
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.secondClick = false;
              });
          },
        });
      },
      submitDictionary() {
        this.$refs.dialogForm.validate().then(() => {
          // create or update
          if (!this.dictDataTable.formInfo.id) {
            this.dictDataTable.formInfo.dict_table = this.slideData.id;
            if (this.secondClick) {
              return;
            }
            this.secondClick = true;
            this.$store.dispatch('dictdata/create', this.dictDataTable.formInfo).then(() => {
              this.$bkMessage({
                message: this.$t('m.systemConfig["添加成功"]'),
                theme: 'success',
              });
              this.closeDictionary();
              this.getList(1);
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.secondClick = false;
              });
          } else {
            if (this.dictDataTable.formInfo.id === this.dictDataTable.formInfo.parent) {
              this.$bkMessage({
                message: this.$t('m.systemConfig["父级目录不能是自己！"]'),
                theme: 'warning',
              });
              return;
            }
            if (this.secondClick) {
              return;
            }
            this.secondClick = true;
            this.$store.dispatch('dictdata/update', this.dictDataTable.formInfo).then(() => {
              this.$bkMessage({
                message: this.$t('m.systemConfig["更新成功"]'),
                theme: 'success',
              });
              this.getList(1);
              this.closeDictionary();
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.secondClick = false;
              });
          }
        });
      },
      // tree操作
      async getTreeInfo() {
        if (!this.addTableInfo.formInfo.key) {
          return;
        }
        const params = {
          key: this.addTableInfo.formInfo.key,
          view_type: 'tree',
        };
        await this.$store.dispatch('dictdata/getTreeInfo', params).then((res) => {
          this.dictDataTable.treeDataList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      onParentChange(tree) {
        this.dictDataTable.formInfo.parentObj = tree;
      },
    },
  };
</script>

<style lang="scss" scoped>
    .bk-add-btn {
        margin-bottom: 15px;
    }
</style>
