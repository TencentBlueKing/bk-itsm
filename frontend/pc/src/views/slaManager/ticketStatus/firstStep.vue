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
  <div class="bk-design-first" v-bkloading="{ isLoading: isDataLoading }">
    <div class="bk-only-btn">
      <div class="bk-more-search">
        <bk-button
          :theme="'primary'"
          :title="$t(`m.deployPage['新增']`)"
          icon="plus"
          class="mr10 plus-cus"
          @click="statusDialog('add')">
          {{ $t('m.deployPage["新增"]') }}
        </bk-button>
      </div>
    </div>
    <bk-table :data="statusTable" :size="'small'" v-bkloading="{ isLoading: isDataLoading }">
      <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.slaContent['状态名']`)" :min-width="150">
        <template slot-scope="props">
          <span class="bk-lable-primary" @click="statusDialog('edit', props.row, props.$index)">
            {{ props.row.name }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :show-overflow-tooltip="true" :label="$t(`m.slaContent['状态说明']`)" width="200">
        <template slot-scope="props">
          {{ props.row.desc || "--" }}
        </template>
      </bk-table-column>
      <bk-table-column :render-header="$renderHeader" :label="$t(`m.slaContent['起始状态']`)" :show-overflow-tooltip="true">
        <template slot-scope="props">
          <template v-if="props.row.flow_status === 'RUNNING' && !props.row.is_over">
            <bk-radio v-model="props.row.is_start" @change="selectOrigin(props.row)"> </bk-radio>
          </template>
          <template v-if="props.row.flow_status !== 'RUNNING' || props.row.is_over">
            <bk-radio
              :disabled="trueStatus"
              v-bk-tooltips.top="
                props.row.is_over
                  ? $t(`m.slaContent['起始状态与结束状态互斥']`)
                  : $t(`m.slaContent['非流转类型的状态不可编辑起始状态']`)
              "
              v-model="props.row.is_start">
            </bk-radio>
          </template>
        </template>
      </bk-table-column>
      <bk-table-column :render-header="$renderHeader" :label="$t(`m.slaContent['结束状态']`)">
        <template slot-scope="props">
          <template v-if="props.row.flow_status === 'RUNNING' && !props.row.is_start">
            <bk-checkbox
              class="bk-outline-none"
              v-model="props.row.is_over"
              :true-value="trueStatus"
              :false-value="falseStatus">
            </bk-checkbox>
          </template>
          <template v-if="props.row.flow_status !== 'RUNNING' || props.row.is_start">
            <bk-checkbox
              class="bk-outline-none"
              :true-value="trueStatus"
              :false-value="falseStatus"
              :disabled="trueStatus"
              v-bk-tooltips.top="
                props.row.is_start
                  ? $t(`m.slaContent['起始状态与结束状态互斥']`)
                  : $t(`m.slaContent['非流转类型的状态不可编辑起始状态']`)
              "
              v-model="props.row.is_over">
            </bk-checkbox>
          </template>
        </template>
      </bk-table-column>
      <bk-table-column :render-header="$renderHeader" :label="$t(`m.slaContent['状态颜色']`)">
        <template slot-scope="props">
          <span
            class="status-color"
            :title="props.row.color_hex"
            :style="{ color: props.row.color_hex, 'border-color': props.row.color_hex }">
            {{ localeCookie ? props.row.name : props.row.flow_status }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.treeinfo['操作']`)" width="150">
        <template slot-scope="props">
          <bk-button theme="primary" text @click="statusDialog('edit', props.row, props.$index)">
            {{ $t('m.slaContent["编辑"]') }}
          </bk-button>
          <template v-if="props.row.is_builtin">
            <span class="bk-label-disabled" v-bk-tooltips.top="$t(`m.slaContent['内置状态不可删除']`)">
              {{ $t('m.slaContent["删除"]') }}
            </span>
          </template>
          <template v-else>
            <bk-button theme="primary" text @click="deleteDialog(props.row)">
              {{ $t('m.slaContent["删除"]') }}
            </bk-button>
          </template>
        </template>
      </bk-table-column>
      <div class="empty" slot="empty">
        <empty :is-error="listError" @onRefresh="getTypeStatusList()"> </empty>
      </div>
    </bk-table>
    <div class="mt20">
      <bk-button
        theme="default"
        class="mr10"
        :title="$t(`m.deployPage['取消']`)"
        :disabled="secondClick"
        @click="backButton">
        {{ $t('m.deployPage["取消"]') }}
      </bk-button>
      <bk-button theme="primary" :title="$t(`m.deployPage['保存并下一步']`)" :loading="secondClick" @click="stepNext">
        {{ $t(`m.deployPage['保存并下一步']`) }}
      </bk-button>
    </div>
    <bk-dialog
      v-model="addStatusDialog.isShow"
      :render-directive="'if'"
      :width="addStatusDialog.width"
      :header-position="addStatusDialog.headerPosition"
      :loading="secondClick"
      :auto-close="addStatusDialog.autoClose"
      :mask-close="addStatusDialog.autoClose"
      :title="addStatusDialog.title"
      @confirm="confirmFn"
      @cancel="cancelFn">
      <bk-form :label-width="200" form-type="vertical" :model="addTemp" :rules="rules" ref="addStatus">
        <bk-form-item :label="$t(`m.slaContent['状态名称']`)" :required="true" :property="'name'">
          <bk-input maxlength="120" :placeholder="$t(`m.slaContent['状态名称']`)" v-model="addTemp.name"> </bk-input>
        </bk-form-item>
        <bk-form-item
          :desc="colorTips"
          :label="$t(`m.slaContent['状态颜色']`)"
          :property="'color_hex'"
          :required="true">
          <div v-bk-clickoutside="closePickers" @click="showPickers">
            <bk-input :placeholder="$t(`m.slaContent['请选择颜色']`)" v-model="addTemp.color_hex">
              <template slot="prepend">
                <div class="color-pick-color" :style="{ backgroundColor: addTemp.color_hex || '#3A84FF' }"></div>
              </template>
            </bk-input>
            <transition>
              <div class="sla-colors-div" v-if="showColorPicker">
                <span
                  class="sla-colors-span"
                  v-for="color in statusColors"
                  :title="color.name"
                  :style="{ backgroundColor: color.color }"
                  @click="changeColor(color)">
                </span>
              </div>
            </transition>
          </div>
        </bk-form-item>
        <bk-form-item :label="$t(`m.slaContent['状态说明']`)">
          <bk-input
            :placeholder="$t(`m.slaContent['请输入状态说明']`)"
            :type="'textarea'"
            :rows="3"
            :maxlength="100"
            v-model="addTemp.desc">
          </bk-input>
        </bk-form-item>
      </bk-form>
    </bk-dialog>
  </div>
