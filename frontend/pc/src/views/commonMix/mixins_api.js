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

import { checkDataType } from '../../utils/getDataType';
import { deepClone } from '../../utils/util';
export default {
  props: {},
  data() {
  },
  created() {
  },
  watch: {},
  methods: {
    // jsonschema --> list
    jsonschemaToList(jsonData) {
      const jsonDataList = [];
      const jsonToListStep = function (jsonDataList, key, valueJsonData, level, requiredList) {
        const valueList = {
          // showChildren: !level,
          showChildren: true,
          checkInfo: false,
          key,
          type: valueJsonData.type || '',
          desc: valueJsonData.description.toString(),
          default: (valueJsonData.default !== undefined
                        && valueJsonData.default.toString()) ? valueJsonData.default : '',
          is_necessary: !level
                        || (!!requiredList && !!requiredList.length && requiredList.indexOf(key) !== -1),
          children: [],
          value: (valueJsonData.default !== undefined) ? valueJsonData.default : '',
        };
        if (valueList.type === 'object') {
          valueList.has_children = !!(valueJsonData.properties
                        && Object.keys(valueJsonData.properties).length);
        }
        if (valueList.type === 'array') {
          valueList.has_children = valueJsonData.items;
          valueList.showChildren = true;
        }
        jsonDataList.push(valueList);
        // jsonDataList[jsonDataList.length-1]['parentInfo'] = level ? jsonDataList[jsonDataList.length-1] : ''
        if (valueList.type === 'object') {
          for (const p in valueJsonData.properties) {
            jsonToListStep(
              valueList.children,
              p,
              valueJsonData.properties[p],
              1,
              valueJsonData.required || []
            );
          }
        }
        if (valueList.type === 'array' && valueJsonData.items) {
          jsonToListStep(valueList.children, 'items', valueJsonData.items, 1, valueJsonData.required || []);
        }
      };
      for (const key in jsonData) {
        jsonToListStep(jsonDataList, key, jsonData[key], 0, ['root']);
      }
      return jsonDataList;
    },
    // list --> jsonschema
    listToJsonschema(listData, isUpdate) {
      // eg:
      // [{
      //     has_children: true,
      //     showChildren: true,
      //     checkInfo: false,
      //     key: 'root',
      //     is_necessary: true,
      //     type: 'object',
      //     desc: '',
      //     children: [
      //         {
      //             has_children: false,
      //             showChildren: false,
      //             checkInfo: false,
      //             key: 'message',
      //             is_necessary: false,
      //             type: 'object',
      //             desc: 'test'
      //         }
      //     ]
      // }]
      const jsonDataDict = {};
      const listToJsonStep = function (jsonDataDict, item, level, lastType) {
        if (!item.key || !item.type) {
          return;
        }
        const valueList = {};
        valueList[item.key] = {
          type: item.type,
          description: item.desc.toString(),
          required: (item.children && item.children.length)
            ? item.children.filter(item => item.is_necessary).map(ite => ite.key) : [],
        };
        if (!valueList[item.key].required.length) {
          delete valueList[item.key].required;
        }
        if (!level) {
          valueList[item.key].$schema = 'http://json-schema.org/draft-04/schema#';
        }
        if (item.type === 'array') {
          if (item.children.length) {
            valueList[item.key].items = {};
          }
          if (lastType === 'array') {
            Object.assign(jsonDataDict, valueList[item.key]);
            for (const j in item.children) {
              listToJsonStep(jsonDataDict.items, item.children[j], 1, 'array');
            }
          }
          if (lastType === 'object') {
            Object.assign(jsonDataDict, valueList);
            for (const j in item.children) {
              listToJsonStep(jsonDataDict[item.key].items, item.children[j], 1, 'array');
            }
          }
        } else if (item.type === 'object') {
          valueList[item.key].properties = {};
          if (lastType === 'array') {
            Object.assign(jsonDataDict, valueList[item.key]);
            for (const j in item.children) {
              listToJsonStep(jsonDataDict.properties, item.children[j], 1, 'object');
            }
          }
          if (lastType === 'object') {
            Object.assign(jsonDataDict, valueList);
            for (const j in item.children) {
              listToJsonStep(jsonDataDict[item.key].properties, item.children[j], 1, 'object');
            }
          }
        } else {
          if (item.default !== undefined && item.default.toString()) {
            if (item.type === 'number') {
              item.default = Number(item.default);
            }
            if (item.type === 'boolean') {
              item.default = !!item.default;
            }
            if (item.type === 'string') {
              item.default = item.default.toString();
            }
          }
          // 根据数据 初始化默认值
          valueList[item.key].default = item.default.toString() ? item.default : '';
          // 更新默认值
          if (item.default_temp !== undefined && item.default_temp.toString()) {
            if (item.type === 'number') {
              item.default_temp = Number(item.default_temp);
            }
            if (item.type === 'boolean') {
              item.default_temp = !!item.default_temp;
            }
            if (item.type === 'string') {
              item.default_temp = item.default_temp.toString();
            }
          }
          // 更新默认值
          if (isUpdate === 'update') {
            valueList[item.key].default = item.default_temp.toString() ? item.default_temp : '';
          }

          if (lastType === 'array') {
            Object.assign(jsonDataDict, valueList[item.key]);
          }
          if (lastType === 'object') {
            Object.assign(jsonDataDict, valueList);
          }
        }
      };
      for (const i in listData) {
        listToJsonStep(jsonDataDict, listData[i], 0, 'object');
      }
      return jsonDataDict;
    },
    // jsonschema --> json
    jsonschemaToJson(schemaData) {
      // eg:
      // {
      //     'root': {
      //         'fields': [
      //             'string'
      //         ],
      //         'condition': {}
      //     }
      // }
      // const reqBody = {
      //     'root': {
      //         '$schema': 'http://json-schema.org/draft-04/schema#',
      //         'type': 'object',
      //         'description': '',
      //         'required': [],
      //         'properties': {
      //             'fields': {
      //                 'type': 'array',
      //                 'items': {
      //                     'type': 'string',
      //                     'description': '字段名'
      //                 },
      //                 'description': this.$t(`m.systemConfig['指定查询的字段，参数为业务的任意属性，如果不填写字段信息，系统会返回业务的所有字段']`)
      //             },
      //             'condition': {
      //                 'type': 'object',
      //                 'properties': {},
      //                 'description': this.$t(`m.systemConfig['查询条件，参数为业务的任意属性，如果不写代表搜索全部数据']`)
      //             },
      //             'page': {
      //                 'type': 'object',
      //                 'properties': {
      //                     'start': {
      //                         'type': 'integer',
      //                         'description': this.$t(`m.systemConfig['记录开始位置']`)
      //                     },
      //                     'limit': {
      //                         'type': 'integer',
      //                         'description': this.$t(`m.systemConfig['每页限制条数,最大200']`)
      //                     },
      //                     'sort': {
      //                         'type': 'string',
      //                         'description': '排序字段，通过在字段前面增加 -，如 sort:"-field" 可以表示按照字段 field降序'
      //                     }
      //                 },
      //                 'description': this.$t(`m.systemConfig['分页条件']`),
      //                 'required': [
      //                     'start',
      //                     'limit'
      //                 ]
      //             }
      //         }
      //     }
      // }
      const jsonDataDict = {};
      const listToJsonStep = function (jsonDataDict, key, item, level, lastType) {
        const valueList = {};
        if (item.type === 'object') {
          valueList[key] = {};
          if (lastType === 'object') {
            Object.assign(jsonDataDict, valueList);
            for (const i in item.properties) {
              listToJsonStep(jsonDataDict[key], i, item.properties[i], 1, 'object');
            }
          } else if (lastType === 'array') {
            jsonDataDict.push(valueList[key]);
            for (const i in item.properties) {
              listToJsonStep(jsonDataDict[0], i, item.properties[i], 1, 'object');
            }
          }
        } else if (item.type === 'array') {
          valueList[key] = [];
          if (lastType === 'object') {
            Object.assign(jsonDataDict, valueList);
            if (item.children && item.children.length) {
              listToJsonStep(jsonDataDict[key], 'items', item.items, 1, 'array');
            }
          } else if (lastType === 'array') {
            jsonDataDict.push(valueList[key]);
            if (item.children && item.children.length) {
              listToJsonStep(jsonDataDict[0], key, item.items, 1, 'array');
            }
          }
        } else {
          switch (item.type) {
            case 'boolean':
              // valueList[key] = item.description !== '' ? item.description : true
              valueList[key] = !!item.default;
              break;
            case 'number':
              // valueList[key] = item.description !== '' ? Number(item.description) : 0
              valueList[key] = Number(item.default);
              break;
            case 'string':
              // valueList[key] = item.description !== '' ? item.description : 'string'
              valueList[key] = item.default.toString() || '';
              break;
            default:
              break;
          }
          if (lastType === 'object') {
            Object.assign(jsonDataDict, valueList);
          } else if (lastType === 'array') {
            jsonDataDict.push(valueList[key]);
          }
        }
      };
      for (const i in schemaData) {
        listToJsonStep(jsonDataDict, i, schemaData[i], 0, 'object');
      }
      return jsonDataDict;
    },
    // json --> jsonschema
    jsonToJsonschema(jsonData) {
      const jsonDataDict = {
        root: {
          $schema: 'http://json-schema.org/draft-04/schema#',
          type: 'object',
          description: this.$t('m.systemConfig["初始化数据"]'),
          required: [],
          properties: {},
        },
      };

      const listToJsonStep = function (lastObject, insertObject, key, item, lastType) {
        if (!key || item === undefined || item === null) {
          return;
        }
        if (lastObject.type !== 'array') {
          lastObject.required.push(key); // 默认必须
        }
        const valueList = {};
        valueList[key] = {
          type: item.constructor.name.toLowerCase(),
          description: '',
          required: [],
        };

        if (item.constructor.name.toLowerCase() === 'array') {
          if (item.length) {
            valueList[key].items = {};
          }
          if (lastType === 'array') {
            Object.assign(insertObject, valueList[key]);
            for (const j in item) {
              listToJsonStep(insertObject, insertObject.items, 'items', item[j], 'array');
            }
          }
          if (lastType === 'object') {
            Object.assign(insertObject, valueList);
            for (const j in item) {
              listToJsonStep(insertObject[key], insertObject[key].items, 'items', item[j], 'array');
            }
          }
        } else if (item.constructor.name.toLowerCase() === 'object') {
          valueList[key].properties = {};
          if (lastType === 'array') {
            Object.assign(insertObject, valueList[key]);
            for (const j in item) {
              listToJsonStep(insertObject, insertObject.properties, j, item[j], 'object');
            }
          }
          if (lastType === 'object') {
            Object.assign(insertObject, valueList);
            if (Object.keys(item).length) {
              for (const j in item) {
                listToJsonStep(insertObject[key], insertObject[key].properties, j, item[j], 'object');
              }
            }
          }
        } else {
          // valueList[key]['description'] = item.toString()
          if (item !== undefined && item.toString()) {
            if (item.constructor.name.toLowerCase() === 'number') {
              item = Number(item);
            }
            if (item.constructor.name.toLowerCase() === 'boolean') {
              item = !!item;
            }
            if (item.constructor.name.toLowerCase() === 'string') {
              item = item.toString();
            }
          }
          valueList[key].default = item;
          if (lastType === 'array') {
            Object.assign(insertObject, valueList[key]);
          }
          if (lastType === 'object') {
            Object.assign(insertObject, valueList);
          }
        }
      };
      for (const key in jsonData) {
        listToJsonStep(jsonDataDict.root, jsonDataDict.root.properties, key, jsonData[key], 'object');
      }
      return jsonDataDict;
    },
    treeToTableList(treeDataList, levelInitial, parentPrimaryKeyInitial, lastTypeInitial, ancestorsListInitial) {
      // eg:
      // this.apiDetailInfo['treeDataList'] = [{
      //     has_children: false,
      //     showChildren: false,
      //     checkInfo: false,
      //     key: 'root',
      //     is_necessary: true,
      //     type: 'object',
      //     desc: this.$t(`m.systemConfig["'初始化数据'"]`),
      //     parentInfo: '',
      //     children: [
      //     ]
      // }]
      const listData = [];
      const jsonToListStep = function (listData, treeDataList, level, parentPrimaryKey, lastType, ancestorsList) {
        for (let i = 0; i < treeDataList.length; i++) {
          treeDataList[i].lastType = lastType;
          treeDataList[i].level = level;
          treeDataList[i].isShow = true;
          treeDataList[i].showChildren = true;
          treeDataList[i].primaryKey = `${level}_${treeDataList[i].key}`;
          if (lastType === 'array') {
            treeDataList[i].primaryKey += `_${i}`;
          }
          treeDataList[i].parentPrimaryKey = parentPrimaryKey;
          treeDataList[i].ancestorsList = ancestorsList;
          const ancestorsListAdd = [...ancestorsList, treeDataList[i].primaryKey]; // 生成唯一标识
          treeDataList[i].ancestorsList_str = ancestorsListAdd.toString();
          listData.push(treeDataList[i]);
          if (treeDataList[i].children && treeDataList[i].children.length) {
            jsonToListStep(
              listData,
              treeDataList[i].children,
              level + 1,
              treeDataList[i].primaryKey,
              treeDataList[i].type,
              ancestorsListAdd
            );
          }
        }
      };

      jsonToListStep(
        listData,
        treeDataList,
        levelInitial || 0,
        parentPrimaryKeyInitial || '',
        lastTypeInitial || 'object',
        ((ancestorsListInitial && ancestorsListInitial.length) ? ancestorsListInitial : [])
      );
      return listData;
    },
    // list --> jsonschema
    treeToJson(listData) {
      // eg:
      // const treeDataList = [{
      //     has_children: true,
      //     showChildren: true,
      //     checkInfo: false,
      //     key: 'root',
      //     is_necessary: true,
      //     type: 'object',
      //     desc: '',
      //     children: [
      //         {
      //             has_children: false,
      //             showChildren: false,
      //             checkInfo: false,
      //             key: 'message',
      //             is_necessary: false,
      //             type: 'object',
      //             desc: 'test'
      //         }
      //     ]
      // }]
      const jsonDataDict = {};
      const treeToJsonStep = function (jsonDataDict, item, level, lastType) {
        if (!item.key) {
          return;
        }
        if (item.type === 'array') {
          const baseItem = [];
          if (lastType === 'array') {
            jsonDataDict.push(baseItem);
            for (const j in item.children) {
              treeToJsonStep(jsonDataDict[jsonDataDict.length - 1], item.children[j], 1, 'array');
            }
          }
          if (lastType === 'object') {
            const baseItem = {};
            baseItem[item.key] = [];
            Object.assign(jsonDataDict, baseItem);
            for (const j in item.children) {
              treeToJsonStep(jsonDataDict[item.key], item.children[j], 1, 'array');
            }
          }
        } else if (item.type === 'object') {
          const baseItem = {};
          if (lastType === 'array') {
            jsonDataDict.push(baseItem);
            for (const j in item.children) {
              treeToJsonStep(jsonDataDict[jsonDataDict.length - 1], item.children[j], 1, 'object');
            }
          }
          if (lastType === 'object') {
            baseItem[item.key] = {};
            Object.assign(jsonDataDict, baseItem);
            for (const j in item.children) {
              treeToJsonStep(jsonDataDict[item.key], item.children[j], 1, 'object');
            }
          }
        } else {
          if (item.type === 'number') {
            item.value = Number(item.value);
          }
          if (lastType === 'array') {
            const baseItem = item.source_type === 'CUSTOM' ? item.value
              : `\${params_${item.value_key}}`;
            jsonDataDict.push(baseItem);
          }
          if (lastType === 'object') {
            const baseItem = {};
            baseItem[item.key] = item.source_type === 'CUSTOM' ? item.value
              : `\${params_${item.value_key}}`;
            Object.assign(jsonDataDict, baseItem);
          }
        }
      };
      for (const i in listData) {
        treeToJsonStep(jsonDataDict, listData[i], 0, 'object');
      }
      return jsonDataDict;
    },
    jsonValueToTree(jsonData, treeDataList) {
      const list = deepClone(treeDataList);
      // eg:
      // const treeDataListEg = [{
      //     has_children: true,
      //     showChildren: true,
      //     checkInfo: false,
      //     key: 'root',
      //     is_necessary: true,
      //     type: 'object',
      //     desc: '',
      //     children: [
      //         {
      //             has_children: false,
      //             showChildren: false,
      //             checkInfo: false,
      //             key: 'message',
      //             is_necessary: false,
      //             type: 'object',
      //             desc: 'test'
      //         }
      //     ]
      // }]

      const listToJsonStep = function (insertObject, key, dataItem, lastType) {
        const dataItemType = checkDataType(dataItem);

        if (lastType === 'object') {
          const reqData = insertObject.find(ite => ite.key === key);
          if (!reqData) {
            return;
          }
          // reqData[0]
          if (dataItemType === 'Array') {
            if (!reqData.children || !reqData.children.length) {
              return;
            }
            const oneItem = Object.assign({ parentInfo: '' }, reqData.children[0]);
            for (let i = 1; i < dataItem.length; i++) {
              reqData.children.push(deepClone(oneItem));
            }
            for (const j in dataItem) {
              listToJsonStep(reqData.children[j], 'items', dataItem[j], 'array');
            }
          } else if (dataItemType === 'Object') {
            for (const j in dataItem) {
              listToJsonStep(reqData.children, j, dataItem[j], 'object');
            }
          } else {
            if (/^\$\{params_.*\}$/.test(dataItem)) {
              reqData.source_type = 'FIELDS';
              reqData.value_key = dataItem ? deepClone(dataItem).replace(/^\$\{params_/, '')
                .replace(/\}$/, '') : '';
              reqData.value = (dataItem !== undefined && dataItem.toString()) ? deepClone(dataItem) : '';
            } else {
              reqData.source_type = 'CUSTOM';
              reqData.value = (dataItem !== undefined && dataItem.toString()) ? deepClone(dataItem) : '';
              reqData.value_key = '';
              // 改变默认值
              reqData.default_temp = reqData.value;
            }
          }
        } else if (lastType === 'array') {
          if (dataItemType === 'Array') {
            const reqData = insertObject.find(ite => ite.key === key);
            if (!reqData) {
              return;
            } // 待定？？？
            if (!reqData.children || !reqData.children.length) {
              return;
            }
            const oneItem = insertObject.children[0];
            for (let i = 1; i < dataItem.length; i++) {
              insertObject.children.push(deepClone(oneItem));
            }
            for (const j in dataItem) {
              listToJsonStep(insertObject.children[j], 'items', dataItem[j], 'array');
            }
          } else if (dataItemType === 'Object') {
            for (const j in dataItem) {
              listToJsonStep(insertObject.children, j, dataItem[j], 'object');
            }
          } else {
            if (/^\$\{params_.*\}$/.test(dataItem)) {
              insertObject.source_type = 'FIELDS';
              insertObject.value_key = dataItem ? deepClone(dataItem).replace(/^\$\{params_/, '')
                .replace(/\}$/, '') : '';
            } else {
              insertObject.source_type = 'CUSTOM';
              insertObject.value = (dataItem !== undefined && dataItem.toString()) ? deepClone(dataItem) : '';
              // 改变默认值
              insertObject.default_temp = insertObject.value;
            }
          }
        }
      };
      for (const key in jsonData) {
        listToJsonStep(list[0].children, key, jsonData[key], 'object');
      }
      return list;
    },
  },
};
