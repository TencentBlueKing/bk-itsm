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
  <van-popup :show="show" position="bottom" :lazy-render="false">
    <div class="person-select">
      <header class="select-title">
        <span v-if="!showSelectedPerson">选择成员</span>
        <span v-else>已选人员 <span class="color-blue">{{ selected.length }}</span> </span>
      </header>
      <div class="select-body">
        <template v-if="showSelectedPerson">
          <ul class="person-list">
            <li
              v-for="(item, index) in selected"
              :key="index"
              class="person-item">
              <span>{{ item.username }}({{ item.display_name }})</span>
              <van-icon class="delete-person-icon" name="cross" @click="cancelSelect(index)" />
            </li>
          </ul>
        </template>
        <template v-else>
          <van-search
            v-model="searchValue"
            shape="round"
            placeholder="请输入搜索关键词"
            @update:model-value="handelerSearchChange" />
          <ul class="person-list search">
            <li
              v-for="(item) in searchList"
              :key="item.username"
              class="person-item">
              <div class="person-name">
                <van-checkbox
                  :model-value="selected.some(person => person.username === item.username)"
                  class="select-checkbox"
                  @click="onSelectPerson(item)" />
                <span v-if="!!searchValue" v-html="item.highlightName" />
                <span v-else>{{ item.username }}({{ item.display_name }})</span>
              </div>
            </li>
          </ul>
        </template>
      </div>
      <footer class="select-footer">
        <span v-if="!showSelectedPerson" @click="showSelectedPerson = true">
          已选：
          <span class="color-blue">{{ selected.length }}</span>
          <van-icon class="unfold-icon" name="arrow-up" />
        </span>
        <span v-else @click="showSelectedPerson = false">
          收起
          <van-icon class="unfold-icon" name="arrow-down" />
        </span>
        <van-button type="primary" class="confirm-button" @click="onClose">确定</van-button>
      </footer>
    </div>
  </van-popup>
</template>
<script lang="ts">
import { defineComponent, ref, toRefs, watch } from 'vue'
import jsonp from 'jsonp'
import { debounce } from '../../utils/tool'

interface IUserItem {
  id: number,
  username: string,
  // eslint-disable-next-line
  display_name: string,
}

export default defineComponent({
  name: 'PersonSelect',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    modelValue: {
      type: Array,
      default: () => ([])
    },
    inculde: {
      type: Array,
      default: () => ([])
    }
  },
  emits: ['update:modelValue', 'close'],
  setup(props, { emit }) {
    const { show, inculde } = toRefs(props)
    const showSelectedPerson = ref(false) // 显示已选
    watch(show, () => {
      const searchStr = inculde.value.length ? inculde.value.join(',') : ''
      getSearchList(searchStr, !!inculde.value.length)
    })

    const selected = ref<IUserItem []>([])
    const cancelSelect = (index: number) => {
      selected.value.splice(index, 1)
    }
    watch(selected, (value) => {
      emit('update:modelValue', value)
    })

    const searchValue = ref('')
    const searchList = ref([])
    /**
     * 搜索人员
     * value 搜索值
     * exact 是否精确搜索
     */
    const loadUserInfo = (value: string, exact = false) => {
      const host = window.BK_USER_MANAGE_WEIXIN_HOST || location.origin
      const api = `${host}/api/c/compapi/v2/usermanage/fs_list_users/`
      return new Promise((resolve, reject) => {
        const lookups = exact ? 'exact_lookups' : 'fuzzy_lookups'
        const url = `${api}?app_code=bk-magicbox&${lookups}=${value}&page_size=20&page=1`
        jsonp(url, null, (err: Error, res: any) => {
          if (err) {
            reject(err)
          } else {
            resolve(res.data.results)
          }
        })
      })
    }
    const getSearchList = (value: string, exact = false) => {
      loadUserInfo(value, exact).then((data: any) => {
        searchList.value = data.filter((item: IUserItem) => {
          if (inculde.value.length && inculde.value.includes(item.username)) {
            return true
          }
          // 当二级处理人为空时，返回所有结果
          if (!inculde.value.length) {
            return true
          }
          return false
        }).map((item: IUserItem) => {
          const reg = new RegExp(value, 'i')
          const names = `${item.username}(${item.display_name})`
          const highlightName = names.replace(reg, `<span style="color: #3a84ff;">${value}</span>`)
          return {
            ...item,
            highlightName
          }
        })
      })
    }
    const onSearch = debounce(getSearchList, 500)
    const handelerSearchChange = (value: string) => {
      onSearch(value)
    }
    const onSelectPerson = (person: IUserItem) => {
      const target = selected.value.find((item: IUserItem) => item.username === person.username)
      console.log(target, 'target')
      if (target) {
        selected.value = selected.value.filter((item: IUserItem) => item.username !== person.username)
      } else {
        selected.value.push(person)
      }
    }

    const onClose = () => {
      emit('close', selected.value)
    }

    return {
      selected,
      searchList,
      cancelSelect,
      searchValue,
      showSelectedPerson,
      handelerSearchChange,
      onSelectPerson,
      onClose
    }
  }
})
</script>
<style lang="postcss">
.color-blue {
  color: #3a84ff;
}
.person-select {
  width: 100%;
  background: #ffffff;
  .select-title {
    padding-left: 45px;
    height: 112px;
    line-height: 112px;
    font-size: 32px;
    color: #262626;
    box-shadow: 0px -1px 0px 0px #e6e6e6 inset;
  }
  .select-body {
    height: 750px;
    overflow: hidden;
    .person-list {
      padding: 0 40px;
      overflow: auto;
      &.search {
        height: 642px;
      }
      .person-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 96px;
        line-height: 96px;
        font-size: 32px;
        font-weight: 400;
        color: #262626;
        box-shadow: 0px -1px 0px 0px #e6e6e6 inset;
        .person-name {
          display: flex;
          .select-checkbox {
            margin-right: 12px;
          }
        }
        .delete-person-icon {
          color: #979ba5;
        }
      }
    }
  }
  .select-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 40px;
    height: 116px;
    color: #262626;
    font-weight: 400;
    font-size: 28px;
    box-shadow: 0px -1px 0px 0px #e6e6e6;
    .confirm-button {
      width: 176px;
      height: 64px;
      border-radius: 6px;
    }
    .unfold-icon {
      margin-left: 22px;
      color: #979ba5;
    }
  }
}
</style>
