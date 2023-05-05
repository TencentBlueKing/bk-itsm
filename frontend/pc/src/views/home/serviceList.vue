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
  <div>
    <div class="service-list-section">
      <div class="tab-wrapper">
        <span class="type-item active">{{ $t(`m.common['常用服务']`) }}</span>
      </div>
      <div class="recently-content" v-bkloading="{ isLoading: loading }">
        <ul class="list-wrapper" v-if="latestList.length > 0">
          <li
            v-for="service in latestList"
            :key="service.id"
            class="service-item"
            @click="onSelectService(service)">
            <div class="service-name" v-bk-overflow-tips>{{ service.name }}</div>
            <i
              :class="['bk-itsm-icon', 'collect-icon', service.favorite ? 'icon-favorite' : 'icon-rate']"
              v-bk-tooltips="{
                content: service.favorite ? $t(`m.common['取消收藏']`) : $t(`m.common['添加收藏']`),
                placement: 'top',
                delay: [300, 0]
              }"
              @click.stop="onCollectClick(service)">
            </i>
          </li>
        </ul>
        <no-data v-else font-size="12" style="padding: 40px 0;" :text="$t(`m['您当前似乎还没有使用过任何服务，您可以在下方全部服务中选择您所需要的服务进行提单']`)"></no-data>
        <!-- <div class="recently-empty" >
          <div class="operation-wrapper">
            <div class="operate">
              <div class="icon-area" @click="onTabChange('all')">
                <i class="bk-itsm-icon icon-arrow-rect"></i>
              </div>
              <div class="text" @click="onTabChange('all')">{{ $t(`m.common['查看服务']`) }}</div>
            </div>
            <div class="operate">
              <div class="icon-area" @click="onCreateTicket">
                <i class="bk-itsm-icon icon-pen-rect"></i>
              </div>
              <div class="text" @click="onCreateTicket">{{ $t(`m.managePage['提单']`) }}</div>
            </div>
          </div>
        </div> -->
      </div>
    </div>
    <div class="service-list-section" style="margin-top: 20px">
      <div class="tab-wrapper">
        <span class="type-item active">{{ $t(`m.common['全部服务']`) }}</span>
      </div>
      <div class="search-input-wrapper" v-bk-clickoutside="handleClickoutside">
        <bk-input
          class="search-input"
          right-icon="bk-icon icon-search"
          :placeholder="$t(`m.common['请输入服务名称，快速提单']`)"
          :clearable="true"
          @focus="searchHandler"
          @change="searchHandler">
        </bk-input>
        <div class="search-result-content" v-if="isSearchResultShow">
          <ul class="result-list" v-if="searchResultList.length > 0">
            <li class="result-item" v-for="service in searchResultList" :key="service.id" @click="onSelectService(service)">
              <i
                :class="['bk-itsm-icon', service.favorite ? 'icon-favorite' : 'icon-rate']"
                v-bk-tooltips="{
                  content: service.favorite ? $t(`m.common['取消收藏']`) : $t(`m.common['添加收藏']`),
                  placement: 'top',
                  delay: [300, 0]
                }"
                @click.stop="onCollectClick(service)">
              </i>
              <div class="name" v-html="service.highlightName"></div>
              <div class="category">{{ service.serviceTypeName }}</div>
            </li>
          </ul>
          <div class="no-data" v-else>{{ $t(`m.common['无匹配服务']`) }}</div>
        </div>
      </div>
      <div class="service-content" v-bkloading="{ isLoading: loading }">
        <template v-if="allList.length > 0">
          <ul class="list-wrapper">
            <li
              v-for="service in activeFold ? allList.slice(0, 16) : allList"
              :key="service.id"
              class="service-item"
              @click="onSelectService(service)">
              <div class="service-name" v-bk-overflow-tips>{{ service.name }}</div>
              <i
                :class="['bk-itsm-icon', 'collect-icon', service.favorite ? 'icon-favorite' : 'icon-rate']"
                v-bk-tooltips="{
                  content: service.favorite ? $t(`m.common['取消收藏']`) : $t(`m.common['添加收藏']`),
                  placement: 'top',
                  delay: [300, 0]
                }"
                @click.stop="onCollectClick(service)">
              </i>
            </li>
          </ul>
          <div class="show-more" v-if="allList.length > 16" @click="toggleFold">
            <template v-if="activeFold">
              <span>{{ $t(`m['更多']`) }}</span>
              <i class="bk-icon icon-angle-down"></i>
            </template>
            <template v-else>
              <span>{{ $t(`m['收起']`) }}</span>
              <i class="bk-icon icon-angle-up"></i>
            </template>
          </div>
        </template>
        <div class="service-empty" v-else>
          <i class="bk-icon icon-empty"></i>
          <p class="text">
            <span>{{ $t(`m.common['暂无服务，']`) }}</span>
            <router-link :to="{ name: 'projectServiceList', query: { project_id: $store.state.project.id } }">{{ $t(`m.taskTemplate['立即创建']`) }}</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
  import debounce from 'throttle-debounce/debounce';
  import bus from '@/utils/bus.js';
  import { errorHandler } from '@/utils/errorHandler';
  import NoData from '../../components/common/NoData.vue';

  export default {
    name: 'ServiceList',
    components: {
      NoData,
    },
    data() {
      return {
        type: 'latest',
        latestList: [],
        allList: [],
        serviceClassify: [],
        activeClassify: '',
        activeFold: true,
        isSearchResultShow: false,
        searchResultList: [],
        latestLoading: false,
        collectedLoading: false,
        allLoading: false,
        serviceClassfyLoading: false,
      };
    },
    computed: {
      loading() {
        return this.latestLoading || this.allLoading || this.serviceClassfyLoading;
      },
    },
    created() {
      this.getLatestService();
      this.getAllService();
      this.getServiceClassify();
      this.searchHandler = debounce(500, val => {
        this.onServiceSearch(val);
      });
    },
    methods: {
      // 获取最近使用的服务
      getLatestService() {
        this.latestLoading = true;
        Promise.all([
          this.$store.dispatch('service/getServiceFavorites'),
          this.$store.dispatch('service/getRecentlyFavorite'),
        ]).then(data => {
          const favoriteList = data[0].data;
          const recentlyList = data[1].data.filter(item => favoriteList.findIndex(fItem => fItem.id === item.id) === -1);
          const len = favoriteList.length;
          this.latestList = len > 16 ? favoriteList : favoriteList.concat(recentlyList.slice(0, 16 - len));
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.latestLoading = false;
          });
      },
      // 获取所有服务
      getAllService() {
        this.allLoading = true;
        this.$store.dispatch('service/getServiceList').then(resp => {
          if (resp.result) {
            this.allList = resp.data;
            this.allList.sort((a, b) => b.favorite - a.favorite);
          }
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.allLoading = false;
          });
      },
      // 获取服务分类信息
      getServiceClassify() {
        this.serviceClassfyLoading = true;
        return this.$store.dispatch('getCustom').then((res) => {
          this.serviceClassify = res.data;
        })
          .catch(res => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.serviceClassfyLoading = false;
          });
      },
      onTabChange(type) {
        this.type = type;
        if (type === 'latest') {
          this.getLatestService();
        } else {
          this.getAllService();
        }
      },
      onCreateTicket() {
        bus.$emit('openCreateTicketDialog');
      },
      handleClickoutside() {
        this.isSearchResultShow = false;
      },
      onServiceSearch(val) {
        this.isSearchResultShow = true;

        if (val) {
          const list = [];
          const reg = new RegExp(val, 'i');
          this.allList.forEach(item => {
            if (reg.test(item.name) && list.length < 6) {
              const highlightName = item.name.replace(reg, `<span style="color: #3a84ff;">${val}</span>`);
              const serviceTypeName = this.serviceClassify.find(classify => classify.key === item.key).name;
              list.push(Object.assign({}, item, { highlightName, serviceTypeName }));
            }
          });
          this.searchResultList = list.sort((a, b) => a.name.length - b.name.length);
        } else {
          this.searchResultList = [];
          this.isSearchResultShow = false;
        }
      },
      onCollectClick(service) {
        const curStatus = service.favorite;
        this.$store.dispatch('service/toggleServiceFavorite', {
          id: service.id,
          favorite: !curStatus,
        }).then((res) => {
          if (res.result) {
            const serviceItem = this.allList.find(item => item.id === service.id);
            service.favorite = !curStatus; // 修改当前数据的收藏状态
            this.$set(serviceItem, 'favorite', !curStatus); // 修改当前数据对应的源数据收藏状态
          }
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      onSelectService(service) {
        const { id } = service;
        const routerObj = this.$router.resolve({
          name: 'CreateTicket',
          query: {
            service_id: id,
            // project_id: service.project_key, // 首页提单不需要项目ID
            from: 'Home',
          },
        });
        window.open(routerObj.href, '_blank');
      },
      toggleFold() {
        this.activeFold = !this.activeFold;
      },
    },
  };
</script>
<style lang="scss" scoped>
    @import '../../scss/mixins/scroller.scss';
    .service-list-section {
        position: relative;
        padding: 20px;
        background: #ffffff;
        box-shadow: 0px 2px 4px 0px rgba(0, 0, 0, 0.1);
    }
    .tab-wrapper {
        margin-bottom: 10px;
        .type-item {
            color: #9a9ba5;
            font-size: 16px;
            cursor: pointer;
            &.active {
                color: #313238;
            }
            &:hover {
                color: #313238;
            }
        }
    }
    .icon-favorite {
        color: #ffb848;
    }
    .icon-rate {
        color: #979ba5;
    }
    .search-input-wrapper {
        position: absolute;
        top: 20px;
        right: 20px;
        .search-input {
            width: 480px;
        }
        .search-result-content {
            position: absolute;
            top: 40px;
            left: 0;
            width: 100%;
            background: #ffffff;
            border: 1px solid #dcdee5;
            border-radius: 2px;
            box-shadow: 0px 2px 6px 0px rgba(0, 0, 0, 0.1);
            z-index: 2;
        }
        .no-data {
            line-height: 32px;
            font-size: 12px;
            color: #63656e;
            text-align: center;
        }
    }
    .result-list {
        li {
            position: relative;
            display: flex;
            align-items: center;
            height: 32px;
            line-height: 32px;
            font-size: 12px;
            cursor: pointer;
            &:hover {
                background: #eaf3ff;
                .icon-rate {
                    display: inline-block;
                }
            }
        }
        .name {
            padding-left: 24px;
            width: 54%;
            color: #63656e;
            white-space: nowrap;
            text-overflow: ellipsis;
            overflow: hidden;
        }
        .bk-itsm-icon {
            position: absolute;
            top: 10px;
            left: 4px;
            font-size: 16px;
        }
        .icon-rate {
            display: none;
        }
        .category {
            padding: 0 10px;
            width: 46%;
            color: #c4c6cc;
            text-align: right;
            white-space: nowrap;
            text-overflow: ellipsis;
            overflow: hidden;
        }
    }
    /deep/ .bk-tab-section {
        padding: 16px 0 0;
    }
    .recently-content {
        // padding-top: 30px;
        min-height: 120px;
        max-height: 240px;
        overflow-y: auto;
        @include scroller;
    }
    .service-content {
        position: relative;
        padding-top: 10px;
        min-height: 276px;
        .show-more {
            position: absolute;
            bottom: -20px;
            left: 50%;
            transform: translateX(-40px);
            display: flex;
            justify-content: center;
            align-items: center;
            width: 80px;
            height: 20px;
            font-size: 12px;
            color: #fff;
            background: #c4c6cc;
            border-radius: 10px 10px 0px 0px;
            cursor: pointer;
            i {
                font-size: 16px;
            }
            &:hover {
                background: #3a84ff;
            }
        }
    }
    .service-item {
        float: left;
        position: relative;
        margin-right: 29px;
        margin-bottom: 16px;
        color: #63656e;
        background: #f3f6fb;
        border-radius: 2px;
        cursor: pointer;
        &:nth-of-type(4n) {
            margin-right: 0;
        }
        &:hover {
            background: #e1ecff;
            color: #3a84ff;
            .collect-icon.icon-rate{
                display: inline-block;
            }
        }
        .service-name {
            padding: 0 40px 0 16px;
            width: 292px;
            height: 40px;
            line-height: 40px;
            font-size: 12px;
            white-space: nowrap;
            text-overflow: ellipsis;
            overflow: hidden;
        }
        .collect-icon {
            position: absolute;
            right: 20px;
            top: 12px;
            font-size: 16px;
            &.icon-favorite {
                color: #ffb848;
            }
            &.icon-rate {
                display: none;
                color: #979ba5;
            }
        }
    }
    .list-wrapper {
        overflow: hidden;
        padding-top: 20px;
    }
    .recently-empty {
        color: #63656e;
        font-size: 14px;
        text-align: center;
        .operation-wrapper {
            display: flex;
            justify-content: center;
            margin-top: 40px;
            p {
                margin-top: 8px;
            }
            .operate {
                margin: 0 80px;
                &:hover {
                    .icon-area {
                        background: #e1ecff;
                    }
                    .text {
                        color: #3a84ff;
                    }
                }
                .icon-area {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 50px;
                    height: 50px;
                    border-radius: 50%;
                    background: #f0f1f5;
                    cursor: pointer;
                    &:hover {
                        background: #e1ecff;
                    }
                }
                i {
                    font-size: 14px;
                    background: #ffffff;
                }
                .text {
                    margin-top: 8px;
                    cursor: pointer;
                    &:hover {
                        color: #3a84ff;
                    }
                }
            }
        }
    }
    .service-empty {
        margin-top: 60px;
        text-align: center;
        i {
            font-size: 65px;
            color: #c3cdd7;
        }
        .text {
            font-size: 12px;
            color: #63656e;
            a {
                color: #3a84ff;
            }
        }
    }
</style>
