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

// 表格的 value 是动态的，由 column key 决定的
type IFormValue = string | Array<Object>
type TagType = 'text' | 'table'
export interface IFormItem {
  label?: string,
  scheme: string,
  desc?: string,
  children?: Array<IFormItem>,
  value: IFormValue
}


export interface IConfig {
  mode?: string;
}

export interface IColumn {
  name: string;
  type?: TagType;
  key: string;
  scheme?: string;
  attrs?: {
    sort?: boolean
  }
}

export interface IScheme {
  [x: string]: {
    type: TagType;
    attrs?: {
      column?: Array<IColumn>;
      styles?: {
        label: Array<string>;
        value: Array<string>;
      },
      desc?: string
    };
  }
}

export interface IContext {
  config?: IConfig;
  schemes: IScheme;
}

export interface ICustomForm {
  config?: IConfig;
  schemes?: IScheme;
  // eslint-disable-next-line camelcase
  form_data: Array<IFormItem>
}

export interface IInnerForms {
  formData: IFormItem[],
  title: string
}

export interface IInnerFormInstance {
  pushToInnerForms(item: IInnerForms): void;
  toPrevInderForm(): void;
  clearInnerForms(): void;
}
