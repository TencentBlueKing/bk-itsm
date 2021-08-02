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

export default function (item, value) {


  // 时间字符转换成时间戳
  const timeStamp = (timeValue) => {
      const timeInfo = timeValue.replace(/-/g, '/')
      const timeStampValue = new Date(timeInfo).getTime()
      return timeStampValue
  }

  const conditionSwitch = (item, value) => {
    let statusInfo = false
    const typeList = ['CHECKBOX', 'MEMBERS', 'MULTISELECT', 'TREESELECT']
    switch (value.condition) {
        case '==':
            if (typeList.some(type => type === item.type)) {
                const valList = value.value.split(',')
                const statusList = valList.map(val => item.val.indexOf(val) === -1)
                statusInfo = ((statusList.every(status => !status)) && item.val.length === value.value.length)
            } else {
                statusInfo = (item.val === value.value || Number(item.val) === Number(value.value))
            }
            break
        case '!=':
            if (typeList.some(type => type === item.type)) {
                const valList = value.value.split(',')
                const statusList = valList.map(val => item.val.indexOf(val) === -1)
                statusInfo = statusList.some(status => !!status) ? statusList.some(status => !!status) : item.val.length !== value.value.length
            } else {
                statusInfo = (item.val !== value.value && Number(item.val) !== Number(value.value))
            }
            break
        case '>':
            if (item.type === 'DATE' || item.type === 'DATETIME') {
                statusInfo = timeStamp(item.val) > timeStamp(value.value)
            } else {
                statusInfo = Number(item.val) > Number(value.value)
            }
            break
        case '<':
            if (item.type === 'DATE' || item.type === 'DATETIME') {
                statusInfo = timeStamp(item.val) < timeStamp(value.value)
            } else {
                statusInfo = Number(item.val) < Number(value.value)
            }
            break
        case '>=':
            if (item.type === 'DATE' || item.type === 'DATETIME') {
                statusInfo = timeStamp(item.val) >= timeStamp(value.value)
            } else {
                statusInfo = Number(item.val) >= Number(value.value)
            }
            break
        case '<=':
            if (item.type === 'DATE' || item.type === 'DATETIME') {
                statusInfo = timeStamp(item.val) <= timeStamp(value.value)
            } else {
                statusInfo = Number(item.val) <= Number(value.value)
            }
            break
        case 'issuperset':
            const issupersetList = value.value.split(',')
            const statusList = issupersetList.map(val => item.val.indexOf(val) === -1)
            statusInfo = statusList.every(status => !status)
            break
        case 'notissuperset':
            const valnoList = value.value.split(',')
            const statusnoList = valnoList.map(val => item.val.indexOf(val) === -1)
            statusInfo = !statusnoList.every(status => !status)
            break
        default:
            statusInfo = true
    }
    return statusInfo
  }
  const conditionField = (item, list) => {
      for (let i = 0; i < list.length; i++) {
        if (list[i].show_type) {
            list[i].showFeild = true
            continue
        }
        // 对于没有expressions字段的参数，跳过逻辑处理
        if (list[i].show_conditions.expressions && list[i].show_conditions.expressions.length) {
            for (let j = 0; j < list[i].show_conditions.expressions.length; j++) {
                // 当当前操作的字段内存在自己配置自己的情况，则忽略配置条件
                if (item.key === list[i].show_conditions.expressions[j].key && item.key === list[i].key && list[i].value === null) {
                    list[i].showFeild = true
                } else {
                    // 当前节点的类型和expressions的数据一样时，进行处理
                    if (item.key === list[i].show_conditions.expressions[j].key) {
                        if (list[i].show_conditions.expressions.length === 1) {
                            list[i].showFeild = conditionSwitch(item, list[i].show_conditions.expressions[j])
                        } else {
                            // 区分条件组‘and’和‘or’的判断逻辑
                            if (list[i].show_conditions.type === 'and') {
                                // 判断其他字段和关联字段的关系
                                const statusList = []
                                for (let z = 0; z < list[i].show_conditions.expressions.length; z++) {
                                    for (let s = 0; s < list.length; s++) {
                                        if (list[i].show_conditions.expressions[z].key === list[s].key) {
                                            const valueStatus = conditionSwitch(list[s], list[i].show_conditions.expressions[z])
                                            statusList.push(valueStatus)
                                        }
                                    }
                                }
                                // 判断当前字段与关联字段的关系
                                list[i].showFeild = statusList.every(status => !!status)
                            } else {
                                // 判断其他字段和关联字段的关系
                                const statusList = []
                                for (let z = 0; z < list[i].show_conditions.expressions.length; z++) {
                                    for (let s = 0; s < list.length; s++) {
                                        if (list[i].show_conditions.expressions[z].key === list[s].key) {
                                            const valueStatus = conditionSwitch(list[s], list[i].show_conditions.expressions[z])
                                            statusList.push(valueStatus)
                                        }
                                    }
                                }
                                list[i].showFeild = statusList.some(status => !!status)
                            }
                        }
                        list[i].showFeild = !list[i].showFeild
                    }
                }
            }
        }
    }
  }

  return {
    conditionField
  }
}
