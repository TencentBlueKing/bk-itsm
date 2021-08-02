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
  <div class="transfer-order">
    <!-- 一级处理人 -->
    <div class="content-item">
      <span class="van-ellipsis">{{ title.firstTitle }}</span>
      <div class="content-right" @click="handlerPopupOpen">
        <span class="processor van-ellipsis">
          {{ firstSelectedItem.name || '请选择' }}
        </span>
        <van-icon name="arrow" color="#8c8c8c" />
      </div>
    </div>
    <!-- 二级处理人 -->
    <template v-if="!noSecondTypeList.includes(firstSelectedItem.type)">
      <div
        :class="['content-item', { 'ban-operate': !firstSelectedItem.type }]">
        <span class="van-ellipsis">{{ firstSelectedItem.name || title.secondTitle }}</span>
        <div
          class="content-right"
          @click="handlerSecondPopupOpen(firstSelectedItem.type)">
          <span class="processor van-ellipsis">
            {{ secondDisplayName || '请选择' }}
          </span>
          <van-icon name="arrow" :color="firstSelectedItem.type ? '#8c8c8c' : '#e5e6e9'" />
        </div>
      </div>
    </template>
    <!-- 弹出层 -->
    <van-popup :show="showPopup" position="bottom" :lazy-render="false">
      <!-- 一级处理人内容 -->
      <van-picker
        v-if="isFirstPopup"
        ref="pickerRef"
        :title="title.popupTitle"
        show-toolbar
        :columns="firstLevelList"
        :default-index="columnIndex"
        value-key="name"
        @confirm="onConfirm"
        @cancel="onCancel" />
      <!-- 二级处理人内容 -->
      <template v-else>
        <div class="seconed-content">
          <div class="content-header">
            <span class="cancel" @click="onCancel">取消</span>
            <span class="title van-ellipsis">{{ firstSelectedItem.name }}</span>
            <span class="confirm" @click="onConfirm">确认({{ checked.length }})</span>
          </div>
          <div v-if="secondLevelList.length" class="content-columns">
            <van-checkbox-group v-model="checked">
              <van-checkbox
                v-for="column in secondLevelList"
                :key="column.id"
                class="column-item"
                :label-disabled="true"
                :name="column.id"
                icon-size="24px"
                shape="square"
                @click="handelerCheckboxClick(column.name)">
                <span>{{ column.name }}</span>
              </van-checkbox>
            </van-checkbox-group>
          </div>
          <div v-else class="no-option">暂无选项</div>
        </div>
      </template>
    </van-popup>
    <!-- 组织架构 -->
    <organization
      v-show="isShowOrg"
      :is-change-type="isChangeType"
      @change="handelerOrgChange" />
    <person-select
      :show="showPersonSelect"
      :inculde="inculdePersons"
      @close="handlePersonSelectClose($event, false)"
      @created="handlePersonSelectClose($event, true)" />
  </div>
</template>

<script lang="ts">
import { defineComponent, toRefs, Ref, ref, nextTick, computed } from 'vue'
import { useStore } from 'vuex'
import Organization from './organization.vue'
import PersonSelect from '../PersonSelect.vue'
import emitter from '../../../utils/emitter'

interface IColumn {
  id: string | number,
  name?: string,
  type?: string
}

interface IUserItem {
  id: number,
  username: string,
  // eslint-disable-next-line
  display_name: string,
}

interface IIncludeItem {
  type: string;
  list: any [];
}

