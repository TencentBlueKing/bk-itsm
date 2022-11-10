<template>
  <div class="service">
    <div class="service-search">
      <van-search
        shape="round"
        v-model="serviceSearchStr"
        placeholder="请输入服务名称"
        @update:model-value="onchange" />
    </div>
    <div class="service-container">
      <van-pull-refresh
        v-model="refreshing"
        pulling-text="释放刷新列表..."
        @refresh="onRefresh">
        <div v-if="!searchFocus" class="service-content">
          <div class="commonly-service">
            <h2 class="serivce-title">
              <i class="itsm-mobile-icon icon-favorite-o"></i>
              收藏的服务</h2>
            <van-loading
              v-if="commonlyLoading"
              size="24px"
              vertical>加载中...</van-loading>
            <div v-else class="container">
              <ul class="service-list">
                <li v-for="serviceItem in serviceList.favoriteList" :key="serviceItem.id">
                  <span
                    class="name"
                    :title="serviceItem.name"
                    @click="onCreateTicket(serviceItem)">
                    {{serviceItem.name}}
                  </span>
                  <span class="favorite" @click="onChangeFavorite(serviceItem)">
                    <i
                      :class="['itsm-mobile-icon', serviceItem.favorite ? 'icon-favorite orange': 'icon-favorite-o']">
                    </i>
                  </span>
                </li>
              </ul>
            </div>
          </div>
          <div class="commonly-service">
            <h2 class="serivce-title">
              <i class="itsm-mobile-icon icon-time-circle"></i>
              近一个月使用服务</h2>
            <van-loading
              v-if="commonlyLoading"
              size="24px"
              vertical>加载中...</van-loading>
            <div v-else class="container">
              <ul class="service-list">
                <li v-for="serviceItem in serviceList.latestList" :key="serviceItem.id">
                  <span
                    class="name"
                    :title="serviceItem.name"
                    @click="onCreateTicket(serviceItem)">
                    {{serviceItem.name}}
                  </span>
                  <span class="favorite" @click="onChangeFavorite(serviceItem)">
                    <i
                      :class="['itsm-mobile-icon', serviceItem.favorite ? 'icon-favorite orange': 'icon-favorite-o']">
                    </i>
                  </span>
                </li>
              </ul>
            </div>
          </div>
          <div class="all-service">
            <h2 class="service-line"></h2>
            <van-loading
              v-if="allLoading"
              size="24px"
              vertical>加载中...</van-loading>
            <div v-else class="container">
              <van-list
                v-model:loading="listState.loading"
                loading-text="加载更多中..."
                :finished="listState.finished"
                finished-text="没有更多了"
                offset="0"
                @load="onload">
                <ul class="service-list">
                  <li v-for="serviceItem in serviceList.allList" :key="serviceItem.id">
                    <span
                      class="name"
                      :title="serviceItem.name"
                      @click="onCreateTicket(serviceItem)">
                      {{serviceItem.name}}
                    </span>
                    <span class="favorite" @click="onChangeFavorite(serviceItem)">
                      <i
                        :class="['itsm-mobile-icon', serviceItem.favorite ? 'icon-favorite orange': 'icon-favorite-o']">
                      </i>
                    </span>
                  </li>
                </ul>
              </van-list>
            </div>
          </div>
        </div>
      </van-pull-refresh>
      <div v-if="searchFocus">
        <ul class="result-list" v-if="serviceList.searchResultList.length > 0">
          <li
            class="result-item"
            v-for="service in serviceList.searchResultList"
            :key="service.id"
            @click="onCreateTicket(service)">
            <div class="favorite-icon">
              <span @click="onChangeFavorite(service)">
                <i :class="['itsm-mobile-icon', service.favorite ? 'icon-favorite orange': 'icon-favorite-o']"></i>
              </span>
            </div>
            <div class="name" v-html="service.highlightName"></div>
            <div class="category">{{ service.key }}</div>
          </li>
        </ul>
        <div class="no-data" v-else>无匹配服务</div>
      </div>
    </div>
    <div class="go-back-home" @click="$router.push({ name: 'homeDefault' })">
      <i class="itsm-mobile-icon icon-index" />
    </div>
  </div>
</template>

<script lang="ts">
import { ref, Ref, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ITicketService } from '../../typings/ticket'

