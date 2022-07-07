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
  <div class="bk-api-basic">
    <div class="bk-basic-item mt20">
      <div class="bk-service-name">
        <h1><span class="is-outline"></span>{{ $t('m.systemConfig["基本信息"]') }}</h1>
      </div>
      <ul class="bk-basic-form">
        <li>
          <span class="bk-info-title">{{ $t('m.systemConfig["接口名称："]') }}</span>
          <span class="bk-info-content">{{apiDetailInfo.name || '--'}}</span>
        </li>
        <li>
          <!-- eslint-disable-next-line no-irregular-whitespace -->
          <span class="bk-info-title">{{ $t('m.systemConfig["创 建 人："]') }}</span>
          <span class="bk-info-content">{{apiDetailInfo.creator || '--'}}</span>
        </li>
        <li>
          <!-- eslint-disable-next-line no-irregular-whitespace -->
          <span class="bk-info-title">{{ $t('m.user["负 责 人："]') }}</span>
          <span class="bk-info-content">{{apiDetailInfo.owners || '--'}}</span>
        </li>
        <li>
          <!-- eslint-disable-next-line no-irregular-whitespace -->
          <span class="bk-info-title">{{ $t('m.systemConfig["状  态："]') }}</span>
          <span class="bk-info-content">{{apiDetailInfo.is_activated ? $t(`m.systemConfig["启用"]`) : $t(`m.systemConfig["关闭"]`)}}</span>
        </li>
        <li>
          <span class="bk-info-title">{{ $t('m.systemConfig["更新时间："]') }}</span>
          <span class="bk-info-content">{{apiDetailInfo.create_at}}</span>
        </li>
        <li>
          <span class="bk-info-title">{{ $t('m.systemConfig["接口路径："]') }}</span>
          <span class="bk-info-content">{{apiDetailInfo.path}}</span>
        </li>
        <li>
          <!-- eslint-disable-next-line no-irregular-whitespace -->
          <span class="bk-info-title">{{ $t('m.systemConfig["备  注："]') }}</span>
          <span class="bk-info-content">{{apiDetailInfo.desc}}</span>
        </li>
      </ul>
    </div>
    <div class="bk-basic-item" style="padding: 0">
      <div class="bk-service-name">
        <h1><span class="is-outline"></span>{{ $t('m.systemConfig["请求参数"]') }}</h1>
      </div>
      <div class="bk-basic-content">
        <p class="bk-basic-p">Query：</p>
        <bk-table
          :data="apiDetailInfo.req_params"
          :size="'small'">
          <bk-table-column :label="$t(`m.systemConfig['参数名称']`)" prop="name"></bk-table-column>
          <bk-table-column :label="$t(`m.systemConfig['必选']`)">
            <template slot-scope="props">
              <span>{{props.row.is_necessary ? $t('m.systemConfig["是"]') : $t('m.systemConfig["否"]')}}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.systemConfig['示例']`)">
            <template slot-scope="props">
              <span :title="props.row.sample">{{props.row.sample || '--'}}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.systemConfig['备注']`)">
            <template slot-scope="props">
              <span :title="props.row.desc">{{props.row.desc || '--'}}</span>
            </template>
          </bk-table-column>
        </bk-table>
      </div>
      <div class="bk-basic-content">
        <p class="bk-basic-p">Body：</p>
        <bk-table
          :data="bodyTableData"
          :size="'small'">
          <bk-table-column :label="$t(`m.systemConfig['名称']`)">
            <template slot-scope="props">
              <div class="bk-more">
                <span :style="{ paddingLeft: 20 * props.row.level + 'px' }"></span>
                <span class="bk-icon tree-expanded-icon icon-right-shape"
                  v-if="props.row.has_children && !props.row.showChildren"></span>
                <span class="bk-icon tree-expanded-icon icon-down-shape"
                  v-else-if="props.row.has_children && props.row.showChildren"></span>
                <span class="bk-icon bk-more-icon" v-else> </span>
                <span>{{props.row.key || '--'}}</span>
              </div>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.systemConfig['类型']`)" prop="type"></bk-table-column>
          <bk-table-column :label="$t(`m.systemConfig['必选']`)">
            <template slot-scope="props">
              <span>{{props.row.is_necessary ? $t('m.systemConfig["是"]') : $t('m.systemConfig["否"]')}}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.systemConfig['备注']`)">
            <template slot-scope="props">
              <span :title="props.row.desc">{{props.row.desc || '--'}}</span>
            </template>
          </bk-table-column>
        </bk-table>
      </div>
    </div>
    <div class="bk-basic-item" style="padding: 0">
      <div class="bk-service-name">
        <h1><span class="is-outline"></span>{{ $t('m.systemConfig["返回数据"]') }}</h1>
      </div>
      <div class="bk-basic-content">
        <bk-table
          :data="responseTableData"
          :size="'small'">
          <bk-table-column :label="$t(`m.systemConfig['名称']`)">
            <template slot-scope="props">
              <div class="bk-more">
                <span :style="{ paddingLeft: 20 * props.row.level + 'px' }"></span>
                <span class="bk-icon tree-expanded-icon icon-right-shape"
                  v-if="props.row.has_children && !props.row.showChildren"></span>
                <span class="bk-icon tree-expanded-icon icon-down-shape"
                  v-else-if="props.row.has_children && props.row.showChildren"></span>
                <span class="bk-icon bk-more-icon" v-else> </span>
                <span>{{props.row.key || '--'}}</span>
              </div>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.systemConfig['类型']`)" prop="type"></bk-table-column>
          <bk-table-column :label="$t(`m.systemConfig['必选']`)">
            <template slot-scope="props">
              <span>{{props.row.is_necessary ? $t('m.systemConfig["是"]') : $t('m.systemConfig["否"]')}}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.systemConfig['备注']`)">
            <template slot-scope="props">
              <span :title="props.row.desc">{{props.row.desc || '--'}}</span>
            </template>
          </bk-table-column>
        </bk-table>
      </div>
    </div>
  </div>
