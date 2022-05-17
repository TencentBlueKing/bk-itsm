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

/**
 * 在输入框光标处插入字符
 * @param {Object} el dom 元素
 * @param {String} name 唯一标识符，类似 id
 * @param {String} addText 需要插入的字符
 * @param {Object} instance vue 实例 （this）
 */
function insertText(el, name, oldValue, addText, instance) {
  const recordStr = sessionStorage.getItem('cursorIndex');
  const recordJson = recordStr && JSON.parse(recordStr);
  if (
    !el
        || (!el.selectionStart && el.selectionStart !== 0)
        || recordJson.name !== name) {
    return oldValue + addText;
  }
  const { start, end } = recordJson;
  const { scrollTop } = el;
  instance.$nextTick(() => {
    el.selectionStart = start + addText.length;
    el.selectionEnd = start + addText.length;
    el.scrollTop = scrollTop;
    el.focus();
  });
  return oldValue.substr(0, start) + addText + oldValue.substr(end);
}
export default insertText;
