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
  <div class="create-ticket-page">
    <nav-title :show-icon="true"
      :title-name="$t(`m.navigation['提单']`)"
      @goBack="onBackIconClick">
    </nav-title>
    <div class="create-ticket-body" v-if="!isRemindPageShow" v-bkloading="{ isLoading: serviceLoading }">
      <!-- 服务信息 -->
      <section class="service-info">
        <div class="service-icon-wrap">
          <span class="service-icon">
            <i class="bk-itsm-icon icon-service"></i>
          </span>
        </div>
        <div class="service-description">
          <h3 class="service-title">
            <span class="service-name">{{ service.name }}</span>
            <i
              :class="['bk-itsm-icon favorite', favorite ? 'icon-favorite' : 'icon-rate']"
              v-bk-tooltips="{
                content: favorite ? $t(`m.common['取消收藏']`) : $t(`m.common['添加收藏']`),
                placement: 'top',
                delay: [300, 0]
              }"
              @click.stop="onCollectClick">
            </i>
            <span class="change-service" @click="onChangeService">{{ $t(`m.common['切换服务']`) }}</span>
          </h3>
          <pre class="service-content">{{ service.desc || $t(`m.common['暂无描述']`) }}</pre>
        </div>
      </section>
      <!-- 提单信息 -->
      <section class="form-panel creaet-fields" v-bkloading="{ isLoading: fieldListLoading }">
        <div class="panel-label">
          <h3 class="panel-label-name">{{ $t(`m.tickets['提单信息']`) }}</h3>
          <div class="select-template" @click="handleTemplateSelect">
            <span>{{ $t(`m['模板选择']`) }}</span>
            <i :class="['bk-itsm-icon', isShowTemplateList ? 'icon-arrow-bottom' : 'icon-arrow-right']"></i>
            <ul v-show="isShowTemplateList && templateList.length !== 0" class="template-list">
              <li v-for="option in templateList"
                :key="option.id"
                @click="handleTemplateChange(option.id)">
                {{ option.name }}
              </li>
            </ul>
          </div>
        </div>
        <div class="panel-content" v-if="!serviceLoading && !fieldListLoading">
          <!-- 添加特定字段，提单人 -->
          <div class="bk-member-form" v-if="service.can_ticket_agency">
            <p class="bk-member-label">{{ $t(`m.common['提单人']`) }}</p>
            <member-select v-model="creator" :multiple="false" style="height: 32px;"></member-select>
          </div>
          <field-info
            ref="fieldInfo"
            :fields="fieldList">
          </field-info>
          <!-- 进度更新提醒 -->
          <div class="ticket-remind">
            <bk-checkbox
              v-model="remindCheck">
              {{ $t('m.common["关注单据，单据进度更新时通知我"]') }}
            </bk-checkbox>
          </div>
        </div>
      </section>
      <!-- 按钮组 -->
      <div class="bottom-group mt20">
        <bk-button :theme="'primary'"
          data-test-id="createTicket-button-submit"
          :title="$t(`m.common['提交']`)"
          :loading="submitting"
          class="mr10"
          @click="onCreateTicket">
          {{$t(`m.common['提交']`)}}
        </bk-button>
        <bk-button :theme="'default'"
          :title="$t(`m['取消']`)"
          :disabled="submitting"
          class="mr10"
          @click="onBackIconClick">
          {{$t(`m['取消']`)}}
        </bk-button>
        <!-- 模板 -->
        <bk-popover
          ref="templatePopover"
          placement="bottom-start"
          trigger="click"
          ext-cls="save-template-pop"
          theme="light">
          <bk-button v-if="tempalteId"
            :theme="'default'"
            :title="$t(`m.common['更新模板']`)"
            :disabled="submitting"
            class="mr10"
            @click.stop="onOpenUpdateTemplate">
            {{$t(`m.common['更新模板']`)}}
          </bk-button>
          <bk-button v-if="tempalteId"
            :theme="'default'"
            :title="$t(`m.common['另存为模板']`)"
            :disabled="submitting"
            class="mr10">
            {{$t(`m.common['另存为模板']`)}}
          </bk-button>
          <bk-button
            v-else
            :theme="'default'"
            :title="$t(`m.common['存为模板']`)"
            :disabled="submitting"
            class="mr10">
            {{$t(`m.common['存为模板']`)}}
          </bk-button>
          <div slot="content" style="width: 320px;">
            <h3 class="save-title">{{$t(`m.common['存为模板']`)}}</h3>
            <bk-form
              width="320"
              form-type="vertical"
              :model="templateFormData"
              :rules="rules"
              ref="templateForm">
              <bk-form-item :label="''" :required="true" :property="'name'">
                <bk-input v-model="templateFormData.name" maxlength="120" :placeholder="$t(`m.common['请输入模板名称']`)"></bk-input>
              </bk-form-item>
            </bk-form>
            <div class="btn-group">
              <span @click="onSaveTemplate">{{$t(`m.systemConfig['确认']`)}}</span>
              <span @click="cancelTemplate">{{$t(`m.systemConfig['取消']`)}}</span>
            </div>
          </div>
        </bk-popover>
      </div>
    </div>
    <create-ticket-dialog :is-show.sync="isCreateTicketDialogShow"></create-ticket-dialog>
    <create-ticket-success
      v-if="isRemindPageShow"
      :router-info="routerInfo"
      @onBackIconClick="onBackIconClick">
    </create-ticket-success>
  </div>