export default defineComponent({
  name: 'TransferOrder',
  components: {
    Organization,
    PersonSelect
  },
  props: {
    firstInfo: { // 一级处理人数据
      type: String,
      default: ''
    },
    secondInfo: { // 二级处理人数据
      type: Array,
      default: () => ([])
    },
    title: { // 标题
      type: Object,
      default: () => ({
        firstTitle: '转单至',
        secondTitle: '转单人',
        popupTitle: '选择转单角色'
      })
    },
    firstIncludeList: { // 一级处理人过滤列表
      type: Array,
      default: () => ([])
    },
    secondIncludeList: { // 二级处理人过滤列表
      type: Array,
      default: () => ([])
    }
  },
  emits: ['update:firstInfo', 'update:secondInfo'],
  setup(props, { emit }) {
    const store = useStore()
    const { firstInfo, secondInfo, title, firstIncludeList, secondIncludeList } = toRefs(props)
    const showPopup: Ref<boolean> = ref(false) // 是否展示弹出层
    const isChangeType: Ref<boolean> = ref(false) // 是否切换处理人类型
    const isShowOrg: Ref<boolean> = ref(false) // 是否展示组织架构
    const showPersonSelect = ref(false) // 人员选择
    const columnIndex: Ref<number> = ref(0) // popup默认选中的下标
    const firstSelectedItem: Ref<IColumn> = ref({
      id: 0,
      name: '',
      type: ''
    }) // 一级处理人信息
    const secondDisplayName = ref('') // 二级处理人信息

    const checked = ref(secondInfo.value) // checkbox 绑定值
    const firstLevelList = ref<Array<IColumn>>([])
    const secondLevelList = ref<Array<IColumn>>([])

    const isFirstPopup: Ref<boolean> = ref(true) // 是否为第一级弹出层
    const noSecondTypeList = ['EMPTY', 'OPEN', 'STARTER', 'BY_ASSIGNOR', 'STARTER_LEADER']
    const searchValue = ref('')
    const initSecondInfo = computed(() => secondInfo.value)// 用来判断是否有二级信息传入
    const checkNames = ref<string []>([])

    // 获取一级处理人列表
    const getFirstList = async () => {
      const resp = await store.dispatch('ticket/getUser', {
        is_processor: true
      })
      const respList = resp.data.map((item: IColumn) => ({
        id: item.id,
        name: item.name,
        type: item.type
      }))
      const includeList = firstIncludeList.value
      if (includeList.length) {
        firstLevelList.value = respList.filter((item: IColumn) => includeList.includes(item.type))
      } else {
        firstLevelList.value = respList
      }
      if (firstInfo.value) {
        firstSelectedItem.value = firstLevelList.value.find((column: IColumn) => column.type === firstInfo.value) || {}
      }
    }

    // 根据用户信息设置二级处理人数据
    const inculdePersons = computed(() => {
      const targetPersonRule = secondIncludeList.value.find((rule: IIncludeItem) => rule.type === 'PERSON')
      if (targetPersonRule) {
        return targetPersonRule.list
      }
      return []
    })

    // 获取二级处理人列表
    const getSecondList = async () => {
      secondLevelList.value = []
      const { type } = firstSelectedItem.value
      if (type === 'PERSON') {
        return
      }
      const resp = await store.dispatch('ticket/getSecondUser', {
        shortcut: true,
        role_type: type
      })
      const respList = resp.data.map((item: IColumn) => {
        if (checked.value.length && checked.value.includes(item.id)) {
          checkNames.value.push(item.name)
        }
        return {
          id: item.id,
          name: item.name,
          type: item.id
        }
      })
      // 筛选要的数据
      const targetRule = secondIncludeList.value.find((rule: any) => rule.type === type)
      if (targetRule) {
        secondLevelList.value = respList.filter((item: IColumn) => {
          const flag = targetRule.list.some((id: string | number) => String(id) === String(item.id))
          return flag
        })
      } else {
        secondLevelList.value = respList
      }
      if (initSecondInfo.value.length) {
        // 根据选中值设置secondDisplayName
        secondDisplayName.value = checkNames.value.join('/')
      }
    }

    const initList = async () => {
      await getFirstList()
      getSecondList()
    }
    initList()

    // 打开一级弹出层
    const handlerPopupOpen = (): void => {
      showPopup.value = true
      isFirstPopup.value = true
      nextTick(() => {
        getColumnIndex()
      })
    }

    // 打开二级弹出层
    const handlerSecondPopupOpen = async (type: string) => {
      if (!firstSelectedItem.value.type) {
        emitter.emit('notify', { type: 'warning', message: `请先选择${title.value.firstTitle}` })
        return
      }
      if (type === 'PERSON') {
        showPersonSelect.value = true
        return
      }
      isFirstPopup.value = false
      if (type === 'ORGANIZATION') {
        isShowOrg.value = true
        isChangeType.value = false
        return
      }
      // 获取二级处理人列表
      if (!secondLevelList.value.length) {
        await getSecondList()
      }
      showPopup.value = true
    }

    // 动态设置默认选项
    const pickerRef = ref<any>(null) // 获取 picker dom
    const getColumnIndex = () => {
      columnIndex.value = firstLevelList.value.findIndex((column: IColumn) => {
        const bool = column.type === firstSelectedItem.value.type
        return bool
      })
      pickerRef.value.setColumnIndex(0, columnIndex.value)
    }

    // Picker选择器确定事件
    const onConfirm = (value: IColumn) => {
      if (!value) return
      if (isFirstPopup.value) {
        const { id } = firstSelectedItem.value
        if (id !== value.id) {
          firstSelectedItem.value = Object.assign({}, firstSelectedItem.value, value)
          isChangeType.value = true
          // 清除二级处理人相关数据
          secondLevelList.value = []
          checked.value = []
          checkNames.value = []
          searchValue.value = ''
          secondDisplayName.value = ''
          getSecondList()
        }
      } else {
        // 根据选中值设置secondDisplayName
        secondDisplayName.value = checkNames.value.join('/')
      }
      emit('update:firstInfo', firstSelectedItem.value.type)
      emit('update:secondInfo', checked.value)
      showPopup.value = false
    }

    // Picker选择器取消事件
    const onCancel = (): void => {
      showPopup.value = false
    }

    const handelerCheckboxClick = () => {
      checkNames.value = checked.value.map((id) => {
        const { name } = secondLevelList.value.find(m => m.id === id)
        return name
      })
    }

    const handelerOrgChange = (val) => {
      isShowOrg.value = false
      firstSelectedItem.value = {
        id: '10',
        name: '组织架构',
        type: 'ORGANIZATION'
      }
      const route = []
      const { id, name, level } = val
      route.push({ id, name, level })
      secondDisplayName.value = route.map(item => item.name).join('/')
      route.pop()
      emit('update:secondInfo', [id])
    }

    const handlePersonSelectClose = (selected: IUserItem [], close: boolean) => {
      showPersonSelect.value = close
      secondDisplayName.value = selected.map((person: IUserItem) => {
        const names = `${person.username}(${person.display_name})`
        return names
      }).join('/')
      checked.value = selected.map((person: IUserItem) => person.username)
      emit('update:secondInfo', checked.value)
    }
    return {
      showPersonSelect,
      isFirstPopup,
      pickerRef,
      showPopup,
      isShowOrg,
      isChangeType,
      noSecondTypeList,
      columnIndex,
      firstSelectedItem,
      searchValue,
      checkNames,
      secondDisplayName,
      checked,
      initList,
      firstLevelList,
      secondLevelList,
      handlerPopupOpen,
      handlerSecondPopupOpen,
      onConfirm,
      onCancel,
      handelerOrgChange,
      handelerCheckboxClick,
      handlePersonSelectClose,
      inculdePersons
    }
  }

})

