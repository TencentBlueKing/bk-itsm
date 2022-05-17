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

import isCrossOriginIFrame from './isCrossOriginIFrame.js';

const isCrossOrigin = isCrossOriginIFrame();
const topWindow = isCrossOrigin ? window : window.top;
const topDocument = topWindow.document;
try {
  topWindow.BLUEKING.corefunc.open_login_dialog = openLoginDialog;
  topWindow.BLUEKING.corefunc.close_login_dialog = closeLoginDialog;
} catch (_) {
  topWindow.BLUEKING = {
    corefunc: {
      open_login_dialog: openLoginDialog,
      close_login_dialog: closeLoginDialog,
    },
  };
}
function openLoginDialog(src, width = 400, height = 400, method = 'get') {
  if (!src) return;
  const isWraperExit = topDocument.querySelector('#bk-gloabal-login-iframe');
  if (isWraperExit) return;
  window.needReloadPage = method === 'get'; // 是否需要刷新界面
  const closeIcon = topDocument.createElement('div');
  closeIcon.style.cssText = 'transform: rotate(45deg);position: absolute;right: 0;cursor: pointer;color: #979ba5;width: 26px;height: 26px;';
  const closeIconTop = topDocument.createElement('span');
  closeIconTop.style.cssText = 'width:20px;display:inline-block;border:1px solid #979ba5;position:absolute;top: 50%;';
  const closeIconBottom = topDocument.createElement('span');
  closeIconBottom.style.cssText = 'width:20px;display:inline-block;border:1px solid #979ba5;transform: rotate(90deg);position: absolute;top: 13px;';
  closeIcon.id = 'bk-gloabal-login-close';
  closeIcon.appendChild(closeIconTop);
  closeIcon.appendChild(closeIconBottom);
  topDocument.addEventListener('click', topWindow.BLUEKING.corefunc.close_login_dialog);

  const frame = topDocument.createElement('iframe');
  frame.setAttribute('src', src);
  frame.style.cssText = `border: 0;outline: 0;width:${width}px;height:${height}px;`;

  const dialogDiv = topDocument.createElement('div');
  dialogDiv.style.cssText = 'position: absolute;left: 50%;top: 20%;transform: translateX(-50%);background: #ffffff;';
  dialogDiv.appendChild(closeIcon);
  dialogDiv.appendChild(frame);

  const wraper = topDocument.createElement('div');
  wraper.id = 'bk-gloabal-login-iframe';
  wraper.style.cssText = 'position: fixed;top: 0;bottom: 0;left: 0;right: 0;background-color: rgba(0,0,0,.6);height: 100%;z-index: 3000;';
  wraper.appendChild(dialogDiv);
  topDocument.body.appendChild(wraper);
}
function closeLoginDialog(e) {
  try {
    e.stopPropagation();
    const el = e.target;
    const closeIcon = topDocument.querySelector('#bk-gloabal-login-close');
    if (closeIcon !== el) return;
    topDocument.removeEventListener('click', topWindow.BLUEKING.corefunc.close_login_dialog);
    // if (el) {
    //     el.removeEventListener('click', topWindow.BLUEKING.corefunc.close_login_dialog)
    // }
    topDocument.body.removeChild(el.parentElement.parentElement);
  } catch (_) {
    topDocument.removeEventListener('click', topWindow.BLUEKING.corefunc.close_login_dialog);
    const wraper = topDocument.querySelector('#bk-gloabal-login-iframe');
    if (wraper) {
      topDocument.body.removeChild(wraper);
    }
  }
  window.needReloadPage && window.location.reload();
}