</template>
<script>
  import NavTitle from '@/components/common/layout/NavTitle';
  import apiFieldsWatchMixin from '@/views/commonMix/api_fields_watch.js';
  import FieldInfo from '@/views/managePage/billCom/fieldInfo.vue';
  import CreateTicketDialog from '@/components/common/modal/CreateTicketDialog.vue';
  import commonMix from '@/views/commonMix/common.js';
  import { errorHandler } from '@/utils/errorHandler';
  import { deepClone } from '../../utils/util';
  import memberSelect from '@/views/commonComponent/memberSelect';
  import CreateTicketSuccess from './details/components/createTicketSuccess.vue';

  export default {
    name: 'CreateTicket',
    components: {
      NavTitle,
      FieldInfo,
      memberSelect,
      CreateTicketDialog,
      CreateTicketSuccess,
    },
    mixins: [apiFieldsWatchMixin, commonMix],
    inject: ['reload'],
    data() {
      return {
        submitting: false,
        serviceLoading: false,
        templateListLoading: false,
        fieldListLoading: false,
        serviceId: '',
        creator: [],
        favorite: false,
        service: {},
        tempalteId: '',
        templateInfo: {},
        templateList: [],
        templateFormData: {
          name: '',
        },
        rules: {},
        fieldList: [],
        reCreateFieldList: [],
        remindCheck: false,
        isCreateTicketDialogShow: false,
        // 落地页
        isRemindPageShow: false,
        routerInfo: {},
        isShowTemplateList: false,
      };
    },
    watch: {
      '$route'() {
        this.reload();
      },
    },
    created() {
      this.initData();
    },
    methods: {
      async initData() {
        // 校验规则
        this.rules.name = this.checkCommonRules('name').name;
        this.serviceId = this.$route.query.service_id;

        this.getTemplateList();
        await this.getServiceDetail();
        await this.getFieldList();
        // 重新提单
        if (this.$route.query.rc_ticket_id) {
          this.getReCreateTicketInfo();
        }
      },
      // 展示模板选择
      handleTemplateSelect() {
        if (this.templateList.length === 0) {
          this.$bkMessage({
            message: this.$t('m[\'暂无模板\']'),
            offsetY: 80,
          });
          return;
        }
        this.isShowTemplateList = !this.isShowTemplateList;
      },
      // 获取服务详情
      getServiceDetail() {
        this.serviceLoading = true;
        return this.$store.dispatch('service/getServiceDetail', this.serviceId).then((res) => {
          this.service = res.data;
          this.favorite = res.data.favorite;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.serviceLoading = false;
          });
      },
      // 获取提单模板列表
      getTemplateList() {
        this.templateListLoading = true;
        const params = {
          service: this.serviceId,
        };
        return this.$store.dispatch('change/getTemplateList', params).then((res) => {
          this.templateList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.templateListLoading = false;
          });
      },
      // 获取提单字段
      getFieldList() {
        this.fieldListLoading = true;
        const params = {
          service_id: this.serviceId,
        };
        return this.$store.dispatch('change/getSubmitFields', params).then(async (res) => {
          this.fieldList = res.data;
          const priorityReadonly = this.fieldList.some(item => item.key === 'impact' || item.key === 'urgency');
          this.fieldList.forEach((item) => {
            if (item.type === 'CASCADE') {
              item.type = 'SELECT';
            }
            if (item.key === 'priority' && !priorityReadonly) {
              this.$set(item, 'is_readonly', false);
            }
            this.$set(item, 'showFeild', true);
            this.$set(item, 'val', item.value);
            this.$set(item, 'service', this.service.key);
          });
          this.isNecessaryToWatch({ fields: this.fieldList }, 'submit', () => {
            // TO IMPROVE 加载完成、重新赋值， isNecessaryToWatch 会去异步加载 choice 数据
            this.fieldList.forEach((item) => {
              this.reCreateFieldList.forEach((node) => {
                if (item.key === node.key) {
                  item.val = node.value;
                }
              });
            });
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.fieldListLoading = false;
          });
      },
      // 获取重新提单单据参数信息
      getReCreateTicketInfo() {
        const id = this.$route.query.rc_ticket_id;
        this.fieldListLoading = true;
        return this.$store.dispatch('change/getCreateTicektParams', { id }).then((res) => {
          if (res.result && res.data.fields && res.data.fields.length) {
            this.reCreateFieldList = res.data.fields;
            this.fieldList.forEach((item) => {
              res.data.fields.forEach((node) => {
                if (item.key === node.key) {
                  item.val = node.value;
                }
              });
            });
          }
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.fieldListLoading = false;
          });
      },
      // 创建单据
      onCreateTicket() {
        if (this.submitting) {
          return;
        }
        // 将字段中的时间转换一遍
        this.$refs.fieldInfo.fieldChange();
        // 字段值校验
        if (!this.$refs.fieldInfo.checkValue()) {
          this.$nextTick(() => {
            const errEl = document.querySelector('.bk-task-error');
            document.querySelector('.create-ticket-body').scrollTop = errEl ? errEl.getBoundingClientRect().y + 200 : 0;
          });
          return false;
        }

        this.submitting = true;
        const params = {
          catalog_id: this.service.catalog_id,
          service_id: this.service.id,
          service_type: this.service.bounded_catalogs[0],
          fields: [],
          creator: this.creator[0] || window.username,
          attention: this.remindCheck,
        };
        this.fieldList.forEach((item) => {
          // 提单环节需要传入隐藏字段，处理节点不需要
          params.fields.push({
            type: item.type,
            id: item.id,
            key: item.key,
            value: item.showFeild ? item.value : '',
            choice: item.choice,
          });
        });
        this.$store.dispatch('change/submit', params).then((res) => {
          this.$bkMessage({
            message: this.$t('m.common["提交成功！"]'),
            theme: 'success',
          });
          this.isRemindPageShow = true;
          this.routerInfo = {
            name: 'TicketDetail',
            params: {
              type: 'readOnly',
            },
            query: {
              id: res.data.id, from: 'created', project_id: this.$route.query.project_id || undefined,
            },
          };
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.submitting = false;
          });
      },
      // 修改服务
      onChangeService() {
        this.isCreateTicketDialogShow = true;
      },
      getSaveTemplateParams() {
        const params = {
          name: this.templateFormData.name,
          service: this.serviceId,
          template: [],
        };
        // 不能保存的字段类型
        const excludeTypes = ['FILE', 'TABLE', 'CUSTOMTABLE'];
        this.fieldList.forEach((item) => {
          if (item.val !== '' && !excludeTypes.includes(item.type)) {
            const templateItem = {
              id: item.id,
              key: item.key,
              type: item.type,
              value: item.val,
            };
            if (templateItem.type === 'DATE') {
              templateItem.value = this.standardDayTime(templateItem.value);
            }
            if (templateItem.type === 'DATETIME') {
              templateItem.value = this.standardTime(templateItem.value);
            }
            params.template.push(templateItem);
          }
        });

        return params;
      },
      // 更新模板
      onOpenUpdateTemplate() {
        const params = deepClone(this.getSaveTemplateParams());
        if (!params.template.length) {
          this.$bkMessage({
            message: this.$t('m.common["无字段可以保存"]'),
            theme: 'warning',
          });
          this.cancelTemplate();
          return false;
        }
        if (this.submitting) {
          return false;
        }
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.common["确认更新模板？"]'),
          subTitle: this.$t('m.common["更新模板操作将会覆盖原先模板的信息"]'),
          confirmFn: () => {
            this.submitting = true;
            const id = this.tempalteId;
            const { name } = this.templateList.find(template => template.id === this.tempalteId);
            params.name = name;

            this.$store.dispatch('change/updateTemplate', { params, id }).then(() => {
              this.$bkMessage({
                message: this.$t('m.common["模板更新成功"]'),
                theme: 'success',
                ellipsisLine: 0,
              });
            })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.getTemplateList();
                this.submitting = false;
              });
          },
        });
      },
      // 保存模板
      onSaveTemplate() {
        const params = this.getSaveTemplateParams();
        if (!params.template.length) {
          this.$bkMessage({
            message: this.$t('m.common["无字段可以保存"]'),
            theme: 'warning',
          });
          this.cancelTemplate();
          return false;
        }
        if (this.submitting) {
          return false;
        }
        this.$refs.templateForm.validate().then(() => {
          this.submitting = true;
          this.$store.dispatch('change/submitTemplate', params).then(() => {
            this.getTemplateList();
            this.$bkMessage({
              message: this.$t('m.common["保存成功"]'),
              theme: 'success',
            });
          })
            .catch((res) => {
              errorHandler(res, this);
            })
            .finally(() => {
              this.submitting = false;
              this.cancelTemplate();
            });
        });
      },
      // 取消模板
      cancelTemplate() {
        this.templateFormData.name = '';
        this.$refs.templatePopover.hideHandler();
      },
      // 选择模板
      handleTemplateChange(id) {
        this.tempalteId = id;
        const template = this.templateList.find(template => template.id === id).template || [];
        this.fieldList.forEach((item) => {
          template.forEach((node) => {
            if (item.key === node.key) {
              item.val = node.value;
            }
          });
        });
      },
      onBackIconClick() {
        let route;
        if (this.$route.query.from) {
          route = {
            name: this.$route.query.from,
          };
        } else {
          route = {
            name: 'projectTicket',
            query: {
              project_id: this.$store.state.project.id,
            },
          };
        }
        this.$router.push(route);
      },
      onCollectClick() {
        this.$store.dispatch('service/toggleServiceFavorite', {
          id: this.serviceId,
          favorite: !this.favorite,
        }).then((res) => {
          if (res.result) {
            this.favorite = !this.favorite; // 修改当前数据的收藏状态
          }
          this.$bkMessage({
            message: this.favorite ? this.$t('m.manageCommon[\'收藏成功\']') : this.$t('m.manageCommon[\'取消成功\']'),
            theme: 'success',
            ellipsisLine: 0,
          });
        })
          .catch((res) => {
            errorHandler(res, this);
          });
      },
    },
  };
