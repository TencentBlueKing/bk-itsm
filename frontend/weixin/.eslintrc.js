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
 * @file 蓝鲸前端代码 ESLint 规则 Vue
 * bkfe
 */

module.exports = {
    parser: 'vue-eslint-parser',
    parserOptions: {
        parser: '@typescript-eslint/parser',
        ecmaVersion: 2018,
        sourceType: 'module',
        extraFileExtensions: ['.vue'],
        ecmaFeatures: {
            jsx: true,
            modules: true
        }
    },
    extends: [
        'plugin:vue/vue3-recommended',
        'eslint-config-tencent'
    ],
    env: {
        browser: true,
        node: true,
        commonjs: true,
        es6: true
    },
    globals: {},
    // add your custom rules hered
    rules: {
        "vue/max-attributes-per-line": ["error", {
            "singleline": 4
        }],
        "vue/html-closing-bracket-newline": ["error", {
            "singleline": "never",
            "multiline": "never"
        }],
        "vue/singleline-html-element-content-newline": "off",
        "comma-dangle": ["error", "never"],
        'semi': ['error', 'never'],
        "camelcase": ['error', {'properties': 'never'}],
        'linebreak-style': ["off", "windows"],
        "no-param-reassign": [2, { "props": false }],
        "newline-per-chained-call": ["warn", { "ignoreChainWithDepth": 5 }],
        'camelcase': ["off"]
    }
}
