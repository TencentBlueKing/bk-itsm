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

import i18n from '../i18n/index';

// 满意度评价等级表
/* eslint-disable */
export const SCORE_LIST = (() => window.run_site === 'bmw'
    ? [
        { id: 1, name: i18n.t('m.newCommon["1分(非常不满意)"]'), type: 'scoreRadio' },
        { id: 2, name: i18n.t('m.newCommon["2分(不满意)"]'), type: 'scoreRadio' },
        { id: 3, name: i18n.t('m.newCommon["3分(一般不满意)"]'), type: 'scoreRadio' },
        { id: 4, name: i18n.t('m.newCommon["4分(一般满意)"]'), type: 'scoreRadio' },
        { id: 5, name: i18n.t('m.newCommon["5分(满意)"]'), type: 'scoreRadio' },
        { id: 6, name: i18n.t('m.newCommon["6分(非常满意)"]'), type: 'scoreRadio' },
    ]
    : [
        { id: 1, name: i18n.t('m.newCommon["1分(非常不满意)"]'), type: 'scoreRadio' },
        { id: 2, name: i18n.t('m.newCommon["2分(不满意)"]'), type: 'scoreRadio' },
        { id: 3, name: i18n.t('m.newCommon["3分(一般)"]'), type: 'scoreRadio' },
        { id: 4, name: i18n.t('m.newCommon["4分(满意)"]'), type: 'scoreRadio' },
        { id: 5, name: i18n.t('m.newCommon["5分(非常满意)"]'), type: 'scoreRadio' },
    ])();
/* eslint-disable */
