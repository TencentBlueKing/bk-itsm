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
  <div class="bk-itsm-service" v-bkloading="{ isLoading: isDataLoading }">
    <template v-if="!changeInfo.isShow">
      <!-- title -->
      <div class="is-title" :class="{ 'bk-title-left': !sliderStatus }">
        <p class="bk-come-back">
          {{ $t('m.slaContent["服务模式"]') }}
        </p>
      </div>
      <div class="itsm-page-content">
        <empty-tip
          v-if="!isDataLoading && modelList.length === 0"
          :title="emptyTip.title"
          :sub-title="emptyTip.subTitle"
          :desc="emptyTip.desc"
          :links="emptyTip.links">
          <template slot="btns">
            <bk-button
              data-test-id="slaPattern_button_createPermission"
              v-cursor="{ active: !hasPermission(['sla_calendar_create'], $store.state.project.projectAuthActions) }"
              theme="primary"
              :class="{
                'btn-permission-disable': !hasPermission(['sla_calendar_create'], $store.state.project.projectAuthActions)
              }"
              @click="addModelInfo">
              {{ $t('m["立即创建"]') }}
            </bk-button>
          </template>
        </empty-tip>
        <template v-else>
          <!-- 提示信息 -->
          <div class="bk-itsm-version" v-if="versionStatus">
            <i class="bk-icon icon-info-circle"></i>
            <span>{{ $t('m.slaContent["服务模式：通过对工作日节假日的配置，工作时段以及工作时间的设置，来设定不同的服务模式。服务模式将会应用到服务级别协议中，最终体现在对不同优先级服务的受理时效上。"]') }}</span>
            <i class="bk-icon icon-close" @click="closeVersion"></i>
          </div>
          <!-- 新增 -->
          <div class="bk-sla-add">
            <bk-button
              data-test-id="slaPattern_button_create"
              v-cursor="{ active: !hasPermission(['sla_calendar_create'], $store.state.project.projectAuthActions) }"
              theme="primary"
              :title="$t(`m.eventdeploy['新增']`)"
              icon="plus"
              :class="['mr10', 'plus-cus', {
                'btn-permission-disable': !hasPermission(['sla_calendar_create'], $store.state.project.projectAuthActions)
              }]"
              @click="addModelInfo">
              {{ $t('m.eventdeploy["新增"]') }}
            </bk-button>
          </div>
          <!-- 列表数据 -->
          <ul class="bk-sla-list" v-if="modelList.length">
            <li v-for="(item, index) in modelList" :key="index" @click="changeLineInfo(item, index)"
              style="cursor: pointer">
              <div class="bk-sla-content">
                <div class="bk-content-info">
                  <p class="bk-info-name" :title="item.name">{{item.name}}</p>
                  <p v-if="item.days[0] && item.days[0].day_of_week">
                    <span v-for="(day, dIndex) in splitItem(item)" :key="String(item.id) + String(dIndex)">{{numToDay(day)}}
                    </span>
                    <span v-for="(it,i) in item.days[0].duration" :key="i">
                      {{it.start_time}}-{{it.end_time}}
                    </span>
                  </p>
                  <p v-else>
                    <span>
                      {{$t('m.slaContent["周一至周日 全天"]')}}
                    </span>
                  </p>
                </div>
                <div class="bk-sla-operat">
                  <i class="bk-icon icon-delete" data-test-id="slaPattern-i-deleteModel1" v-if="!item.is_builtin"
                    @click.stop="deleteModel(item, index)"></i>
                  <i class="bk-icon icon-delete bk-icon-disabled builtin" data-test-id="slaPattern-i-deleteModel2" v-else
                    @click.stop="deleteModel(item, index)"
                    v-bk-tooltips="bktooltipsInfo"></i>
                </div>
              </div>
            </li>
          </ul>
        </template>
      </div>
    </template>
    <template v-else>
      <add-model
        :change-info="changeInfo"
        :is-edit="isEdit">
      </add-model>
    </template>
  </div>
</template>

