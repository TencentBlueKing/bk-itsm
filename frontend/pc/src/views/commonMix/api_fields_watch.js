/*
 * Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 * BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
 *
 * License for BK-ITSM 蓝鲸流程服务:
 * --------------------------------------------------------------------
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
 * LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
 * NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
 */

// /* eslint-disable */
import _ from 'lodash';
import { errorHandler } from '../../utils/errorHandler';
export default {
  methods: {
    // 获取优先级
    async get_priority(params, itemRelate) {
      const data = JSON.parse(JSON.stringify(params));
      data.service_type = itemRelate.service;
      delete data.id;
      const preFieldParams = {
        id: itemRelate.ticket_id,
      };
      // 从之前节点中找紧急程度和影响范围
      if (!(data.impact && data.urgency)) {
        await this.$store.dispatch('change/getStepList', preFieldParams).then((res) => {
          res.data.forEach((node) => {
            node.fields.forEach((field) => {
              if (field.key === 'urgency') {
                data.urgency = params.urgency || field.value;
              }
              if (field.key === 'impact') {
                data.impact = params.impact || field.value;
              }
            });
          });
        }, (res) => {
          errorHandler(res, this);
        });
      }
      this.$store.dispatch('apiRemote/get_priority', { data }).then((res) => {
        // 改变字段值 itemRelate.val
        itemRelate.val = res.data;
      })
        .catch((res) => {
          errorHandler(res, this);
        });
    },
    // 获取数据字典 get_data_by_key
    async get_data_by_key(itemRelate) {
      return this.$store.dispatch('datadict/get_data_by_key', {
        key: itemRelate.source_uri,
        field_key: itemRelate.key,
        service: itemRelate.service,
        current_status: itemRelate.ticket_status,
      }).then((res) => {
        itemRelate.choice = res.data.map(item => ({
          key: item.key,
          name: item.name,
        }));
      })
        .catch((res) => {
          errorHandler(res, this);
        });
    },
    // 获取级联字段 get_data_workflow
    apiRemoteGetData(params, field, type) {
      let reqParams = JSON.parse(JSON.stringify(params));
      // 工单处理
      let url = 'apiRemote/get_data';
      // 流程 api字段预览/条件判断...
      if (type === 'workflow') {
        url = 'apiRemote/get_data_workflow';
      }
      // 提单节点 特殊处理
      if (type === 'submit') {
        url = 'apiRemote/get_data_receipts';
        reqParams = {
          api_instance_id: field.api_instance_id,
          kv_relation: field.kv_relation,
          fields: reqParams,
        };
      }
      reqParams.id = field.id;
      reqParams.kv_relation = field.kv_relation;
      reqParams.api_instance_id = field.api_instance_id;
      reqParams.api_info = field.api_info;

      return this.$store.dispatch(url, reqParams).then((res) => {
        field.choice = [];
        const choice = res.data.map(item => ({
          // key: item['key'],
          key: item.key || item.id,
          name: item.name,
        }));
        choice.forEach((itemRefresh) => {
          field.choice.push(JSON.parse(JSON.stringify(itemRefresh)));
        });
      })
        .catch((res) => {
          errorHandler(res, this);
        });
    },
    debounce: _.debounce(async (params, itemRelate, vm, type, refreshComp) => {
      if (itemRelate.key === 'priority') {
        vm.get_priority(params, itemRelate, type);
        return false;
      }
      vm.apiRemoteGetData(params, itemRelate, type, refreshComp);
    }, 1000, {
      leading: true,
      trailing: true,
      maxWait: 2000,
    }),
    async isNecessaryToWatch(item, type, refreshComp) {
      const promiseQueue = [];
      item.fields.forEach((field) => {
        // 数组字典
        if (field.type === 'DATADICT' && field.type !== 'TREESELECT') {
          promiseQueue.push(this.get_data_by_key(field));
        }
        // API 优先级
        if ((field.source_type === 'API' || field.key === 'priority')
                    && !field.choice.some(item => item.can_delete)
        ) {
          const params = {
            id: field.id,
            api_instance_id: field.api_instance_id,
            kv_relation: field.kv_relation,
          };
          if (field.related_fields && field.related_fields.rely_on) {
            field.related_fields.rely_on.forEach((itefinal) => {
              const targetField = item.fields.find(f => f.key === itefinal);
              if (targetField) {
                params[itefinal] = targetField.val || '';
              }
            });
          }
          // 没有引用变量的api字段 才可以 发送请求
          if (Object.values(params).every(p => !!p) && item.key !== 'priority') {
            promiseQueue.push(this.apiRemoteGetData(params, field, type));
          }
        }
      });
      Promise.all(promiseQueue).then(() => {
        refreshComp && refreshComp();
      });
      // 1.当前节点是否有引用变量的api字段
      const CurrentApiFields = item.fields.filter(ite => (ite.source_type === 'API' || ite.key === 'priority')
                        && ite.related_fields && ite.related_fields.rely_on
                        && ite.related_fields.rely_on.length);
      if (!CurrentApiFields.length) {
        return;
      }
      let relyOnFieldsKeyList = []; // api字段所依赖字段（全部）
      CurrentApiFields.forEach((ite) => {
        relyOnFieldsKeyList = relyOnFieldsKeyList.concat(ite.related_fields.rely_on);
      });
      // 2.当前节点是否有被引用的字段
      const CurrentreBeReliedFields = item.fields.filter(ite => ite.related_fields && ite.related_fields.be_relied
                        && ite.related_fields.be_relied.length);
      if (!CurrentreBeReliedFields.length) {
        return;
      }
      // 3.当前节点是否有需要监听的 被引用字段 -- 和当前节点的api字段有关联
      const CurrentrelyOnFields = CurrentreBeReliedFields
        .filter(ite => relyOnFieldsKeyList.indexOf(ite.key) !== -1);
      if (!CurrentrelyOnFields.length) {
        return;
      }
      // 4.监听依赖字段 -- api字段所依赖字段（在当前节点的），是否全部填充
      // 监听每个值 // 函数
      const vm = this;

      CurrentrelyOnFields.forEach((ite) => {
        vm.$watch(
          () => ite.val,
          () => {
            // 关联字段 赋值
            if (ite.val) {
              // 相关api字段
              const rca = CurrentApiFields
                .filter(item_ => item_.related_fields.rely_on.indexOf(ite.key) !== -1);
              rca.forEach(async (itemRelate) => {
                // api字段相关依赖
                const relateCurrentreBeRelied = CurrentrelyOnFields
                  .filter(itemRe => itemRelate.related_fields.rely_on.indexOf(itemRe.key) !== -1);
                // 在当前节点的依赖字段 是否全部填充 / isALlFill
                const isALlFill = relateCurrentreBeRelied.every(itemRely => itemRely.val);
                // 是否全部填充 / 非必填 ？
                if (isALlFill || false) {
                  const params = {
                    id: itemRelate.id,
                    api_instance_id: itemRelate.api_instance_id,
                    kv_relation: itemRelate.kv_relation,
                  };
                  if (itemRelate.related_fields && itemRelate.related_fields.rely_on) {
                    itemRelate.related_fields.rely_on.forEach((itefinal) => {
                      const currTargetField = CurrentrelyOnFields.find(f => f.key === itefinal);
                      const targetField = item.fields.find(f => f.key === itefinal);
                      if (targetField) {
                        params[itefinal] = currTargetField.val || '';
                      }
                    });
                  }
                  if (itemRelate.key !== 'priority') {
                    itemRelate.choice.splice(0, itemRelate.choice.length);
                    itemRelate.val = '';
                  }
                  vm.debounce(params, itemRelate, vm, type);
                }
              });
            }
          },
          {
            deep: true,
          }
        );
      });
    },
    // 刷新数据源
    freshApi(item, changeFields, type) {
      const vm = this;
      const params = {};
      const keyList = changeFields.map(itemfiter => itemfiter.key);
      if (item.related_fields && item.related_fields.rely_on) {
        item.related_fields.rely_on.forEach((itefinal) => {
          const relateobj = changeFields.filter(itemFi => itemFi.key === itefinal)[0];
          if (keyList.indexOf(itefinal) !== -1) {
            params[itefinal] = relateobj ? (relateobj.val || '') : '';
          }
          // params[itefinal] = relateobj ? relateobj.val : ''
        });
      }
      // 是否全部填充 / 非必填 ？
      if (Object.values(params).every(item => !!item) || false) {
        item.choice.splice(0, item.choice.length);
        item.val = '';
        vm.debounce(params, item, vm, type);
      }
    },
  },
};
