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

import cloneDeepWith from 'lodash/cloneDeepWith';
import { checkDataType } from './getDataType';
import i18n from '@/i18n/index.js';

export function isVNode(node) {
  return typeof node === 'object' && Object.prototype.hasOwnProperty.call(node, 'componentOptions');
}

export function isInArray(ele, array) {
  for (const item of array) {
    if (item === ele) {
      return true;
    }
  }

  return false;
}

export function isInlineElment(node) {
  const inlineElements = ['a', 'abbr', 'acronym', 'b', 'bdo', 'big', 'br', 'cite', 'code', 'dfn', 'em', 'font', 'i', 'img', 'input', 'kbd', 'label', 'q', 's', 'samp', 'select', 'small', 'span', 'strike', 'strong', 'sub', 'sup', 'textarea', 'tt', 'u', 'var'];
  const tag = (node.tagName).toLowerCase();
  const { display } = getComputedStyle(node);

  if ((isInArray(tag, inlineElements) && display === 'index') || display === 'inline') {
    console.warn('Binding node is displayed as inline element. To avoid some unexpected rendering error, please set binding node displayed as block element.');

    return true;
  }

  return false;
}
export function isEmpty(val) {
  if (val === 0) {
    return false;
  }
  const type = checkDataType(val);
  let isValid = true;
  switch (type) {
    case 'Array':
      isValid = !val.length;
      break;
    case 'Object':
      isValid = JSON.stringify(val) === '{}';
      break;
    default:
      isValid = !val;
  }
  return isValid;
}
/**
 *  获取元素相对于页面的高度
 *  @param node {NodeElement} 指定的DOM元素
 */
export function getActualTop(node) {
  let actualTop = node.offsetTop;
  let current = node.offsetParent;

  while (current !== null) {
    actualTop += current.offsetTop;
    current = current.offsetParent;
  }

  return actualTop;
}

/**
 *  获取元素相对于页面左侧的宽度
 *  @param node {NodeElement} 指定的DOM元素
 */
export function getActualLeft(node) {
  let actualLeft = node.offsetLeft;
  let current = node.offsetParent;

  while (current !== null) {
    actualLeft += current.offsetLeft;
    current = current.offsetParent;
  }

  return actualLeft;
}

/**
 *  对元素添加样式类
 *  @param node {NodeElement} 指定的DOM元素
 *  @param className {String} 类名
 */
export function addClass(node, className) {
  const classNames = className.split(' ');
  if (node.nodeType === 1) {
    if (!node.className && classNames.length === 1) {
      node.className = className;
    } else {
      let setClass = ` ${node.className} `;
      classNames.forEach((cl) => {
        if (setClass.indexOf(` ${cl} `) < 0) {
          setClass += `${cl} `;
        }
      });
      const rtrim = /^\s+|\s+$/;
      node.className = setClass.replace(rtrim, '');
    }
  }
}

/**
 *  对元素删除样式类
 *  @param node {NodeElement} 指定的DOM元素
 *  @param className {String} 类名
 */
export function removeClass(node, className) {
  const classNames = className.split(' ');
  if (node.nodeType === 1) {
    let setClass = ` ${node.className} `;
    classNames.forEach((cl) => {
      setClass = setClass.replace(` ${cl} `, ' ');
    });
    const rtrim = /^\s+|\s+$/;
    node.className = setClass.replace(rtrim, '');
  }
}

/**
 *  将传入的配置项转成本地的对象
 *  @param config {Object} 传入的对象
 *  @return obj {Object} 本地化之后的对象
 */
export function localizeConfig(config) {
  const obj = {};

  for (const key in config) {
    obj[key] = config[key];
  }

  return obj;
}

/**
 *  在一个元素为对象的数组中，根据oldKey: oldValue找到指定的数组元素，并返回该数组元素中指定key的value
 *  @param arr - 元素为对象的数组
 *  @param oldKey - 查找的key
 *  @param oldValue - 查找的value
 *  @param key - 需要返回的value的指定的key
 *  @return result - 找到的value值，未找到返回undefined
 */
