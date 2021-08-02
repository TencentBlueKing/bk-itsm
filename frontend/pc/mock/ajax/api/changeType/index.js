/**
 * changeType  变更类型mock
 * @author edehua <>
 */

import moment from 'moment'
import faker from 'faker'

const randomInt = (n, m) => {
    return Math.floor(Math.random() * (m - n + 1) + n)
}

const sleep = delay => {
    var start = new Date().getTime()
    while (new Date().getTime() < start + delay);
}

export function response (getArgs, postArgs, req) {
    const invoke = getArgs.invoke
    const result = {
        code: 'OK',
        data: null,
        result: true,
        message: ''
    }
    if (invoke === 'getChangeTypeList') {
        result.data = [
            {key: 1, 'level': '赵伟', 'desc': '阿萨德骄傲和地区我IE千万IE精确为哦'},
            {key: 2, 'level': '111', 'desc': '1231231222222222222222'}
        ]
        result.message = '获取变更类型信息成功'
        return result
    }
    if (invoke === 'submit') {
        result.data = {id: randomInt(1, 10000), type: '123', explain: '我的说明！'}
        result.message = '提交成功！'
        return result
    }
    if (invoke === 'update') {
        result.data = {id: randomInt(1, 10000), type: '123', explain: '我的说明！'}
        result.message = '修改成功！'
        return result
    }
    if (invoke === 'delete') {
        result.data = {}
        result.message = '删除成功！'
        return result
    }
    return {
        code: 'OK',
        data: []
    }
}
