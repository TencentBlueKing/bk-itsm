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
  <div class="project-sla-agreement">
    <!-- title -->
    <div class="is-title">
      <p class="bk-come-back" @click="goToServiceList">
        <i class="bk-icon icon-arrows-left"></i>
        <span>{{ serviceData.name || '--' }}</span> > SLA{{ $t(`m['设置']`) }}
      </p>
    </div>
    <!-- content -->
    <div class="sla-agreement-container">
      <div v-bkloading="{ isLoading: serviceLoading }" class="bk-content-group">
        <bk-form
          :label-width="250"
          form-type="vertical"
          class="bk-sla-box"
          ref="dynamicForm">
          <div class="bk-sla-content">
            <span>{{$t(`m.serviceConfig['是否启用']`)}}</span>
            <bk-switcher
              size="small"
              theme="primary"
              v-model="isSlaActive"
              :pre-check="handleUseSlaPreCheck"></bk-switcher>
            {{$t(`m.serviceConfig['可以通过点击添加“+”或点击流程节点添加']`)}}
          </div>
          <div class="bk-sla-content" v-if="isSlaActive">
            <div class="bk-service-agreement">
              <span class="bk-service-label">
                {{$t(`m.serviceConfig['服务协议']`)}}
                <span class="red-star">*</span>
              </span>
              <div class="bk-service-agreement-list">
                <div class="bk-agreement-content"
                  v-for="(agree, index) in serviceData.sla"
                  :key="index">
                  <span class="bk-agreement-color"
                    :style="'background-color: ' + agree.color">
                  </span>
                  <span class="bk-agreement-text" @click="agreementTextClick(agree, 'edit')">
                    {{ getProtocolName(agree.sla_id) || $t(`m.tickets["未设置"]`) }}
                  </span>
                  <span class="bk-icon icon-delete"
                    @click="agreementCloseClick(agree, index)">
                  </span>
                </div>
                <bk-button
                  class="bk-sla-add"
                  size="small"
                  theme="default"
                  icon="plus"
                  @click="agreementTextClick({})">
                </bk-button>
              </div>
            </div>
            <div style="height: 420px;margin-top:10px" v-bkloading="{ isLoading: canvasDataLoading }">
              <second-flow
                v-if="!canvasDataLoading"
                ref="flowInfo"
                :add-list="addList"
                :service-agreement-list="serviceData.sla"
                :line-list="lineList"
                :flow-info="previewInfo"
                @slaIconClick="agreementTextClick"
                @configuNode="configuNode">
              </second-flow>
            </div>
          </div>
        </bk-form>
      </div>
      <div class="bk-priority-btn">
        <bk-button
          theme="primary"
          :title="$t(`m.slaContent['提交']`)"
          class="mr10"
          :loading="submitPending"
          :disabled="serviceLoading"
          @click="submitFn">{{ $t(`m.slaContent['提交']`) }}
        </bk-button>
        <bk-button
          theme="default"
          :title="$t(`m.eventdeploy['取消']`)"
          class="mr10"
          @click="goToServiceList">{{ $t('m.eventdeploy["取消"]') }}
        </bk-button>
      </div>
    </div>
    <bk-sideslider
      :is-show.sync="serviceAgreementIsShow"
      :quick-close="true"
      :before-close="clearLastNode"
      :width="695">
      <div slot="header" class="sideslider-header">
        {{$t(`m.serviceConfig['绑定服务协议']`)}}
        <div @click="viewAgreementIsShow = true" class="view-agreement-text">
          {{$t(`m.serviceConfig['查看协议计时说明']`)}}
        </div>
      </div>
      <div slot="content" class="sideslider-content">
        <bk-form
          :label-width="250"
          form-type="vertical"
          :model="agreementEditData"
          :rules="agreementRules"
          ref="agreementForm">
          <bk-form-item
            style="width: calc(50% - 15px)"
            :label="$t(`m.serviceConfig['开始节点']`)"
            :required="true"
            :property="'start_node_id'">
            <bk-select
              :placeholder="$t(`m.serviceConfig['请选择开始计时节点']`)"
              v-model="agreementEditData.start_node_id"
              searchable
              @change="getPostNodes">
              <bk-option v-for="option in nodeOption"
                :key="option.id"
                :id="option.id"
                :name="option.name">
              </bk-option>
            </bk-select>
          </bk-form-item>
          <span class="bk-line-icon"></span>
          <bk-form-item
            style="width: calc(50% - 15px)"
            :label="$t(`m.serviceConfig['结束节点']`)"
            :required="true"
            :property="'end_node_id'">
            <bk-select
              :placeholder="$t(`m.serviceConfig['请选择结束计时节点']`)"
              v-model="agreementEditData.end_node_id"
              searchable
              :loading="endNodeSelectLoading">
              <bk-option v-for="option in endNodeOption"
                :key="option.id"
                :id="option.id"
                :name="option.name">
              </bk-option>
            </bk-select>
          </bk-form-item>
          <bk-form-item
            :label="$t(`m.serviceConfig['服务协议']`)"
            :required="true"
            :property="'sla_id'">
            <bk-select
              :placeholder="$t(`m.serviceConfig['请选择服务协议']`)"
              v-model="agreementEditData.sla_id"
              searchable>
              <bk-option v-for="option in slaList"
                :key="option.id"
                :id="option.id"
                :name="option.name">
                <span>{{option.name}}</span>
                <i v-bk-tooltips="{ content: '跳转查看协议', placements: ['top'] }"
                  class="bk-icon icon-edit"
                  @click.stop="handleEditAgreement(option)">
                </i>
              </bk-option>
              <div slot="extension" @click="handleCreateAgreement" style="cursor: pointer;">
                <i class="bk-icon icon-plus-circle"></i>{{$t(`m.serviceConfig['跳转新建协议']`)}}
              </div>
            </bk-select>
          </bk-form-item>
          <bk-form-item
            :label="$t(`m.serviceConfig['颜色标志设置']`)">
            <bk-color-picker v-model="agreementEditData.color"></bk-color-picker>
          </bk-form-item>
        </bk-form>
        <div style="margin-top: 20px;">
          <bk-button style="margin-right: 10px;width:86px" theme="primary" @click="handleSetAgreement()">
            确定
          </bk-button>
          <bk-button style="width:86px" theme="default" @click="handleCancelAgreement()">
            取消
          </bk-button>
        </div>
      </div>
    </bk-sideslider>
    <bk-dialog
      v-model="viewAgreementIsShow"
      class="viewAgreeDialog"
      theme="primary"
      width="1220"
      :mask-close="false"
      cancel-text="关闭"
      :title="$t(`m.serviceConfig['协议计时说明']`)">
      <div class="agree-img"></div>
    </bk-dialog>

  </div>
