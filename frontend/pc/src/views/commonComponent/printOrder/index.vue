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
  <div id="bk-printcontent">
    <bk-button class="bk-print-button"
      :theme="'primary'"
      :title="$t(`m.common['打印本页']`)"
      :disabled="isCanPrint"
      @click="doPrint">
      {{ $t('m.common["打印本页"]') }}
    </bk-button>
    <div class="bk-printcontent_">
      <div class="bk-print-header">
        <h1 class="bk-title">ITSM-{{name}}- {{sn}}</h1>
        <div class="bk-header-line">
          <ul>
            <li style="width: 40%;">{{ $t('m.common["打印日期"]') }}：{{printDate}}</li>
            <li style="width: 40%;">{{ $t('m.common["打印人"]') }}：{{username}}</li>
            <li style="width: 20%;">{{ $t('m.common["状态"]') }}：{{state}}</li>
          </ul>
        </div>
      </div>
      <div class="bk-print-content">
        <div class="bk-print-message">
          <h2>{{ $t('m.common["一、工单信息"]') }}</h2>
          <ul class="bk-message-ul" v-if="jdList.length">
            <li>{{ $t('m.common["提单时间"]') }}：{{createAt}}</li>
            <li style="width: 20%;">{{ $t('m.common["提单人"]') }}: {{operator}}</li>
            <li style="width: 45%;">{{ $t('m.common["服务目录"]') }}: {{cataLog}}</li>
          </ul>
        </div>
        <div class="bk-content-inner">
          <table style="table-layout: fixed;"
            v-if="ticketList.length % 2 !== 1 && ticketList.length !== 0"
            class="bk-table-zone">
            <tr v-for="index in (ticketList.length / 2)" :key="index">
              <td>
                <span class="bk-table-head">
                  {{ ticketList[(index - 1) * 2].name }} {{ ticketList[(index - 1) * 2].name === '--' ? '' : ':' }}
                </span>
              </td>
              <td>
                <div v-if="ticketTypeList1.indexOf(ticketList[(index - 1) * 2].type) !== -1 && ticketList[(index - 1) * 2].display_value">
                  <span>{{ $t('m.common["见表格"]') }} : &lt; {{ ticketList[(index - 1) * 2].name }} &gt;
                  </span>
                </div>
                <div class="bk-dict_"
                  v-else-if="ticketTypeList2.indexOf(ticketList[(index - 1) * 2].type) !== -1 && ticketList[(index - 1) * 2].display_value">
                  <div v-for="(i, ind) in ticketList[(index - 1) * 2].choice" :key="ind">
                    <div v-if="ticketList[(index - 1) * 2].display_value.indexOf(i.key) !== -1">
                      <span class="bk-pot">·</span>
                      <span class="bk-pot-after"> {{i.name}} </span>
                    </div>
                  </div>
                </div>
                <div v-else-if="ticketTypeList4.indexOf(ticketList[(index - 1) * 2].type) !== -1 && ticketList[(index - 1) * 2].display_value">
                  <div class="bk-RICHTEXT" v-html="ticketList[(index - 1) * 2].display_value"></div>
                </div>
                <div v-else-if="ticketList[(index - 1) * 2].type === 'TEXT' && ticketList[(index - 1) * 2].display_value">
                  {{ ticketList[(index - 1) * 2].display_value }}
                </div>
                <div v-else-if="ticketList[(index - 1) * 2].type === 'CUSTOM-FORM' && ticketList[(index - 1) * 2].display_value">
                  见：&lt; {{ ticketList[(index - 1) * 2].name }} &gt;
                </div>
                <div v-else>
                  {{ ticketList[(index - 1) * 2].display_value }}
                </div>
              </td>
              <td>
                <span class="bk-table-head">
                  {{ ticketList[(index - 1) * 2 + 1].name}} {{ ticketList[(index - 1) * 2 + 1].name === '--' ? '' : ':' }}
                </span>
              </td>
              <td>
                <div v-if="ticketTypeList1.indexOf(ticketList[(index - 1) * 2 + 1].type) !== -1 && ticketList[(index - 1) * 2 + 1].display_value">
                  <div>{{ $t('m.common["见表格"]') }} : &lt; {{ticketList[(index - 1) * 2 + 1].name }}
                    &gt;
                  </div>
                </div>
                <div class="bk-dict_"
                  v-else-if="ticketTypeList2.indexOf(ticketList[(index - 1) * 2 + 1].type) !== -1 && ticketList[(index - 1) * 2 + 1].display_value">
                  <div v-for="(i, ind) in ticketList[(index - 1) * 2 + 1].choice" :key="ind">
                    <div v-if="ticketList[(index - 1) * 2 + 1].display_value.indexOf(i.key) !== -1">
                      <span class="bk-pot">·</span>
                      <span class="bk-pot-after">{{i.name}}</span>
                    </div>
                  </div>
                </div>
                <div v-else-if="ticketTypeList4.indexOf(ticketList[(index - 1) * 2 + 1].type) !== -1 && ticketList[(index - 1) * 2 + 1].display_value">
                  <div class="bk-RICHTEXT" v-html="ticketList[(index - 1) * 2 + 1].display_value"></div>
                </div>
                <div v-else-if="ticketList[(index - 1) * 2 + 1].type === 'TEXT' && ticketList[(index - 1) * 2 + 1].display_value">
                  <div>{{ ticketList[(index - 1) * 2 + 1].display_value }}</div>
                </div>
                <div v-else>
                  {{ ticketList[(index - 1) * 2 + 1].display_value }}
                </div>
              </td>
            </tr>
          </table>
          <div v-for="(item, index) in ticketList"
            :key="index"
            v-if="ticketTypeList1.indexOf(item.type) !== -1 && item.display_value" class="bk-break">
            <h4>{{ $t('m.common["表格"]') }}：{{item.name}}</h4>
            <template v-if="item.type === 'TABLE'">
              <table style="table-layout: fixed;" class="bk-table-zone">
                <tr>
                  <th v-for="(i, iIndex) in item.choice" :key="iIndex">{{ i.name }}</th>
                </tr>
                <tr v-for="(itemC, ind) in item.display_value" :key="ind">
                  <td v-for="(i, iIndex) in item.choice" :key="iIndex">{{ itemC[i.key] }}</td>
                </tr>
              </table>
            </template>
            <template v-else-if="item.type === 'CUSTOMTABLE'">
              <table style="table-layout: fixed;" class="bk-table-zone">
                <tr>
                  <th v-for="(title, titleIndex) in item.meta.columns" :key="titleIndex">
                    {{title.name}}
                  </th>
                </tr>
                <tr v-for="(tr, trIndex) in item.value" :key="trIndex">
                  <td v-for="(column, columnIndex) in item.meta.columns" :key="columnIndex">
                    <template v-for="key in Object.keys(tr)"
                      v-if="key === column.key"
                      :title="tr[key]">
                      {{getCustomTableDisplayValue(column, tr) || '--'}}
                    </template>
                  </td>
                </tr>
              </table>
            </template>

          </div>
          <div v-for="(item, index) in ticketList.filter(item => item.type === 'CUSTOM-FORM')" :key="index">
            <h4>{{item.name}}</h4>
            <div v-for="(customForm, i) in getCustomFormDisplayValue(item)" :key="i">
              <pre style="line-height: 32px;" v-if="customForm.type === 'text'"> {{ customForm.name }}：{{ customForm.value }} </pre>
              <template v-else-if="customForm.type === 'table'">
                <h5 style="margin: 10px 0;">{{ customForm.name }}</h5>
                <table>
                  <tr>
                    <th v-for="(column, columnIndex) in customForm.columns" :key="columnIndex">
                      {{ column.name }}
                    </th>
                  </tr>
                  <tr v-for="(tr, trIndex) in customForm.value" :key="trIndex">
                    <td v-for="(column, columnIndex) in customForm.columns" :key="columnIndex">
                      {{ tr[column.key] }}
                    </td>
                  </tr>
                </table>
              </template>
              <p v-else>{{ customForm.name }}：{{ customForm.value }}</p>
            </div>
          </div>
        </div>
        <div class="bk-print-message">
          <h2>{{ $t('m.common["二、工作流"]') }}</h2>
        </div>
        <div class="bk-print-message" v-for="(itemFlow, indexFlow) in jdList" :key="indexFlow">
          <h3>{{indexFlow + 1}}.{{itemFlow.name}}</h3>
          <ul class="bk-message-ul">
            <li v-if="itemFlow.operate_at && itemFlow.status !== 'RUNNING'">
              {{ itemFlow.type === 'END' ? $t(`m.common["结束"]`) : $t(`m.common["处理时间："]`) }}{{ itemFlow.operate_at }}
            </li>
            <li v-if="itemFlow.operator && itemFlow.status !== 'RUNNING'">
              {{ $t('m.common["处理人："]') }}{{ itemFlow.operator }}
            </li>
            <li v-if="itemFlow.operator && itemFlow.status !== 'RUNNING'">
              {{ $t('m.common["处理操作："]') }}{{ itemFlow.action || '--' }}
            </li>
          </ul>
          <template v-if="itemFlow['fields'] && itemFlow['fields'].length">
            <table style="table-layout: fixed;" v-if="itemFlow.length % 2 !== 1" class="bk-table-zone">
              <tr v-for="index in (itemFlow['fields'] ? itemFlow['fields'].length / 2 : [])" :key="index">
                <td>
                  <span class="bk-table-head">
                    {{ itemFlow['fields'][(index - 1) * 2].name}} {{ itemFlow['fields'][(index - 1) * 2].name === '--' ? '' : ':' }}
                  </span>
                </td>
                <td>
                  <div v-if="ticketTypeList1.indexOf(itemFlow['fields'][(index - 1) * 2].type) !== -1 && itemFlow['fields'][(index - 1) * 2].display_value">
                    <div>
                      {{ $t('m.common["见表格"]') }} : &lt; {{itemFlow['fields'][(index - 1) * 2].name }} &gt;
                    </div>
                  </div>
                  <div class="bk-dict_"
                    v-else-if="ticketTypeList2.indexOf(itemFlow['fields'][(index - 1) * 2].type) !== -1 && itemFlow['fields'][(index - 1) * 2].display_value">
                    <div v-for="(i, ind) in itemFlow['fields'][(index - 1) * 2].choice" :key="ind">
                      <div v-if="(itemFlow['fields'][(index - 1) * 2].display_value).indexOf(i.key) !== -1">
                        <span class="bk-pot">·</span>
                        <span class="bk-pot-after">{{ i.name }}</span>
                      </div>
                    </div>
                  </div>
                  <div v-else-if="ticketTypeList4.indexOf(itemFlow['fields'][(index - 1) * 2].type) !== -1 && itemFlow['fields'][(index - 1) * 2].display_value">
                    <div class="bk-RICHTEXT"
                      v-html="itemFlow['fields'][(index - 1) * 2].display_value"></div>
                  </div>
                  <div v-else-if="itemFlow['fields'][(index - 1) * 2].type === 'TEXT' && itemFlow['fields'][(index - 1) * 2].display_value">
                    <div>{{ itemFlow['fields'][(index - 1) * 2].display_value }}</div>
                  </div>
                  <div v-else>
                    {{ itemFlow['fields'][(index - 1) * 2].display_value }}
                  </div>
                </td>
                <td>
                  <span class="bk-table-head">
                    {{itemFlow['fields'][(index - 1) * 2 + 1].name}} {{ itemFlow['fields'][(index - 1) * 2 + 1].name === '--' ? '' : ':' }}
                  </span>
                </td>
                <td>
                  <div v-if="ticketTypeList1.indexOf(itemFlow['fields'][(index - 1) * 2 + 1].type) !== -1 && itemFlow['fields'][(index - 1) * 2 + 1].display_value">
                    <div>{{ $t('m.common["见表格"]') }} : &lt;
                      {{itemFlow['fields'][(index - 1) * 2 + 1].name}} &gt;
                    </div>
                  </div>
                  <div class="bk-dict_"
                    v-else-if="ticketTypeList2.indexOf(itemFlow['fields'][(index - 1) * 2 + 1].type) !== -1 && itemFlow['fields'][(index - 1) * 2 + 1].display_value">
                    <div v-for="(i, ind) in itemFlow['fields'][(index - 1) * 2 + 1].choice" :key="ind">
                      <div v-if="itemFlow['fields'][(index - 1) * 2 + 1].display_value.indexOf(i.key) !== -1">
                        <span class="bk-pot">·</span>
                        <span class="bk-pot-after">{{ i.name }}</span>
                      </div>
                    </div>
                  </div>
                  <div v-else-if="ticketTypeList4.indexOf(itemFlow['fields'][(index - 1) * 2 + 1].type) !== -1 && itemFlow['fields'][(index - 1) * 2 + 1].display_value">
                    <div class="bk-RICHTEXT"
                      v-html="itemFlow['fields'][(index - 1) * 2 + 1].display_value"></div>
                  </div>
                  <div v-else-if="itemFlow['fields'][(index - 1) * 2 + 1].type === 'TEXT' && itemFlow['fields'][(index - 1) * 2 + 1].display_value">
                    <div>{{ itemFlow['fields'][(index - 1) * 2 + 1].display_value }}</div>
                  </div>
                  <div v-else>
                    {{ itemFlow['fields'][(index - 1) * 2 + 1].display_value }}
                  </div>
                </td>
              </tr>
            </table>
            <!-- 表格集合 -->
            <template v-if="itemFlow.table_data && itemFlow.table_data.length">
              <div v-for="(it, itIndex) in itemFlow.table_data" :key="itIndex">
                <h4>{{ $t('m.common["表格"]') }}：{{it.name}}</h4>
                <template v-if="it.type === 'TABLE'">
                  <table style="table-layout: fixed;" class="bk-table-zone">
                    <tr>
                      <th v-for="(i, iIndex) in it.choice" :key="iIndex">{{i.name }}
                      </th>
                    </tr>
                    <tr v-for="(itemC,ind) in it.display_value" :key="ind">
                      <td v-for="(i, iIndex) in it.choice" :key="iIndex">
                        {{itemC[i.key]}}
                      </td>
                    </tr>
                  </table>
                </template>
                <template v-if="it.type === 'CUSTOMTABLE'">
                  <table style="table-layout: fixed;" class="bk-table-zone">
                    <tr>
                      <th v-for="(title, titleIndex) in it.meta.columns" :key="titleIndex">
                        {{title.name}}
                      </th>
                    </tr>
                    <tr v-for="(tr, trIndex) in it.value" :key="trIndex">
                      <td v-for="(column, indexColumns) in it.meta.columns" :key="indexColumns">
                        <template v-for="key in Object.keys(tr)"
                          v-if="key === column.key"
                          :title="tr[key]">
                          {{getCustomTableDisplayValue(column, tr) || '--'}}
                        </template>
                      </td>
                    </tr>
                  </table>
                </template>
              </div>
            </template>
            <!-- 自定义表单集合 -->

          </template>
          <template v-if="itemFlow.operator && itemFlow.status !== 'RUNNING'">
            {{ $t('m.common["处理信息："]') }}{{ itemFlow.message || '--' }}
          </template>
        </div>
      </div>
    </div>
  </div>

