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
interface IColumn {
  name: string,
  display: string,
  choice: Array<{
    name: string,
    key: string
  }>
}

interface IMeta {
  columns?: IColumn
}
/* eslint-disable camelcase */
export interface IField {
  id: number;
  key: string;
  type: string;
  choice: Array<any>;
  name: string;
  value: any;
  display: boolean;
  display_value: any;
  related_fields: any;
  meta: IMeta;
  source_type: string;
  source_uri: string;
  kv_relation: any;
  validate_type: string;
  api_instance_id: number;
  regex: string;
  regex_config?: Record<'rule', { expressions: Array<any>, type: string }>;
  custom_regex: string,
  default: any;
  desc: string;
  tips: string;
  is_tips: boolean;
  layout: string;
  is_valid: boolean;
  is_builtin: boolean;
  ticket_id: number;
  state_id: string;
  show_conditions: any;
  show_type: number;
  is_readonly: boolean;
  source: string;
  workflow_field_id: number;
  creator: string | null;
  create_at: string;
  updated_by: string | null;
  update_at: string | null;
  end_at: string | null;
  workflow_id: number;
  show_result: boolean
}
