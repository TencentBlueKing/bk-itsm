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

module.exports = ({ file }) => {
  return {
    plugins: [
      require('postcss-normalize'),
      require('postcss-import'),
      // require('stylelint'),
      require('postcss-advanced-variables'),
      require('postcss-nested'),
      require('postcss-mixins'),
      require('postcss-preset-env'),
      // 采用 rem 布局时打开， 插件地址：https://github.com/songsiqi/px2rem
      // require('postcss-px2rem')({
      //   remUnit: 75
      // }),
      // 使用 vw 布局时打开，配置项参考：https://github.com/evrone/postcss-px-to-viewport
      require('postcss-px-to-viewport')({
        viewportWidth: file && file.dirname && file.dirname.includes("vant") ? 375 : 750,
        unitPrecision: 5,
        selectorBlackList: []
      }),
      require('autoprefixer'),
      require('cssnano')
    ]
  }
}