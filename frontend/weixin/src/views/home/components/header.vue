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
  <section class="home-header van-hairline--bottom" v-bind="$attrs">
    <div class="header-content " :class="{ 'search-mode': searchMode }">
      <template v-if="!searchMode && !ticketMode">
        <div class="logo">
          <img src="../../../assets/images/itsm-logo.svg">
        </div>
        <div class="ticket-type" @click="onToggleTypePanel">
          <span class="current-type">{{ typeName }}</span>
          <van-icon name="play" class="triangle-icon" />
        </div>
        <div class="ticket-func">
          <div class="search-entry" @click="onSearchModeOpen">
            <van-icon name="search" />
          </div>
          <div class="create-ticket" @click="onCreateTicket">+</div>
        </div>
      </template>
      <div v-if="searchMode" class="search-input">
        <form action="#">
          <van-search
            ref="searchInput"
            v-model="searchStr"
            shape="round"
            placeholder="请输入搜索关键字"
            @clear="onSearchClear"
            @search="onSearch" />
        </form>
        <span class="cancel-btn" @click="onSearchModeClose">取消</span>
      </div>
    </div>
    <div v-show="showTypePanel" class="type-wrap">
      <van-popup
        :show="showPopup"
        position="top"
        :style="{ position: 'absolute' }"
        :overlay-style="{ position: 'absolute' }"
        @click-overlay="onPopupHide"
        @closed="onPopupClosed">
        <ul class="type-list">
          <li
            v-for="item in typeList"
            :key="item.key"
            :class="{ active: item.key === crtType }"
            @click="onSelectType(item)">
            {{ item.name }}
          </li>
        </ul>
      </van-popup>
    </div>
  </section>
</template>
<script lang="ts">
import { useStore } from 'vuex'
import { ref, Ref, computed, watch, onMounted, nextTick, toRefs } from 'vue'
import { useRouter } from 'vue-router'

interface ServiceList {
  name: string,
  key: string
}

export default {
  name: 'HomeHeader',
  props: {
    keyword: {
      type: String,
      default: ''
    }
  },
  emits: [
    'change',
    'toggle-search',
    'search'
  ],
  setup(props, { emit }) {
    const store = useStore()
    const router  = useRouter()
    const { keyword } = toRefs(props)
    const defaultType: ServiceList = {
      key: 'all',
      name: '全部类别'
    }
    const crtType: Ref<string> = ref(defaultType.key)
    const searchMode: Ref<boolean> = ref(false)
    const searchStr: Ref<string> = ref('')
    const showTypePanel: Ref<boolean> = ref(false)
    const showPopup: Ref<boolean> = ref(false)
    const typeList: Ref<ServiceList[]> = ref([{ ...defaultType }])
    const searchInput = ref(null)

    const typeName = computed(() => typeList.value.find(item => item.key === crtType.value).name)

    watch(keyword, (val) => {
      searchStr.value = val
    })

    const getAllTypeList = async () => {
      const resp = await store.dispatch('getCategories')
      typeList.value = [{ ...defaultType }, ...resp.data]
    }
    const onToggleTypePanel = (): void => {
      if (!showPopup.value) {
        showTypePanel.value = true
        showPopup.value = true
      } else {
        onPopupHide()
      }
    }
    const onPopupHide = (): void => {
      showPopup.value = false
    }
    const onPopupClosed = (): void => {
      showTypePanel.value = false
    }
    const onSelectType = (item: ServiceList): void => {
      crtType.value = item.key
      onPopupHide()
      emit('change', item.key)
    }
    const onSearchModeOpen = async (): void => {
      searchMode.value = true
      emit('toggle-search', true)
      onPopupHide()
      await nextTick()
      searchInput.value.focus()
    }
    const onSearchClear = (): void => {
      searchMode.value = true
      searchStr.value = ''
      emit('search', '')
    }
    const onSearchModeClose = (): void => {
      searchMode.value = false
      emit('search', '')
      emit('toggle-search', false)
    }
    const onSearch = (): void => {
      emit('search', searchStr.value)
    }
    const onCreateTicket = (): void => {
      router.push({
        name: 'service'
      })
    }

    onMounted(getAllTypeList)

    return {
      crtType,
      searchMode,
      searchStr,
      showTypePanel,
      showPopup,
      typeList,
      typeName,
      searchInput,
      onToggleTypePanel,
      onPopupHide,
      onPopupClosed,
      onSelectType,
      onSearchModeOpen,
      onSearchModeClose,
      onSearchClear,
      onSearch,
      onCreateTicket
    }
  }
}
</script>
<style lang="postcss" scoped>
  .home-header {
    position: relative;
    &:after {
      border-color: #e6e6e6;
    }
  }
  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 32px;
    height: 98px;
    color: #63656e;
    z-index: 11;
    &.search-mode {
      height: 112px;
    }
  }
  .logo {
    width: 48px;
    height: 48px;
    img {
      width: 100%;
    }
  }
  .ticket-type {
    display: flex;
    align-items: center;
    .current-type {
      margin-right: 8px;
      font-size: 32px;
      color: #63656e;
    }
    .triangle-icon {
      font-size: 16px;
      color: #979ba5;
      transform: rotate(90deg);
    }
  }
  .create-ticket {
    width: 50px;
    height: 50px;
    margin-left: 20px;
    background: #3a83ff;
    color: #fff;
    border-radius: 8px;
    line-height: 50px;
    font-size: 50px;
    text-align: center;
  }
  .ticket-func {
    display: flex;
    align-items: center;
  }
  .search-entry {
    display: flex;
    align-items: center;
    width: 64px;
    height: 48px;
    justify-content: center;
    font-size: 32px;
    background: #f5f6fa;
    border-radius: 24px;
    i {
      font-size: 32px;
      color: #979ba5;
    }
  }
  .create-ticket-model {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    height: 60px;
    border: 2px solid #d3d3d3;
    border-radius: 8px;
    font-size: 32px;
    margin: 0 60px;
  }
  .search-input {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    font-size: 32px;
    .vant-cell {
      font-size: 32px;
    }
    .van-search {
      width: 600px;
      font-size: 32px;
      /deep/ .van-search__content {
        padding-left: 32px;
      }
      /deep/ input {
        font-size: 32px;
      }
      /deep/ .van-field__left-icon {
        display: inline-flex;
        align-items: center;
      }
      /deep/ .van-icon {
        font-size: 32px;
        color: #979ba5;
      }
    }
    .cancel-btn {
      font-size: 32px;
      color: #3a84ff;
    }
  }
  .type-wrap {
    position: fixed;
    top: 99px;
    left: 0;
    right: 0;
    bottom: 0;
    background: transparent;
    z-index: 10;
    overflow: hidden;
  }
  .type-list {
    padding: 32px 30px 8px;
    color: #63656e;
    background: #ffffff;
    li {
      margin-bottom: 32px;
      margin-right: 30px;
      display: inline-block;
      padding: 16px 0;
      width: 200px;
      text-align: center;
      font-size: 32px;
      line-height: 1;
      background: #f4f6fa;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      &.active {
        color: #3a84ff;
        border: 1px solid #3a84ff;
      }
    }
  }
</style>
