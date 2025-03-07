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
  <div v-if="item.showFeild">
    <bk-form-item :label="item.name" :required="item.validate_type === 'REQUIRE'"
      :desc="{ content: item.tips, allowHTML: false }" desc-type="icon">
      <bk-table
        :data="item.val"
        :size="'small'">
        <template v-for="columnItem in item.meta.columns">
          <bk-table-column :label="columnItem.name" :key="columnItem.key">
            <template slot-scope="props">
              <template v-if="columnItem.display === 'input'">
                <bk-input
                  :clearable="true"
                  :font-size="'normal'"
                  behavior="simplicity"
                  size="small"
                  v-model="props.row[columnItem.key]"
                  :disabled="disabled"></bk-input>
              </template>
              <template v-if="columnItem.display === 'select'">
                <bk-select
                  searchable
                  v-model="props.row[columnItem.key]"
                  :font-size="'normal'"
                  :popover-min-width="180"
                  behavior="simplicity"
                  size="small"
                  :disabled="disabled"
                  @change="handleSelectChange(props.$index, columnItem.key, props.row[columnItem.key])">
                  <bk-option v-for="option in (props.row[`${columnItem.key}_choice`] || columnItem.choice)"
                    :key="option.key"
                    :id="option.key"
                    :name="option.name">
                  </bk-option>
                </bk-select>
              </template>
              <template v-if="columnItem.display === 'multiselect'">
                <bk-select searchable
                  multiple
                  :popover-min-width="180"
                  :font-size="'normal'"
                  behavior="simplicity"
                  size="small"
                  :disabled="disabled"
                  show-select-all
                  v-model="props.row[columnItem.key]">
                  <bk-option v-for="option in (props.row[`${columnItem.key}_choice`] || columnItem.choice)"
                    :key="option.key"
                    :id="option.key"
                    :name="option.name">
                  </bk-option>
                </bk-select>
              </template>
              <template v-if="columnItem.display === 'date'">
                <bk-date-picker v-model="props.row[columnItem.key]"
                  :transfer="true"
                  :disabled="disabled">
                </bk-date-picker>
              </template>
              <template v-if="columnItem.display === 'datetime'">
                <bk-date-picker v-model="props.row[columnItem.key]"
                  :transfer="true"
                  :disabled="disabled"
                  :type="'datetime'">
                </bk-date-picker>
              </template>
            </template>
          </bk-table-column>
        </template>
        <bk-table-column :label="$t(`m.user['操作']`)" width="150">
          <template slot-scope="props">
            <bk-button theme="primary" text @click="addOne" :disabled="disabled">
              {{ $t('m.newCommon["添加"]') }}
            </bk-button>
            <bk-button theme="primary" text @click="cloneOne(props.$index)" :disabled="disabled">
              克隆
            </bk-button>
            <bk-button theme="primary" text @click="deleteOne(props)" :disabled="disabled">
              {{ $t('m.newCommon["删除"]') }}
            </bk-button>
          </template>
        </bk-table-column>
      </bk-table>
    </bk-form-item>
    <template v-if="item.checkValue">
      <p class="bk-task-error" v-if="item.checkMessage">{{ item.checkMessage }}</p>
      <p class="bk-task-error" v-else>{{ item.name }}{{ $t('m.newCommon["为必填项！"]') }}</p>
    </template>
  </div>
</template>

