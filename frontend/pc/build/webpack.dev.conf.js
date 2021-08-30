const path = require('path')
const webpack = require('webpack')
const merge = require('webpack-merge')
const webpackBase = require('./webpack.base.conf')
const HtmlWebpackPlugin = require('html-webpack-plugin')

// 本地代理地址
const HOST = ''
const ORIGIN = `http://${HOST}`
const SET_URL = ''

module.exports = merge(webpackBase, {
    mode: 'development',
    module: {
        rules: [
            {
                test: /\.(css|scss|sass)$/,
                use: ['style-loader', 'css-loader', 'sass-loader']
            }
        ]
    },
    plugins: [
        new webpack.NamedModulesPlugin(),
        new webpack.HotModuleReplacementPlugin(),
        new HtmlWebpackPlugin({
            filename: 'index.html',
            template: 'index-dev.html',
            inject: true
        })
    ],
    devtool: 'inline-source-map',
    devServer: {
        contentBase: path.posix.join(__dirname, '../../../static'),
        host: `dev.${HOST}`,
        port: 8004,
        https: ORIGIN.indexOf('https') > -1,
        hot: true,
        open: false, // webpack 升级之前设置为打开状态
        overlay: true,
        proxy: {
            '/api/*':{
                target: ORIGIN + SET_URL,
                changeOrigin: true,
                secure: false
            },
            '/openapi/*':{
                target: ORIGIN + SET_URL,
                changeOrigin: true,
                secure: false
            },
            '/core/': {
                target: ORIGIN + SET_URL,
                changeOrigin: true,
                secure: false
            },
            '/o/bk_sops/*': {
                target: ORIGIN,
                changeOrigin: true,
                secure: false,
            },
            '/sops/*':{
                target: ORIGIN + '/o/bk_sops/',
                changeOrigin: true,
                secure: false,
            }
        },
        stats: {
            children: false,
            entrypoints: false,
            modules: false
        }
    }
})