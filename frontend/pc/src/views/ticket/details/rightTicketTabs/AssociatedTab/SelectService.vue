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
  <div class="bk-build-bill">
    <bk-form
      :label-width="200"
      form-type="vertical"
      :model="formData"
      ref="billForm"
      :class="{ 'inline-form': isGetField }"
    >
      <bk-form-item
        :label="$t(`m.manageCommon['服务目录']`)"
        class="inline-item"
      >
        <common-cascade
          style="width: 100%"
          ref="commoncascader"
          v-model="formData.cascadeCheck"
          :options="cascadeList"
          :iscollect-two="customId !== 'all'"
          :isshow-number="customId !== 'all'"
          :isactive="true"
          :options-favorites="optionsFavorites"
          @change="handleChange"
          @collect="collect"
          @cancelcollect="cancelcollect"
        >
        </common-cascade>
      </bk-form-item>
      <bk-form-item
        :label="$t(`m.manageCommon['服务']`)"
        class="inline-item"
      >
        <bk-select
          v-model="formData.service_id"
          :clearable="false"
          :loading="isSecondLoading"
          searchable
          :font-size="'medium'"
          @selected="selectedService"
        >
          <bk-option
            v-for="option in billList"
            :key="option.id"
            :id="option.id"
            :name="option.name"
            :disabled="option.disabled"
          >
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item :label="$t(`m.manageCommon['服务说明']`)">
        <p class="bk-sevice-desc">{{ billListInfo || "--" }}</p>
      </bk-form-item>
    </bk-form>
  </div>
</template>

<script>
  import commonCascade from '@/views/commonComponent/commonCascade';
  import { errorHandler } from '@/utils/errorHandler';

  export default {
    name: 'SelectService',
    components: {
      commonCascade,
    },
    props: {
      customId: {
        type: String,
        default() {
          return '';
        },
      },
      isGetField: {
        type: Boolean,
        default() {
          return false;
        },
      },
    },
    data() {
      return {
        isSecondLoading: false,
        formData: {
          cascadeCheck: [],
          cascadeId: '',
          service_id: '',
          canAgency: false,
          key: '',
        },
        cascadeList: [],
        billList: [],
        billListInfo: '',
        // 收藏
        optionsFavorites: [],
      };
    },
    watch: {
      'formData.service_id'() {
        if (this.isGetField) {
          this.$emit('getFieldList');
        }
      },
    },
    mounted() {
      this.getBillList();
      // 全局视图没有收藏功能
      if (this.customId !== 'all') {
        this.getfavorites();
      }
    },
    methods: {
      // 获取列表数据
      getBillList() {
        const params = {
          key: this.customId === 'all' ? 'global' : this.customId,
          show_deleted: false,
          project_key: this.$store.state.project.id,
        };
        this.$store
          .dispatch('serviceCatalog/getTreeData', params)
          .then((res) => {
            this.cascadeList = res.data.length
              ? res.data[0].children
              : [];
            this.$refs.commoncascader.settextinfo(
              [this.cascadeList[0]],
              'give_default'
            );
          })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      getServiceList() {
        if (!this.formData.cascadeId) {
          return;
        }
        const params = {
          catalog_id: this.formData.cascadeId,
          service_key:
            this.customId === 'all' ? 'globalview' : this.customId,
          is_valid: 1,
          project_key: this.$store.state.project.id,
        };
        this.isSecondLoading = true;
        this.$store
          .dispatch('catalogService/getServices', params)
          .then((res) => {
            this.billList = res.data;
            this.billList.forEach((item) => {
              this.$set(item, 'disabled', !item.is_valid);
            });
            // 默认初始化选中一个
            if (this.billList.length) {
              this.formData.service_id = this.billList[0].id;
              this.billListInfo = this.billList[0].desc;
              this.formData.canAgency =                            this.billList[0].can_ticket_agency;
              this.formData.key = this.billList[0].key;
            } else {
              this.formData.service_id = '';
              this.billListInfo = '';
              this.formData.canAgency = '';
              this.formData.key = '';
            }
          })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isSecondLoading = false;
          });
      },
      handleChange(value) {
        this.formData.cascadeId = value[value.length - 1].id;
        this.billListInfo = '';
        this.getServiceList();
      },
      selectedService(value) {
        const selectedItem = this.billList.filter(item => item.id === value)[0];
        this.billListInfo = selectedItem.desc;
        this.formData.canAgency = selectedItem.can_ticket_agency;
        this.formData.key = selectedItem.key;
      },
      // 收藏
      getfavorites() {
        if (!this.customId) {
          return;
        }
        const params = {
          service: this.customId,
        };
        this.$store
          .dispatch('service/getfavorites', params)
          .then((res) => {
            if (res.data.length) {
              this.optionsFavorites = res.data[0].data.filter(item => item.is_deleted === false);
            } else {
              this.optionsFavorites = [];
            }
          })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      collect(favoriteslist) {
        const favorite = {};
        favorite.service = this.customId;
        favorite.data = favoriteslist;
        // 更新收藏分类
        this.$store
          .dispatch('service/updatefavorites', favorite)
          .then(() => {
            this.$bkMessage({
              message: this.$t('m.manageCommon["收藏成功"]'),
              theme: 'success',
            });
            this.optionsFavorites = favoriteslist;
          })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      cancelcollect(favoriteslist) {
        const favorite = {};
        favorite.service = this.customId;
        favorite.data = favoriteslist;
        this.$store
          .dispatch('service/updatefavorites', favorite)
          .then(() => {
            this.$bkMessage({
              message: this.$t('m.manageCommon["取消成功"]'),
              theme: 'success',
            });
            this.optionsFavorites = favoriteslist;
          })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
    },
  };
</script>

<style lang="scss" scoped>
.bk-sevice-desc {
    line-height: 30px;
    color: #63656e;
    font-size: 12px;
}
.inline-form {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;

    .inline-item {
        width: 49%;
        margin-top: 0 !important;
    }
}
</style>
