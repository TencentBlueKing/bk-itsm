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
  <div v-if="item.showFeild">
    <bk-form-item :label="item.name" :required="item.validate_type === 'REQUIRE'" :desc="item.tips" desc-type="icon">
      <bk-select searchable
        v-model="firstInfo"
        :font-size="'medium'"
        :class="{ 'bk-form-two': firstShow }"
        :disabled="(item.is_readonly && !isCurrent) || disabled"
        :placeholder="item.choice[0] ? item.choice[0].desc : firstPlace"
        @selected="itemSelect">
        <bk-option v-for="option in item.choice"
          :key="option.key"
          :id="option.key"
          :name="option.name">
        </bk-option>
      </bk-select>
      <template v-if="firstShow">
        <bk-select searchable
          v-model="secondInfo"
          :class="{ 'bk-form-two-other': firstShow }"
          :disabled="(item.is_readonly && !isCurrent) || disabled"
          :font-size="'medium'"
          :placeholder="firstList[0] ? firstList[0].desc : secondPlace"
          @selected="changeFrist">
          <bk-option v-for="option in firstList"
            :key="option.key"
            :id="option.key"
            :name="option.name">
          </bk-option>
        </bk-select>
      </template>
      <!-- <div class="bk-form-content">
                <bk-selector
                    style="position: relative;"
                    :class="{'bk-form-two': firstShow}"
                    :list="item.choice"
                    :selected.sync="firstInfo"
                    :setting-key="'key'"
                    @item-selected="itemSelect"
                    :searchable="true"
                    :disabled="item.is_readonly&&!isCurrent"
                    :placeholder="item.choice[0] ? item.choice[0].desc : firstPlace">
                </bk-selector>
                <bk-selector
                    v-if="firstShow"
                    style="position: relative;"
                    :class="{'bk-form-two-other': firstShow}"
                    :list="firstList"
                    :selected.sync="secondInfo"
                    :setting-key="'key'"
                    :disabled="item.is_readonly&&!isCurrent"
                    @item-selected="changeFrist"
                    :searchable="true"
                    :placeholder="firstList[0] ? firstList[0].desc : secondPlace">
                </bk-selector>
            </div> -->
    </bk-form-item>
    <template v-if="item.checkValue">
      <p class="bk-task-error" v-if="item.checkMessage">{{ item.checkMessage }}</p>
      <p class="bk-task-error" v-else>{{ item.name }}{{$t('m.newCommon["为必填项！"]')}}</p>
    </template>
  </div>
</template>

<script>
  export default {
    name: 'CASCADE',
    props: {
      item: {
        type: Object,
        required: true,
        default: () => {},
      },
      fields: {
        type: Array,
        required: true,
        default: () => [],
      },
      isCurrent: {
        type: Boolean,
        default: false,
      },
      disabled: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        // selectList: []
        firstShow: false,
        firstInfo: this.item.val,
        firstList: [],
        secondInfo: '',
        firstPlace: this.$t('m.newCommon["请选择所属的厅委办"]'),
        secondPlace: this.$t('m.newCommon["请选择所属业务"]'),
        clickChange: false,
      };
    },
    computed: {
      changeFields() {
        return this.fields;
      },
    },
    watch: {
      'item.val'() {
        this.changeInfo();
      },
    },
    mounted() {
      this.changeInfo();
    },
    methods: {
      itemSelect(val) {
        const itemInfo = this.item.choice.filter(item => item.key === val)[0];
        this.clickInfo = true;
        this.firstShow = !!itemInfo.items;
        this.firstInfo = val;
        this.item.val = this.firstShow ? '' : val;
        this.firstList = itemInfo.items;
        this.secondInfo = '';
        this.clickChange = true;
      },
      changeFrist(val) {
        this.secondInfo = val;
        this.item.val = this.secondInfo;
      },
      changeInfo() {
        if (this.clickChange) {
          this.clickChange = false;
          return;
        }

        if (!this.item.val) {
          this.firstShow = false;
          this.firstList = [];
          this.firstInfo = '';
        } else {
          this.firstShow = false;
          this.firstList = [];
          let valStatus = true;
          for (let i = 0; i < this.item.choice.length; i++) {
            if (String(this.item.choice[i].key) === String(this.item.val)) {
              this.firstInfo = this.item.val;
              valStatus = false;
              this.firstShow = !!this.item.choice[i].items;
              break;
            }
          }
          if (valStatus) {
            for (let i = 0; i < this.item.choice.length; i++) {
              if (this.item.choice[i].items) {
                const valInfo = this.item.choice[i].items;
                this.firstShow = true;
                if (this.firstInfo === this.item.choice[i].key) {
                  this.firstList = valInfo;
                }

                for (let j = 0; j < valInfo.length; j++) {
                  if (String(valInfo[j].key) === String(this.item.val)) {
                    this.firstList = valInfo;
                    this.secondInfo = this.item.val;
                    this.firstInfo = this.item.choice[i].key;
                    break;
                  }
                }
              }
            }
          }
        }
      },
    },
  };
</script>

<style lang='scss' scoped>
    .bk-form-two {
        float: left;
        width: 49%;
        margin-right: 2%;
        position: relative;
    }
    .bk-form-two-other {
        float: left;
        width: 49%;
        position: relative;
    }
</style>
