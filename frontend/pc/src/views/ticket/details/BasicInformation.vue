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

<template>
  <div :class="['basic-info-wrap', { 'fold': !showMore }, { 'has-more-icon': displayMoreIcon }]">
    <div class="bk-basic-info" ref="basicInfo">
      <div class="bk-basic-form">
        <table-fields :basic-infomation="basicInfomation" :first-state-fields="firstStateFields"></table-fields>
      </div>
    </div>
  </div>
</template>

<script>
  import tableFields from './components/tableFields.vue';
  // import fieldsDone from './components/fieldsDone.vue'
  export default {
    name: 'BasicInformation',
    components: {
      // fieldsDone,
      tableFields,
    },
    props: {
      basicInfomation: {
        type: Object,
        default() {
          return {};
        },
      },
      firstStateFields: {
        type: Array,
        default() {
          return [];
        },
      },
    },
    data() {
      return {
        showMore: false,
        showInfo: true,
        displayMoreIcon: true,
        basicInfomationList: [],
        basicInfoType: ['STRING', 'TEXT', 'SELECT', 'INT', 'DATE'],
      };
    },
    computed: {
      profile() {
        if (!this.basicInfomation) {
          return;
        }
        return {
          name: this.basicInfomation.profile.name,
          phone: this.basicInfomation.profile.phone,
          department: this.basicInfomation.profile.departments ? this.basicInfomation.profile.departments : [],
        };
      },
    },
    mounted() {
      this.tableFields();
      // 这里是为了等 dom 加载完后计算真实高度
      setTimeout(() => {
        const contentsDom = document.querySelectorAll('.basic-info-wrap > .bk-basic-info > .bk-basic-form');
        let height = 0;
        Array.prototype.forEach.call(contentsDom, (node) => {
          height += node.offsetHeight;
        });
        this.displayMoreIcon = height >= 300;
      }, 100);
    },
    methods: {
      // 处理人栏显示处理
      processtrans(item) {
        switch (item.current_status) {
          case 'DISTRIBUTING':
            return item.current_assignors;
          case 'DISTRIBUTING-RECEIVING':
            return (Array.from(new Set([...item.current_processors.split(','), ...item.current_assignors.split(',')])).join()
              .replace(/(^,*)|(,$)/g, ''));
          default :
            return item.current_processors || '--';
        }
      },
      changeShow() {
        this.showMore = !this.showMore;
      },
      // 处理基本信息字段
      tableFields() {
        const tlist = []; // 表单表格类型的字段
        const { service_type_name, sn, catalog_fullname: catalogFullname, service_name: serviceName, title } = this.basicInfomation;
        const list = [
          { name: '标题', display_value: title, type: 'STRING' },
          { name: '单号', display_value: sn, type: 'STRING' },
          { name: '工单类型', display_value: service_type_name, type: 'STRING' },
          { name: '服务目录', display_value: `${catalogFullname}>${serviceName}`, type: 'STRING' },
          { name: '关联服务', display_value: serviceName, type: 'STRING' },
        ];
        const fields = this.firstStateFields.map(item => item);
        fields.forEach((ite) => {
          if (!this.basicInfoType.includes(ite.type)) {
            tlist.push(ite);
          } else {
            tlist.unshift(ite);
          }
        });
        this.basicInfomationList = list.concat(tlist.filter(ite => ite.key !== 'title'));
      },
    },
  };
</script>

<style scoped lang='scss'>
    @import '../../../scss/mixins/clearfix.scss';
    @import '../../../scss/mixins/scroller.scss';
    .show {
        width: 500px;
        // margin-top: -10px;
        overflow: auto;
        @include scroller;
    }
    .basic-info-wrap {
        position: relative;
        padding-bottom: 14px;
        &.fold {
            .bk-basic-info {
                // max-height: 500px;
                overflow: auto;
                @include scroller;
            }
        }
        &.has-more-icon {
            padding-bottom: 30px;
        }
    }
    .bk-basic-info {
        position: relative;
        padding-top: 7px;
    }

    .bk-basic-form {
        padding: 0 20px;

        ul {
            @include clearfix;
        }

        li {
            width: 33.33%;
            float: left;
            margin: 8px 0;
            font-size: 14px;
            color: #63656e;
            line-height: 22px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
            padding-right: 10px;
            @include clearfix;
            .icon-basic-info {
                display: inline-block;
                position: relative;
                &:hover {
                    .show {
                        display: block;
                    }
                }
                .show {
                    display: none;
                    position: absolute;
                    top: 0;
                    left: 0;
                    background-color: blue;
                    width: 300px;
                    height: 200px;
                }
            }
        }

        .ul-no-border {
            border: none;
        }

        .bk-info-title {
            width: 70px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
            text-align: right;
            float: left;
            color: #979ba5;
        }
        .view-content {
            padding-left: 10px;
            cursor: pointer;
            opacity: 0.5;
        }
        .bk-info-content {
            word-wrap: break-word;
            padding-left: 10px;
            color: #313238;
        }

        .bk-basic-li {
            height: auto;
            width: 100%;

            ul {
                margin-bottom: -10px;
                clear: both;
                width: calc(100% - 70px);
                display: inline-block;
                background: #eff6fd;
                border-radius: 5px;
                padding-left: 10px;

                li {
                    width: 100%;

                    .bk-info-title {
                        width: 50px;
                    }
                }
            }
        }
    }

    .more-content-btn {
        padding: 2px 20px;
        position: absolute;
        left: 50%;
        bottom: 0;
        z-index: 1;
        transform: translateX(-50%);
        color: #fff;
        font-size: 12px;
        text-align: center;
        cursor: pointer;
        background: #c4c6cc;
        border-radius: 10px 10px 0px 0px;
        &:hover {
            color: #ffffff;
            background: #3a84ff;
        }
    }
</style>
