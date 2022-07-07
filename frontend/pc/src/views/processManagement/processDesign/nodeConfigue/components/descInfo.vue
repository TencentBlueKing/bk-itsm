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
  <bk-form-item>
    <bk-input
      style="width: 450px"
      ref="input"
      v-if="isEdit"
      behavior="simplicity"
      :maxlength="64"
      :placeholder="$t(`m.systemConfig['请输入描述']`)"
      type="textarea"
      v-model="desc"
      @blur.self="change">
    </bk-input>
    <div v-else style="font-size: 12px; color: #63656e; width: 450px; word-wrap:break-word;line-height: 16px;">
      <span v-if="!value">{{ $t(`m['当前节点未设置节点描述']`) }}</span>
      {{desc}}
      <i style="font-size: 16px" class="bk-itsm-icon icon-edit-bold edit-icon"></i>
      <span style="color: #3a84ff" @click="edit">{{ $t(`m['点击修改']`) }}</span>
    </div>
  </bk-form-item>
</template>

<script>
  export default {
    name: 'descInfo',
    props: {
      value: {
        type: String,
        default: () => '',
      },
    },
    data() {
      return {
        isEdit: false,
        desc: this.value,
      };
    },
    watch: {
      value(val) {
        this.desc = val;
      },
    },
    mounted() {
    },
    methods: {
      edit() {
        this.isEdit = true;
        this.$nextTick(function () {
          this.$refs.input.focus();
        });
      },
      change(value) {
        this.isEdit = false;
        this.$emit('input', value);
      },
    },
  };
</script>
<style lang='scss' scoped>
/deep/ .bk-textarea-wrapper {
  height: 70px;
  .bk-form-textarea {
    height: 100%;
    min-height: unset;
  }
}
</style>