</script>

<style lang="postcss">
  .transfer-order {
    .content-item {
      height: 96px;
      display: flex;
      background: #fff;
      align-items: center;
      justify-content: space-between;
      font-size: 28px;
      color: #262626;
      box-shadow: 0px -1px 0px 0px #e6e6e6 inset;
      padding: 0 40px;
      .content-left {
        min-width: 200px;
      }
      .content-right {
        flex: 1;
        min-width: 300px;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        .van-icon {
          font-size: 32px;
          margin-left: 5px;
        }
        .processor {
          color: #8c8c8c;
          margin-left: 40px;
        }
      }
      &.ban-operate .processor {
        color: #e5e6e9;
      }
    }
    /deep/ .van-picker {
      .van-picker__toolbar {
        height: 112px;
        button {
          font-size: 32px;
        }
        .van-picker__title {
          font-size: 32px;
          font-weight: 500;
          line-height: 48px;
          color: #262626;
        }
        .van-picker__confirm {
          color: #3a84ff;
        }
      }
      .van-picker-column {
        font-size: 32px;
        color: #262626;
      }
    }
    .van-search {
      margin: 0 16px;
      .van-search__content {
        height: 68px;
        .van-cell {
          .van-icon {
            font-size: 36px;
            color: #b2b2b2;
            margin-right: 5px;
          }
        }
      }
    }
    .seconed-content {
      height: 640px;
      display: flex;
      flex-direction: column;
      .content-header {
        height: 112px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0px -1px 0px 0px #e6e6e6 inset;
        padding: 0 40px;
        font-size: 32px;
        font-weight: 500;
        .cancel {
          color: #969799;
        }
        .title {
          color: #262626;
          max-width: 50%;
          text-align: center;
        }
        .confirm {
          color: #3a84ff;
        }
      }
      .content-columns {
        padding: 0 40px;
        flex: 1;
        overflow-y: scroll;
        .column-item {
          height: 96px;
          background: #ffffff;
          box-shadow: 0px -1px 0px 0px #e6e6e6 inset;
          &:last-child {
            box-shadow: none;
          }
          .van-checkbox__label {
            margin-left: 20px;
          }
        }
      }
    }
    .no-option {
      display: flex;
      flex: 1;
      justify-content: center;
      align-items: center;
      color: #e5e6e9;
    }
  }

</style>
