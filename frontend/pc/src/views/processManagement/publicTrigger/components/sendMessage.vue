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
  <div class="bk-send-message">
    <bk-tab :active="activeName" @tab-change="changPanel" v-if="show">
      <bk-tab-panel
        v-for="(panel, index) in itemInfo.sub_components"
        v-bind="panel"
        :key="index"
        :test-posi-id="panel.key">
        <template slot="label">
          <bk-checkbox style="float: left; margin: 0px 8px 0 0;"
            :true-value="trueStatus"
            :false-value="falseStatus"
            v-model="panel.checked">
          </bk-checkbox>
          <i class="bk-icon" :class="[panel.icon]"></i>
          <span class="panel-name">{{panel.label}}</span>
        </template>
        <!-- <div v-for="(subPanel, subIndex) in itemInfo.sub_components"
                    :key="subIndex"
                    v-if="activeName === subPanel.name"> -->
        <div v-for="(field, fieldIndex) in panel.field_schema"
          :key="field.key"
          class="mb20"
          :test-posi-id="field.key">
          <bk-form-item
            :label="field.name"
            :required="field.required"
            :key="index"
            :desc="field.tips">
            <change-conductor
              :index="index"
              :item-info="field"
              :origin="'message'"
              :is-show-var="isShowVar"
              @change-panel-status="changePanelStatus(panel, fieldIndex)">
            </change-conductor>
          </bk-form-item>
        </div>
        <!-- </div> -->
      </bk-tab-panel>
    </bk-tab>
  </div>
</template>
<script>
  import changeConductor from './changeConductor.vue';

  export default {
    name: 'sendMessage',
    components: {
      changeConductor,
    },
    props: {
      itemInfo: {
        type: Object,
        default() {
          return {};
        },
      },
      isShowVar: {
        type: Boolean,
        default: () => true,
      },
    },
    data() {
      return {
        trueStatus: true,
        falseStatus: false,
        activeName: 'send_email_message',
        show: true,
      };
    },
    computed: {
    },
    created() {
      this.itemInfo.sub_components.forEach(item => {
        this.$set(item, 'checked', (item.checked || false));
        if (item.checked) {
          this.activeName = item.name;
        }
        this.$set(item, 'label', item.name);
        this.$set(item, 'icon', '');
        switch (item.key) {
          case 'send_email_message':
            item.icon = 'icon-email';
            break;
          case 'send_sms_message':
            item.icon = 'icon-mobile';
            break;
          case 'send_wechat_message':
            item.icon = 'icon-weixin';
            break;
        }
        // item.name = item.key
      });
    },
    mounted() {
    },
    methods: {
      changPanel(name) {
        this.activeName = name;
      },
      changePanelStatus(panel, pIndex) {
        console.log(panel, pIndex);
        // this.show = false
        // this.$nextTick(() => {
        //     panel.checked = true
        //     this.itemInfo.sub_components.splice(pIndex, 1)
        //     this.show = true
        // })
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../../../scss/mixins/clearfix.scss';

    .bk-send-message {
        /deep/ .bk-tab-label-item{
            min-width: 200px;
            .bk-tab-label {
                padding: 0 5px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
        }
    }
</style>
