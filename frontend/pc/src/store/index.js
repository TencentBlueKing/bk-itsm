/*
 * Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 * BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
 *
 * License for BK-ITSM 蓝鲸流程服务:
 * --------------------------------------------------------------------
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
 * LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
 * NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
 */

import Vue from "vue";
import Vuex from "vuex";
import ajax from "../utils/ajax";

import common from "./modules/common";
import changeType from "./modules/changeType";
import change from "./modules/change";
import request from "./modules/request";
import question from "./modules/question";
import eventType from "./modules/eventType";
import design from "./modules/design";
import service from "./modules/service";
import cdeploy from "./modules/cdeploy";
import print from "./modules/print";
import evaluation from "./modules/evaluation";
import workbench from "./modules/workbench";
import operation from "./modules/operation";
import serviceEntry from "./modules/serviceEntry";
import sla from "./modules/sla";
import slaManagement from "./modules/slaManagement";
import serviceCatalog from "./modules/serviceCatalog";
import catalogService from "./modules/catalogService";
import workflowVersion from "./modules/workflowVersion";
import attachmentStorage from "./modules/attachmentStorage";
import apiRemote from "./modules/apiRemote";
import storeFlow from "./modules/storeFlow";

import deployCommon from "./modules/deployCommon";
import deployOrder from "./modules/deployOrder";
import noticeConfigure from "./modules/noticeConfigure";
import datadict from "./modules/datadict";
import dictdata from "./modules/dictdata";
import systemLog from "./modules/systemLog";
import version from "./modules/version";
import publicField from "./modules/publicField";
import basicModule from "./modules/basicModule";
import ticketStatus from "./modules/ticketStatus";
import taskTemplate from "./modules/taskTemplate";
import taskExecute from "./modules/taskExecute";

import bkPlugin from "./modules/bkPlugin";

// 组件升级统一请求
import user from "./newModules/user";
// 新增功能
import trigger from "./newModules/trigger";
import taskFlow from "./newModules/taskFlow";
import project from "./modules/project.js";

// 根据模板重新整理
import ticket from "./modules/ticket";

Vue.use(Vuex);

