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

// import ajax from '@/utils/ajax'
import { errorHandler } from '../../utils/errorHandler';
export default {
  methods: {
    // 自定义表单数据处理
    async getFieldOptions(item) {
      let data = [];
      switch (item.source_type) {
        case 'CUSTOM':
          data = item.choice;
          break;
        case 'API':
          data = [];
          item.choice.forEach((node) => {
            data.push({
              key: String(node.id || node.key),
              name: node.name,
              can_delete: Boolean(node.can_delete),
            });
            // data.push(node)
          });
          break;
        case 'DATADICT':
          data = [];
          if (item.choice.some(it => it.can_delete)) {
            data = item.choice;
            break;
          }
          if (item.type !== 'TREESELECT') {
            // 请求数据字典数据
            await this.$store.dispatch('datadict/get_data_by_key', {
              key: item.source_uri,
              field_key: item.key,
              service: item.service,
              current_status: item.ticket_status,
            }).then((res) => {
              data = res.data.map((ite) => {
                const temp = {
                  key: ite.key,
                  name: ite.name,
                };
                if (item.key === 'current_status') {
                  this.$set(temp, 'isOver', ite.is_over);
                }
                return temp;
              });
            })
              .catch((res) => {
                errorHandler(res, this);
              });
          }
          break;
        case 'RPC':
          // 获取rpc数据
          data = [];
          if (item.choice.some(it => it.can_delete)) {
            data = item.choice;
            break;
          }
          await this.$store.dispatch('apiRemote/getRpcData', item).then((res) => {
            data = res.data;
          })
            .catch((res) => {
              errorHandler(res, this);
            });
          break;
      }
      return data;
    },
    // 判断值是否合理
    judgeValue(value, list) {
      if (value) return list.some(item => value.toString().indexOf(item.key) !== -1);
    },
    // 关联数据展示的逻辑处理
    conditionField(item, list) {
      for (let i = 0; i < list.length; i++) {
        // eslint-disable-next-line
                if (list[i].show_type || (!list[i].hasOwnProperty('show_conditions') && (!list[i].hasOwnProperty('show_result') || list[i].show_result))) {
          list[i].showFeild = true;
          continue;
        }
        // 对于没有expressions字段的参数，跳过逻辑处理
        if (list[i].show_conditions.expressions && list[i].show_conditions.expressions.length) {
          for (let j = 0; j < list[i].show_conditions.expressions.length; j++) {
            // 当当前操作的字段内存在自己配置自己的情况，则忽略配置条件
            if (item.key === list[i].show_conditions.expressions[j].key
                            && item.key === list[i].key
                            && list[i].value === null) {
              list[i].showFeild = true;
            } else {
              // 当前节点的类型和expressions的数据一样时，进行处理
              if (item.key === list[i].show_conditions.expressions[j].key) {
                if (list[i].show_conditions.expressions.length === 1) {
                  list[i].showFeild = this.conditionSwitch(
                    item,
                    list[i].show_conditions.expressions[j]
                  );
                } else {
                  // 区分条件组‘and’和‘or’的判断逻辑
                  if (list[i].show_conditions.type === 'and') {
                    // 判断其他字段和关联字段的关系
                    const statusList = [];
                    for (let z = 0; z < list[i].show_conditions.expressions.length; z++) {
                      for (let s = 0; s < list.length; s++) {
                        if (list[i].show_conditions.expressions[z].key === list[s].key) {
                          const valueStatus = this.conditionSwitch(
                            list[s],
                            list[i].show_conditions.expressions[z]
                          );
                          statusList.push(valueStatus);
                        }
                      }
                    }
                    // 判断当前字段与关联字段的关系
                    list[i].showFeild = statusList.every(status => !!status);
                  } else {
                    // 判断其他字段和关联字段的关系
                    const statusList = [];
                    for (let z = 0; z < list[i].show_conditions.expressions.length; z++) {
                      for (let s = 0; s < list.length; s++) {
                        if (list[i].show_conditions.expressions[z].key === list[s].key) {
                          const valueStatus = this.conditionSwitch(
                            list[s],
                            list[i].show_conditions.expressions[z]
                          );
                          statusList.push(valueStatus);
                        }
                      }
                    }
                    list[i].showFeild = statusList.some(status => !!status);
                  }
                }
                list[i].showFeild = !list[i].showFeild;
              }
            }
          }
        }
      }
    },
    conditionSwitch(item, value) {
      let statusInfo = false;
      const typeList = ['CHECKBOX', 'MEMBERS', 'MULTISELECT', 'TREESELECT'];
      switch (value.condition) {
        case '==': {
          if (typeList.some(type => type === item.type)) {
            const valList = value.value.split(',');
            const statusList = valList.map(val => item.val.indexOf(val) === -1);
            statusInfo = ((statusList.every(status => !status)) && item.val.length === value.value.length);
          } else {
            statusInfo = (item.val === value.value || Number(item.val) === Number(value.value));
          }
          break;
        }
        case '!=': {
          if (typeList.some(type => type === item.type)) {
            const valList = value.value.split(',');
            const statusList = valList.map(val => item.val.indexOf(val) === -1);
            statusInfo = statusList.some(status => !!status)
              ? statusList.some(status => !!status) : item.val.length !== value.value.length;
          } else {
            statusInfo = (item.val !== value.value && Number(item.val) !== Number(value.value));
          }
          break;
        }
        case '>': {
          if (item.type === 'DATE' || item.type === 'DATETIME') {
            statusInfo = this.timeStamp(item.val) > this.timeStamp(value.value);
          } else {
            statusInfo = Number(item.val) > Number(value.value);
          }
          break;
        }
        case '<': {
          if (item.type === 'DATE' || item.type === 'DATETIME') {
            statusInfo = this.timeStamp(item.val) < this.timeStamp(value.value);
          } else {
            statusInfo = Number(item.val) < Number(value.value);
          }
          break;
        }
        case '>=': {
          if (item.type === 'DATE' || item.type === 'DATETIME') {
            statusInfo = this.timeStamp(item.val) >= this.timeStamp(value.value);
          } else {
            statusInfo = Number(item.val) >= Number(value.value);
          }
          break;
        }
        case '<=': {
          if (item.type === 'DATE' || item.type === 'DATETIME') {
            statusInfo = this.timeStamp(item.val) <= this.timeStamp(value.value);
          } else {
            statusInfo = Number(item.val) <= Number(value.value);
          }
          break;
        }
        case 'issuperset': {
          const issupersetList = value.value.split(',');
          const statusList = issupersetList.map(val => item.val.indexOf(val) === -1);
          statusInfo = statusList.every(status => !status);
          break;
        }
        case 'notissuperset': {
          const valnoList = value.value.split(',');
          const statusnoList = valnoList.map(val => item.val.indexOf(val) === -1);
          statusInfo = !statusnoList.every(status => !status);
          break;
        }
        default: {
          statusInfo = true;
        }
      }
      return statusInfo;
    },
    // 时间字符转换成时间戳
    timeStamp(timeValue) {
      const timeInfo = timeValue.replace(/-/g, '/');
      const timeStampValue = new Date(timeInfo).getTime();
      return timeStampValue;
    },
  },
};
