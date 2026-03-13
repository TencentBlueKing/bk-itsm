<template>
  <div class="bk-basic-node" v-bkloading="{ isLoading: isLoading }">
    <basic-card>
      <bk-form
        ref="webForm"
        :label-width="150"
        :model="formData"
        :rules="rules"
        form-type="vertical">
        <bk-form-item
          v-if="isStatus"
          :label="$t(`m['节点名称']`)"
          :ext-cls="'bk-form-width bk-form-display'"
          property="name"
          error-display-type="normal"
          required>
          <bk-input v-model="formData.name"></bk-input>
        </bk-form-item>
        <desc-info v-model="formData.desc"></desc-info>
        <bk-form-item
          v-if="isStatus"
          data-test-id="devops-component-processor"
          :label="$t(`m.treeinfo['处理人：']`)"
          :required="true">
          <div @click="checkStatus.processors = false">
            <deal-person
              ref="processors"
              :value="processorsInfo"
              :show-overbook="true"
              :node-info="configur"
              :exclude-role-type-list="excludeProcessor">
            </deal-person>
          </div>
        </bk-form-item>
        <bk-form-item
          :label="'URL'"
          :ext-cls="'bk-form-display'"
          required
          property="url"
          error-display-type="normal">
          <bk-input v-model="formData.url"
            ref="urlInput"
            :clearable="true"
            :font-size="'medium'"
            :placeholder="isStatus ? $t(`m['以http://或https://开头(引用变量忽略), 输入“{{”可选择引用变量']`) : $t(`m['请输入']`)"
            :disabled="disable"
            @change="handleUrlChange">
            <bk-dropdown-menu
              ref="dropdown"
              class="group-text"
              slot="prepend"
              :font-size="'medium'"
              @show="isDropdownShow = true"
              @hide="isDropdownShow = false">
              <bk-button type="primary" slot="dropdown-trigger">
                <template v-for="(item, index) in requestOptions">
                  <span v-if="curEq === item" :key="index">{{item}}</span>
                </template>
                <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShow }]"></i>
              </bk-button>
              <ul class="bk-dropdown-list" slot="dropdown-content">
                <li v-for="(item, index) in requestOptions"
                  :key="index">
                  <a href="javascript:;" @click="selectRequsetOpt(item)">{{ item }}</a>
                </li>
              </ul>
            </bk-dropdown-menu>
          </bk-input>
          <div v-show="filterVariableList.length !== 0" class="select-variables">
            <ul>
              <li v-for="(item, index) in filterVariableList"
                :key="index"
                @click="handleSelectContent(item)">
                {{item.name}}
                <span class="variable-key">({{item.key}})</span>
              </li>
            </ul>
          </div>
        </bk-form-item>
        <bk-form-item :ext-cls="'bk-form-display'">
          <div class="requset-config">
            <request-config
              ref="requestConfig"
              :type="curEq"
              :configur="configur"
              :is-status="isStatus"
              :state-list="stateList"
              :disable="disable"
              @changeFormStatus="changeFormStatus">
            </request-config>
            <p v-if="errorTip" class="error-tip">{{ $t(`m['已选参数的字段名和值不能为空']`) }}</p>
          </div>
        </bk-form-item>
        <bk-form-item :label="$t(`m['成功条件']`)" :ext-cls="'bk-form-display'">
          <bk-input v-model="formData.success_exp" :disabled="disable" :placeholder="$t(`m['输入你所要的条件，如： resp.result==ture 或者 false']`)"></bk-input>
        </bk-form-item>
        <bk-form-item v-if="isStatus" :label="$t(`m['返回变量']`)" :ext-cls="'bk-form-display'">
          <bk-table :data="returnReslut"
            :size="'small'">
            <bk-table-column :label="$t(`m['变量名称']`)">
              <template slot-scope="props">
                <bk-input :behavior="'simplicity'" v-model="props.row.name" :disabled="disable" @change="changeReturnInput(props.row, props.$index)"></bk-input>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m['来源']`)">
              <template slot-scope="props">
                <bk-input :behavior="'simplicity'" v-model="props.row.ref_path" :disabled="disable" :placeholder="$t(`m['输入变量来源，如：resp.message']`)" @change="changeReturnInput(props.row, props.$index)"></bk-input>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m['操作']`)" width="100">
              <template slot-scope="props" v-if="!disable && isShowDelete !== returnReslut.indexOf(props.row)">
                <i class="bk-itsm-icon icon-flow-other-add result-icon" @click="addReturnReslut"></i>
                <i class="bk-itsm-icon icon-flow-other-reduc result-icon"
                  :class="{ 'no-delete': retrunResultIsEmtry }"
                  @click="deleteReturnReslut(props.row)">
                </i>
              </template>
            </bk-table-column>
          </bk-table>
        </bk-form-item>
      </bk-form>
      <common-trigger-list
        v-if="isStatus"
        ref="commonTriggerList"
        :origin="'state'"
        :node-type="configur.type"
        :source-id="flowInfo.id"
        :sender="configur.id"
        :table="flowInfo.table">
      </common-trigger-list>

      <div v-if="isStatus" class="mt20" style="font-size: 0">
        <bk-button :theme="'primary'"
          data-test-id="devops-button-submit"
          :title="$t(`m.treeinfo['确定']`)"
          :loading="secondClick"
          class="mr10"
          @click="submit">
          {{$t(`m.treeinfo['确定']`)}}
        </bk-button>
        <bk-button :theme="'default'"
          data-test-id="devops-button-close"
          :title="$t(`m.treeinfo['取消']`)"
          class="mr10"
          @click="closeNode">
          {{$t(`m.treeinfo['取消']`)}}
        </bk-button>
      </div>
    </basic-card>
  </div>
