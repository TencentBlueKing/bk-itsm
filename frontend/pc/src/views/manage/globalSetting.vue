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
  <div class="bk-itsm-service">
    <div class="is-title" :class="{ 'bk-title-left': !sliderStatus }">
      <p class="bk-come-back">
        {{ $t('m["全局配置"]') }}
      </p>
    </div>
    <div class="itsm-page-content">
      <!-- 附件存储 -->
      <div class="bk-system-file">
        <div class="bk-file-left">
          <p class="bk-left-title">{{ $t('m.home["附件存储"]') }}</p>
          <div class="bk-left-content">
            <p class="bk-left-message">
              <span v-if=" !moduleInfo.systemPath.formerValue">
                {{ $t('m.home["（您尚未设置附件存放的目录，请填写）"]') }}
              </span>
              <span v-else>{{ $t('m.home["当前存放附件文件的目录为"]') }}：</span>
            </p>
            <bk-input v-model.trim="moduleInfo.systemPath.nowValue"
              :disabled="!moduleInfo.systemPath.changing || isAllStatusGetting"
              :placeholder="$t(`m.home['请填写路径']`)">
            </bk-input>
            <div class="bk-left-btn">
              <span
                v-if="!moduleInfo.systemPath.changing"
                v-cursor="{ active: !hasPermission(['global_settings_manage']) }"
                :class="['bk-change-place', {
                  'btn-permission-disable': !hasPermission(['global_settings_manage'])
                }]"
                @click="handleChangeSystemPath">
                {{ $t('m.home["更改位置"]') }}
              </span>
              <template v-else-if="moduleInfo.systemPath.formerValue && moduleInfo.systemPath.changing">
                <bk-button
                  theme="primary"
                  :title="$t(`m.home['保存']`)"
                  class="mr10"
                  :disabled="!moduleInfo.systemPath.nowValue"
                  @click="allSwitchChange('off','systemPath')">
                  {{$t(`m.home['保存']`)}}
                </bk-button>
                <bk-button theme="default"
                  :title="$t(`m.home['取消']`)"
                  class="mr10"
                  @click="cancelPath">
                  {{$t(`m.home['取消']`)}}
                </bk-button>
              </template>
              <bk-button v-else
                theme="primary"
                :disabled="!moduleInfo.systemPath.nowValue || isAllStatusGetting"
                :title="$t(`m.home['提交']`)"
                class="mr10"
                @click="allSwitchChange('off','systemPath')">
                {{$t(`m.home['提交']`)}}
              </bk-button>
            </div>
          </div>
        </div>
        <div class="bk-file-right">
          <p class="bk-right-title">{{ $t('m.home["附件存储"]') }}</p>
          <ul class="bk-number-ul">
            <li>
              {{ $t('m.home["请配置合法的系统路径，并保证每台AppServer都能访问该目录（如nfs）"]') }}
            </li>
            <li>
              {{ $t('m.home["若需更换目录，请务必将原目录文件拷贝到新目录"]') }}
            </li>
            <li>
              {{ $t('m.home["蓝鲸企业版默认提供了NFS服务，可以直接配置目录为："]') }}
              <span class="bk-red">/data/app/code/USERRES/</span>
            </li>
            <li>
              {{ $t('m.home["企业版"]') }}
              <span class="bk-red">2.2.x</span>
              {{ $t('m.home["需要先升级SaaS部署脚本（"]') }}
              <span class="bk-red">2.4</span>
              {{ $t('m.home["以后的版本不需要），请下载"]') }}
              <span class="bk-red">
                <a target="blank" :href="downUrl">{{ $t('m.home["升级压缩包"]') }}</a>
              </span>
              {{ $t('m.home["后按照"]') }}
              <span class="bk-red">readme</span>
              {{ $t('m.home["进行操作"]') }}
            </li>
          </ul>
        </div>
      </div>
      <!-- 清除缓存 -->
      <div class="bk-system-file">
        <div class="bk-file-left">
          <p class="bk-left-title">{{ $t('m.home["清除缓存"]') }}</p>
          <div class="bk-left-content">
            <p class="bk-left-message">
              {{ $t('m.home["缓存内容"]') }}：
            </p>
            <p class="bk-left-message">
              1.{{ $t('m.home["业务列表缓存"]') }}
            </p>
            <p class="bk-left-message">
              2.{{ $t('m.home["业务角色及人员列表缓存"]') }}
            </p>
            <div class="bk-left-btn">
              <bk-button
                v-cursor="{ active: !hasPermission(['global_settings_manage']) }"
                theme="primary"
                :title="$t(`m.home['一键清除']`)"
                :class="['mr10', {
                  'btn-permission-disable': !hasPermission(['global_settings_manage'])
                }]"
                @click="handleClear">
                {{ $t('m.home["一键清除"]') }}
              </bk-button>
              <span class="bk-clear-info">
                {{ $t('m.home["上次清除时间："]') }}{{clearStorageTime}}
              </span>
            </div>
          </div>
        </div>
        <div class="bk-file-right">
          <p class="bk-right-title">{{ $t('m.home["缓存清除"]') }}</p>
          <ul class="bk-number-ul">
            <li>
              {{ $t('m.home["如需即时更新来自CMDB的最新数据，可以通过手动清除缓存获取最新数据。"]') }}
            </li>
          </ul>
        </div>
      </div>
      <!-- 功能开关开关-->
      <div class="bk-system-file">
        <div class="bk-file-left">
          <p class="bk-left-title">{{ $t('m.home["功能开关"]') }}</p>
          <div class="bk-left-content">
            <div class="bk-left-btn" v-for="(item,key) in moduleInfo" :key="key">
              <template v-if="onceSlaSwitcher(item)">
                <span class="bk-clear-info">
                  {{ item.title }}
                </span>
                <bk-switcher
                  v-model="item.open"
                  v-cursor="{ active: !hasPermission(['global_settings_manage']) }"
                  :class="{
                    'text-permission-disable': !hasPermission(['global_settings_manage'])
                  }"
                  :disabled="isAllStatusGetting || !hasPermission(['global_settings_manage'])"
                  size="small"
                  :on-text="$t(`m.home['打开']`)"
                  :off-text="$t(`m.home['关闭']`)"
                  @change="allSwitchChange($event,key)"></bk-switcher>
              </template>
            </div>
          </div>
        </div>
        <div class="bk-file-right">
          <p class="bk-right-title">{{ $t('m.home["功能开关"]') }}</p>
          <ul class="bk-number-ul">
            <li>
              {{ $t('m.home["“功能开关”可以自定义启停以下ITSM功能模块，关闭后，该模块对应的所有的功能将被隐藏。"]') }}
            </li>
            <li v-if="moduleInfo.sla.open">
              {{ $t('m.home["“SLA功能开关” 关闭后，该按钮开关和模块对应的所有的功能将被隐藏。"]') }}
            </li>
          </ul>
        </div>
      </div>
    </div>
    <!-- 数据库升级 -->
    <!-- <div class="bk-system-file">
            <div class="bk-file-left">
                <p class="bk-left-title">{{ $t('m.home["数据库升级"]') }}</p>
                <div class="bk-left-content">
                    <p class="bk-left-message">
                        {{ $t('m.home["选择升级前的版本号以进行相应的数据库升级："]') }}
                    </p>
                    <p class="bk-left-select">
                        {{ $t('m.home["最新版本号："]') }}<span>V{{updatedVersion}}</span>
                    </p>
                    <p class="bk-left-select">
                        <span class="bk-select-span">{{ $t('m.home["旧版本号："]') }}</span>
                        <bk-select v-model="formerVersion"
                            style="width: 250px; float: left;"
                            searchable>
                            <bk-option v-for="option in versionList"
                                :key="option.name"
                                :id="option.name"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                    </p>
                    <div class="bk-left-btn">
                        <bk-button
                            theme="primary"
                            :title="$t(`m.home['一键升级']`)"
                            :disabled="!(formerVersion.length > 0)"
                            class="mr10"
                            @click="onKeyUpdate">
                            {{ $t('m.home["一键升级"]') }}
                        </bk-button>
                        <bk-button
                            theme="default"
                            :title="$t(`m.home['升级记录']`)"
                            class="mr10"
                            @click="seeLog">
                            {{ $t('m.home["升级记录"]') }}
                        </bk-button>
                    </div>
                </div>
            </div>
            <div class="bk-file-right">
                <p class="bk-right-title">{{ $t('m.home["数据库升级："]') }}</p>
                <ul class="bk-number-ul">
                    <li>
                        {{ $t('m.home["使用本功能前，请务必确保当前版本为最新。旧版本号为执行版本更新前的版本。"]') }}
                    </li>
                </ul>
            </div>
        </div> -->
    <bk-sideslider
      :is-show.sync="versionLogData.show"
      :title="versionLogData.title"
      :width="versionLogData.width">
      <div class="p20" slot="content" v-if="versionLogData.show">
        <version-log :version-log-data="versionLogData"></version-log>
      </div>
    </bk-sideslider>
  </div>
