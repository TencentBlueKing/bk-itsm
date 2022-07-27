<template>
  <div>
    <ul class="bk-config-tab">
      <li v-for="(item, index) in panels"
        :key="item.id"
        :class="{ 'bk-check-config': acticeTab === item.key }"
        @click="changeTab(item, index)">
        <span>{{ item.label }}</span>
        <!-- <span v-if="count[item.key]">{{ count[item.key] }}</span> -->
      </li>
    </ul>
    <template v-if="acticeTab === 'queryParams'">
      <div class="param-config">
        <i class="bk-itsm-icon icon-info-fail"></i>
        <span style="font-size: 12px;color: #63656e">{{ $t(`m['参数说明']`) }}</span>
        <params-table
          :list="config.queryParams"
          :state-list="stateList"
          :is-status="isStatus"
          :disable="disable"
          @changeFormStatus="changeFormStatus">
        </params-table>
      </div>
    </template>
    <template v-if="acticeTab === 'auth'">
      <div class="param-config">
        <bk-radio-group v-model="config.authRadio">
          <bk-radio :value="'none'">{{ $t(`m['无需认证']`) }}</bk-radio>
          <bk-radio :value="'bearer_token'">Bearer Token</bk-radio>
          <bk-radio :value="'basic_auth'">Basic Auth</bk-radio>
        </bk-radio-group>
        <div class="bk-radio-config">
          <div v-if="config.authRadio === 'none'">
            <span>{{ $t(`m['该请求不需要任何认证']`) }}</span>
          </div>
          <div v-else-if="config.authRadio === 'bearer_token'">
            <div class="config-option" style="width: 80%">
              <p class="mb5">TOKEN ：</p>
              <bk-input behavior="simplicity" :disabled="disable" :clearable="true" v-model="config.auth_config.Token"></bk-input>
            </div>
          </div>
          <div v-else style="display: flex">
            <div class="config-option">
              <p class="mb5">{{ $t(`m['用户名']`) }}：</p>
              <bk-input behavior="simplicity" :disabled="disable" :clearable="true" v-model="config.auth_config.username"></bk-input>
            </div>
            <div class="config-option">
              <p class="mb5">{{ $t(`m['密码']`) }}：</p>
              <bk-input behavior="simplicity" :disabled="disable" type="password" :clearable="true" v-model="config.auth_config.password"></bk-input>
            </div>
          </div>
        </div>
      </div>
    </template>
    <template v-if="acticeTab === 'body'">
      <div class="param-config">
        <div style="display: flex; align-items: center; margin-bottom: 8px">
          <bk-radio-group v-model="config.bodyRadio" style="width: 500px">
            <bk-radio :value="'none'">{{ $t(`m['默认']`) }}</bk-radio>
            <bk-radio :value="'form-data'" :disabled="radioDisabled">form-data</bk-radio>
            <bk-radio :value="'x-www-form-urlencoded'" :disabled="radioDisabled">x-www-form-urlencoded</bk-radio>
            <bk-radio :value="'raw'" :disabled="radioDisabled">raw</bk-radio>
          </bk-radio-group>
          <bk-select
            v-if="config.bodyRadio === 'raw'"
            ext-cls="select-custom"
            :disabled="false"
            v-model="config.rawType"
            style="width: 100px;"
            behavior="simplicity">
            <bk-option v-for="(option, index) in rawList"
              :key="index"
              :id="option"
              :name="option">
            </bk-option>
          </bk-select>
        </div>
        <template v-if="config.bodyRadio === 'form-data'">
          <params-table
            :list="config.bodyFormData"
            :is-status="isStatus"
            :disable="disable"
            :state-list="stateList"
            @changeFormStatus="changeFormStatus">
          </params-table>
        </template>
        <template v-if="config.bodyRadio === 'x-www-form-urlencoded'">
          <params-table
            :list="config.bodyWwwForm"
            :disable="disable"
            :is-status="isStatus"
            :state-list="stateList"
            @changeFormStatus="changeFormStatus">
          </params-table>
        </template>
        <template v-if="config.bodyRadio === 'raw'">
          <textarea
            ref="textarea"
            class="bk-form-textarea"
            style="resize: vertical"
            v-model="config.bodyValue"
            :placeholder="$t(`m['请输入']`)">
                    </textarea>
          <ul class="raw-select" v-show="rawVarList.length !== 0" :style="{ left: left + 'px', top: top + 'px' }">
            <li v-for="(item, index) in rawVarList"
              :key="index"
              @click="handleSelectContent(item)">
              {{item.name}}
              <span class="variable-key">({{item.key}})</span>
            </li>
          </ul>
        </template>
      </div>
    </template>
    <template v-if="acticeTab === 'headers'">
      <div class="param-config">
        <params-table :list="config.headers" :disable="disable" :state-list="stateList" :is-status="isStatus"></params-table>
      </div>
    </template>
    <template v-if="acticeTab === 'settings'">
      <div class="param-config">
        <div class="setting-option">
          <p class="mb5">{{ $t(`m['请求超时']`) }}</p>
          <div class="setting-content">
            <bk-input type="number" behavior="simplicity" :max="1000" :min="0" v-model="config.settings.timeout"></bk-input>
            <span style="margin-left: 5px">s</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
  import { position } from 'caret-pos';
  import paramsTable from './paramsTable.vue';
  export default {
    key: 'requestConfig',
    components: {
      paramsTable,
    },
    props: {
      type: {
        type: String,
        default: () => 'GET',
      },
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
      stateList: Array,
    },
    data() {
      return {
        left: 20,
        top: 72,
        acticeTab: 'queryParams',
        panels: [
          { key: 'queryParams', label: this.$t('m[\'参数\']'), count: 0 },
          { key: 'auth', label: this.$t('m[\'认证\']'), count: 0 },
          { key: 'headers', label: this.$t('m[\'头信息\']'), count: 0 },
          { key: 'body', label: this.$t('m[\'主体\']'), count: 0 },
          { key: 'settings', label: this.$t('m[\'设置\']'), count: 0 },
        ],
        list: [
          {
            check: false,
            key: '',
            value: '',
            desc: '',
            select: false,
          },
        ],
        rawList: ['JSON', 'HTML', 'XML', 'Text'],
        rawVarList: [],
        filterParams: '',
        config: {
          auth_config: {
            Token: '',
            username: '',
            password: '',
          },
          authRadio: 'none',
          queryParams: [
            {
              check: false,
              key: '',
              value: '',
              desc: '',
              select: false,
            },
          ],
          headers: [
            {
              check: false,
              key: '',
              value: '',
              desc: '',
              select: false,
            },
          ],
          bodyWwwForm: [
            {
              check: false,
              key: '',
              value: '',
              desc: '',
              select: false,
            },
          ],
          bodyFormData: [
            {
              check: false,
              key: '',
              value: '',
              desc: '',
              select: false,
            },
          ],
          bodyRadio: 'none',
          bodyValue: '',
          rawType: 'Text',
          settings: {
            timeout: 10,
          },
        },
      };
    },
    computed: {
      count() {
        const queryParams = this.config.queryParams.filter(item => item.select).length;
        return { queryParams };
      },
      radioDisabled() {
        return this.type === 'GET';
      },
    },
    watch: {
      type(val) {
        if (val === 'GET') {
          this.config.bodyRadio = 'none';
        }
      },
      'config.bodyValue'(val) {
        // 定位变量位置
        if (this.$refs.textarea) {
          const textDom = this.$refs.textarea;
          const pos = position(textDom);
          // const off = offset(textDom)
          this.left = pos.left + 10;
          this.top = pos.top + 40 + 24 + 2 - textDom.scrollTop;
          if (!val) {
            this.rawVarList = [];
            return;
          }
          const index = val.lastIndexOf('\{\{');
          if (index !== -1) {
            const params = val.substring(index + 2, val.length) || '';
            // console.log(params)
            this.filterParams = params;
            this.rawVarList = this.stateList.filter(item => item.name.indexOf(params) !== -1 || item.key.indexOf(params) !== -1);
            if (this.rawVarList.length !== 0) {
              this.$refs.textarea.focus();
            }
          }
        }
      },
    },
    created() {
      // document.onkeydown = (e) => {
      //     console.log(e)
      // }
    },
    mounted() {
      if (this.isStatus) {
        if (Object.keys(this.configur.extras).length !== 0) {
          const { auth, settings, query_params, body, headers } = this.configur.extras.webhook_info;
          this.config.queryParams = [...query_params, ...this.config.queryParams];
          this.config.headers = [...headers, ...this.config.headers];
          this.config.settings.timeout = settings.timeout;
          this.config.authRadio = auth.auth_type || 'none';
          // const { username, password, Token } = auth_config
          if (auth.auth_type === 'bearer_token') {
            this.config.auth_config.Token = auth.auth_config.token;
          } else if (auth.auth_type === 'basic_auth') {
            this.config.auth_config.username = auth.auth_config.username;
            this.config.auth_config.password = auth.auth_config.password;
          }
          this.config.bodyRadio = body.type || 'none';
          if (body.type === 'form-data') {
            this.config.bodyFormData = [...body.content, ...this.config.bodyFormData];
          } else if (body.type === 'x-www-form-urlencoded') {
            this.config.bodyWwwForm = [...body.content, ...this.config.bodyWwwForm];
          } else if (body.type === 'raw') {
            this.config.rawType = body.raw_type;
            this.config.bodyValue = body.content;
          }
        }
      } else {
        if (Object.keys(this.configur.api_info).length !== 0) {
          const { body, settings, auth, query_params } = this.configur.api_info.webhook_info;
          this.config.settings.timeout = settings.timeout;
          // query_params auth
          const result = [];
          for (const key in query_params) {
            result.push({
              key,
              value: query_params[key],
              select: true,
            });
          }
          this.config.queryParams = [...result, ...this.config.queryParams];
          this.config.bodyRadio = body.type || 'none';
          if (body.type === 'x-www-form-urlencoded') {
            const list = [];
            body.content.split('&').map(item => {
              const cl = item.split('=');
              list.push({
                key: cl[0],
                value: cl[1],
                select: true,
              });
            });
            this.config.bodyWwwForm = [...list, ...this.config.bodyWwwForm];
          } else if (body.type === 'form-data') {
            // this.config.body =
          } else if (body.type === 'raw') {
            this.config.rawType = body.raw_type;
            this.config.bodyValue = body.content;
          }
          if ('auth_type' in auth) {
            this.config.authRadio = auth.auth_type;
            if (auth.auth_type === 'bearer_token') {
              this.config.auth_config.Token = auth.auth_config.token;
            } else if (auth.auth_type === 'basic_auth') {
              this.config.auth_config.username = auth.auth_config.username;
              this.config.auth_config.password = auth.auth_config.password;
            }
          } else {
            this.config.authRadio = 'none';
          }
        }
      }
    },
    methods: {
      handleSelectContent(item) {
        this.config.bodyValue = `${this.config.bodyValue.slice(0, -(this.filterParams.length + 2))}{{ ${item.key}}}`;
        this.$refs.textarea.focus();
      },
      changeTab(item) {
        this.acticeTab = item.key;
      },
      handleDelete(row) {
        const index = this.list.indexOf(row);
        if (index !== -1) {
          this.list.splice(index, 1);
        }
      },
      changeFormStatus(val) {
        this.$emit('changeFormStatus', val);
      },
      changeInput(val) {
        if (!val.check) {
          val.check = true;
          val.select = true;
          this.list.push({
            check: false,
            key: '',
            value: '',
            desc: '',
            select: false,
          });
        } else {
          const { key, value, desc } = val;
          const checkList = [key, value, desc];
          if (checkList.every(item => item === '')) {
            this.list.pop();
            val.check = false;
            val.select = false;
          }
        }
      },
    },
  };
