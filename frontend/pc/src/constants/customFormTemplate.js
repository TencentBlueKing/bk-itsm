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

export const CUSTOM_FORM_TEMPLATE = {
  config: {
    mode: 'sideslider', // combine
  },
  schemes: {
    base_text_scheme: {
      type: 'text',
      attrs: {
        styles: {
          label: ['border'],
          value: ['highlight', 'border'],
        },
        desc: '通用描述文字',
      },
    },
    table_text_scheme: {
      type: 'text',
      attrs: {
        styles: {
          label: ['border'],
          value: ['highlight', 'border'],
        },
      },
    },
    base_table_scheme: {
      type: 'table',
      attrs: {
        column: [
          {
            name: '操作',
            type: 'text',
            key: 'column1',
          },
          {
            name: '关联相关内容',
            key: 'column2',
            scheme: 'table_text_scheme',
            attrs: {
            },
          },
          {
            name: '申请期限',
            type: 'text',
            key: 'column3',
            attrs: {
              sort: true,
            },
          },
        ],
      },
    },
    sub_table_scheme: {
      type: 'table',
      attrs: {
        column: [
          {
            name: '关联内容-类型',
            key: 'column1',
            scheme: 'base_text_scheme',
          },
          {
            name: '类型值',
            key: 'column2',
            scheme: 'table_text_scheme',
          },
        ],
      },
    },
    sub2_table_scheme: {
      type: 'table',
      attrs: {
        column: [
          {
            name: '主机',
            key: 'column1',
            scheme: 'base_text_scheme',
          },
        ],
      },
    },
  },
  form_data: [
    {
      label: '业务：',
      scheme: 'base_text_scheme',
      value: '蓝鲸',
      desc: '覆盖 scheme 中通用描述文字',
      children: [
        {
          label: '子业务1：',
          scheme: 'base_text_scheme',
          value: 'test1',
        },
        {
          label: '子业务2：',
          scheme: 'base_text_scheme',
          value: 'test2',
        },
      ],
    },
    {
      label: '提单人：',
      scheme: 'base_text_scheme',
      value: '',
    },
    {
      label: '提单时间：',
      scheme: 'base_text_scheme',
      value: '',
    },
  ],
};
