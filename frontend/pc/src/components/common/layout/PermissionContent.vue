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
  <div class="permission-content">
    <div class="permission-header">
      <span class="title-icon">
        <img :src="lock" alt="permission-lock" class="lock-img" />
      </span>
      <h3>{{$t(`m.common['该操作需要以下权限']`)}}</h3>
    </div>
    <table class="permission-table table-header">
      <thead>
        <tr>
          <th width="20%">{{$t(`m.common['系统']`)}}</th>
          <th width="30%">{{$t(`m.common['需要申请的权限']`)}}</th>
          <th width="50%">{{$t(`m.common['关联的资源实例']`)}}</th>
        </tr>
      </thead>
    </table>
    <div class="table-content">
      <table class="permission-table">
        <tbody>
          <template v-if="permissionData.actions && permissionData.actions.length > 0">
            <tr v-for="(action, index) in permissionData.actions" :key="index">
              <td width="20%">{{permissionData.system_name}}</td>
              <td width="30%">{{action.name}}</td>
              <td width="50%">
                <p
                  class="resource-type-item"
                  v-for="(reItem, reIndex) in getResource(action.related_resource_types)"
                  :key="reIndex">
                  {{reItem}}
                </p>
              </td>
            </tr>
          </template>
          <tr v-else>
            <td class="no-data" colspan="3">{{$t(`m.common['无数据']`)}}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
<script>
  export default {
    name: 'PermissionContent',
    props: {
      permissionData: {
        type: Object,
        default: {},
      },
    },
    data() {
      return {
        lock: require('../../../images/lock-radius.svg'),
        // 返回499code 关联的实例对象取type
        resource_label: {
          task_template: this.$t('m.common[\'任务模板\']'),
          public_api: this.$t('m.common[\'公共API\']'),
          service: this.$t('m.common[\'服务\']'),
        },
      };
    },
    methods: {
      getResource(resoures) {
        if (resoures.length === 0) {
          return ['--'];
        }

        const data = [];
        resoures.forEach((resource) => {
          if (resource.instances.length > 0) {
            resource.instances.forEach((instanceItem) => {
              instanceItem.forEach((item) => {
                data.push(`${item.type_name === null ? this.resource_label[item.type] : item.type_name}：${item.name}`);
              });
            });
          }
        });
        return data;
      },
    },
  };
</script>
<style lang="scss" scoped>
    .permission-content {
        width: 100%;
        .permission-header {
            text-align: center;
            .title-icon {
                display: inline-block;
            }
            .lock-img {
                width: 120px;
            }
            h3 {
                margin: 6px 0 24px;
                color: #63656e;
                font-size: 20px;
                font-weight: normal;
                line-height: 1;
            }
        }
        .permission-table {
            width: 100%;
            color: #63656e;
            border-bottom: 1px solid #e7e8ed;
            border-collapse: collapse;
            table-layout: fixed;
            th,
            td {
                padding: 12px 18px;
                font-size: 12px;
                text-align: left;
                border-bottom: 1px solid #e7e8ed;
                word-break: break-all;
            }
            th {
                color: #313238;
                background: #f5f6fa;
            }
        }
        .table-content {
            max-height: 260px;
            border-bottom: 1px solid #e7e8ed;
            border-top: none;
            overflow: auto;
            .permission-table {
                border-top: none;
                border-bottom: none;
                td:last-child {
                    border-right: none;
                }
                tr:last-child td {
                    border-bottom: none;
                }
                .resource-type-item {
                    padding: 0;
                    margin: 0;
                }
            }
            .no-data {
                padding: 30px;
                text-align: center;
                color: #999999;
            }
        }
    }
    .button-group {
        .bk-button {
            margin-left: 7px;
        }
    }

</style>
