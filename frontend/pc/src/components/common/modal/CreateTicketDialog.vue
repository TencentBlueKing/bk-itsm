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
  <bk-dialog
    data-test-id="createTicket-dialog-ontext"
    render-directive="if"
    ext-cls="create-ticket-dialog"
    :width="980"
    :value="isShow"
    :show-footer="false"
    :mask-close="false"
    :auto-close="false"
    :close-icon="true"
    @cancel="onCloseDialog">
    <div class="select-service">
      <div class="tab-wrapper">
        <template>
          <span class="type-item active">{{ $t(`m.managePage['提单']`) }}</span>
        </template>
      </div>
      <div class="search-input-wrapper">
        <bk-input
          data-test-id="createTicket-input-search"
          class="search-input"
          right-icon="bk-icon icon-search"
          :placeholder="$t(`m.common['请输入服务名称']`)"
          :clearable="true"
          @change="searchHandler">
        </bk-input>
      </div>
      <div style="height: calc(100% - 40px);" v-bkloading="{ isLoading: loading }">
        <template v-if="!loading">
          <bk-tab :active="activeClassify" type="unborder-card" @tab-change="handleTabChange">
            <bk-tab-panel
              v-for="(group, index) in serviceList"
              v-bind="group"
              :key="index">
              <template v-slot:label>
                <i class="panel-icon bk-icon icon-cog-shape"></i>
                <span class="panel-name">{{ group.label }}</span>
                <span class="panel-count" v-if="searchModel">{{ listNum[group.name] }}</span>
                <i :class="[group.name === activeName ? 'active-line' : '']"></i>
              </template>
              <ul v-if="group.data.length > 0" class="service-content">
                <li
                  v-for="service in group.data"
                  :class="['service-item', { active: selectedService && selectedService.id === service.id }]"
                  :key="service.id"
                  @click="onSelectService(service)">
                  <div
                    v-html="service.name"
                    v-bk-tooltips="{
                      allowHtml: true,
                      placement: 'top',
                      boundary: 'window',
                      extCls: 'service-title-desc-tooltip',
                      width: 354,
                      delay: [500, 0],
                      content: `#serviceTips_${service.id}`
                    }"
                    class="service-name">
                  </div>
                  <div :id="`serviceTips_${service.id}`" class="service-tooltip-content"><h4 v-html="service.name"></h4><pre>{{service.desc}}</pre></div>
                  <div class="active-tag">
                    <i class="bk-itsm-icon icon-itsm-icon-fill-fit"></i>
                  </div>
                  <i
                    v-bk-tooltips="{
                      placement: 'top',
                      boundary: 'window',
                      extCls: 'favorite-desc-tooltip',
                      content: service.favorite ? $t(`m.common['取消收藏']`) : $t(`m.common['添加收藏']`),
                      delay: [300, 0]
                    }"
                    data-test-id="createTicket-i-favorite"
                    :class="['bk-itsm-icon', 'collect-icon', service.favorite ? 'icon-favorite' : 'icon-rate']"
                    @click.stop="onCollectClick(service)">
                  </i>
                </li>
              </ul>
              <div class="service-empty" v-else>
                <div>
                  <i class="bk-icon icon-empty"></i>
                  <p class="text">
                    <template v-if="!searchModel">
                      <span>{{ $t(`m.common['暂无服务，']`) }}</span>
                      <router-link :to="{ name: 'projectServiceList', query: { project_id: $store.state.project.id } }" @click.native="onCloseDialog">{{ $t(`m.taskTemplate['立即创建']`) }}</router-link>
                    </template>
                    <span v-else>{{ $t(`m.common['无匹配服务']`) }}</span>
                  </p>
                </div>
              </div>
            </bk-tab-panel>
          </bk-tab>
        </template>
      </div>
    </div>
  </bk-dialog>
