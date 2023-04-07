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
  <div class="bk-api-tree">
    <div class="bk-tree-content">
      <div class="mb20">
        <bk-input v-model="searchWord"
          :right-icon="'bk-icon icon-search'"
          :clearable="true"
          @clear="clearInfo">
          <template slot="append">
            <bk-dropdown-menu class="group-text"
              @show="dropdownShow"
              @hide="dropdownHide"
              ref="dropdown"
              style="width: 70px; line-height: 30px;">
              <div class="dropdown-trigger-btn" style="padding-left: 6px;" slot="dropdown-trigger">
                <span>{{ $t(`m.systemConfig['系统接入']`)}}</span>
                <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShow }]"></i>
              </div>
              <ul class="bk-dropdown-list" slot="dropdown-content">
                <li>
                  <a href="javascript:;"
                    data-test-id="api_a_accessApi"
                    v-cursor="{ active: !projectId && !hasPermission(['public_api_create']) }"
                    :class="{ 'text-permission-disable': !projectId && !hasPermission(['public_api_create']) }"
                    :title="$t(`m.systemConfig['系统接入']`)"
                    @click="openDictionary('JION')">
                    {{ $t(`m.systemConfig['系统接入']`) }}
                  </a>
                </li>
                <li>
                  <a href="javascript:;"
                    data-test-id="api_a_createApi"
                    v-cursor="{ active: !projectId && !hasPermission(['public_api_create']) }"
                    :class="{ 'text-permission-disable': !projectId && !hasPermission(['public_api_create']) }"
                    :title="$t(`m.systemConfig['系统新增']`)"
                    @click="openDictionary('ADD')">
                    {{$t(`m.systemConfig['系统新增']`)}}
                  </a>
                </li>
              </ul>
            </bk-dropdown-menu>
          </template>
        </bk-input>
      </div>
      <div class="bk-tree-info" v-bkloading="{ isLoading: isTreeLoading }">
        <ul class="bk-tree-group" @scroll="scrollEvent">
          <template v-if="treeList.length !== 0">
            <li v-for="(item, index) in treeList"
              :key="index"
              data-test-id="api_li_viewApiTable"
              @click="showBackground(item, index, 0)">
              <template v-if="!item.id">
                <div class="bk-group-parent bk-p18"
                  :class="{ 'bk-group-li': item.check }">
                  <i class="bk-icon icon-folder bk-ml5"></i>
                  <span>{{ $t('m.systemConfig["全部系统"]') }}</span>
                </div>
              </template>
              <template v-else>
                <div class="bk-group-parent bk-p18 bk-handel"
                  :class="{ 'bk-group-li': item.check }">
                  <i class="bk-icon icon-folder-open bk-ml5"></i>
                  <span class="bk-group-name" v-bk-overflow-tips>{{item.name}}</span>
                  <span style="display: inline-block;" class="bk-edit" v-if="item.can_edit">
                    <i class="bk-icon icon-more bk-tree-point bk-point-selected">
                    </i>
                    <ul class="bk-more" :style="styletranslateY">
                      <li
                        v-if="!item.is_builtin"
                        data-test-id="api_li_deleteApiDirectory"
                        v-cursor="{ active: !projectId && hasPermission(['public_api_manage']) }"
                        :class="{ 'text-permission-disable': !projectId && hasPermission(['public_api_manage']) }"
                        @click.stop="openDelete(item)">
                        <span>{{ $t('m.systemConfig["删除"]') }}</span>
                      </li>
                      <li
                        data-test-id="api_li_editApiDirectory"
                        v-cursor="{ active: !projectId && hasPermission(['public_api_manage']) }"
                        :class="{ 'text-permission-disable': !projectId && hasPermission(['public_api_manage']) }"
                        @click.stop="openDictionary('CHANGE' ,item)">
                        <span>{{ $t('m.systemConfig["编辑"]') }}</span>
                      </li>
                    </ul>
                  </span>
                </div>
                <collapse-transition>
                  <template v-if="item.showMore && false">
                    <ul class="bk-group-child">
                      <li v-for="(node, nodeIndex) in item.apis"
                        :key="nodeIndex"
                        class="bk-p42"
                        :class="{ 'bk-group-li': node.check }"
                        @click.stop="showBackground(node, index, 1)">
                        <span class="bk-group-child-name">{{node.name}}</span>
                      </li>
                    </ul>
                  </template>
                </collapse-transition>
              </template>
            </li>
          </template>
          <Empty
            v-else
            :is-search="Boolean(searchWord)"
            @onClearSearch="clearInfo"
          ></Empty>
        </ul>
      </div>
    </div>
    <!-- 接入系统 -->
    <bk-dialog
      data-test-id="api_dialog_accessApi"
      v-model="dictDataTable.showDialog"
      :render-directive="'if'"
      :width="dictDataTable.width"
      :header-position="dictDataTable.headerPosition"
      :loading="secondClick"
      :auto-close="dictDataTable.autoClose"
      :mask-close="dictDataTable.autoClose"
      :title="dictDataTable.title"
      @confirm="submitDictionary">
      <div class="bk-add-module">
        <bk-form
          :label-width="200"
          form-type="vertical"
          :model="dictDataTable.formInfo"
          :rules="rules"
          ref="dictDataForm">
          <template v-if="dictDataTable.type === 'ADD'">
            <bk-form-item
              data-test-id="api-input-systemName"
              :label="$t(`m.systemConfig['系统名称：']`)"
              :required="true"
              :property="'addName'">
              <bk-input :clearable="true" v-model="dictDataTable.formInfo.addName"></bk-input>
            </bk-form-item>
            <bk-form-item
              data-test-id="api-input-systemCode"
              :label="$t(`m.systemConfig['系统编码：']`)"
              :required="true"
              :property="'addCode'">
              <bk-input :clearable="true" v-model="dictDataTable.formInfo.addCode"></bk-input>
            </bk-form-item>
          </template>
          <template v-else>
            <bk-form-item
              :label="$t(`m.systemConfig['系统名称：']`)"
              :required="true"
              :property="'code'">
              <template v-if="dictDataTable.type === 'CHANGE'">
                <bk-select disabled
                  v-model="dictDataTable.formInfo.code"
                  :clearable="false"
                  searchable
                  @selected="changeCode">
                  <bk-option v-for="option in allCodeList"
                    :key="option.code"
                    :id="option.code"
                    :name="option.name">
                  </bk-option>
                </bk-select>
              </template>
              <template v-else>
                <bk-select
                  v-model="dictDataTable.formInfo.code"
                  :clearable="false"
                  searchable
                  @selected="changeCode">
                  <bk-option v-for="option in codeList"
                    :key="option.code"
                    :id="option.code"
                    :name="option.name">
                  </bk-option>
                </bk-select>
              </template>
            </bk-form-item>
          </template>
          <bk-form-item
            :label="$t(`m.systemConfig['系统域名：']`)"
            :property="'domain'">
            <bk-input :clearable="true" v-model="dictDataTable.formInfo.domain"></bk-input>
          </bk-form-item>
          <bk-form-item
            :label="$t(`m.systemConfig['负责人：']`)">
            <member-select
              v-model="dictDataTable.formInfo.personInCharge">
            </member-select>
          </bk-form-item>
          <bk-form-item
            :label="$t(`m.systemConfig['备注：']`)">
            <bk-input
              :placeholder="$t(`m.systemConfig['请输入备注']`)"
              :type="'textarea'"
              :rows="3"
              v-model="dictDataTable.formInfo.desc">
            </bk-input>
          </bk-form-item>
          <bk-form-item
            :label="$t(`m.systemConfig['启用：']`)">
            <bk-switcher v-model="dictDataTable.formInfo.is_activated" size="small"></bk-switcher>
          </bk-form-item>
        </bk-form>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
  import collapseTransition from '@/utils/collapse-transition.js';
  import memberSelect from '../../commonComponent/memberSelect';
  import commonMix from '../../commonMix/common.js';
  import { errorHandler } from '../../../utils/errorHandler.js';
  import permission from '@/mixins/permission.js';
  import Empty from '../../../components/common/Empty.vue';

  export default {
    name: 'apiTree',
    components: {
      collapseTransition,
      memberSelect,
      Empty,
    },
    mixins: [commonMix, permission],
    props: {
      projectId: String,
      treeListOri: {
        type: Array,
        default() {
          return [];
        },
      },
      codeList: {
        type: Array,
        default() {
          return [];
        },
      },
      allCodeList: {
        type: Array,
        default() {
          return [];
        },
      },
    },
    data() {
      return {
        secondClick: false,
        // 基本信息人员数组
        basicPerson: {
          // 禁用数组
          disabledList: [],
        },
        styletranslateY: {
          transform: 'translate(40px,-20px)',
        },
        isTreeLoading: false,
        searchWord: '',
        // 接入系统
        dictDataTable: {
          showDialog: false,
          width: 700,
          headerPosition: 'left',
          autoClose: false,
          precision: 0,
          formInfo: {
            addName: '',
            addCode: '',
            name: '',
            desc: '',
            code: '',
            domain: '',
            owners: '',
            personInCharge: [],
            contact_information: '',
            id: '',
            system_id: '',
            is_activated: true,
          },
        },
        isDropdownShow: false,
        rules: {},
      };
    },
    computed: {
      treeList: {
        // getter
        get() {
          const vm = this;
          return this.treeListOri.filter(item => item.name.indexOf(vm.searchWord) !== -1);
        },
        // setter
        set(newVal) {
          newVal.forEach(item => {
            const ori = this.$parent.treeList.filter(ite => ite.system_id === item.system_id && ite.id === item.id);
            if (ori.length) {
              ori[0] = JSON.parse(JSON.stringify(item));
            }
          });
        },
      },
    },
    async mounted() {
      await this.treeListOri;
      // 获取所有系统
      await this.showBackground(this.treeList[0], 0, 0);
      // 校验
      this.rules.code = this.checkCommonRules('select').select;
      this.rules.addName = this.checkCommonRules('name').name;
      this.rules.addCode = this.checkCommonRules('key').key;
    },
    methods: {
      scrollEvent($event) {
        this.styletranslateY.transform = `translate(40px,${-$event.target.scrollTop - 20}px)`;
      },
      changeCode(code) {
        const dataItem = this.codeList.filter(item => item.code === code)[0];
        this.dictDataTable.formInfo.name = dataItem.name;
        this.dictDataTable.formInfo.system_id = dataItem.system_id;
      },
      clearInfo() {
        this.searchWord = '';
      },
      // 展开/收起tree
      showGroupChild(item) {
        item.showMore = !item.showMore;
        this.treeList = [...JSON.parse(JSON.stringify(this.treeList))];
      },
      // 显示底色
      showBackground(item, index, level) {
        if (!level) {
          this.$parent.displayInfo.level_1 = {};
          this.$parent.displayInfo.level_0 = item;
          // 展示 api列表
          // this.$parent.showContent = false
          this.$parent.getTableList(item.id);
          // this.$parent.getChannelPathList(item.system_id)
        } else {
          this.$parent.displayInfo.level_1 = item;
          // 展示 单个api
          // this.$parent.showContent = true
          this.$parent.getRemoteApiDetail(item.id);
        }
        this.treeList.forEach(tree => {
          this.recordCheckFn(tree);
        });
        item.check = true;
        this.treeList = [...JSON.parse(JSON.stringify(this.treeList))];
      },
      recordCheckFn(tree) {
        tree.check = false;
        if (tree.apis && tree.apis.length) {
          tree.apis.forEach(node => {
            node.check = false;
          });
        }
      },
      getRemoteSystemData() {
        this.$parent.getRemoteSystemData();
      },
      // 接入系统/修改系统
      submitDictionary() {
        this.$refs.dictDataForm.validate().then(() => {
          if (this.secondClick) {
            return;
          }
          this.dictDataTable.formInfo.owners = this.dictDataTable.formInfo.personInCharge.join(',');
          const params = {
            name: this.dictDataTable.formInfo.name,
            desc: this.dictDataTable.formInfo.desc,
            code: this.dictDataTable.formInfo.code,
            domain: this.dictDataTable.formInfo.domain,
            system_id: this.dictDataTable.formInfo.system_id,
            owners: this.dictDataTable.formInfo.owners,
            contact_information: this.dictDataTable.formInfo.contact_information,
            is_activated: this.dictDataTable.formInfo.is_activated,
            headers: [],
            cookies: [],
            variables: [],
          };
          if (this.dictDataTable.type === 'ADD') {
            params.name = this.dictDataTable.formInfo.addName;
            params.code = this.dictDataTable.formInfo.addCode;
          }
          params.project_key = !this.projectId ? 'public' : this.projectId;
          if (this.dictDataTable.title === this.$t('m.systemConfig["修改系统"]')) {
            params.id = this.dictDataTable.formInfo.id;
            this.secondClick = true;
            this.$store.dispatch('apiRemote/put_remote_system', params).then(() => {
              this.$bkMessage({
                message: this.$t('m.systemConfig["修改成功"]'),
                theme: 'success',
              });
              this.getRemoteSystemData();
              this.closeDictionary();
            })
              .catch(res => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.secondClick = false;
              });
            return;
          }
          this.secondClick = true;
          this.$store.dispatch('apiRemote/post_remote_system', params).then(() => {
            this.$bkMessage({
              message: this.$t('m.systemConfig["添加成功"]'),
              theme: 'success',
            });
            this.getRemoteSystemData();
            this.closeDictionary();
          })
            .catch(res => {
              errorHandler(res, this);
            })
            .finally(() => {
              this.secondClick = false;
            });
        }, validator => {
          console.warn(validator);
        });
      },
      openDictionary(type, item) {
        if (!this.projectId) {
          let reqPerm = ['public_api_create'];
          let crtPerm = [];
          let resourceData = {};
          if (!['JION', 'ADD'].includes(type)) {
            reqPerm = ['public_api_manage'];
            crtPerm = item.auth_actions;
            resourceData = {
              public_api: [{
                id: item.id,
                name: item.name,
              }],
            };
          }
          if (crtPerm && !this.hasPermission(reqPerm, crtPerm)) {
            this.applyForPermission(reqPerm, crtPerm, resourceData);
            return;
          }
        }
        this.dictDataTable.showDialog = true;
        this.dictDataTable.type = type;
        this.dictDataTable.title = type === 'ADD' ? this.$t('m.systemConfig["新增系统"]') : (item ? this.$t('m.systemConfig["修改系统"]') : this.$t('m.systemConfig["接入系统"]'));
        this.dictDataTable.formInfo = {
          addName: '',
          addCode: '',
          name: item ? item.name : '',
          desc: item ? item.desc : '',
          domain: item ? item.domain : '',
          code: item ? item.code : '',
          owners: item ? item.owners : '',
          personInCharge: item ? item.owners.split(',') : [],
          contact_information: item ? item.contact_information : '',
          id: item ? item.id : '',
          system_id: item ? item.system_id : '',
          is_activated: item ? item.is_activated : true,
        };
        this.$refs.dropdown.hide();
      },
      closeDictionary() {
        this.dictDataTable.showDialog = false;
      },
      dropdownShow() {
        this.isDropdownShow = true;
      },
      dropdownHide() {
        this.isDropdownShow = false;
      },
      // 二次弹窗确认
      openDelete(item) {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.systemConfig["确认移除系统？"]'),
          subTitle: this.$t('m.systemConfig["移除后，将无法使用该系统，请谨慎操作"]'),
          confirmFn: () => {
            const id = item.id;
            if (this.secondClick) {
              return;
            }
            this.secondClick = true;
            this.$store.dispatch('apiRemote/delete_remote_system', id).then(() => {
              this.$bkMessage({
                message: this.$t('m.systemConfig["删除成功"]'),
                theme: 'success',
              });
              this.getRemoteSystemData();
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.secondClick = false;
              });
          },
        });
      },
    },
  };