<script>
  import { errorHandler } from '../../utils/errorHandler';
  import permission from '@/mixins/permission.js';
  import addModel from './addModel.vue';
  import EmptyTip from '../project/components/emptyTip.vue';

  export default {
    name: 'slaManager',
    components: {
      addModel,
      EmptyTip,
    },
    mixins: [permission],
    data() {
      return {
        isDataLoading: false,
        secondClick: false,
        versionStatus: true,
        modelList: [],
        // 新增修改
        changeInfo: {
          isShow: false,
          info: {
            is_builtin: false,
          },
        },
        // 编辑模式发送初始信息
        isEdit: false,
        bktooltipsInfo: {
          content: this.$t('m.slaContent[\'内置服务模型不可删除\']'),
          showOnInit: false,
          placements: ['top'],
        },
        emptyTip: {
          title: this.$t('m[\'当前项目下还没有 <SLA模式>\']'),
          subTitle: this.$t('m[\'SLA（即服务级别协议）是服务支撑团队与组织机构内最终用户之间的“服务合同”。通常，SLA 是通过定义所提供的服务必须遵守的质量标准以及交付服务的时间表来建立对服务和服务质量的清晰理解；加快服务响应时间、减少等待时长、降低运营成本，一套合理且适用的 SLA 将是您实现这些目标的最佳选择。\']'),
          desc: [
            {
              src: require('../../images/illustration/apply.svg'),
              title: this.$t('m[\'设计服务模式并制定协议\']'),
              content: this.$t('m[\'通常我们会先设定团队的服务时间段，然后进一步配置在规定的服务时间段内，针对不同的服务工单紧急程度约定响应和处理时长，为的是保障用户的服务体验、提升用户满意度。\']'),
            },
            {
              src: require('../../images/illustration/start-service.svg'),
              title: this.$t('m[\'为服务配置合适的 SLA\']'),
              content: this.$t('m[\'接下来就是为不同的服务配置合适的 SLA 了，因为很多服务的处理流程中可能会需要多个不同职能团队来处理，所以我们支持在一个服务内针对不同的流程区间设置差异化的服务协议，满足对不同服务团队的SLA要求。\']'),
            },
          ],
          links: [
            {
              text: this.$t('m[\'如何设计一套合理有效的 SLA ？\']'),
              btn: this.$t('m[\'产品白皮书\']'),
              href: 'https://bk.tencent.com/docs/document/6.0/145/6596',
            },
          ],
        },
      };
    },
    computed: {
      sliderStatus() {
        return this.$store.state.common.slideStatus;
      },
    },
    watch: {},
    mounted() {
      this.getModelList();
      if (this.$route.query.key === 'create') this.addModelInfo();
    },
    methods: {
      async getModelList() {
        this.isDataLoading = true;
        await this.$store.dispatch('sla/getScheduleList', { project_key: this.$store.state.project.id }).then((res) => {
          this.modelList = res.data;
        })
          .catch((res) => {
            errorHandler(res, this);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
      },
      closeVersion() {
        this.versionStatus = false;
      },
      // 新增
      addModelInfo() {
        if (!this.hasPermission(['sla_calendar_create'], this.$store.state.project.projectAuthActions)) {
          const { projectInfo } = this.$store.state.project;
          const resourceData = {
            project: [{
              id: projectInfo.key,
              name: projectInfo.name,
            }],
          };
          this.applyForPermission(['sla_calendar_create'], this.$store.state.project.projectAuthActions, resourceData);
        } else {
          this.isEdit = false;
          this.changeInfo.isShow = true;
          this.changeInfo.info.is_builtin = false;
        }
      },
      // 修改信息/查看详情
      changeLineInfo(item) {
        if (!this.hasPermission(['sla_calendar_edit'], [...this.$store.state.project.projectAuthActions, ...item.auth_actions])) {
          const { projectInfo } = this.$store.state.project;
          const resourceData = {
            project: [{
              id: projectInfo.key,
              name: projectInfo.name,
            }],
            sla_calendar: [{
              id: item.id,
              name: item.name,
            }],
          };
          this.applyForPermission(['sla_calendar_edit'], [...this.$store.state.project.projectAuthActions, ...item.auth_actions], resourceData);
          return false;
        }
        this.changeInfo.info = item;
        this.isEdit = true;
        this.changeInfo.isShow = true;
      },
      // 删除
      deleteModel(item) {
        if (!this.hasPermission(['sla_calendar_delete'], [...this.$store.state.project.projectAuthActions, ...item.auth_actions])) {
          const { projectInfo } = this.$store.state.project;
          const resourceData = {
            project: [{
              id: projectInfo.key,
              name: projectInfo.name,
            }],
            sla_calendar: [{
              id: item.id,
              name: item.name,
            }],
          };
          this.applyForPermission(['sla_calendar_delete'], [...this.$store.state.project.projectAuthActions, ...item.auth_actions], resourceData);
          return false;
        }
        if (item.is_builtin) {
          return;
        }
        this.$bkInfo({
          type: 'warning',
          title: this.$t('m.slaContent["确定删除该服务模式？"]'),
          confirmFn: () => {
            const { id } = item;
            if (this.secondClick) {
              return;
            }
            this.secondClick = true;
            this.$store.dispatch('sla/deleteSchedule', id).then(() => {
              this.getModelList();
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
      splitItem(item) {
        return item.days[0].day_of_week.split(',');
      },
      numToDay(val) {
        let temp = '';
        switch (val) {
          case '0':
            temp = this.$t('m.slaContent["周一"]');
            break;
          case '1':
            temp = this.$t('m.slaContent["周二"]');
            break;
          case '2':
            temp = this.$t('m.slaContent["周三"]');
            break;
          case '3':
            temp = this.$t('m.slaContent["周四"]');
            break;
          case '4':
            temp = this.$t('m.slaContent["周五"]');
            break;
          case '5':
            temp = this.$t('m.slaContent["周六"]');
            break;
          case '6':
            temp = this.$t('m.slaContent["周日"]');
            break;
          default:
            temp = '';
        }
        return temp;
      },
    },
  };
</script>

<style lang='scss' scoped>
    @import '../../scss/mixins/clearfix.scss';
    @import '../../scss/mixins/scroller.scss';
    .itsm-page-content {
        padding-top: 14px;
        .bk-itsm-version {
            margin: 0;
            margin-bottom: 14px;
        }
    }
    .bk-sla-add {
        @include clearfix;
    }

    .bk-sla-list {
        margin-top: 14px;
        @include clearfix;
        li {
            float: left;
            width: calc(33.33% - 8px);
            height: 60px;
            margin-bottom: 10px;
            margin-right: 12px;

            &:nth-child(3n) {
                margin-right: 0;
            }

            &:hover {
                .bk-sla-time {
                    color: #fff;
                    background-color: #3A84FF;
                    border-color: #3A84FF;
                }

                .bk-sla-content {
                    border-color: #3A84FF;
                }

                .bk-sla-operat {
                    display: block;

                    .icon-delete-disable {
                        color: #C4C6CC;
                    }
                }
            }
        }

        .bk-sla-content {
            float: left;
            width: 100%;
            height: 60px;
            padding: 10px 24px;
            line-height: 20px;
            color: #C4C6CC;
            font-size: 12px;
            background-color: white;
            box-shadow: 0px 2px 2px 0px rgba(0,0,0,0.10);
            .bk-content-info {
                float: left;
                width: 92%;

                p {
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }

                .bk-info-name {
                    color: #63656E;
                    font-weight: bold;
                    font-size: 13px;
                }
            }

            .bk-sla-operat {
                float: left;
                width: 8%;
                line-height: 40px;
                text-align: right;
                display: none;

                .bk-icon {
                    font-size: 14px;
                    padding: 9px;
                    cursor: pointer;

                    &:hover {
                        color: #3A84FF;
                    }
                }

                .bk-icon-disabled {
                    color: #C4C6CC;

                    &:hover {
                        color: #C4C6CC;
                    }
                }
            }
        }
    }
    .builtin {
        color: #C4C6CC !important;
        cursor: not-allowed!important;
    }
</style>
