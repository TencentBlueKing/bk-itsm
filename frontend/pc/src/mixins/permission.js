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

import bus from '@/utils/bus.js';
const permission = {
  methods: {
    /**
         * 获取项目已有的的权限
         * 项目权限 + 不关联资源的页面权限 + 当前实例的已有权限
         * @param { Array } curPermission 当前拥有的权限（针对单个实例）
         */
    getAllAppPermission(curPermission) {
      const { systemPermission } = this.$store.state.common;
      return [...systemPermission, ...curPermission];
    },
    /**
         * 判断当前权限是否满足需要的权限
         * @param {Array} reqPermission 需要申请的权限
         * @param {Array} curPermission 当前拥有的权限
         */
    hasPermission(reqPermission = [], curPermission = []) {
      const { actions } = this.$store.state.common.permissionMeta;
      return reqPermission.every((item) => {
        const permActionData = actions.find(action => action.id === item);
        if (!permActionData) { // 权限没有在 meta 数据中返回，判定为无对应权限
          return false;
        }
        // 项目已有权限 + 实例已有权限
        if (!this.getAllAppPermission(curPermission).includes(item)) {
          return false;
        }
        if (permActionData.relate_actions.length > 0) {
          return this.hasPermission(permActionData.relate_actions, curPermission);
        }
        return true;
      });
    },
    /**
         * 拼接申请权限跳转链接接口请求参数
         * @param {Array} reqPermission 需要的申请的权限
         * @param {Array} curPermission 当前拥有的权限
         * @param {Array} resourceData 资源数据
         */
    applyForPermission(reqPermission = [], curPermission = [], resourceData = {}, ret = false) {
      const { actions, resources, system } = this.$store.state.common.permissionMeta;
      const bkitsm = system[0];
      const { id: systemId, name: systemName } = bkitsm;
      const actionsData = this.assembleActionsData(
        reqPermission,
        curPermission,
        resourceData,
        actions,
        resources,
        systemId,
        systemName
      );
      const data = {
        system_id: systemId,
        system_name: systemName,
        actions: actionsData,
      };
      if (ret) {
        return data;
      }
      this.triggerPermisionModal(data);
    },
    /**
         * 组装 actions 数据，权限之间可能有相互依赖关系需要递归处理
         * @param {Arrau} reqPermission 需要的申请的权限
         * @param {Array} curPermission 当前拥有的权限
         * @param {Object} resourceData 资源数据
         * @param {Array} actions 系统中所有需要鉴权的操作相关信息
         * @param {Array} resources 系统中资源信息
         * @param {String} systemId 系统 id
         * @param {String} systemName 系统名称
         */
    assembleActionsData(reqPermission, curPermission, resourceData, actions, resources, systemId, systemName) {
      const actionsData = [];
      reqPermission.forEach((requiredItem) => {
        const permActionData = actions.find(action => action.id === requiredItem);
        // 权限字典里不存在该权限时
        if (!permActionData) {
          return;
        }
        // 用户没有该权限
        if (!this.getAllAppPermission(curPermission).includes(requiredItem)) {
          const relateResources = [];
          permActionData.relate_resources.forEach((reItem) => {
            const resourceMap = resources.find(item => item.id === reItem);
            const instances = this.assembleInstances(resources, resourceMap, resourceData);
            relateResources.push({
              system_id: systemId,
              system_name: systemName,
              type: resourceMap.id,
              type_name: resourceMap.name,
              instances: [instances],
            });
          });
          actionsData.push({
            id: permActionData.id,
            name: permActionData.name,
            related_resource_types: relateResources,
          });
        }
        // 该权限依赖其他权限
        if (permActionData.relate_actions.length > 0) {
          const relateActions = this.assembleActionsData(
            permActionData.relate_actions,
            curPermission,
            resourceData,
            actions,
            resources,
            systemId,
            systemName
          );
          relateActions.forEach((item) => {
            if (actionsData.findIndex(action => action.id === item.id) === -1) { // 避免操作权限重复
              actionsData.push(item);
            }
          });
        }
      });
      return actionsData;
    },
    /**
         * 拼接权限所关联的资源实例信息
         * @param {Object} resources 系统中资源信息
         * @param {Object} resourceMap 当前资源详情
         * @param {Object} resourceData 资源实例数据
         */
    assembleInstances(resources, resourceMap, resourceData) {
      let data = [];
      if (resourceMap.parent_id) {
        const parentMap = resources.find(item => item.id === resourceMap.parent_id);
        data = data.concat(this.assembleInstances(resources, parentMap, resourceData));
      }
      const instanceData = resourceData[resourceMap.id];
      instanceData.forEach((item) => {
        data.push({
          type: resourceMap.id,
          type_name: resourceMap.name,
          id: item.id,
          name: item.name,
        });
      });
      return data;
    },
    /**
         * 打开权限申请弹窗
         * @param {Obejct} permissions 无权限请求权限中心链接请求参数数据
         */
    triggerPermisionModal(permissions) {
      bus.$emit('showPermissionModal', permissions);
    },
    // 页面权限验证
    checkPagePermission() {
      const authMap = {
        OperationHome: 'operational_data_view',
        OperationService: 'operational_data_view',
        // 'publicFields': 'public_field_view',
        // 'publicAPI': 'public_api_view',
        // 'taskTpl': 'task_template_view',
        notifySetting: 'notification_view',
        slaPriority: 'sla_priority_view',
        ticketStatus: 'ticket_state_view',
        globalSetting: 'global_settings_view',
      };
      const actionId = authMap[this.$route.name];

      if (actionId && !this.hasPermission([actionId])) {
        const data = this.applyForPermission([actionId], [], {}, true);
        return { verified: false, data };
      }

      return { verified: true, data: null };
    },
  },
};

export default permission;
