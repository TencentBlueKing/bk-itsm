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

/* eslint-disable */
import { useStore } from 'vuex'
export default function () {
  const store = useStore()

  // 自定义数据 - API
  function getFieldApiData (field, fields) {
    const params = {
      id: field.id,
      api_instance_id: field.api_instance_id,
      kv_relation: field.kv_relation
    }
    if (field.related_fields && field.related_fields.rely_on) {
      field.related_fields.rely_on.forEach(itefinal => {
        const targetField = fields.find(f => f.key === itefinal)
          if (targetField) {
              params[itefinal] = targetField.value || ''
          }
        })
    }
    // 没有引用变量的api字段 才可以 发送请求
    if (!Object.values(params).every(p => !!p) || field.key === 'priority') {
      return false
    }
    params['api_info'] = field.api_info
    params.fields = {
      id: field.id,
      api_instance_id: field.api_instance_id,
      kv_relation: field.kv_relation
    }
    return store.dispatch('field/getfieldApiChoice', params).then(resp => {
      field.choice = resp.data.map(item => ({ key: item.key || item.id, name: item.name }))
    })
  }

  // 自定义数据 - 数据字典
  function getFieldDatadictData (field) {
    return store.dispatch('field/getDatadict', {
      key: field.source_uri,
      field_key: field.key,
      service: field.service,
      current_status: field.ticket_status
    }).then(resp => {
      field.choice = resp.data.map(item => ({
        key: item.key,
        name: item.name,
        isOver: item.is_over
      }))
    })
  }

  // 自定义数据 - 系统数据RPC
  function getFieldRPCData (field) {
    return store.dispatch('field/getRPC', field).then(resp => {
      field.choice = resp.data
    })
  }

  // 加载远程数据
  function insertRemoteChoiceData (fields) {
    fields.forEach(field => {
      const choice = Array.isArray(field.choice) ? field.choice : []
      if (!choice.some(it => it.can_delete)) {
        const sourceType = field.source_type
        if (sourceType === 'API') {
          getFieldApiData(field, fields)
        } else if (sourceType === 'DATADICT') {
          getFieldDatadictData(field)
        } else if (sourceType === 'RPC') {
          getFieldRPCData(field)
        }
      }
    })
  }

  return {
    insertRemoteChoiceData
  }
}