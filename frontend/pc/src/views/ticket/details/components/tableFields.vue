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
  <div class="bk-table-fields">
    <template v-if="openFunction.FIRST_STATE_SWITCH">
      <span class="bk-field-tip">{{ $t(`m['单据内容：']`)}}</span>
      <bk-form :label-width="200" form-type="vertical" :ext-cls="'bk-ext-form'">
        <template v-for="(item, index) in firstStateFields">
          <div v-if="item.showFeild"
            :key="index"
            class="bk-field-line">
            <fields-done
              :item="item"
              :basic-info-type="basicInfoType"
              :fields="firstStateFields"
              :basic-infomation="basicInfomation">
            </fields-done>
          </div>
        </template>
      </bk-form>
    </template>
    <!-- <div class="split-line" v-if="openFunction.TABLE_FIELDS_SWITCH && openFunction.FIRST_STATE_SWITCH"></div> -->
    <template v-if="openFunction.TABLE_FIELDS_SWITCH">
      <span class="bk-field-tip">{{ $t(`m['基础字段信息：']`)}}</span>
      <bk-form :label-width="200" form-type="vertical" :ext-cls="'bk-ext-form'">
        <div v-for="(item, index) in tableFields"
          :key="index"
          class="bk-field-line">
          <!-- 静态展示 -->
          <template v-if="!item.isEdit">
            <fields-done
              :item="item"
              :basic-info-type="basicInfoType"
              :fields="basicInfomation.table_fields"
              :basic-infomation="basicInfomation">
            </fields-done>
          </template>
          <!-- 编辑状态 -->
          <template v-else>
            <fields-running
              :item="item"
              :fields="basicInfomation.table_fields"
              :basic-infomation="basicInfomation">
            </fields-running>
          </template>
        </div>
      </bk-form>
    </template>
  </div>
</template>
<script>
  import fieldsDone from './fieldsDone.vue';
  import fieldsRunning from './fieldsRunning.vue';
  import apiFieldsWatch from '@/views/commonMix/api_fields_watch.js';
  export default {
    name: 'tableFields',
    components: {
      fieldsDone,
      fieldsRunning,
    },
    mixins: [apiFieldsWatch],
    props: {
      basicInfomation: {
        type: Object,
        default() {
          return {
            table_fields: [],
          };
        },
      },
      firstStateFields: {
        type: Array,
        default() {
          return [];
        },
      },
    },
    data() {
      return {
        showMore: false,
        showInfo: true,
        fieldList: [],
        basicInfoType: ['STRING', 'TEXT', 'SELECT', 'INT', 'DATE', 'MULTISELECT', 'MEMBER'],
      };
    },
    computed: {
      profile() {
        if (!this.basicInfomation) {
          return;
        }
        return {
          name: this.basicInfomation.profile.name,
          phone: this.basicInfomation.profile.phone,
          department: this.basicInfomation.profile.departments ? this.basicInfomation.profile.departments : [],
        };
      },
      openFunction() {
        return this.$store.state.openFunction;
      },
      tableFields() {
        const list = [];
        const fields = this.basicInfomation.table_fields;
        fields.forEach((ite) => {
          if (!this.basicInfoType.includes(ite.type)) {
            list.push(ite);
          } else {
            list.unshift(ite);
          }
        });
        return list;
      },
    },
    watch: {
      'basicInfomation.table_fields'() {
        this.initData();
      },
    },
    mouted() {
      this.initData();
    },
    methods: {
      initData() {
        this.basicInfomation.table_fields.forEach((item) => {
          this.$set(item, 'isEdit', false);
          this.$set(item, 'service', this.basicInfomation.service_type);
          this.$set(item, 'val', (item.value || ''));
          this.$set(item, 'showFeild', true);
          if (item.key === 'current_status') {
            this.$set(item, 'ticket_status', this.basicInfomation.current_status);
          }
        });
        this.isNecessaryToWatch({ fields: this.basicInfomation.table_fields });
        this.basicInfomation.table_fields.forEach((item) => {
          if ((item.type === 'TABLE' || item.type === 'CUSTOMTABLE') && !item.value) {
            item.value = [];
          }
        });
      },
      // 处理人栏显示处理
      processtrans(item) {
        switch (item.current_status) {
          case 'DISTRIBUTING':
            return item.current_assignors;
          case 'DISTRIBUTING-RECEIVING':
            return (Array.from(new Set([...item.current_processors.split(','), ...item.current_assignors.split(',')])).join()
              .replace(/(^,*)|(,$)/g, ''));
          default :
            return item.current_processors || '--';
        }
      },
      changeShow() {
        this.showMore = !this.showMore;
      },
    },
  };
</script>
<style lang='scss' scoped>
    @import '../../../../scss/mixins/clearfix.scss';
    @import '../../../../scss/mixins/scroller.scss';
    .bk-field-tip {
        color: #c4c6cc;
        margin-left: 27px;
    }
    .bk-field-line {
        width: 50%;
        position: relative;
        padding: 4px;
        font-size: 14px;
        display: inline-block;
    }
    .bk-field-half {
        width: 50%;
        position: relative;
        padding-right: 10px;
        display: inline-block;
    }
    .split-line{
        margin: 10px 0;
        display: block;
        width: 100%;
        padding: 0 20px;
        border-bottom: 1px solid #dde4eb;
    }
    .bk-table-fields {
        padding-top: 7px;
        font-size: 12px;
        color: #737987;
        height: auto;
        width: 100%;
        position: relative;
        .bk-table-fields-item {
            min-height: 36px;
            box-sizing: border-box;
            display: flex;
            align-items: center;
            width: 100%;
        }
    }
</style>
