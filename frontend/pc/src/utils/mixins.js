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

import _ from 'lodash';
import { errorHandler } from '../utils/errorHandler';
export default {

  props: {
    fields: {
      type: Array,
      default: () => [],
    },
    isPreview: {
      type: Boolean,
      default: false,
    },
  },
  data() {

  },
  created() {
  },
  watch: {
  },
  methods: {
    debounce: _.debounce(async function () {
      this.item.choice = await this.getFieldOptions(this.item, this.isPreview);
      this.options = this.item.choice;
    }, 1000, {
      leading: true,
      trailing: true,
      maxWait: 2000,
    }),
    // 自定义表单数据处理
    async getFieldOptions(item, type) {
      await item;
      let data = [];
      switch (item.source_type) {
        case 'CUSTOM':
          data = item.choice;
          break;
        case 'API':
          // TODO ajax请求-wl
          if (type && item.id) {
            const reqParams = item.relyOn || {};
            reqParams.id = item.id;
            await this.$store.dispatch('apiRemote/get_data', reqParams).then((res) => {
              data = res.data.map(item => ({
                key: item.key,
                name: item.name,
              }));
            })
              .catch((res) => {
                errorHandler(res, this);
              });
          } else {
            data = [];
            item.choice.forEach((node) => {
              data.push({
                key: node.id,
                name: node.name,
              });
            });
          }
          break;
        case 'DATADICT':
          // 请求数据字典数据
          if (type && item.type !== 'TREESELECT') {
            await this.$store.dispatch('datadict/get_data_by_key', {
              key: item.source_uri,
              field_key: item.key,
              service: item.service,
              current_status: item.ticket_status,
            }).then((res) => {
              data = res.data.map(item => ({
                key: item.id,
                name: item.name,
              }));
            })
              .catch((res) => {
                errorHandler(res, this);
              });
          } else {
            data = [];
            item.choice.forEach((node) => {
              data.push({
                key: node.id,
                name: node.name,
              });
            });
          }
          break;
      }
      return data;
    },
    itemSelect() {
      if (this.item.related_fields.be_relied) {
        this.item.related_fields.be_relied.forEach((fieldKey) => {
          this.fields.forEach((field) => {
            if (field.key === fieldKey) {
              this.$set(field.relyOn, this.item.key, this.item.val);
            }
          });
        });
      }
    },
  },
};