</template>

<script>
  import mixins from '../../../commonMix/mixins_api.js';

  export default {
    mixins: [mixins],
    props: {
      apiDetailInfo: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        bodyTableData: [],
        responseTableData: [],
        bodyDetailConfig: {
          value: '',
          width: '100%',
          height: 200,
          readOnly: true,
          fullScreen: true,
          lang: 'json',
        },
        responseDetailConfig: {
          value: '',
          width: '100%',
          height: 200,
          readOnly: true,
          fullScreen: true,
          lang: 'json',
        },
        basicList: [
          { id: 'name', name: this.$t('m.systemConfig["接口名称："]'), value: 'get_user_info' },
          { id: 'creator', name: this.$t('m.systemConfig["创建人："]'), value: 'pitou' },
          { id: 'state', name: this.$t('m.systemConfig["状态："]'), value: '草稿' },
          { id: 'update_time', name: this.$t('m.systemConfig["更新时间："]'), value: '2019-05-07 10:42:42' },
          { id: 'path', name: this.$t('m.systemConfig["接口路径："]'), code: 'GET', value: '/api/user/' },
          { id: 'desc', name: this.$t('m.systemConfig["备注：："]'), value: 'test api' },
          {
            id: 'mock',
            name: this.$t('m.systemConfig["Mock地址："]'),
            value: 'http://yapi.demo.qunar.com/mock/65300/api/user/',
          },
        ],
        headersList: [
          {
            name: 'Content-Type',
            value: 'application/json',
            is_necessary: true,
            sample: '',
            desc: '',
          },
        ],
        queryList: [
          {
            name: 'aaa',
            is_necessary: true,
            sample: '1123',
            desc: '',
          },
        ],
        bodyList: [
          {
            name: 'result',
            type: 'object',
            is_necessary: false,
            default: '',
            desc: '',
            otherInfo: `${this.$t('m.systemConfig["备注："]')}test`,
          },
        ],
        resultList: [
          {
            name: 'result',
            type: ' boolean',
            is_necessary: false,
            default: '',
            desc: '',
            otherInfo: 'input: 123',
          },
        ],
      };
    },
    computed: {},
    watch: {
      apiDetailInfo() {
        this.initDate();
      },
    },
    mounted() {
      this.initDate();
    },
    methods: {
      async bodyTableDataChange() {
        const bodyTableData = JSON.parse(JSON.stringify(this.apiDetailInfo.bodyTableData));
        await bodyTableData.forEach((item) => {
          item.children = [];
        });
        await this.recordChildren(bodyTableData);
        this.bodyTableData = await bodyTableData;
      },
      responseTableDataChange() {
        this.responseTableData = JSON.parse(JSON.stringify(this.apiDetailInfo.responseTableData));
        this.responseTableData.forEach((item) => {
          item.children = [];
        });
        this.recordChildren(this.responseTableData);
      },
      initDate() {
        if (this.apiDetailInfo.bodyJsonData) {
          this.bodyDetailConfig.value = JSON.stringify(this.apiDetailInfo.bodyJsonData.root, null, 4);
        }
        this.bodyTableDataChange();
        this.responseTableDataChange();
      },
      editorInitAfter() {
        // ...
      },
      changeState(item) {
        item.showChildren = !item.showChildren;
        item.children.forEach((ite) => {
          ite.isShow = item.showChildren;
        });
        if (!item.showChildren) {
          this.closeChildren(item);
        }
      },
      closeChildren(item) {
        item.children.forEach((ite) => {
          ite.isShow = false;
          if (ite.has_children) {
            ite.showChildren = false;
            this.closeChildren(ite);
          }
        });
      },
      recordChildren(tableData) {
        const levelList = tableData.map(item => item.level);
        const maxLevel = Math.max(...levelList);
        const recordChildrenStep = function (tableData, item) {
          tableData.filter(ite => (ite.level === item.level - 1 && ite.primaryKey === item.parentPrimaryKey && ite.ancestorsList.toString() === item.ancestorsList.slice(0, -1).toString()))[0].children.push(item);
        };
        for (let i = maxLevel; i > 0; i--) {
          tableData.filter(item => item.level === i).forEach((ite) => {
            recordChildrenStep(tableData, ite);
          });
        }
      },
    },
  };
