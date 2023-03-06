<template>
  <div class="bk-itsm-service">
    <div class="is-title" :class="{ 'bk-title-left': !sliderStatus }">
      <p class="bk-come-back">
        {{ $t('m["通知配置"]') }}
      </p>
    </div>
    <div class="itsm-page-content">
      <ul class="bk-notice-tab">
        <li v-for="(item, index) in noticeType"
          :key="item.typeName"
          :class="{ 'bk-check-notice': acticeTab === item.typeName }"
          @click="changeNotice(item, index)">
          <span>{{ item.name }}</span>
        </li>
      </ul>
      <div class="bk-only-btn">
        <bk-button theme="primary"
          data-test-id="notice_button_create"
          @click="addNotice">
          <i class="bk-itsm-icon icon-itsm-icon-one-five"></i>
          {{ $t(`m.deployPage['新增']`) }}
        </bk-button>
        <div class="bk-only-search">
          <bk-input
            data-test-id="notice_input_search"
            :placeholder="$t(`m['请输入模板内容']`)"
            :clearable="true"
            :right-icon="'bk-icon icon-search'"
            v-model="searchNotice"
            @enter="getNoticeList(1)"
            @clear="getNoticeList(1)">
          </bk-input>
        </div>
      </div>
      <bk-table
        v-bkloading="{ isLoading: isDataLoading }"
        :data="noticeList"
        :size="'small'">
        <bk-table-column type="index" label="No." align="center" width="60"></bk-table-column>
        <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.deployPage['通知类型']`)" prop="action_name"></bk-table-column>
        <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.slaContent['更新时间']`)" prop="update_at"></bk-table-column>
        <bk-table-column :render-header="$renderHeader" :show-overflow-tooltip="true" :label="$t(`m.deployPage['更新人']`)" prop="updated_by"></bk-table-column>
        <bk-table-column :label="$t(`m.deployPage['操作']`)" width="150">
          <template slot-scope="props">
            <bk-button
              theme="primary"
              text
              @click="editNotice(props.row)">
              {{ $t('m.deployPage["编辑"]') }}
            </bk-button>
            <bk-button
              theme="primary"
              text
              @click="deleteNotice(props.row)">
              {{ $t('m.deployPage["删除"]') }}
            </bk-button>
          </template>
        </bk-table-column>
        <div class="empty" slot="empty">
          <empty
            :is-error="listError"
            :is-search="searchToggle"
            @onRefresh="getNoticeList()"
            @onClearSearch="getNoticeList()">
          </empty>
        </div>
      </bk-table>
      <bk-dialog v-model="isShowEdit"
        width="690"
        theme="primary"
        :mask-close="false"
        :auto-close="false"
        :header-position="'left'"
        :title="isEdit ? $t(`m['编辑']`) : $t(`m['新建']`) "
        @confirm="submitNotice"
        @cancel="closeNotice">
        <div class="notice-forms">
          <bk-form ref="basicFrom" :model="formData" :label-width="300" width="700" form-type="vertical" :rules="rules">
            <bk-form-item :label="$t(`m['通知方式']`)" :required="true" :property="'noticeType'">
              <bk-select :disabled="true" v-model="formData.noticeType" searchable>
                <bk-option v-for="option in noticeType"
                  :key="option.typeName"
                  :id="option.typeName"
                  :name="option.name">
                </bk-option>
              </bk-select>
            </bk-form-item>
            <bk-form-item :label="$t(`m['通知场景']`)" :required="true" :property="'noticeUserBy'">
              <bk-select :disabled="false" v-model="formData.noticeUserBy" searchable @selected="handleSelectUserBy">
                <bk-option v-for="option in userByList"
                  :key="option.id"
                  :id="option.id"
                  :name="option.name">
                </bk-option>
              </bk-select>
            </bk-form-item>
            <bk-form-item :label="$t(`m['通知类型']`)" :required="true" :property="'noticeAction'">
              <bk-select v-model="formData.noticeAction" searchable :loading="actionLoading">
                <bk-option v-for="option in actionList"
                  :key="option.id"
                  :id="option.id"
                  :name="option.name">
                </bk-option>
              </bk-select>
            </bk-form-item>
          </bk-form>
          <editor-notice
            ref="editorNotice"
            :custom-row="customRow"
            :is-show-title="true"
            :check-id="acticeTab"
            :is-show-footer="false"
            :notice-info="formInfo"
            @closeEditor="closeEditor">
          </editor-notice>
        </div>
      </bk-dialog>
    </div>
  </div>