</template>

<script>
  import descInfo from './components/descInfo.vue';
  import requestConfig from './components/requestConfig.vue';
  import BasicCard from '@/components/common/layout/BasicCard.vue';
  import dealPerson from './components/dealPerson.vue';
  import commonTriggerList from '../../taskTemplate/components/commonTriggerList';
  export default {
    name: 'webHookNode',
    components: {
      BasicCard,
      dealPerson,
      commonTriggerList,
      requestConfig,
      descInfo,
    },
    props: {
      // 流程信息
      flowInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      // 节点信息
      configur: {
        type: Object,
        default() {
          return {};
        },
      },
      isStatus: {
        type: Boolean,
        default() {
          return true;
        },
      },
      disable: {
        type: Boolean,
        default() {
          return false;
        },
      },
      taskErrorTip: {
        type: Boolean,
        default() {
          return false;
        },
      },
    },
    data() {
      return {
        isLoading: false,
        secondClick: false,
        isDropdownShow: false,
        curEq: 'GET',
        requestOptions: ['GET', 'POST'],
        formData: {
          name: '',
          desc: '',
          url: '',
          success_exp: '',
        },
        rules: {
          name: [
            {
              required: true,
              message: this.$t('m[\'必填项\']'),
              trigger: 'blur',
            },
          ],
          url: [
            {
              required: true,
              message: this.$t('m[\'必填项\']'),
              trigger: 'blur',
            },
            {
              validator: (val) => {
                if (val.indexOf('{{') !== -1) {
                  return true;
                }
                const reg = /(http|https):\/\/\S*/;
                return reg.test(val);
              },
              message: this.$t('m[\'必需以http://或https://开头\']'),
              trigger: 'blur',
            },
          ],
        },
        returnReslut: [
          {
            name: '',
            ref_path: '',
            check: false,
          },
        ],
        processorsInfo: {
          type: '',
          value: '',
        },
        checkStatus: {
          delivers: false,
          processors: false,
        },
        excludeProcessor: ['EMPTY', 'OPEN'],
        isShowUrlVariable: false,
        filterParams: '',
        stateList: [],
        errorTip: false,
        urlField: '',
      };
    },
    computed: {
      retrunResultIsEmtry() {
        return this.returnReslut.length <= 1;
      },
      filterVariableList() {
        if (!this.formData.url) return [];
        const index = this.formData.url.lastIndexOf('\{\{');
        if (index !== -1) {
          const params = this.formData.url.substring(index + 2, this.formData.url.length) || '';
          this.filterParams = params || '';
          const list = this.stateList.filter(item => item.name.indexOf(params) !== -1 || item.key.indexOf(params) !== -1);
          if (list.length !== 0) {
            this.$refs.urlInput.focus();
          }
          return list;
        }
        return [];
      },
      isShowDelete() {
        return this.returnReslut.length - 1;
      },
    },
    watch: {
      taskErrorTip(val) {
        this.errorTip = val;
      },
    },
    mounted() {
      this.getWebHookDetail();
      this.getRelatedFields();
    },
    methods: {
      getWebHookDetail() {
        if (this.isStatus) {
          console.log(this.configur);
          if (Object.keys(this.configur.extras).length !== 0) {
            const { url, success_exp, method } = this.configur.extras.webhook_info;
            this.formData.name = this.configur.name;
            this.formData.desc = this.configur.desc;
            this.formData.success_exp = success_exp;
            this.formData.url = url;
            this.curEq = method;
            console.log(this.formData);
            this.processorsInfo.type = this.configur.processors_type;
            this.processorsInfo.value = this.configur.processors;
    
            this.returnReslut = this.configur.variables.outputs.length !== 0 ? [...this.configur.variables.outputs, ...this.returnReslut] : [{ name: '', ref_path: '', check: false }];
          }
        } else {
          const { url, success_exp, method } = this.configur.api_info.webhook_info;
          this.formData.name = this.configur.name;
          this.formData.success_exp = success_exp;
          this.formData.url = url;
          this.curEq = method;
        }
      },
      getRelatedFields() {
        if (!this.isStatus) return;
        const params = {
          workflow: this.flowInfo.id,
          state: this.configur.id,
          field: '',
        };
        this.$store.dispatch('apiRemote/get_related_fields', params).then(res => {
          this.stateList = res.data;
        });
      },
      handleSelectContent(item) {
        this.formData.url = `${this.formData.url.slice(0, -(this.filterParams.length + 2))}{{ ${item.key}}}`;
        this.$refs.urlInput.focus();
      },
      handleUrlChange(value) {
        if (value.endsWith('{{')) {
          this.isShowUrlVariable = true;
        } else {
          this.isShowUrlVariable = false;
        }
      },
      selectRequsetOpt(item) {
        this.curEq = item;
      },
      closeNode() {
        this.$parent.closeConfigur();
      },
      addReturnReslut() {
        this.returnReslut.push({
          name: '',
          ref_path: '',
          check: false,
        });
      },
      changeReturnInput(item) {
        if (!item.check) {
          item.check = true;
          this.returnReslut.push({
            name: '',
            ref_path: '',
            check: false,
          });
        } else {
          const { name, ref_path } = item;
          const checkList = [name, ref_path];
          if (checkList.every(item => item === '')) {
            this.returnReslut.pop();
            item.check = false;
          }
        }
      },
      changeFormStatus(val) {
        this.errorTip = val;
      },
      validate() {
        return this.$refs.webForm.validate();
      },
      deleteReturnReslut(row) {
        if (this.retrunResultIsEmtry) return;
        const index = this.returnReslut.indexOf(row);
        if (index !== -1) {
          this.returnReslut.splice(index, 1);
        }
      },
      submit() {
        Promise.all([this.$refs.processors.verifyValue(), this.$refs.webForm.validate()]).then(() => {
          const { value: processors, type: processors_type } = this.$refs.processors.getValue();
          const { queryParams, bodyFormData, bodyWwwForm, authRadio, auth_config, settings, bodyValue, bodyRadio, rawType, headers } = this.$refs.requestConfig.config;
          const query_params = queryParams.filter(item => item.select);
          const outputs = this.returnReslut.filter(item => item.name !== '');
          outputs.forEach(item => {
            item.source = 'global';
            item.type = 'string';
          });
          // auth
          const auth_params = {
            auth_type: authRadio !== 'None' ? authRadio : '',
            auth_config: {},
          };
          const { username, password, Token } = auth_config;
          if (authRadio === 'basic_auth') {
            auth_params.auth_config.username = username;
            auth_params.auth_config.password = password;
          } else if (authRadio === 'bearer_token') {
            auth_params.auth_config.token = Token;
          }
          // headers
          const headers_params = headers.filter(item => item.select);
          // body
          const body_params = {
            type: bodyRadio !== 'none' ? bodyRadio : '',
            raw_type: '',
            content: '',
          };
          if (bodyRadio === 'form-data') {
            body_params.content = bodyFormData.filter(item => item.select);
          } else if (bodyRadio === 'x-www-form-urlencoded') {
            body_params.content = bodyWwwForm.filter(item => item.select);
          } else if (bodyRadio === 'raw') {
            body_params.raw_type = rawType || 'Text';
            body_params.content = bodyValue;
          }
          // settings
          const settings_parmas = {
            timeout: Number(settings.timeout),
          };
          const params = {
            name: this.formData.name,
            desc: this.formData.desc || undefined,
            processors: processors || '',
            processors_type: processors_type || '',
            type: 'WEBHOOK',
            is_draft: false,
            extras: {
              webhook_info: {
                method: this.curEq,
                url: this.formData.url,
                query_params,
                auth: auth_params,
                headers: headers_params,
                body: body_params,
                settings: settings_parmas,
                success_exp: this.formData.success_exp,
              },
            },
            variables: {
              outputs,
              inputs: [],
            },
            workflow: this.configur.workflow,
          };
          // 校验 勾选参数的key value
          if (this.curEq === 'GET') {
            this.errorTip = !query_params.every(item => item.key !== '' && item.value !== '');
          } else if (typeof body_params.content !== 'string') {
            this.errorTip = ![body_params.content, query_params].every(item => item.every(ite => ite.key !== '' && ite.value !== ''));
          }
          if (this.errorTip) return;
          if (this.secondClick) return;
          this.secondClick = true;
          const stateId = this.configur.id;
          this.$store.dispatch('cdeploy/putWebHook', { params, stateId }).then(() => {
            this.$bkMessage({
              message: this.$t('m.treeinfo["保存成功"]'),
              theme: 'success',
            });
            this.$parent.closeConfigur();
          }, e => {
            console.log(e);
          })
            .finally(() => {
              this.secondClick = false;
            });
        });
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../../scss/mixins/scroller.scss';
    .bk-form {
        display: flex;
        flex-direction: column;
    }
    .bk-basic-node {
        padding: 30px 40px;
        height: 100%;
        background-color: #FAFBFD;
        overflow: auto;
        @include scroller;
        /deep/ .common-section-card-label {
            display: none;
        }
        /deep/ .common-section-card-body {
            padding: 20px;
        }
        /deep/ .bk-form-width {
            width: 448px;
        }
        .piprline-title {
            font-size: 14px;
            p:nth-child(1) {
                color: #63656e;
                margin-bottom: 4px;
            }
            p:nth-child(2) {
                font-size: 12px;
                color: #929397;
            }
        }
    }
    .requset-config {
        min-height: 120px;
        margin: 10px 0;
        padding: 0 16px;
        background-color: #f5f7fa;
        .error-tip {
            font-size: 12px;
            color: red;
            margin-left: 10px;
        }
    }
    .bk-basic-info {
        padding-bottom: 20px;
        border-bottom: 1px solid #E9EDF1;
        margin-bottom: 20px;
    }
    .bk-form-width {
        width: 448px;
    }
    .bk-form-display {
        position: relative;
        float: left;
        margin-right: 10px;
        .select-variables {
            width: 492px;
            height: 230px;
            position: absolute;
            border-radius: 4px;
            background: #fff;
            font-size: 14px;
            border: 1px solid #c4c6cc;
            top: 35px;
            left: 71px;
            z-index: 2000;
            overflow-y: auto;
            @include scroller;
            ul {
                padding: 5px;
                li {
                    height: 30px;
                    cursor: pointer;
                    color: #75777f;
                    &:hover {
                        background-color: #e1ecff;
                        color: #3a84ff;
                    }
                }
            }
        }
    }
    .setion-title-icon {
        margin-top: 5px;
    }
    .result-icon {
        font-size: 16px;
        color: #c4c6cc;
        margin-right: 10px;
        cursor: pointer;
    }
    .no-delete {
        color: #eaebf0;
        cursor: auto;
    }
    .variable-key {
        font-size: 12px;
        color: #c4c6cc;
        margin-left: 10px;
    }
</style>