</template>
<script>
  import { errorHandler } from '../../utils/errorHandler';
  import versionLog from '../systemConfig/component/versionLog.vue';
  import permission from '@/mixins/permission.js';

  export default {
    name: 'attachmentStorage',
    components: {
      versionLog,
    },
    mixins: [permission],
    data() {
      return {
        clearStorageTime: localStorage.getItem('clearStorageTime') || this.$t('m.home["暂无"]'),
        // placeholder: "请填写以 ''/'' 结尾的绝对目录.",
        placeholder: this.$t('m.home["请填写路径"]'),
        issending: false,
        downUrl: (`${window.STATIC_URL}`) + 'help/itsm_nfs.tar.gz',
        rowVersionList: [],
        versionList: [],
        formerVersion: '',
        updatedVersion: '',
        versionLogData: {
          title: this.$t('m.home["升级记录"]'),
          show: false,
          width: 700,
        },
        // 开关功能对照表
        switchKeyMap: {
          SYS_FILE_PATH: 'systemPath',
          FLOW_PREVIEW: 'preview',
          WIKI_SWITCH: 'wiki',
          CHILD_TICKET_SWITCH: 'inherit',
          SLA_SWITCH: 'sla',
          TRIGGER_SWITCH: 'trigger',
          TASK_SWITCH: 'task',
          FIRST_STATE_SWITCH: 'basic',
          TABLE_FIELDS_SWITCH: 'module',
          SMS_COMMENT_SWITCH: 'smsComment',
        },
        // 开关功能总体信息
        moduleInfo: {
          basic: {
            id: '',
            title: this.$t('m.home["提单信息展示开关："]'),
            open: false,
            isAvailable: true,
          },
          module: {
            id: '',
            title: this.$t('m.home["基础信息展示开关："]'),
            open: false,
            isAvailable: true,
          },
          systemPath: {
            id: '',
            formerValue: '',
            nowValue: '',
            changing: false,
          },
          preview: {
            id: '',
            title: this.$t('m.home["流程预览功能开关："]'),
            open: false,
            isAvailable: true,
          },
          sla: {
            id: '',
            title: this.$t('m.home["SLA功能开关："]'),
            open: false,
            isAvailable: true,
          },
          inherit: {
            id: '',
            title: this.$t('m.home["母子单功能开关："]'),
            open: false,
            isAvailable: true,
          },
          wiki: {
            id: '',
            title: this.$t('m.home["知识库功能开关："]'),
            open: false,
            isAvailable: false,
          },
          task: {
            id: '',
            title: this.$t('m.home["任务功能开关："]'),
            open: false,
            isAvailable: true,
          },
          trigger: {
            id: '',
            title: this.$t('m.home["触发器功能开关："]'),
            open: false,
            isAvailable: true,
          },
          smsComment: {
            id: '',
            title: this.$t('m.home["短信评论开关："]'),
            open: false,
            isAvailable: true,
          },
        },
        // 获取开关状态按钮禁用
        isAllStatusGetting: false,
      };
    },
    computed: {
      sliderStatus() {
        return this.$store.state.common.slideStatus;
      },
    },
    watch: {},
    async created() {
      await this.getEnableStatusAndStorage();
    },
    async mounted() {
      await this.getVersionList();
    },
    methods: {
      onceSlaSwitcher(item) {
        const { isAvailable, open, title } = item;
        if (title === 'SLA功能开关：') {
          return open;
        }
        return isAvailable;
      },
      async getEnableStatusAndStorage() {
        this.isAllStatusGetting = true;
        await this.$store.dispatch('attachmentStorage/getEnableStatus').then((res) => {
          const tempObj = {};
          res.data.forEach((item) => {
            if (item.key === 'SYS_FILE_PATH') {
              tempObj.SYS_FILE_PATH = item.value;
              this.moduleInfo.systemPath.nowValue = item.value;
              this.moduleInfo.systemPath.formerValue = item.value;
              this.moduleInfo.systemPath.id = item.id || '';
            } else if (item.key !== 'SERVICE_SWITCH' && this.switchKeyMap[item.key]) {
              tempObj[item.key] = item.value === 'on';
              this.moduleInfo[this.switchKeyMap[item.key]].open = tempObj[item.key];
              this.moduleInfo[this.switchKeyMap[item.key]].id = item.id || '';
            }
          });
          this.$store.commit('changeOpenFunction', tempObj);
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isAllStatusGetting = false;
          });
      },
      cancelPath() {
        this.moduleInfo.systemPath.changing = false;
        this.moduleInfo.systemPath.nowValue = this.moduleInfo.systemPath.formerValue;
      },
      async allSwitchChange(openStatus, type) {
        if (!this.hasPermission(['global_settings_manage'])) {
          this.applyForPermission(['global_settings_manage'], [], {});
          return;
        }
        if (this.isAllStatusGetting) {
          return;
        }
        const { id } = this.moduleInfo[type];
        const params = {
          type: 'FUNCTION',
          key: Object.keys(this.switchKeyMap)[Object.values(this.switchKeyMap).indexOf(type)],
          value: openStatus ? 'on' : 'off',
        };
        if (type === 'systemPath') {
          params.value = this.moduleInfo.systemPath.nowValue;
          params.type = 'PATH';
        }
        this.isAllStatusGetting = true;
        await this.$store.dispatch('attachmentStorage/putEnableStatus', { params, id }).then(() => {
          this.$bkMessage({
            message: this.$t('m.home["更新成功"]'),
            theme: 'success',
          });
          this.getEnableStatusAndStorage();
        })
          .catch((res) => {
            errorHandler(res, this);
            this.getEnableStatusAndStorage();
            this.moduleInfo.systemPath.nowValue = this.moduleInfo.systemPath.formerValue;
          })
          .finally(() => {
            this.moduleInfo.systemPath.changing = false;
            this.isAllStatusGetting = false;
          });
      },
      // 一键清除 缓存
      handleClear() {
        if (!this.hasPermission(['global_settings_manage'])) {
          this.applyForPermission(['global_settings_manage'], [], {});
          return;
        }
        // https://paas-poc.o.qcloud.com/t/itsm/api/misc/clean_cache/
        if (this.issending === true) {
          return;
        }
        this.issending = true;
        this.$store.dispatch('attachmentStorage/clearStorage', {}).then(() => {
          this.$bkMessage({
            message: this.$t('m.home["清除缓存成功"]'),
            theme: 'success',
          });
          this.clearStorageTime = new Date().toLocaleString('zh', { hour12: false });
          window.localStorage.setItem('clearStorageTime', this.clearStorageTime);
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            setTimeout(() => {
              this.issending = false;
            }, 10000);
          });
      },
      seeLog() {
        this.versionLogData.show = true;
      },
      async getVersionList() {
        await this.$store.dispatch('version/version_logs').then((res) => {
          this.rowVersionList = res.data.data;
          this.updatedVersion = this.rowVersionList[0].version;
          this.rowVersionList.forEach((item) => {
            const ite = {
              name: `V${item.version}`,
            };
            this.versionList.push(ite);
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {

          });
      },
      async onKeyUpdate() {
        const params = {
          version_from: this.formerVersion.substr(1, this.formerVersion.length - 1),
          version_to: this.updatedVersion,
        };
        await this.$store.dispatch('version/oneKeymigrate', params).then(() => {
          this.$bkMessage({
            message: this.$t('m.home["提交成功，后台执行升级中"]'),
            theme: 'success',
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.formerVersion = '';
          });
      },
      handleChangeSystemPath() {
        if (!this.hasPermission(['global_settings_manage'])) {
          this.applyForPermission(['global_settings_manage'], [], {});
          return;
        }
        this.moduleInfo.systemPath.changing = true;
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../scss/mixins/clearfix.scss';
    @import '../../scss/mixins/scroller.scss';

    .bk-system-file {
        margin-bottom: 20px;
        @include clearfix;
    }
    .bk-file-left {
        float: left;
        width: 60%;
        background-color: #fff;
        border: 1px solid #dfe0e5;
        .bk-left-title {
            line-height: 40px;
            padding-left: 20px;
            border-bottom: 1px solid #dfe0e5;
            font-size: 16px;
            color: #424950;
        }
        .bk-left-content {
            padding: 16px 20px;
            .bk-left-message,
            .bk-left-select {
                line-height: 24px;
                font-size: 14px;
                color: #656770;
            }
            .bk-left-select {
                line-height: 32px;
                @include clearfix;
                .bk-select-span {
                    float: left;
                }
            }
            .bk-left-btn {
                margin-top: 15px;
                font-size: 14px;
                .bk-change-place {
                    color:#3E86FF;
                    cursor: pointer;
                }
                .bk-clear-info {
                    color: #656770;
                }
            }
        }
    }
    .bk-file-right {
        float: left;
        width: 40%;
        padding-left: 20px;
        .bk-right-title {
            font-weight: bold;
            line-height: 24px;
            color: #737987;
            font-size: 14px;
        }
        .bk-number-ul {
            padding-left: 14px;
            li {
                list-style: decimal;
                text-align: justify;
                color: #737987;
                line-height: 18px;
                font-size: 12px;
                margin-bottom: 6px;
                .bk-red {
                    color: #ff5656;
                }
            }
        }
    }
</style>
