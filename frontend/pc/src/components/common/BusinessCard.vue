<!--
  - Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.
  - Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
  - BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
  -
  - License for BK-ITSM 蓝鲸流程服务:
  - -------------------------------------------------------------------
  -
  - Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
  - documentation files (the "Software"), to deal in the Software without restriction, including without limitation
  - the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
  - and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  - The above copyright notice and this permission notice shall be included in all copies or substantial
  - portions of the Software.
  -
  - THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
  - LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
  - NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  - WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  - SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
  -->

<!--    1104 人员名片展示-->
<template>
  <bk-popover
    placement="bottom"
    ext-cls="bk-business-card"
    class="business-popover"
    :on-show="showMessage"
    trigger="click"
    theme="light">
    <i class="bk-icon icon-id" v-if="memberVal" ref="icon"></i>
    <div slot="content">
      <ul ref="message" class="bk-member-message" v-bkloading="{ isLoading: localLoading }">
        <li v-for="(member, memIndex) in memberList"
          :key="memIndex"
          style="margin-bottom: 10px; overflow: hidden;">
          <p class="bk-message-name">{{member.username}}</p>
          <p class="bk-member-other"
            v-for="(person, personIndex) in memberValList"
            :key="personIndex"
            :title="member[person.type]">
            <span class="bk-member-label">{{person.name}} {{$t(`m.newCommon["："]`)}}</span>
            <pre class="bk-member-value">{{member[person.type] || '--'}}</pre>
          </p>
        </li>
      </ul>
    </div>
  </bk-popover>
</template>

<script>
  import { errorHandler } from '../../utils/errorHandler';
  export default {
    name: 'BusinessCard',
    props: {
      item: {
        type: Object,
        default() {
          return {};
        },
      },
      basicInfomation: {
        type: Object,
        default() {
          return {};
        },
      },
    },
    data() {
      return {
        memberList: [],
        memberValList: [
          { type: 'display_name', name: this.$t('m.newCommon["中文名"]') },
          { type: 'email', name: this.$t('m.newCommon["邮箱"]') },
          // { type: 'phone', name: this.$t(`m.newCommon["手机"]`) }
          { type: 'departmentsDispName', name: this.$t('m.newCommon["部门信息"]') },
        ],
        showInfo: false,
        localLoading: false,
      };
    },
    computed: {
      memberVal() {
        return this.basicInfomation.creator ? this.basicInfomation.creator : this.item.val;
      },
    },
    created() {
      if (window.run_site !== 'bmw') {
        this.memberValList.push({ type: 'qq', name: this.$t('m.newCommon["QQ"]') });
        this.memberValList.push({ type: 'wx_userid', name: this.$t('m.newCommon["微信"]') });
        this.memberValList.push({ type: 'time_zone', name: this.$t('m.newCommon["时区"]') });
      }
    },
    methods: {
      showMessage() {
        if (!this.memberVal) {
          return;
        }
        this.localLoading = true;
        const valList = this.memberVal.split(',');
        const userIds = valList.map(name => name.replace(/\(.*\)$/, ''));
        const params = {
          users: userIds.join(','),
        };
        this.$store.dispatch('getPersonInfo', params).then((res) => {
          if (res.data && res.data.length) {
            this.memberList = res.data;
            this.memberList.forEach((info) => {
              if (info.departments && info.departments.length) {
                const depName = info.departments.reduce((names, dep, index) => {
                  if (index) {
                    names += '\n';
                  }
                  names += dep.full_name;
                  return names;
                }, '');
                info.departmentsDispName = depName;
              }
            });
            this.showInfo = true;
          }
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.localLoading = false;
          });
      },
    },
  };
</script>

<style scoped lang="scss">
    @import "../../scss/mixins/scroller";
    .icon-id {
        display: inline-block;
        width: 20px;
        height: 20px;
        position: relative;
        vertical-align: -2px;
        font-size: 20px;
        color: #979BA5;
        cursor: pointer;
        &:hover {
            color: #63656E;
        }
    }
    .bk-business-card {
        .bk-member-message {
            width: 240px;
            min-height: 160px;
            max-height: 200px;
            font-size: 12px;
            color: #737987;
            line-height: 22px;
            overflow: auto;
            @include scroller;
            .bk-message-name {
                border-bottom: 1px solid #dde4eb;
                text-align: left;
                font-weight: bold;
            }

            .bk-member-other {
                display: flex;
                text-align: left;

                .bk-member-label {
                    display: inline-block;
                    width: 70px;
                    text-align: left;
                    word-break: break-all;
                    flex-shrink: 0;
                }

                .bk-member-value {
                    display: inline-block;
                    text-align: left;
                    margin-left: 5px;
                    font-weight: bold;
                    white-space: break-spaces;
                }
            }
        }
    }

</style>
