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
  <div class="bk-task-library">
    <bk-form :label-width="200"
      ref="addLibrary"
      form-type="vertical">
      <bk-form-item :label="$t(`m.task['任务库']`)"
        :required="true">
        <div style="width: 50%; padding-right: 10px;">
          <bk-select v-model="formData.key"
            searchable
            @selected="selectLibrary">
            <bk-option class="custom-option"
              v-for="option in libraryList"
              :key="option.id"
              :id="option.id"
              :name="option.name">
              <span>{{option.name}}</span>
              <i class="bk-icon icon-close"
                style="font-size: 18px;"
                @click.stop="handleDeleteOption(option)">
              </i>
            </bk-option>
          </bk-select>
        </div>
      </bk-form-item>
    </bk-form>
    <p class="bk-library-message">
      <i class="bk-icon icon-info-circle"></i><span>{{$t(`m.task['标准运维任务，创建成功不支持修改，请修改后再提交']`)}}</span>
    </p>
    <div v-if="formData.key">
      <bk-table v-bkloading="{ isLoading: tabLoading }"
        :data="tableList"
        :size="'small'">
        <bk-table-column :label="$t(`m.task['顺序']`)" :min-width="minWidth">
          <template slot-scope="props">
            <template v-if="props.row.orderStatus">
              <span class="bk-task-order" @click="changeOrderStatus(props.row)">{{props.row.order}}</span>
            </template>
            <template v-else>
              <bk-input style="display: inline-block; width: 60px;"
                type="number"
                :min="0"
                :precision="precision"
                v-model="props.row.orderInfo">
              </bk-input>
              <p style="display: inline-block; font-size: 12px;">
                <span style="margin-right: 5px; margin-left: 5px; cursor: pointer; color: #3a84ff;"
                  @click="submitOrder(props.row)">确认</span>
                <span style="cursor: pointer; color: #3a84ff;"
                  @click="closeOrder(props.row)">取消</span>
              </p>
            </template>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.task['任务名称']`)">
          <template slot-scope="props">
            <span :title="props.row.name">{{props.row.name || '--'}}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.task['处理人']`)">
          <template slot-scope="props">
            <span :title="props.row.processor_users">{{props.row.processor_users || '--'}}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.task['任务类型']`)">
          <template slot-scope="props">
            <span>
              {{props.row.component_type === 'NORMAL' ? $t(`m.task['普通任务']`) : $t(`m.task['标准运维任务']`)}}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.task['操作']`)" min-width="120">
          <template slot-scope="props">
            <bk-button theme="primary"
              text
              @click="editorLibrary(props.row)">
              {{$t(`m.task['编辑']`)}}
            </bk-button>
            <bk-button theme="primary"
              text
              @click="deleteLibrary(props.row)">
              {{ $t('m.user["删除"]') }}
            </bk-button>
          </template>
        </bk-table-column>
      </bk-table>
    </div>
    <div class="bk-library-btn mt20">
      <bk-button
        :theme="'primary'"
        :title="$t(`m.task['确认']`)"
        :disabled="!formData.key || !tableList.length || btnLoading"
        class="mr10"
        @click="submitLibrary">
        {{$t(`m.task['确认']`)}}
      </bk-button>
      <bk-button :theme="'default'"
        :disabled="!formData.key || !tableList.length || btnLoading"
        :title="$t(`m.task['更新任务库']`)"
        class="mr10"
        @click="updataLibrary">
        {{$t(`m.task['更新任务库']`)}}
      </bk-button>
      <bk-button :theme="'default'"
        :disabled="btnLoading"
        :title="$t(`m.task['取消']`)"
        @click="closeTaskLibrary">
        {{$t(`m.task['取消']`)}}
      </bk-button>
    </div>
    <!-- 编辑列表数据弹窗 -->
    <bk-sideslider
      :is-show.sync="tableContent.show"
      :title="tableContent.title"
      :width="tableContent.width">
      <div class="bk-task-library" slot="content" v-if="tableContent.show">
        <bk-form :ext-cls="'mb10'"
          :label-width="200"
          form-type="vertical">
          <!-- 处理人 -->
          <bk-form-item :label="$t(`m.task['处理人']`)"
            :required="true">
            <deal-person
              ref="personSelect"
              class="deal-person"
              :shortcut="true"
              :value="tableContent.formInfo"
              :exclude-role-type-list="excludeTypeList">
            </deal-person>
          </bk-form-item>
        </bk-form>
        <field-info ref="fieldInfo"
          :fields="tableContent.content.fields"
          :basic-infomation="basicInfomation">
        </field-info>
        <div class="mt20">
          <bk-button :theme="'primary'"
            :title="$t(`m.task['确认']`)"
            :disabled="btnLoading"
            class="mr10"
            @click="submitTableContent">
            {{$t(`m.task['确认']`)}}
          </bk-button>
          <bk-button :theme="'default'"
            :disabled="btnLoading"
            :title="$t(`m.task['取消']`)"
            @click.stop="tableContent.show = false">
            {{$t(`m.task['取消']`)}}
          </bk-button>
        </div>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import fieldInfo from '../../managePage/billCom/fieldInfo.vue';
  import DealPerson from '../../processManagement/processDesign/nodeConfigue/components/dealPerson';
  import commonMix from '../../commonMix/common.js';
  import apiFieldsWatch from '../../commonMix/api_fields_watch.js';
  import { errorHandler } from '@/utils/errorHandler';

  export default {
    name: 'taskLibrary',
    components: {
      fieldInfo,
      DealPerson,
    },
    mixins: [apiFieldsWatch, commonMix],
    props: {
      basicInfomation: {
        type: Object,
        default() {
          return {};
        },
      },
      ticketId: {
        type: Number,
        default() {
          return '';
        },
      },
    },
    data() {
      return {
        btnLoading: false,
        excludeTypeList: [
          'OPEN',
          'STARTER',
          'BY_ASSIGNOR',
          'EMPTY',
          'VARIABLE',
          'CMDB',
          'ORGANIZATION',
          'IAM',
          'STARTER_LEADER',
          'API'],
        formData: {
          key: '',
        },
        libraryList: [],
        // table数据
        tableList: [],
        tabLoading: false,
        tableContent: {
          show: false,
          title: this.$t('m.task[\'修改任务信息\']'),
          width: 660,
          content: {},
          formInfo: {
            value: '',
            type: '',
          },
        },
        // 输入框
        precision: 0,
        minWidth: 60,
      };
    },
    created() {
      this.getLibraryList();
    },
    methods: {
      getLibraryList() {
        this.$store.dispatch('taskFlow/getLibraryList').then((res) => {
          this.libraryList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {

          });
      },
      // 删除某个任务库
      handleDeleteOption(option) {
        const { id } = option;
        this.$store.dispatch('taskFlow/deleteLibrary', id).then(() => {
          this.libraryList = this.libraryList.filter(item => item.id !== option.id);
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {

          });
      },
      selectLibrary() {
        // 根据任务库获取列表数据
        this.tabLoading = true;
        const id = this.formData.key;
        const params = {
          ticket_id: this.ticketId,
        };
        this.$store.dispatch('taskFlow/getLibraryInfo', { params, id }).then((res) => {
          this.tableList = res.data;
          this.tableList.forEach((item) => {
            this.$set(item, 'orderStatus', true);
            this.$set(item, 'orderInfo', item.order);
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.tabLoading = false;
          });
      },
      // 改变处理顺序
      changeOrderStatus(value) {
        this.tableList.forEach((item) => {
          item.orderStatus = true;
        });
        value.orderStatus = false;
        this.minWidth = 160;
      },
      submitOrder(value) {
        value.order = Number(value.orderInfo);
        value.orderStatus = true;
        this.minWidth = 60;
      },
      closeOrder(value) {
        const orderValue = this.tableList.filter(item => item.id === value.id)[0].order;
        value.orderInfo = Number(orderValue);
        value.orderStatus = true;
        this.minWidth = 60;
      },
      // 删除数据
      deleteLibrary(item) {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.task[\'确认删除数据？\']'),
          subTitle: this.$t('m.task[\'数据如果被删除，此数据在当前任务库中不可用。\']'),
          confirmFn: () => {
            this.tableList = this.tableList.filter(node => node.id !== item.id);
          },
        });
      },
      closeTaskLibrary() {
        this.$emit('closeTaskLibrary');
      },
      // 编辑任务弹窗
      editorLibrary(item) {
        this.tableContent.show = true;
        this.tableContent.content = JSON.parse(JSON.stringify(item));
        // fields数据
        this.tableContent.content.fields = this.tableContent.content.fields.filter(item => item.type !== 'COMPLEX-MEMBERS');
        this.tableContent.content.fields.forEach((item) => {
          if (item.type === 'CASCADE') {
            item.type = 'SELECT';
          }
          this.$set(item, 'showFeild', true);
          this.$set(item, 'val', item.value || '');
        });
        this.isNecessaryToWatch({ fields: this.tableContent.content.fields }, 'submit');
        // 处理人数据
        this.tableContent.formInfo.value = item.processors;
        this.tableContent.formInfo.type = item.processors_type;
      },
      submitTableContent() {
        // 处理人信息
        if (this.$refs.personSelect) {
          const data = this.$refs.personSelect.getValue();
          this.tableContent.formInfo.type = data.type;
          this.tableContent.formInfo.value = data.value;
        }

        // 字段信息(将字段信息value值进行转换)
        this.fieldFormatting(this.tableContent.content.fields);
        // 将修改好的信息存入列表数据
        this.tableList.forEach((item) => {
          if (item.id === this.tableContent.content.id) {
            item.fields = this.tableContent.content.fields;
            item.processors = this.tableContent.formInfo.value;
            item.processors_type = this.tableContent.formInfo.type;
            item.name = this.tableContent.content.fields.filter(node => node.key === 'task_name')[0].value;
          }
        });
        this.tableContent.show = false;
      },
      // 更新任务库
      updataLibrary() {
        this.btnLoading = true;
        const id = this.formData.key;
        const params = {
          name: this.libraryList.filter(item => item.id === this.formData.key)[0].name,
          tasks: this.tableList,
        };
        this.$store.dispatch('taskFlow/updataLibrary', { params, id }).then(() => {
          this.$bkMessage({
            message: this.$t('m.task[\'更新成功\']'),
            theme: 'success',
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.btnLoading = false;
          });
      },
      // 创建任务库
      submitLibrary() {
        const params = {
          batch_create: 1,
          ticket_id: this.ticketId,
          tasks: [],
        };
        this.tableList.forEach((node) => {
          const valueInfo = {
            processors: node.processors,
            processors_type: node.processors_type,
            task_schema_id: node.task_schema_id,
            order: node.order,
            fields: {},
          };
          node.fields.forEach((item) => {
            valueInfo.fields[item.key] = item.value;
          });
          params.tasks.push(valueInfo);
        });
        this.btnLoading = true;
        this.$store.dispatch('taskFlow/createTask', params).then(() => {
          this.$bkMessage({
            message: this.$t('m.task[\'创建任务成功\']'),
            theme: 'success',
          });
          this.$emit('closeTaskLibrary');
          // 刷新数据
          this.$emit('getTaskList');
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.btnLoading = false;
          });
      },
    },
  };
</script>

<style scoped lang='scss'>
    .bk-task-library {
        padding: 16px 20px 70px 20px;
    }
    .custom-option .icon-close {
        display: none;
        position: absolute;
        right: 0;
        top: 3px;
        font-size: 12px;
        width: 26px;
        height: 26px;
        line-height: 26px;
        text-align: center;
    }
    .custom-option:hover .icon-close {
        display: block;
    }
    .bk-library-message {
        margin-top: 20px;
        margin-bottom: 10px;
        line-height: 20px;
        color: #63656E;
        font-size: 12px;
        .bk-icon {
            color: #979BA5;
            margin-right: 8px;
        }
    }
    .bk-task-order {
        line-height: 26px;
        display: inline-block;
        width: 50px;
        padding-left: 5px;
        &:hover {
            background-color: #DCDEE5;
            cursor: pointer;
        }
    }
    .deal-person {
        /deep/ .bk-form-width {
            width: 300px;
        }
    }
</style>