</script>

<style lang='scss' scoped>
@import '../../../../../scss/mixins/scroller.scss';
.bk-config-tab {
    border-bottom: 1px solid #dde4eb;
    height: 40px;
    margin: 0 10px;
    // background-color: #ffffff;
    li {
        float: left;
        padding: 0 10px;
        line-height: 38px;
        text-align: center;
        color: #63656e;
        cursor: pointer;
        font-size: 12px;

        &:hover {
            color: #3a84ff;
        }
    }
    .bk-check-config {
        border-bottom: 2px solid #3a84ff;
        color: #3a84ff;
    }
}
.param-config {
    // margin-top: 10px;
    padding: 10px;
    position: relative;
    .bk-radio-config {
        width: 500px;
        font-size: 12px;
        color: #63656e;
        .config-option {
            width: 40%;
            margin-right: 20px;
        }
    }
    .select-custom {
        width: 80px;
        margin-left: -30px;
    }
    .setting-option {
        font-size: 14px;
        width: 25%;
        .setting-content {
            display: flex;
        }
    }
    .raw-select {
        position: absolute;
        background-color: #fff;
        border: 1px solid #c4c6cc;
        border-radius: 4px;
        font-size: 12px;
        z-index: 100;
        width: 300px;
        height: 200px;
        padding: 5px;
        overflow: auto;
        @include scroller;
        li {
            height: 30px;
            line-height: 30px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            cursor: pointer;
            color: #75777f;
            &:hover {
                background-color: #e1ecff;
                color: #3a84ff;
            }
            span {
                font-size: 12px;
            }
        }
    }
}
.icon-info-fail {
    font-size: 16px;
    color: #63656e;
}
.bk-form-radio {
    margin-right: 30px;
}
</style>
