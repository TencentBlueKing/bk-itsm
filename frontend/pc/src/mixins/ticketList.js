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

import { errorHandler } from '@/utils/errorHandler';
import { deepClone } from '@/utils/util';

const ticketListMixins = {
  methods: {
    /**
         * 异步加载列表中的某些字段信息
         * @param {Array} originList 单据列表
         */
    //  @param {Array} exclude 排除字段（不需要去加载的字段）
    __asyncReplaceTicketListAttr(originList) {
      if (originList.length === 0) {
        return;
      }
      this.__getTicketsProcessors(originList);
      this.__getTicketsCreator(originList);
      this.__getTicketscanOperate(originList);
    },
    // 异步获取单据处理人
    __getTicketsProcessors(originList) {
      const copyList = deepClone(originList);
      originList.forEach((ticket) => {
        this.$set(ticket, 'current_processors', '加载中...');
      });
      const ids = copyList.map(ticket => ticket.id);
      this.$store.dispatch('ticket/getTicketsProcessors', { ids: ids.toString() }).then((res) => {
        if (res.result && res.data) {
          originList.forEach((ticket, index) => {
            const replaceValue = Object.prototype.hasOwnProperty.call(res.data, ticket.id)
              ? res.data[ticket.id]
              : copyList[index].current_processors;
            this.$set(ticket, 'current_processors', replaceValue);
          });
        }
      })
        .catch((res) => {
          errorHandler(res, this);
        });
    },
    // 异步获取提单人
    __getTicketsCreator(originList) {
      const copyList = deepClone(originList);
      originList.forEach((ticket) => {
        this.$set(ticket, 'creator', '加载中...');
      });
      const ids = copyList.map(ticket => ticket.id);
      this.$store.dispatch('ticket/getTicketsCreator', { ids: ids.toString() }).then((res) => {
        if (res.result && res.data) {
          originList.forEach((ticket, index) => {
            const replaceValue = Object.prototype.hasOwnProperty.call(res.data, copyList[index].creator)
              ? res.data[copyList[index].creator]
              : copyList[index].creator;
            this.$set(ticket, 'creator', replaceValue);
          });
        }
      })
        .catch((res) => {
          errorHandler(res, this);
        });
    },
    // 异步获取单据 can_operate
    __getTicketscanOperate(originList) {
      const copyList = deepClone(originList);
      originList.forEach((ticket) => {
        // 开始是都不能操作
        this.$set(ticket, 'can_operate', false);
      });
      const ids = copyList.map(ticket => ticket.id);
      this.$store.dispatch('ticket/getTicketscanOperate', { ids: ids.toString() }).then((res) => {
        if (res.result && res.data) {
          originList.forEach((ticket) => {
            const replaceValue = Object.prototype.hasOwnProperty.call(res.data, ticket.id)
              ? res.data[ticket.id] : false;
            this.$set(ticket, 'can_operate', replaceValue);
          });
        }
      })
        .catch((res) => {
          errorHandler(res, this);
        });
    },
  },
};

export default ticketListMixins;