</template>

<script>
import { errorHandler } from "../../../utils/errorHandler.js";
import commonMix from "../../commonMix/common.js";
import cookie from "cookie";
import Empty from "../../../components/common/Empty.vue";

export default {
  name: "firstStep",
  mixins: [commonMix],
  components: {
    Empty,
  },
  props: {
    statusType: {
      type: String,
      default: "",
    },
  },
  data() {
    return {
      listError: false,
      trueStatus: true,
      falseStatus: false,
      secondClick: false,
      isDataLoading: false,
      statusTable: [],
      addStatusDialog: {
        isAdd: true,
        isShow: false,
        title: "",
        width: 700,
        headerPosition: "left",
        autoClose: false,
        precision: 0,
      },
      addTemp: {
        name: "",
        desc: "",
        color_hex: "#3A84FF",
      },
      isEdit: {
        flag: false,
        index: null,
        id: null,
      },
      statusColors: [
        {
          name: "ITSM blue",
          color: "#3A84FF",
        },
        {
          name: "UA blue",
          color: "#0033CC",
        },
        {
          name: "Moderate blue",
          color: "#428BCA",
        },
        {
          name: "lime green",
          color: "#44AD8E",
        },
        {
          name: "feijoa",
          color: "#A8D695",
        },
        {
          name: "Slightly desaturate green",
          color: "#5CB85C",
        },
        {
          name: "bright green",
          color: "#69D100",
        },
        {
          name: "Very dark lime green",
          color: "#004E00",
        },
        {
          name: "Very dark desaturate blue",
          color: "#34495E",
        },
        {
          name: "Slightly cyan",
          color: "#A4AAB3",
        },
        {
          name: "Dark grayish cyan",
          color: "#7F8C8D",
        },
        {
          name: "Slight desaturate blue",
          color: "#A295D6",
        },
        {
          name: "Dark moderate blue",
          color: "#5843AD",
        },
        {
          name: "Dark moderate violet",
          color: "#8E44AD",
        },
        {
          name: "Very pale orange",
          color: "#FFECDB",
        },
        {
          name: "Dark moderate pink",
          color: "#AD4363",
        },
        {
          name: "Strong pink",
          color: "#D10069",
        },
        {
          name: "Strong red",
          color: "#CC0033",
        },
        {
          name: "Light red",
          color: "#FF5656",
        },
        {
          name: "Pure red",
          color: "#FF0000",
        },
        {
          name: "Soft red",
          color: "#D9534F",
        },
        {
          name: "Strong yellow",
          color: "#D1D100",
        },
        {
          name: "Soft orange",
          color: "#F0AD4E",
        },
        {
          name: "Dark moderate orange",
          color: "#AD8D43",
        },
      ],
      colorTips: {
        width: 130,
        content: this.$t(
          'm.slaContent["选择颜色后，当单据流转到该状态时，单据状态栏信息会更新为对应颜色。多个状态的颜色可以重复。"]'
        ),
        placement: "top",
      },
      showColorPicker: false,
      rules: {},
      localeCookie: false,
    };
  },
  async mounted() {
    await this.getTypeStatus();
    this.rules.name = this.checkCommonRules("name").name;
    this.rules.desc = this.checkCommonRules("select").select;
    this.rules.color_hex = this.checkCommonRules("color").color;
    this.localeCookie = cookie.parse(document.cookie).blueking_language === "zh-cn";
  },
  methods: {
    // setting status color
    changeColor(item) {
      this.addTemp.color_hex = item.color;
    },
    // show colors
    showPickers() {
      this.showColorPicker = true;
    },
    closePickers() {
      this.showColorPicker = false;
    },
    selectOrigin(item) {
      this.statusTable.forEach((item) => {
        item.is_start = false;
      });
      item.is_start = !item.is_start;
    },
    selectFinish(item) {
      item.is_over = !item.is_over;
    },
    initAddTemp() {
      this.addTemp = {
        name: "",
        desc: "",
        color_hex: "#3A84FF",
      };
    },
    statusDialog(type, item, index) {
      if (this.secondClick) {
        return;
      }
      this.secondClick = true;
      if (type === "add") {
        this.addStatusDialog.title = this.$t('m.slaContent["新增状态"]');
        this.addStatusDialog.isShow = true;
        this.addTemp.color_hex = "#3A84FF";
      } else {
        this.addStatusDialog.title = this.$t('m.slaContent["编辑状态"]');
        this.isEdit.flag = true;
        this.isEdit.index = index;
        this.isEdit.id = item.id;
        this.addTemp = JSON.parse(JSON.stringify(item));
        this.addStatusDialog.isShow = true;
      }
      this.secondClick = false;
    },
    // 添加状态弹窗事件
    cancelFn() {
      this.showColorPicker = false;
      this.isEdit.flag = false;
      this.initAddTemp();
      this.addStatusDialog.isShow = false;
    },
    confirmFn() {
      this.$refs.addStatus.validate().then(
        (validator) => {
          this.secondClick = true;
          const params = {
            name: this.addTemp.name,
            desc: this.addTemp.desc,
            color_hex: this.addTemp.color_hex,
          };
          let temp = {};
          if (!this.isEdit.flag) {
            params.service_type = this.statusType;
            this.$store
              .dispatch("ticketStatus/addTypeState", params)
              .then((res) => {
                temp = res.data;
                this.$bkMessage({
                  message: this.$t('m.serviceConfig["添加成功"]'),
                  theme: "success",
                });
              })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.statusTable.push(temp);
                this.secondClick = false;
                this.showColorPicker = false;
                this.initAddTemp();
                this.isEdit.flag = false;
                this.addStatusDialog.isShow = false;
                this.getTypeStatus();
              });
          } else {
            const id = this.isEdit.id;
            this.$store
              .dispatch("ticketStatus/editTypeState", { params, id })
              .then((res) => {
                temp = res.data;
                this.$bkMessage({
                  message: "编辑成功",
                  theme: "success",
                });
              })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.statusTable[this.isEdit.index].name = temp.name;
                this.statusTable[this.isEdit.index].desc = temp.desc;
                this.statusTable[this.isEdit.index].color_hex = temp.color_hex;
                this.secondClick = false;
                this.showColorPicker = false;
                this.initAddTemp();
                this.isEdit.flag = false;
                this.addStatusDialog.isShow = false;
                this.getTypeStatus();
              });
          }
        },
        (validator) => {
          console.warn(validator);
        }
      );
    },
    // 删除状态
    deleteDialog(item) {
      this.$bkInfo({
        type: "warning",
        title: this.$t(`m.slaContent["确认删除？"]`),
        confirmFn: () => {
          const id = item.id;
          if (this.secondClick) {
            return;
          }
          this.secondClick = true;
          this.$store
            .dispatch("ticketStatus/deleteTypeState", id)
            .then((res) => {
              this.$bkMessage({
                message: this.$t(`m.systemConfig["删除成功"]`),
                theme: "success",
              });
              this.getTypeStatus();
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
    // 返回
    backButton() {
      this.$parent.backTab();
    },
    // 下一步
    async stepNext() {
      if (this.secondClick) {
        return;
      }
      this.secondClick = true;
      const params = {
        service_type: this.statusType,
        ticket_status_ids: [],
        start_status_id: null,
        over_status_ids: [],
      };
      this.statusTable.forEach((item) => {
        params.ticket_status_ids.push(item.id);
        if (item.is_start) {
          params.start_status_id = item.id;
        }
        if (item.is_over) {
          params.over_status_ids.push(item.id);
        }
      });
      await this.$store
        .dispatch("ticketStatus/saveTypeState", params)
        .then((res) => {
          this.$bkMessage({
            message: this.$t('m.newCommon["保存成功"]'),
            theme: "success",
          });
        })
        .catch((res) => {
          errorHandler(res, this);
        })
        .finally(() => {
          this.secondClick = false;
          this.getTypeStatus();
        });
      this.$parent.changeTree(0, "next");
    },
    async getTypeStatus() {
      this.isDataLoading = true;
      this.listError = false;
      const params = {
        // flow_status: 'RUNNING'
      };
      await this.$store
        .dispatch("ticketStatus/getTypeStatus", {
          type: this.statusType,
          params,
        })
        .then((res) => {
          this.statusTable = res.data;
        })
        .catch((res) => {
          this.listError = true;
          errorHandler(res, this);
        })
        .finally(() => {
          this.isDataLoading = false;
        });
    },
  },
};
</script>

<style scoped lang="scss">
.status-color {
  width: 90px;
  padding: 2px 10px;
  display: inline-block;
  text-align: center;
  line-height: 18px;
  border-radius: 2px;
  border: 1px solid;
  border-radius: 2px;
  background-color: #fff;
  color: rgba(255, 255, 255, 1);
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
}

.color-pick-color {
  height: 30px;
  width: 50px;
  display: inline-block;
  border: 1px solid #c3cdd7;
  border-right: none;
}

.sla-colors-div {
  overflow: hidden;
  margin-top: 20px;

  .sla-colors-span {
    display: inline-block;
    border-radius: 5px;
    width: 30px;
    height: 30px;
    margin-right: 10px;
    cursor: pointer;
  }
}

.v-enter,
.v-leave-to {
  height: 0;
}

.v-enter-to,
.v-leave {
  height: 70px;
}

.v-enter-active,
.v-leave-active {
  transition: all 0.3s ease;
}
</style>