</template>

<script>
  import { errorHandler } from '../../../utils/errorHandler';
  import { getCustomTableDisplayValue } from '@/components/RenderField/fieldUtils';

  export default {
    name: 'commonview',
    data() {
      return {
        // 头部信息
        printDate: '',
        username: '',
        state: '',
        id: '',
        name: '',
        sn: '',
        cataLog: '',
        ticketList: [],
        jdList: [],
        ticketTypeList1: ['TABLE', 'CUSTOMTABLE'],
        ticketTypeList2: [],
        ticketTypeList4: ['RICHTEXT'],
        createAt: '',
        operator: '',
        isCanPrint: true,
        isTableLoading: false,
      };
    },
    mounted() {
      this.id = this.$route.query.ticket_id;
      this.username = window.username;
      this.getPrintInfo();
    },
    methods: {
      // 打印
      doPrint() {
        const OutputRankPrint = document.querySelector('.bk-printcontent_');
        document.body.innerHTML = OutputRankPrint.innerHTML;
        document.body.style.padding = '0 15% 0 5%';
        window.print();
        window.location.reload();
        return false;
      },
      getPrintInfo() {
        this.isTableLoading = true;
        const params = {
          id: this.id,
        };
        if (this.$route.query.token) {
          params.token = this.$route.query.token;
        }
        this.$store.dispatch('print/getOnePrint', params).then((res) => {
          if (res.code === 'OK') {
            // 单据信息
            this.printDate = res.data.print_date;
            this.sn = res.data.sn;
            this.state = res.data.status;
            this.cataLog = res.data.cata_log;
            this.name = res.data.service;
            // 提单信息
            this.createAt = res.data.state[0].create_at;
            this.operator = res.data.state[0].operator;
            this.ticketList = res.data.state[0].fields || [];
            if (this.ticketList.length % 2 === 1) {
              this.ticketList.push({
                type: 'STRING',
                name: '--',
                value: '--',
                display_value: '--',
              });
            }
            // 工作流
            this.jdList = res.data.state.slice(1, res.data.state.length);
            this.jdList = this.jdList.map((item) => {
              this.$set(item, 'table_data', []);
              if (!item.fields) {
                item.fields = [];
              }
              item.fields.map((it) => {
                if (this.ticketTypeList1.indexOf(it.type) !== -1) {
                  item.table_data.push(it);
                }
              });
              if (item.fields.length % 2 === 1) {
                item.fields.push({
                  type: 'STRING',
                  name: '--',
                  value: '--',
                });
              }
              return item;
            });
          }
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isCanPrint = false;
            this.isTableLoading = false;
          });
      },
      getCustomTableDisplayValue(column, value) {
        return getCustomTableDisplayValue(column, value);
      },
      getCustomFormDisplayValue(item) {
        function flatValue(value) {
          if (Array.isArray(value)) {
            return value.reduce((str, item) => {
              if (item.label) {
                str += `${item.label}:`;
              }
              str += (item.value || '--');
              str += '\n';
              return str;
            }, '');
          }
          return value;
        }
        const { form_data: fromData, schemes } = item.display_value;
        const newDisplayValue = [];
        fromData.forEach((form) => {
          const scheme = schemes[form.scheme];
          const { type } = scheme;
          if (type === 'text') {
            const val = Array.isArray(form.value) ? flatValue(form.value) : form.value;
            newDisplayValue.push({
              type: 'text',
              name: form.label,
              value: val || '--',
            });
          }
          if (type === 'table') {
            const columns = scheme.attrs.column;
            newDisplayValue.push({
              type: 'table',
              name: form.label,
              columns,
              value: form.value.map((oneV) => {
                const newOne = {};
                Object.keys(oneV).forEach((key) => {
                  newOne[key] = oneV[key].label ? `${oneV[key].label}：${flatValue(oneV[key].value)}` : flatValue(oneV[key].value);
                });
                return newOne;
              }),
            });
          }
        });
        return newDisplayValue;
      },
    },
  };