</template>

<script>
  import axios from 'axios';
  import secondFlow from './slaJsflowCanvas/secondFlow.vue';
  import commonMix from '../../commonMix/common.js';
  import { ProcessTools } from '@/utils/process.js';
  import { errorHandler } from '../../../utils/errorHandler';

  export default {
    name: 'ProjectServiceSla',
    components: {
      secondFlow,
    },
    mixins: [commonMix],
    props: {
      modelPriority: {
        type: Array,
        default() {
          return [];
        },
      },
    },
    data() {
      return {
        serviceLoading: true,
        serviceData: {},
        slaListLoading: true,
        slaList: [],
        isSlaActive: false,
        nodeOption: [],
        endNodeOption: [],
        agreementEditData: {},
        isNodeClick: false,
        serviceAgreementIsShow: false,
        viewAgreementIsShow: false,
        endNodeSelectLoading: false,
        addList: [],
        lineList: [],
        canvasDataLoading: false,
        previewInfo: {
          canClick: false,
          narrowSize: 0.9,
        },
        submitPending: false,
        agreementRules: {
          start_node_id: [
            {
              message: '字段必填',
              required: true,
              trigger: 'blur',
              validator: v => !!v,
            },
          ],
          end_node_id: [
            {
              message: '字段必填',
              required: true,
              trigger: 'blur',
              validator: v => !!v,
            },
          ],
          sla_id: [
            {
              message: '字段必填',
              required: true,
              trigger: 'blur',
              validator: v => !!v,
            },
          ],
        },
        agreeType: 'add',
        isStartSla: true,
        processTools: null,
      };
    },
    computed: {
      getTransitionLines() {
        return {
          from_state: this.agreementEditData.start_node_id,
          to_state: this.agreementEditData.end_node_id,
        };
      },
    },
    watch: {
      getTransitionLines(states) {
        if (states.from_state && states.to_state) {
          const params = {
            id: this.serviceData.workflow,
            from_state_id: states.from_state,
            to_state_id: states.to_state,
          };
          this.$store.dispatch('workflowVersion/getTransitionLines', params).then((res) => {
            this.agreementEditData.lines = res.data.lines;
            this.agreementEditData.states = res.data.states;
          })
            .catch((res) => {
              errorHandler(res, this);
            });
        }
      },
    },
    mounted() {
      this.initData();
    },
    methods: {
      // 初始化数据
      async initData() {
        this.getSlaList();
        await this.getServiceDetail();
        this.getWorkflowCanvasData();
      },
      // 获取服务详情
      getServiceDetail() {
        this.serviceLoading = true;
        return this.$store.dispatch('service/getServiceDetail', this.$route.params.id).then((res) => {
          this.serviceData = res.data;
          if (res.data.sla.length > 0) {
            this.isSlaActive = true;
          }
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.serviceLoading = false;
          });
      },
      // 服务级别列表
      getSlaList() {
        this.slaListLoading = true;
        const params = {
          is_enabled: true,
          project_key: this.$store.state.project.id,
        };
        this.$store.dispatch('slaManagement/getProtocolsList', { params }).then((res) => {
          this.slaList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.slaListLoading = false;
          });
      },
      getWorkflowCanvasData() {
        this.canvasDataLoading = true;
        axios.all([
          this.$store.dispatch('deployCommon/getNodeVersion', { id: this.serviceData.workflow }),
          this.$store.dispatch('deployCommon/getLineVersion', { id: this.serviceData.workflow }),
        ]).then(axios.spread((userResp, reposResp) => {
          this.addList = userResp.data;
          for (let i = 0; i < this.addList.length; i++) {
            this.addList[i].indexInfo = i;
          }
          this.$store.commit('cdeploy/getChart', this.addList);

          this.lineList = reposResp.data.items;
          this.nodeOption = userResp.data.filter(node => node.name !== '' && node.type !== 'START' && node.type !== 'END');

          this.processTools = new ProcessTools(this.addList, this.lineList);
        }))
          .finally(() => {
            this.canvasDataLoading = false;
          });
      },
      getPostNodes(startId) {
        const afterNodes = this.processTools.getSlaAfterNodes(startId);
        this.endNodeOption = afterNodes;
      },
      getProtocolName(protocol) {
        const slaname = this.slaList.find(sla => sla.id === protocol);
        if (slaname && slaname.name) {
          return protocol && slaname.name;
        }
      },
      handleSetAgreement() {
        this.$refs.agreementForm.validate().then(() => {
          if (!this.isNodeClick && this.agreeType === 'add') {
            this.serviceData.sla.push(this.agreementEditData);
          }
          this.isNodeClick = false;
          this.serviceAgreementIsShow = false;
        });
      },
      agreementTextClick(agree, type) {
        this.agreeType = type || 'add';
        this.agreementEditData = agree;
        this.serviceAgreementIsShow = true;
        this.endNodeOption = [];
        if (!agree.color) {
          this.$set(this.agreementEditData, 'color', this.getRendomColor());
        }
        if (this.agreementEditData.start_node_id) {
          this.getPostNodes(this.agreementEditData.start_node_id);
        }
        this.isNodeClick = false;
      },
      // 节点校验
      nodeCheck(agree) {
        const isError = agree.start_node_id === agree.end_node_id;
        if (isError) {
          this.$bkMessage({
            message: this.$t('m.serviceConfig[\'添加协议失败，请重新选择正确结束节点！\']'),
            theme: 'error',
            ellipsisLine: 0,
          });
        }
        return isError;
      },
      agreementCloseClick(agree, agreeIndex) {
        this.$bkInfo({
          extCls: 'agreement-close',
          type: 'warning',
          title: this.getProtocolName(agree.sla_id) ? `${this.$t('m.serviceConfig["确认删除服务协议"]')}<${this.getProtocolName(agree.sla_id)}>` : this.$t('m["当前服务协议配置未完成，确认要删除吗？"]'),
          confirmFn: () => {
            const lastIndex = this.serviceData.sla.length - 1;
            if (lastIndex === agreeIndex && !this.serviceData.sla[lastIndex].end_node_id) {
              this.isStartSla = true;
              this.isNodeClick = false;
            }
            this.serviceData.sla.splice(agreeIndex, 1);
          },
        });
      },
      configuNode(value) {
        const { sla } = this.serviceData;
        if (this.isStartSla) {
          sla.push({
            start_node_id: value.id,
            color: this.getRendomColor(),
          });
        } else {
          const len = sla.length - 1;
          const lastSlaItem = sla[len];
          const endOptions = this.processTools.getSlaAfterNodes(lastSlaItem.start_node_id);
          if (!endOptions.find(n => n.id === value.id)) {
            this.$bkMessage({
              message: '该节点不能作为 SLA 结束节点',
              theme: 'error',
              ellipsisLine: 0,
            });
            return false;
          }

          lastSlaItem.end_node_id = value.id;
          this.$set(sla, len, sla[len]);
          if (this.nodeCheck(sla[len])) {
            sla[len].end_node_id = '';
            return;
          }
          this.agreementTextClick(sla[len]);
          this.isNodeClick = true;
        }
        this.isStartSla = !this.isStartSla;
      },
      getRendomColor() {
        let i = 0;
        let colorStr = '#';
        let random = 0;
        const aryNum = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'];
        /* eslint-disable */
                for (i = 0; i < 6; i++) {
                    random = parseInt(Math.random() * 16);
                    colorStr += aryNum[random];
                }
                /* eslint-disable */
                if (colorStr === '#FFFFFF')colorStr = '#87cb12';
                return colorStr;
            },
            // 提交 取消
            submitFn() {
                const {
                    can_ticket_agency, catalog_id, desc, display_type, id, is_valid, key,
                    name, owners, sla, workflow,
                } = this.serviceData;
                const params = {
                    can_ticket_agency,
                    catalog_id,
                    desc,
                    display_type,
                    id,
                    is_valid,
                    key,
                    name,
                    owners,
                    sla,
                    workflow,
                    admin: owners.split(','),
                    project_key: this.$store.state.project.id,
                };
                // SLA开关
                if (this.isSlaActive) {
                    if (!params.sla.length) {
                        this.$bkMessage({
                            message: this.$t('m.deployPage["请添加SLA协议！"]'),
                            theme: 'error',
                        });
                        return;
                    }
                    params.sla = params.sla.map((sla) => {
                        sla.name = this.getProtocolName(sla.sla_id);
                        return sla;
                    });
                } else {
                    params.sla = [];
                }
                // 请求方法
                if (this.submitPending) {
                    return;
                }
                this.submitPending = true;
                this.$store.dispatch('serviceEntry/updateService', params).then(() => {
                    this.$bkMessage({
                        message: this.$t('m.deployPage["保存成功"]'),
                        theme: 'success',
                    });
                    this.goToServiceList();
                })
                    .catch((res) => {
                        errorHandler(res, this);
                    })
                    .finally(() => {
                        this.submitPending = false;
                    });
            },
            goToServiceList() {
                this.$router.push({ name: 'projectServiceList', query: { project_id: this.$route.query.project_id, catalog_id: this.$route.query.catalog_id } });
            },
            // 跳转到新建服务协议
            handleCreateAgreement() {
                const routeData = this.$router.resolve({ path: '/project/sla_agreement', query: { project_id: this.$store.state.project.id } });
                window.open(routeData.href, '_blank');
            },
            handleEditAgreement(option) {
                const routeData = this.$router.resolve({ path: '/project/sla_agreement', query: { project_id: this.$store.state.project.id, item: JSON.stringify(option) } });
                window.open(routeData.href, '_blank');
            },
            // 校验
            async submitInfo() {
                this.$refs.dynamicForm.validate().then(() => {

                }, () => {
                    this.$parent.$refs.agreement.scrollTop = 0;
                });
            },
            handleCancelAgreement() {
                this.serviceAgreementIsShow = false;
                this.clearLastNode();
            },
            clearLastNode() {
                if (this.isNodeClick && this.agreeType === 'add') {
                    this.serviceData.sla.pop();
                }
                return true;
            },
            // 校验流程是否可以启用 sla 协议
            handleUseSlaPreCheck(val) {
                if (!val) {
                    return true;
                }
                if (!this.serviceData.workflow) {
                    this.$bkMessage({
                        message: this.$t('m.serviceConfig[\'请选择流程版本\']'),
                        theme: 'error',
                    });
                    return false;
                }
                const result = new Promise((resolve, reject) => {
                    this.$store.dispatch('sla/checkProcessCanUseSla', this.serviceData.workflow).then((res) => {
                        resolve(res.result);
                    })
                        .catch((err) => {
                            errorHandler(err, this);
                            reject(err);
                        });
                });
                return result;
            },
        },
    };