export function findValByKeyValue(arr, oldKey, oldValue, key) {
  let result;

  for (const obj of arr) {
    for (const objKey in obj) {
      if (objKey === oldKey && obj[objKey] === oldValue) {
        result = obj[key];

        break;
      }
    }
  }

  return result;
}

/**
 *  在一个元素为对象的数组中，根据oldKey: oldValue找到指定的数组元素，并返回该数组的index
 *  @param arr - 元素为对象的数组
 *  @param oldKey - 查找的key
 *  @param oldValue - 查找的value
 *  @return result - 找到的index值，未找到返回-1
 */
export function findIndexByKeyValue(arr, oldKey, oldValue) {
  let result;

  arr.some((v, i) => {
    for (const objKey in v) {
      if (objKey === oldKey && v[objKey] === oldValue) {
        result = i;
        break;
      }
    }
    return false;
  });
  return result;
}

export function deepClone(obj) {
  return cloneDeepWith(obj);
}

/**
 *  将字符串去掉指定内容之后转成数字
 *  @param {String} str - 需要转换的字符串
 *  @param {String} indicator - 需要被去掉的内容
 */
export function converStrToNum(str, indicator) {
  const reg = new RegExp(indicator, 'g');
  const $str = str.replace(reg, '');

  return ~~$str;
}

/**
 *  将字符串根据indicator转成数组
 */
export function converStrToArr(str, indicator) {
  return str.length ? str.split(indicator) : [];
}

/**
 *  将毫秒值转换成x时x分x秒的形式
 *  @param {Number} time - 时间的毫秒形式
 *  @return {String} str - 转换后的字符串
 */
export function convertMStoString(time) {
  function getSeconds(sec) {
    return `${sec}${window.app.$t('m.js[\'秒\']')}`;
  }

  function getMinutes(sec) {
    if (sec / 60 >= 1) {
      return `${Math.floor(sec / 60)}${window.app.$t('m.js[\'分\']')}${getSeconds(sec % 60)}`;
    }
    return getSeconds(sec);
  }

  function getHours(sec) {
    if (sec / 3600 >= 1) {
      return `${Math.floor(sec / 3600)}${window.app.$t('m.js[\'小时\']')}${getMinutes(sec % 3600)}`;
    }
    return getMinutes(sec);
  }

  function getDays(sec) {
    if (sec / 86400 >= 1) {
      return `${Math.floor(sec / 86400)}${window.app.$t('m.js[\'天\']')}${getHours(sec % 86400)}`;
    }
    return getHours(sec);
  }

  return time ? getDays(Math.floor(time / 1000)) : 0;
}

/**
 * 时间数组转时间戳
 * @param {*} tArr 时间数组 [年，月，日，时，分，秒]
 */
export function convertTimeArrToMS(tArr = [0, 0, 0, 0, 0, 0]) {
  const timeRule = [12, 30, 24, 60, 60];
  return tArr.reduce((pre, num, index) => {
    const r = timeRule.slice(index).reduce((s, n) => {
      s *= n;
      return s;
    }, 1);
    pre += (r * num);
    return pre;
  }, 0);
}

/**
 * 时间数组实例化成 x年 x月 x日 x时 x分 x秒
 * @param {*} tArr 时间数组 [年，月，日，时，分，秒]
 */
export function convertTimeArrToString(tArr = []) {
  if (!(tArr instanceof Array)) return;
  const timeRule = [
    i18n.t('m.newCommon["年"]'),
    i18n.t('m.newCommon["个月"]'),
    i18n.t('m.newCommon["天"]'),
    i18n.t('m.newCommon["小时"]'),
    i18n.t('m.newCommon["分"]'),
    i18n.t('m.newCommon["秒"]'),
  ];
  const str = tArr.reduce((str, num, index) => {
    if (num) {
      str += (num + timeRule[index]);
    }
    return str;
  }, '');
  return str || '0秒';
}