</script>

<style scoped lang='scss'>
    @import '../../../scss/mixins/clearfix.scss';
    @import '../../../scss/mixins/scroller.scss';
    #bk-printcontent {
        min-width: 1280px;
        width: 100%;
        position: fixed;
        top: 0;
        left: 0;
        background: white;
        z-index: 200;
        height: 100%;
        overflow-y: scroll;
        padding: 0 0 20px 0;
        @include scroller;
        .bk-printcontent_ {
            position: relative;
            padding: 0 15%;
        }
        .bk-print-button {
            position: absolute;
            top: 72px;
            right: 15%;
            z-index: 10;
        }
    }
    .bk-print-header {
        .bk-title {
            text-align: center;
            margin: 15px 0;
        }
        .bk-header-line {
            @include clearfix;
            ul {
                float: left;
                width: calc(100% - 100px);
                @include clearfix;
                line-height: 32px;
            }
            li {
                float: left;
                font-size: 16px;
                width: 33%;
            }
        }
    }
    .bk-print-message {
        h2 {
            margin: 15px 0;
        }
        .bk-message-ul {
            @include clearfix;
            line-height: 32px;
            li {
                float: left;
                width: 33%;
            }
        }
    }

    .bk-dict_ {
        display: flex;
        align-items: center;
        .bk-pot {
            font-size: 20px;
            font-weight: 600;
            padding-right: 2px;
        }
        .bk-pot-after {
            padding-right: 5px;
        }
    }
    table {
        width: 100%;
        border-collapse: collapse;
        tr {
            width: 100% td {
                padding: 5px;
                word-wrap: break-word;
                height: 28px
            }
            th {
                font-weight: 540;
            }
        }
    }
    table, td, th {
        border: 1px solid #505050;
        text-align: center
    }
    table.bk-table-zone {
        width: 100%;
        border-collapse: collapse;

        tr {
            th,
            td {
                word-wrap: break-word;
                word-break: break-all;
            }
            td:nth-child(1) {
                padding: 5px;
                width: 15%;
                word-wrap: break-word;
                word-break: break-all;
            }
            td:nth-child(3) {
                padding: 5px;
                width: 15%;
                word-wrap: break-word;
                word-break: break-all;
            }
            td:nth-child(2) {
                padding: 5px;
                width: 35%;
                word-wrap: break-word;
                word-break: break-all;
            }
            td:nth-child(4) {
                padding: 5px;
                width: 35%;
                word-wrap: break-word;
                word-break: break-all;
            }
            td {
                text-align: center;

                div {
                    text-align: left;
                }
            }
        }

        .bk-RICHTEXT {
            width: 100%;
            /deep/ img {
                width: 100%;
            }
        }
    }
    table.bk-table-zone, td, th {
        border: 1px solid #505050;
        text-align: center
    }
    .bk-bj > div {
        border: 1px solid #505050;
        margin-top: -1px;
        margin-left: -1px;
    }
    .bk-bj > div:nth-child(1) {
        min-width: 250px;
    }
</style>