export default new Vuex.Store({
  // 模块
  modules: {
    user,
    common,
    changeType,
    design,
    service,
    request,
    question,
    eventType,
    cdeploy,
    change,
    print,
    evaluation,
    workbench,
    deployCommon,
    deployOrder,
    noticeConfigure,
    operation,
    attachmentStorage,
    serviceEntry,
    serviceCatalog,
    catalogService,
    workflowVersion,
    sla,
    slaManagement,
    datadict,
    dictdata,
    apiRemote,
    storeFlow,
    systemLog,
    version,
    publicField,
    basicModule,
    ticketStatus,
    taskTemplate,
    trigger,
    taskFlow,
    taskExecute,
    project,
    // new
    ticket,
    bkPlugin,
  },
  // 公共 store
  state: {
    language: "zh-cn",
    // 任务执行后刷新任务记录列表
    taskHistoryRefresh: false,
    // 缓存人员选择器数据
    memberList: [],
    // 提单成功信息
    subinfo: null,
    // 屏宽
    clientWidth: null,
    // 工作台图表数据
    drawType: {},
    drawTime: {},
    drawStatus: {},
    // 运营图表数据
    operationalall: {},
    operationalmodule: {},
    // 自定义数据
    customList: [],
    customDict: {},
    choice_type_list: [],
    serviceList: [],
    commomInfo: {
      choice_state_list_dict: {},
      export_fields: [],
    },
    // 系统当前登录用户
    user: {},
    // iFrame加载状态
    isIframeLoading: true,
    // 权限状态
    permisStatus: {},
    // 我的待办和待认领
    myToDoInfo: false,
    basicId: "",
    // file状态
    fileStatus: false,
    // 深复制
    deepcopy: function (item) {
      if (!item) {
        return item;
      }
      if (item.constructor === Object) {
        const itemobject = {};
        const keys = Object.keys(item);
        if (keys.length) {
          keys.map((it) => {
            itemobject[it] = this.deepcopy(item[it]);
          });
        }
        return itemobject;
      } else if (item.constructor === Array) {
        const itemarray = [];
        if (item.length) {
          item.map((ite) => {
            itemarray.push(this.deepcopy(ite));
          });
        }
        return itemarray;
      } else {
        return item;
      }
    },
    // 数据校验isSub
    dataCheck: function (data, type) {
      // 非空校验
      if (!data) {
        return this.$t(`m.wiki["不能为空"]`);
      }
      // 长度校验
      let typelist;
      let islength;
      let minlength;
      let maxlength;
      // type eg: 'Metacharacter_1$length^150_chinse'
      if (type) {
        typelist = type.toString().split("_");
        type = typelist[0];
        typelist.forEach((item) => {
          if (item.indexOf("length") !== -1) {
            islength = true;
            if (item.indexOf("$") !== -1) {
              minlength = item.split("$")[0];
            }
            if (item.indexOf("^") !== -1) {
              maxlength = item.split("^")[1];
            }
          }
        });
        if (islength) {
          if (minlength && data.length < minlength) {
            return this.$t("m.wiki['长度应大于']") + `${minlength}`;
          }
          if (maxlength && data.length > maxlength) {
            return this.$t("m.wiki['长度应小于']") + `${minlength}`;
          }
          // 默认不超过255
          if (data.length > 255) {
            return this.$t("m.wiki['长度1~255']");
          }
        }
      }
      // 多类型校验 /^[\u4e00-\u9fa5_a-zA-Z0-9]+$/
      switch (type) {
        case "Metacharacter":
          // 判断输入字符串是否为中文、数字、字母、下划线组成
          if (typelist && typelist.indexOf("chinse") !== -1) {
            if (/^[\u4e00-\u9fa5_a-zA-Z0-9]+$/.test(data)) {
              return "";
            }
            return this.$t("m.wiki['内容应由中文、数字、字母、下划线组成']");
          }
          // 判断输入字符串是否为数字、字母、下划线组成
          if (/^\w+$/.test(data)) {
            return "";
          }
          return this.$t("m.wiki['内容应由数字、字母、下划线组成']");
        // break
        case "Number":
          // 判断输入字符串是否为数字、字母、下划线组成
          if (/^\d+$/.test(data)) {
            return "";
          }
          return this.$t("m.wiki['请填写数字']");
        // break
        default:
          return "";
      }
    },
    // 所属业务 -- 接口数据缓存
    business: [],
    faultType: [],
    openFunction: {
      SYS_FILE_PATH: false,
      FLOW_PREVIEW: false,
      CHILD_TICKET_SWITCH: false,
      WIKI_SWITCH: false,
      SLA_SWITCH: false,
      TRIGGER_SWITCH: false,
      TASK_SWITCH: false,
      TABLE_FIELDS_SWITCH: false,
      FIRST_STATE_SWITCH: false,
      SMS_COMMENT_SWITCH: false,
    },
  },
  // 公共 mutations
  mutations: {
    // 设置语言
    setLanguage(state, value) {
      state.language = value;
    },
    /**
     * 更新当前用户 user
     *
     * @param {Object} state store state
     * @param {Object} user user 对象
     */
    // 人员选择数据
    changMemberList(state, value) {
      state.memberList = value;
    },
    // 改变file的上传状态
    changeFileStatus(state, value) {
      state.fileStatus = value;
    },
    // 所属业务缓存
    storeBusiness(state, value) {
      state.business = value;
    },
    // 故障类型缓存
    storeFault(state, value) {
      state.faultType = value;
    },
    setIframeLoadingState(state, payload) {
      state.isIframeLoading = payload.status;
    },
    changeBasicId(state, value) {
      state.basicId = value;
    },
    // 改变权限设置
    changePermis(state, value) {
      state.permisStatus = value;
    },
    // 自定义数据
    changeCustom(state, value) {
      state.customList = value;
    },
    // 公共数据
    getTypeWay(state, value) {
      state.commomInfo["export_fields"] = value["export_fields"];
      state.commomInfo["choice_state_list_dict"] = value["choice_state_list_dict"];
      state.commomInfo["processor_type"] = value["processor_type"];
    },
    // 工作台图表数据
    getdrawType(state, value) {
      state.drawType = value;
    },
    getdrawTime(state, value) {
      state.drawTime = value;
    },
    getdrawStatus(state, value) {
      state.drawStatus = value;
    },
    // 运营图表数据
    setoperationalall(state, value) {
      state.operationalall[value[0]] = value[1];
    },
    setoperationalmodule(state, value) {
      state.operationalmodule[value[0]] = value[1];
    },
    // 屏宽
    changeClient(state, value) {
      state.clientWidth = value;
    },
    // 我的待办和待认领
    changeMyData(state, value) {
      state.myToDoInfo = value;
    },
    // 全选函数
    allselected(state, obj) {
      if (obj.vm[obj.dic][obj.isall]) {
        if ((obj.key.indexOf("all") !== -1) | (obj.data.length === obj.datalist.length - 1)) {
          // 全选
          obj.vm[obj.dic][obj.Selected] = obj.datalist.map((item) => {
            return item.key;
          });
          obj.vm[obj.dic][obj.isall] = false;
        }
      } else {
        if (obj.key.indexOf("all") !== -1) {
          // 去掉 全选--all
          obj.vm[obj.dic][obj.Selected].splice(0, 1);
        } else {
          // 取消全选
          obj.vm[obj.dic][obj.Selected] = [];
        }
        obj.vm[obj.dic][obj.isall] = true;
      }
    },
    changeMsg(state, obj) {
      state.choice_type_list = obj;
    },
    taskHistoryRefreshFunc(state) {
      state.taskHistoryRefresh = !state.taskHistoryRefresh;
    },
    changeOpenFunction(state, obj) {
      state.openFunction = obj;
    },
  },
  // 公共 actions
  actions: {
    /**
     * 获取项目里面的 rtx 人员选择器数据
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {string} projectId 项目 id
     *
     * @return {Promise} promise 对象
     */
    getProjectRtxList({ commit, state, dispatch }, { projectId }) {
      return ajax.get(`api/projects/users/?project_id=${projectId}`).then((response) => response.data);
    },
    // 自定义列表数据
    getCustom({ commit, state, dispatch }) {
      return ajax.get(`service/categories/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 自定义列表数据 -- dict
    getCustomDict({ commit, state, dispatch }) {
      return ajax.get(`service/categories/translate_view/`).then((response) => {
        const res = response.data;
        state.customDict = res.data;
        return res;
      });
    },
    // 权限中心
    getPermiss({ commit, state, dispatch }) {
      return ajax.get(`role/users/extra/get_access_by_user/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取首页待办
    getHomeProcess({ commit, state, dispatch }) {
      return ajax.get(`ticket/receipts/mine/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取最新动态
    getlogList({ commit, state, dispatch }) {
      return ajax.get(`ticket/logs/get_index_ticket_event_log/`).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 获取单个人员的详细信息
    getPersonInfo({ commit, state, dispatch }, params) {
      return ajax.get(`gateway/bk_login/get_batch_users/`, { params: params }).then((response) => {
        const res = response.data;
        return res;
      });
    },
    // 通过部门 id 获取部门信息
    getDepartmentInfo({ commit, state, dispatch }, params) {
      return ajax.get(`gateway/usermanage/get_department_info/`, { params: params }).then((response) => {
        let res = response.data;
        return res;
      });
    },
    // 获取标准运维流程模板
    getTemplateList({ commit }, params) {
      return ajax.get(`gateway/sops/get_template_list/`, { params: params }).then((response) => response.data);
    },
    // 获取标准运维流程模板
    getTemplateDetail({ commit }, params) {
      return ajax.get(`gateway/sops/get_template_detail/`, { params: params }).then((response) => response.data);
    },
    // 获取标准运维方案列表
    getTemplatePlanList({ commit }, params) {
      return ajax.get(`gateway/sops/get_sops_template_schemes/`, { params: params }).then((response) => response.data);
    },
    // 创建标准运维任务
    createTask({ commit }, params) {
      return ajax.post(`task/create_task/`, params).then((response) => response.data);
    },
    getTaskList({ commit }, query) {
      return ajax.get("task/get_tasks/", { params: { ...query } }).then((response) => response.data);
    },
    getBkBizList({ commit }, query) {
      return ajax.get("gateway/cmdb/get_app_list", { params: { ...query } }).then((response) => response.data);
    },
    operateTask({ commit }, params) {
      return ajax.post(`task/operate_task/`, params).then((response) => response.data);
    },
    startTask({ commit }, params) {
      return ajax.post(`task/start_task/`, params).then((response) => response.data);
    },
  },
});
