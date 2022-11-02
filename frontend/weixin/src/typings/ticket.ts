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

/* eslint-disable camelcase */
export interface IPriority {
  key: string,
  name: string,
  order: number,
}

export interface Meta {
  priority: IPriority,
}

export interface ICurrentStep {
  id: number,
  tag: string,
  name: string,
}

export interface ITicketItem {
  id: number,
  catalog_id: string,
  catalog_name: string,
  catalog_fullname: string,
  service_id: string,
  service_name: string,
  flow_id: number,
  sn: string,
  title: string,
  service_type: string,
  service_type_name: string,
  is_draft: boolean,
  current_status: string,
  current_status_display: string,
  comment_id: string,
  sla_status: string,
  is_commented: boolean,
  is_over: boolean,
  related_type?: string | null,
  has_relationships: boolean,
  priority_name: string,
  meta: Meta,
  task_schemas: any[],
  bk_biz_id: number,
  creator: string,
  create_at: string,
  updated_by: string,
  update_at: string,
  end_at?: string | null,
  current_steps: ICurrentStep[],
  current_processors: string,
  can_comment: boolean,
  can_operate: boolean,
  can_view: boolean,
  waiting_approve: boolean,
  followers: Array<string>
}

export interface INodeInfo {
  action_type: string,
  api_info: object,
  assignors: string,
  assignors_type: string,
  buttons: any[],
  can_create_task: boolean,
  can_deliver: boolean,
  can_execute_task: boolean,
  can_operate: boolean,
  can_terminate: boolean,
  can_view: boolean,
  contexts: object,
  create_at: string,
  creator: null,
  delivers: string,
  delivers_type: string,
  end_at: string,
  fields: object[],
  from_transition_id: string,
  id: number,
  is_schedule_ready: boolean,
  is_sequential: boolean,
  members: string,
  name: string,
  operations: any[],
  origin_assignors: string,
  origin_delivers: string,
  origin_processors: string,
  processors: string,
  processors_type: string,
  query_params: object,
  state_id: number,
  status: string,
  tag: string,
  tasks: any[],
  terminate_message: string,
  ticket_id: number,
  type: string,
  update_at: string,
  updated_by: string
}

export interface ITicketDetail {
  status: string,
  is_over: boolean
}
export interface IOperation {
  can_operate?: boolean,
  key?: string,
  name?: string
}

export interface ITicketService {
  id: number,
  key: string,
  name: string,
  favortie: boolean,
  bounded_catalogs: string[]
}

export interface IServiceInfo {
  auth_actions: string[],
  bounded_catalogs: string[],
  bounded_relations: any[],
  can_ticket_agency: boolean,
  catalog_id: number,
  create_at: string,
  creator: string,
  desc: string,
  display_role: string,
  display_type: string,
  extras: object,
  favorite: true
  first_state_id: number,
  id: number,
  is_biz_needed: false
  is_builtin: false
  is_supervise_needed: false
  is_valid: true
  key: string,
  name: string,
  notify: any[]
  notify_freq: number,
  notify_rule: string,
  owners: string,
  project_key: string,
  revoke_config: object,
  sla: any[]
  source: string,
  supervise_type: string,
  supervisor: string,
  update_at: string,
  updated_by: string,
  version_number: string,
  workflow: number | string,
  workflow_id: number,
  workflow_name: string
}