</script>

<style lang="scss" scoped>
    @import '../../../scss/mixins/clearfix.scss';
    @import '../../../scss/mixins/scroller.scss';
    .bk-api-tree {
        padding: 20px 10px;
    }

    .bk-tree-info {
        color: #737987;
        font-size: 14px;
        line-height: 36px;
        min-height: 300px;

        .bk-tree-group {
            height: 100%;
            @include scroller;
            @include clearfix;
            overflow: auto;
            text-align: center;
            li {
                cursor: pointer;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
            }

            .bk-group-li {
                color: #4b8fff;
                background-color: #e1ecff;
                
            }

            .bk-group-name {
                display: inline-block;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
                text-align: left;
                width: calc(100% - 50px);
            }

            .bk-group-child-name {
                display: inline-block;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
                width: calc(100% - 20px);
            }

            .bk-p42 {
                padding-left: 42px;
            }

            .bk-p18 {
                padding-left: 18px;
                display: flex;
                align-items: center;
            }

            .bk-ml5 {
                margin-right: 5px;
            }
        }
    }

    .bk-handel {
        position: relative;

        .bk-icon.icon-more.bk-tree-point.bk-point-selected {
            position: absolute;
            top: 8px;
            right: 0;
            // color: #737987;
            font-size: 19px;
            line-height: 19px;
            cursor: pointer;
            font-weight: 500;
        }
    }

    .bk-group-parent.bk-handel {

        position: relative;

        .bk-edit {
            &:hover {
                .bk-more {
                    display: inline-block;
                }
            }
        }

        .bk-more {
            display: none;
            position: fixed;
            width: 79px;
            // height: 108px;
            background: #fff;
            -webkit-box-shadow: 0px 2px 2px 2px rgba(227, 225, 225, 0.5);
            box-shadow: 0px 2px 2px 2px rgba(227, 225, 225, 0.5);
            border-radius: 2px;
            z-index: 10;

            ul {
                width: 100%;
                height: 100%;
            }

            li {
                width: 100%;
                height: 36px;
                line-height: 36px;
                color: #63656E;
                text-align: center;
                cursor: pointer;
                font-size: 14px;

                &:hover {
                    background: rgba(163, 197, 253, 0.2);
                    color: #3A84FF;
                }
            }
        }
    }

    .bk-api-tree .bk-form .bk-label {
        font-weight: 500;
    }
    .group-text {
        cursor: pointer;
    }
</style>
