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

import ajax from '../../utils/ajax'

export default {
    namespaced: true,
    state: {
        // projectAuthActions: [], // 拥有的项目权限列表
        projectAuthActions: [
            // 'project_view',
            // 'project_edit',
            // 'workflow_create',
            // 'service_create',
            // 'role_create',
            // 'sla_manage',
            // 'flow_element_manage',
            // 'system_settings_manage'
        ], // 拥有的项目权限列表
        id: window.DEFAULT_PROJECT,
        projectInfo: {}, // 项目信息
        projectListLoading: false,
        projectList: []
    },
    mutations: {
        setProjectId (state, value) {
            state.id = value
        },
        setProjectInfo (state, value) {
            state.projectInfo = value
            state.projectAuthActions = value.auth_actions
        },
        setProjectListLoading (state, val) {
            state.projectListLoading = val
        },
        setProjectList (state, value) {
            state.projectList = value
        }
    },
    actions: {
        getProjectInfo ({ commit }, params) {
            //  目前项目在 ITSM 是虚拟的，所以暂时默认为 0
            const project_id = 0
            return ajax.get(`/project/projects/${project_id}/info/`, params).then(response => {
                // const res = response.data
                // commit('setProjectInfo', res.data)
                return response.data
            })
        },
        // 获取项目列表
        getProjectList ({ commit }, params) {
            return ajax.get('/project/projects/', { params }).then(response => response.data)
        },
        // 获取项目所以列表
        getProjectAllList ({ commit }, params) {
            return ajax.get('/project/projects/all/', { params }).then(response => response.data)
        },
        // 创建项目
        createProject ({ commit }, data) {
            return ajax.post('/project/projects/', data).then(response => response.data)
        },
        // 获取项目详情
        getProjectDetail ({ commit }, key) {
            return ajax.get(`/project/projects/${key}/`).then(response => {
                commit('setProjectInfo', response.data.data)
                return response.data
            })
        },
        // 更新项目信息
        updateProject ({ commit }, data) {
            return ajax.put(`/project/projects/${data.key}/`, data).then(response => response.data)
        },
        // 删除项目
        deleteProject ({ commit }, key) {
            return ajax.delete(`/project/projects/${key}/`).then(response => response.data)
        },
        // 更改默认项目
        changeDefaultProject ({ commit }, id) {
            return ajax.post(`project/projects/${id}/update_project_record/`)
        }
    }
}
