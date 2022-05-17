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
    data-test-id="service_dialog_serviceChoiceDialog"
    render-directive="if"
    ext-cls="choose-service-template-dialog"
    :width="980"
    :value="isShow"
    :auto-close="false"
    :show-footer="false"
    @value-change="onDialogClose">
    <div class="choose-service-template">
      <h3 class="dialog-header">
        <span class="dialog-name">{{ createInfo.name }}</span>
        <bk-input
          v-if="createWay === 'created'"
          class="search-input"
          right-icon="bk-icon icon-search"
          :placeholder="$t(`m.common['请输入服务名称']`)"
          :clearable="true"
          @change="searchHandler">
        </bk-input>
      </h3>
      <div class="dialog-body" v-bkloading="{ isLoading: loading }">
        <ul class="template-list" v-if="templateList.length">
          <li class="template-item" v-for="(template, index) in templateList"
            :key="index"
            :data-test-id="`serviceTemplateList-li-${template.id}`"
            @click="onTemplateClick(template)">
            <p class="template-name" v-html="template.name"></p>
            <p class="template-time" v-if="createWay === 'recom'">{{ template.time }}</p>
          </li>
        </ul>
        <div class="service-empty" v-else>
          <div>
            <i class="bk-icon icon-empty"></i>
            <p class="text">
              <span v-if="!searchModel">暂无服务</span>
              <span v-else>{{ $t(`m.common['无匹配服务']`) }}</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  </bk-dialog>
</template>

<script>
  import { errorHandler } from '../../../utils/errorHandler';

  export default {
    name: 'ChooseServiceTemplateDialog',
    components: {},
    props: {
      isShow: Boolean,
      createInfo: Object,
      serviceId: [String, Number],
    },
    data() {
      return {
        loading: false,
        searchModel: false,
        searchResultList: [],
        recomTemplateList: [],
        createdTemplateList: [],
      };
    },
    computed: {
      createWay() {
        return this.createInfo.key;
      },
      templateList() {
        if (this.searchModel) {
          return this.searchResultList;
        }
        return this.createWay === 'recom' ? this.recomTemplateList : this.createdTemplateList;
      },
    },
    watch: {
      isShow(val) {
        if (!val) {
          return false;
        }
        if (this.createWay === 'recom') {
          this.getRecomService();
        } else {
          this.getAllService();
        }
      },
    },
    methods: {
      // 获取所有服务
      getAllService() {
        this.loading = true;
        this.$store.dispatch('service/getServiceList', { no_page: true }).then((resp) => {
          if (resp.result) {
            this.createdTemplateList = resp.data;
          }
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.loading = false;
          });
      },
      // 获取推荐服务（原基础模型）列表
      getRecomService() {
        this.loading = true;
        this.$store.dispatch('basicModule/get_tables', { no_page: true }).then((res) => {
          this.recomTemplateList = res.data;
        }, (res) => {
          errorHandler(res, this);
        })
          .finally(() => {
            this.loading = false;
          });
      },
      searchHandler(val) {
        this.searchModel = val !== '';
        const reg = new RegExp(`(${val})`, 'ig');
        this.searchResultList = this.createdTemplateList
          .filter(item => reg.test(item.name))
          .map(item => ({
            ...item,
            name: item.name.replace(reg, '<span style="color: #3a84ff;">$1</span>'),
          }));
      },
      onTemplateClick(item) {
        let params;
        let actionName;
        if (this.createWay === 'recom') {
          params = {
            id: this.serviceId,
            table_id: item.id,
          };
          actionName = 'importFromTemplate';
        } else {
          params = {
            id: this.serviceId,
            service_id: item.id,
          };
          actionName = 'importFromService';
        }
        this.updateCurrServiceForm(params, actionName);
      },
      updateCurrServiceForm(params, actionName) {
        this.loading = true;
        this.$store.dispatch(`service/${actionName}`, params).then(() => {
          this.$bkMessage({
            message: this.$t('m.systemConfig["更新成功"]'),
            theme: 'success',
          });
          this.$emit('update:isShow', false);
          this.$emit('updateServiceSource', actionName === 'importFromTemplate' ? 'template' : 'service');
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.loading = false;
          });
      },
      onDialogClose(val) {
        this.$emit('update:isShow', val);
      },
    },
  };
</script>
<style lang='scss' scoped>
@import '~@/scss/mixins/ellipsis.scss';
@import '~@/scss/mixins/scroller.scss';
.choose-service-template-dialog {
    .choose-service-template {
        position: relative;
        min-height: 200px;
        .dialog-header {
            display: flex;
            justify-content: space-between;
            margin: 0;
            font-weight: normal;
            .dialog-name {
                font-size: 20px;
                color: #313238;
            }
            .search-input {
                width: 356px;
            }
        }
        .dialog-body {
            height: 498px;
            overflow: auto;
            @include scroller;
            .template-list {
                display: flex;
                flex-wrap: wrap;
                .template-item {
                    margin-top: 20px;
                    padding: 12px 16px;
                    width: calc((100% - 60px) / 3);
                    background: #f3f6fb;
                    border-radius: 2px;
                    cursor: pointer;
                    &:hover {
                        background: #e1ecff;
                    }
                    &:not(:nth-child(3n)) {
                        margin-right: 30px;
                    }
                    .template-name {
                        @include ellipsis(100%);
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
        }
    }
}
</style>