<script>
  import { errorHandler } from '../../../utils/errorHandler';

  export default {
    name: 'CUSTOMTABLE',
    props: {
      item: {
        type: Object,
        required: true,
        default: () => {
        },
      },
      isCurrent: {
        type: Boolean,
        default: false,
      },
      disabled: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        multiSelect: true,
        watchers: {},  // 用于跟踪已经绑定的监听器
      };
    },
    watch: {
      'item.val': {
        // handler(newVal) {
        handler() {
          // console.log(newVal);
          if (typeof this.$parent.refresh === 'function') {
            this.$parent.refresh();
          }
          // 重新设置级联监听器
          this.setupCascadeWatchers();
        },
        deep: true,
      },
    },
    created() {
      if (this.item.val === '' || (Array.isArray(this.item.val) && !this.item.val.length)) {
        this.item.val = [];
        const obj = {};
        for (let i = 0; i < this.item.meta.columns.length; i++) {
          const { key } = this.item.meta.columns[i];
          obj[key] = '';
        }
        this.item.val.push(obj);
      }

      // 脏数据处理
      this.item.val.forEach((row) => {
        this.item.meta.columns.forEach((column) => {
          if ((column.display === 'multiselect' || column.display === 'select')) {
            const vals = typeof row[column.key] === 'string' ? [row[column.key]] : row[column.key];
            if (!vals.every(key => column.choice.find(c => c.key === key))) {
              const option = column.choice.find(c => c.name === row[column.key]);
              row[column.key] = option ? option.key : '';
            }
          }
        });
      });

      // 拉取 select 数据
      this.fetchSelectData();

      // 设置每一行的级联监听器
      // this.setupCascadeWatchers();
    },
    methods: {
      handleSelectChange(rowIndex, columnKey, newValue) {
        console.log('handleSelectChange enter:', rowIndex, columnKey, newValue);
        const columns = this.item.meta.columns;
        const column = columns.find(column => column.key === columnKey);
        if (column && column.api) {
          const apiObj = JSON.parse(column.api);
          if (apiObj.cascade) {
            const watcherKey = `${rowIndex}-${column.key}`;
            if (!this.watchers[watcherKey]) {
              this.watchers[watcherKey] = this.$watch(`item.val.${rowIndex}.${column.key}`, (newValue) => {
                const cascadeColumn = this.item.meta.columns.find(c => c.key === apiObj.cascade);
                const rowData = this.item.val[rowIndex];
                if (cascadeColumn && cascadeColumn.api && rowData) {
                  console.log('handleSelectChange cascade', rowIndex, column.key, newValue, rowData, cascadeColumn.api);
                  const reqParams = {
                    ...rowData,
                    api: JSON.parse(cascadeColumn.api),
                  };
                  this.$store.dispatch('apiRemote/get_table_select_data', reqParams).then((res) => {
                    this.$set(this.item.val[rowIndex], `${cascadeColumn.key}_choice`, res.data);
                    // 重置级联下拉框的当前值
                    this.$set(this.item.val[rowIndex], cascadeColumn.key, cascadeColumn.display === 'multiselect' ? [] : '');
                  })
                    .catch((res) => {
                      errorHandler(res, this);
                    });
                }
              });
            }
          }
        }
      },

      fetchSelectData() {
        this.item.meta.columns.forEach((column) => {
          if (column.api) {
            const reqParams = {
              api: JSON.parse(column.api),
            };
            this.$store.dispatch('apiRemote/get_table_select_data', reqParams).then((res) => {
              column.choice = res.data;
            })
              .catch((res) => {
                errorHandler(res, this);
              });
          }
        });
      },
      addOne() {
        const obj = {};
        for (let i = 0; i < this.item.meta.columns.length; i++) {
          const { key } = this.item.meta.columns[i];
          obj[key] = '';
        }
        this.item.val.push(obj);
        // 为新添加的行设置级联监听器
        // this.setupCascadeWatcherForRow(this.item.val.length - 1);
      },
      cloneOne(index) {
        const obj = { ...this.item.val[index] };
        this.item.val.splice(index + 1, 0, obj);
        // 为新克隆的行设置级联监听器
        this.setupCascadeWatcherForRow(index + 1);
      },
      deleteOne(index) {
        if (this.item.val.length === 1) {
          this.$bkMessage({
            message: '默认行不能删除',
            theme: 'warning',
          });
        } else {
          this.$bkInfo({
            title: '确认要删除此条数据？',
            confirmFn: () => {
              // this.item.val.splice(index.$index, 1);
              // 移除该行上所有已绑定的监听器
              const rowIndex = index.$index;
              this.item.meta.columns.forEach((column) => {
                if (column.api) {
                  const apiObj = JSON.parse(column.api);
                  if (apiObj.cascade) {
                    const watcherKey = `${rowIndex}-${column.key}`;
                    if (this.watchers[watcherKey]) {
                      this.watchers[watcherKey]();
                      delete this.watchers[watcherKey];
                    }
                  }
                }
              });
              // 移除行
              this.item.val.splice(rowIndex, 1);
            },
          });
        }
      },
      // fix: 第一次无法没有触发级联
      setupCascadeWatchers() {
        this.item.val.forEach((_, rowIndex) => {
          this.setupCascadeWatcherForRow(rowIndex);
        });
      },

      setupCascadeWatcherForRow(rowIndex) {
        console.log('setupCascadeWatcherForRow enter:', rowIndex);
        this.item.meta.columns.forEach((column) => {
          if (column.api) {
            const apiObj = JSON.parse(column.api);
            if (apiObj.cascade) {
              const watcherKey = `${rowIndex}-${column.key}`;
              if (!this.watchers[watcherKey]) {
                this.watchers[watcherKey] = this.$watch(`item.val.${rowIndex}.${column.key}`, (newValue) => {
                  const cascadeColumn = this.item.meta.columns.find(c => c.key === apiObj.cascade);
                  const rowData = this.item.val[rowIndex];
                  console.log('setupCascadeWatcherForRow cascade watch:', rowIndex, column.key, newValue, rowData, cascadeColumn);
                  if (cascadeColumn && cascadeColumn.api && rowData) {
                    const reqParams = {
                      ...rowData,
                      api: JSON.parse(cascadeColumn.api),
                    };
                    this.$store.dispatch('apiRemote/get_table_select_data', reqParams).then((res) => {
                      this.$set(this.item.val[rowIndex], `${cascadeColumn.key}_choice`, res.data);
                      // 重置级联下拉框的当前值
                      this.$set(this.item.val[rowIndex], cascadeColumn.key, cascadeColumn.display === 'multiselect' ? [] : '');
                    })
                      .catch((res) => {
                        errorHandler(res, this);
                      });
                  }
                });
              }
            }
          }
        });
      },
    },
  };
</script>