</script>

<style lang="scss" scoped>
    @import '../../../../scss/mixins/clearfix.scss';
    .bk-basic-item {
        padding-bottom: 20px;
        border-bottom: 1px solid #E9EDF1;
        margin-bottom: 20px;
    }
    .bk-basic-form {
        padding: 0px 20px;
        @include clearfix;
        li {
            width: 50%;
            float: left;
            font-size: 12px;
            color: #737987;
            height: 30px;
            line-height: 30px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
            @include clearfix;

            .bk-info-content {
                padding-left: 5px;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
            }
        }
        .bk-info-title {
            font-weight: 700;
            min-width: 72px;
            float: left;
        }
        .bk-info-content {
            width: calc(100% - 72px);
            float: left;
            word-wrap: break-word;
            padding-left: 5px;
        }
    }
    .bk-basic-content {
        padding: 0 20px 20px;
    }
    .bk-basic-p {
        font-size: 14px;
        color: #737987;
        line-height: 36px;
    }
    .bk-more {
        &.bk-value {
            position: relative;
            justify-content: space-between;
        }

        overflow: visible;
        display: flex;
        align-items: center;

        .bk-icon {
            padding-right: 5px;
            color: #c0c4cc;
            cursor: pointer;
        }

        .bk-more-icon {
            width: 17px;
        }
    }
</style>