</script>
<style lang="scss" scoped>
@import '../../scss/mixins/scroller.scss';
.create-ticket-body {
    margin: 2px 0;
    padding: 20px;
    height: calc(100vh - 104px);
    overflow: auto;
    @include scroller;
}
.service-info {
    width: 62.5%;
    margin: 0 auto;
    display: flex;
    align-items: center;
    padding: 20px 100px 20px 20px;
    background: #ffffff;
    border-radius: 2px;
    box-shadow: 0px 2px 6px 0px rgba(6,6,6,0.1);
    .service-icon-wrap {
        width: 80px;
        .service-icon {
            display: block;
            width: 56px;
            height: 56px;
            line-height: 56px;
            text-align: center;
            font-size: 24px;
            color: #3a84ff;
            background: #e1ecff;
            border-radius: 28px;
        }
    }
    .service-description {
        flex: 1;
        .service-title {
            margin: 0;
            line-height: 16px;
            .service-name {
                font-size: 16px;
                color: #313238;
                line-height: 21px;
            }
            .change-service {
                display: inline-block;
                vertical-align: 1px;
                margin-left: 16px;
                font-size: 12px;
                font-weight: 500;
                color: #3a84ff;
                cursor: pointer;
            }
        }
        .service-content {
            margin-top: 7px;
            font-size: 12px;
            color: #63656e;
            line-height: 20px;
            width: 100%;
            word-break: break-all;
            white-space: normal;
        }
        .favorite {
            display: inline-block;
            vertical-align: 1px;
            margin-left: 7px;
            font-size: 16px;
            cursor: pointer;
        }
        .icon-favorite {
            color: #ffb848;
        }
        .icon-rate {
            color: #979ba5;
        }
    }
}

