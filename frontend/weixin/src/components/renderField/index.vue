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
  <div :class="['render-field', { 'is-view-mode': isViewMode }]">
    <van-form>
      <div
        v-for="(item, index) in fields"
        :key="index"
        :class="['field-wrap', { 'field-margin': !isViewMode, 'last': index === fields.length - 1}]">
        <template v-if="item.showFeild !== false">
          <component
            :is="`Field-${item.type}`"
            v-if="!notSupportTypes.includes(item.type)"
            :ref="setItemRef"
            :item="item"
            :is-view-mode="isViewMode"
            :highlight-refuse="highlightRefuse"
            :fields="fields"
            @change="handleFiledChange($event, item)" />
          <!-- 不支持的组件 -->
          <not-support v-else :is-view-mode="isViewMode" :item="item" />
        </template>
      </div>
    </van-form>
  </div>
</template>
<script lang="ts">
/**
 * RenderField 组件主要用作渲染流程中配置的所有类型的字段
 */
import { defineComponent, ConcreteComponent, toRefs, ref, Ref, onBeforeUpdate, watch } from 'vue'
import { debounce } from '../../utils/tool'
import NotSupport from './notSupport.vue'
import useFieldDisplay from './use/useFieldDisplay'
import useFieldChoice from './use/useFieldChoice'

// 注入 fields 下的所有组件
const registerComponents = (() => {
  const context = require.context('./fields/', false, /.vue$/)
  return context.keys().reduce((components: Record<string, ConcreteComponent>, key: string) => {
    // key eg: './text.vue'
    const match = key.match(/^\.\/([\w-]+)/i)
    if (match) {
      const name = match[1].toUpperCase()
      components[`Field-${name}`] = context(key).default
    }
    return components
  }, {})
})()

// 不支持的指字段类型
const notSupportTypes: string [] = [
  'CUSTOMTABLE', // 自定义表格
  'TREESELECT', //  树形选择
  // 'FILE', //        文件上传
  'CASCADE', //     级联字段
  'SOPS_TEMPLATE', // 标准运维
  'TABLE' //         表格 TODO
]

// 不支持编辑，支持查看的字段类型
const notSupportEditTypes: string [] = [
  'INPUTSELECT',
  'MEMBER',
  'MEMBERS',
  'MULTISELECT',
  'RICHTEXT'
]

interface IFieldItem {
  id: number,
  val: any,
  key?: string
}

export default defineComponent({
  name: 'RenderField',
  components: {
    ...registerComponents,
    NotSupport
  },
  props: {
    fields: {
      type: Array,
      default: () => ([])
    },
    isViewMode: {
      type: Boolean,
      default: false
    },
    highlightRefuse: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const { fields }  = toRefs<{ fields: any [] }>(props)
    const renderFieldRef: Ref = ref(null)

    // 校验相关
    let fieldRefs: Ref [] = []
    onBeforeUpdate(() => {
      fieldRefs = []
    })

    // set ref
    const setItemRef = (el: any): void => {
      // 提前剔除隐藏字段 ref
      fieldRefs = fieldRefs.filter((fieldEl: any) => !!fieldEl.item.showFeild)
      if (el && el.item.showFeild) {
        const sameRefIndex = fieldRefs.findIndex((fieldEl: any) => fieldEl.item.id === el.item.id)
        // 已存在
        if (sameRefIndex !== -1) {
          fieldRefs[sameRefIndex] = el
        } else {
          fieldRefs.push(el)
        }
      }
    }

    const hasNotSupportRequiredField = () => {
      const allNotSupportTypes = [...notSupportEditTypes, ...notSupportTypes]
      return fields.value.some((field: any) => {
        const { type, validate_type, showFeild } = field
        return allNotSupportTypes.includes(type) && validate_type === 'REQUIRE' && showFeild
      })
    }

    // 所有字段校验
    const validate = () => {
      const validateFns: Promise<boolean> [] = []
      fieldRefs.forEach((el: Ref) => {
        const fieldValidate = (el as any).validate
        if (fieldValidate instanceof Function) {
          validateFns.push(fieldValidate)
        }
      })
      const results = validateFns.map(fn => fn())
      const required = results.every(item => item)
      const allNotSupportTypes = [...notSupportEditTypes, ...notSupportTypes]
      const hasNotSupportField = fields.value.some(field => allNotSupportTypes.indexOf(field.type) !== -1)
      return required && !hasNotSupportField
    }

    /** 字段隐藏逻辑处理 */
    const watchShowFeild = useFieldDisplay()
    const watchAllFieldsDispaly = () => {
      if (fields.value.length) { // 初始化时先计算一次
        fields.value.forEach((field) => {
          field.val = field.value
          watchShowFeild.conditionField(field, fields.value)
        })
      }
    }
    watchAllFieldsDispaly()
    watch(fields, watchAllFieldsDispaly)

    /** 插入字段异步数据到 choice 中 */
    const getFieldChoice = useFieldChoice()
    getFieldChoice.insertRemoteChoiceData(fields.value)
    watch(fields, () => {
      getFieldChoice.insertRemoteChoiceData(fields.value)
    })

    const filedChange = (value: any, item: any) => {
      const targetField = fields.value.find((field: IFieldItem) => field.id === item.id)
      targetField.value = value
      targetField.val = value
      watchShowFeild.conditionField(targetField, fields.value)
    }
    const handleFiledChange = debounce(filedChange, 500)

    const getValue = () => {
      // 过滤掉隐藏字段
      const cloneValue = JSON.parse(JSON.stringify(fields.value.filter(field => field.showFeild !== false)))
      // 删除脏数据
      cloneValue.forEach((field: { val: any, showFeild: any }) => {
        delete field.val
        delete field.showFeild
      })
      return cloneValue
    }

    return {
      notSupportTypes,
      renderFieldRef,
      setItemRef,
      validate,
      fieldRefs,
      handleFiledChange,
      getValue,
      hasNotSupportRequiredField
    }
  }
})
</script>
<style lang="postcss" scoped>
.render-field {
  &.is-view-mode {
    padding: 12px 0;
    background: #ffffff;
  }
}
.field-margin {
  margin: 20px 0;
}
.field-wrap {
  display: flex;
  align-items: center;
  &.last {
    /deep/ .van-cell {
      border-bottom: none;
    }
    .not-support {
      border-bottom: none;
    }
  }
  /deep/ .van-cell {
    padding: 24px 0;
    height: 100%;
    line-height: inherit;
    border-bottom: 1px solid rgba(0,0,0,.12);
    &:after {
      border-bottom: none;
    }
    .van-cell__title {
      font-size: 28px;
      &.van-field__label {
        flex: 1;
        box-flex: 1;
      }
      & > span {
        color: #63656E;
      }
    }
    .van-cell__value {
      line-height: 36px;
      font-size: 28px;
      color: #979BA5;
      .van-field__control {
        text-align: right;
        color: #969799;
        font-size: 28px;
      }
      .van-field__error-message {
        text-align: right;
      }
    }
    &.van-cell--required:before {
      left: -14px;
      top: 26px;
    }
  }
}
/* 字段通用样式 */
/deep/ .common-view-field {
  padding: 12px 18px;
  display: flex;
  width: 100%;
  font-size: 24px;
  text-align: left;
  color: #63656e;
  line-height: 34px;
  .view-label {
    flex-shrink: 0;
    width: 160px;
    word-break: break-all;
  }
  .view-value {
    margin-left: 10px;
    word-break: break-all;
  }
}
</style>
