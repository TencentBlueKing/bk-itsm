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
    <bk-form-item :label="item.name" :required="item.validate_type === 'REQUIRE'" :desc="item.tips" desc-type="icon">
      <bk-table
        :data="item.val"
        :size="'small'">
        <template v-for="columnItem in item.meta.columns">
          <bk-table-column :label="columnItem.name" :key="columnItem.key">
            <template slot-scope="props">
              <template v-if="columnItem.display === 'input'">
                <bk-input
                  :clearable="true"
                  v-model="props.row[columnItem.key]"
                  :disabled="disabled"></bk-input>
              </template>
              <template v-if="columnItem.display === 'select'">
                <bk-select
                  searchable
                  v-model="props.row[columnItem.key]"
                  :font-size="'medium'"
                  :popover-min-width="180"
                  :disabled="disabled">
                  <bk-option v-for="option in columnItem.choice"
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
                  :font-size="'medium'"
                  :disabled="disabled"
                  show-select-all
                  v-model="props.row[columnItem.key]">
                  <bk-option v-for="option in columnItem.choice"
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
            <bk-button theme="primary" text @click="deleteOne(props)" :disabled="disabled">
              {{ $t('m.newCommon["删除"]') }}
            </bk-button>
          </template>
        </bk-table-column>
      </bk-table>
    </bk-form-item>
    <template v-if="item.checkValue">
      <p class="bk-task-error" v-if="item.checkMessage">{{ item.checkMessage }}</p>
      <p class="bk-task-error" v-else>{{ item.name }}{{$t('m.newCommon["为必填项！"]')}}</p>
    </template>
  </div>
</template>

<script>
  export default {
    name: 'CUSTOMTABLE',
    props: {
      item: {
        type: Object,
        required: true,
        default: () => {},
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
      };
    },
    watch: {
      'item.val'() {
        if (this.item.val === '') {
          this.item.val = [];
          const obj = {};
          for (let i = 0; i < this.item.meta.columns.length; i++) {
            const { key } = this.item.meta.columns[i];
            obj[key] = '';
          }
          this.item.val.push(obj);
        }
        if (typeof this.$parent.refresh === 'function') {
          this.$parent.refresh();
        }
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
      // 脏数据处理：如果自定义表格中有下拉框，且选中的 key 在 choice.key 中找不到
      // 尝试把 key 在 choice.name 中找,找到，则把 key 替换成 choice.key
      // 上诉条件都不满足！则把该项的 value 赋值为空，结合必填校验让用户去重新选择！
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
    },
    methods: {
      addOne() {
        const obj = {};
        for (let i = 0; i < this.item.meta.columns.length; i++) {
          const { key } = this.item.meta.columns[i];
          obj[key] = '';
        }
        this.item.val.push(obj);
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
              this.item.val.splice(index.$index, 1);
            },
          });
        }
      },
    },
  };
</script>


