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

import { deepClone } from '@/utils/util';

// TODO: 现有字段渲染公共方法梳理整合
// export const formattingData = (node) => {

// }
// export const fieldFormatting = (valueList) => {

// }

/**
 * 获取自定义表格每个单元格的显示值
 * @param {Object} column 表头信息
 * @param {Object} row 行数据
 */
export const getCustomTableDisplayValue = (column, row) => {
  const val = deepClone(row[column.key]);
  if (column && (column.display === 'multiselect' || column.display === 'select')) {
    const vals = typeof val === 'string' ? [val] : val;
    const names = vals.map((val) => {
      // 兼容脏数据，正常情况下自定义表格中select存的是 key,之前也有可能存的 name（流程打回时错误将key转name，直接保存）
      const seletedOption = column.choice.find(oneChoice => oneChoice.key === val || oneChoice.name === val);
      return seletedOption ? seletedOption.name : '';
    });
    return names.join(',');
  }
  return val;
};

// 单个字段
export class Field {
  constructor(type, defaultValueMap) {
    this.prevId = ''; // 前置节点 id
    this.name = ''; // 名称
    this.type = type; // 类型
    this.regex = ''; // 校验
    this.regex_config = {
      rule: {
        expressions: [],
        type: 'and',
      },
    };
    this.customRegex = '';
    this.source_type = '';
    this.source_uri = '';
    this.default_value = '';
    this.layout = '';
    this.validate = '';
    this.desc = '';
    this.is_tips = '';
    this.tips = '';
    this.show_type = '';
    this.show_conditions = {};
    this.setDefaultValue(defaultValueMap);
  }
  setDefaultValue(defaultValueMap) {
    const self = this;
    Object.keys(defaultValueMap).forEach((key) => {
      self[key] = defaultValueMap[key];
    });
  }
}