</template>

<script>
  import editorNotice from '../processManagement/notice/editorNotice.vue';
  import permission from '@/mixins/permission.js';
  import { mapState } from 'vuex';
  import Empty from '../../components/common/Empty.vue';
  export default {
    name: 'Notice',
    components: {
      editorNotice,
      Empty,
    },
    mixins: [permission],
    data() {
      return {
        acticeTab: 'WEIXIN',
        isShowEdit: false,
        isEdit: false,
        editNoticeId: '',
        remindWayList: [
          { id: 'WEIXIN', name: this.$t('m.treeinfo["企业微信"]') },
          { id: 'EMAIL', name: this.$t('m.treeinfo["邮件"]') },
          { id: 'SMS', name: this.$t('m.treeinfo["手机短信"]') },
        ],
        noticeList: [],
        // 先写死，后续添加自定义
        noticeTypeLIST: [
          { id: 'WEIXIN', name: this.$t('m.treeinfo["企业微信"]') },
          { id: 'EMAIL', name: this.$t('m.treeinfo["邮件"]') },
          { id: 'SMS', name: this.$t('m.treeinfo["手机短信"]') },
        ],
        userByList: [
          { id: 'TICKET', name: this.$t('m[\'单据\']') },
          { id: 'SLA', name: this.$t('m[\'SLA\']') },
          { id: 'TASK', name: this.$t('m[\'任务\']') },
        ],
        rules: {
          noticeType: [
            {
              required: true,
              message: this.$t('m[\'必选项\']'),
              trigger: 'blur',
            },
          ],
          noticeAction: [
            {
              required: true,
              message: this.$t('m[\'必选项\']'),
              trigger: 'blur',
            },
          ],
          noticeUserBy: [
            {
              required: true,
              message: this.$t('m[\'必选项\']'),
              trigger: 'blur',
            },
          ],
        },
        actionList: [],
        typeList: [],
        formData: {
          noticeType: '',
          noticeAction: '',
          noticeUserBy: '',
        },
        formInfo: {},
        isDataLoading: false,
        searchNotice: '',
        searchToggle: false,
        listError: false,
        customRow: 5,
        actionLoading: false,
      };
    },
    computed: {
      sliderStatus() {
        return this.$store.state.common.slideStatus;
      },
      ...mapState({
        noticeType: state => state.common.configurInfo.notify_type,
      }),
    },
    watch: {
      acticeTab: {
        handler(val) {
          this.formData.noticeType = val;
        },
        immediate: true,
      },
    },
    mounted() {
      this.getNoticeList();
    },
    methods: {
      changeNotice(item) {
        this.acticeTab = item.typeName;
        this.getNoticeList();
      },
      async handleSelectUserBy(val) {
        try {
          this.actionLoading = true;
          this.actionList = [];
          this.formData.noticeAction = '';
          const parmas = {
            used_by: val,
          };
          const res = await this.$store.dispatch('project/getAction', parmas);
          if (res.data && res.result) {
            const list = res.data;
            for (const item in list) {
              this.actionList.push({
                id: item,
                name: list[item],
              });
            }
          }
        } catch (e) {
          console.log(e);
        } finally {
          this.actionLoading = false;
        }
      },
      getNoticeList(isSearch) {
        this.isDataLoading = true;
        const params = {
          project_key: this.$route.query.project_id,
          notify_type: this.acticeTab,
        };
        this.listError = false;
        this.searchToggle = false;
        if (isSearch) {
          this.searchToggle = true;
          params.content_template__icontains = this.searchNotice;
        } else {
          this.searchNotice = '';
        }
        this.$store.dispatch('project/getProjectNotice', { params }).then((res) => {
          this.noticeList = res.data;
        })
          .catch((res) => {
            this.listError = true;
            console.log(res);
          })
          .finally(() => {
            this.isDataLoading = false;
          });
      },
      submitNotice() {
        Promise.all([this.$refs.editorNotice.$refs.wechatForm.validate(), this.$refs.basicFrom.validate()]).then(() => {
          const { title, message } = this.$refs.editorNotice.formInfo;
          const params = {
            title_template: title,
            content_template: message,
            project_key: this.$route.query.project_id,
          };
          const url = this.isEdit ? 'project/updateProjectNotice' : 'project/addProjectNotice';
          if (this.isEdit) params.id = this.editNoticeId;
          params.notify_type = this.formData.noticeType;
          params.action = this.formData.noticeAction;
          params.used_by = this.formData.noticeUserBy;
          // 调取接口数据
          this.$store.dispatch(url, params).then(res => {
            this.$bkMessage({
              message: res.message,
              theme: 'success',
            });
            this.isShowEdit = false;
            this.getNoticeList();
            this.clearFromData();
          })
            .catch(e => {
              this.$bkMessage({
                message: e.data.message,
                theme: 'error',
              });
            });
        });
      },
      clearFromData() {
        this.formData.noticeAction = '';
        this.formData.noticeUserBy = '';
        this.$refs.editorNotice.formInfo = {
          title: '',
          message: '',
        };
      },
      closeNotice() {
        this.$refs.basicFrom.clearError();
        this.$refs.editorNotice.$refs.wechatForm.clearError();
        this.clearFromData();
        this.isShowEdit = false;
      },
      // 新增配置
      addNotice() {
        this.isEdit = false;
        this.isShowEdit = true;
      },
      editNotice(row) {
        this.editNoticeId = row.id;
        this.formData.noticeUserBy = row.used_by;
        this.handleSelectUserBy(row.used_by);
        this.formData.noticeAction = row.action;
        this.$refs.editorNotice.formInfo = {
          title: row.title_template,
          message: row.content_template,
        };
        this.isEdit = true;
        this.isShowEdit = true;
      },
      deleteNotice(row) {
        this.$bkInfo({
          title: this.$t('m["确认要删除？"]'),
          confirmLoading: true,
          confirmFn: () => {
            this.$store.dispatch('project/deleteProjectNotice', row.id).then(() => {
              this.$bkMessage({
                message: this.$t('m["删除成功"]'),
                theme: 'success',
              });
              this.getNoticeList();
            });
          },
        });
      },
      closeEditor() {
        this.isShowEdit = false;
      },
    },
  };

</script>

<style lang='scss' scoped>
    @import '../../scss/mixins/clearfix.scss';
    @import '../../scss/mixins/scroller.scss';
    .bk-notice-tab {
        @include clearfix;
        border-bottom: 1px solid #dde4eb;
        margin: -20px -20px 20px;
        padding: 0 20px;
        background-color: #ffffff;
        li {
            float: left;
            padding: 0 10px;
            line-height: 46px;
            text-align: center;
            color: #63656e;
            cursor: pointer;
            font-size: 14px;

            &:hover {
                color: #3a84ff;
            }
        }

        .bk-check-notice {
            border-bottom: 2px solid #3a84ff;
            color: #3a84ff;
        }
    }
    .notice-forms {
        max-height: 600px;
        padding: 4px;
        overflow-y: auto;
        @include scroller;
    }
</style>
