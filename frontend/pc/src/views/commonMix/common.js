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

export default {
  data() {
    return {
      commonRules: {
        key: [
          {
            required: true,
            message: this.$t('m.systemConfig["编码格式为英文数字及下划线"]'),
            trigger: 'blur',
          },
          {
            regex: /^[a-zA-Z0-9_]+$/,
            message: this.$t('m.systemConfig["编码格式为英文数字及下划线"]'),
            trigger: 'blur',
          },
        ],
        name: [
          {
            required: true,
            message: this.$t('m.systemConfig["格式为长度小于120"]'),
            trigger: 'blur',
          },
          {
            max: 120,
            message: this.$t('m.systemConfig["格式为长度小于120"]'),
            trigger: 'blur',
          },
        ],
        smallName: [
          {
            required: true,
            message: this.$t('m.systemConfig["格式为长度不超过8个字符"]'),
            trigger: 'blur',
          },
          {
            max: 8,
            message: this.$t('m.systemConfig["格式为长度不超过8个字符"]'),
            trigger: 'blur',
          },
        ],
        select: [
          {
            required: true,
            message: this.$t('m.treeinfo["字段必填"]'),
            trigger: 'blur',
          },
        ],
        color: [
          {
            regex: /^#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$/,
            message: this.$t('m.slaContent["请输入3位或6位合法色值"]'),
            trigger: 'blur',
          },
        ],
        multipleSelect: [
          {
            validator(val) {
              return val.length >= 1;
            },
            message: this.$t('m.treeinfo["字段必填"]'),
            trigger: 'blur',
          },
        ],
        required: [
          {
            validator(val) {
              if (Array.isArray(val)) {
                return val.length >= 1;
              }
              return !!val;
            },
            message: this.$t('m.treeinfo["字段必填"]'),
            trigger: 'input',
          },
        ],
      },
      keyList: {
        name: ['name', 'dayName'],
        key: ['key'],
        select: ['select', 'dayTime', 'schedule', 'handle_time', 'value'],
        color: ['color'],
        multipleSelect: ['multipleSelect'],
        required: ['required'],
      },
    };
  },
  computed: {
    globalChoise() {
      return this.$store.state.common.configurInfo;
    },
  },
  methods: {
    // 字段间关系校验
    relatedRegex(list, allList) {
      const allRelateList = [];
      for (let i = 0; i < list.length; i++) {
        if (list[i].showFeild && list[i].regex === 'ASSOCIATED_FIELD_VALIDATION' && list[i].regex_config.rule && list[i].regex_config.rule.expressions && list[i].regex_config.rule.expressions.length) {
          const linkRule = list[i].regex_config.rule.type;
          const relateResult = {
            validList: [],
            result: '',
          };
          for (let j = 0; j < list[i].regex_config.rule.expressions.length; j++) {
            // 字段和系统间的校验
            if (list[i].regex_config.rule.expressions[j].source === 'system') {
              if (list[i].regex_config.rule.expressions[j].key === 'system_time') {
                const val1 = new Date(list[i].val).getTime();
                const val2 = new Date().getTime();
                const result = this.checkExpressionResult(
                  { name: list[i].name, val: val1, key: list[i].key },
                  { name: this.$t('m.common["系统时间"]'), val: val2 },
                  list[i].regex_config.rule.expressions[j].condition,
                  list[i].type
                );
                relateResult.validList.push(result);
                break;
              }
            }
            // 字段与字段间的校验
            for (let k = 0; k < allList.length; k++) {
              if (list[i].regex_config.rule.expressions[j].key === allList[k].key && allList[k].showFeild) {
                const val1 = list[i].type === 'INT' ? list[i].val : new Date(list[i].val).getTime();
                const val2 = allList[k].type === 'INT' ? allList[k].val : new Date(allList[k].val).getTime();
                const result = this.checkExpressionResult(
                  { name: list[i].name, val: val1, key: list[i].key },
                  { name: allList[k].name, val: val2 },
                  list[i].regex_config.rule.expressions[j].condition,
                  list[i].type
                );
                relateResult.validList.push(result);
                break;
              }
            }
          }
          // 当validList为空并且or返回true
          relateResult.result = linkRule === 'and' ? relateResult.validList.every(val => val.valid) : (!relateResult.validList.length || relateResult.validList.some(val => val.valid));
          allRelateList.push(relateResult);
        }
      }
      return {
        validList: allRelateList,
        result: allRelateList.every(val => val.result),
      };
    },
    /**
         * 校验比较的两个值是否满足条件
         * @param {Object} left 左边值信息
         * @param {Object} right 右边值信息
         * @param {String} condition 条件
         * @param {String} type 字段类型
         */
    checkExpressionResult(left, right, condition, type) {
      let result = {};
      const val1 = left.val;
      const val2 = right.val;
      const name1 = left.name;
      const name2 = right.name;
      switch (condition) {
        case '>':
          result = {
            valid: val1 > val2,
            tips: `"${name1}"${type === 'INT' ? this.$t('m.newCommon["应大于"]') : this.$t('m.newCommon["应晚于"]')}"${name2}"`,
          };
          break;
        case '<':
          result = {
            valid: val1 < val2,
            tips: `"${name1}"${type === 'INT' ? this.$t('m.newCommon["应小于"]') : this.$t('m.newCommon["应早于"]')}"${name2}"`,
          };
          break;
        case '==':
          result = {
            valid: val2 === val1,
            tips: `"${name1}"${this.$t('m.newCommon["应等于"]')}"${name2}"`,
          };
          break;
        case '<=':
          result = {
            valid: val1 <= val2,
            tips: `"${name1}"${type === 'INT' ? this.$t('m.newCommon["应不大于"]') : this.$t('m.newCommon["应不晚于"]')}"${name2}"`,
          };
          break;
        case '>=':
          result = {
            valid: val1 >= val2,
            tips: `"${name1}"${type === 'INT' ? this.$t('m.newCommon["应不小于"]') : this.$t('m.newCommon["应不早于"]')}"${name2}"`,
          };
          break;
        default:
          break;
      }
      result.key = left.key;
      return result;
    },
    standardTime(value) {
      if (!value) {
        return '';
      }
      const d = new Date(value);
      // 时分秒进行补0处理
      const hours = this.addZero(d.getHours());
      const minutes = this.addZero(d.getMinutes());
      const seconds = this.addZero(d.getSeconds());
      const gteTime = `${d.getFullYear()}-${this.addZero((d.getMonth() + 1))}-${this.addZero(d.getDate())} ${hours}:${minutes}:${seconds}`;
      return gteTime;
    },
    standardDayTime(value) {
      if (!value) {
        return '';
      }
      const d = new Date(value);
      // 年月进行补0处理
      const gteTime = `${d.getFullYear()}-${this.addZero((d.getMonth() + 1))}-${this.addZero(d.getDate())}`;
      return gteTime;
    },
    addZero(value) {
      const backValue = value >= 10 ? value : (`0${value}`);
      return backValue;
    },
    checkCommonRules(value) {
      const rule = {};
      if (this.keyList.name.some(item => value === item)) {
        rule[value] = this.commonRules.name;
      } else if (this.keyList.key.some(item => value === item)) {
        rule[value] = this.commonRules.key;
      } else if (this.keyList.select.some(item => value === item)) {
        rule[value] = this.commonRules.select;
      } else if (this.keyList.color.some(item => value === item)) {
        rule[value] = this.commonRules.color;
      } else if (this.keyList.multipleSelect.some(item => value === item)) {
        rule[value] = this.commonRules.multipleSelect;
      } else if (this.keyList.required.some(item => value === item)) {
        rule[value] = this.commonRules.required;
      }
      return rule;
    },
    // 数据装换
    typeTransition(type) {
      if (this.globalChoise.field_type) {
        const typeValue = this.globalChoise.field_type.filter(item => item.typeName === type);
        return typeValue.length ? typeValue[0].name : '';
      }
    },
    valueTransition(item) {
      if (this.globalChoise.field_type) {
        let contentValue = '';
        if (item.type === 'FILE') {
          const tempNameList = [];
          for (const key in item.choice) {
            tempNameList.push(item.choice[key].name);
          }
          contentValue = tempNameList.join(',');
        } else {
          contentValue = item.choice.map(node => node.name).join(',');
        }
        return contentValue;
      }
    },
    // 格式化处理数据格式（数字，时间，数组，日期，布尔值）
    formattingData(node) {
      let returnValue = '';
      // 数据
      if (Array.isArray(node.value)) {
        returnValue = node.value.join(',');
      } else {
        if (node.type === 'INT') {
          returnValue = node.value === '' ? '' : Number(node.value);
        } else if (node.type === 'BOOLEAN') {
          returnValue = !!Number(node.value);
        } else if (node.type === 'DATETIME') {
          returnValue = this.standardTime(node.value);
        } else if (node.type === 'DATE') {
          returnValue = this.standardDayTime(node.value);
        } else {
          returnValue = node.value;
        }
      }
      return returnValue;
    },
    fieldFormatting(valueList) {
      for (const item of valueList) {
        if (!item.showFeild) {
          continue;
        }
        item.value = item.val;
        if (item.type === 'DATETIME' || item.type === 'DATE') {
          item.value = this.formattingData(item);
        }
        if (item.type !== 'CUSTOMTABLE' && item.type !== 'TABLE') {
          item.value = this.formattingData(item);
        }
        if (item.type === 'CUSTOMTABLE') {
          // 通过meta.columns来判断哪些属于需要转换的key值
          const dateList = [];
          const datetimeList = [];
          item.meta.columns.forEach((meta) => {
            if (meta.display === 'date') {
              dateList.push(meta.key);
            }
            if (meta.display === 'datetime') {
              datetimeList.push(meta.key);
            }
          });
          Array.isArray(item.value) && item.value.forEach((itemValue) => {
            for (const key in itemValue) {
              if (dateList.some(meta => meta === key)) {
                itemValue[key] = this.standardDayTime(itemValue[key]);
              }
              if (datetimeList.some(meta => meta === key)) {
                itemValue[key] = this.standardTime(itemValue[key]);
              }
            }
          });
        }
      }
    },
    /**
         * 比较两个节点信息，是不是同一个节点,且状态信息一致
         * 需要注意的是新旧节点的 fields 信息不一定一致是正常的，因为旧节点 fields 中 value 会有更新（用户已填写内容）
         */
    isSameStatusNode(nodeA, nodeB) {
      return nodeA && nodeB
                && nodeA.status === nodeB.status
                && nodeA.state_id === nodeB.state_id
                && nodeA.fields.length === nodeB.fields.length
                && nodeA.operations.length === nodeB.operations.length
                && nodeA.can_operate === nodeB.can_operate
                && nodeA.is_schedule_ready === nodeB.is_schedule_ready;
    },
  },
};
