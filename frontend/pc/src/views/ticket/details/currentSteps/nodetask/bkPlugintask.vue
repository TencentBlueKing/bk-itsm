<template>
  <div>
    <bk-form ref="form" :label-width="200" :model="formData" form-type="vertical" :rules="rules">
      <bk-form-item :label="item.name" v-for="item in constantList" :key="item.key" :required="true" :property="item.key">
        <bk-input v-model="formData[item.key]" :disabled="disable"></bk-input>
      </bk-form-item>
    </bk-form>
    <div class="submit-btn" v-if="nodeInfo.status === 'FAILED'">
      <bk-button v-if="changeBtn" :theme="'primary'" @click="submit">{{ $t(`m["提交"]`) }}</bk-button>
      <bk-button :theme="'primary'" @click="reSetSopTask">{{ changeBtn ? $t(`m["返回"]`) : $t(`m["重做"]`) }}</bk-button>
      <bk-button @click="ignore">{{ $t(`m["忽略"]`) }}</bk-button>
    </div>
  </div>
</template>

<script>
  import i18n from '@/i18n/index.js';
  export default {
    name: 'bkPluginTask',
    components: {
    },
    props: {
      ticketInfo: Object,
      nodeInfo: Object,
      workflow: [Number, String],
    },
    data() {
      return {
        isStatic: false,
        changeBtn: false,
        formData: {},
        rules: {},
        constantList: [],
        isHook: false,
        isEdit: false,
        stateList: [],
        disable: true,
        errorTip: false,
      };
    },
    watch: {
    },
    mounted() {
      this.init();
      this.getRelatedFields();
    },
    methods: {
      init() {
        if ('inputs' in this.nodeInfo.contexts.build_params) {
          const params = {
            plugin_code: this.nodeInfo.contexts.build_params.plugin_code,
            plugin_version: this.nodeInfo.contexts.build_params.version,
          };
          this.$store.dispatch('bkPlugin/getPluginDetail', params).then((res) => {
            this.constantList = Object.keys(this.nodeInfo.contexts.build_params.inputs).map(item => {
              this.$set(this.formData, item, this.nodeInfo.contexts.build_params.inputs[item]);
              this.$set(this.rules, item, [{
                required: true,
                message: i18n.t('m.treeinfo["字段必填"]'),
                trigger: 'blur',
              }]);
              return {
                name: res.data.inputs.properties[item].title,
                key: item,
              };
            });
          });
        }
      },
      async getRelatedFields() {
        const params = {
          workflow: this.workflow,
          state: this.nodeInfo.state_id,
          field: '',
        };
        await this.$store.dispatch('apiRemote/get_related_fields', params).then(res => {
          this.stateList = res.data;
        })
          .catch(res => {
            console.log(res);
          })
          .finally(() => {
          });
      },
      reSetSopTask() {
        this.changeBtn = !this.changeBtn;
        this.disable = !this.changeBtn;
        this.isEdit = !this.isEdit;
      },
      onChangeHook(key, value) {
        this.$emit('onChangeHook', key, value);
      },
      ignore() {
        const params = {
          inputs: {},
          is_direct: true,
          state_id: this.nodeInfo.state_id,
        };
        this.$store.dispatch('deployOrder/ignoreNode', { params, ticketId: this.nodeInfo.ticket_id }).then(() => {
          this.$bkMessage({
            message: this.$t('m["忽略完成"]'),
            theme: 'success',
          });
          this.$emit('reloadTicket');
        });
      },
      retry(params) {
        this.$store.dispatch('deployOrder/retryNode', { params, ticketId: this.nodeInfo.ticket_id }).then(() => {
          this.$bkMessage({
            message: this.$t('m.newCommon["提交成功"]'),
            theme: 'success',
          });
          this.changeBtn = false;
          this.$emit('reloadTicket');
        });
      },
      submit() {
        this.$refs.form.validate().then(() => {
          const params = {
            inputs: {
              inputs: {},
              context: {},
              plugin_code: this.nodeInfo.contexts.build_params.plugin_code,
              version: this.nodeInfo.contexts.build_params.version,
            },
            state_id: this.nodeInfo.state_id,
          };
          Object.keys(this.formData).map(item => {
            params.inputs.inputs[item] = this.formData[item];
          });
          this.retry(params);
        });
      },
    },
  };
</script>

<style lang="scss" scoped>
    .sops-form {
        width: 100%;
        min-height: 100px;
    }
    .submit-btn {
        margin-top: 60px;
    }
    .bk-basic-node {
        padding: 0;
        /deep/ .common-section-card-block {
            display: block;
        }
        /deep/ .common-section-card-body {
            padding: 0;
        }
    }
</style>