.fields-params-tempalte {
    height: 84px;
}
.form-panel {
    width: 62.5%;
    // margin-top: 20px;
    margin: 20px auto;
    padding: 20px 100px;
    display: flex;
    flex-direction: column;
    // align-items: center;
    background: #ffffff;
    box-shadow: 0px 2px 6px 0px rgba(6,6,6,0.1);
    border-radius: 2px;
    .panel-label {
        width: 100%;
        height: 50px;
        display: flex;
        justify-content: space-between;
        // flex-shrink: 0;
        // align-self: start;
        .panel-label-name {
            margin: 0;
            line-height: 19px;
            font-size: 14px;
            color: #63656e;
        }
        .select-template {
            height: 22px;
            width: 82px;
            font-size: 14px;
            line-height: 22px;
            color: #979ba5;
            position: relative;
            cursor: pointer;
            i {
                margin-left: 2px;
            }
            .template-list {
                z-index: 10;
                width: 170px;
                max-height: 208px;
                border: 1px solid #dcdee5;
                border-radius: 2px;
                background: #ffffff;
                box-shadow: 0px 2px 6px 0px rgba(0,0,0,0.10);
                position: absolute;
                top: 22px;
                right: 0;
                padding: 8px 0;
                overflow-y: auto;
                @include scroller;
                li {
                    height: 32px;
                    padding: 0 8px;
                    line-height: 32px;
                    font-size: 12px;
                    color: #63656e;
                    &:hover {
                        color: #3a84ff;
                        background: rgba(225,236,255,0.60);
                    }
                }
            }
        }
    }
    .panel-content {
        width: 80%;
        .template-select {
            width: 50%;
        }
        .ticket-remind {
            margin-top: 22px;
            font-size: 14px;
            color: #63656e;
        }
    }
}
.bottom-group {
    width: 62.5%;
    margin: 0 auto;
}
.save-template-pop {
    padding: 10px;
    .save-title {
        font-size: 14px;
        color: #63656e;
    }
    .btn-group {
        margin-top: 10px;
        text-align: right;
        span {
            margin-right: 10px;
            color: #3a84ff;
            cursor: pointer;
        }
    }
}
.bk-member-form {
    margin-bottom: 8px;
    padding-right: 10px;
    .bk-member-label {
        line-height: 30px;
        color: #666;
        font-size: 14px;
    }
}
.remind-page {
    width: 500px;
    height: 300px;
    margin: 0 auto;
    border: 1px solid red;
}
</style>