/**
 * 以 baseColor 为基础生成随机颜色
 *
 * @param {string} baseColor 基础颜色
 * @param {number} count 随机颜色个数
 *
 * @return {Array} 颜色数组
 */
export function randomColor(baseColor, count) {
  const segments = baseColor.match(/[\da-z]{2}/g);
  // 转换成 rgb 数字
  for (let i = 0; i < segments.length; i++) {
    segments[i] = parseInt(segments[i], 16);
  }
  const ret = [];
  // 生成 count 组颜色，色差 20 * Math.random
  for (let i = 0; i < count; i++) {
    ret[i] = `#${
      Math.floor(segments[0] + (Math.random() < 0.5 ? -1 : 1) * Math.random() * 20).toString(16)
    }${Math.floor(segments[1] + (Math.random() < 0.5 ? -1 : 1) * Math.random() * 20).toString(16)
    }${Math.floor(segments[2] + (Math.random() < 0.5 ? -1 : 1) * Math.random() * 20).toString(16)}`;
  }
  return ret;
}

/**
 * min max 之间的随机证书
 *
 * @param {number} min 最小值
 * @param {number} max 最大值
 *
 * @return {number} 随机数
 */
export function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min);
}

/**
 * 异常处理
 *
 * @param {Object} err 错误对象
 * @param {Object} ctx 上下文对象，这里主要指当前的 Vue 组件
 */
export function catchErrorHandler(err, ctx) {
  const { data } = err;
  if (data) {
    if (!data.code || data.code === 404) {
      ctx.exceptionCode = {
        code: '404',
        msg: window.app.$t('m.js[\'当前访问的页面不存在\']'),
      };
    } else if (data.code === 403) {
      ctx.exceptionCode = {
        code: '403',
        msg: window.app.$t('m.js[\'Sorry，您的权限不足!\']'),
      };
    } else {
      console.error(err);
      ctx.bkMessageInstance = ctx.$bkMessage({
        theme: 'error',
        message: err.message || err.data.msg || err.statusText,
      });
    }
  } else {
    console.error(err);
    ctx.bkMessageInstance = ctx.$bkMessage({
      theme: 'error',
      message: err.message || err.data.msg || err.statusText,
    });
  }
}
/**
 * 匹配 html 字符串中 a 标签是否有 target 属性，没有则加上 target="_blank"
 */
/* eslint-disable */
export function appendTargetAttrToHtml(html) {
    return html.replace(/\<a (.*?)\>/g, (matchStr) => {
        const targetReg = /target\=[\'\"](.*?)[\'\"]/g;
        const hasTargetAttr = targetReg.test(matchStr);
        return hasTargetAttr
            ? matchStr
            : matchStr.replace(/.$/, ' target="_blank">');
    });
}
/* eslint-disable */

export function debounce(fn, wait) {
    let timeout = null;
    return function () {
        if (timeout !== null) {
            clearTimeout(timeout);
        }
        timeout = setTimeout(fn, wait);
    };
}

export function convertByteToSize(Byte) {
    if (Byte < 1024) {
        return `${Byte}Byte`;
    }
    if (Byte > 1024 && Byte < 10 * 1024) {
        return `${(Byte / 1024).toFixed(2)}KB`;
    }
    return `${(Byte / 1024 / 1024).toFixed(2)}M`;
}
export function getCookie(name) {
  var arr, reg = new RegExp("(^| )" + name + "=([^;]*)(;|$)");
  return (arr = document.cookie.match(reg)) ? unescape(arr[2]) : null;
}

// 适用未对做处理的bk-table 表格头
export function renderHeader(h, { column }) {
  return h('p', { style: { overflow: 'hidden', 'white-space': 'nowrap', 'text-overflow': 'ellipsis' },  directives:[{ name: 'bk-overflow-tips' }]}, [column.label]);
}