</template>
<script>
  import debounce from 'throttle-debounce/debounce';
  import { errorHandler } from '../../../utils/errorHandler';

  export default {
    name: 'CreateTicketDialog',
    props: {
      isShow: Boolean,
    },
    data() {
      return {
        allList: [],
        latestList: [],
        searchList: [],
        serviceClassify: [],
        activeClassify: '',
        searchModel: false,
        selectedService: null,
        latestLoading: false,
        allLoading: false,
        activeName: 'requset',
      };
    },
    computed: {
      loading() {
        return this.latestLoading || this.collectedLoading || this.allLoading;
      },
      serviceList() {
        const data = this.searchModel ? this.searchList : this.allList;
        const list = this.serviceClassify.map(item => ({
          name: item.key,
          label: item.name,
          data: [],
        }));
        data.forEach((service) => {
          const group = list.find(item => item.name === service.key);
          group.data.push(service);
        });
        list.forEach(service => {
          service.data.sort((a, b) => b.favorite - a.favorite);
        });
        return list;
      },
      listNum() {
        const serviceCount = {};
        this.serviceList.forEach((item) => {
          serviceCount[item.name] = item.data.length;
        });
        return serviceCount;
      },
    },
    watch: {
      isShow(val) {
        if (val) {
          this.getAllService();
          this.getServiceClassify();
        }
      },
    },
    created() {
      this.searchHandler = debounce(500, (val) => {
        this.onServiceSearch(val);
      });
    },
    methods: {
      // 获取所有服务
      getAllService() {
        this.allLoading = true;
        this.$store.dispatch('service/getServiceList', { no_page: true }).then((resp) => {
          if (resp.result) {
            this.allList = resp.data;
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
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.serviceClassfyLoading = false;
          });
      },
      onServiceSearch(val) {
        if (val) {
          const list = [];
          const reg = new RegExp(val, 'i');
          this.allList.forEach((item) => {
            if (reg.test(item.name)) {
              const name = item.name.replace(reg, `<span style="color: #3a84ff;">${val}</span>`);
              list.push(Object.assign({}, item, { name }));
            }
          });
          this.searchModel = true;
          this.searchList = list;
        } else {
          this.searchModel = false;
          this.searchList = [];
        }
      },
      // 收藏/取消收藏
      onCollectClick(service) {
        this.$store.dispatch('service/toggleServiceFavorite', {
          id: service.id,
          favorite: !service.favorite,
        }).then((res) => {
          if (res.result) {
            this.$set(service, 'favorite', !service.favorite);
          }
          this.$bkMessage({
            message: service.favorite ? this.$t('m.manageCommon[\'收藏成功\']') : this.$t('m.manageCommon[\'取消成功\']'),
            theme: 'success',
            ellipsisLine: 0,
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 点击服务
      onSelectService(service) {
        const { id, key } = service;
        this.onCloseDialog();
        this.$router.push({
          name: 'CreateTicket',
          query: {
            service_id: id,
            key,
            project_id: this.$route.query.project_id,
            from: this.$route.name,
          },
        });
      },
      handleTabChange(name) {
        this.activeName = name;
      },
      onCloseDialog() {
        this.$emit('update:isShow', false);
        this.selectedService = null;
        this.searchList = [];
        this.searchModel = false;
      },
    },
  };
</script>
<style lang="scss" scoped>
    @import '../../../scss/mixins/scroller.scss';
    .active-line {
        display: inline-block;
        position: absolute;
        height: 2px;
        width: 100%;
        background-color: #3a84ff;
        top: 48px;
        left: 0;
    }
    .select-service {
        position: relative;
        height: 498px;
    }
    .tab-wrapper {
        height: 40px;
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
    .search-input-wrapper {
        position: absolute;
        top: -5px;
        right: 8px;
        .search-input {
            width: 400px;
            background-color: #ffb848;
        }
    }
    .panel-count {
        padding: 0 4px;
        background-color: #f5f7fa;
    }
    /deep/ .bk-form-input {
        border: 0px;
        border-bottom: 1px solid  #9a9ba5;
        border-radius: 0;
    }
    /deep/.search-result {
        li {
            display: flex;
            justify-content: flex-end;
            padding: 0 10px;
            height: 32px;
            line-height: 32px;
            font-size: 12px;
            cursor: pointer;
            &:hover {
                background: #eaf3ff;
            }
        }
        .service-name {
            width: 190px;
            color: #63656e;
            white-space: nowrap;
            text-overflow: ellipsis;
            overflow: hidden;
        }
        .service-classify {
            width: 190px;
            color: #979ba5;
            text-align: right;
            white-space: nowrap;
            text-overflow: ellipsis;
            overflow: hidden;
        }
    }
    /deep/ .bk-tab-section {
        padding: 16px 0 0;
    }
    .service-content {
        padding-top: 20px;
        height: 400px;
        overflow: auto;
        @include scroller;
        .service-item {
            float: left;
            position: relative;
            margin-right: 30px;
            margin-bottom: 10px;
            color: #63656e;
            background: #f3f6fb;
            border-radius: 2px;
            cursor: pointer;
            &:nth-of-type(3n) {
                margin-right: 0;
            }
            &:hover {
                color: #3a84ff;
                background: #e1ecff;
                .collect-icon.icon-rate{
                    display: inline-block;
                }
            }
            &.active {
                background: #e1ecff;
                color: #3a84ff;
                .active-tag {
                    display: inline-block;
                }
            }
            .service-name {
                padding: 0 40px 0 16px;
                width: 288px;
                height: 40px;
                line-height: 40px;
                font-size: 12px;
                white-space: nowrap;
                text-overflow: ellipsis;
                overflow: hidden;
            }
            .active-tag {
                display: none;
                position: absolute;
                bottom: 0;
                right: 0;
                width: 0;
                height: 0;
                border-style: solid;
                border-width: 0 0 29px 33px;
                border-color: transparent transparent #007bff transparent;
                .bk-itsm-icon {
                    position: absolute;
                    right: 0;
                    top: 8px;
                    color: #ffffff;
                    font-size: 20px;
                }
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
    }
    .service-empty {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 400px;
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
<style lang="scss">
    .search-service-popover {
        width: 400px;
        .tippy-tooltip {
            padding: 0;
            max-height: 192px; // 最多显示6条
            background: #ffffff;
            border: 1px solid #dcdee5;
            border-radius: 2px;
            box-shadow: none;
        }
    }
    .create-ticket-dialog {
        &.bk-dialog-wrapper .bk-dialog-tool {
            min-height: 16px;
            height: calc(100% - 40px);
            .bk-dialog-close {
                top: 20px;
            }
        }
    }
    .service-title-desc-tooltip {
        font-size: 12px;
        h4 {
            margin: 7px 0 10px;
            font-weight: bold;
            line-height: 1;
        }
        p {
            margin: 0 0 7px;
        }
    }
    .favorite-desc-tooltip, .service-title-desc-tooltip {
        /deep/ .tippy-tooltip .tippy-arrow {
            bottom: -8px;
        }
    }
</style>
