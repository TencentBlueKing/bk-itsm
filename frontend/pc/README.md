# 前端开发文档

  ITSM 项目前端基于 vue 框架以及配套的 vuex、vue-router、axios 等相关依赖库搭建。采用 webpack 做为前端构建工具，用来处理本地开发和生产环境打包。

  项目的运行需要安装相关依赖包，执行 `npm install` 等待包安装完成，即可进行本地开发或者其他构建需求，根据实际的网络环境可选择 `tnpm` 或者 `cnpm` 替换 `npm`。

## 本地开发环境配置

  本地开发环境使用 webpack-dev-server 插件，它支持在本地起一个 webserver 来提供静态资源文件和 api 的反向代理。在开发时，静态资源文件支持热加载，修改静态资源代码后不需要刷新页面，
  浏览器会自动重载页面；api 的调用可通过修改 `src/build/webpack.dev.conf.js` 文件里的 `devserver` 属性来配置接口地址、代理路径、http/https协议等。
  
  开发环境的启动有以下三个步骤：
  
  - 修改本机 hosts，推荐使用线上地址的子域名，这样可以避免单独处理系统登录、cookies 获取、api 调用跨域等问题，如：
    ```shell
    127.0.0.1     dev.paas.bking.com`
    ```
  - 按需修改`src/build/webpack.dev.conf.js` 文件里的 `devserver`配置，`host`属性对应上一步配置的本机 hosts 域名， `proxy`下的 `target` 属性设置为实际的 api 调用地址,
    `proxy` 的更多配置可参考 [http-proxy-middleware](https://github.com/chimurai/http-proxy-middleware)文档

  - 执行 
    ``` shell 
    npm install
    npm run dev
    ```
  

## 生产环境配置

  生产环境打包命名为：
  ``` shell
    npm run build[:prodution]
    npm run build:production:sourcemap  #若需生成 js 文件的 souremap
  ```

  `src/index.html` 文件定义了两个常量来处理一套代码部署到多环境的需求，后台根据当前环境在入口 html 文件对应的按需赋值即可：
  
  - `window.SITE_URL` 用来设置接口`api path`前缀，如`SITE_URL`赋值为`'/t/bk_itsm/'`，接口路径会配置为 `/t/bk_itsm/api/**`

  - `window.BK_STATIC_URL` 用来设置静态资源的公共路径，变量值会被传递到 `__webpack_public_path__`，拼接到 `assets/**`之前,
  后台根据实际发布的环境动态配置，如 `BK_STATIC_URL`赋值为 `'/t/bk_itsm/static'`，非入口的静态文件路径会配置为 `/t/bk_itsm/static/assets/**` 



## 注意事项

  - 旧版开发环境升级到当前环境需要删除 node_nodules 文件夹以及 package-lock.json 文件，重新安装依赖包
  - url-loader 升级到 3.0.0 版本后，要求 nodejs 的版本至少为 10.13.0，若打包报错需要检查本机安装的 nodejs 版本