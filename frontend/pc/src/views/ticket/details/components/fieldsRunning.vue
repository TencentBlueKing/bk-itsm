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
  <div class="bk-fields-running">
    <div class="bk-field-contain" :key="routerKey">
      <component
        ref="temp"
        :is="'CW-' + item.type"
        :item="item"
        :fields="fields"
        :is-current="true"></component>
    </div>
    <div class="bk-save-cancel" :class="{ 'bk-save-margin': marginTypeList.some(type => type === item.type) }">
      <span class="bk-save-cancel-item" @click="save(item)">{{$t(`m.systemConfig["保存"]`)}}</span>
      <span class="bk-save-cancel-split">|</span>
      <span class="bk-save-cancel-item" @click="cancel(item)">{{$t(`m.wiki['取消']`)}}</span>
    </div>
  </div>
</template>
<script>
  import commonMix from '../../../commonMix/common.js';
  import string from '../../../commonComponent/fieldComponent/string.vue';
  import link from '../../../commonComponent/fieldComponent/link';
  import int from '../../../commonComponent/fieldComponent/int.vue';
  import text from '../../../commonComponent/fieldComponent/text.vue';
  import checkbox from '../../../commonComponent/fieldComponent/checkbox.vue';
  import radio from '../../../commonComponent/fieldComponent/radio.vue';
  import select from '../../../commonComponent/fieldComponent/select.vue';
  import inputSelect from '../../../commonComponent/fieldComponent/inputSelect';
  import multiselect from '../../../commonComponent/fieldComponent/multiselect.vue';
  import date from '../../../commonComponent/fieldComponent/date.vue';
  import datetime from '../../../commonComponent/fieldComponent/datetime.vue';
  import member from '../../../commonComponent/fieldComponent/member.vue';
  import members from '../../../commonComponent/fieldComponent/members.vue';
  import table from '../../../commonComponent/fieldComponent/table.vue';
  import customtable from '../../../commonComponent/fieldComponent/customtable.vue';
  import editor from '../../../commonComponent/fieldComponent/editor.vue';
  import tree from '../../../commonComponent/fieldComponent/tree.vue';
  import file from '../../../commonComponent/fieldComponent/file.vue';
  import cascade from '../../../commonComponent/fieldComponent/cascade.vue';
  import customForm from '../../../commonComponent/fieldComponent/customForm.vue';
  import { errorHandler } from '@/utils/errorHandler.js';

  export default {
    name: 'fieldsRunning',
    inject: ['reloadTicket'],
    components: {
      'CW-STRING': string,
      'CW-LINK': link,
      'CW-INT': int,
      'CW-TEXT': text,
      'CW-CHECKBOX': checkbox,
      'CW-RADIO': radio,
      'CW-SELECT': select,
      'CW-INPUTSELECT': inputSelect,
      'CW-MULTISELECT': multiselect,
      'CW-DATE': date,
      'CW-DATETIME': datetime,
      'CW-MEMBER': member,
      'CW-MEMBERS': members,
      'CW-TABLE': table,
      'CW-CUSTOMTABLE': customtable,
      'CW-RICHTEXT': editor,
      'CW-TREESELECT': tree,
      'CW-FILE': file,
      'CW-CASCADE': cascade,
      'CW-CUSTOM-FORM': customForm,
    },
    mixins: [commonMix],
    props: {
      basicInfomation: {
        type: Object,
        default() {
          return {};
        },
      },
      fields: {
        type: Array,
        default() {
          return [];
        },
      },
      item: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        showMore: false,
        showInfo: true,
        fieldList: [
          {
            isEdit: false,
            name: 1,
            content: 'qwsqw',
          },
          {
            isEdit: false,
            name: 2,
            content: 'qw1q1qsqw',
          },
        ],
        routerKey: +new Date(),
        secondClick: false,
        rotate: false,
        marginTypeList: ['TABLE', 'CUSTOMTABLE', 'FILE', 'RICHTEXT'],
      };
    },
    computed: {
      profile() {
        if (!this.basicInfomation) {
          return;
        }
        return {
          name: this.basicInfomation.profile.name,
          phone: this.basicInfomation.profile.phone,
          department: this.basicInfomation.profile.departments ? this.basicInfomation.profile.departments : [],
        };
      },
    },
    mounted() {
      this.$set(this.item, 'isEdit', true);
      this.$nextTick(() => {
        this.reloadCurPage();
      });
      this.$forceUpdate();
    },
    methods: {
      freshBtn(item, changeFields) {
        this.rotate = !this.rotate;
        this.freshApi(item, changeFields, 'field');
      },
      freshRpc(item) {
        this.$store.dispatch('apiRemote/getRpcData', item).then((res) => {
          item.choice = res.data;
          item.val = '';
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
      // 修改至结束状态弹窗事件
      submitTemplate() {
        const { id } = this.basicInfomation;
        this.fieldFormatting([this.item]);
        const params = {
          field: {
            id: this.item.id,
            key: this.item.key,
            value: this.item.value,
            type: this.item.type,
          },
        };
        if (this.secondClick) {
          return;
        }
        this.secondClick = true;
        this.$store.dispatch('basicModule/edit_field', { params, id }).then(() => {
          this.$bkMessage({
            message: this.$t('m.systemConfig["修改成功"]'),
            theme: 'success',
          });
          this.reloadTicket();
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.secondClick = false;
            this.toDone();
          });
      },
      reloadCurPage() {
        this.routerKey = +new Date();
      },
      cancel() {
        this.fields.forEach((ite) => {
          ite.isEdit = false;
        });
        this.$set(this.item, 'isEdit', false);
      },
      async save() {
        if (this.item.key === 'current_status') {
          const temp = this.item.choice.filter(ite => ite.key === this.item.val)[0];
          if (temp.is_over === 'True') {
            this.$bkInfo({
              type: 'warning',
              title: this.$t('m.systemConfig["确认保存？"]'),
              subTitle: this.$t('m.systemConfig["状态修改为【"]') + temp.name + this.$t('m.systemConfig["】将导致整个单据结束"]'),
              confirmFn: () => {
                this.submitTemplate();
                // 仅修改单据状态后刷新整个单据
                this.reloadTicket();
              },
            });
          } else {
            this.submitTemplate();
          }
        } else {
          this.submitTemplate();
        }
      },
      async toDone() {
        await this.$set(this.item, 'isEdit', false);
        // await this.partUpdate()
      },
    },
  };
</script>
<style lang='scss' scoped>
    @import '../../../../scss/mixins/clearfix.scss';
    @import '../../../../scss/mixins/scroller.scss';

    .bk-fields-running {
        font-size: 14px;
        color: #63656E;
        width: 100%;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        padding: 8px 0;

        .bk-field-lable {
            line-height: 32px;
            font-weight: bold;
        }

        .bk-field-contain {
            @include clearfix;
            @include scroller;
            max-width: 100%;
            flex-grow: 1;
        }

        .bk-save-cancel {
            margin: 30px 7px 0px;

            .bk-save-cancel-item {
                cursor: pointer;
                color: #3A84FF;
            }

            .bk-save-cancel-split {
                padding: 0 5px;
                color: #D8D8D8;
            }
        }
        .bk-save-margin {
            display: block;
            width: 100%;
            margin: 10px 0px 0;
        }
    }

    .bk-field-contain {
        position: relative;
        border: none;
        box-sizing: border-box;

        .bk-field-lable {
            position: absolute;
            top: 0px;
            left: 0px;
            width: 100%;
            height: auto;
            float: left;
            padding: 0px 10px 10px 0px;
            vertical-align: middle;
            font-size: 14px;
            font-weight: bold;

            .bk-field-apart {
                background: white;
                display: flex;
                align-items: center;
                justify-content: space-between;

                .bk-field-apart-left {
                    display: block;
                    // width: 100%;
                    line-height: 19px;
                    font-weight: normal;
                    padding: 0;
                    text-align: left;
                    padding-bottom: 5px;
                    overflow: hidden;
                    white-space: nowrap;
                    text-overflow: ellipsis;
                    color: #737987;

                    .bk-input-required {
                        color: red;
                    }
                }

                .bk-field-apart-right {
                    cursor: pointer;
                    display: block;
                    // width: 100%;
                    line-height: 19px;
                    font-weight: normal;
                    font-size: 12px;
                    padding: 0;
                    text-align: left;
                    padding-bottom: 5px;
                    overflow: hidden;
                    white-space: nowrap;
                    text-overflow: ellipsis;
                    color: #737987;
                }
            }
        }
    }

    .rotate {
        transition: all 1s;
        transform: rotate(360deg);
    }
    .not-rotate{
        transform: rotate(0deg);
    }
</style>
