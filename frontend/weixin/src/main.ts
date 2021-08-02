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

import './public-path.js'
import { createApp } from 'vue'
import {
  DropdownMenu,
  Search,
  Overlay,
  Popup,
  Icon,
  Tag,
  List,
  PullRefresh,
  Button,
  ActionSheet,
  Form,
  Field,
  Skeleton,
  Notify,
  Cell,
  CellGroup,
  Step,
  Steps,
  Picker,
  Checkbox,
  CheckboxGroup,
  Radio,
  RadioGroup,
  DatetimePicker,
  Loading,
  Uploader,
  Dialog
} from 'vant'
import router from './router'
import store from './store/index'
import axiosInstance from './apis/index'
import './css/app.css'
import App from './App.vue'
import 'vant/lib/index.css'
// import Vconsole from 'vconsole'

// const vconsole = new Vconsole()
// console.log(vconsole)

const app = createApp(App)
app.config.globalProperties.$api = axiosInstance
app.config.globalProperties.$Notify = Notify
app.use(router)
app.use(store)
app.use(Popup)
  .use(Icon)
  .use(DropdownMenu)
  .use(Search)
  .use(Overlay)
  .use(Tag)
  .use(List)
  .use(PullRefresh)
  .use(Button)
  .use(ActionSheet)
  .use(Form)
  .use(Field)
  .use(Skeleton)
  .use(Cell)
  .use(CellGroup)
  .use(Step)
  .use(Steps)
  .use(Picker)
  .use(Checkbox)
  .use(CheckboxGroup)
  .use(Radio)
  .use(RadioGroup)
  .use(DatetimePicker)
  .use(Loading)
  .use(Uploader)
  .use(Dialog)
app.mount('#app-container')

export default app