</script>

<style lang='scss' scoped>
    @import '../../../scss/mixins/clearfix.scss';
    @import '../../../scss/mixins/scroller.scss';

    .project-sla-agreement {
        height: calc(100vh - 52px);
    }
    .bk-loading /deep/.bk-spin-loading {
        width: 16px;
        height: 16px;
    }
    .sla-agreement-container {
        margin: 0 25px;
        padding-top: 82px;
        .bk-content-group {
            margin-bottom: 18px;
            box-shadow: 0px 2px 6px 0px rgba(6, 6, 6, 0.1);
            border-radius: 2px;
            padding: 16px;
            position: relative;
            background: #ffffff;
            .bk-form {
                padding: 0 10px;
            }
            .bk-label {
                font-weight: normal;
            }
        }
        .red-star {
            color: red;
            vertical-align: middle;
            font-size: 12px;
        }
        .bk-form {
            margin: 0 auto;
            display: block;
            width: 87.5%;
            position: relative;
            .bk-group-table {
                width: 100%;
                border: none;
                position: relative;
            }
            .add-and-reduce-box {
                position: absolute;
                right: -20px;
                top: 50%;
                transform: translateY(-50%);
                .bk-itsm-icon {
                    font-size: 18px;
                    color: #C4C6CC;
                }
            }
            .bk-form-control,.bk-select {
                max-width: 540px;
            }
            .bk-form-item {
                display: inline-block;
                width: calc(50% - 34px);
                vertical-align: top;
                margin-top: 20px;
                &:nth-child(2n) {
                    margin-left: 60px;
                }
            }
            .bk-form-item:nth-of-type(-n + 2) {
                margin-top: 0;
            }
        }
        .bk-priority-configur {
            display: inline-block;
            width: 84%;
        }
        .bk-sla-box {
            font-size: 14px;
            color: #63656E;
            .bk-sla-content {
                margin-top: 20px;
                .bk-switcher {
                    margin: 0 18px;
                }
                .palette-panel-wrap {
                    display: none;
                }
                .bk-service-agreement {
                    display: flex;
                    align-items: center;
                }
                .bk-service-label {
                    flex-shrink: 0;
                }
                .bk-service-agreement-list {
                    margin-left: 18px;
                    .bk-agreement-content {
                        display: inline-block;
                        width: 200px;
                        height: 32px;
                        margin-right: 6px;
                        border: 1px solid #c4c6cc;
                        border-radius: 2px;
                        line-height: 32px;
                        position: relative;
                        .bk-agreement-color {
                            position: absolute;
                            left: 6px;
                            top: 50%;
                            transform: translateY(-50%);
                            width: 10px;
                            height: 10px;
                            background-color: #63656E;
                            cursor: initial;
                        }
                        .bk-agreement-text {
                            float: left;
                            margin-left: 26px;
                            width: calc(100% - 50px);
                            overflow: hidden;
                            text-overflow: ellipsis;
                            white-space: nowrap;
                        }
                        .bk-icon:hover {
                            color: #3a84ff;
                        }
                        .bk-icon {
                            line-height: 32px;
                            float: right;
                            font-size: 16px;
                            margin-right: 4px;
                            color: #979BA5;
                        }
                    }
                    .bk-agreement-content:hover {
                        cursor: pointer;
                        border: 1px solid #3a84ff;
                        box-shadow: 0 0 4px rgba(58, 132, 255, 0.4);
                    }
                }
            }
            .bk-sla-content:first-of-type {
                margin-top: 0px;
            }
            .bk-sla-add {
                margin-left: -5px;
                display: inline-block;
                vertical-align: top;
                width: 32px;
                height: 32px;
                line-height: 32px;
                padding: 0px 5px;
            }
        }
    }
    .display-range {
        width: 100%;
        /deep/ {
            .first-level {
                margin-right: 8px;
            }
            .first-level, .second-level {
                width: calc(50% - 4px);
            }
            .bk-form-width {
                width: 100%;
            }
        }
        /deep/ &.no-second {
            .first-level {
                width: 100%;
            }
            .second-level {
                display: none;
            }
            .bk-form-width {
                width: 100%;
            }
        }
    }
    .sideslider-header {
        position: relative;
        .view-agreement-text {
            color: #3a84ff;
            font-size: 12px;
            font-weight: normal;
            float: right;
            margin-right: 20px;
            cursor: pointer;
        }
    }
    .sideslider-content {
        padding: 25px 36px;
        .bk-form-item {
            width: 100%;
            display: inline-block;
        }
        .bk-line-icon {
            display: inline-block;
            width: 10px;
            border-top: 1px solid #979BA5;
            margin-bottom: 10px;
            margin: 14px 4px;
        }
    }
    .icon-edit {
        position: absolute;
        right: 20px;
        top: 50%;
        transform: translateY(-50%);
    }
</style>

<style lang="scss">

.viewAgreeDialog {
    .bk-primary {
        display: none;
    }
    .agree-img {
        height: 433px;
        background: url(../../../images/viewAgreement.png);
    }
}
.bk-itsm-service {
    .sla-agreement-container {
        .bk-form {
            .bk-form-content {
                max-width: 540px;
                width: 100%;
            }
        }
        .bk-form-50 {
            width: 12% !important;
            .bk-form-content {
                max-width: 540px;
                width: 50%;
            }
        }
    }
}

.bk-sla-box {
    .palette-panel-wrap {
        display: none;
    }
    .canvas-flow-wrap {
        background: #F5F7FA;
    }
}

.bk-select-tag-container .bk-select-tag {
    max-width: none;
}
.agreement-close {
    .bk-dialog-content {
        width: auto !important;
    }
}
</style>
