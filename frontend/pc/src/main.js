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

import "./public-path";
import Vue from "vue";
// import Vuex from 'vuex'
import cookie from "cookie";
import $ from "jquery";
import * as monaco from "monaco-editor";
// magicBox引入及国际化
import bkMagic, { locale, lang } from "bk-magic-vue";
import "bk-magic-vue/dist/bk-magic-vue.min.css";
import {
  Input,
  InputNumber,
  Select,
  Radio,
  RadioGroup,
  RadioButton,
  Checkbox,
  CheckboxGroup,
  Button,
  Option,
  OptionGroup,
  Table,
  TableColumn,
  DatePicker,
  TimePicker,
  TimeSelect,
  Upload,
  Tree,
  Loading,
  Container,
  Row,
  Col,
  Pagination,
  Tooltip,
  Cascader,
} from "element-ui";
import enLocale from "element-ui/lib/locale/lang/en";
import zhLocale from "element-ui/lib/locale/lang/zh-CN";
import locales from "element-ui/lib/locale";
// view components
import App from "./App";
// components
import router from "./router";
import Exception from "./components/common/exception";
import ArrowsLeftIcon from "./components/common/layout/ArrowsLeftIcon";
import "./utils/login.js";
import i18n from "./i18n/index.js";
import store from "./store";
// 自定义指令
import directives from "./directives";
Vue.use(directives);
import vClickOutside from "v-click-outside";
Vue.use(vClickOutside);

window.$ = $;
window.monaco = monaco;

Vue.use(bkMagic);

Vue.use(Input);
Vue.use(InputNumber);
Vue.use(Select);
Vue.use(Radio);
Vue.use(RadioGroup);
Vue.use(RadioButton);
Vue.use(Checkbox);
Vue.use(CheckboxGroup);
Vue.use(Button);
Vue.use(Option);
Vue.use(OptionGroup);
Vue.use(Table);
Vue.use(TableColumn);
Vue.use(DatePicker);
Vue.use(TimeSelect);
Vue.use(TimePicker);
Vue.use(Upload);
Vue.use(Tree);
Vue.use(Loading.directive);
Vue.use(Container);
Vue.use(Row);
Vue.use(Col);
Vue.use(Pagination);
Vue.use(Tooltip);
Vue.use(Cascader);

const ace = require("brace");
const { renderHeader } = require('./utils/util')
Vue.prototype.$ace = ace;
Vue.prototype.$cookie = cookie;
Vue.prototype.$renderHeader = renderHeader;
require("brace/mode/javascript");
require("brace/mode/python");
require("brace/mode/json");
require("brace/mode/yaml");
require("brace/theme/monokai");
require("brace/theme/textmate");
require("brace/theme/solarized_dark");

Vue.use(renderForm);
Vue.component("app-exception", Exception);
Vue.component("arrows-left-icon", ArrowsLeftIcon);

// 国际化
const localeCookie = cookie.parse(document.cookie).blueking_language || "zh-cn";
// magicbox 组件国际化
if (localeCookie === "en") {
  locale.use(lang.enUS);
  locales.use(enLocale);
} else {
  locale.use(lang.zhCN);
  locales.use(zhLocale);
}

store.commit("setLanguage", localeCookie);

// Vue.use(bkMagic)
Vue.use(bkMagic, {
  i18n: function (path, options) {
    const value = i18n.t(path, options);
    if (value !== null && value !== undefined) {
      return value;
    }
    return "";
  },
});

locale.i18n((key, value) => i18n.t(key, value));

if (window.TAM_PROJECT_ID) {
  /* eslint-disable-next-line */
  new Aegis({
    id: window.TAM_PROJECT_ID,
    uin: window.USERNAME,
    reportApiSpeed: true,
    reportAssetSpeed: true,
  });
}

const app = new Vue({
  el: "#app",
  i18n,
  router,
  store,
  components: {
    App,
  },
  template: "<App/>",
});

window.app = app;
