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
      <bk-table :data="item.val"
        :size="'small'">
        <template v-for="title in item.choice">
          <bk-table-column :label="title.name" :key="title.key">
            <template slot-scope="props">
              <bk-input :clearable="true" v-model="props.row[title.key]" :disabled="disabled"></bk-input>
            </template>
          </bk-table-column>
        </template>
        <bk-table-column :label="$t(`m.user['操作']`)" width="150">
          <template slot-scope="props">
            <bk-button theme="primary" :disabled="disabled" text @click="addOne">
              {{ $t('m.newCommon["添加"]') }}
            </bk-button>
            <bk-button theme="primary" :disabled="disabled" text @click="deleteOne(props)">
              {{ $t('m.newCommon["删除"]') }}
            </bk-button>
          </template>
        </bk-table-column>
      </bk-table>
      <template v-if="item.checkValue">
        <p class="bk-task-error" v-if="item.checkMessage">{{ item.checkMessage }}</p>
        <p class="bk-task-error" v-else>{{ item.name }}{{$t('m.newCommon["为必填项！"]')}}</p>
      </template>
    </bk-form-item>
  </div>
</template>

<script>
  export default {
    name: 'TABLE',
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
      return {};
    },
    watch: {
      'item.val'() {
        if (this.item.val === '') {
          this.item.val = [];
          const obj = {};
          for (let i = 0; i < this.item.choice.length; i++) {
            const { key } = this.item.choice[i];
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
        for (let i = 0; i < this.item.choice.length; i++) {
          const { key } = this.item.choice[i];
          obj[key] = '';
        }
        this.item.val.push(obj);
      }
    },
    methods: {
      addOne() {
        const obj = {};
        for (let i = 0; i < this.item.choice.length; i++) {
          const { key } = this.item.choice[i];
          obj[key] = '';
        }
        this.item.val.push(obj);
      },
      deleteOne(props) {
        if (this.item.val.length === 1) {
          this.$bkMessage({
            message: '默认行不能删除',
            theme: 'warning',
          });
        } else {
          this.$bkInfo({
            title: '确认要删除此条数据？',
            confirmFn: () => {
              this.item.val.splice(props.$index, 1);
            },
          });
        }
      },
    },
  };
</script>


