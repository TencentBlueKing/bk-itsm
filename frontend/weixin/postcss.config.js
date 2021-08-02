module.exports = ({ file }) => {
  return {
    plugins: [
      require('postcss-normalize'),
      require('postcss-import'),
      // require('stylelint'),
      require('postcss-advanced-variables'),
      require('postcss-nested'),
      require('postcss-mixins'),
      require('postcss-preset-env'),
      // 采用 rem 布局时打开， 插件地址：https://github.com/songsiqi/px2rem
      // require('postcss-px2rem')({
      //   remUnit: 75
      // }),
      // 使用 vw 布局时打开，配置项参考：https://github.com/evrone/postcss-px-to-viewport
      require('postcss-px-to-viewport')({
        viewportWidth: file && file.dirname && file.dirname.includes("vant") ? 375 : 750,
        unitPrecision: 5,
        selectorBlackList: []
      }),
      require('autoprefixer'),
      require('cssnano')
    ]
  }
}