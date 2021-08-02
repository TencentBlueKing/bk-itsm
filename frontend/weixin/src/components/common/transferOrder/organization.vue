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
  <div class="organization">
    <div class="org-header">
      <span
        :class="['van-ellipsis', { 'is-multistage': isBreadCrumb.length }]"
        @click="handlerGoFirstLevel">
        组织架构
      </span>
      <div v-if="isBreadCrumb.length" class="bread-crumb">
        <span
          v-if="isBreadCrumb.length === 1"
          class="bread-crumb-item van-ellipsis">
          <van-icon name="arrow" color="#979ba5" />
          {{ isBreadCrumb[0].name }}
        </span>
        <span
          v-if="isBreadCrumb.length > 1"
          class="bread-crumb-item"
          @click="handlerBreadCrumbClick">
          <van-icon name="arrow" color="#979ba5" />
          {{ '...' }}
        </span>
        <span
          v-if="isBreadCrumb.length > 1"
          class="bread-crumb-item van-ellipsis">
          <van-icon name="arrow" color="#979ba5" />
          {{ isBreadCrumb[isBreadCrumb.length - 1].name }}
        </span>
      </div>
    </div>
    <div class="org-content">
      <div v-for="organization in organizationList" :key="organization.id" class="content-item">
        <van-checkbox
          :model-value="isCheckedId === organization.id"
          :label-disabled="true"
          @click="handelerCheckboxClick(organization)">
          <van-icon name="shrink" />
          {{ organization.name }}
        </van-checkbox>
        <van-icon
          v-if="organization.children && organization.children.length"
          name="arrow"
          color="#979ba5"
          @click="handlerGoNextLevel(organization)" />
      </div>
    </div>
    <div class="org-buuton">
      <span v-if="checkedInfo.name" class="select">已选：{{ checkedInfo.name }}</span>
      <span v-else class="not-select">暂未选择</span>
      <van-button type="primary" size="normal" @click="handlerDetermineClick">确定</van-button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, Ref, watch, ref, toRefs } from 'vue'
import { useStore } from 'vuex'

interface Idepartment {
  id: number | null,
  name: string,
  children?: Array<Idepartment>
}

export default defineComponent({
  name: 'Organization',
  props: {
    isChangeType: {
      type: Boolean,
      default: false
    }
  },
  emits: ['change'],
  setup(props, { emit }) {
    const { isChangeType } = toRefs(props)
    const store = useStore()
    const dataInfo = ref([])
    const checkedInfo: Ref<Idepartment> = ref({
      id: null,
      name: ''
    })
    const isBreadCrumb = ref([]) // 面包屑路径
    const isCheckedId: Ref<number> = ref(0) // 当前选择id
    const organizationList: Ref<Idepartment[]> = ref([])
    watch(isChangeType, (val) => {
      if (val) return
      checkedInfo.value = {
        id: null,
        name: ''
      }
      isBreadCrumb.value = []
      organizationList.value = dataInfo.value
      isCheckedId.value = 0
    })
    // 获取组织架构内容
    const getOrganization = async () => {
      const resp = await store.dispatch('ticket/getTreeInfo')
      dataInfo.value = resp.data
      organizationList.value = dataInfo.value
    }
    getOrganization()

    // 选择部门
    const handelerCheckboxClick = (val: Idepartment): void => {
      isCheckedId.value = isCheckedId.value === val.id ? 0 : val.id
      if (Number(checkedInfo.value.id) === Number(val.id)) {
        checkedInfo.value = {
          id: null,
          name: ''
        }
        return
      }
      checkedInfo.value = Object.assign({}, checkedInfo.value, val)
    }

    // 前往下一级
    const handlerGoNextLevel = (val: Idepartment): void => {
      // 设置面包屑路径
      const { id, name, children } = val
      isBreadCrumb.value.push({
        id,
        name
      })
      // 根据id来获取架构列表数据
      organizationList.value = children || []
    }

    // 面包屑点击事件
    const handlerBreadCrumbClick = async () => {
      // 修改路由
      isBreadCrumb.value.pop()
      const { length } = isBreadCrumb.value
      const { id } = isBreadCrumb.value[length - 1]
      // 根据id来获取架构列表数据
      await onPassIdgetOrgList(dataInfo.value, id)
    }

    /**
     * 根据id来获取架构列表数据
     * @param {Idepartment[]} data - 用来筛选的数据
     * @param {number} id - 用来进行匹配的id
     * @param {boolean} isRouter - 是否为外界传进来的
     */
    const onPassIdgetOrgList = (data, id: number) => {
      data.forEach((item: Idepartment) => {
        if (item.id === id) {
          organizationList.value = item.children
          return
        }
        if (item.children) {
          onPassIdgetOrgList(item.children, id)
        }
      })
    }

    // 返回第一级
    const handlerGoFirstLevel = (): void => {
      organizationList.value = dataInfo.value
      isBreadCrumb.value = []
    }

    // 确定保存
    const handlerDetermineClick = (): void => {
      emit('change', checkedInfo.value)
    }

    return {
      organizationList,
      isCheckedId,
      checkedInfo,
      isBreadCrumb,
      getOrganization,
      handelerCheckboxClick,
      handlerGoNextLevel,
      handlerDetermineClick,
      handlerBreadCrumbClick,
      handlerGoFirstLevel
    }
  }
})

</script>

<style lang="postcss" scoped>
  .organization {
    height: 100%;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    display: flex;
    flex-direction: column;
    background: #f9f9f9;
    z-index: 1001;
    .org-header {
      display: flex;
      align-items: center;
      font-size: 32px;
      height: 96px;
      padding: 0 40px;
      margin-top: 1px;
      color: #262626;
      background: #fff;
      box-shadow: 0px -1px 0px 0px #e6e6e6 inset;
      margin-bottom: 20px;
      .is-multistage {
        color: #979ba5;
      }
      .bread-crumb {
        display: flex;
        align-items: center;
      }
      .bread-crumb-item {
        display: flex;
        align-items: center;
        max-width: 300px;
        .van-icon {
          top: 2px;
          font-size: 32px;
          margin: 0 16px;
        }
      }
    }
    .org-content {
      flex: 1;
      overflow-y: scroll;
      background: #ffffff;
      padding: 0 40px;
      .content-item {
        height: 112px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 32px;
        color: #262626;
        box-shadow: 0px -1px 0px 0px #e6e6e6 inset;
        padding: 0;
        /deep/ .van-checkbox {
          .van-checkbox__icon {
            height: 48px;
            font-size: 48px;
            margin-right: 31px;
          }
          .van-checkbox__label {
            display: flex;
            align-items: center;
            margin-left: 0;
            .van-icon {
              font-size: 64px;
              margin-right: 16px;
            }
          }
        }
      }
    }
    .org-buuton {
      height: 116px;
      padding: 0 40px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0px -1px 0px 0px #e6e6e6;
      font-size: 28px;
      .select {
        color: #262626;
      }
      .not-select {
        color: #8c8c8c;
      }
      .van-button {
        width: 176px;
        height: 64px;
        border-radius: 6px;
      }
    }
  }
</style>