interface IState {
  searchResultList: Array<ITicketService>,
  favoriteList: Array<ITicketService>,
  latestList: Array<ITicketService>,
  allList: Array<ITicketService>,
  initList: Array<ITicketService>
}
interface LState {
  list: Array<any>
  loading: boolean,
  finished: boolean,
  pagination: {
    page: number,
    totalPage: number,
    count: number
  }
}
export default {
  name: 'Service',
  props: {},
  emits: {},
  setup() {
    const store = useStore()
    const router = useRouter()
    const refreshing = ref(false)
    const searchFocus: Ref<boolean> = ref(false)
    const commonlyLoading: Ref<boolean> = ref(true)
    const allLoading: Ref<boolean> = ref(true)
    const serviceSearchStr: Ref<string> = ref('')
    const serviceList = reactive<IState>({
      searchResultList: [],
      favoriteList: [],
      latestList: [], // 最近一个月使用服务
      allList: [],
      initList: []
    })
    const listState = reactive<LState>({
      list: [],
      loading: false,
      finished: false,
      pagination: {
        page: 1,
        totalPage: 1,
        count: 40
      }
    })
    const onload = () => {
      listState.pagination.page += 1
      listState.finished = listState.pagination.page === listState.pagination.totalPage
      const begin = (listState.pagination.page - 1) * listState.pagination.count
      const end = listState.pagination.page * listState.pagination.count
      const list = serviceList.initList.slice(begin, end)
      serviceList.allList = [...serviceList.allList, ...list]
      listState.loading = false
    }
    const onchange = (str: string): void => {
      if (str) {
        searchFocus.value = true
        const list: Array<any> = []
        const reg = new RegExp(str, 'i')
        serviceList.initList.forEach(item => {
          if (reg.test(item.name) && list.length < 6) {
            const highlightName = item.name.replace(reg, `<span style="color: #3a84ff;">${str}</span>`)
            list.push(Object.assign({}, item, { highlightName }))
          }
        })
        serviceList.searchResultList = list.sort((a: any, b: any) => a.name.length - b.name.length)
      } else {
        searchFocus.value = false
        serviceList.searchResultList = []
      }
    }
    const onCreateTicket = (service: any): void => {
      router.push({
        name: 'createTicket',
        query: {
          serviceId: service.id
        }
      })
    }
    const onChangeFavorite = (service: any): void => {
      store.dispatch('toggleServiceFavorite', {
        id: service.id,
        favorite: !service.favorite
      }).then(res => {
        if (res.result) {
          // 同步所有服务favorite状态
          service.favorite = !service.favorite
          const serviceItem = serviceList.initList.find(item => item.id === service.id)
          serviceItem.favorite = service.favorite
          getService()
        }
      })
    }
    const getService = (): void => {
      commonlyLoading.value = true
      Promise.all([
        store.dispatch('getServiceFavorites'),
        store.dispatch('getRecentFavorites')
      ]).then(res => {
        serviceList.favoriteList = res[0]
        serviceList.latestList = res[1]
      }).catch(e => {
        console.log(e)
      }).finally(() => {
        commonlyLoading.value = false
      })
    }
    const getAllService = async () => {
      allLoading.value = true
      const res = await store.dispatch('getServiceList')
      serviceList.initList = res.sort((a: any, b: any) => b.favorite - a.favorite)
      serviceList.allList = serviceList.initList.slice(listState.pagination.page - 1, listState.pagination.count)
      allLoading.value = false
      refreshing.value = false
      listState.pagination.totalPage = Math.ceil(serviceList.initList.length / 40)
    }
    const onRefresh = (): void => {
      listState.pagination = {
        page: 1,
        totalPage: 1,
        count: 40
      }
      getService()
      getAllService()
    }
    onMounted(() => {
      getService()
      getAllService()
    })
    return {
      serviceSearchStr,
      serviceList,
      searchFocus,
      commonlyLoading,
      refreshing,
      allLoading,
      listState,
      onchange,
      onRefresh,
      onload,
      getService,
      onCreateTicket,
      onChangeFavorite
    }
  }
}
</script>

<style lang="postcss" scoped>
.orange {
  color: #fbb948;
}
.service {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  font-size: 32px;
  .service-search {
    width: 100%;
    padding: 0 10px;
    border-bottom: 4px solid #eee;
    /deep/ .van-search__content {
      background-color: #eff1f5;
    }
  }
  .service-container {
    flex: 1;
    width: 100%;
    overflow: auto;
  }
  .service-content {
    padding: 40px 20px;
    font-size: 32px;
    .serivce-title {
      font-size: 28px;
      color: #a2a4a7;
      font-weight: 400;
      padding: 0 28px;
      i {
        font-size: 36px;
      }
    }
    .service-line {
      border-bottom: 4px solid #eee;
      margin: 10px 20px;
    }
    .container {
      width: 100%;
      padding: 20px;
      .service-list {
        display: grid;
        justify-content: space-evenly;
        grid-template-columns: repeat(auto-fill, 320px);
        grid-gap: 20px;
        li {
          height: 80px;
          font-size: 28px;
          padding: 10px 20px;
          background: #f1f5fa;
          line-height: 60px;
          display: flex;
          .name {
            width: 240px;
            text-align: left;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            word-break: break-all;
          }
          .favorite {
            width: 60px;
            text-align: center;
            font-size: 40px;
          }
        }
      }
    }
  }
  .result-list {
    width: 100%;
    padding: 0px 40px;
    .result-item {
      height: 80px;
      line-height: 80px;
      display: flex;
      .favorite-icon {
        width: 50px;
        margin-right: 10px;
        font-size: 40px;
      }
      .name {
        flex: 1;
      }
      .category {
        color: #e0e0e0;
        width: 100px;
        text-align: right;
      }
    }
  }
  .no-data {
    text-align: center;
    margin: 100px 0;
    font-size: 32px;
  }
}
.go-back-home {
  position: fixed;
  bottom: 250px;
  right: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: rgba(105,157,244,0.8);
  i {
    color: #ffffff;
    font-size: 40px;
  }
}
</style>
