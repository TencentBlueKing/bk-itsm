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
      :label-width="150"
      :model="addTableInfo.formInfo"
      form-type="vertical"
      :rules="rules"
      ref="addForm">
      <bk-form-item
        :label="$t(`m.systemConfig['名称']`)"
        :required="true"
        :property="'name'">
        <bk-input maxlength="120"
          type="text"
          :placeholder="$t(`m.systemConfig['请输入名称']`)"
          v-model.trim="addTableInfo.formInfo.name">
        </bk-input>
      </bk-form-item>
      <bk-form-item
        :label="$t(`m.systemConfig['描述']`)">
        <bk-input type="textarea"
          :rows="5"
          :maxlength="255"
          :placeholder="$t(`m.systemConfig['请输入描述']`)"
          v-model.trim="addTableInfo.formInfo.desc">
        </bk-input>
      </bk-form-item>
      <bk-form-item
        :label="$t(`m.basicModule['公共字段']`)">
        <bk-select v-model="addTableInfo.formInfo.fields"
          :placeholder="$t(`m.basicModule['请选择']`)"
          :clearable="false"
          multiple
          searchable
          :font-size="'medium'"
          @selected="typeSelected">
          <bk-option v-for="option in fieldsList"
            :key="option.id"
            :id="option.id"
            :name="option.name">
          </bk-option>
        </bk-select>
      </bk-form-item>
    </bk-form>
    <!-- 表格拖拽 -->
    <!-- <draggable element="tbody" v-model="moduleRelateFields" @end="updateInfo"></draggable> -->
    <div class="mt15 bk-draggable" v-bkloading="{ isLoading: isDataLoading }">
      <table class="bk-draggable-table">
        <thead>
          <tr>
            <th>No.</th>
            <th>{{ $t('m.treeinfo["字段名称"]') }}</th>
            <th style="max-width: 120px;">{{ $t('m.publicField["唯一标识"]') }}</th>
            <th style="max-width: 120px;">{{ $t('m.publicField["字段类型"]') }}</th>
          </tr>
        </thead>
        <draggable element="tbody" v-model="dataList" @end="updateInfo">
          <template v-if="dataList.length">
            <tr v-for="(item, index) in dataList" :key="index">
              <td class="move-handler-content">
                <span><i class="bk-itsm-icon icon-move-new move-handler"></i>{{index + 1}}</span>
              </td>
              <td>
                <span>{{ item.name }}</span>
              </td>
              <td style="max-width: 120px;">
                <span>{{ item.key }}</span>
              </td>
              <td style="max-width: 120px;">
                <span>{{ item.typeName }}</span>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-cloak>
              <td colspan="10" class="bk-none-content">
                <i class="bk-table-empty-icon bk-icon icon-empty"></i>
                <p class="bk-none-info">{{ $t('m.treeinfo["暂无数据"]') }}</p>
              </td>
            </tr>
          </template>
        </draggable>
      </table>
    </div>
    <!-- button -->
    <div class="mt15">
      <bk-button
        theme="primary"
        :title="$t(`m.systemConfig['保存']`)"
        class="mr10"
        @click="save">
        {{ $t(`m.systemConfig['保存']`) }}
      </bk-button>
      <bk-button
        theme="default"
        :title="$t(`m.systemConfig['取消']`)"
        @click="cancel">
        {{ $t('m.systemConfig["取消"]') }}
      </bk-button>
    </div>
  </div>
</template>

<script>
  import draggable from 'vuedraggable';
  import { errorHandler } from '../../../utils/errorHandler.js';
  import commonMix from '../../commonMix/common.js';

  export default {
    name: 'addBasicModule',
    components: {
      draggable,
    },
    mixins: [commonMix],
    props: {
      slideData: {
        type: Object,
        default() {
          return {};
        },
      },
      publicList: {
        type: Array,
        default() {
          return [];
        },
      },
    },
    data() {
      return {
        isDataLoading: false,
        addTableInfo: {
          openShow: false,
          formInfo: {
            id: '',
            name: '',
            desc: '',
            fields: [],
          },
        },
        dataList: [],
        fieldsList: [],
        rules: {},
      };
    },
    computed: {
      globalChoise() {
        return this.$store.state.common.configurInfo;
      },
    },
    mounted() {
      this.initData();
      this.rules = this.checkCommonRules('name');
    },
    methods: {
      initData() {
        this.publicList.forEach((item) => {
          this.globalChoise.field_type.forEach((node) => {
            if (item.type === node.typeName) {
              this.$set(item, 'typeName', node.name);
            }
          });
        });
        this.fieldsList = this.publicList.filter(item => (item.key !== 'title' && item.key !== 'current_status'));
        if (this.slideData.id) {
          this.addTableInfo.formInfo.id = this.slideData.id;
          this.addTableInfo.formInfo.name = this.slideData.name;
          this.addTableInfo.formInfo.desc = this.slideData.desc;
          this.addTableInfo.formInfo.fields = this.slideData.fields_order;
          // 初始化列表数据
          this.dataList = JSON.parse(JSON.stringify(this.slideData.fields));
          this.dataList.forEach((item) => {
            this.globalChoise.field_type.forEach((node) => {
              if (item.type === node.typeName) {
                this.$set(item, 'typeName', node.name);
              }
            });
          });
        } else {
          this.dataList = this.publicList.filter(item => (item.key === 'title' || item.key === 'current_status'));
          this.addTableInfo.formInfo.fields = this.dataList.map(item => item.id);
        }
      },
      // 创建/更新数据字典
      save() {
        this.$refs.addForm.validate().then(() => {
          const params = {
            desc: this.addTableInfo.formInfo.desc,
            fields: this.addTableInfo.formInfo.fields,
            fields_order: this.addTableInfo.formInfo.fields,
            id: this.addTableInfo.formInfo.id,
            name: this.addTableInfo.formInfo.name,
          };
          // create or update
          if (!this.addTableInfo.formInfo.id) {
            this.$store.dispatch('basicModule/add_tables', { params }).then(() => {
              this.$bkMessage({
                message: this.$t('m.systemConfig["添加成功"]'),
                theme: 'success',
              });
              this.cancel();
              this.$parent.$parent.getList();
            })
              .catch((res) => {
                errorHandler(res, this);
              });
          } else {
            this.$store.dispatch('basicModule/update_tables', {
              params,
              id: this.addTableInfo.formInfo.id,
            }).then(() => {
              this.$bkMessage({
                message: this.$t('m.systemConfig["更新成功"]'),
                theme: 'success',
              });
              this.cancel();
              this.$parent.$parent.getList();
            })
              .catch((res) => {
                errorHandler(res, this);
              });
          }
        }, () => {});
      },
      // 取消
      cancel() {
        this.$parent.$parent.closeShade();
      },
      typeSelected(...value) {
        this.addTableInfo.formInfo.fields = value[0];
        this.dataList = [];
        value[0].forEach((node) => {
          this.publicList.forEach((item) => {
            if (item.id === node) {
              this.dataList.push(item);
            }
          });
        });
      },
      // 拖动结束后的数据
      updateInfo() {
        this.addTableInfo.formInfo.fields = this.dataList.map(item => item.id);
      },
    },
  };
</script>

<style lang="scss" scoped>
    @import '../../../scss/mixins/table.scss';
    .bk-add-dictionary {
        margin: 0;
        padding: 20px;
    }
    .move-handler-content {
        cursor: move;
        .move-handler {
            margin-right: 5px;
            position: relative;
            top: 1px;
            opacity: 0;
        }
    }
    .bk-draggable {
        @include table;
    }
</style>
